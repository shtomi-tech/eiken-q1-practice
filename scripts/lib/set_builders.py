"""セット単位の生成スクリプト（scripts/build_q1_*_data.py）が共有する組み立て・検証処理。

各生成スクリプトは問題・語彙の定義だけを持ち、ここの run_* を呼ぶ。
出力を変えない変更かどうかは scripts/verify-builder-output.py で確認する。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
BLANK_RE = re.compile(r"\(\s+\)")
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}

def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def build_q1_mock(
    round_id: str, QUESTIONS: list[dict], DETAILS: dict, CORE_IMAGES: dict
) -> tuple[dict, dict]:
    """英検1級 自作模試（第10回以降の形式）の語彙・問題データを検証して組み立てる。"""
    if len(QUESTIONS) != 25:
        raise ValueError(f"模試第{round_id.removeprefix('mock-')}回は25問である必要があります")

    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != len(set(choices)):
        raise ValueError("選択肢に重複があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    extra = sorted(set(DETAILS) - set(choices))
    if extra:
        raise ValueError(f"使われていない語句情報があります: {extra}")

    for question in QUESTIONS:
        if question["stem"].count("(   )") != 1:
            raise ValueError(f"空所は1か所である必要があります: {question['stem'][:40]}")
        stem_words = {word.lower() for word in WORD_RE.findall(question["stem"])}
        for choice in question["choices"]:
            # 熟語の不変化詞・前置詞は機能語なので、本文に出ていても手掛かりにならない。
            for part in choice.split():
                if part.lower() in PARTICLES:
                    continue
                if part.lower() in stem_words:
                    raise ValueError(f"選択肢の語が設問文に出ています: {choice} / {part}")
        for mark in ("(", "（"):
            if mark in question["translation"]:
                raise ValueError(f"和訳に空所記号が残っています: {question['translation'][:30]}")
        meanings = [DETAILS[choice][0] for choice in question["choices"]]
        if len(meanings) != len(set(meanings)):
            raise ValueError(f"同一設問内で意味が重複しています: {question['choices']}")
        parts_of_speech = {DETAILS[choice][1] for choice in question["choices"]}
        if len(parts_of_speech) != 1:
            raise ValueError(f"同一設問内で品詞が揃っていません: {question['choices']}")

    answer_positions = [question["answerIndex"] for question in QUESTIONS]
    for index in range(4):
        if answer_positions.count(index) < 4:
            raise ValueError(f"正答位置が偏っています: {[answer_positions.count(i) for i in range(4)]}")

    meta = {
        "grade": "英検1級",
        "round": round_id,
        "section": "Reading 大問1（語句空所補充）",
        "source": f"AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の {round_id} 割り当てに従う",
        "counts": {"words": 84, "idioms": 16, "total": 100},
    }
    question_data = {
        "meta": meta,
        "questions": [
            {"q": index, **question} for index, question in enumerate(QUESTIONS, start=1)
        ],
    }

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    words = []
    idioms = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            meaning, pos, example, example_translation = DETAILS[choice]
            if len(WORD_RE.findall(example)) < 8:
                raise ValueError(f"{choice}の例文が8語未満です")
            pattern = r"\b" + re.escape(choice) + r"\b"
            if len(re.findall(pattern, example, flags=re.IGNORECASE)) != 1:
                raise ValueError(f"{choice}の例文に見出し語句が1回ありません")
            example_key = re.sub(pattern, "( )", example, count=1, flags=re.IGNORECASE)
            example_key = " ".join(example_key.lower().split())
            if example_key in seen_examples:
                raise ValueError(f"例文の骨格が重複しています: {choice} / {seen_examples[example_key]}")
            seen_examples[example_key] = choice
            for variant in surface_variants(choice):
                if variant in seen_surfaces:
                    raise ValueError(f"同一セット内で語形が重複しています: {choice} / {seen_surfaces[variant]}")
                seen_surfaces[variant] = choice

            item = {
                "q": q,
                "is_answer": index == question["answerIndex"],
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
                "pos": pos,
            }
            if " " in choice:
                if choice not in CORE_IMAGES:
                    raise ValueError(f"核心イメージがありません: {choice}")
                item["phrase"] = choice
                item["coreImage"] = CORE_IMAGES[choice]
                idioms.append(item)
            else:
                item["word"] = choice
                words.append(item)

    if (len(words), len(idioms)) != (84, 16):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idioms)}")
    return {"meta": meta, "words": words, "idioms": idioms}, question_data


def run_q1_mock(round_id: str, questions: list[dict], details: dict, core_images: dict) -> None:
    """英検1級 自作模試（第10回以降の形式）の vocab/questions JSON を data/ に書き出す。"""
    vocab, question_data = build_q1_mock(round_id, questions, details, core_images)
    write_json(DATA_DIR / f"vocab_1_{round_id}.json", vocab)
    write_json(DATA_DIR / f"questions_1_{round_id}.json", question_data)
    print(f"{round_id}: 25 questions / 100 items (84 words, 16 idioms)")


def build_eiken2_mock(
    round_id: str, QUESTIONS: list[dict], DETAILS: dict, CORE_IMAGES: dict, IDIOM_QUESTIONS
) -> tuple[dict, dict]:
    """英検2級 Chapter 3 模擬テストの語彙・問題データを検証して組み立てる。"""
    if len(QUESTIONS) != 20:
        raise ValueError(f"2級模試第{round_id.removeprefix('mock-')}回は20問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 80 or len(choices) != len(set(choices)):
        raise ValueError("選択肢は重複しない80件である必要があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    idioms = {
        choice
        for q, question in enumerate(QUESTIONS, start=1)
        if q in IDIOM_QUESTIONS
        for choice in question["choices"]
    }
    if idioms != set(CORE_IMAGES):
        raise ValueError(f"核心イメージの定義が一致しません: {sorted(idioms ^ set(CORE_IMAGES))}")

    meta = {
        "grade": "英検2級",
        "round": round_id,
        "section": "Reading 大問1（語句空所補充）",
        "source": f"ユーザー提供のChapter 3 模擬テスト第{round_id.removeprefix('mock-')}回原稿を基に構造化。訳・例文・語句情報は学習用に作成",
        "counts": {"questions": 20, "words": 56, "idioms": 24, "total": 80},
    }
    question_data = {
        "meta": meta,
        "questions": [{"q": index, **question} for index, question in enumerate(QUESTIONS, start=1)],
    }
    words = []
    idiom_items = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            meaning, pos, example, example_translation = DETAILS[choice]
            item = {
                "q": q,
                "is_answer": index == question["answerIndex"],
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
                "pos": pos,
            }
            if q in IDIOM_QUESTIONS:
                item["type"] = "idiom"
                item["phrase"] = choice
                item["coreImage"] = CORE_IMAGES[choice]
                idiom_items.append(item)
            else:
                item["word"] = choice
                words.append(item)
    if (len(words), len(idiom_items)) != (56, 24):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idiom_items)}")
    return {"meta": meta, "words": words, "idioms": idiom_items}, question_data


def run_eiken2_mock(
    round_id: str, QUESTIONS: list[dict], DETAILS: dict, CORE_IMAGES: dict, IDIOM_QUESTIONS
) -> None:
    """英検2級 Chapter 3 模擬テストの vocab/questions JSON を data/ に書き出す。"""
    vocab, questions = build_eiken2_mock(round_id, QUESTIONS, DETAILS, CORE_IMAGES, IDIOM_QUESTIONS)
    write_json(DATA_DIR / f"vocab_2_{round_id}.json", vocab)
    write_json(DATA_DIR / f"questions_2_{round_id}.json", questions)
    print(f"eiken2 {round_id}: 20 questions / 80 items (56 words, 24 idioms)")


def build_p2_mock(
    round_id: str, QUESTIONS: list[dict], DETAILS: dict, CORE_IMAGES: dict
) -> tuple[dict, dict]:
    """英検準2級 自作模試（第2回以降の形式）の語彙・問題データを検証して組み立てる。"""
    if len(QUESTIONS) != 15:
        raise ValueError(f"準2級模試第{round_id.removeprefix('mock-')}回は15問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 60 or len(choices) != len(set(choices)):
        raise ValueError("選択肢は重複しない60件である必要があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    idioms = {choice for choice in choices if " " in choice}
    if idioms != set(CORE_IMAGES):
        raise ValueError(f"核心イメージの定義が一致しません: {sorted(idioms ^ set(CORE_IMAGES))}")
    if sum(bool(CORE_IMAGES[phrase].get("particle")) for phrase in idioms) < 4:
        raise ValueError("句動詞の核心イメージが4件未満です")

    meta = {
        "grade": "英検準2級",
        "round": round_id,
        "section": "Reading 大問1（語句空所補充）",
        "source": "AI生成（英検過去問の引用なし）・人手校閲",
        "counts": {"questions": 15, "words": 40, "idioms": 20, "total": 60},
    }
    question_data = {
        "meta": meta,
        "questions": [{"q": index, **question} for index, question in enumerate(QUESTIONS, start=1)],
    }
    words = []
    idiom_items = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            meaning, pos, example, example_translation = DETAILS[choice]
            item = {
                "q": q,
                "is_answer": index == question["answerIndex"],
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
                "pos": pos,
            }
            if " " in choice:
                item["type"] = "idiom"
                item["phrase"] = choice
                item["coreImage"] = CORE_IMAGES[choice]
                idiom_items.append(item)
            else:
                item["word"] = choice
                words.append(item)
    if (len(words), len(idiom_items)) != (40, 20):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idiom_items)}")
    return {"meta": meta, "words": words, "idioms": idiom_items}, question_data


def run_p2_mock(
    round_id: str, QUESTIONS: list[dict], DETAILS: dict, CORE_IMAGES: dict
) -> None:
    """英検準2級 自作模試（第2回以降の形式）の vocab/questions JSON を data/ に書き出す。"""
    vocab, questions = build_p2_mock(round_id, QUESTIONS, DETAILS, CORE_IMAGES)
    write_json(DATA_DIR / f"vocab_p2_{round_id}.json", vocab)
    write_json(DATA_DIR / f"questions_p2_{round_id}.json", questions)
    print(f"p2 {round_id}: 15 questions / 60 items (40 words, 20 idioms)")


def build_q1_mock_8_9(
    round_id: str, QUESTIONS: list[dict], DETAILS: dict, CORE_IMAGES: dict, SOURCE: str
) -> tuple[dict, dict]:
    """英検1級 模試第8・9回（ユーザー提供画像ベースの形式）の語彙・問題データを検証して組み立てる。"""
    if len(QUESTIONS) != 25:
        raise ValueError(f"模試第{round_id.removeprefix('mock-')}回は25問である必要があります")

    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != len(set(choices)):
        raise ValueError("選択肢に重複があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    for index, question in enumerate(QUESTIONS, start=1):
        if len(question["choices"]) != 4 or question["answerIndex"] not in range(4):
            raise ValueError(f"Q{index}の4択または正答位置が不正です")
        if len(BLANK_RE.findall(question["stem"])) != 1:
            raise ValueError(f"Q{index}の空所が1か所ではありません")
        if any(re.search(rf"\b{re.escape(choice)}\b", question["stem"], flags=re.IGNORECASE) for choice in question["choices"]):
            raise ValueError(f"Q{index}の選択肢が設問文に含まれています")
        if re.search(r"\(\s*\)|（\s*）", question["translation"]):
            raise ValueError(f"Q{index}の和訳に空所記号があります")

    for phrase in choices:
        if " " in phrase and phrase not in CORE_IMAGES:
            raise ValueError(f"熟語の核心イメージがありません: {phrase}")

    meta = {
        "grade": "英検1級",
        "round": round_id,
        "section": "Reading 大問1（語句空所補充）",
        "source": SOURCE,
        "counts": {"words": 84, "idioms": 16, "total": 100},
    }
    question_data = {
        "meta": meta,
        "questions": [
            {"q": index, **question}
            for index, question in enumerate(QUESTIONS, start=1)
        ],
    }

    words = []
    idioms = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            meaning, pos, example, example_translation = DETAILS[choice]
            if len(WORD_RE.findall(example)) < 8:
                raise ValueError(f"{choice}の例文が8語未満です")
            if len(re.findall(re.escape(choice), example, flags=re.IGNORECASE)) != 1:
                raise ValueError(f"{choice}の例文に見出し語句が1回ありません")
            example_key = re.sub(re.escape(choice), "( )", example, count=1, flags=re.IGNORECASE)
            example_key = " ".join(example_key.lower().split())
            if example_key in seen_examples:
                raise ValueError(f"例文の骨格が重複しています: {choice} / {seen_examples[example_key]}")
            seen_examples[example_key] = choice
            for variant in surface_variants(choice):
                if variant in seen_surfaces:
                    raise ValueError(f"同一セット内で語形が重複しています: {choice} / {seen_surfaces[variant]}")
                seen_surfaces[variant] = choice

            item = {
                "q": q,
                "is_answer": index == question["answerIndex"],
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
                "pos": pos,
            }
            if " " in choice:
                item["phrase"] = choice
                item["coreImage"] = CORE_IMAGES[choice]
                idioms.append(item)
            else:
                item["word"] = choice
                words.append(item)

    if (len(words), len(idioms)) != (84, 16):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idioms)}")
    return {"meta": meta, "words": words, "idioms": idioms}, question_data


def run_q1_mock_8_9(
    round_id: str, QUESTIONS: list[dict], DETAILS: dict, CORE_IMAGES: dict, SOURCE: str
) -> None:
    """英検1級 模試第8・9回（ユーザー提供画像ベースの形式）の vocab/questions JSON を data/ に書き出す。"""
    vocab, questions = build_q1_mock_8_9(round_id, QUESTIONS, DETAILS, CORE_IMAGES, SOURCE)
    write_json(DATA_DIR / f"vocab_1_{round_id}.json", vocab)
    write_json(DATA_DIR / f"questions_1_{round_id}.json", questions)
    print(f"{round_id}: 25 questions / 100 items (84 words, 16 idioms)")

