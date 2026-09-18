"""問題セットの形式・構造を英検1級セット基準で監査する。

内容（語義の正しさ・和訳の自然さ・難易度）は見ない。形と構造だけを見る。
基準値は data/ の eiken1-* セットから実行時に算出する（BASELINE_PREFIX）。

    py -3 scripts/audit_question_set.py                    # 全セット
    py -3 scripts/audit_question_set.py eiken1-mock-9      # セット指定
    py -3 scripts/audit_question_set.py --grade eikenp2    # 級指定
    py -3 scripts/audit_question_set.py --baseline         # 基準値だけ表示
    py -3 scripts/audit_question_set.py --json             # 機械可読出力
    py -3 scripts/audit_question_set.py --severity error   # ERRORだけ表示

終了コード: ERROR が1件でもあれば 1（--no-fail で常に 0）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BASELINE_PREFIX = "eiken1-"

# --- 基準（eiken1 の実データから確認済みの固定値） ---------------------------
CHOICE_COUNT = 4
STEM_WORDS_MIN = 13          # eiken1 実測の下限
STEM_WORDS_MAX = 45          # eiken1 実測の上限
EXAMPLE_WORDS_MIN = 8        # AUTHORING.md の規則。eiken1 は全件が満たす
ANSWER_POS_MIN_RATIO = 0.10  # 正答位置の偏り WARN 閾値
ANSWER_POS_MAX_RATIO = 0.40
MAX_DISTINCT_POS_PER_Q = 2   # 同一設問内の品詞の散らばり WARN 閾値
PARTICLE_MIN_RATIO = 0.25    # 熟語に占める句動詞（coreImage.particle 付き）の下限
WORD_FIELDS = {"q", "is_answer", "word", "pos", "meaning", "example", "exampleTranslation", "ipa"}
IDIOM_FIELDS = {"q", "is_answer", "phrase", "pos", "meaning", "example", "exampleTranslation", "coreImage"}
FORBIDDEN_FIELDS = {"etymology", "collocation"}
META_FIELDS = {"grade", "round", "section", "source", "counts"}

BLANK_RE = re.compile(r"\(\s*\)")
PAREN_RE = re.compile(r"\([^)]*\)")
TRANSLATION_BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")
BOUNDARY = r"\b"  # 語境界
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
SENTENCE_END_RE = re.compile(r"""[.!?"']$""")


@dataclass
class Finding:
    severity: str   # ERROR / WARN
    dataset: str
    where: str      # "Q12" / "set"
    check: str      # 検査ID
    message: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def words_of(text: str) -> list[str]:
    return WORD_RE.findall(str(text or ""))


def surface(item: dict) -> str:
    return str(item.get("phrase") if item.get("type") == "idiom" else item.get("word", ""))


def variants(value: str) -> set[str]:
    """語形の揺れを吸収する。check_q1_data.surface_variants と同じ考え方。"""
    base = " ".join(str(value or "").lower().split())
    base = re.sub(r"\b(one's|his|her|my|your|our|their|its)\b", "@poss", base)
    out = {base}
    if base.endswith(("ies", "ied")) and len(base) > 3:
        out.add(base[:-3] + "y")
    if base.endswith("es") and len(base) > 3:
        out.add(base[:-2])
    if base.endswith("s") and len(base) > 2:
        out.add(base[:-1])
    if base.endswith("ed") and len(base) > 3:
        stem = base[:-2]
        out |= {stem, stem + "e"}
        if len(stem) > 1 and stem[-1] == stem[-2]:
            out.add(stem[:-1])
    if base.endswith("ing") and len(base) > 4:
        stem = base[:-3]
        out |= {stem, stem + "e"}
        if len(stem) > 1 and stem[-1] == stem[-2]:
            out.add(stem[:-1])
    return {v for v in out if v}


def skeleton(text: str, needle: str = "") -> str:
    value = str(text or "")
    if needle:
        value = re.sub(re.escape(needle), "( )", value, count=1, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).strip().casefold()


def contains_surface(haystack: str, value: str) -> bool:
    for variant in variants(value):
        if len(variant) < 4:
            continue
        if re.search(r"\b" + re.escape(variant) + r"\w{0,3}\b", haystack, re.IGNORECASE):
            return True
    return False


