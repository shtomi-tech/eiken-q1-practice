"""英検5級 2026年度第1回・大問1の内容と生成物を検査する。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
QUESTIONS_PATH = DATA_DIR / "questions_5_2026-1.json"
VOCAB_PATH = DATA_DIR / "vocab_5_2026-1.json"
DATASET_ID = "eiken5-2026-1"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"\(\s+\)")
TRANSLATION_BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")

EXPECTED_CHOICES = [
    ["music", "paint", "newspaper", "lunch"],
    ["books", "teeth", "fruits", "people"],
    ["fork", "dictionary", "kite", "racket"],
    ["sleep", "drink", "arrive", "talk"],
    ["pool", "station", "library", "mountain"],
    ["fast", "cold", "young", "tall"],
    ["know", "leave", "take", "eat"],
    ["look", "see", "play", "stand"],
    ["under", "with", "about", "at"],
    ["go", "want", "close", "play"],
    ["after", "about", "down", "on"],
    ["sing", "talk", "close", "wake"],
    ["his", "he", "him", "us"],
    ["I", "my", "me", "mine"],
    ["is studying", "are studying", "am studying", "studying"],
]
EXPECTED_ANSWERS = [2, 3, 3, 1, 3, 3, 1, 1, 3, 0, 0, 3, 0, 3, 0]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise ValueError(f"{DATASET_ID}: {message}")


def surface_occurrences(text: str, surface: str) -> int:
    pattern = rf"(?<![A-Za-z]){re.escape(surface)}(?![A-Za-z])"
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def example_skeleton(example: str, surface: str) -> str:
    pattern = rf"(?<![A-Za-z]){re.escape(surface)}(?![A-Za-z])"
    return re.sub(pattern, "( )", example, count=1, flags=re.IGNORECASE).casefold()


def main() -> None:
    if not QUESTIONS_PATH.is_file() or not VOCAB_PATH.is_file():
        fail("生成済みJSONがありません")

    questions_data = load(QUESTIONS_PATH)
    vocab = load(VOCAB_PATH)
    questions = questions_data.get("questions", [])
    words = vocab.get("words", [])
    idioms = vocab.get("idioms", [])

    if len(questions) != 15 or len(words) != 60 or idioms:
        fail(f"件数が不正です: questions={len(questions)}, words={len(words)}, idioms={len(idioms)}")
    if questions_data.get("meta") != vocab.get("meta"):
        fail("問題JSONと語彙JSONのmetaが一致しません")
    meta = vocab.get("meta", {})
    if meta.get("source_problem_url") != "https://www.eiken.or.jp/eiken/exam/kakomon/2026-1-1ji-5kyu.pdf":
        fail("問題冊子の出典URLが不正です")
    if meta.get("source_answer_url") != "https://www.eiken.or.jp/eiken/result/pdf/202601F5kyu.pdf":
        fail("解答の出典URLが不正です")
    if meta.get("counts") != {"words": 60, "idioms": 0, "total": 60}:
        fail(f"meta.countsが不正です: {meta.get('counts')}")

    items_by_q: dict[int, list[dict]] = {}
    for item in words:
        if not item.get("itemKey"):
            fail("itemKeyがありません")
        items_by_q.setdefault(int(item.get("q", 0)), []).append(item)
    if sorted(items_by_q) != list(range(1, 16)):
        fail("語彙の設問番号が1〜15で連続していません")

    answer_positions = Counter()
    seen_item_keys: set[str] = set()
    seen_example_skeletons: set[str] = set()
    for q, question in enumerate(questions, start=1):
        if question.get("q") != q:
            fail(f"設問番号が不正です: {question.get('q')}")
        choices = question.get("choices", [])
        if choices != EXPECTED_CHOICES[q - 1]:
            fail(f"Q{q}の選択肢が公式問題と一致しません")
        answer_index = question.get("answerIndex")
        if answer_index != EXPECTED_ANSWERS[q - 1]:
            fail(f"Q{q}の正答位置が公式解答と一致しません")
        answer_positions[answer_index] += 1
        if len(BLANK_RE.findall(str(question.get("stem", "")))) != 1:
            fail(f"Q{q}の空所が1か所ではありません")
        if TRANSLATION_BLANK_RE.search(str(question.get("translation", ""))):
            fail(f"Q{q}の和訳に空所記号があります")

        items = items_by_q.get(q, [])
        if len(items) != 4:
            fail(f"Q{q}の語彙項目が4件ではありません")
        item_surfaces = [str(item.get("word", "")) for item in items]
        if item_surfaces != choices:
            fail(f"Q{q}の語彙と選択肢の順序が一致しません")
        if sum(bool(item.get("is_answer")) for item in items) != 1:
            fail(f"Q{q}の正答項目が1件ではありません")
        if not items[answer_index].get("is_answer"):
            fail(f"Q{q}の正答項目の位置が不正です")
        if len({str(item.get("meaning", "")) for item in items}) != 4:
            fail(f"Q{q}の意味が重複しています")
        if len({str(item.get("pos", "")) for item in items}) != 1:
            fail(f"Q{q}の品詞ラベルが揃っていません")

        for item in items:
            key = str(item["itemKey"])
            if key in seen_item_keys:
                fail(f"itemKeyが重複しています: {key}")
            seen_item_keys.add(key)
            surface = str(item.get("word", ""))
            example = str(item.get("example", ""))
            if not item.get("meaning") or not item.get("pos") or not item.get("exampleTranslation"):
                fail(f"{surface}の学習情報が不足しています")
            if len(WORD_RE.findall(example)) < 8:
                fail(f"Q{q}/{surface}の例文が8語未満です")
            if surface_occurrences(example, surface) != 1:
                fail(f"Q{q}/{surface}の例文に見出し語句が1回ありません")
            skeleton = example_skeleton(example, surface)
            if skeleton in seen_example_skeletons:
                fail(f"例文の骨格が重複しています: Q{q}/{surface}")
            seen_example_skeletons.add(skeleton)

    if len(seen_item_keys) != 60:
        fail(f"itemKey数が不正です: {len(seen_item_keys)}")

    print(f"{DATASET_ID}: 15 questions / 60 words OK")
    print(f"answer positions: {dict(sorted(answer_positions.items()))}")
    print("official source/answers: OK")


if __name__ == "__main__":
    main()
