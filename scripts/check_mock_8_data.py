"""英検1級模試第8回の構造・内容・重複・音声を検査する。"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATASET_ID = "eiken1-mock-8"
QUESTIONS_PATH = DATA_DIR / "questions_1_mock-8.json"
VOCAB_PATH = DATA_DIR / "vocab_1_mock-8.json"
LEMMA_PATH = DATA_DIR / "lemmas.json"
ORIGINS_PATH = DATA_DIR / "word_origins.json"
EXCLUDED_PATH = DATA_DIR / "word_origin_excluded.json"
AUDIO_DIR = ROOT / "assets" / "audio" / "vocab" / "1" / "mock-8"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"\(\s+\)")
TRANSLATION_BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")
IPA_RE = re.compile(r"^/.+/$")
FLASHCARD_VERB_LEMMAS = {
    "assailed": "assail",
    "bridling": "bridle",
    "dismantled": "dismantle",
    "diffused": "diffuse",
    "grappled": "grapple",
    "lauding": "laud",
    "maligned": "malign",
    "ostracizing": "ostracize",
    "pulverizing": "pulverize",
    "reviled": "revile",
    "scuffed": "scuff",
    "shirked": "shirk",
}
EXPECTED_ANSWER_INDICES = [
    1, 3, 0, 0, 0, 2, 1, 0, 0, 0,
    1, 1, 2, 3, 0, 1, 2, 3, 0, 3,
    3, 0, 3, 0, 1,
]

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(ROOT / "scripts"))
from check_q1_data import surface_variants  # noqa: E402


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise ValueError(f"{DATASET_ID}: {message}")


def item_surface(item: dict) -> str:
    return str(item.get("phrase") or item.get("word") or "").strip()


def text_skeleton(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def example_skeleton(example: str, surface: str) -> str:
    return text_skeleton(re.sub(re.escape(surface), "( )", example, count=1, flags=re.IGNORECASE))


def audio_slug(value: str) -> str:
    normalized = str(value or "").lower().replace("’", "'")
    normalized = re.sub(r"\b(one's|his|her|my|your|our|their|its)\b", "@poss", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def check_audio(vocab: dict, lemmas: dict, allow_missing_audio: bool) -> list[str]:
    missing: list[str] = []
    for item in vocab.get("words", []):
        surface = item_surface(item)
        target = AUDIO_DIR / f"{audio_slug(surface)}.mp3"
        if not target.is_file() or target.stat().st_size == 0:
            missing.append(str(target.relative_to(ROOT)))
        flashcard_lemma = (lemmas.get("flashcardLemmas") or {}).get(surface.lower())
        if flashcard_lemma:
            target = ROOT / "assets" / "audio" / "lemma" / f"{audio_slug(flashcard_lemma)}.mp3"
            if not target.is_file() or target.stat().st_size == 0:
                missing.append(str(target.relative_to(ROOT)))
    for item in vocab.get("idioms", []):
        surface = item_surface(item)
        target = AUDIO_DIR / "idiom" / f"{audio_slug(surface)}.mp3"
        if not target.is_file() or target.stat().st_size == 0:
            missing.append(str(target.relative_to(ROOT)))
    if missing and not allow_missing_audio:
        fail(f"MP3が不足しています: {', '.join(missing)}")
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-missing-audio", action="store_true", help="不足音声を報告だけにする")
    args = parser.parse_args()

    if not QUESTIONS_PATH.is_file() or not VOCAB_PATH.is_file():
        fail("生成済みJSONがありません")

    questions = load(QUESTIONS_PATH).get("questions", [])
    vocab = load(VOCAB_PATH)
    lemmas = load(LEMMA_PATH)
    origins = {str(key).lower(): value for key, value in load(ORIGINS_PATH).get("origins", {}).items()}
    excluded = {
        str(lemma).lower()
        for words in load(EXCLUDED_PATH).get("excluded", {}).values()
        for lemma in words
    }

    if len(questions) != 25:
        fail(f"設問数が不正です: {len(questions)}")
    if len(vocab.get("words", [])) != 84 or len(vocab.get("idioms", [])) != 16:
        fail(f"語句数が不正です: words={len(vocab.get('words', []))}, idioms={len(vocab.get('idioms', []))}")

    questions_by_q = {int(question["q"]): question for question in questions}
    items_by_q: dict[int, list[dict]] = {}
    for item in [*vocab.get("words", []), *vocab.get("idioms", [])]:
        items_by_q.setdefault(int(item["q"]), []).append(item)
    if sorted(questions_by_q) != list(range(1, 26)) or sorted(items_by_q) != list(range(1, 26)):
        fail("設問番号が1〜25で連続していません")

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    answer_positions = Counter()
    for q in range(1, 26):
        question = questions_by_q[q]
        items = items_by_q[q]
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        if len(choices) != 4 or len(items) != 4 or answer_index not in range(4):
            fail(f"Q{q}の4択または語彙項目が不正です")
        if len(set(choices)) != 4:
            fail(f"Q{q}の選択肢に重複があります")
        if len(BLANK_RE.findall(str(question.get("stem", "")))) != 1:
            fail(f"Q{q}の空所が1か所ではありません")
        if TRANSLATION_BLANK_RE.search(str(question.get("translation", ""))):
            fail(f"Q{q}の和訳に空所記号があります")
        if sum(bool(item.get("is_answer")) for item in items) != 1:
            fail(f"Q{q}の正答項目が1件ではありません")
        answer_positions[answer_index] += 1

        surfaces = [item_surface(item) for item in items]
        if len(set(surfaces)) != 4 or any(not surface for surface in surfaces):
            fail(f"Q{q}の語句が4件の一意な非空項目ではありません")
        if any(
            not any(surface_variants(choice) & surface_variants(surface) for surface in surfaces)
            for choice in choices
        ):
            fail(f"Q{q}の選択肢と語彙項目が対応しません")
        if not any(item_surface(item) == choices[answer_index] and item.get("is_answer") for item in items):
            fail(f"Q{q}のanswerIndexと正答項目が一致しません")
        if len({str(item.get("meaning", "")) for item in items}) != 4:
            fail(f"Q{q}の意味が重複しています")
        if len({str(item.get("pos", "")) for item in items}) != 1:
            fail(f"Q{q}の品詞ラベルが揃っていません")

        stem = str(question.get("stem", ""))
        for choice in choices:
            if re.search(rf"\b{re.escape(choice)}\b", stem, flags=re.IGNORECASE):
                fail(f"Q{q}の選択肢が設問文に露出しています: {choice}")
        for item in items:
            surface = item_surface(item)
            label = f"Q{q}/{surface}"
            if not all(str(item.get(field, "")).strip() for field in ("meaning", "pos", "example", "exampleTranslation", "etymology")):
                fail(f"{label}の必須フィールドが不足しています")
            if "word" in item and not IPA_RE.fullmatch(str(item.get("ipa", ""))):
                fail(f"{label}のIPAがありません")
            if "phrase" in item and not isinstance(item.get("coreImage"), dict):
                fail(f"{label}の核心イメージがありません")
            example = str(item.get("example", ""))
            if len(WORD_RE.findall(example)) < 8:
                fail(f"{label}の例文が8語未満です")
            if len(re.findall(re.escape(surface), example, flags=re.IGNORECASE)) != 1:
                fail(f"{label}の例文に見出し語句が1回ありません")
            key = example_skeleton(example, surface)
            if key in seen_examples:
                fail(f"例文の骨格が重複しています: {surface} / {seen_examples[key]}")
            seen_examples[key] = surface
            for variant in surface_variants(surface):
                if variant in seen_surfaces:
                    fail(f"同一セット内で語形が重複しています: {surface} / {seen_surfaces[variant]}")
                seen_surfaces[variant] = surface

    if [questions_by_q[q]["answerIndex"] for q in range(1, 26)] != EXPECTED_ANSWER_INDICES:
        fail("正答位置が第8回の登録値と一致しません")

    existing_grade: dict[str, str] = {}
    existing_phrases: set[str] = set()
    for path_string in glob.glob(str(DATA_DIR / "vocab_1_*.json")):
        path = Path(path_string)
        if path.name == VOCAB_PATH.name:
            continue
        data = load(path)
        for bucket in ("words", "idioms"):
            for item in data.get(bucket, []):
                surface = item_surface(item)
                for variant in surface_variants(surface):
                    existing_grade.setdefault(variant, f"{path.name}:{surface}")
                if bucket == "idioms":
                    existing_phrases.add(text_skeleton(surface))

    lemma_data = lemmas.get("lemmas", {})
    lemma_forms = {str(key).lower() for key in lemma_data} | {str(value).lower() for value in lemma_data.values()}
    for item in [*vocab.get("words", []), *vocab.get("idioms", [])]:
        surface = item_surface(item)
        if "word" in item and any(variant in lemma_forms for variant in surface_variants(surface)):
            fail(f"語がlemmas.jsonと衝突しています: {surface}")
        if "phrase" in item and text_skeleton(surface) in existing_phrases:
            fail(f"熟語phraseが既存1級データと重複しています: {surface}")
        for variant in surface_variants(surface):
            if variant in existing_grade:
                fail(f"1級既存語句と重複しています: {surface} / {existing_grade[variant]}")

    lemma_map = {str(surface).lower(): str(lemma).lower() for surface, lemma in lemma_data.items()}
    missing_origins = []
    for item in vocab.get("words", []):
        surface = item_surface(item)
        lemma = lemma_map.get(surface.lower(), surface.lower())
        if lemma not in origins and lemma not in excluded:
            missing_origins.append(f"{surface}=>{lemma}")
    if missing_origins:
        fail(f"語源またはC型除外記録がありません: {', '.join(missing_origins)}")

    flashcard_lemmas = {
        str(key).lower(): str(value).lower()
        for key, value in (lemmas.get("flashcardLemmas") or {}).items()
    }
    for surface, expected_lemma in FLASHCARD_VERB_LEMMAS.items():
        if flashcard_lemmas.get(surface) != expected_lemma:
            fail(f"暗記カード原形マップが不正です: {surface} -> {flashcard_lemmas.get(surface)}")

    missing_audio = check_audio(vocab, lemmas, args.allow_missing_audio)
    print(f"{DATASET_ID}: 25 questions / 100 items OK")
    print(f"answer positions: {dict(sorted(answer_positions.items()))}")
    print("etymology: 100 / 100; IPA: 84 / 84; core images: 16 / 16")
    if missing_audio:
        print(f"audio: missing {len(missing_audio)} file(s)")
    else:
        print("audio: 100 / 100 surface files present")


if __name__ == "__main__":
    main()