def count_occurrences(text: str, needle: str) -> int:
    """語境界つきで数える。needle が短い語でも他語の一部を拾わないようにする。"""
    if not needle:
        return 0
    pattern = re.escape(needle)
    if needle[:1].isalnum():
        pattern = BOUNDARY + pattern
    if needle[-1:].isalnum():
        pattern = pattern + BOUNDARY
    return len(re.findall(pattern, str(text), re.IGNORECASE))


def grade_of(dataset_id: str) -> str:
    return dataset_id.rsplit("-", 2)[0] if "-" in dataset_id else dataset_id


def family_of(dataset_id: str) -> str:
    """形の比較単位。過去問（YYYY-N）と模試（mock-N）は設問数が違うので分ける。"""
    kind = "mock" if "-mock-" in dataset_id else "regular"
    return f"{grade_of(dataset_id)}/{kind}"


def load_dataset(dataset_id: str, meta: dict) -> dict:
    questions_doc = load_json(ROOT / meta["questionsUrl"])
    vocab_doc = load_json(ROOT / meta["vocabUrl"])
    items = (
        [dict(item, type="word") for item in vocab_doc.get("words", [])]
        + [dict(item, type="idiom") for item in vocab_doc.get("idioms", [])]
    )
    return {
        "id": dataset_id,
        "manifest": meta,
        "questions": questions_doc.get("questions", []),
        "questionsMeta": questions_doc.get("meta", {}),
        "vocabMeta": vocab_doc.get("meta", {}),
        "items": items,
    }


def shape_of(dataset: dict) -> dict:
    """セットの形（設問数・熟語設問数・空所表記）。同級内の多数派との比較に使う。"""
    total = len(dataset["questions"])
    idiom_qs = sorted({int(i["q"]) for i in dataset["items"] if i["type"] == "idiom"})
    tail = list(range(total - len(idiom_qs) + 1, total + 1))
    blanks = Counter(
        (PAREN_RE.findall(q.get("stem", "")) or ["NONE"])[0]
        for q in dataset["questions"]
        if BLANK_RE.search(q.get("stem", ""))
    )
    return {
        "questions": total,
        "idiomQuestions": len(idiom_qs),
        "idiomTail": (idiom_qs == tail) if idiom_qs else True,
        "blankForms": blanks,
    }


# --- 個別の検査 ---------------------------------------------------------------

def audit_structure(ds: dict, majority: dict, add) -> None:
    questions, items = ds["questions"], ds["items"]
    numbers = [q.get("q") for q in questions]
    if numbers != list(range(1, len(questions) + 1)):
        add("ERROR", "set", "S01", "設問番号が1からの連番になっていない")
    by_q: dict[int, list[dict]] = defaultdict(list)
    for item in items:
        by_q[int(item["q"])].append(item)
    for q in numbers:
        if len(by_q.get(q, [])) != CHOICE_COUNT:
            add("ERROR", f"Q{q}", "S02", f"語彙が{len(by_q.get(q, []))}件（4件必要）")
    orphans = sorted(set(by_q) - set(numbers))
    if orphans:
        add("ERROR", "set", "S03", f"設問のない語彙番号: {orphans}")

    shape = shape_of(ds)
    if majority:
        for key, label in (("questions", "設問数"), ("idiomQuestions", "熟語設問数")):
            if shape[key] != majority[key]:
                add("WARN", "set", "S04",
                    f"{label}が同種セットの標準と違う: {shape[key]}（標準 {majority[key]}）")
    if not shape["idiomTail"]:
        add("ERROR", "set", "S05", "熟語設問がセット末尾に連続していない")
    if len(shape["blankForms"]) > 1:
        add("ERROR", "set", "S06",
            f"空所の表記がセット内で混在: {dict(shape['blankForms'])}")
    elif majority and shape["blankForms"] and majority.get("blankForm") \
            and next(iter(shape["blankForms"])) != majority["blankForm"]:
        add("WARN", "set", "S07",
            f"空所表記が同種セットの標準と違う: {next(iter(shape['blankForms']))!r}"
            f"（標準 {majority['blankForm']!r}）")

    meta = ds["questionsMeta"]
    missing = META_FIELDS - set(meta)
    if missing:
        add("ERROR", "set", "S08", f"questions の meta に不足: {sorted(missing)}")
    if ds["vocabMeta"] and ds["vocabMeta"] != meta:
        add("WARN", "set", "S09", "questions と vocab の meta が一致しない")
    counts = meta.get("counts") or {}
    actual = {
        "words": sum(1 for i in items if i["type"] == "word"),
        "idioms": sum(1 for i in items if i["type"] == "idiom"),
        "total": len(items),
    }
    if counts and {k: counts.get(k) for k in actual} != actual:
        add("ERROR", "set", "S10", f"meta.counts が実データと不一致: {counts} != {actual}")
    manifest = ds["manifest"]
    if manifest.get("totalQuestions") != len(questions) or manifest.get("totalVocabulary") != len(items):
        add("ERROR", "set", "S11", "manifest の totalQuestions/totalVocabulary が実データと不一致")


