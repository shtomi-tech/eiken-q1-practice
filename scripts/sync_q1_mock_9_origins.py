"""模試第9回の単語を語源表示辞書へ登録する。"""

from __future__ import annotations

import json
from pathlib import Path

from build_q1_mock_9_data import ETYMOLOGY


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
VOCAB_PATH = DATA_DIR / "vocab_1_mock-9.json"
ORIGINS_PATH = DATA_DIR / "word_origins.json"
LEMMAS_PATH = DATA_DIR / "lemmas.json"
EXCLUDED_PATH = DATA_DIR / "word_origin_excluded.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    vocab = load(VOCAB_PATH)
    original_bytes = ORIGINS_PATH.read_bytes()
    newline = "\r\n" if b"\r\n" in original_bytes else "\n"
    original_text = original_bytes.decode("utf-8")
    source_text = original_text.replace("\r\n", "\n")
    origins_data = json.loads(original_text)
    lemmas = {str(surface).lower(): str(lemma).lower() for surface, lemma in (load(LEMMAS_PATH).get("lemmas") or {}).items()}
    excluded = {str(lemma).lower() for words in (load(EXCLUDED_PATH).get("excluded") or {}).values() for lemma in (words or {})}

    origins = origins_data.setdefault("origins", {})
    new_entries: list[tuple[str, dict]] = []
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
        value = {"type": "B", "derivation": f"{ETYMOLOGY[surface]} → {meaning}"}
        origins[key] = value
        new_entries.append((key, value))
        added += 1

    if new_entries:
        marker = "\n  }\n}"
        insert_at = source_text.rfind(marker)
        if insert_at < 0:
            raise ValueError("word_origins.jsonのorigins終端を特定できません")
        body = source_text[:insert_at].rstrip()
        if not body.endswith(","):
            body += ","
        entry_blocks = []
        for key, value in new_entries:
            compact = json.dumps({key: value}, ensure_ascii=False, indent=2)
            lines = compact.splitlines()[1:-1]
            entry_blocks.append("\n".join(f"  {line}" for line in lines))
        updated_text = body + "\n" + ",\n".join(entry_blocks) + source_text[insert_at:]
        if newline == "\r\n":
            updated_text = updated_text.replace("\n", "\r\n")
        ORIGINS_PATH.write_bytes(updated_text.encode("utf-8"))
    print(f"mock-9 origins: added {added}, existing {skipped_existing}, excluded {skipped_excluded}")


if __name__ == "__main__":
    main()
