#!/usr/bin/env python3
"""Print a read-only candidate list for one word-origin root.

The output is a human-review stub for phase 2. It normalizes vocabulary words
through lemmas.json, finds partial matches for the selected root and its
variants, and prints the existing meanings and source files. It never assigns
origins, writes JSON, or invents a derivation.
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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "").lower())


def lemma_mapping() -> dict[str, str]:
    data = read_json(DATA_DIR / "lemmas.json")
    return {
        normalize(surface): normalize(lemma)
        for surface, lemma in data.get("lemmas", {}).items()
    }


def resolve_root(requested: str) -> tuple[str, dict[str, Any]]:
    data = read_json(DATA_DIR / "word_roots.json")
    roots = data.get("roots", {})
    requested_key = normalize(requested)
    for root, entry in roots.items():
        forms = [root, *(entry.get("variants", []) or [])]
        if requested_key in {normalize(form) for form in forms}:
            return root, entry
    raise ValueError(f"語根 {requested!r} が data/word_roots.json にありません")


def build_candidates(root: str, entry: dict[str, Any]) -> dict[str, Any]:
    forms = [normalize(root), *(normalize(form) for form in entry.get("variants", []) or [])]
    lemmas = lemma_mapping()
    candidates: dict[str, dict[str, Any]] = {}

    for path in sorted(DATA_DIR.glob("vocab_*.json")):
        vocab = read_json(path)
        for item in vocab.get("words", []):
            surface = normalize(item.get("word"))
            lemma = lemmas.get(surface, surface)
            if not lemma:
                continue
            matches = [form for form in forms if form and form in lemma]
            if not matches:
                continue
            row = candidates.setdefault(
                lemma,
                {"lemma": lemma, "matches": set(), "meanings": set(), "files": set()},
            )
            row["matches"].update(matches)
            meaning = str(item.get("meaning") or "").strip()
            if meaning:
                row["meanings"].add(meaning)
            row["files"].add(path.name)

    rows = []
    for lemma in sorted(candidates):
        row = candidates[lemma]
        rows.append({
            "lemma": row["lemma"],
            "matches": [form for form in forms if form in row["matches"]],
            "meanings": sorted(row["meanings"]),
            "files": sorted(row["files"]),
        })
    return {
        "root": root,
        "gloss": entry.get("gloss", ""),
        "origin": entry.get("origin", ""),
        "forms": forms,
        "candidates": rows,
    }


def print_markdown(result: dict[str, Any]) -> None:
    print(f"## {result['root']}（{result['gloss']}）")
    print(f"- origin: {result['origin']}")
    print(f"- forms: {' / '.join(result['forms'])}")
    print(f"- candidates: {len(result['candidates'])}")
    for row in result["candidates"]:
        meanings = "；".join(row["meanings"]) or "（意味なし）"
        matches = ", ".join(row["matches"])
        files = ", ".join(row["files"])
        print(f"- `{row['lemma']}` [{matches}] — {meanings} — {files}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="語根キー。variantsを指定しても解決します")
    parser.add_argument("--json", action="store_true", help="MarkdownではなくJSONを出力します")
    args = parser.parse_args()

    try:
        root, entry = resolve_root(args.root)
    except ValueError as error:
        parser.error(str(error))
    result = build_candidates(root, entry)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_markdown(result)


if __name__ == "__main__":
    main()
