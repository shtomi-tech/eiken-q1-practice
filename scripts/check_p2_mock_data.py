"""準2級模試第1回の新規生成データを内容面から検証する。"""

from __future__ import annotations

import json
import re
from pathlib import Path

from check_q1_data import check_dataset, example_skeleton, surface_variants


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATASET_ID = "eikenp2-mock-1"
VOCAB_PATH = DATA_DIR / "vocab_p2_mock-1.json"
QUESTIONS_PATH = DATA_DIR / "questions_p2_mock-1.json"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"ファイルがありません: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def item_surface(item: dict, bucket: str) -> str:
    return str(item.get("phrase") if bucket == "idioms" else item.get("word", "")).strip()


def fail(message: str) -> None:
    raise ValueError(f"{DATASET_ID}: {message}")


def check() -> None:
    vocab = load_json(VOCAB_PATH)
    questions_data = load_json(QUESTIONS_PATH)
    questions = questions_data.get("questions", [])
    words = vocab.get("words", [])
    idioms = vocab.get("idioms", [])
    all_items = [(item, "words") for item in words] + [(item, "idioms") for item in idioms]

    check_dataset(
        DATASET_ID,
        {
            "vocabUrl": "data/vocab_p2_mock-1.json",
            "questionsUrl": "data/questions_p2_mock-1.json",
        },
    )

    if (len(questions), len(words), len(idioms)) != (15, 40, 20):
        fail(f"件数が不正です: questions={len(questions)}, words={len(words)}, idioms={len(idioms)}")
    if sum(item.get("is_answer") is True for item, _ in all_items) != 15:
        fail("正答項目の件数が15ではありません")
    # 本番の準2級3セットは15問中6〜8問が会話文。自作セットも同じ帯に収める。
    conversation = sum(str(question.get("stem", "")).count("A:") for question in questions)
    if not 6 <= conversation <= 8:
        fail(f"会話文が6〜8問ではありません: {conversation}問")

    item_by_q: dict[int, list[tuple[dict, str]]] = {}
    for item, bucket in all_items:
        item_by_q.setdefault(int(item["q"]), []).append((item, bucket))

    seen_new: dict[str, str] = {}
    for item, bucket in all_items:
        surface = item_surface(item, bucket)
        if not surface:
            fail("見出し語句が空です")
        variants = surface_variants(surface)
        overlap = variants & seen_new.keys()
        if overlap:
            fail(f"同一セット内の語句が重複しています: {surface}")
        for variant in variants:
            seen_new[variant] = surface

        example = str(item.get("example", ""))
        if len(WORD_RE.findall(example)) < 8:
            fail(f"例文が8語未満です: {surface}")
        if len(re.findall(re.escape(surface), example, flags=re.IGNORECASE)) != 1:
            fail(f"例文に見出し語句がちょうど1回ありません: {surface}")
        key = example_skeleton(example, surface)
        if key in seen_new:
            fail(f"例文の骨格が重複しています: {surface}")
        seen_new[key] = f"example:{surface}"

    existing: dict[str, str] = {}
    for path in sorted(DATA_DIR.glob("vocab_p2_*.json")):
        if path.name == VOCAB_PATH.name:
            continue
        data = load_json(path)
        for bucket in ("words", "idioms"):
            for item in data.get(bucket, []):
                surface = item_surface(item, bucket)
                for variant in surface_variants(surface):
                    existing[variant] = f"{path.name}:{surface}"
    for item, bucket in all_items:
        surface = item_surface(item, bucket)
        overlap = surface_variants(surface) & existing.keys()
        if overlap:
            fail(f"既存準2級語彙と重複しています: {surface} ({existing[next(iter(overlap))]})")

    for question in questions:
        q = int(question["q"])
        stem = str(question.get("stem", ""))
        word_count = len(WORD_RE.findall(stem))
        if not 15 <= word_count <= 35:
            fail(f"Q{q}の設問文が15〜35語ではありません: {word_count}語")
        if BLANK_RE.search(str(question.get("translation", ""))):
            fail(f"Q{q}の訳に空所記号があります")
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        q_items = item_by_q[q]
        if sum(item.get("is_answer") is True for item, _ in q_items) != 1:
            fail(f"Q{q}の正答項目が1件ではありません")
        correct_item = next(item for item, _ in q_items if item.get("is_answer") is True)
        if choices[answer_index] != item_surface(
            correct_item,
            "idioms" if "phrase" in correct_item else "words",
        ):
            fail(f"Q{q}の正答位置と語彙データが一致しません")
        if re.search(re.escape(choices[answer_index]), stem, flags=re.IGNORECASE):
            fail(f"Q{q}の正答語句が設問文に出ています")
        if len({item.get("pos") for item, _ in q_items}) != 1:
            fail(f"Q{q}の4択の品詞が一致していません")

    print(f"{DATASET_ID}: content OK (15 questions / 60 items)")


if __name__ == "__main__":
    check()
