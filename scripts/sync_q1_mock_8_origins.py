"""模試第8回の単語を語源表示辞書へ登録する。"""

from __future__ import annotations

import json
from pathlib import Path

from build_q1_mock_8_data import ETYMOLOGY


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
VOCAB_PATH = DATA_DIR / "vocab_1_mock-8.json"
ORIGINS_PATH = DATA_DIR / "word_origins.json"
LEMMAS_PATH = DATA_DIR / "lemmas.json"
EXCLUDED_PATH = DATA_DIR / "word_origin_excluded.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    vocab = load(VOCAB_PATH)
    origins_data = load(ORIGINS_PATH)
    lemmas = {
        str(surface).lower(): str(lemma).lower()
        for surface, lemma in (load(LEMMAS_PATH).get("lemmas") or {}).items()
    }
    excluded = {
        str(lemma).lower()
        for words in (load(EXCLUDED_PATH).get("excluded") or {}).values()
        for lemma in (words or {})
    }

    origins = origins_data.setdefault("origins", {})
    added = 0
    skipped_existing = 0
    skipped_excluded = 0
    for item in vocab.get("words", []):
        surface = str(item.get("word", "")).strip()
        key = lemmas.get(surface.lower(), surface.lower())
        if key in excluded:
            skipped_excluded += 1
            continue
        if key in origins:
            skipped_existing += 1
            continue
        meaning = str(item.get("meaning", "")).strip()
        derivation = f"{ETYMOLOGY[surface]} → {meaning}"
        origins[key] = {"type": "B", "derivation": derivation}
        added += 1

    ORIGINS_PATH.write_text(
        json.dumps(origins_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"mock-8 origins: added {added}, existing {skipped_existing}, "
        f"excluded {skipped_excluded}"
    )


if __name__ == "__main__":
    main()
