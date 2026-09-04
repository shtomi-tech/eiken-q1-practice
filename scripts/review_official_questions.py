"""正答を伏せた公式Q1をローカル別モデルで独立レビューする。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "manifest.json"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OFFICIAL_PREFIXES = ("eiken2-", "eikenp2-", "eikenp1-")
RESULT_RE = re.compile(r"^Q(\d+)\s+(UNIQUE|AMBIGUOUS|NONE)(?:\s+([0-9,]+))?\s*$", re.IGNORECASE)
CHOICE_LABEL_RE = re.compile(r"^Q(\d+)\s+.+\s+([1-4])\s*$", re.IGNORECASE)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def target_ids(dataset_id: str | None) -> list[str]:
    manifest = load(MANIFEST_PATH).get("q1", {})
    if dataset_id:
        if dataset_id not in manifest:
            raise ValueError(f"manifestにdatasetIdがありません: {dataset_id}")
        return [dataset_id]
    return [
        current
        for current in manifest
        if current.startswith(OFFICIAL_PREFIXES) and "-mock-" not in current
    ]


def prompt_for(questions: list[dict]) -> str:
    lines = [
        "You are independently reviewing Eiken multiple-choice questions.",
        "The answer key is intentionally hidden. For each question, choose every option that is grammatically and contextually valid.",
        "Reply with exactly one plain-text line per question: Q1 UNIQUE 3, Q1 AMBIGUOUS 2,3, or Q1 NONE.",
        "Do not add explanations, headings, markdown, or an answer summary.",
    ]
    for question in questions:
        options = " | ".join(
            f"{index}:{choice}" for index, choice in enumerate(question.get("choices", []), start=1)
        )
        lines.append(f"Q{question['q']} {question['stem']} OPTIONS: {options}")
    return "\n".join(lines)


def review(model: str, prompt: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": 0},
        }
    ).encode("utf-8")
    request = Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except URLError as error:
        raise RuntimeError(f"Ollamaへ接続できません: {error.reason}") from error
    return str(result.get("response", "")).strip()


def parse_results(text: str, count: int) -> dict[int, tuple[str, list[int]]]:
    results: dict[int, tuple[str, list[int]]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip().strip("* ")
        match = RESULT_RE.fullmatch(line)
        if match:
            q = int(match.group(1))
            choices = [int(value) for value in (match.group(3) or "").split(",") if value]
            results[q] = (match.group(2).upper(), choices)
            continue
        choice_match = CHOICE_LABEL_RE.fullmatch(line)
        if choice_match:
            results[int(choice_match.group(1))] = ("UNIQUE", [int(choice_match.group(2))])
    if sorted(results) != list(range(1, count + 1)):
        missing = sorted(set(range(1, count + 1)) - set(results))
        raise ValueError(f"レビュー出力を全問解析できません。欠番: {missing}; raw={text[:500]!r}")
    return results


def review_dataset(dataset_id: str, model: str) -> tuple[int, list[str]]:
    manifest = load(MANIFEST_PATH)["q1"][dataset_id]
    questions = load(ROOT / manifest["questionsUrl"])["questions"]
    raw = review(model, prompt_for(questions))
    results = parse_results(raw, len(questions))
    issues = []
    for question in questions:
        q = int(question["q"])
        status, choices = results[q]
        expected = int(question["answerIndex"]) + 1
        if status != "UNIQUE" or choices != [expected]:
            issues.append(f"Q{q}: model={status} {choices}, official={expected}")
    return len(questions), issues


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id")
    parser.add_argument("--model", default="qwen3:8b")
    args = parser.parse_args()

    failed = False
    for dataset_id in target_ids(args.dataset_id):
        count, issues = review_dataset(dataset_id, args.model)
        if issues:
            failed = True
            print(f"{dataset_id}: REVIEW ({len(issues)}/{count})")
            for issue in issues:
                print(f"- {issue}")
        else:
            print(f"{dataset_id}: UNIQUE {count}/{count} ({args.model}, answer hidden)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
