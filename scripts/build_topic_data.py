"""トピック別表現集を、Q1アプリ用の5セットへ変換する。"""

from __future__ import annotations

import json
import re
from collections import Counter
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCE_PATH = DATA_DIR / "topic_phrases_1.json"
EXAMPLES_PATH = DATA_DIR / "topic_phrase_examples_1.json"

SET_TOPICS = {
    1: ("少子高齢社会", "現代人のモラル", "都市化", "プライバシー", "言論の自由", "女性の権利", "教育", "伝統文化", "スポーツイベント"),
    2: ("犯罪", "刑務所", "違法ダウンロード", "インターネット", "マスメディアと広告"),
    3: ("世界の貧困", "世界の飢餓・水問題", "貿易と関税", "世界経済のボーダーレス化", "世界の問題", "難民・移民の受け入れ"),
    4: ("戦争と紛争", "核兵器", "テロリズム", "自衛隊", "化石燃料と再生可能エネルギー", "原子力発電", "森林破壊"),
    5: ("テクノロジー", "宇宙開発", "医療", "再生医療", "遺伝子組み換え作物", "クローン", "動物実験", "労働", "税"),
}
EXPECTED_QUESTIONS = {1: 20, 2: 11, 3: 19, 4: 16, 5: 18}
AXES = {"problem", "cause", "solution", "concept"}


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


def make_example(entry: dict) -> tuple[str, str]:
    surface = entry["en"]
    meaning = entry["ja"]
    if surface == "have a high concentration of population":
        return (
            "Major cities have a high concentration of population, so public services must be planned carefully.",
            "大都市では人口が集中しているため、公共サービスを慎重に計画しなければならない。",
        )
    if surface == "improve food self-sufficiency rate":
        return (
            "The government aims to improve food self-sufficiency rate by supporting local farmers.",
            "政府は地元の農家を支援することで、食料自給率の改善を目指している。",
        )
    if surface == "eradicate extreme poverty":
        return (
            "International agencies work to eradicate extreme poverty through education and healthcare.",
            "国際機関は教育と医療を通じて極度の貧困を根絶しようとしている。",
        )
    if surface == "develop new drugs":
        return (
            "Researchers are working to develop new drugs for infections that resist current treatments.",
            "研究者たちは、現在の治療に抵抗する感染症向けの新薬を開発しようとしている。",
        )
    if surface == "pirate":
        return (
            "Some users pirate copyrighted material despite repeated legal warnings.",
            "一部の利用者は、法的な警告を何度受けても著作物を違法に複製する。",
        )
    if surface == "invade someone's privacy":
        return (
            "Aggressive apps can invade someone's privacy without clear consent.",
            "過剰なアプリは、明確な同意なしに人のプライバシーを侵害することがある。",
        )
    if surface == "out of control":
        return (
            "Without effective oversight, the spread of false information could get out of control.",
            "効果的な監視がなければ、誤情報の拡散は制御不能になる可能性がある。",
        )
    if surface == "innocent until proven guilty":
        return (
            "In a fair trial, every suspect is treated as innocent until proven guilty.",
            "公正な裁判では、すべての容疑者は有罪と証明されるまで無罪として扱われる。",
        )
    if surface == "chemical-free":
        return (
            "Many consumers prefer chemical-free produce when they can afford it.",
            "多くの消費者は、購入できる余裕があれば無農薬の農産物を好む。",
        )

    if surface.startswith(("have ", "improve ", "eradicate ", "develop ", "pirate ", "invade ")):
        return (
            f"Governments should {surface} when they want to protect vulnerable communities.",
            f"政府は、弱い立場の地域社会を守りたいなら、{meaning}べきだ。",
        )
    templates = {
        "problem": (
            f"Experts warned that {surface} could seriously harm local communities if ignored.",
            f"専門家は、{meaning}を放置すれば地域社会に深刻な影響を与える可能性があると警告した。",
        ),
        "cause": (
            f"Researchers identified {surface} as one factor behind the rapid social change.",
            f"研究者は、{meaning}が急速な社会変化の一因だと説明した。",
        ),
        "solution": (
            f"The government promoted {surface} to improve people's lives over the long term.",
            f"政府は、長期的に人々の生活を改善するため、{meaning}を推進した。",
        ),
        "concept": (
            f"The policy debate focused on {surface} and its effects on society.",
            f"その政策論争では、{meaning}と社会への影響が焦点になった。",
        ),
    }
    return templates[entry["axis"]]


def example_key(entry: dict) -> str:
    return f"{entry['topic']}::{entry['en']}"


