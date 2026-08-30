"""英検1級・準1級セットを模試第6回の品質基準で検査する。

問題の内容・ID・進捗キーを変更せず、既存セットの問題文訳・語句カードに
必要なメタデータ、語源、核心イメージ、原形音声、表層音声が揃っているかを確認する。
``--audit`` は不足項目を列挙して終了し、整備前の差分監査に使う。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
VOCAB_AUDIO_DIR = ROOT / "assets" / "audio" / "vocab"
LEMMA_AUDIO_DIR = ROOT / "assets" / "audio" / "lemma"
VOCAB_AUDIO_GRADE = {"eiken1": "1", "eikenp1": "pre1"}
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")
TRANSLATION_BLANK_RE = BLANK_RE
IPA_RE = re.compile(r"^/.+/$")

sys.path.insert(0, str(ROOT / "scripts"))
from check_q1_data import surface_variants  # noqa: E402


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def item_surface(item: dict[str, Any]) -> str:
    return str(item.get("phrase") or item.get("word") or "").strip()


def audio_slug(value: str) -> str:
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", value.strip().lower()))


def text_skeleton(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def surface_matches(example: str, surface: str) -> list[re.Match[str]]:
    """見出し語句の連続形と、二語の分離型句動詞を数える。"""
    parts = surface.split()
    exact = re.compile(
        rf"(?<![A-Za-z]){re.escape(surface)}(?![A-Za-z])",
        flags=re.IGNORECASE,
    )
    matches = list(exact.finditer(example))
    if matches or len(parts) != 2:
        return matches
    separated = re.compile(
        rf"(?<![A-Za-z]){re.escape(parts[0])}(?:\s+[A-Za-z]+){{1,5}}\s+{re.escape(parts[1])}(?![A-Za-z])",
        flags=re.IGNORECASE,
    )
    return list(separated.finditer(example))


def example_skeleton(example: str, surface: str) -> str:
    matches = surface_matches(example, surface)
    if not matches:
        return text_skeleton(example)
    match = matches[0]
    return text_skeleton(example[: match.start()] + "( )" + example[match.end() :])


def manifest_entry(dataset_id: str) -> dict[str, Any]:
    manifest = load(DATA_DIR / "manifest.json")
    entry = manifest.get("q1", {}).get(dataset_id)
    if not isinstance(entry, dict):
        raise ValueError(f"manifest.q1 に {dataset_id} がありません")
    return entry


def data_path(url: str) -> Path:
    if not url.startswith("data/"):
        raise ValueError(f"data URLが不正です: {url}")
    return ROOT / url


def lemma_maps() -> tuple[dict[str, str], dict[str, str]]:
    data = load(DATA_DIR / "lemmas.json")
    canonical = {
        str(surface).lower(): str(lemma).lower()
        for surface, lemma in (data.get("lemmas") or {}).items()
    }
    flashcard = {
        str(surface).lower(): str(lemma).lower()
        for surface, lemma in (data.get("flashcardLemmas") or {}).items()
    }
    return canonical, flashcard


def excluded_lemmas() -> set[str]:
    data = load(DATA_DIR / "word_origin_excluded.json")
    return {
        str(lemma).lower()
        for words in (data.get("excluded") or {}).values()
        for lemma in (words or {})
    }


def expected_audio_path(dataset_id: str, item: dict[str, Any]) -> Path:
    prefix, round_id = dataset_id.split("-", 1)
    surface = item_surface(item)
    subdir = "idiom" if "phrase" in item else ""
    return VOCAB_AUDIO_DIR / VOCAB_AUDIO_GRADE[prefix] / round_id / subdir / f"{audio_slug(surface)}.mp3"


def collect_issues(dataset_id: str, require_audio: bool | None = None) -> list[str]:
    prefix = dataset_id.split("-", 1)[0]
    if prefix not in VOCAB_AUDIO_GRADE:
        raise ValueError(f"対応していない級のdatasetIdです: {dataset_id}")
    if require_audio is None:
        require_audio = prefix == "eiken1"
    entry = manifest_entry(dataset_id)
    questions_path = data_path(str(entry["questionsUrl"]))
    vocab_path = data_path(str(entry["vocabUrl"]))
    questions_data = load(questions_path)
    vocab = load(vocab_path)
    questions = questions_data.get("questions", [])
    words = vocab.get("words", [])
    idioms = vocab.get("idioms", [])
    all_items = [*words, *idioms]
    canonical_lemmas, flashcard_lemmas = lemma_maps()
    origins = load(DATA_DIR / "word_origins.json").get("origins", {})
    origins = {str(key).lower(): value for key, value in origins.items()}
    excluded = excluded_lemmas()
    issues: list[str] = []

    declared_counts = (vocab.get("meta") or {}).get("counts") or {}
    declared_questions = int(entry.get("totalQuestions", len(questions)))
    declared_items = int(entry.get("totalVocabulary", len(all_items)))
    if len(questions) != declared_questions:
        issues.append(f"設問数 {len(questions)} != manifest {declared_questions}")
    if len(all_items) != declared_items:
        issues.append(f"語句数 {len(all_items)} != manifest {declared_items}")
    if declared_counts and int(declared_counts.get("total", len(all_items))) != len(all_items):
        issues.append("vocab.meta.counts.total と実データの件数が不一致")
    if declared_counts:
        for key, actual in (("words", len(words)), ("idioms", len(idioms))):
            if int(declared_counts.get(key, actual)) != actual:
                issues.append(f"vocab.meta.counts.{key} と実データの件数が不一致")

    questions_by_q = {int(question.get("q", -1)): question for question in questions}
    items_by_q: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in all_items:
        try:
            items_by_q[int(item.get("q", -1))].append(item)
        except (TypeError, ValueError):
            issues.append(f"設問番号が不正です: {item_surface(item)}")
    expected_qs = list(range(1, len(questions) + 1))
    if sorted(questions_by_q) != expected_qs:
        issues.append(f"設問番号が1〜{len(questions)}で連続していません")
    if sorted(items_by_q) != expected_qs:
        issues.append(f"語彙側の設問番号が1〜{len(questions)}で連続していません")

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    for q in expected_qs:
        question = questions_by_q.get(q, {})
        items = items_by_q.get(q, [])
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        if len(choices) != 4 or len(items) != 4:
            issues.append(f"Q{q}: 4択または語彙項目が4件ではありません")
            continue
        if not isinstance(answer_index, int) or answer_index not in range(4):
            issues.append(f"Q{q}: answerIndexが不正です")
        if len(BLANK_RE.findall(str(question.get("stem", "")))) != 1:
            issues.append(f"Q{q}: 設問文の空所が1件ではありません")
        if not str(question.get("translation", "")).strip():
            issues.append(f"Q{q}: 設問文の和訳がありません")
        if TRANSLATION_BLANK_RE.search(str(question.get("translation", ""))):
            issues.append(f"Q{q}: 和訳に空所記号があります")
        if sum(bool(item.get("is_answer")) for item in items) != 1:
            issues.append(f"Q{q}: 正答項目が1件ではありません")

        surfaces = [item_surface(item) for item in items]
        if len(set(surfaces)) != 4 or any(not surface for surface in surfaces):
            issues.append(f"Q{q}: 語句が4件の一意な非空項目ではありません")
        for choice in choices:
            if not any(surface_variants(choice) & surface_variants(surface) for surface in surfaces):
                issues.append(f"Q{q}: 選択肢と語彙項目が対応しません: {choice}")
            if re.search(rf"\b{re.escape(choice)}\b", str(question.get("stem", "")), flags=re.IGNORECASE):
                issues.append(f"Q{q}: 選択肢が設問文に露出しています: {choice}")

        meanings = [str(item.get("meaning", "")) for item in items]
        if len(set(meanings)) != 4:
            issues.append(f"Q{q}: 意味が重複しています")

        for item in items:
            surface = item_surface(item)
            label = f"Q{q}/{surface}"
            if not surface:
                continue
            for variant in surface_variants(surface):
                if variant in seen_surfaces:
                    issues.append(f"{label}: 同一セット内で語形が重複しています（{seen_surfaces[variant]}）")
                seen_surfaces[variant] = surface

            for field in ("meaning", "pos", "example", "exampleTranslation", "etymology"):
                if not str(item.get(field, "")).strip():
                    issues.append(f"{label}: {field} がありません")
            if "word" in item and not IPA_RE.fullmatch(str(item.get("ipa", ""))):
                issues.append(f"{label}: IPAがありません")

            example = str(item.get("example", ""))
            if len(WORD_RE.findall(example)) < 8:
                issues.append(f"{label}: 例文が8語未満です")
            if len(surface_matches(example, surface)) != 1:
                issues.append(f"{label}: 例文に見出し語句が1回ありません")
            skeleton = example_skeleton(example, surface)
            if skeleton in seen_examples:
                issues.append(f"{label}: 例文の骨格が重複しています（{seen_examples[skeleton]}）")
            seen_examples[skeleton] = surface

            canonical = canonical_lemmas.get(surface.lower(), surface.lower())
            if prefix == "eiken1" and "word" in item and canonical not in origins and canonical not in excluded:
                issues.append(f"{label}: 語源またはC型理由がありません（原形: {canonical}）")

            audio_path = expected_audio_path(dataset_id, item)
            if require_audio and (not audio_path.is_file() or audio_path.stat().st_size == 0):
                issues.append(f"{label}: 表層音声がありません（{audio_path.relative_to(ROOT)}）")
            if "word" in item:
                lemma = flashcard_lemmas.get(surface.lower())
                if lemma:
                    lemma_audio = LEMMA_AUDIO_DIR / f"{audio_slug(lemma)}.mp3"
                    if not lemma_audio.is_file() or lemma_audio.stat().st_size == 0:
                        issues.append(
                            f"{label}: 原形音声がありません（{lemma_audio.relative_to(ROOT)}）"
                        )
            elif not isinstance(item.get("coreImage"), dict):
                issues.append(f"{label}: 核心イメージがありません")

    return issues


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True, help="例: eiken1-mock-1 / eikenp1-2026-1")
    parser.add_argument(
        "--require-audio",
        action="store_true",
        help="表層MP3も必須にする（準1級では省略時にブラウザ音声を許容）",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="不足項目を列挙するだけで終了する（整備前の監査用）",
    )
    args = parser.parse_args()
    if not any(args.dataset_id.startswith(f"{prefix}-") for prefix in VOCAB_AUDIO_GRADE):
        parser.error("eiken1- または eikenp1- のdatasetIdを指定してください")
    try:
        issues = collect_issues(args.dataset_id, require_audio=args.require_audio or args.dataset_id.startswith("eiken1-"))
    except (KeyError, TypeError, ValueError, FileNotFoundError, json.JSONDecodeError) as error:
        print(f"{args.dataset_id}: 検査自体を実行できません: {error}", file=sys.stderr)
        return 1

    if issues:
        print(f"{args.dataset_id}: {len(issues)}件の不足・不整合")
        for issue in issues:
            print(f"- {issue}")
        return 0 if args.audit else 1
    print(f"{args.dataset_id}: 第6回基準の整合OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
