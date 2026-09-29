"""Jev（TypeSafe System One）で暗記カードの「語源・なりたち」を分類する。

使い方:
    python scripts/jev_classify_word_origins.py [--limit N] [--dry-run]

data/word_origins.json の各語について、表示される語源テキスト
（derivation・構成パーツ・語源チェーン）を読ませ、次の2軸で分類する。
  1. lineage   : 語源をさかのぼった最も古い系統（ラテン語・ギリシャ語・ゲルマン系 など）
  2. formation : 語のなりたちの型（接辞＋語根・借用・複合・比喩転用・擬音 など）

分類は語源テキストを根拠にする。言語名がない A型は、構成パーツ（接頭辞・語根）から系統を判断させる。
最上位の確率が LOW_PROB 未満の語は「要確認」として一覧に出す。

環境変数 TYPESAFE_API_KEY が必要。結果は out/jev-word-origins.json と
out/jev-word-origins.csv に保存する。
"""

from __future__ import annotations

import argparse
import asyncio
import collections
import csv
import json
import os
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, Choice

ROOT = Path(__file__).resolve().parent.parent
ORIGINS = ROOT / "data" / "word_origins.json"
OUT_DIR = ROOT / "out"

CONCURRENCY = 6
# 最上位ラベルの確率がこれ未満なら「Jevが迷った語」として報告する
LOW_PROB = 0.6

LINEAGE = {
    "latin": "Traced back to Latin (including via Old French, Anglo-Norman, or Italian from Latin).",
    "greek": "Traced back to Ancient Greek (including via Latin or French from Greek).",
    "germanic": "Native Germanic: Old English, Proto-Germanic, Old Norse, Dutch, Low German, or other Germanic sources.",
    "french_non_latin": "Old French or Anglo-Norman whose deeper source is Frankish/Germanic, Celtic, or not stated.",
    "other": "Some other language family, e.g. Arabic, Hebrew, Persian, Sanskrit, Chinese, Japanese, Native American, Celtic.",
    "unknown": "The text says the origin is unknown, uncertain, or disputed, and gives nothing to judge the lineage from.",
}

FORMATION = {
    "affix_root": "Built from a prefix and/or suffix attached to a root (e.g. con- + don 'give').",
    "compound": "Two or more independent words joined together (e.g. back + fire, a phrasal verb or verb + particle).",
    "borrowing": "Borrowed essentially whole from another language, with the meaning carried over largely unchanged.",
    "semantic_shift": "The modern meaning grew out of an older concrete meaning or image by metaphor, narrowing, or extension.",
    "imitative": "Imitative or onomatopoeic: the sound of the word echoes a noise or motion.",
    "eponym": "Derived from a person's name, place name, or other proper noun.",
    "shortening": "Clipping, blend, back-formation, or acronym.",
    "unclear": "The text does not explain how the word was formed.",
}


def display_state(word: str, entry: dict) -> dict:
    """暗記カードに表示される語源情報だけを Jev に渡す。"""
    state: dict = {"word": word, "etymology_ja": entry.get("derivation", "")}
    if entry.get("parts"):
        state["parts"] = [
            {"form": p.get("form"), "kind": p.get("kind"), "meaning_ja": p.get("gloss")}
            for p in entry["parts"]
        ]
    if entry.get("chain"):
        state["chain"] = [
            {k: v for k, v in step.items() if k in ("term", "gloss")} for step in entry["chain"]
        ]
    if entry.get("note"):
        state["note_ja"] = entry["note"]
    return state


QUESTIONS = {
    "lineage": Choice(
        instructions=(
            "Based only on the Japanese etymology text in `etymology_ja` (and `parts`, "
            "`chain`, `note_ja` if present) for the English word in `word`, which language "
            "lineage does the word ultimately trace back to? Use the earliest source "
            "language the text states. If no language is named but the text breaks the "
            "word into classical prefixes and roots (e.g. per- + spect), judge the lineage "
            "those elements belong to."
        ),
        criteria=LINEAGE,
    ),
    "formation": Choice(
        instructions=(
            "Based only on the etymology text provided for `word`, which best describes "
            "how the English word was formed?"
        ),
        criteria=FORMATION,
    ),
}


async def classify(client: AsyncTypeSafeClient, word: str, entry: dict, sem: asyncio.Semaphore) -> dict:
    async with sem:
        res = await client.system_one(state=display_state(word, entry), questions=QUESTIONS)
    row = {"word": word, "type": entry.get("type"), "derivation": entry.get("derivation", "")}
    for key in QUESTIONS:
        ans = res.choices[key]
        probs = dict(sorted(ans.probabilities.items(), key=lambda kv: -kv[1]))
        row[key] = ans.choice
        row[f"{key}_prob"] = round(probs[ans.choice], 3)
        row[f"{key}_probabilities"] = {k: round(v, 3) for k, v in probs.items()}
    return row


def uncertain(row: dict) -> list[str]:
    return [f"{k}={row[k]}({row[f'{k}_prob']})" for k in QUESTIONS if row[f"{k}_prob"] < LOW_PROB]


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None, help="先頭N語だけ処理する")
    p.add_argument("--dry-run", action="store_true", help="API を呼ばず、Jev に渡す state を表示する")
    args = p.parse_args()

    origins = json.loads(ORIGINS.read_text(encoding="utf-8"))["origins"]
    items = [(w, e) for w, e in origins.items() if e and e.get("derivation")][: args.limit]

    if args.dry_run:
        for w, e in items[:5]:
            print(json.dumps(display_state(w, e), ensure_ascii=False, indent=2))
        print(f"\n対象 {len(items)}語（dry-run のため API は呼んでいません）")
        return

    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY が設定されていません。")

    sem = asyncio.Semaphore(CONCURRENCY)
    async with AsyncTypeSafeClient() as client:
        rows = await asyncio.gather(*(classify(client, w, e, sem) for w, e in items))

    OUT_DIR.mkdir(exist_ok=True)
    json_path = OUT_DIR / "jev-word-origins.json"
    json_path.write_text(
        json.dumps({"source": str(ORIGINS.relative_to(ROOT)), "results": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    csv_path = OUT_DIR / "jev-word-origins.csv"
    cols = ["word", "type", "lineage", "lineage_prob", "formation", "formation_prob", "derivation"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"=== {len(rows)}語を分類 -> {json_path} / {csv_path}")
    for key in QUESTIONS:
        print(f"\n[{key}]")
        for label, n in collections.Counter(r[key] for r in rows).most_common():
            print(f"  {label:<18}{n:>5}")
        print("  -- A/B型別 --")
        for t in sorted({r["type"] for r in rows}):
            c = collections.Counter(r[key] for r in rows if r["type"] == t)
            print(f"  {t}: " + ", ".join(f"{k} {v}" for k, v in c.most_common()))

    flagged = [r for r in rows if uncertain(r)]
    print(f"\n要確認（最上位確率 < {LOW_PROB}）: {len(flagged)}語")
    for r in flagged[:40]:
        print(f"  {r['word']}: {' / '.join(uncertain(r))}")
        print(f"    {r['derivation']}")


if __name__ == "__main__":
    asyncio.run(main())