def audit_questions(ds: dict, add, rows: dict) -> None:
    by_q: dict[int, list[dict]] = defaultdict(list)
    for item in ds["items"]:
        by_q[int(item["q"])].append(item)
    positions: Counter[int] = Counter()
    for question in ds["questions"]:
        q = int(question.get("q", 0))
        where = f"Q{q}"
        stem = str(question.get("stem", ""))
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        group = by_q.get(q, [])

        if len(choices) != CHOICE_COUNT or answer_index not in range(CHOICE_COUNT):
            add("ERROR", where, "Q01", "選択肢が4件でないか answerIndex が範囲外")
            continue
        positions[answer_index] += 1
        if len(set(choices)) != CHOICE_COUNT:
            add("ERROR", where, "Q02", "選択肢が重複している")

        blanks = len(BLANK_RE.findall(stem))
        if blanks != 1:
            add("ERROR", where, "Q03", f"空所が{blanks}か所（1か所必要）")
        count = len(words_of(stem))
        if not (STEM_WORDS_MIN <= count <= STEM_WORDS_MAX):
            add("WARN", where, "Q04",
                f"設問文が{count}語（基準 {STEM_WORDS_MIN}〜{STEM_WORDS_MAX}語）")

        for index, choice in enumerate(choices):
            if contains_surface(stem, choice):
                kind = "正答" if index == answer_index else "誤答"
                add("ERROR", where, "Q05", f"{kind}語 {choice!r} が設問文に出ている")

        translation = str(question.get("translation", ""))
        if not translation.strip():
            add("ERROR", where, "Q06", "設問文の和訳がない")
        elif TRANSLATION_BLANK_RE.search(translation):
            add("ERROR", where, "Q07", "設問文の和訳に空所記号が残っている")

        surfaces = [surface(item) for item in group]
        if len(surfaces) == CHOICE_COUNT:
            matched = [
                choice for choice in choices
                if sum(bool(variants(choice) & variants(s)) for s in surfaces) == 1
            ]
            if len(matched) != CHOICE_COUNT:
                add("ERROR", where, "Q08", "選択肢と語彙項目が1対1で対応しない")
            answers = [item for item in group if item.get("is_answer")]
            if len(answers) != 1:
                add("ERROR", where, "Q09", f"is_answer が{len(answers)}件（1件必要）")
            elif not (variants(surface(answers[0])) & variants(choices[answer_index])):
                add("ERROR", where, "Q10", "is_answer の語句と answerIndex の選択肢が違う")
            meanings = [str(item.get("meaning", "")) for item in group]
            if len(set(meanings)) != len(meanings):
                add("ERROR", where, "Q11", "同一設問内で meaning が重複している")
            kinds = {item["type"] for item in group}
            if len(kinds) > 1:
                add("ERROR", where, "Q12", "同一設問に単語と熟語が混在している")
            distinct_pos = {str(item.get("pos", "")) for item in group}
            if len(distinct_pos) > MAX_DISTINCT_POS_PER_Q:
                add("WARN", where, "Q13",
                    f"選択肢の品詞が{len(distinct_pos)}種類: {sorted(distinct_pos)}")
        rows["stems"].append((skeleton(stem), f"{ds['id']}/{where}"))

    total = sum(positions.values())
    if total:
        for index in range(CHOICE_COUNT):
            ratio = positions[index] / total
            if ratio < ANSWER_POS_MIN_RATIO or ratio > ANSWER_POS_MAX_RATIO:
                add("WARN", "set", "Q14",
                    f"正答位置の偏り: 選択肢{index + 1}が{positions[index]}/{total}問")
    ds["_positions"] = positions


