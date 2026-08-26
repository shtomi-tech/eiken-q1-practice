"""準2級の自作模試（全回）の内容を検証する。"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from check_q1_data import check_dataset, example_skeleton, surface_variants, text_skeleton


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"ファイルがありません: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def item_surface(item: dict, bucket: str) -> str:
    return str(item.get("phrase") if bucket == "idioms" else item.get("word", "")).strip()


def fail(dataset_id: str, message: str) -> None:
    raise ValueError(f"{dataset_id}: {message}")


def dataset_id_for(round_id: str) -> str:
    return f"eikenp2-{round_id}"


def mock_rounds() -> tuple[str, ...]:
    rounds = []
    for path in DATA_DIR.glob("vocab_p2_mock-*.json"):
        round_id = path.stem.removeprefix("vocab_p2_")
        if re.fullmatch(r"mock-\d+", round_id):
            rounds.append(round_id)
    return tuple(sorted(set(rounds), key=lambda value: int(value.split("-")[1])))


def target_paths(dataset_id: str) -> tuple[Path, Path]:
    round_id = dataset_id.removeprefix("eikenp2-")
    return (
        DATA_DIR / f"vocab_p2_{round_id}.json",
        DATA_DIR / f"questions_p2_{round_id}.json",
    )


def resolve_dataset_id(value: str) -> str:
    round_id = value.removeprefix("eikenp2-")
    if round_id not in mock_rounds():
        available = "、".join(mock_rounds()) or "なし"
        raise ValueError(f"対象の準2級模試がありません: {value}（利用可能: {available}）")
    return dataset_id_for(round_id)


def word_surface_forms(surface: str) -> set[str]:
    base = text_skeleton(surface)
    if not base or " " in base:
        return {base}
    forms = {base}
    if base.endswith("y") and len(base) > 1 and base[-2] not in "aeiou":
        forms.add(base[:-1] + "ies")
    else:
        forms.add(base + "s")
    if base.endswith(("s", "x", "z", "ch", "sh")):
        forms.add(base + "es")
    forms.add(base[:-1] + "d" if base.endswith("e") else base + "ed")
    if base.endswith("e") and not base.endswith("ee"):
        forms.add(base[:-1] + "ing")
    else:
        forms.add(base + "ing")
    if (
        len(base) >= 3
        and base[-1] not in "aeiouwxy"
        and base[-2] in "aeiou"
        and base[-3] not in "aeiou"
    ):
        forms.update({base + base[-1] + "ed", base + base[-1] + "ing"})
    return forms


def choice_in_stem(choice: str, stem: str) -> bool:
    forms = {text_skeleton(choice)} if " " in choice else word_surface_forms(choice)
    return any(
        re.search(rf"(?<![A-Za-z]){re.escape(form)}(?![A-Za-z])", stem, flags=re.IGNORECASE)
        for form in forms
    )


def existing_idiom_pos_labels() -> set[str]:
    labels: set[str] = set()
    for path in DATA_DIR.glob("vocab_*.json"):
        if re.fullmatch(r"vocab_p2_mock-\d+\.json", path.name):
            continue
        data = load_json(path)
        labels.update(
            str(item.get("pos", "")).strip()
            for item in data.get("idioms", [])
            if str(item.get("pos", "")).strip()
        )
    return labels


def lemma_forms() -> set[str]:
    data = load_json(DATA_DIR / "lemmas.json")
    mapping = data.get("lemmas", {})
    if not isinstance(mapping, dict):
        raise ValueError("lemmas.json の lemmas が辞書ではありません")
    return {
        str(value).strip().lower()
        for value in [*mapping.keys(), *mapping.values()]
        if str(value).strip()
    }


def all_p2_surfaces(exclude_file: str = "") -> dict[str, str]:
    existing: dict[str, str] = {}
    for path in sorted(DATA_DIR.glob("vocab_p2_*.json")):
        if path.name == exclude_file:
            continue
        data = load_json(path)
        for bucket in ("words", "idioms"):
            for item in data.get(bucket, []):
                surface = item_surface(item, bucket)
                for variant in surface_variants(surface):
                    existing[variant] = f"{path.name}:{surface}"
    return existing


def phrase_owners() -> dict[str, list[str]]:
    owners: dict[str, list[str]] = {}
    for path in sorted(DATA_DIR.glob("vocab_*.json")):
        data = load_json(path)
        for item in data.get("idioms", []):
            phrase = text_skeleton(item.get("phrase", ""))
            owners.setdefault(phrase, []).append(f"{path.name}:{item.get('phrase', '')}")
    return owners


def check(dataset_id: str) -> None:
    vocab_path, questions_path = target_paths(dataset_id)
    vocab = load_json(vocab_path)
    questions_data = load_json(questions_path)
    questions = questions_data.get("questions", [])
    words = vocab.get("words", [])
    idioms = vocab.get("idioms", [])
    all_items = [(item, "words") for item in words] + [(item, "idioms") for item in idioms]

    check_dataset(
        dataset_id,
        {
            "vocabUrl": f"data/{vocab_path.name}",
            "questionsUrl": f"data/{questions_path.name}",
        },
    )

    if (len(questions), len(words), len(idioms)) != (15, 40, 20):
        fail(dataset_id, f"件数が不正です: questions={len(questions)}, words={len(words)}, idioms={len(idioms)}")
    if sum(item.get("is_answer") is True for item, _ in all_items) != 15:
        fail(dataset_id, "正答項目の件数が15ではありません")
    conversation = sum(str(question.get("stem", "")).count("A:") for question in questions)
    if not 6 <= conversation <= 8:
        fail(dataset_id, f"会話文が6〜8問ではありません: {conversation}問")

    item_by_q: dict[int, list[tuple[dict, str]]] = {}
    for item, bucket in all_items:
        item_by_q.setdefault(int(item["q"]), []).append((item, bucket))

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    for item, bucket in all_items:
        surface = item_surface(item, bucket)
        if not surface:
            fail(dataset_id, "見出し語句が空です")
        variants = surface_variants(surface)
        overlap = variants & seen_surfaces.keys()
        if overlap:
            fail(dataset_id, f"同一セット内の語句が重複しています: {surface}")
        for variant in variants:
            seen_surfaces[variant] = surface

        example = str(item.get("example", ""))
        if len(WORD_RE.findall(example)) < 8:
            fail(dataset_id, f"例文が8語未満です: {surface}")
        if len(re.findall(re.escape(surface), example, flags=re.IGNORECASE)) != 1:
            fail(dataset_id, f"例文に見出し語句がちょうど1回ありません: {surface}")
        key = example_skeleton(example, surface)
        if key in seen_examples:
            fail(dataset_id, f"例文の骨格が重複しています: {surface}")
        seen_examples[key] = surface

    existing = all_p2_surfaces(vocab_path.name)
    for item, bucket in all_items:
        surface = item_surface(item, bucket)
        variants = surface_variants(surface)
        owners = [owner for variant, owner in existing.items() if variant in variants]
        if owners:
            fail(dataset_id, f"既存準2級語彙と重複しています: {surface} ({owners[0]})")

    forms = lemma_forms()
    for item in words:
        surface = item_surface(item, "words")
        if surface.lower() in forms:
            fail(dataset_id, f"新語がlemmas.jsonのキー・原形値と衝突しています: {surface}")

    owners_by_phrase = phrase_owners()
    for item in idioms:
        phrase = item_surface(item, "idioms")
        owners = owners_by_phrase.get(text_skeleton(phrase), [])
        other_owners = [owner for owner in owners if not owner.startswith(f"{vocab_path.name}:")]
        if other_owners:
            fail(dataset_id, f"全配信データの熟語phraseと重複しています: {phrase} ({other_owners[0]})")

    allowed_idiom_pos = existing_idiom_pos_labels()
    for item in idioms:
        pos = str(item.get("pos", "")).strip()
        if pos == "熟語" or pos not in allowed_idiom_pos:
            fail(dataset_id, f"熟語の品詞ラベルが既存データの集合外です: {item_surface(item, 'idioms')} ({pos})")
    particle_count = sum(bool((item.get("coreImage") or {}).get("particle")) for item in idioms)
    if particle_count < 4:
        fail(dataset_id, f"句動詞のcoreImage.particleが4件未満です: {particle_count}件")

    answer_counts = Counter(int(question["answerIndex"]) for question in questions)
    if any(answer_counts[index] not in range(3, 6) for index in range(4)):
        distribution = [answer_counts[index] for index in range(4)]
        fail(dataset_id, f"正答位置の分布が各3〜5件ではありません: {distribution}")

    for question in questions:
        q = int(question["q"])
        stem = str(question.get("stem", ""))
        word_count = len(WORD_RE.findall(stem))
        if not 15 <= word_count <= 35:
            fail(dataset_id, f"Q{q}の設問文が15〜35語ではありません: {word_count}語")
        if stem.count("(   )") != 1:
            fail(dataset_id, f"Q{q}の設問文の空所が1か所ではありません")
        question_translation = str(question.get("translation", ""))
        if not question_translation:
            fail(dataset_id, f"Q{q}の設問文訳がありません")
        if BLANK_RE.search(question_translation):
            fail(dataset_id, f"Q{q}の訳に空所記号があります")
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        q_items = item_by_q[q]
        if sum(item.get("is_answer") is True for item, _ in q_items) != 1:
            fail(dataset_id, f"Q{q}の正答項目が1件ではありません")
        correct_item, correct_bucket = next(item_pair for item_pair in q_items if item_pair[0].get("is_answer") is True)
        if choices[answer_index] != item_surface(correct_item, correct_bucket):
            fail(dataset_id, f"Q{q}の正答位置と語彙データが一致しません")
        if re.search(re.escape(choices[answer_index]), stem, flags=re.IGNORECASE):
            fail(dataset_id, f"Q{q}の正答語句が設問文に出ています")
        for index, choice in enumerate(choices):
            if index != answer_index and choice_in_stem(choice, stem):
                fail(dataset_id, f"Q{q}の誤答選択肢が設問文に出ています: {choice}")
        if len({item.get("pos") for item, _ in q_items}) != 1:
            fail(dataset_id, f"Q{q}の4択の品詞が一致していません")

    print(f"{dataset_id}: content OK (15 questions / 60 items)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        metavar="DATASET_ID",
        help="単一セットだけ検査する（例: eikenp2-mock-2 または mock-2）",
    )
    args = parser.parse_args()
    dataset_ids = [resolve_dataset_id(args.dataset)] if args.dataset else [dataset_id_for(round_id) for round_id in mock_rounds()]
    for dataset_id in dataset_ids:
        check(dataset_id)


if __name__ == "__main__":
    main()
