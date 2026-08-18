"""テーマ別4択の全選択肢を空所へ入れたレビュー用出力を作る。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def review_set(set_no: int) -> str:
    path = DATA_DIR / f"questions_topic_set-{set_no}.json"
    questions = load_json(path).get("questions", [])
    lines = [f"# set-{set_no}"]
    for question in questions:
        stem = str(question["stem"])
        if stem.count("( )") != 1:
            raise ValueError(f"set-{set_no} Q{question.get('q')}: 空所が1つではありません")
        lines.append(
            f"\n## Q{question['q']} / {question.get('topic', '')} / 正答 {question['answerIndex'] + 1}"
        )
        for index, choice in enumerate(question["choices"]):
            filled = stem.replace("( )", choice, 1)
            marker = " *" if index == question["answerIndex"] else ""
            lines.append(f"{index + 1}{marker}. {filled}")
        lines.append(f"訳: {question.get('translation', '')}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", dest="set_no", type=int, choices=range(1, 6))
    args = parser.parse_args()
    set_numbers = [args.set_no] if args.set_no else range(1, 6)
    print("\n\n".join(review_set(set_no) for set_no in set_numbers))


if __name__ == "__main__":
    main()
