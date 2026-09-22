"""Jev（TypeSafe System One）で文脈推測（Context Discovery）データを点検する。

使い方:
    python scripts/jev_check_contexts.py data/context_1_mock-1.json [--limit N]
    python scripts/jev_check_contexts.py data/context_1_*.json --sample 5
    python scripts/jev_check_contexts.py data/context_1_*.json --concurrency 12

各項目について次を判定し、要確認の項目だけを表示する。
  1. answer         : 文脈だけを見せて4択から語義を選ばせ、データの answerIndex と突き合わせる
  2. multi_valid    : 正解以外にも当てはまる選択肢があるか
  3. sense_ok       : targetSense がその文中での target の意味になっているか
  4. inferable      : 手がかりから語義を絞り込めるか（推測不能な問題を見つける）
  5. leakage        : 文脈が語義をそのまま言い換えていて推測が不要になっていないか
  6. explanation_ok : 解説（日本語）が英文の内容と合っているか

環境変数 TYPESAFE_API_KEY が必要。結果は out/jev-context-<round>.json に保存する。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
from collections import Counter
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul

CONCURRENCY = 6
# 正解の確率がこれ未満なら「モデルが迷った項目」として報告する
LOW_PROB = 0.7
# flags() が返す指摘名（集計の見出しに使う）
FLAG_NAMES = (
    "正解不一致",
    "正解確率が低い",
    "複数成立の疑い",
    "語義に疑い",
    "手がかり不足",
    "答えの露出",
    "解説に疑い",
)


def build_questions(item: dict) -> dict:
    criteria = {c: None for c in item["choices"]}
    return {
        "answer": Choice(
            instructions=(
                "A Japanese learner reads `context` without knowing the word "
                "`target`. Which of the Japanese glosses in `criteria` is the "
                "meaning that `target` carries in this passage?"
            ),
            criteria=criteria,
        ),
        "multi_valid": Noul(
            instructions=(
                "More than one of the Japanese glosses in `choices` fits `target` "
                "as it is used in `context`, so the item has no single defensible "
                "answer."
            ),
        ),
        "sense_ok": Noul(
            instructions=(
                "`intended_sense` is an accurate Japanese gloss for the meaning "
                "`target` actually carries in `context`."
            ),
        ),
        "inferable": Noul(
            instructions=(
                "The phrases listed in `clues` give a reader who does not know "
                "`target` enough evidence to narrow its meaning to "
                "`intended_sense` rather than merely guessing."
            ),
        ),
        "leakage": Noul(
            instructions=(
                "`context` gives the meaning of `target` away directly — by "
                "defining it, by restating it with an answer-equivalent synonym, "
                "or by translating it — so that no inference is required."
            ),
        ),
        "explanation_ok": Noul(
            instructions=(
                "The Japanese text in `explanation` accurately describes what "
                "`context` says, with no mistranslation, no claim absent from "
                "`context`, and no contradiction of it."
            ),
        ),
    }


async def check_item(client: AsyncTypeSafeClient, item: dict, sem: asyncio.Semaphore) -> dict:
    choices = item["choices"]
    intended = choices[item["answerIndex"]]
    state = {
        "target": item["target"],
        "context": " ".join(item["fullEnglish"]),
        "clues": [c["text"] for c in item["contextClues"]],
        "choices": choices,
        "intended_sense": intended,
        "explanation": item.get("inferenceExplanation", ""),
    }
    async with sem:
        res = await client.system_one(state=state, questions=build_questions(item))

    ans = res.choices["answer"]
    nouls = {k: round(v.noul, 3) for k, v in res.nouls.items()}
    return {
        "q": item["q"],
        "target": item["target"],
        "intended": intended,
        "jev_choice": ans.choice,
        "intended_prob": round(ans.probabilities.get(intended, 0.0), 3),
        "probabilities": {k: round(v, 3) for k, v in ans.probabilities.items()},
        "context": state["context"],
        "clues": state["clues"],
        "explanation": state["explanation"],
        **nouls,
    }


def flags(r: dict) -> list[str]:
    out = []
    if r["jev_choice"] != r["intended"]:
        out.append("正解不一致")
    if r["intended_prob"] < LOW_PROB:
        out.append(f"正解確率が低い({r['intended_prob']})")
    if r["multi_valid"] >= 0.5:
        out.append(f"複数成立の疑い({r['multi_valid']})")
    if r["sense_ok"] < 0.5:
        out.append(f"語義に疑い({r['sense_ok']})")
    if r["inferable"] < 0.5:
        out.append(f"手がかり不足({r['inferable']})")
    if r["leakage"] >= 0.5:
        out.append(f"答えの露出({r['leakage']})")
    if r["explanation_ok"] < 0.5:
        out.append(f"解説に疑い({r['explanation_ok']})")
    return out


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path, nargs="+", help="点検する文脈JSON（複数可）")
    p.add_argument("--limit", type=int, default=None, help="各ファイルの先頭N件だけ処理する")
    p.add_argument("--sample", type=int, default=None, help="各ファイルから無作為にN件処理する")
    p.add_argument("--seed", type=int, default=0, help="--sample の乱数種")
    p.add_argument(
        "--concurrency", type=int, default=CONCURRENCY, help=f"同時実行数（既定 {CONCURRENCY}）"
    )
    p.add_argument("--quiet", action="store_true", help="指摘の本文を省き、件数だけ表示する")
    args = p.parse_args()

    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY が設定されていません。")

    sem = asyncio.Semaphore(args.concurrency)
    total_items = total_flagged = 0
    tally: Counter[str] = Counter()
    rng = random.Random(args.seed)

    async with AsyncTypeSafeClient() as client:
        for path in args.path:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data["contexts"]
            if args.sample is not None and args.sample < len(items):
                items = sorted(rng.sample(items, args.sample), key=lambda i: i["q"])
            elif args.limit is not None:
                items = items[: args.limit]
            results = await asyncio.gather(*(check_item(client, i, sem) for i in items))

            flagged = [r for r in results if flags(r)]
            total_items += len(items)
            total_flagged += len(flagged)
            for r in flagged:
                for f in flags(r):
                    for name in FLAG_NAMES:
                        if f.startswith(name):
                            tally[name] += 1
                            break

            out_dir = path.parent.parent / "out"
            out_dir.mkdir(exist_ok=True)
            round_name = data["meta"]["datasetId"]
            out_path = out_dir / f"jev-context-{round_name}.json"
            out_path.write_text(
                json.dumps({"source": str(path), "results": results}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            print(f"\n=== {path.name}: {len(items)}件中 {len(flagged)}件が要確認 -> {out_path}", flush=True)
            for r in [] if args.quiet else flagged:
                print(f"\nQ{r['q']} {r['target']}: {' / '.join(flags(r))}")
                print(f"  {r['context']}")
                print(f"  手がかり: {r['clues']}")
                print(f"  データの正解: {r['intended']} / Jev: {r['jev_choice']}")
                print(f"  確率: {r['probabilities']}")

    print(f"\n合計: {total_items}件中 {total_flagged}件が要確認")
    for name in FLAG_NAMES:
        if tally[name]:
            print(f"  {name}: {tally[name]}件")


if __name__ == "__main__":
    asyncio.run(main())
