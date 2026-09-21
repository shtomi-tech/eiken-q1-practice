"""Jev（TypeSafe System One）で語句空所補充データを点検する。

使い方:
    python scripts/jev_check_questions.py data/questions_1_mock-1.json [--limit N]

各問について次の3点を判定し、要確認の問題だけを表示する。
  1. answer          : 4択から正解を選ばせ、データの answerIndex と突き合わせる
  2. multi_valid     : 正解以外にも成立する選択肢があるか
  3. translation_ok  : translation が英文の意味と一致しているか

環境変数 TYPESAFE_API_KEY が必要。結果は out/jev-check-<round>.json に保存する。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul

CONCURRENCY = 6
# 正解の確率がこれ未満なら「モデルが迷った問題」として報告する
LOW_PROB = 0.7


def build_questions(item: dict) -> dict:
    criteria = {c: None for c in item["choices"]}
    return {
        "answer": Choice(
            instructions=(
                "Which single word or phrase correctly fills the blank ( ) in "
                "`stem`, producing the most natural and idiomatic English for an "
                "advanced vocabulary exam?"
            ),
            criteria=criteria,
        ),
        "multi_valid": Noul(
            instructions=(
                "More than one of the options in `choices` produces a fully "
                "acceptable, natural sentence when placed in the blank in `stem`, "
                "so the item has no single defensible answer."
            ),
        ),
        "translation_ok": Noul(
            instructions=(
                "The Japanese text in `translation` accurately conveys the meaning "
                "of `stem` with the intended answer in the blank, with no "
                "mistranslation, omission, or addition."
            ),
        ),
    }


async def check_item(client: AsyncTypeSafeClient, item: dict, sem: asyncio.Semaphore) -> dict:
    choices = item["choices"]
    intended = choices[item["answerIndex"]]
    state = {
        "stem": item["stem"],
        "choices": choices,
        "intended_answer": intended,
        "translation": item.get("translation", ""),
    }
    async with sem:
        res = await client.system_one(state=state, questions=build_questions(item))

    ans = res.choices["answer"]
    return {
        "q": item["q"],
        "intended": intended,
        "jev_choice": ans.choice,
        "intended_prob": round(ans.probabilities.get(intended, 0.0), 3),
        "probabilities": {k: round(v, 3) for k, v in ans.probabilities.items()},
        "multi_valid": round(res.nouls["multi_valid"].noul, 3),
        "translation_ok": round(res.nouls["translation_ok"].noul, 3),
        "stem": item["stem"],
        "translation": item.get("translation", ""),
    }


def flags(r: dict) -> list[str]:
    out = []
    if r["jev_choice"] != r["intended"]:
        out.append("正解不一致")
    if r["intended_prob"] < LOW_PROB:
        out.append(f"正解確率が低い({r['intended_prob']})")
    if r["multi_valid"] >= 0.5:
        out.append(f"複数成立の疑い({r['multi_valid']})")
    if r["translation_ok"] < 0.5:
        out.append(f"和訳に疑い({r['translation_ok']})")
    return out


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path, nargs="+", help="点検する問題JSON（複数可）")
    p.add_argument("--limit", type=int, default=None, help="各ファイルの先頭N問だけ処理する")
    args = p.parse_args()

    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY が設定されていません。")

    sem = asyncio.Semaphore(CONCURRENCY)
    total_items = total_flagged = 0

    async with AsyncTypeSafeClient() as client:
        for path in args.path:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data["questions"][: args.limit]
            results = await asyncio.gather(*(check_item(client, i, sem) for i in items))

            flagged = [r for r in results if flags(r)]
            total_items += len(items)
            total_flagged += len(flagged)

            out_dir = path.parent.parent / "out"
            out_dir.mkdir(exist_ok=True)
            out_path = out_dir / f"jev-check-{data['meta']['round']}.json"
            out_path.write_text(
                json.dumps({"source": str(path), "results": results}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            print(f"\n=== {path.name}: {len(items)}問中 {len(flagged)}問が要確認 -> {out_path}")
            for r in flagged:
                print(f"\nQ{r['q']}: {' / '.join(flags(r))}")
                print(f"  {r['stem']}")
                print(f"  データの正解: {r['intended']} / Jev: {r['jev_choice']}")
                print(f"  確率: {r['probabilities']}")

    print(f"\n合計: {total_items}問中 {total_flagged}問が要確認")


if __name__ == "__main__":
    asyncio.run(main())
