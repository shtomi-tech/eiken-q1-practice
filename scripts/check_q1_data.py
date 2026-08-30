"""Q1用データセットの最低限の契約を検証する。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EXPECTED_IDS = {
    "eiken5-2026-1",
    *(f"eiken2-{round_id}" for round_id in ("2026-1", "2025-3", "2025-2")),
    *(f"eikenp2-{round_id}" for round_id in ("2026-1", "2025-3", "2025-2")),
    *(f"eikenp1-{round_id}" for round_id in ("2026-1", "2025-3", "2025-2")),
    *(f"eiken1-{round_id}" for round_id in ("2026-1", "2025-3", "2025-2")),
    "eiken1-mock-1",
    "eiken1-mock-2",
    "eiken1-mock-3",
    "eiken1-mock-4",
    "eiken1-mock-5",
    "eiken1-mock-6",
    "eiken1-mock-7",
    "eiken1-mock-8",
    "eiken1-mock-9",
    "eikenp2-mock-1",
    "eikenp2-mock-2",
    "eikenp2-mock-3",
    "eikenp2-mock-4",
    "iuhw-set-1",
}
TRANSLATION_BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def surface(item: dict) -> str:
    return str(item.get("phrase") if item.get("type") == "idiom" else item.get("word", ""))


def surface_variants(value: str) -> set[str]:
    base = " ".join(str(value or "").lower().split())
    base = re.sub(r"\b(one's|his|her|my|your|our|their|its)\b", "@poss", base)
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


def surfaces_match(left: str, right: str) -> bool:
    return bool(surface_variants(left) & surface_variants(right))


def text_skeleton(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def example_skeleton(value: str, needle: str) -> str:
    replaced = re.sub(re.escape(needle), "( )", str(value), count=1, flags=re.IGNORECASE)
    return text_skeleton(replaced)


def translation_skeleton(value: str, meaning: str) -> str:
    replaced = str(value).replace(meaning, "( )", 1)
    return text_skeleton(replaced)


def check_unique(values: list[tuple[str, str]], label: str) -> None:
    seen: dict[str, str] = {}
    for key, owner in values:
        if key in seen:
            raise ValueError(f"テーマ別: {label}が重複しています: {seen[key]} / {owner}")
        seen[key] = owner


def check_dataset(dataset_id: str, meta: dict) -> dict[str, object]:
    vocab_path = ROOT / meta["vocabUrl"]
    questions_path = ROOT / meta["questionsUrl"]
    if not vocab_path.is_file() or not questions_path.is_file():
        raise ValueError(f"{dataset_id}: データファイルがありません")

    vocab = load_json(vocab_path)
    questions = load_json(questions_path).get("questions", [])
    items = [
        {**item, "type": "word"}
        for item in vocab.get("words", [])
    ] + [
        {**item, "type": "idiom"}
        for item in vocab.get("idioms", [])
    ]
    if dataset_id.startswith("eikentopic-"):
        for item in items:
            if item.get("axis") not in {"problem", "cause", "solution", "concept"}:
                raise ValueError(f"{dataset_id}: axis が不正です")
            if not item.get("example") or not item.get("exampleTranslation"):
                raise ValueError(f"{dataset_id}: 例文または例文訳がありません")
    topic_rows: dict[str, list[dict]] = {
        "questions": [],
        "items": [],
        "translation_warnings": [],
        "mixed_questions": [],
    }
    topic_question_surfaces: Counter[str] = Counter()
    if not questions or not items:
        raise ValueError(f"{dataset_id}: 設問または語彙が空です")

    question_numbers = [question.get("q") for question in questions]
    if question_numbers != list(range(1, len(questions) + 1)):
        raise ValueError(f"{dataset_id}: 設問番号が不連続です")

    items_by_q: dict[int, list[dict]] = {}
    for item in items:
        if not item.get("q") or not surface(item) or not item.get("meaning"):
            raise ValueError(f"{dataset_id}: 語彙項目の必須値が不足しています")
        items_by_q.setdefault(int(item["q"]), []).append(item)

    if sorted(items_by_q) != question_numbers:
        raise ValueError(f"{dataset_id}: 語彙と設問の番号が一致しません")

    for question in questions:
        q = int(question["q"])
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        q_items = items_by_q[q]
        if len(choices) != 4 or answer_index not in range(4):
            raise ValueError(f"{dataset_id}: Q{q}の4択または正答位置が不正です")
        item_surfaces = [surface(item) for item in q_items]
        if len(item_surfaces) != 4 or len(item_surfaces) != len(set(item_surfaces)):
            raise ValueError(f"{dataset_id}: Q{q}の語彙と選択肢が一致しません")
        matches = [
            choice for choice in choices
            if sum(surfaces_match(choice, item_surface) for item_surface in item_surfaces) == 1
        ]
        if len(matches) != 4:
            raise ValueError(f"{dataset_id}: Q{q}の語彙と選択肢が一致しません")
        meanings = [item["meaning"] for item in q_items]
        if len(meanings) != len(set(meanings)):
            raise ValueError(f"{dataset_id}: Q{q}の意味が重複しています")
        if dataset_id.startswith("eikentopic-"):
            axes = [item["axis"] for item in q_items]
            if max(Counter(axes).values()) > 2:
                raise ValueError(f"{dataset_id}: Q{q}のaxisが3件以上重複しています")
            correct_items = [item for item in q_items if item.get("is_answer")]
            if len(correct_items) != 1:
                raise ValueError(f"{dataset_id}: Q{q}の正答語句が1件ではありません")
            correct_axis = correct_items[0]["axis"]
            if any(item["axis"] == correct_axis for item in q_items if not item.get("is_answer")):
                raise ValueError(f"{dataset_id}: Q{q}の正答と誤答のaxisが一致しています")
            stem = str(question.get("stem", ""))
            if (
                stem.count("( )") != 1
                or re.search(re.escape(surface(correct_items[0])), stem, flags=re.IGNORECASE)
            ):
                raise ValueError(f"{dataset_id}: Q{q}の設問文空所が不正です")
            if len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", stem)) < 15:
                raise ValueError(f"{dataset_id}: Q{q}の設問文が15語未満です")
            question_translation = str(question.get("translation", ""))
            if not question_translation:
                raise ValueError(f"{dataset_id}: Q{q}の設問文訳がありません")
            if TRANSLATION_BLANK_RE.search(question_translation):
                raise ValueError(f"{dataset_id}: Q{q}の設問文訳に空所記号があります")
            topic_question_surfaces.update(item_surfaces)
            topics = {str(item.get("topic", "")) for item in q_items}
            if len(topics) > 1:
                topic_rows["mixed_questions"].append({
                    "owner": f"{dataset_id}/Q{q}",
                    "topics": sorted(topics),
                })
            correct_meaning = str(correct_items[0]["meaning"])
            if correct_meaning not in question_translation:
                topic_rows["translation_warnings"].append({
                    "owner": f"{dataset_id}/Q{q}",
                    "meaning": correct_meaning,
                    "translation": question_translation,
                })
            topic_rows["questions"].append({
                "owner": f"{dataset_id}/Q{q}",
                "stem": text_skeleton(stem),
                "example_stems": [
                    example_skeleton(str(item.get("example", "")), surface(item))
                    for item in q_items
                ],
            })
            for item in q_items:
                item_surface = surface(item)
                example = str(item.get("example", ""))
                translation = str(item.get("exampleTranslation", ""))
                if len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", example)) < 8:
                    raise ValueError(f"{dataset_id}: Q{q}の例文が8語未満です")
                if len(re.findall(re.escape(item_surface), example, flags=re.IGNORECASE)) != 1:
                    raise ValueError(f"{dataset_id}: Q{q}の例文に見出し表現が1回ありません")
                topic_rows["items"].append({
                    "owner": f"{dataset_id}/Q{q}/{item_surface}",
                    "key": f"{item.get('topic', '')}::{item_surface}",
                    "example": example,
                    "translation": translation,
                    "meaning": str(item["meaning"]),
                    "surface": item_surface,
                })

    repeated_surfaces = {
        item_surface: count
        for item_surface, count in topic_question_surfaces.items()
        if count >= 3
    }
    if repeated_surfaces:
        repeated = ", ".join(
            f"{item_surface}×{count}"
            for item_surface, count in sorted(repeated_surfaces.items())
        )
        raise ValueError(f"{dataset_id}: 同じ語句が3問以上に登場します: {repeated}")

    print(f"{dataset_id}: {len(questions)} questions / {len(items)} words OK")
    topic_rows["counts"] = {
        "totalQuestions": len({int(item["q"]) for item in items}),
        "totalVocabulary": len(items),
    }
    return topic_rows


def check_topic_rows(topic_rows: dict[str, list[dict]]) -> None:
    for row in topic_rows["questions"]:
        if row["stem"] in row["example_stems"]:
            raise ValueError(f"テーマ別: 設問文が語句例文と同一です: {row['owner']}")
    check_unique(
        [(row["stem"], row["owner"]) for row in topic_rows["questions"]],
        "設問文の骨格",
    )
    unique_items = {row["key"]: row for row in topic_rows["items"]}
    check_unique(
        [
            (example_skeleton(row["example"], row["surface"]), row["owner"])
            for row in unique_items.values()
        ],
        "語句例文の骨格",
    )
    check_unique(
        [
            (translation_skeleton(row["translation"], row["meaning"]), row["owner"])
            for row in unique_items.values()
        ],
        "語句例文訳の骨格",
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="英検Q1データ契約を検証します")
    parser.add_argument(
        "--update-manifest",
        action="store_true",
        help="語彙データから算出した総数をdata/manifest.jsonへ書き戻します",
    )
    args = parser.parse_args()
    manifest = load_json(DATA_DIR / "manifest.json")
    if set(manifest) != {"defaultDatasetId", "q1"}:
        raise ValueError(f"manifest にQ1以外の領域があります: {sorted(manifest)}")
    q1 = manifest.get("q1", {})
    if set(q1) != EXPECTED_IDS:
        raise ValueError(f"manifest.q1 のセットが不一致です: {sorted(q1)}")
    topic_rows: dict[str, list[dict]] = {
        "questions": [],
        "items": [],
        "translation_warnings": [],
        "mixed_questions": [],
    }
    counts_by_dataset: dict[str, dict[str, int]] = {}
    for dataset_id, meta in q1.items():
        checked = check_dataset(dataset_id, meta)
        topic_rows["questions"].extend(checked["questions"])
        topic_rows["items"].extend(checked["items"])
        topic_rows["translation_warnings"].extend(checked["translation_warnings"])
        topic_rows["mixed_questions"].extend(checked["mixed_questions"])
        counts_by_dataset[dataset_id] = checked["counts"]
    if args.update_manifest:
        for dataset_id, counts in counts_by_dataset.items():
            q1[dataset_id]["totalQuestions"] = counts["totalQuestions"]
            q1[dataset_id]["totalVocabulary"] = counts["totalVocabulary"]
        (DATA_DIR / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("manifest: counts updated")
    else:
        for dataset_id, counts in counts_by_dataset.items():
            meta = q1[dataset_id]
            for key in ("totalQuestions", "totalVocabulary"):
                declared = meta.get(key)
                expected = counts[key]
                if isinstance(declared, bool) or not isinstance(declared, int) or declared != expected:
                    raise ValueError(
                        f"{dataset_id}: manifestの{key}={declared!r}は実データの{expected}と一致しません"
                    )
    check_topic_rows(topic_rows)
    if topic_rows["translation_warnings"]:
        print(f"WARN: 設問文訳に正答meaningを含まない設問 {len(topic_rows['translation_warnings'])}件")
        for warning in topic_rows["translation_warnings"]:
            print(f"  {warning['owner']}: {warning['meaning']}")
    if topic_rows["mixed_questions"]:
        print(f"WARN: 複数トピックの設問 {len(topic_rows['mixed_questions'])}件")
        for warning in topic_rows["mixed_questions"]:
            print(f"  {warning['owner']}: {' / '.join(warning['topics'])}")
    print("Q1 data: OK")


if __name__ == "__main__":
    main()