def audit_items(ds: dict, add, rows: dict) -> None:
    for item in ds["items"]:
        where = f"Q{item.get('q')}/{surface(item) or '?'}"
        expected = WORD_FIELDS if item["type"] == "word" else IDIOM_FIELDS
        present = set(item) - {"type"}
        missing = expected - present
        if missing:
            severity = "WARN" if missing == {"ipa"} else "ERROR"
            add(severity, where, "V01", f"フィールド不足: {sorted(missing)}")
        if item["type"] == "idiom" and "ipa" in item:
            add("WARN", where, "V03", "熟語に ipa が付いている（基準セットには無い）")
        for field in ("meaning", "example", "exampleTranslation", "pos"):
            if not str(item.get(field, "")).strip():
                add("ERROR", where, "V04", f"{field} が空")

        text = str(item.get("example", ""))
        head = surface(item)
        hits = count_occurrences(text, head)
        if hits != 1:
            add("ERROR", where, "V05", f"例文に見出し語句が{hits}回（ちょうど1回必要）")
        length = len(words_of(text))
        if length < EXAMPLE_WORDS_MIN:
            add("ERROR", where, "V06", f"例文が{length}語（{EXAMPLE_WORDS_MIN}語以上）")
        if text.strip() and not SENTENCE_END_RE.search(text.strip()):
            add("WARN", where, "V07", "例文が句読点で終わっていない")

        if item["type"] == "idiom":
            core = item.get("coreImage") or {}
            chain = core.get("chain") or []
            if len(chain) < 3:
                add("ERROR", where, "V08", f"coreImage.chain が{len(chain)}段（3段以上）")
            if any(not str(step.get("gloss", "")).strip() for step in chain):
                add("ERROR", where, "V09", "coreImage.chain に gloss の空要素がある")

        rows["examples"].append((skeleton(text, head), f"{ds['id']}/{where}"))
        rows["exampleTranslations"].append(
            (skeleton(item.get("exampleTranslation", ""), str(item.get("meaning", ""))),
             f"{ds['id']}/{where}")
        )

    stray = Counter()
    for item in ds["items"]:
        stray.update((set(item) - {"type"}) & FORBIDDEN_FIELDS)
    for field, count in sorted(stray.items()):
        add("WARN", "set", "V02",
            f"付けてはいけないフィールド {field} が{count}件（基準セットには無い）")

    idioms = [i for i in ds["items"] if i["type"] == "idiom"]
    if idioms:
        with_particle = sum(1 for i in idioms if (i.get("coreImage") or {}).get("particle"))
        if with_particle == 0:
            add("ERROR", "set", "V10", "句動詞（coreImage.particle 付き）が0件")
        elif with_particle < len(idioms) * PARTICLE_MIN_RATIO:
            add("WARN", "set", "V10",
                f"句動詞が{with_particle}/{len(idioms)}件"
                f"（下限 {PARTICLE_MIN_RATIO:.0%}。基準セットは概ね全件）")


def audit_cross(rows: dict, findings: list[Finding]) -> None:
    labels = {
        "stems": ("X01", "設問文の骨格"),
        "examples": ("X02", "例文の骨格"),
        "exampleTranslations": ("X03", "例文訳の骨格"),
    }
    for key, (check, label) in labels.items():
        seen: dict[str, str] = {}
        for value, owner in rows[key]:
            if not value:
                continue
            dataset, _, where = owner.partition("/")
            if value not in seen:
                seen[value] = owner
                continue
            same_set = seen[value].partition("/")[0] == dataset
            findings.append(Finding(
                "ERROR" if same_set else "WARN", dataset, where, check,
                f"{label}が{'同一セット内で重複' if same_set else '別セットと同一'}: {seen[value]}",
            ))


# --- 実行 ---------------------------------------------------------------------

