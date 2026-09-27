#!/usr/bin/env python3
"""Compare mock Q1 sets with the official past-paper style profile.

Word counts intentionally use whitespace-separated tokens, matching the audit
that established the project targets. Similarity is only a surface screen; it
does not establish whether a question was paraphrased from a source.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OFFICIAL_BY_GRADE = {
    "eiken1": ("eiken1-2025-2", "eiken1-2025-3", "eiken1-2026-1"),
    "eiken2": ("eiken2-2025-2", "eiken2-2025-3", "eiken2-2026-1"),
    "eikenp2": ("eikenp2-2025-2", "eikenp2-2025-3", "eikenp2-2026-1"),
}
BLANK_RE = re.compile(r"\(\s*\)")
DIALOGUE_A_RE = re.compile(r"(?m)^\s*A\s*:")
DIALOGUE_B_RE = re.compile(r"\bB\s*:")
MOCK10_21 = tuple(f"eiken1-mock-{n}" for n in range(10, 22))
MOCK1_9 = tuple(f"eiken1-mock-{n}" for n in range(1, 10))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def grade_of(dataset_id: str) -> str:
    for prefix in ("eikenp2-", "eiken1-", "eiken2-"):
        if dataset_id.startswith(prefix):
            return prefix[:-1]
    return dataset_id.split("-", 1)[0]


def load_questions(dataset_id: str, metadata: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / metadata["questionsUrl"]
    data = read_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError(f"{dataset_id}: questions配列がありません ({path})")
    return {"id": dataset_id, "path": path, "data": data}


def stem_words(stem: str) -> int:
    # The audit baseline used whitespace tokens; punctuation remains attached.
    return len(stem.split())


def is_dialogue(stem: str) -> bool:
    return bool(DIALOGUE_A_RE.search(stem) and DIALOGUE_B_RE.search(stem))


def normalized_stem(stem: str) -> str:
    value = BLANK_RE.sub("( )", stem)
    return " ".join(value.casefold().split())


def question_metrics(dataset: dict[str, Any]) -> dict[str, Any]:
    questions = dataset["data"]["questions"]
    lengths = [stem_words(str(q.get("stem", ""))) for q in questions]
    dialogue_count = sum(is_dialogue(str(q.get("stem", ""))) for q in questions)
    total = len(questions)
    return {
        "questions": total,
        "stemWords": {
            "mean": round(statistics.mean(lengths), 2) if lengths else None,
            "median": statistics.median(lengths) if lengths else None,
            "min": min(lengths) if lengths else None,
            "max": max(lengths) if lengths else None,
        },
        "dialogueQuestions": dialogue_count,
        "dialogueRatePct": round(dialogue_count * 100 / total, 2) if total else None,
    }


def combined_metrics(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    questions = [q for ds in datasets for q in ds["data"]["questions"]]
    lengths = [stem_words(str(q.get("stem", ""))) for q in questions]
    dialogue_count = sum(is_dialogue(str(q.get("stem", ""))) for q in questions)
    total = len(questions)
    return {
        "sets": len(datasets),
        "questions": total,
        "stemWords": {
            "mean": round(statistics.mean(lengths), 2) if lengths else None,
            "median": statistics.median(lengths) if lengths else None,
            "min": min(lengths) if lengths else None,
            "max": max(lengths) if lengths else None,
        },
        "dialogueQuestions": dialogue_count,
        "dialogueRatePct": round(dialogue_count * 100 / total, 2) if total else None,
    }


def cohort_result(
    label: str, required_ids: tuple[str, ...], datasets: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    missing = [dataset_id for dataset_id in required_ids if dataset_id not in datasets]
    if missing:
        return {"status": "NOT_CHECKED", "missingDatasetIds": missing}
    return {
        "status": "AVAILABLE",
        "metrics": combined_metrics([datasets[dataset_id] for dataset_id in required_ids]),
    }


def structural_findings(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    dataset_id = dataset["id"]
    questions = dataset["data"]["questions"]
    findings: list[dict[str, Any]] = []
    seen_q: list[Any] = []
    for fallback, question in enumerate(questions, start=1):
        q = question.get("q", fallback)
        where = f"{dataset_id}/Q{q}"
        seen_q.append(q)
        stem = str(question.get("stem", ""))
        choices = question.get("choices")
        answer_index = question.get("answerIndex")
        if len(BLANK_RE.findall(stem)) != 1:
            findings.append({"where": where, "check": "blank", "detail": "空所が1か所ではありません"})
        if not isinstance(choices, list) or len(choices) != 4:
            findings.append({"where": where, "check": "choices", "detail": "選択肢が4件ではありません"})
        if not isinstance(answer_index, int) or isinstance(answer_index, bool) or not 0 <= answer_index < 4:
            findings.append({"where": where, "check": "answerIndex", "detail": "answerIndexが範囲外です"})
        if not stem.strip():
            findings.append({"where": where, "check": "stem", "detail": "設問文が空です"})
        if not str(question.get("translation", "")).strip():
            findings.append({"where": where, "check": "translation", "detail": "和訳が空です"})
    expected = list(range(1, len(questions) + 1))
    if seen_q != expected:
        findings.append({
            "where": dataset_id,
            "check": "questionNumbers",
            "detail": "設問番号が1からの連番ではありません",
        })
    return findings


def compare_surfaces(
    mock_datasets: list[dict[str, Any]], official_by_grade: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    exact_pairs: list[dict[str, Any]] = []
    near_pairs: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    comparisons = 0
    for mock in mock_datasets:
        reference_sets = official_by_grade.get(grade_of(mock["id"]), [])
        official = [
            (ds["id"], q.get("q"), normalized_stem(str(q.get("stem", ""))))
            for ds in reference_sets
            for q in ds["data"]["questions"]
        ]
        for question in mock["data"]["questions"]:
            left = normalized_stem(str(question.get("stem", "")))
            for official_id, official_q, right in official:
                ratio = SequenceMatcher(None, left, right, autojunk=False).ratio()
                comparisons += 1
                pair = {
                    "mockDataset": mock["id"],
                    "mockQ": question.get("q"),
                    "officialDataset": official_id,
                    "officialQ": official_q,
                    "ratio": round(ratio, 4),
                }
                if left == right:
                    exact_pairs.append(pair)
                elif ratio >= 0.8:
                    near_pairs.append(pair)
                if best is None or ratio > best["ratio"]:
                    best = pair
    near_pairs.sort(key=lambda row: (-row["ratio"], row["mockDataset"], row["mockQ"]))
    return {
        "comparisonCount": comparisons,
        "exactPairCount": len(exact_pairs),
        "exactPairs": exact_pairs,
        "nearPairThreshold": 0.8,
        "nearPairCount": len(near_pairs),
        "nearPairs": near_pairs,
        "closestPair": best,
        "interpretation": "表層スクリーニング。言い換え転載の不存在を証明しない。",
    }


def check_targets(
    requested_ids: set[str],
    datasets: dict[str, dict[str, Any]],
    per_set: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    status: dict[str, Any] = {}
    for dataset_id in sorted(requested_ids):
        if dataset_id not in datasets:
            continue
        metrics = per_set[dataset_id]
        words = metrics["stemWords"]
        targets: dict[str, Any] = {}
        if dataset_id in MOCK10_21:
            targets["meanWords"] = 22 <= words["mean"] <= 29
            targets["medianWords"] = 22 <= words["median"] <= 29
            targets["dialogueQuestions"] = 1 <= metrics["dialogueQuestions"] <= 4
        elif dataset_id in {"eiken1-mock-1", "eiken1-mock-5"}:
            targets["dialogueQuestions"] = 1 <= metrics["dialogueQuestions"] <= 4
        else:
            continue
        target_findings = structural_findings(datasets[dataset_id])
        targets["structure"] = not target_findings
        if target_findings:
            findings.extend(target_findings)
        for key, passed in targets.items():
            if passed is False:
                findings.append({
                    "where": dataset_id,
                    "check": key,
                    "detail": f"閾値未達: {metrics}",
                })
        status[dataset_id] = {"checks": targets, "structuralFindings": target_findings}

    cohorts: list[tuple[str, tuple[str, ...], float, float]] = [
        ("eiken1-mock-10..21", MOCK10_21, 6.0, 12.0),
        ("eiken1-mock-1..9", MOCK1_9, 8.0, 13.0),
    ]
    cohort_results: dict[str, Any] = {}
    for label, required_ids, low, high in cohorts:
        missing = [dataset_id for dataset_id in required_ids if dataset_id not in requested_ids]
        if missing:
            cohort_results[label] = {"status": "NOT_CHECKED", "missingDatasetIds": missing}
            continue
        cohort_data = [datasets[dataset_id] for dataset_id in required_ids]
        metrics = combined_metrics(cohort_data)
        passed = low <= metrics["dialogueRatePct"] <= high
        cohort_results[label] = {
            "status": "PASS" if passed else "FAIL",
            "targetRatePct": [low, high],
            "metrics": metrics,
        }
        if not passed:
            findings.append({
                "where": label,
                "check": "aggregateDialogueRate",
                "detail": f"会話率{metrics['dialogueRatePct']}%が{low}〜{high}%の範囲外です",
            })
    status["cohorts"] = cohort_results
    return findings, status


def main() -> int:
    parser = argparse.ArgumentParser(description="公式過去問と模試のQ1スタイルを比較します")
    parser.add_argument("--grade", choices=("eiken1", "eiken2", "eikenp2"))
    parser.add_argument("--datasets", nargs="+")
    parser.add_argument("--check-targets", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.grade and not args.datasets:
        parser.error("--grade または --datasets を指定してください")

    manifest = read_json(DATA_DIR / "manifest.json")["q1"]
    unknown = sorted(set(args.datasets or []) - set(manifest))
    if unknown:
        parser.error(f"未知のdatasetId: {', '.join(unknown)}")
    targets = set(args.datasets or manifest)
    if args.grade:
        targets = {dataset_id for dataset_id in targets if grade_of(dataset_id) == args.grade}
    if not targets:
        parser.error("対象セットがありません")
    target_grades = sorted({grade_of(dataset_id) for dataset_id in targets})
    unsupported_grades = sorted(set(target_grades) - set(OFFICIAL_BY_GRADE))
    if unsupported_grades:
        parser.error(f"公式参照セットの定義がない級です: {unsupported_grades}")
    if args.check_targets and any(grade != "eiken1" for grade in target_grades):
        parser.error("--check-targets はeiken1のデータセットだけを対象にします")

    loaded = {dataset_id: load_questions(dataset_id, manifest[dataset_id]) for dataset_id in sorted(targets)}
    reference_ids: list[str] = []
    for grade in target_grades:
        if grade not in OFFICIAL_BY_GRADE:
            continue
        required = OFFICIAL_BY_GRADE[grade]
        missing_official = [dataset_id for dataset_id in required if dataset_id not in manifest]
        if missing_official:
            parser.error(f"{grade}の公式参照セットがmanifestにありません: {missing_official}")
        reference_ids.extend(required)
    official = [load_questions(ds_id, manifest[ds_id]) for ds_id in reference_ids]
    official_by_grade = {
        grade: [ds for ds in official if grade_of(ds["id"]) == grade]
        for grade in target_grades
    }

    metrics = {dataset_id: question_metrics(ds) for dataset_id, ds in loaded.items()}
    style_mocks = [ds for ds in loaded.values() if "mock-" in ds["id"]]
    similarity = compare_surfaces(style_mocks, official_by_grade) if style_mocks and official else None
    aggregate_metrics: dict[str, Any] = {}
    official_aggregates = {
        grade: combined_metrics(datasets)
        for grade, datasets in official_by_grade.items()
        if datasets
    }
    aggregate_metrics["officialReferenceByGrade"] = official_aggregates
    if "eiken1" in official_aggregates:
        aggregate_metrics["eiken1OfficialReference"] = official_aggregates["eiken1"]
    aggregate_metrics["eiken1Mock10To21"] = cohort_result("eiken1-mock-10..21", MOCK10_21, loaded)
    aggregate_metrics["eiken1Mock1To9"] = cohort_result("eiken1-mock-1..9", MOCK1_9, loaded)
    if args.grade in {"eiken2", "eikenp2"}:
        grade_sets = list(loaded.values())
        aggregate_metrics["official"] = combined_metrics(
            [ds for ds in grade_sets if "mock-" not in ds["id"]]
        )
        aggregate_metrics["mocks"] = combined_metrics(
            [ds for ds in grade_sets if "mock-" in ds["id"]]
        )
    target_findings: list[dict[str, Any]] = []
    target_status = None
    if args.check_targets:
        target_findings, target_status = check_targets(targets, loaded, metrics)
        # Only explicitly requested and loaded per-set checks participate here.
        # Missing sets make cohort aggregates NOT_CHECKED, never an implicit pass.

    output: dict[str, Any] = {
        "grade": args.grade,
        "targets": sorted(targets),
        "metrics": metrics,
        "aggregateMetrics": aggregate_metrics,
        "officialReferenceDatasets": [ds["id"] for ds in official],
        "officialReferenceMetrics": {
            ds["id"]: question_metrics(ds) for ds in official
        },
        "surfaceSimilarity": similarity,
        "targetChecks": target_status,
        "findings": target_findings,
        "summary": {"errors": len(target_findings)},
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for dataset_id, value in metrics.items():
            print(f"{dataset_id}: {json.dumps(value, ensure_ascii=False)}")
        if official:
            all_official = combined_metrics(official)
            print(f"official reference: {json.dumps(all_official, ensure_ascii=False)}")
        if similarity:
            print(
                "surface similarity: "
                f"exact={similarity['exactPairCount']} near(>=0.80)={similarity['nearPairCount']}"
            )
        if target_status is not None:
            print(f"target checks: {json.dumps(target_status, ensure_ascii=False)}")
            for finding in target_findings:
                print(f"FAIL {finding['where']} {finding['check']}: {finding['detail']}")
    return 1 if target_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
