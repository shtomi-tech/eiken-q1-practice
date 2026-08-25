#!/usr/bin/env python3
"""Print a read-only candidate list for one word-origin root or prefix.

The output is a human-review stub for phase 2. It normalizes vocabulary words
through lemmas.json, finds partial matches for the selected root and its
variants, and prints the existing meanings and source files. Prefix mode finds
unregistered words that start with the selected prefix and reports matching
suffixes as review hints. It never assigns origins, writes JSON, or invents a
derivation.
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


def resolve_prefix(requested: str) -> tuple[str, dict[str, Any], dict[str, Any]]:
    data = read_json(DATA_DIR / "word_roots.json")
    affixes = data.get("affixes", {})
    requested_key = normalize(requested).lstrip("-")
    for prefix, entry in affixes.items():
        if entry.get("kind") != "prefix":
            continue
        if normalize(prefix).lstrip("-") == requested_key:
            return prefix, entry, affixes
    raise ValueError(f"接頭辞 {requested!r} が data/word_roots.json のaffixesにありません")


def registered_origin_lemmas() -> set[str]:
    data = read_json(DATA_DIR / "word_origins.json")
    return {normalize(lemma) for lemma in data.get("origins", {})}


def excluded_lemmas() -> dict[str, str]:
    """判定済みで語源を付けないと決めた語。キー=原形、値="語根: 理由"。"""
    data = read_json(DATA_DIR / "word_origin_excluded.json")
    result: dict[str, str] = {}
    for group, words in (data.get("excluded") or {}).items():
        for lemma, reason in (words or {}).items():
            result[normalize(lemma)] = f"{group}: {reason}"
    return result


def matching_suffixes(lemma: str, affixes: dict[str, Any]) -> list[str]:
    normalized_lemma = normalize(lemma)
    suffixes = []
    for suffix, entry in affixes.items():
        if entry.get("kind") != "suffix":
            continue
        ending = normalize(suffix).lstrip("-")
        if ending and normalized_lemma.endswith(ending):
            suffixes.append(suffix)
    return suffixes


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


def build_prefix_candidates(prefix: str, entry: dict[str, Any], affixes: dict[str, Any]) -> dict[str, Any]:
    prefix_form = normalize(prefix).lstrip("-")
    lemmas = lemma_mapping()
    registered = registered_origin_lemmas()
    excluded = excluded_lemmas()
    candidates: dict[str, dict[str, Any]] = {}

    for path in sorted(DATA_DIR.glob("vocab_*.json")):
        vocab = read_json(path)
        for item in vocab.get("words", []):
            raw_surface = str(item.get("word") or "").strip()
            if not raw_surface or re.search(r"\s", raw_surface):
                continue
            surface = normalize(raw_surface)
            lemma = lemmas.get(surface, surface)
            if (
                not lemma
                or lemma in registered
                or not lemma.startswith(prefix_form)
                or len(lemma) < len(prefix_form) + 5
            ):
                continue
            row = candidates.setdefault(
                lemma,
                {
                    "lemma": lemma,
                    "matches": set(),
                    "suffixes": set(),
                    "meanings": set(),
                    "files": set(),
                },
            )
            row["matches"].add(prefix_form)
            row["suffixes"].update(matching_suffixes(lemma, affixes))
            meaning = str(item.get("meaning") or "").strip()
            if meaning:
                row["meanings"].add(meaning)
            row["files"].add(path.name)

    rows = []
    for lemma in sorted(candidates):
        row = candidates[lemma]
        rows.append({
            "lemma": row["lemma"],
            "matches": [prefix_form],
            "suffixes": sorted(row["suffixes"]),
            "meanings": sorted(row["meanings"]),
            "files": sorted(row["files"]),
            "excluded": excluded.get(row["lemma"], ""),
        })
    return {
        "prefix": prefix_form,
        "gloss": entry.get("gloss", ""),
        "kind": entry.get("kind", "prefix"),
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


def print_prefix_markdown(result: dict[str, Any]) -> None:
    print(f"## {result['prefix']}-（{result['gloss']}）")
    rows = result["candidates"]
    pending = [row for row in rows if not row.get("excluded")]
    decided = [row for row in rows if row.get("excluded")]
    print(f"- candidates: {len(pending)}（未判定）／判定済み {len(decided)}")
    for row in pending:
        meanings = "；".join(row["meanings"]) or "（意味なし）"
        matches = ", ".join(row["matches"])
        suffixes = " / ".join(row["suffixes"]) or "なし"
        files = ", ".join(row["files"])
        print(f"- `{row['lemma']}` [{matches}] 接尾辞: {suffixes} — {meanings} — {files}")
    if decided:
        print("")
        print("### 判定済み（word_origin_excluded.json に記録あり・再検討不要）")
        for row in decided:
            print(f"- `{row['lemma']}` — {row['excluded']}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--root", help="語根キー。variantsを指定しても解決します")
    target.add_argument("--prefix", help="接頭辞キー。affixesのprefixを指定します")
    parser.add_argument("--json", action="store_true", help="MarkdownではなくJSONを出力します")
    args = parser.parse_args()

    if args.root:
        try:
            root, entry = resolve_root(args.root)
        except ValueError as error:
            parser.error(str(error))
        result = build_candidates(root, entry)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_markdown(result)
        return

    try:
        prefix, entry, affixes = resolve_prefix(args.prefix)
    except ValueError as error:
        parser.error(str(error))
    result = build_prefix_candidates(prefix, entry, affixes)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_prefix_markdown(result)


if __name__ == "__main__":
    main()
