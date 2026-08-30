"""模試2〜4の語源説明から、原形キーの表示用語源辞書を同期する。"""

from __future__ import annotations

import json
from pathlib import Path

from q1_mock_etymology import ETYMOLOGY_BY_ROUND


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MOCK_ROUNDS = ("mock-2", "mock-3", "mock-4")
UNCERTAIN_MARKERS = ("語源は不確か", "語形成は不確か")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_map() -> dict[str, str]:
    data = load(DATA_DIR / "lemmas.json")
    return {
        str(surface).lower(): str(lemma).lower()
        for surface, lemma in (data.get("lemmas") or {}).items()
    }


def write_origin_entries(path: Path, entries: dict[str, dict]) -> int:
    if not entries:
        return 0
    text = path.read_text(encoding="utf-8")
    marker = "\n  }\n}\n"
    marker_pos = text.rfind(marker)
    if marker_pos < 0:
        raise ValueError(f"originsの終端を見つけられません: {path}")

    blocks: list[str] = []
    for key in sorted(entries):
        entry_lines = json.dumps(entries[key], ensure_ascii=False, indent=2).splitlines()
        blocks.append(
            "\n".join(
                [f'    {json.dumps(key, ensure_ascii=False)}: {entry_lines[0]}']
                + [f"    {line}" for line in entry_lines[1:]]
            )
        )
    addition = ",\n" + ",\n".join(blocks)
    path.write_text(text[:marker_pos] + addition + text[marker_pos:], encoding="utf-8")
    return len(entries)


def sync() -> tuple[int, int]:
    canonical = canonical_map()
    vocab_entries: dict[str, dict] = {}
    for round_id in MOCK_ROUNDS:
        vocab = load(DATA_DIR / f"vocab_1_{round_id}.json")
        for item in vocab.get("words", []):
            surface = str(item.get("word", "")).strip()
            lemma = canonical.get(surface.lower(), surface.lower())
            if not lemma or lemma in vocab_entries:
                continue
            explanation = ETYMOLOGY_BY_ROUND[round_id][surface]
            vocab_entries[lemma] = {
                "meaning": str(item.get("meaning", "")).strip(),
                "explanation": explanation.rstrip("。"),
            }

    origins_data = load(DATA_DIR / "word_origins.json")
    existing_origins = {
        str(key).lower(): value for key, value in origins_data.get("origins", {}).items()
    }
    excluded_path = DATA_DIR / "word_origin_excluded.json"
    excluded_data = load(excluded_path)
    excluded = excluded_data.setdefault("excluded", {})
    general_excluded = excluded.setdefault("general", {})

    new_origins: dict[str, dict] = {}
    new_excluded: dict[str, str] = {}
    for lemma, details in vocab_entries.items():
        if lemma in existing_origins or any(
            lemma in {str(word).lower() for word in words}
            for words in excluded.values()
        ):
            continue
        explanation = details["explanation"]
        if any(marker in explanation for marker in UNCERTAIN_MARKERS):
            new_excluded[lemma] = "生成元の語源説明でも不確かと明記されており、安全な語源分解を作らない"
            continue
        new_origins[lemma] = {
            "type": "B",
            "derivation": f"{explanation} → {details['meaning']}",
        }

    for lemma, reason in new_excluded.items():
        general_excluded[lemma] = reason
    if new_excluded:
        excluded_path.write_text(
            json.dumps(excluded_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    added_origins = write_origin_entries(DATA_DIR / "word_origins.json", new_origins)
    return added_origins, len(new_excluded)


def main() -> None:
    origins, excluded = sync()
    print(f"mock origins: {origins}件追加 / C型除外 {excluded}件")


if __name__ == "__main__":
    main()
