#!/usr/bin/env python3
"""Use Jev to compare mock Eiken 1 Q1 stem style with official past questions.

This is a heuristic reference review, not a calibrated scoring instrument.
Only question numbers and stems are sent; answer keys, choices, and translations
are deliberately excluded from the state.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from typesafe_sdk import AsyncTypeSafeClient, Noul, Score

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OFFICIAL_DATASETS = ("eiken1-2025-2", "eiken1-2025-3", "eiken1-2026-1")
PROMPT_VERSION = "eiken1-q1-style-v1"
ROUND_RE = re.compile(r"^mock-[0-9]+$")

STYLE_LEVELS = [
    {
        "label": "far_from_reference",
        "description": (
            "The set is clearly unlike the official reference questions in several "
            "major style traits, such as stem length, contextual detail, dialogue use, "
            "or the way information is developed."
        ),
    },
    {
        "label": "weak_alignment",
        "description": (
            "The set shares some surface traits but differs substantially from the "
            "official reference in typical stem length, context, or presentation."
        ),
    },
    {
        "label": "partial_alignment",
        "description": (
            "The set resembles the official reference in some recurring traits, while "
            "noticeable differences remain in the overall question-stem style."
        ),
    },
    {
        "label": "strong_alignment",
        "description": (
            "The set generally follows the official reference's stem length, amount of "
            "context, dialogue balance, and information flow, with only modest variation."
        ),
    },
    {
        "label": "close_alignment",
        "description": (
            "Across the set, the question stems closely resemble the official reference "
            "in length, contextual detail, dialogue balance, and information flow."
        ),
    },
]

DIAGNOSTICS = {
    "too_brief": (
        "The candidate set is dominated by stems that are noticeably shorter or less "
        "contextualized than the official reference questions."
    ),
    "dialogue_mismatch": (
        "The candidate set's use and form of short A/B dialogues noticeably differs "
        "from the official reference questions."
    ),
    "context_mismatch": (
        "The candidate stems often provide too little situational information for the "
        "blank to be resolved in the style of the official reference."
    ),
}

DIAGNOSTIC_LABELS = {
    "too_brief": "短く文脈が少ない設問が目立つ",
    "dialogue_mismatch": "会話形式の使い方が参照群と異なる",
    "context_mismatch": "空所を解く状況情報の置き方が参照群と異なる",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_dataset(dataset_id: str, metadata: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / metadata["questionsUrl"]
    data = read_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError(f"{dataset_id}: questions配列がありません ({path})")
    return {"id": dataset_id, "path": path, "data": data}


def question_stems(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"q": question.get("q", index), "stem": str(question.get("stem", ""))}
        for index, question in enumerate(dataset["data"]["questions"], start=1)
    ]


def make_questions() -> dict[str, Any]:
    questions: dict[str, Any] = {
        "style_alignment": Score(
            instructions=(
                "Compare the candidate question set with the official reference questions "
                "for Eiken Grade 1 Reading Part 1. Judge overall set-level style: typical "
                "stem length, contextual detail, dialogue use, and how each stem develops "
                "information toward its blank. Topics may differ. Do not judge answer "
                "correctness, vocabulary difficulty, or translation. Use the ordered rubric."
            ),
            criteria=STYLE_LEVELS,
        )
    }
    for name, description in DIAGNOSTICS.items():
        questions[name] = Noul(
            instructions=(
                "Evaluate this specific possible style mismatch against the official "
                "reference questions. Answer yes only when the difference is noticeable "
                "across the candidate set, not because of one unusual item.\n\n"
                + description
            ),
            criteria={
                "true": description,
                "false": "The described style mismatch is not noticeable across the candidate set.",
            },
        )
    return questions


async def evaluate(
    client: AsyncTypeSafeClient,
    target: dict[str, Any],
    references: list[dict[str, Any]],
) -> dict[str, Any]:
    state = {
        "task": "Compare question-writing style with the provided official reference stems.",
        "reference_questions": [
            {"dataset": ds["id"], **item}
            for ds in references
            for item in question_stems(ds)
        ],
        "candidate_questions": question_stems(target),
    }
    response = await client.system_one(state=state, questions=make_questions())
    score = response.scores["style_alignment"]
    signals = {
        name: round(response.nouls[name].noul, 3)
        for name in DIAGNOSTICS
    }
    reasons = [
        {
            "signal": name,
            "observation": DIAGNOSTIC_LABELS[name],
            "probability": probability,
        }
        for name, probability in signals.items()
        if probability >= 0.5
    ]
    if not reasons:
        reasons = [{
            "signal": "no_diagnostic_above_threshold",
            "observation": "個別の不一致シグナルはいずれも0.5未満",
            "probability": max(signals.values(), default=0.0),
        }]
    return {
        "datasetId": target["id"],
        "promptVersion": PROMPT_VERSION,
        "model": response.model,
        "score": round(score.score, 3),
        "confidence": round(score.confidence, 3),
        "levelProbabilities": {
            str(level): round(probability, 3)
            for level, probability in sorted(score.probabilities.items())
        },
        "diagnosticProbabilities": signals,
        "reasons": reasons,
    }


async def main_async(args: argparse.Namespace) -> int:
    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY が設定されていません。")

    manifest = read_json(DATA_DIR / "manifest.json")["q1"]
    references = []
    for dataset_id in OFFICIAL_DATASETS:
        if dataset_id not in manifest:
            raise SystemExit(f"公式参照セットがmanifestにありません: {dataset_id}")
        references.append(load_dataset(dataset_id, manifest[dataset_id]))

    targets: list[dict[str, Any]] = []
    seen_rounds: set[str] = set()
    for path in args.paths:
        if not path.is_file():
            raise SystemExit(f"入力ファイルがありません: {path}")
        data = read_json(path)
        meta = data.get("meta", {})
        round_id = str(meta.get("round", ""))
        if meta.get("grade") != "英検1級" or not ROUND_RE.fullmatch(round_id):
            raise SystemExit(f"英検1級のmock JSONではありません: {path}")
        if round_id in seen_rounds:
            raise SystemExit(f"入力に重複した回があります: {round_id}")
        if not isinstance(data.get("questions"), list) or not data["questions"]:
            raise SystemExit(f"設問がありません: {path}")
        seen_rounds.add(round_id)
        targets.append({"id": f"eiken1-{round_id}", "path": path.resolve(), "data": data})

    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise SystemExit(f"出力先がすでに存在します（上書きしません）: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(exist_ok=False)

    reference_hashes = {ds["id"]: sha256(ds["path"]) for ds in references}
    async with AsyncTypeSafeClient() as client:
        for target in targets:
            result = await evaluate(client, target, references)
            round_id = target["data"]["meta"]["round"]
            output = {
                "source": str(target["path"]),
                "sourceSha256": sha256(target["path"]),
                "referenceSources": [str(ds["path"]) for ds in references],
                "referenceSha256": reference_hashes,
                "promptVersion": PROMPT_VERSION,
                "evaluationType": "heuristic_reference_review",
                "warning": "Jevの参考評価。公式形式への適合を保証する校正済み尺度ではありません。",
                "result": result,
            }
            out_path = output_dir / f"jev-style-{round_id}.json"
            out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
            print(
                f"{target['id']}: score={result['score']} "
                f"confidence={result['confidence']} -> {out_path}"
            )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Jevで1級模試と公式過去問の設問スタイルを比較します")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--fail-if-exists",
        action="store_true",
        required=True,
        help="出力先が既存なら上書きせず終了する（安全確認のため必須）",
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