def majority_shape(datasets: list[dict]) -> dict:
    if not datasets:
        return {}
    shapes = [shape_of(d) for d in datasets]
    blank: Counter[str] = Counter()
    for shape in shapes:
        blank.update(shape["blankForms"])
    return {
        "questions": Counter(s["questions"] for s in shapes).most_common(1)[0][0],
        "idiomQuestions": Counter(s["idiomQuestions"] for s in shapes).most_common(1)[0][0],
        "blankForm": blank.most_common(1)[0][0] if blank else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="問題セットの形式・構造を監査します")
    parser.add_argument("datasets", nargs="*", help="監査する datasetId（省略時は全件）")
    parser.add_argument("--grade", help="級で絞る（例: eiken1, eikenp2, iuhw）")
    parser.add_argument("--severity", choices=["error", "warn"], default="warn",
                        help="表示する最低深刻度（既定 warn）")
    parser.add_argument("--baseline", action="store_true", help="基準値を表示して終了")
    parser.add_argument("--json", action="store_true", help="JSONで出力")
    parser.add_argument("--no-fail", action="store_true", help="ERRORがあっても終了コード0")
    args = parser.parse_args()

    manifest = load_json(DATA_DIR / "manifest.json")["q1"]
    all_datasets = {ds_id: load_dataset(ds_id, meta) for ds_id, meta in manifest.items()}
    baseline = [d for ds_id, d in all_datasets.items() if ds_id.startswith(BASELINE_PREFIX)]

    if args.baseline:
        shape = majority_shape(baseline)
        stems = [len(words_of(q.get("stem", ""))) for d in baseline for q in d["questions"]]
        examples = [len(words_of(i.get("example", ""))) for d in baseline for i in d["items"]]
        print(f"基準セット: {len(baseline)}件 ({BASELINE_PREFIX}*)")
        print(f"  設問数の標準: {shape['questions']} / 熟語設問: {shape['idiomQuestions']}")
        print(f"  空所表記の標準: {shape['blankForm']!r}")
        print(f"  設問文の語数: {min(stems)}〜{max(stems)}")
        print(f"  例文の語数: {min(examples)}〜{max(examples)}")
        return 0

    targets = list(all_datasets)
    if args.datasets:
        unknown = [d for d in args.datasets if d not in all_datasets]
        if unknown:
            print(f"未知の datasetId: {unknown}", file=sys.stderr)
            return 2
        targets = args.datasets
    if args.grade:
        targets = [d for d in targets if grade_of(d) == args.grade]
    if not targets:
        print("対象セットがありません", file=sys.stderr)
        return 2

    by_family: dict[str, list[dict]] = defaultdict(list)
    for ds_id, dataset in all_datasets.items():
        by_family[family_of(ds_id)].append(dataset)

    findings: list[Finding] = []
    rows = {"stems": [], "examples": [], "exampleTranslations": []}
    metrics: dict[str, dict] = {}

    for ds_id, dataset in all_datasets.items():  # 骨格の重複は全セット横断で見る
        local: list[Finding] = []

        def add(severity, where, check, message, _dataset=ds_id, _sink=local):
            _sink.append(Finding(severity, _dataset, where, check, message))

        audit_structure(dataset, majority_shape(by_family[family_of(ds_id)]), add)
        audit_questions(dataset, add, rows)
        audit_items(dataset, add, rows)
        if ds_id in targets:
            findings.extend(local)
            positions = dataset.get("_positions", Counter())
            metrics[ds_id] = {
                "questions": len(dataset["questions"]),
                "vocabulary": len(dataset["items"]),
                "answerPositions": [positions[i] for i in range(CHOICE_COUNT)],
            }

    cross: list[Finding] = []
    audit_cross(rows, cross)
    findings.extend(f for f in cross if f.dataset in targets)

    order = {"ERROR": 0, "WARN": 1}
    findings.sort(key=lambda f: (f.dataset, order[f.severity], f.check, f.where))
    if args.severity == "error":
        findings = [f for f in findings if f.severity == "ERROR"]

    errors = sum(1 for f in findings if f.severity == "ERROR")
    warns = len(findings) - errors

    if args.json:
        print(json.dumps({
            "baseline": BASELINE_PREFIX,
            "targets": targets,
            "metrics": metrics,
            "summary": {"error": errors, "warn": warns},
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
    else:
        current = None
        for finding in findings:
            if finding.dataset != current:
                current = finding.dataset
                counts = metrics[current]
                print(f"\n## {current}  設問{counts['questions']} / 語彙{counts['vocabulary']}"
                      f" / 正答位置{counts['answerPositions']}")
            print(f"  [{finding.severity}] {finding.check} {finding.where}: {finding.message}")
        clean = [t for t in targets if all(f.dataset != t for f in findings)]
        if clean:
            print(f"\n指摘なし: {', '.join(clean)}")
        print(f"\n合計 ERROR {errors} / WARN {warns}（対象 {len(targets)}セット）")

    return 1 if errors and not args.no_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
