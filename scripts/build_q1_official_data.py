"""2級・準2級・準1級の公式PDFからQ1の出題部分を検証・再適用する。

公式PDFはgitignore対象の ``data/eiken_<grade>/<round>`` に置く。語句カードの
教材情報は級別metadataスクリプトを正本とし、このスクリプトはPDF由来の設問文、
選択肢、正答位置が追跡中JSONと一致することを確認してから再適用する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

from build_pre1_data import (  # noqa: E402
    answer_key,
    clean_text,
    page_texts,
    parse_choices,
    parse_numbered_blocks,
)
from build_q1_1_data import clean_choice  # noqa: E402
from q1_eiken2_metadata import apply_round as apply_eiken2  # noqa: E402
from q1_eikenp2_metadata import apply_round as apply_eikenp2  # noqa: E402
from q1_pre1_metadata import apply_round as apply_eikenp1  # noqa: E402


CONFIG: dict[str, dict[str, object]] = {
    "2": {
        "source": "eiken_2",
        "questions": "questions_{round_id}.json",
        "count": 17,
        "apply": apply_eiken2,
    },
    "pre2": {
        "source": "eiken_p2",
        "questions": "questions_p2_{round_id}.json",
        "count": 15,
        "apply": apply_eikenp2,
    },
    "pre1": {
        "source": "eiken_p1",
        "questions": "questions_pre1_{round_id}.json",
        "count": 18,
        "apply": apply_eikenp1,
    },
}
ROUND_IDS = ("2025-2", "2025-3", "2026-1")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    newline = "\r\n" if b"\r\n" in path.read_bytes() else "\n"
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if newline == "\r\n":
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def display_stem(value: str) -> str:
    cleaned = clean_text(value)
    return re.sub(r"(?<![A-Za-z])([AB])\s+:\s*", r"\1: ", cleaned)


def comparable_stem(value: str) -> str:
    # PDFの禁則ハイフンは抽出時に消えるため、追跡中JSONとの照合時だけASCIIハイフンも無視する。
    return display_stem(value).replace("-", "").casefold()


def extract_questions(source_dir: Path, count: int) -> list[dict]:
    problem_path = source_dir / "problem.pdf"
    answer_path = source_dir / "answer.pdf"
    if not problem_path.is_file() or not answer_path.is_file():
        raise FileNotFoundError(f"公式PDFがありません: {source_dir}")

    blocks: dict[int, str] = {}
    for number, block in parse_numbered_blocks("\n".join(page_texts(problem_path))):
        if 1 <= number <= count and number not in blocks:
            blocks[number] = block
    answers = answer_key(answer_path)
    if sorted(blocks) != list(range(1, count + 1)):
        raise ValueError(f"{source_dir}: Q1の設問番号を1〜{count}で抽出できません")

    questions = []
    for number in range(1, count + 1):
        stem, raw_choices = parse_choices(blocks[number])
        choices = [clean_choice(choice) for choice in raw_choices]
        if len(choices) != 4 or any(not choice for choice in choices):
            raise ValueError(f"{source_dir}: Q{number}の4択を抽出できません")
        if number not in answers:
            raise ValueError(f"{source_dir}: Q{number}の正答を抽出できません")
        questions.append(
            {
                "q": number,
                "stem": display_stem(stem),
                "choices": choices,
                "answerIndex": answers[number],
            }
        )
    return questions


def verify_and_apply(grade: str, round_id: str, write: bool) -> None:
    config = CONFIG[grade]
    questions_path = DATA_DIR / str(config["questions"]).format(round_id=round_id)
    questions_data = load_json(questions_path)
    tracked = questions_data.get("questions", [])
    extracted = extract_questions(
        DATA_DIR / str(config["source"]) / round_id,
        int(config["count"]),
    )
    if len(tracked) != len(extracted):
        raise ValueError(f"{grade}/{round_id}: 追跡中JSONの設問数が一致しません")

    for current, source in zip(tracked, extracted, strict=True):
        q = source["q"]
        if int(current.get("q", -1)) != q:
            raise ValueError(f"{grade}/{round_id}: Q{q}の設問番号が一致しません")
        if comparable_stem(str(current.get("stem", ""))) != comparable_stem(source["stem"]):
            raise ValueError(f"{grade}/{round_id}: Q{q}の設問文が公式PDFと一致しません")
        if current.get("choices") != source["choices"]:
            raise ValueError(f"{grade}/{round_id}: Q{q}の選択肢が公式PDFと一致しません")
        if current.get("answerIndex") != source["answerIndex"]:
            raise ValueError(f"{grade}/{round_id}: Q{q}の正答位置が公式解答と一致しません")
        if write:
            current["stem"] = source["stem"]
            current["choices"] = source["choices"]
            current["answerIndex"] = source["answerIndex"]

    if write:
        write_json(questions_path, questions_data)
        apply = config["apply"]
        assert callable(apply)
        apply(round_id)
    mode = "再適用" if write else "照合"
    print(f"{grade}/{round_id}: 公式PDFと{len(extracted)}問を{mode} OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grade", choices=["all", *CONFIG], default="all")
    parser.add_argument("--round", dest="round_id", choices=["all", *ROUND_IDS], default="all")
    parser.add_argument("--write", action="store_true", help="照合後にPDF由来フィールドを再適用する")
    args = parser.parse_args()

    grades = list(CONFIG) if args.grade == "all" else [args.grade]
    rounds = list(ROUND_IDS) if args.round_id == "all" else [args.round_id]
    for grade in grades:
        for round_id in rounds:
            verify_and_apply(grade, round_id, args.write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
