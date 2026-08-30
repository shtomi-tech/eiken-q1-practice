#!/usr/bin/env python3
"""Print human-review stubs for idiom core-image authoring.

This script is intentionally read-only. It proposes a type and particle
candidate, but never writes vocab JSON or invents a chain/meaning.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PARTICLE_ORDER = (
    "up to",
    "out of",
    "back",
    "into",
    "across",
    "together",
    "along",
    "behind",
    "upon",
    "under",
    "around",
    "forward",
    "out",
    "up",
    "off",
    "on",
    "in",
    "down",
    "over",
    "away",
)
# 既知の動詞を列挙すると新しい熟語が必ず未知語になるため、動詞側は列挙しない。
# 「機能語で始まるか」という構造だけで判定し、最終判断は人が行う。
FUNCTION_WORD_STARTS = {
    "in", "at", "on", "for", "by", "with", "of", "as", "to", "from",
    "under", "over", "into", "out", "up", "down", "off", "no", "none",
    "more", "less", "sooner", "safe", "far", "all", "bit", "day",
    "before", "after", "provided", "rather", "even", "so", "such",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def particle_candidate(phrase: str) -> str | None:
    normalized = re.sub(r"\s+", " ", phrase.lower()).strip()
    for particle in PARTICLE_ORDER:
        if re.search(rf"(?:^|\s){re.escape(particle)}(?:$|\s)", normalized):
            return particle
    return None


def type_candidate(phrase: str, particle: str | None) -> str:
    """A / B / C の候補を返す。判定は構造のみで、語彙知識には依存しない。

    A: 動詞＋不変化詞（連鎖＋不変化詞パネル）
    B: 前置詞句・定型表現（連鎖のみ、particle を付けない）
    C: 連鎖がこじつけになるもの（coreImage を付けない）
    """
    tokens = re.findall(r"[a-z]+(?:['-][a-z]+)?", phrase.lower())
    if not tokens:
        return "C?"
    if tokens[0] in FUNCTION_WORD_STARTS:
        # in search of / for the time being / more or less など
        return "B"
    if particle:
        # 先頭が機能語でなく不変化詞を含む＝動詞＋不変化詞とみなす
        return "A"
    # shake hands / take a nap のような動詞＋名詞。B と C の判断は人が行う
    return "B/C?"


def selected_files(value: str | None) -> list[Path]:
    if value:
        path = Path(value)
        if not path.is_absolute():
            path = ROOT / path
        return [path]
    return sorted(
        path
        for path in DATA_DIR.glob("vocab_*.json")
        if "topic" not in path.name and "iuhw" not in path.name and "pre1" not in path.name
    )


def build_rows(path: Path, missing_only: bool) -> list[dict[str, Any]]:
    vocab = read_json(path)
    rows = []
    for item in vocab.get("idioms", []):
        if missing_only and "coreImage" in item:
            continue
        particle = particle_candidate(item.get("phrase", ""))
        particle_entry = read_json(DATA_DIR / "particle_images.json").get("particles", {}).get(particle, {}) if particle else {}
        rows.append({
            "file": path.name,
            "q": item.get("q"),
            "phrase": item.get("phrase"),
            "meaning": item.get("meaning"),
            "example": item.get("example"),
            "typeCandidate": type_candidate(item.get("phrase", ""), particle),
            "particleCandidate": particle,
            "knownSenses": [
                {"id": sense.get("id"), "label": sense.get("label"), "siblings": sense.get("siblings", [])}
                for sense in particle_entry.get("senses", [])
            ],
            "coreImage": {"chain": []},
        })
    return rows


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="one vocab JSON; defaults to all non-topic delivery vocab files")
    parser.add_argument("--all", action="store_true", help="include entries that already have coreImage")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = parser.parse_args()
    rows = [
        row
        for path in selected_files(args.file)
        for row in build_rows(path, missing_only=not args.all)
    ]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for row in rows:
        print(f"## {row['file']} / Q{row['q']} / {row['phrase']}")
        print(f"- type candidate: {row['typeCandidate']}")
        print(f"- particle candidate: {row['particleCandidate'] or '(none)'}")
        print(f"- meaning: {row['meaning']}")
        print(f"- example: {row['example']}")
        if row["knownSenses"]:
            print("- known senses:")
            for sense in row["knownSenses"]:
                print(f"  - {sense['id']}: {sense['label']}")
        print("- coreImage: { chain: [] }  # human authoring required")
        print()


if __name__ == "__main__":
    main()
