"""英検1級模試第5回が、模試第6回の品質基準を満たすか検査する。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
QUESTIONS_PATH = DATA_DIR / "questions_1_mock-5.json"
VOCAB_PATH = DATA_DIR / "vocab_1_mock-5.json"
LEMMAS_PATH = DATA_DIR / "lemmas.json"
ORIGINS_PATH = DATA_DIR / "word_origins.json"
EXCLUDED_PATH = DATA_DIR / "word_origin_excluded.json"
AUDIO_DIR = ROOT / "assets" / "audio" / "vocab" / "1" / "mock-5"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"\(\s*\)|（\s*）")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise ValueError(f"eiken1-mock-5: {message}")


def item_surface(item: dict) -> str:
    return str(item.get("phrase") or item.get("word") or "").strip()


def surface_variants(value: str) -> set[str]:
    base = " ".join(str(value or "").lower().split())
    variants = {base}
    if base.endswith("ies") and len(base) > 3:
        variants.add(base[:-3] + "y")
    if base.endswith("ied") and len(base) > 3:
        variants.add(base[:-3] + "y")
    if base.endswith("es") and len(base) > 3:
        variants.add(base[:-2])
    if base.endswith("s") and len(base) > 2:
        variants.add(base[:-1])
    if base.endswith("ed") and len(base) > 3:
        stem = base[:-2]
        variants.add(stem)
        if len(stem) > 1 and stem[-1] == stem[-2]:
            variants.add(stem[:-1])
        if stem.endswith("i"):
            variants.add(stem[:-1] + "y")
        variants.add(stem + "e")
    if base.endswith("ing") and len(base) > 4:
        stem = base[:-3]
        variants.add(stem)
        if len(stem) > 1 and stem[-1] == stem[-2]:
            variants.add(stem[:-1])
        variants.add(stem + "e")
    return variants


def example_skeleton(example: str, surface: str) -> str:
    replaced = re.sub(re.escape(surface), "( )", example, count=1, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", replaced.strip()).casefold()


def audio_slug(value: str) -> str:
    normalized = str(value or "").lower().replace("’", "'")
    normalized = re.sub(r"\b(one's|his|her|my|your|our|their|its)\b", "@poss", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def excluded_words(data: dict) -> set[str]:
    return {
        str(lemma).lower()
        for group in data.get("excluded", {}).values()
        for lemma in group
    }


def check_audio(vocab: dict, lemmas: dict, allow_missing_audio: bool) -> list[str]:
    missing: list[str] = []
    for item in vocab.get("words", []):
        surface = item_surface(item)
        target = AUDIO_DIR / f"{audio_slug(surface)}.mp3"
        if not target.is_file() or target.stat().st_size == 0:
            missing.append(str(target.relative_to(ROOT)))
        flashcard_lemma = lemmas.get("flashcardLemmas", {}).get(surface.lower())
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
    parser.add_argument(
        "--allow-missing-audio",
        action="store_true",
        help="不足音声を報告だけにする",
    )
    args = parser.parse_args()

    if not QUESTIONS_PATH.is_file() or not VOCAB_PATH.is_file():
        fail("生成済みJSONがありません")

    questions = load(QUESTIONS_PATH).get("questions", [])
    vocab = load(VOCAB_PATH)
    lemmas = load(LEMMAS_PATH)
    origins = load(ORIGINS_PATH).get("origins", {})
    excluded = excluded_words(load(EXCLUDED_PATH))

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

    seen_examples: dict[str, str] = {}
    for q in range(1, 26):
        question = questions_by_q[q]
        items = items_by_q[q]
        choices = question.get("choices", [])
        if len(choices) != 4 or len(items) != 4 or question.get("answerIndex") not in range(4):
            fail(f"Q{q}の4択または語彙項目が不正です")
        if len(BLANK_RE.findall(str(question.get("stem", "")))) != 1:
            fail(f"Q{q}の空所が1か所ではありません")
        if BLANK_RE.search(str(question.get("translation", ""))):
            fail(f"Q{q}の和訳に空所記号があります")
        if sum(bool(item.get("is_answer")) for item in items) != 1:
            fail(f"Q{q}の正答項目が1件ではありません")
        surfaces = [item_surface(item) for item in items]
        if len(set(surfaces)) != 4 or any(not surface for surface in surfaces):
            fail(f"Q{q}の語句が4件の一意な非空項目ではありません")
        if any(
            not any(surface_variants(choice) & surface_variants(surface) for surface in surfaces)
            for choice in choices
        ):
            fail(f"Q{q}の選択肢と語彙項目が一致しません")
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
            example = str(item.get("example", ""))
            if not item.get("meaning") or not item.get("pos") or not item.get("exampleTranslation"):
                fail(f"Q{q}/{surface}の必須フィールドが不足しています")
            if not item.get("etymology"):
                fail(f"Q{q}/{surface}の語源説明がありません")
            if item.get("word") and not re.fullmatch(r"/.+/", str(item.get("ipa", ""))):
                fail(f"Q{q}/{surface}のIPAがありません")
            if len(WORD_RE.findall(example)) < 8:
                fail(f"Q{q}/{surface}の例文が8語未満です")
            if len(re.findall(re.escape(surface), example, flags=re.IGNORECASE)) != 1:
                fail(f"Q{q}/{surface}の例文に見出し語句が1回ありません")
            key = example_skeleton(example, surface)
            if key in seen_examples:
                fail(f"例文の骨格が重複しています: {surface} / {seen_examples[key]}")
            seen_examples[key] = surface
        if any("coreImage" not in item for item in vocab.get("idioms", []) if int(item["q"]) == q):
            fail(f"Q{q}の熟語に核心イメージがありません")

    lemma_map = {
        str(surface).lower(): str(lemma).lower()
        for surface, lemma in lemmas.get("lemmas", {}).items()
    }
    missing_origins: list[str] = []
    for item in vocab.get("words", []):
        surface = item_surface(item)
        lemma = lemma_map.get(surface.lower(), surface.lower())
        if lemma not in origins and lemma not in excluded:
            missing_origins.append(f"{surface}=>{lemma}")
    if missing_origins:
        fail(f"語源またはC型除外記録がありません: {', '.join(missing_origins)}")

    missing_audio = check_audio(vocab, lemmas, args.allow_missing_audio)
    print("eiken1-mock-5: 25 questions / 100 items OK")
    print(f"etymology: 100 / 100; IPA: 84 / 84; core images: 16 / 16")
    print(f"word origins: {84 - len([item for item in vocab.get('words', []) if lemma_map.get(item_surface(item).lower(), item_surface(item).lower()) in excluded])} / 84; C: {len([item for item in vocab.get('words', []) if lemma_map.get(item_surface(item).lower(), item_surface(item).lower()) in excluded])}")
    if missing_audio:
        print(f"audio: missing {len(missing_audio)} file(s) ({', '.join(missing_audio)})")
    else:
        print("audio: 100 / 100 surface files and all flashcard lemma files present")


if __name__ == "__main__":
    main()
