"""トピック別表現集を、Q1アプリ用の5セットへ変換する。"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCE_PATH = DATA_DIR / "topic_phrases_1.json"
EXAMPLES_PATH = DATA_DIR / "topic_phrase_examples_1.json"
GROUPS_PATH = DATA_DIR / "topic_question_groups_1.json"
STEMS_PATH = DATA_DIR / "topic_question_stems_1.json"

SET_TOPICS = {
    1: ("少子高齢社会", "現代人のモラル", "都市化", "プライバシー", "言論の自由", "女性の権利", "教育", "伝統文化", "スポーツイベント"),
    2: ("犯罪", "刑務所", "違法ダウンロード", "インターネット", "マスメディアと広告"),
    3: ("世界の貧困", "世界の飢餓・水問題", "貿易と関税", "世界経済のボーダーレス化", "世界の問題", "難民・移民の受け入れ"),
    4: ("戦争と紛争", "核兵器", "テロリズム", "自衛隊", "化石燃料と再生可能エネルギー", "原子力発電", "森林破壊"),
    5: ("テクノロジー", "宇宙開発", "医療", "再生医療", "遺伝子組み換え作物", "クローン", "動物実験", "労働", "税"),
}
EXPECTED_QUESTIONS = {1: 20, 2: 11, 3: 19, 4: 16, 5: 18}
AXES = {"problem", "cause", "solution", "concept"}
SET_EXCLUDED_SURFACES = {5: {"discrimination"}}


# 出題表面形を一つに固定する。代替表現は意味・語源欄へ残す。
SURFACE_REPLACEMENTS = {
    "cyber war(fare)": "cyber war",
    "doubt(s) about the effectiveness of recycling": "doubts about the effectiveness of recycling",
}

SURFACE_NOTES = {
    "basic human rights": "fundamental human rights",
    "invade someone's privacy": "violate someone's privacy",
    "dual surnames": "two surnames",
    "crime victim": "victim of a crime",
    "malnourishment": "malnutrition",
    "farming technique": "agricultural technique",
    "food waste": "food loss",
    "a vicious cycle of violence": "a vicious cycle of revenge",
    "weapons of mass destruction": "略：WMD",
    "War Against Terrorism": "War on Terror",
    "tariff": "import tariff / import tax",
    "biological diversity": "biodiversity",
    "required course": "mandatory course",
    "distance education": "correspondence education",
    "academic performance": "academic achievement",
    "elementary education": "primary education",
    "information technology": "略：IT",
    "artificial intelligence": "略：AI",
    "hacking": "cyber attack",
    "International Space Station": "略：ISS",
    "cyber war": "cyber warfare",
    "tuition": "fee",
    "base salary": "basic salary",
    "labor conditions": "work conditions",
    "doubts about the effectiveness of recycling": "doubt about the effectiveness of recycling",
    "maiden name": "補足: 既婚女性の旧姓",
}

# 文脈だけでは軸が決まりにくい語句の最小限の手動補正。
AXIS_OVERRIDES = {
    "aging society": "concept",
    "advancement of medicine": "cause",
    "healthcare system": "concept",
    "sustainable society": "solution",
    "quality of life": "concept",
    "materialism": "cause",
    "sensitive issue": "concept",
    "commuter": "concept",
    "man's connection with nature": "solution",
    "basic human rights": "concept",
    "human life protection": "solution",
    "regulation by state powers": "problem",
    "the First Amendment": "concept",
    "freedom of speech": "concept",
    "gender equality": "solution",
    "the glass ceiling": "problem",
    "maiden name": "concept",
    "excellent human resources": "solution",
    "criminal case": "concept",
    "judgment ability": "concept",
    "crime victim": "problem",
    "emotion of victims": "concept",
    "possibility of correction": "solution",
    "effect of heavy punishment": "solution",
    "parole": "solution",
    "prison break": "problem",
    "torrent site": "concept",
    "pirate": "problem",
    "developing country": "concept",
    "farming technique": "solution",
    "innovation": "solution",
    "genetic modification technology": "concept",
    "food supply": "concept",
    "food security": "solution",
    "all-out war": "problem",
    "deterrent": "solution",
    "a world without nuclear weapons": "solution",
    "secret development": "problem",
    "out of control": "problem",
    "development of technology": "cause",
    "protectionism": "concept",
    "trade balance": "concept",
    "surplus trader": "concept",
    "free trade": "solution",
    "market liberalization": "solution",
    "developing country": "concept",
    "international status": "concept",
    "U.S.-Japan alliance": "concept",
    "popular sentiment": "concept",
    "self-defense": "solution",
    "immigration policy": "concept",
    "maintenance of a workforce": "solution",
    "economic stabilization": "solution",
    "thermal power generation": "concept",
    "low-energy society": "solution",
    "clean energy": "solution",
    "fuel cell": "solution",
    "nuclear power plant": "concept",
    "reliable supply of electricity": "solution",
    "nuclear material": "concept",
    "military utilization": "problem",
    "world natural heritage": "concept",
    "ecotourism": "solution",
    "entrance fee": "concept",
    "tuition": "problem",
    "scholarship": "solution",
    "college credit": "concept",
    "college degree": "concept",
    "graduate school": "concept",
    "curriculum": "concept",
    "creative thinking": "solution",
    "higher education": "solution",
    "work experience": "solution",
    "internship": "solution",
    "cultural heritage": "concept",
    "historic structure": "concept",
    "historic site": "concept",
    "traditional event": "concept",
    "traditional culture": "concept",
    "creation of jobs": "solution",
    "temporary economic effect": "concept",
    "national budget": "concept",
    "technological innovation": "solution",
    "information technology": "concept",
    "electronics industry": "concept",
    "artificial intelligence": "concept",
    "smart appliances": "solution",
    "accessibility": "solution",
    "browsing history": "concept",
    "image search": "concept",
    "search engine": "concept",
    "the emergence of the Internet": "cause",
    "affiliate marketing": "concept",
    "astronaut": "concept",
    "commercial satellite": "concept",
    "habitable planet": "solution",
    "human exploration": "solution",
    "zero-gravity environment": "concept",
    "International Space Station": "concept",
    "space food": "concept",
    "the space race": "cause",
    "the limits of technology": "problem",
    "allocation of resources": "solution",
    "alternative remedy": "solution",
    "prescription": "concept",
    "antibiotic": "concept",
    "pharmaceutical drug": "concept",
    "generic drug": "solution",
    "regenerative medicine": "solution",
    "stem cell": "concept",
    "tissue": "concept",
    "genetic trait": "concept",
    "rejection": "problem",
    "organ trade": "problem",
    "efficiency of crops": "solution",
    "influence on humans": "problem",
    "chemical-free": "solution",
    "monopoly": "problem",
    "product safety": "solution",
    "biohazard": "problem",
    "ethical question": "problem",
    "ecological destruction": "problem",
    "solution to world hunger": "solution",
    "animal rights": "solution",
    "work-life balance": "solution",
    "base salary": "concept",
    "minimum wage": "solution",
    "overtime allowance": "solution",
    "full-time job": "concept",
    "labor conditions": "concept",
    "paid leave": "solution",
    "flexible working hours": "solution",
    "deregulation": "solution",
    "lifelong employment system": "concept",
    "merit system": "concept",
    "progressive taxes": "solution",
    "inheritance": "concept",
    "fairness": "solution",
    "free competition": "solution",
    "media bias": "problem",
    "information sharing": "solution",
    "quick reporting": "solution",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_parenthetical(value: str) -> tuple[str, list[str], list[str], list[str]]:
    etymology: list[str] = []
    abbreviations: list[str] = []
    alternatives: list[str] = []

    def replace(match: re.Match[str]) -> str:
        content = match.group(1).strip()
        if content.startswith("<"):
            etymology.append(content[1:].strip())
        elif content.startswith("略"):
            abbreviations.append(content.split("：", 1)[-1].strip())
        elif content:
            alternatives.append(content)
        return ""

    cleaned = re.sub(r"[（(]([^（）()]*)[）)]", replace, value)
    return cleaned, etymology, abbreviations, alternatives


def normalize_surface(raw: str) -> tuple[str, list[str], list[str], list[str]]:
    value = str(raw or "").strip()
    value = SURFACE_REPLACEMENTS.get(value, value)
    alternatives = []
    variants = [part.strip() for part in value.split("/")]
    value = variants[0]
    alternatives.extend(variants[1:])

    def remove_bracket(match: re.Match[str]) -> str:
        alternatives.append(match.group(1).strip())
        return ""

    value = re.sub(r"\s*\[([^\]]+)\]", remove_bracket, value)
    value = value.replace("doubt(s)", "doubts")
    value, etymology, abbreviations, parenthetical_alternatives = extract_parenthetical(value)
    alternatives.extend(parenthetical_alternatives)
    value = re.sub(r"\s+", " ", value).strip(" ,")
    return value, etymology, abbreviations, alternatives


def normalize_japanese(raw: str) -> tuple[str, list[str]]:
    value, etymology, _, _ = extract_parenthetical(str(raw or "").strip())
    value = re.sub(r"\s+", " ", value).strip()
    return value, etymology


def infer_axis(surface: str, meaning: str) -> str:
    if surface in AXIS_OVERRIDES:
        return AXIS_OVERRIDES[surface]
    text = f"{surface} {meaning}".lower()
    problem_terms = (
        "shortage", "decline", "collapse", "crisis", "deterioration", "overpopulation", "destruction",
        "infringement", "invade", "violate", "suppression", "hate speech", "censorship", "discrimination",
        "harassment", "crime", "criminal", "violence", "repeat offender", "prison population", "prison break",
        "illegal", "poverty", "famine", "drought", "malnutrition", "malnourishment", "stunted", "depletion",
        "war", "weapon", "conflict", "bombing", "proliferation", "out of control", "terror", "barrier",
        "ban", "restriction", "embargo", "friction", "imbalance", "deficit", "influx", "risks", "radioactive",
        "meltdown", "leakage", "acid rain", "desertification", "addiction", "cybercrime", "hacking", "limits",
        "rejection", "organ trade", "monopoly", "exploitation", "biohazard", "ethical question", "doubts",
        "wage reduction", "unpaid", "death from overwork", "suicide", "tax avoidance", "tax evasion", "polarization",
        "bias", "false report", "fall of motivation",
    )
    solution_terms = (
        "preventive", "employment", "sustainable", "unemployment rate", "education", "altruistic", "infrastructure",
        "protection", "equality", "diversity", "rehabilitation", "correction", "punishment", "prevention", "parole",
        "eradicate", "fight against", "fair trade", "opportunities", "improve", "food security", "irrigation",
        "desalination", "defense", "deterrent", "world without", "development", "aid", "support", "contribution",
        "self-defense", "stabilization", "clean energy", "biofuel", "fuel cell", "alternative energy", "conservation",
        "environment", "assessment", "ecotourism", "carbon offset", "scholarship", "creative thinking", "higher education",
        "work experience", "internship", "heritage", "creation of jobs", "promotion", "innovation", "accessibility",
        "authenticity", "information sharing", "quick reporting", "habitable", "exploration", "practicality", "remedy",
        "new drugs", "generic drug", "regenerative", "stem cell", "chemical-free", "product safety", "solution to",
        "animal rights", "work-life balance", "minimum wage", "allowance", "paid leave", "flexible", "deregulation",
        "merit system", "progressive taxes", "fairness", "redistribution", "free competition", "free trade",
    )
    cause_terms = (
        "advancement", "growing trend", "growing popularity", "urbanization", "concentration of population", "emergence",
        "spread of infections", "population growth", "genetic modification", "impact of technology", "space race", "trickle-down",
        "increased spending", "intensified competition", "division of roles", "nuclear families", "secularism",
    )
    def has_term(term: str) -> bool:
        return bool(re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", text))

    if any(has_term(term) for term in problem_terms):
        return "problem"
    if any(has_term(term) for term in solution_terms):
        return "solution"
    if any(has_term(term) for term in cause_terms):
        return "cause"
    return "concept"


def infer_pos(surface: str) -> str:
    if surface.startswith(("have ", "improve ", "eradicate ", "develop ", "pirate ", "invade ")):
        return "動詞句"
    if surface in {"chemical-free", "out of control", "innocent until proven guilty"}:
        return "形容詞句"
    return "名詞"


def normalize_entries(source: dict) -> list[dict]:
    seen_exact: set[str] = set()
    entries: list[dict] = []
    for topic in source.get("topics", []):
        topic_name = topic["topic"]
        for raw in topic.get("entries", []):
            surface, en_etymology, abbreviations, alternatives = normalize_surface(raw.get("en", ""))
            meaning, ja_etymology = normalize_japanese(raw.get("ja", ""))
            exact_key = str(raw.get("en", "")).casefold()
            has_annotation = bool(raw.get("etymology") or en_etymology or ja_etymology)
            if not surface or (exact_key in seen_exact and not has_annotation):
                continue
            seen_exact.add(exact_key)
            if abbreviations and "略" not in meaning:
                meaning += f"（略：{', '.join(abbreviations)}）"
            mapped_note = SURFACE_NOTES.get(surface, "")
            if mapped_note.startswith(("略：", "補足: ")) and mapped_note.split(":", 1)[-1] not in meaning:
                meaning += f"（{mapped_note}）"
                mapped_note = ""
            notes = list(dict.fromkeys([*alternatives, mapped_note]))
            notes = [note for note in notes if note and note not in meaning]
            if notes:
                meaning += f"（別表現: {' / '.join(notes)}）"
            entry = {
                "topic": topic_name,
                "en": surface,
                "ja": meaning,
                "axis": AXIS_OVERRIDES.get(surface) or (raw.get("axis") if raw.get("axis") in AXES else infer_axis(surface, meaning)),
            }
            etymology = [*en_etymology, *ja_etymology]
            if raw.get("etymology"):
                etymology.insert(0, str(raw["etymology"]))
            if etymology:
                entry["etymology"] = " / ".join(dict.fromkeys(etymology))
            entries.append(entry)
    if len(entries) != 325:
        raise ValueError(f"正規化後の語句数が325ではありません: {len(entries)}")
    if any(entry["axis"] not in AXES for entry in entries):
        raise ValueError("axis に未定義の値があります")
    return entries


def topic_source(entries: list[dict], original: dict) -> dict:
    by_topic: dict[str, list[dict]] = {topic["topic"]: [] for topic in original.get("topics", [])}
    for entry in entries:
        by_topic[entry["topic"]].append({key: value for key, value in entry.items() if key != "topic"})
    return {
        "meta": {
            "title": original.get("meta", {}).get("title", "英検1級 トピック別頻出表現"),
            "note": "表層形を正規化し、意味の方向タグ（axis）を付与した出題用の正本。代替表現・略語は意味または語源欄へ移した。",
            "source": original.get("meta", {}).get("source", "ユーザー提供のリスト"),
            "counts": {"topics": len(by_topic), "entries": len(entries)},
        },
        "topics": [{"topic": name, "entries": items} for name, items in by_topic.items()],
    }


def example_key(entry: dict) -> str:
    return f"{entry['topic']}::{entry['en']}"


def load_examples(entries: list[dict]) -> dict[str, dict[str, str]]:
    if not EXAMPLES_PATH.exists():
        raise ValueError(f"例文データがありません: {EXAMPLES_PATH}")
    saved = load_json(EXAMPLES_PATH).get("examples", [])
    if isinstance(saved, dict):
        saved = [{"en": surface, **value} for surface, value in saved.items()]
    examples_by_key: dict[str, dict[str, str]] = {}
    for value in saved:
        if not isinstance(value, dict):
            continue
        key = f"{value.get('topic', '')}::{value.get('en', '')}"
        if key in examples_by_key:
            raise ValueError(f"例文データが重複しています: {key}")
        examples_by_key[key] = {
            field: str(value.get(field, ""))
            for field in ("example", "exampleTranslation")
        }
    expected_keys = {example_key(entry) for entry in entries}
    if set(examples_by_key) != expected_keys:
        missing = sorted(expected_keys - set(examples_by_key))
        extra = sorted(set(examples_by_key) - expected_keys)
        raise ValueError(f"例文データのキーが不一致です: missing={missing} extra={extra}")
    for entry in entries:
        key = example_key(entry)
        item = examples_by_key.get(key)
        if item is None:
            raise ValueError(f"例文データがありません: {key}")
        if not re.search(re.escape(entry["en"]), item["example"], flags=re.IGNORECASE):
            raise ValueError(f"例文に表層形がありません: {entry['en']}")
        if not item["exampleTranslation"]:
            raise ValueError(f"例文訳がありません: {entry['en']}")
    return examples_by_key


def set_entries(entries: list[dict], set_no: int) -> list[dict]:
    allowed = set(SET_TOPICS[set_no])
    excluded = SET_EXCLUDED_SURFACES.get(set_no, set())
    return [entry for entry in entries if entry["topic"] in allowed and entry["en"] not in excluded]


def valid_group_shape(group: list[dict]) -> bool:
    surfaces = [item["en"] for item in group]
    axes = Counter(item["axis"] for item in group)
    return (
        len(group) == 4
        and len(surfaces) == len(set(surfaces))
        and max(axes.values()) <= 2
        and any(count == 1 for count in axes.values())
    )


def group_answer_indices(group: list[dict], indices: tuple[int, ...]) -> tuple[int, ...] | None:
    axes = Counter(item["axis"] for item in group)
    answers = [
        index
        for index in indices
        if axes[group[indices.index(index)]["axis"]] == 1
        and not group[indices.index(index)].get("_repeat")
    ]
    if not answers:
        return None
    answer = min(answers, key=lambda index: group[indices.index(index)].get("_order", index))
    return (answer, *(index for index in indices if index != answer))


def topic_group_candidates(items: list[dict]) -> dict[int, list[tuple[int, tuple[int, ...]]]]:
    by_anchor: dict[int, list[tuple[int, tuple[int, ...]]]] = {index: [] for index in range(len(items))}
    for indices in combinations(range(len(items)), 4):
        group = [items[index] for index in indices]
        if not valid_group_shape(group):
            continue
        ordered = group_answer_indices(group, indices)
        if ordered is None:
            continue
        mask = sum(1 << index for index in indices)
        for index in indices:
            by_anchor[index].append((mask, ordered))
    return by_anchor


def topic_group_pack_options(
    items: list[dict], target: int
) -> list[tuple[int, tuple[int, ...], list[list[dict]], list[dict]]]:
    candidates = topic_group_candidates(items)
    axis_order = tuple(sorted(AXES))

    @lru_cache(maxsize=None)
    def solve(
        available: int, remaining: int
    ) -> tuple[tuple[tuple[int, ...], tuple[tuple[int, ...], ...]], ...]:
        if remaining == 0:
            return (((0, 0, 0, 0), ()),)
        if available.bit_count() < remaining * 4:
            return ()
        anchor = (available & -available).bit_length() - 1
        results: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
        if available.bit_count() > remaining * 4:
            for profile, selected in solve(available ^ (1 << anchor), remaining):
                results.setdefault(profile, selected)
        for mask, ordered in candidates[anchor]:
            if mask & available != mask:
                continue
            group_counts = Counter(items[index]["axis"] for index in ordered)
            group_profile = tuple(group_counts[axis] for axis in axis_order)
            for profile, selected in solve(available ^ mask, remaining - 1):
                combined = tuple(
                    profile[index] + group_profile[index]
                    for index in range(len(axis_order))
                )
                results.setdefault(combined, (ordered, *selected))
        return tuple(results.items())

    options: list[tuple[int, tuple[int, ...], list[list[dict]], list[dict]]] = []
    for group_count in range(target, -1, -1):
        for profile, selected in solve((1 << len(items)) - 1, group_count):
            used = 0
            groups = []
            for indices in selected:
                mask = sum(1 << index for index in indices)
                used |= mask
                groups.append([items[index] for index in indices])
            remaining_items = [
                items[index]
                for index in range(len(items))
                if not (used & (1 << index))
            ]
            options.append((group_count, profile, groups, remaining_items))
    return options


def solve_axis_patterns(axis_counts: Counter[str], group_count: int) -> tuple[tuple[str, ...], ...] | None:
    axis_order = tuple(sorted(AXES))
    patterns = [
        pattern
        for pattern in combinations_with_replacement(axis_order, 4)
        if max(Counter(pattern).values()) <= 2
        and any(count == 1 for count in Counter(pattern).values())
    ]

    @lru_cache(maxsize=None)
    def solve(remaining_axes: tuple[int, ...], remaining_groups: int) -> tuple[tuple[str, ...], ...] | None:
        if remaining_groups == 0:
            return () if not any(remaining_axes) else None
        for pattern in patterns:
            used = Counter(pattern)
            next_axes = tuple(
                remaining_axes[index] - used[axis]
                for index, axis in enumerate(axis_order)
            )
            if min(next_axes) < 0:
                continue
            result = solve(next_axes, remaining_groups - 1)
            if result is not None:
                return (pattern, *result)
        return None

    return solve(tuple(axis_counts[axis] for axis in axis_order), group_count)


def assign_pattern_groups(
    items: list[dict], patterns: tuple[tuple[str, ...], ...]
) -> list[list[dict]] | None:
    unique_patterns = tuple(sorted(set(patterns)))
    initial_counts = tuple(patterns.count(pattern) for pattern in unique_patterns)

    candidates_by_pattern: dict[tuple[str, ...], list[tuple[int, tuple[int, ...]]]] = {
        pattern: [] for pattern in unique_patterns
    }
    allowed_patterns = set(unique_patterns)
    for combo in combinations(range(len(items)), 4):
        group = [items[index] for index in combo]
        pattern = tuple(sorted(item["axis"] for item in group))
        if pattern not in allowed_patterns or len({item["en"] for item in group}) != 4:
            continue
        ordered = group_answer_indices(group, combo)
        if ordered is not None:
            candidates_by_pattern[pattern].append((sum(1 << index for index in combo), ordered))

    @lru_cache(maxsize=None)
    def options(available: int, pattern: tuple[str, ...]) -> tuple[tuple[int, tuple[int, ...]], ...]:
        return tuple(
            candidate
            for candidate in candidates_by_pattern[pattern]
            if candidate[0] & available == candidate[0]
        )

    @lru_cache(maxsize=None)
    def solve(available: int, remaining_counts: tuple[int, ...]) -> tuple[tuple[int, ...], ...] | None:
        if not any(remaining_counts):
            return () if available == 0 else None
        if available.bit_count() != sum(remaining_counts) * 4:
            return None
        candidates: list[tuple[int, int, tuple[tuple[int, tuple[int, ...]], ...]]] = []
        for pattern_index, count in enumerate(remaining_counts):
            if count:
                pattern_options = options(available, unique_patterns[pattern_index])
                if not pattern_options:
                    return None
                candidates.append((len(pattern_options), pattern_index, pattern_options))
        pivot = min(
            (index for index in range(len(items)) if available & (1 << index)),
            key=lambda index: sum(
                any(mask & (1 << index) for mask, _ in pattern_options)
                for _, _, pattern_options in candidates
            ),
        )
        pivot_mask = 1 << pivot
        narrowed = [
            (sum(1 for mask, _ in pattern_options if mask & pivot_mask), pattern_index,
             tuple(candidate for candidate in pattern_options if candidate[0] & pivot_mask))
            for _, pattern_index, pattern_options in candidates
        ]
        for _, pattern_index, pattern_options in sorted(narrowed, key=lambda value: value[0]):
            next_counts = list(remaining_counts)
            next_counts[pattern_index] -= 1
            for mask, ordered in pattern_options:
                result = solve(available ^ mask, tuple(next_counts))
                if result is not None:
                    return (ordered, *result)
        return None

    selected = solve((1 << len(items)) - 1, initial_counts)
    if selected is None:
        return None
    return [[items[index] for index in indices] for indices in selected]


def choose_groups(entries: list[dict], set_no: int) -> list[list[dict]]:
    question_count = EXPECTED_QUESTIONS[set_no]
    repeat_count = question_count * 4 - len(entries)
    if repeat_count < 0 or repeat_count > 3:
        raise ValueError(f"set-{set_no}: 端数再掲数が不正です: {repeat_count}")

    prepared = [dict(entry, _order=index) for index, entry in enumerate(entries)]
    topic_options: list[list[tuple[int, tuple[int, ...], list[list[dict]], list[dict]]]] = []
    for topic in SET_TOPICS[set_no]:
        topic_items = [item for item in prepared if item["topic"] == topic]
        topic_options.append(topic_group_pack_options(topic_items, len(topic_items) // 4))

    states: dict[tuple[int, int, int, int, int], list[tuple[list[list[dict]], list[dict]]]] = {
        (0, 0, 0, 0, 0): []
    }
    for options in topic_options:
        next_states: dict[tuple[int, int, int, int, int], list[tuple[list[list[dict]], list[dict]]]] = {}
        for state, selected_topics in states.items():
            for group_count, profile, groups, remaining in options:
                next_state = tuple(
                    state[index] + profile[index] for index in range(4)
                ) + (state[4] + group_count,)
                next_states.setdefault(next_state, [*selected_topics, (groups, remaining)])
        states = next_states

    surface_counts = Counter(item["en"] for item in prepared)
    axis_counts = Counter(item["axis"] for item in prepared)
    repeat_candidates = {
        axis: [
            dict(item, _repeat=True)
            for item in prepared
            if item["axis"] == axis
            and axis_counts[axis] > 1
            and surface_counts[item["en"]] == 1
        ]
        for axis in sorted(AXES)
    }
    axis_order = tuple(sorted(AXES))
    repeat_axes_order = tuple(axis for axis in axis_order if axis_counts[axis] > 1)
    for state, selected_topics in sorted(states.items(), key=lambda item: -item[0][4]):
        same_topic_groups = [
            group
            for groups, _ in selected_topics
            for group in groups
        ]
        leftovers = [
            item
            for _, remaining in selected_topics
            for item in remaining
        ]
        mixed_count = question_count - len(same_topic_groups)
        for repeat_axes in product(repeat_axes_order, repeat=repeat_count):
            total_axes = Counter(item["axis"] for item in leftovers)
            total_axes.update(repeat_axes)
            patterns = solve_axis_patterns(total_axes, mixed_count)
            if patterns is None:
                continue
            selections = [
                list(combinations(repeat_candidates[axis], repeat_axes.count(axis)))
                if repeat_axes.count(axis)
                else [()]
                for axis in axis_order
            ]
            for selected in product(*selections):
                repeats = [item for group in selected for item in group]
                if len({item["en"] for item in repeats}) != len(repeats):
                    continue
                mixed_groups = assign_pattern_groups(leftovers + repeats, patterns)
                if mixed_groups is None:
                    continue
                groups = same_topic_groups + mixed_groups
                if len(groups) != question_count or any(len(group) != 4 for group in groups):
                    raise ValueError(f"set-{set_no}: 問題数またはグループサイズが不正です")
                return groups
    raise ValueError(f"set-{set_no}: トピック優先の混在問を作れません")


def grouping_report(entries: list[dict], set_no: int, groups: list[list[dict]]) -> None:
    same_topic_counts = Counter(
        group[0]["topic"]
        for group in groups
        if len({item["topic"] for item in group}) == 1
    )
    same_topic_total = sum(same_topic_counts.values())
    repeated = Counter(item["en"] for group in groups for item in group)
    repeated = Counter({surface: count for surface, count in repeated.items() if count > 1})
    print(
        f"set-{set_no}: 同一トピック={same_topic_total}問 / "
        f"混在={len(groups) - same_topic_total}問 / 再掲語={len(repeated)}"
    )
    entry_counts = Counter(item["topic"] for item in entries)
    for topic in SET_TOPICS[set_no]:
        topic_questions = same_topic_counts[topic]
        print(f"  {topic}: {topic_questions}問 / 端数={entry_counts[topic] - topic_questions * 4}")
    if repeated:
        replay_text = ", ".join(f"{surface}×{count}" for surface, count in sorted(repeated.items()))
        print(f"  再掲: {replay_text}")
    if same_topic_total < 55:
        print("  注意: 既存axisタグの制約下では同一トピック55問に届きません")


def freeze_groups(entries: list[dict]) -> None:
    records: list[dict] = []
    for set_no in range(1, 6):
        groups = choose_groups(set_entries(entries, set_no), set_no)
        grouping_report(set_entries(entries, set_no), set_no, groups)
        for q, group in enumerate(groups, 1):
            records.append({
                "set": set_no,
                "q": q,
                "answer": example_key(group[0]),
                "distractors": [example_key(item) for item in group[1:]],
            })
    write_json(
        GROUPS_PATH,
        {
            "meta": {"sets": 5, "questions": len(records)},
            "groups": records,
        },
    )


def load_groups(entries: list[dict]) -> dict[int, list[list[dict]]]:
    entry_by_key = {example_key(entry): entry for entry in entries}
    if not GROUPS_PATH.exists():
        return {
            set_no: choose_groups(set_entries(entries, set_no), set_no)
            for set_no in range(1, 6)
        }

    saved = load_json(GROUPS_PATH)
    records = saved.get("groups", [])
    expected_count = sum(EXPECTED_QUESTIONS.values())
    if saved.get("meta", {}).get("questions") != expected_count or len(records) != expected_count:
        raise ValueError(f"凍結グループの設問数が不正です: {len(records)}")

    grouped: dict[int, dict[int, list[dict]]] = {set_no: {} for set_no in range(1, 6)}
    seen_questions: set[tuple[int, int]] = set()
    answer_keys: list[str] = []
    for record in records:
        set_no = record.get("set")
        q = record.get("q")
        if set_no not in grouped:
            raise ValueError(f"凍結グループのセットまたは設問番号が不正です: {set_no}/{q}")
        if not isinstance(q, int) or q not in range(1, EXPECTED_QUESTIONS[set_no] + 1):
            raise ValueError(f"凍結グループの設問番号が不正です: {set_no}/{q}")
        if (set_no, q) in seen_questions:
            raise ValueError(f"凍結グループの設問番号が重複しています: {set_no}/{q}")
        distractors = record.get("distractors")
        if not isinstance(distractors, list):
            raise ValueError(f"凍結グループの誤答一覧が不正です: {set_no}/{q}")
        keys = [record.get("answer"), *distractors]
        if len(keys) != 4 or len(set(keys)) != 4 or any(key not in entry_by_key for key in keys):
            raise ValueError(f"凍結グループの語句キーが不正です: {set_no}/{q}")
        allowed = {example_key(entry) for entry in set_entries(entries, set_no)}
        if any(key not in allowed for key in keys):
            raise ValueError(f"凍結グループにセット外の語句があります: {set_no}/{q}")
        grouped[set_no][q] = [entry_by_key[key] for key in keys]
        seen_questions.add((set_no, q))
        answer_keys.append(record["answer"])

    if len(answer_keys) != len(set(answer_keys)):
        raise ValueError("凍結グループの正答キーが重複しています")
    ordered_groups: dict[int, list[list[dict]]] = {}
    for set_no, groups_by_q in grouped.items():
        if len(groups_by_q) != EXPECTED_QUESTIONS[set_no]:
            raise ValueError(f"set-{set_no}: 凍結グループの設問数が不正です")
        if sorted(q for current_set, q in seen_questions if current_set == set_no) != list(range(1, EXPECTED_QUESTIONS[set_no] + 1)):
            raise ValueError(f"set-{set_no}: 凍結グループの設問番号が不連続です")
        groups = [groups_by_q[q] for q in range(1, EXPECTED_QUESTIONS[set_no] + 1)]
        keys = [example_key(item) for group in groups for item in group]
        expected_keys = {example_key(entry) for entry in set_entries(entries, set_no)}
        if set(keys) != expected_keys:
            raise ValueError(f"set-{set_no}: 凍結グループの語句一覧が不一致です")
        ordered_groups[set_no] = groups
    return ordered_groups


def load_stems(groups: dict[int, list[list[dict]]]) -> dict[str, dict[str, str]]:
    if not STEMS_PATH.exists():
        raise ValueError(f"設問文データがありません: {STEMS_PATH}")
    saved = load_json(STEMS_PATH).get("stems", [])
    expected = {
        example_key(group[0])
        for groups_for_set in groups.values()
        for group in groups_for_set
    }
    stems_by_key: dict[str, dict[str, str]] = {}
    for value in saved:
        if not isinstance(value, dict):
            continue
        key = str(value.get("answer", ""))
        if key in stems_by_key:
            raise ValueError(f"設問文データが重複しています: {key}")
        if not isinstance(value.get("stem"), str) or not isinstance(value.get("translation"), str):
            raise ValueError(f"設問文データの型が不正です: {key}")
        stems_by_key[key] = {
            "stem": value["stem"],
            "translation": value["translation"],
        }
    if len(saved) != len(expected) or set(stems_by_key) != expected:
        missing = sorted(expected - set(stems_by_key))
        extra = sorted(set(stems_by_key) - expected)
        raise ValueError(f"設問文データのキーが不一致です: missing={missing} extra={extra}")
    entry_by_key = {
        example_key(group[0]): group[0]
        for groups_for_set in groups.values()
        for group in groups_for_set
    }
    for key, value in stems_by_key.items():
        stem = value["stem"]
        if stem.count("( )") != 1:
            raise ValueError(f"設問文の空所が1つではありません: {key}")
        if re.search(re.escape(entry_by_key[key]["en"]), stem, flags=re.IGNORECASE):
            raise ValueError(f"設問文に正答語句が含まれています: {key}")
        if not value["translation"]:
            raise ValueError(f"設問文訳がありません: {key}")
    return stems_by_key


def vocab_item(entry: dict, q: int, is_answer: bool, examples: dict[str, dict[str, str]]) -> dict:
    item = {
        "q": q,
        "is_answer": is_answer,
        "meaning": entry["ja"],
        "example": examples[example_key(entry)]["example"],
        "exampleTranslation": examples[example_key(entry)]["exampleTranslation"],
        "axis": entry["axis"],
        "topic": entry["topic"],
        "pos": "熟語" if len(entry["en"].split()) >= 2 else infer_pos(entry["en"]),
    }
    if entry.get("etymology"):
        item["etymology"] = entry["etymology"]
    item["phrase" if len(entry["en"].split()) >= 2 else "word"] = entry["en"]
    return item


def build_set(
    entries: list[dict],
    set_no: int,
    examples: dict[str, dict[str, str]],
    groups: list[list[dict]],
    stems: dict[str, dict[str, str]],
) -> None:
    vocab_words: list[dict] = []
    vocab_idioms: list[dict] = []
    questions: list[dict] = []
    for q, group in enumerate(groups, 1):
        answer = group[0]
        answer_index = (q * 3 + set_no) % 4
        ordered = [None] * 4
        ordered[answer_index] = answer
        rest = [item for item in group[1:]]
        for index, item in enumerate(rest):
            if ordered[index] is None:
                ordered[index] = item
            else:
                next_index = next(i for i, value in enumerate(ordered) if value is None)
                ordered[next_index] = item
        question_stem = stems[example_key(answer)]
        questions.append({
            "q": q,
            "stem": question_stem["stem"],
            "choices": [item["en"] for item in ordered],
            "answerIndex": answer_index,
            "translation": question_stem["translation"],
            "topic": answer["topic"],
        })
        for item in group:
            target = vocab_idioms if len(item["en"].split()) >= 2 else vocab_words
            target.append(vocab_item(item, q, item is answer, examples))

    counts = {"words": len(vocab_words), "idioms": len(vocab_idioms), "total": len(vocab_words) + len(vocab_idioms)}
    meta = {
        "grade": "英検1級テーマ別",
        "round": f"set-{set_no}",
        "section": "Topic phrases（設問文の空所補充）",
        "source": "data/topic_phrases_1.json（ユーザー提供の表現集）",
        "counts": counts,
        "unique_total": len(set_entries(entries, set_no)),
    }
    write_json(DATA_DIR / f"vocab_topic_set-{set_no}.json", {"meta": meta, "words": vocab_words, "idioms": vocab_idioms})
    write_json(DATA_DIR / f"questions_topic_set-{set_no}.json", {"meta": meta, "questions": questions})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true", help="現在のグルーピングを凍結ファイルに保存する")
    args = parser.parse_args()
    original = load_json(SOURCE_PATH)
    entries = normalize_entries(original)
    write_json(SOURCE_PATH, topic_source(entries, original))
    if args.freeze:
        freeze_groups(entries)
        print(f"topic groups frozen: {sum(EXPECTED_QUESTIONS.values())} questions")
        return
    examples = load_examples(entries)
    groups = load_groups(entries)
    stems = load_stems(groups)
    for set_no in range(1, 6):
        grouping_report(set_entries(entries, set_no), set_no, groups[set_no])
        build_set(entries, set_no, examples, groups[set_no], stems)
    print(f"topic phrases: {len(entries)} unique entries / {len(entries)} examples / 5 sets / 84 questions")


if __name__ == "__main__":
    main()
