"""既存の単語語源注記を表示用 origin 辞書へ同期する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import quote

from q1_iuhw_etymology import ORIGIN_SOURCE_SLUGS


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: object) -> str:
    return "".join(str(value or "").lower().split())


def lemma_mapping() -> dict[str, str]:
    data = read_json(DATA_DIR / "lemmas.json")
    return {
        normalize(surface): normalize(lemma)
        for surface, lemma in (data.get("lemmas") or {}).items()
    }


def excluded_lemmas() -> set[str]:
    data = read_json(DATA_DIR / "word_origin_excluded.json")
    return {
        normalize(lemma)
        for words in (data.get("excluded") or {}).values()
        for lemma in (words or {})
    }


def vocab_paths() -> list[Path]:
    manifest = read_json(DATA_DIR / "manifest.json")
    paths = {
        ROOT / meta["vocabUrl"]
        for meta in (manifest.get("q1") or {}).values()
        if meta.get("vocabUrl")
    }
    return sorted(paths)


def source_url(lemma: str) -> str | None:
    slug = ORIGIN_SOURCE_SLUGS.get(lemma)
    if not slug:
        return None
    return f"https://www.etymonline.com/word/{quote(slug, safe='')}"


def candidate_score(candidate: dict[str, str], lemma: str) -> tuple[int, int, int, str]:
    explanation = candidate["explanation"]
    has_japanese = int(any("\u3040" <= char <= "\u9fff" for char in explanation))
    is_base_surface = int(candidate["surface"].lower() == lemma)
    return (is_base_surface, has_japanese, len(explanation), candidate["file"])


def collect_candidates(lemmas: dict[str, str], excluded: set[str]) -> dict[str, dict[str, str]]:
    candidates: dict[str, dict[str, str]] = {}
    for path in vocab_paths():
        vocab = read_json(path)
        for item in vocab.get("words", []):
            surface = str(item.get("word") or "").strip()
            if not surface or any(char.isspace() for char in surface):
                continue
            lemma = lemmas.get(surface.lower(), surface.lower())
            if not lemma or normalize(lemma) in excluded:
                continue
            explanation = str(item.get("etymology") or "").strip()
            meaning = str(item.get("meaning") or "").strip()
            if not explanation or not meaning:
                continue
            candidate = {
                "surface": surface,
                "explanation": explanation,
                "meaning": meaning,
                "file": path.name,
            }
            previous = candidates.get(lemma)
            if previous is None or candidate_score(candidate, lemma) > candidate_score(previous, lemma):
                candidates[lemma] = candidate
    return candidates


def append_origin_entries_preserving_format(path: Path, additions: dict[str, dict[str, str]]) -> None:
    original_bytes = path.read_bytes()
    newline = "\r\n" if b"\r\n" in original_bytes else "\n"
    original = original_bytes.decode("utf-8").replace("\r\n", "\n")
    marker = "\n  }\n}"
    marker_index = original.rfind(marker)
    if marker_index < 0:
        raise ValueError(f"origins辞書の終端を特定できません: {path}")

    lines = json.dumps(additions, ensure_ascii=False, indent=2).splitlines()
    body = "\n".join(f"  {line}" for line in lines[1:-1])
    updated = original[:marker_index] + ",\n" + body + original[marker_index:]
    if newline == "\r\n":
        updated = updated.replace("\n", "\r\n")
    path.write_bytes(updated.encode("utf-8"))


def sync(write: bool) -> tuple[int, list[str], int]:
    origins_path = DATA_DIR / "word_origins.json"
    origins_data = read_json(origins_path)
    origins = origins_data.setdefault("origins", {})
    lemmas = lemma_mapping()
    excluded = excluded_lemmas()
    candidates = collect_candidates(lemmas, excluded)

    additions: dict[str, dict[str, str]] = {}
    for lemma, candidate in candidates.items():
        if lemma in origins:
            continue
        explanation = candidate["explanation"].rstrip("。.")
        origin = {
            "type": "B",
            "derivation": f"{explanation} → {candidate['meaning']}",
        }
        source = source_url(lemma)
        if source:
            origin["source"] = source
        additions[lemma] = origin

    if write and additions:
        append_origin_entries_preserving_format(origins_path, additions)

    return len(additions), sorted(additions), len(candidates)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="word_origins.jsonへ反映する")
    args = parser.parse_args()
    added, lemmas, candidate_count = sync(args.write)
    action = "追加" if args.write else "追加候補"
    print(f"{action}: {added}語 / 候補総数: {candidate_count}語")
    if args.write and lemmas:
        print("先頭:", ", ".join(lemmas[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