def load_examples(entries: list[dict]) -> dict[str, dict[str, str]]:
    generated = {example_key(entry): dict(zip(("example", "exampleTranslation"), make_example(entry))) for entry in entries}
    if EXAMPLES_PATH.exists():
        saved = load_json(EXAMPLES_PATH).get("examples", [])
        if isinstance(saved, dict):
            saved = [{"en": surface, **value} for surface, value in saved.items()]
        for value in saved:
            key = f"{value.get('topic', '')}::{value.get('en', '')}"
            if key in generated and isinstance(value, dict):
                generated[key].update({key: str(value[key]) for key in ("example", "exampleTranslation") if value.get(key)})
    for entry in entries:
        item = generated[example_key(entry)]
        if entry["en"] not in item["example"]:
            raise ValueError(f"例文に表層形がありません: {entry['en']}")
        if not item["exampleTranslation"]:
            raise ValueError(f"例文訳がありません: {entry['en']}")
    example_rows = [
        {"topic": entry["topic"], "en": entry["en"], **generated[example_key(entry)]}
        for entry in entries
    ]
    write_json(EXAMPLES_PATH, {"meta": {"source": "data/topic_phrases_1.json", "entries": len(example_rows)}, "examples": example_rows})
    return generated


def set_entries(entries: list[dict], set_no: int) -> list[dict]:
    allowed = set(SET_TOPICS[set_no])
    return [entry for entry in entries if entry["topic"] in allowed]


def choose_groups(entries: list[dict], set_no: int) -> list[list[dict]]:
    question_count = EXPECTED_QUESTIONS[set_no]
    repeat_count = question_count * 4 - len(entries)
    if repeat_count < 0 or repeat_count > 3:
        raise ValueError(f"set-{set_no}: 端数再掲数が不正です: {repeat_count}")
    base_pool = [dict(entry, _occurrence=i) for i, entry in enumerate(entries)]
    base_pool += [dict(entries[i], _occurrence=len(entries) + i) for i in range(repeat_count)]
    axis_order = tuple(sorted(AXES))
    patterns = [
        pattern
        for pattern in combinations_with_replacement(axis_order, 4)
        if max(Counter(pattern).values()) <= 2
    ]

    @lru_cache(maxsize=None)
    def solve(remaining_groups: int, remaining_axes: tuple[int, ...]) -> tuple[tuple[str, ...], ...] | None:
        if remaining_groups == 0:
            return () if not any(remaining_axes) else None
        for pattern in patterns:
            used = Counter(pattern)
            next_axes = tuple(remaining_axes[i] - used[axis] for i, axis in enumerate(axis_order))
            if min(next_axes) < 0:
                continue
            result = solve(remaining_groups - 1, next_axes)
            if result is not None:
                return (pattern, *result)
        return None

    axis_counts = Counter(item["axis"] for item in base_pool)
    axis_patterns = solve(question_count, tuple(axis_counts[axis] for axis in axis_order))
    if axis_patterns is None:
        raise ValueError(f"set-{set_no}: axis規則を満たす組み合わせを作れません")

    pools = {axis: [item for item in base_pool if item["axis"] == axis] for axis in axis_order}
    groups: list[list[dict]] = []
    for pattern in axis_patterns:
        group: list[dict] = []
        for axis in pattern:
            candidates = [item for item in pools[axis] if item["en"] not in {x["en"] for x in group}]
            if not candidates:
                raise ValueError(f"set-{set_no}: 同一問の表層形重複を避けられません")
            chosen = max(candidates, key=lambda item: item["topic"] == group[0]["topic"] if group else False)
            pools[axis].remove(chosen)
            group.append(chosen)
        groups.append(group)
    if any(pools.values()) or len(groups) != question_count:
        raise ValueError(f"set-{set_no}: 問題数またはaxis項目数が不正です")
    return groups


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


def build_set(entries: list[dict], set_no: int, examples: dict[str, dict[str, str]]) -> None:
    groups = choose_groups(set_entries(entries, set_no), set_no)
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
        surface = answer["en"]
        stem = examples[example_key(answer)]["example"].replace(surface, "( )", 1)
        questions.append({
            "q": q,
            "stem": stem,
            "choices": [item["en"] for item in ordered],
            "answerIndex": answer_index,
            "translation": examples[example_key(answer)]["exampleTranslation"],
            "topic": answer["topic"],
        })
        for item in group:
            target = vocab_idioms if len(item["en"].split()) >= 2 else vocab_words
            target.append(vocab_item(item, q, item is answer, examples))

    counts = {"words": len(vocab_words), "idioms": len(vocab_idioms), "total": len(vocab_words) + len(vocab_idioms)}
    meta = {
        "grade": "英検1級テーマ別",
        "round": f"set-{set_no}",
        "section": "Topic phrases（英語例文の空所補充）",
        "source": "data/topic_phrases_1.json（ユーザー提供の表現集）",
        "counts": counts,
        "unique_total": len(set_entries(entries, set_no)),
    }
    write_json(DATA_DIR / f"vocab_topic_set-{set_no}.json", {"meta": meta, "words": vocab_words, "idioms": vocab_idioms})
    write_json(DATA_DIR / f"questions_topic_set-{set_no}.json", {"meta": meta, "questions": questions})


def main() -> None:
    original = load_json(SOURCE_PATH)
    entries = normalize_entries(original)
    write_json(SOURCE_PATH, topic_source(entries, original))
    examples = load_examples(entries)
    for set_no in range(1, 6):
        build_set(entries, set_no, examples)
    print(f"topic phrases: {len(entries)} unique entries / {len(entries)} examples / 5 sets / 84 questions")


if __name__ == "__main__":
    main()
