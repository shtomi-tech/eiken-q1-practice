"""英検1級模試第6回の内容面を検査する。"""

from __future__ import annotations

import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))
from check_q1_data import surface_variants  # noqa: E402


DATASET_ID = "eiken1-mock-6"
QUESTIONS_PATH = DATA_DIR / "questions_1_mock-6.json"
VOCAB_PATH = DATA_DIR / "vocab_1_mock-6.json"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"\(\s+\)")
TRANSLATION_BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def item_surface(item: dict) -> str:
    return str(item.get("phrase") or item.get("word") or "").strip()


def text_skeleton(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def example_skeleton(example: str, surface: str) -> str:
    return text_skeleton(re.sub(re.escape(surface), "( )", example, count=1, flags=re.IGNORECASE))


def fail(message: str) -> None:
    raise ValueError(f"{DATASET_ID}: {message}")


def main() -> None:
    if not QUESTIONS_PATH.is_file() or not VOCAB_PATH.is_file():
        fail("生成済みJSONがありません")
    questions = load(QUESTIONS_PATH).get("questions", [])
    vocab = load(VOCAB_PATH)
    if len(questions) != 25:
        fail(f"設問数が不正です: {len(questions)}")

    all_items = [
        (item, "word")
        for item in vocab.get("words", [])
    ] + [
        (item, "phrase")
        for item in vocab.get("idioms", [])
    ]
    if len(vocab.get("words", [])) != 84 or len(vocab.get("idioms", [])) != 16:
        fail(f"語句数が不正です: words={len(vocab.get('words', []))}, idioms={len(vocab.get('idioms', []))}")

    questions_by_q = {int(question["q"]): question for question in questions}
    items_by_q: dict[int, list[dict]] = {}
    for item, _ in all_items:
        items_by_q.setdefault(int(item["q"]), []).append(item)
    if sorted(questions_by_q) != list(range(1, 26)) or sorted(items_by_q) != list(range(1, 26)):
        fail("設問番号が1〜25で連続していません")

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    answer_positions = Counter()
    for q in range(1, 26):
        question = questions_by_q[q]
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        items = items_by_q[q]
        if len(choices) != 4 or len(items) != 4 or answer_index not in range(4):
            fail(f"Q{q}の4択または語彙項目が不正です")
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
        if any(not any(surface_variants(choice) & surface_variants(item_surface(item)) for item in items) for choice in choices):
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
            if len(WORD_RE.findall(example)) < 8:
                fail(f"Q{q}/{surface}の例文が8語未満です")
            if len(re.findall(re.escape(surface), example, flags=re.IGNORECASE)) != 1:
                fail(f"Q{q}/{surface}の例文に見出し語句が1回ありません")
            key = example_skeleton(example, surface)
            if key in seen_examples:
                fail(f"例文の骨格が重複しています: {surface} / {seen_examples[key]}")
            seen_examples[key] = surface
            for variant in surface_variants(surface):
                if variant in seen_surfaces:
                    fail(f"同一セット内または既存セットと語形が重複しています: {surface} / {seen_surfaces[variant]}")
                seen_surfaces[variant] = surface

    existing_grade: dict[str, str] = {}
    for path in glob.glob(str(DATA_DIR / "vocab_1_*.json")):
        if Path(path).name == VOCAB_PATH.name:
            continue
        data = load(Path(path))
        for bucket in ("words", "idioms"):
            for item in data.get(bucket, []):
                surface = item_surface(item)
                for variant in surface_variants(surface):
                    existing_grade.setdefault(variant, f"{Path(path).name}:{surface}")
    lemmas = load(DATA_DIR / "lemmas.json").get("lemmas", {})
    lemma_forms = {str(key).lower() for key in lemmas} | {str(value).lower() for value in lemmas.values()}
    existing_phrases = set()
    for path in glob.glob(str(DATA_DIR / "vocab_*.json")):
        data = load(Path(path))
        existing_phrases.update(text_skeleton(item.get("phrase", "")) for item in data.get("idioms", []))

    for item, bucket in all_items:
        surface = item_surface(item)
        if bucket == "word" and surface.casefold() in lemma_forms:
            fail(f"語がlemmas.jsonと衝突しています: {surface}")
        if bucket == "phrase" and text_skeleton(surface) in existing_phrases - {text_skeleton(surface)}:
            fail(f"熟語phraseが既存データと重複しています: {surface}")
        for variant in surface_variants(surface):
            if variant in existing_grade:
                fail(f"1級既存語句と重複しています: {surface} / {existing_grade[variant]}")

    core_count = sum(bool(item.get("coreImage")) for item in vocab.get("idioms", []))
    if core_count != 16:
        fail(f"核心イメージの付与数が想定と違います: {core_count}")
    if any(not item.get("coreImage") for item in vocab.get("idioms", [])):
        fail("熟語16件すべてに核心イメージが必要です")

    print(f"{DATASET_ID}: 25 questions / 100 items OK")
    print(f"answer positions: {dict(sorted(answer_positions.items()))}")
    print(f"core images: {core_count} / 16 idioms")


if __name__ == "__main__":
    main()
