"""英検2級 Chapter 3 模擬テスト第3回の内容と重複を検証する。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from check_q1_data import check_dataset, example_skeleton, surface_variants, text_skeleton


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
VOCAB_PATH = DATA_DIR / "vocab_2_mock-3.json"
QUESTIONS_PATH = DATA_DIR / "questions_2_mock-3.json"
DATASET_ID = "eiken2-mock-3"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"ファイルがありません: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def surface(item: dict, bucket: str) -> str:
    return str(item.get("phrase") if bucket == "idioms" else item.get("word", "")).strip()


def fail(message: str) -> None:
    raise ValueError(f"{DATASET_ID}: {message}")


def is_eiken2_file(path: Path) -> bool:
    return bool(re.fullmatch(r"vocab_20\d{2}-\d+\.json|vocab_2_mock-\d+\.json", path.name))


def existing_grade_surfaces(exclude: str) -> dict[str, str]:
    existing: dict[str, str] = {}
    for path in sorted(DATA_DIR.glob("vocab_*.json")):
        if path.name == exclude or not is_eiken2_file(path):
            continue
        data = load_json(path)
        for bucket in ("words", "idioms"):
            for item in data.get(bucket, []):
                value = surface(item, bucket)
                for variant in surface_variants(value):
                    existing[variant] = f"{path.name}:{value}"
    return existing


def phrase_owners(exclude: str) -> dict[str, list[str]]:
    owners: dict[str, list[str]] = {}
    for path in sorted(DATA_DIR.glob("vocab_*.json")):
        if path.name == exclude:
            continue
        data = load_json(path)
        for item in data.get("idioms", []):
            phrase = text_skeleton(item.get("phrase", ""))
            owners.setdefault(phrase, []).append(f"{path.name}:{item.get('phrase', '')}")
    return owners


def lemma_forms() -> set[str]:
    data = load_json(DATA_DIR / "lemmas.json")
    forms: set[str] = set()
    for key in ("lemmas", "flashcardLemmas"):
        mapping = data.get(key, {})
        if isinstance(mapping, dict):
            forms.update(str(value).strip().lower() for value in mapping)
            forms.update(str(value).strip().lower() for value in mapping.values())
    return {value for value in forms if value}


def word_surface_forms(value: str) -> set[str]:
    base = text_skeleton(value)
    forms = {base}
    if not base or " " in base:
        return forms
    if base.endswith("y") and len(base) > 1 and base[-2] not in "aeiou":
        forms.add(base[:-1] + "ies")
    else:
        forms.add(base + "s")
    forms.add(base[:-1] + "d" if base.endswith("e") else base + "ed")
    forms.add(base[:-1] + "ing" if base.endswith("e") else base + "ing")
    return forms


def choice_in_stem(choice: str, stem: str) -> bool:
    forms = {text_skeleton(choice)} if " " in choice else word_surface_forms(choice)
    return any(
        re.search(rf"(?<![A-Za-z]){re.escape(form)}(?![A-Za-z])", stem, flags=re.IGNORECASE)
        for form in forms
    )


def check() -> None:
    vocab = load_json(VOCAB_PATH)
    questions_data = load_json(QUESTIONS_PATH)
    questions = questions_data.get("questions", [])
    words = vocab.get("words", [])
    idioms = vocab.get("idioms", [])
    all_items = [(item, "words") for item in words] + [(item, "idioms") for item in idioms]

    check_dataset(
        DATASET_ID,
        {"vocabUrl": f"data/{VOCAB_PATH.name}", "questionsUrl": f"data/{QUESTIONS_PATH.name}"},
    )
    if (len(questions), len(words), len(idioms)) != (20, 63, 17):
        fail(f"件数が不正です: questions={len(questions)}, words={len(words)}, idioms={len(idioms)}")
    if sum(item.get("is_answer") is True for item, _ in all_items) != 20:
        fail("正答項目の件数が20ではありません")

    answer_counts = Counter(int(question["answerIndex"]) for question in questions)
    answer_distribution = [answer_counts[index] for index in range(4)]
    if answer_distribution != [6, 8, 2, 4]:
        fail(f"正答位置の分布が想定と違います: {answer_distribution}")
    if sum(str(question.get("stem", "")).count("A:") for question in questions) != 8:
        fail("会話文の件数が原稿の8問と一致しません")

    items_by_q: dict[int, list[tuple[dict, str]]] = {}
    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    for item, bucket in all_items:
        value = surface(item, bucket)
        if not value:
            fail("見出し語句が空です")
        variants = surface_variants(value)
        if variants & seen_surfaces.keys():
            fail(f"同一セット内の語句が重複しています: {value}")
        for variant in variants:
            seen_surfaces[variant] = value
        items_by_q.setdefault(int(item["q"]), []).append((item, bucket))

        example = str(item.get("example", ""))
        if len(WORD_RE.findall(example)) < 8:
            fail(f"例文が8語未満です: {value}")
        if len(re.findall(re.escape(value), example, flags=re.IGNORECASE)) != 1:
            fail(f"例文に見出し語句がちょうど1回ありません: {value}")
        key = example_skeleton(example, value)
        if key in seen_examples:
            fail(f"例文の骨格が重複しています: {value}")
        seen_examples[key] = value

    existing = existing_grade_surfaces(VOCAB_PATH.name)
    for item, bucket in all_items:
        value = surface(item, bucket)
        owners = [existing[variant] for variant in surface_variants(value) if variant in existing]
        if owners:
            fail(f"既存2級語彙と重複しています: {value} ({owners[0]})")

    forms = lemma_forms()
    for item, bucket in all_items:
        value = surface(item, bucket)
        if " " not in value and value.lower() in forms:
            fail(f"新語がlemmas.jsonのキー・原形値と衝突しています: {value}")

    owners_by_phrase = phrase_owners(VOCAB_PATH.name)
    for item in idioms:
        value = surface(item, "idioms")
        owners = owners_by_phrase.get(text_skeleton(value), [])
        if owners:
            fail(f"全配信データの熟語phraseと重複しています: {value} ({owners[0]})")
        if not isinstance(item.get("coreImage"), dict):
            fail(f"熟語にcoreImageがありません: {value}")

    item_surfaces = {q: [(surface(item, bucket), item) for item, bucket in pairs] for q, pairs in items_by_q.items()}
    for question in questions:
        q = int(question["q"])
        stem = str(question.get("stem", ""))
        choices = question.get("choices", [])
        if not 12 <= len(WORD_RE.findall(stem)) <= 45:
            fail(f"Q{q}の設問文の語数が12〜45語ではありません")
        if stem.count("(   )") != 1:
            fail(f"Q{q}の設問文の空所が1か所ではありません")
        if BLANK_RE.search(str(question.get("translation", ""))):
            fail(f"Q{q}の訳に空所記号があります")
        if len(choices) != 4 or len(set(choices)) != 4:
            fail(f"Q{q}の選択肢が4件の一意な値ではありません")
        q_items = item_surfaces.get(q, [])
        if len(q_items) != 4:
            fail(f"Q{q}の語彙項目が4件ではありません")
        if sum(item.get("is_answer") is True for _, item in q_items) != 1:
            fail(f"Q{q}の正答項目が1件ではありません")
        correct = next(value for value, item in q_items if item.get("is_answer") is True)
        if choices[int(question["answerIndex"])] != correct:
            fail(f"Q{q}の正答位置と語彙データが一致しません")
        for choice in choices:
            if choice_in_stem(choice, stem):
                fail(f"Q{q}の選択肢が設問文に出ています: {choice}")

    print(f"{DATASET_ID}: content OK (20 questions / 80 items; 63 words, 17 idioms)")


if __name__ == "__main__":
    check()
