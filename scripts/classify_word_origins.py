"""暗記カードの「語源・なりたち」をルールで分類し、崩れた語源文を洗い出す。

使い方:
    python scripts/classify_word_origins.py [--report docs/WORD_ORIGIN_CLASSIFICATION.md]

Jev を使わない決定的な分類。次の3つを根拠にする。
  - data/word_origins.json                    表示される語源文・構成パーツ・語源チェーン
  - data/word_origin_research.json の research originLanguage・historicalPath・confidence
  - data/word_roots.json                      A型の語根の由来言語

分類軸（ラベルは scripts/jev_classify_word_origins.py と共通）:
  lineage   : latin / greek / germanic / french_non_latin / other / mixed / english / unknown
              english = 英語内部の派生・複合だけが書かれ、さらに古い系統が示されていない
  formation : affix_root / compound / borrowing / semantic_shift / imitative / eponym / shortening / unclear

品質フラグ:
  bogus_source      「英語 the に由来」「英語 Russian に由来」「英語 un- に由来」のように、
                    語源でない語・言語名・接頭辞だけを英語の語源として書いている
  circular          「英語 hunch に由来」「英語 provide の過去分詞形」のように、見出し語自身や
                    その派生語・原形を挙げるだけで語源になっていない
  inflected_key     キーが原形でない（「原形Xからの語形変化」を含む）
  no_arrow          導出文に「→」（現在の意味への橋渡し）がない
  low_confidence    再調査台帳の confidence が low
  legacy            再調査台帳で未再調査（status: legacy）

結果は out/word-origin-classes.json と out/word-origin-classes.csv に保存する。
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "out"

FAMILY_PATTERNS = {
    "greek": r"ギリシャ|Greek",
    "latin": r"ラテン|Latin",
    "germanic": r"古英語|ゲルマン|ノルド|オランダ|ドイツ|フリジア|スカンジナビア|フランク|Old English|Germanic|Norse|Dutch|German|Frisian|Scandinavian|Frankish",
    "french": r"フランス|フレンチ|French|Anglo",
    "other": (
        r"アラビア|ヘブライ|ペルシャ|サンスクリット|ヒンディー|ケルト|ゲール|アイルランド|ブリトン|"
        r"スペイン|イタリア|ポルトガル|日本語|中国語|ロシア|エトルリア|オック|トルコ|マレー|アルゴンキン|"
        r"Arabic|Hebrew|Persian|Sanskrit|Hindi|Celtic|Gaelic|Irish|Spanish|Italian|Japanese|Chinese|Russian|Algonquian|Turkish"
    ),
}

FORMATION_RULES = [
    ("unclear", r"語源未詳|語源不明|起源不明|不詳|確定していない|はっきりしない|起源は不明"),
    ("imitative", r"擬音|擬声|音をまね|音を模|音を表す|imitative|echoic"),
    ("eponym", r"人名|地名|固有名|神話|にちなむ|に因む|ちなんで|商標|ブランド名"),
    ("shortening", r"短縮|逆成|略語|略した|混成|頭字語"),
]
SHIFT_PATTERN = r"ことから|から →|意味へ|転じ|比喩|広がっ|たとえ"
AFFIX_TEXT = r"[＋+]\s*-|-[＋+]|に-\w+を付けた語|[a-z]+-（"

# 「英語 X に由来」の X に入っていたら語源として成り立たない語
JUNK_TOKENS = {
    "a", "an", "the", "or", "c", "br", "obsolete", "causative", "assimilated", "noun",
    "dialectal", "past", "present", "all", "age", "cover", "open", "out", "over", "up", "short",
}


def load() -> tuple[dict, dict, dict]:
    origins = json.loads((ROOT / "data/word_origins.json").read_text(encoding="utf-8"))["origins"]
    research = json.loads((ROOT / "data/word_origin_research.json").read_text(encoding="utf-8"))["entries"]
    roots = json.loads((ROOT / "data/word_roots.json").read_text(encoding="utf-8"))["roots"]
    root_origin = {}
    for form, r in roots.items():
        for f in [form, *r.get("variants", [])]:
            root_origin.setdefault(f, r.get("origin", ""))
    return origins, research, root_origin


def families(text: str) -> set[str]:
    return {fam for fam, pat in FAMILY_PATTERNS.items() if re.search(pat, text)}


def lineage(word: str, entry: dict, res: dict, root_origin: dict) -> tuple[str, str]:
    """(ラベル, 根拠) を返す。台帳・語根辞書・表示文をまとめて見て、最も古い系統を採る。"""
    ledger = " ".join([res.get("originLanguage", ""), *res.get("historicalPath", [])])
    roots = " ".join(root_origin.get(p["form"], "") for p in entry.get("parts", []) if p["kind"] == "root")
    display = entry["derivation"] + " " + " ".join(s.get("term", "") for s in entry.get("chain", []))
    text = " ".join([ledger, roots, display])
    fams = families(text)
    basis = "ledger" if families(ledger + " " + roots) else "display"
    if not fams:
        # 「英語 safe に -ly」のように英語内部の派生・複合だけが書かれている
        if re.search(r"英語|English", text):
            return "english", basis
        return "unknown", "none"
    classical = fams & {"greek", "latin"}
    # dead＋line のように、ゲルマン系と古典語系の要素を英語で組み合わせた語
    if classical and "germanic" in fams and re.search(r"[＋+]", entry["derivation"]):
        return "mixed", basis
    for fam in ("greek", "latin", "germanic"):
        if fam in fams:
            return fam, basis
    if "french" in fams:
        return "french_non_latin", basis
    return "other", basis


def formation(word: str, entry: dict, lin: str) -> str:
    d = entry["derivation"]
    for label, pat in FORMATION_RULES:
        if re.search(pat, d):
            return label
    if " " in word or ("-" in word and not word.startswith("-")):
        return "compound"
    if entry.get("parts") or re.search(AFFIX_TEXT, d):
        return "affix_root"
    if re.search(r"[a-zæðþ]+\s*[＋+]\s*[a-zæðþ]+", d):
        return "compound"
    if entry.get("chain") or re.search(SHIFT_PATTERN, d):
        return "semantic_shift"
    if lin not in ("unknown", "english"):
        return "borrowing"
    return "unclear"


def quality_flags(word: str, entry: dict, res: dict, status: str) -> list[str]:
    d = entry["derivation"]
    flags = []
    base = re.search(r"原形([A-Za-z\- ]+?)からの語形変化", d)
    base_form = base.group(1) if base else word
    # 「古英語」「中英語」は正当な語源表記なので除き、単独の「英語 X に由来」だけを見る
    for m in re.finditer(r"(?<![古中代期])英語 ([A-Za-z][A-Za-z\-]*?)(?=に由来|。|、|の過去|の複数)", d):
        x = m.group(1)
        if x[0].isupper() or x.lower() in JUNK_TOKENS or len(x.strip("-")) <= 2:
            flags.append("bogus_source")
        elif not families(d) and (x in (word, base_form) or (len(x) >= 5 and x[:5] in (word[:5], base_form[:5]))):
            flags.append("circular")
    if base:
        flags.append("inflected_key")
    if "→" not in d and not entry.get("chain"):
        flags.append("no_arrow")
    if res.get("confidence") == "low":
        flags.append("low_confidence")
    if status == "legacy":
        flags.append("legacy")
    return list(dict.fromkeys(flags))


def classify() -> list[dict]:
    origins, research, root_origin = load()
    rows = []
    for word, entry in origins.items():
        if not entry or not entry.get("derivation"):
            continue
        led = research.get(word, {})
        res = led.get("research") or {}
        lin, basis = lineage(word, entry, res, root_origin)
        rows.append({
            "word": word,
            "type": entry.get("type"),
            "lineage": lin,
            "lineage_basis": basis,
            "formation": formation(word, entry, lin),
            "flags": quality_flags(word, entry, res, res.get("status", "")),
            "confidence": res.get("confidence", ""),
            "derivation": entry["derivation"],
        })
    return rows


def table(counter: collections.Counter, total: int) -> list[str]:
    lines = ["| ラベル | 語数 | 割合 |", "| --- | ---: | ---: |"]
    lines += [f"| {k} | {v} | {v / total:.1%} |" for k, v in counter.most_common()]
    return lines


def cross(rows: list[dict], a: str, b: str) -> list[str]:
    cols = [k for k, _ in collections.Counter(r[b] for r in rows).most_common()]
    lines = [f"| {a} \\ {b} | " + " | ".join(cols) + " |", "| --- |" + " ---: |" * len(cols)]
    for k, _ in collections.Counter(r[a] for r in rows).most_common():
        c = collections.Counter(r[b] for r in rows if r[a] == k)
        lines.append(f"| {k} | " + " | ".join(str(c.get(col, "")) for col in cols) + " |")
    return lines


def report(rows: list[dict]) -> str:
    n = len(rows)
    flag_count = collections.Counter(f for r in rows for f in r["flags"])
    out = [
        "# 暗記カード語源の分類と品質点検",
        "",
        f"`scripts/classify_word_origins.py` によるルール分類の結果（対象 {n}語 = `data/word_origins.json` の全件）。",
        "再生成: `python scripts/classify_word_origins.py --report docs/WORD_ORIGIN_CLASSIFICATION.md`。",
        "語ごとの結果は `out/word-origin-classes.csv`（gitignore 対象）に出る。",
        "",
        "## 系統（lineage）",
        "",
        "語源をさかのぼった最も古い系統。再調査台帳の originLanguage・historicalPath と A型語根の由来を優先し、",
        "表示文と合わせて最も古い系統を採る。ゲルマン系と古典語系の要素を＋で組み合わせた語（dead＋line など）は mixed、",
        "英語内部の派生・複合しか書かれていない語は english。french_non_latin はフランス語より前の系統が書かれていない語。",
        "",
        *table(collections.Counter(r["lineage"] for r in rows), n),
        "",
        "## なりたち（formation）",
        "",
        "判定順: unclear → imitative → eponym → shortening → 句（compound）→ 接辞＋語根 → 複合 → 意味の転用 → 借用。",
        "",
        *table(collections.Counter(r["formation"] for r in rows), n),
        "",
        "## 系統 × なりたち",
        "",
        *cross(rows, "lineage", "formation"),
        "",
        "## A型・B型 × なりたち",
        "",
        *cross(rows, "type", "formation"),
        "",
        "## 品質フラグ",
        "",
        "| フラグ | 語数 | 意味 |",
        "| --- | ---: | --- |",
    ]
    meaning = {
        "bogus_source": "語源でない語（the・a など）・言語名・接頭辞だけを「英語 X に由来」と書いている",
        "circular": "見出し語自身・原形・派生語を挙げるだけで語源になっていない",
        "inflected_key": "キーが原形でない（「原形Xからの語形変化」）",
        "no_arrow": "現在の意味への「→」がない",
        "low_confidence": "再調査台帳の confidence が low",
        "legacy": "再調査台帳で未再調査",
    }
    out += [f"| {f} | {flag_count.get(f, 0)} | {m} |" for f, m in meaning.items()]
    for f in ("bogus_source", "circular", "no_arrow", "low_confidence"):
        hit = [r for r in rows if f in r["flags"]]
        if not hit:
            continue
        out += ["", f"### {f}（{len(hit)}語）", "", "| 語 | 導出文 |", "| --- | --- |"]
        out += [f"| {r['word']} | {r['derivation'].replace('|', '／')} |" for r in hit]
    unknown = [r for r in rows if r["lineage"] in ("unknown", "english")]
    out += ["", f"### 英語より前の系統が書かれていない語（english / unknown、{len(unknown)}語）", "",
            ", ".join(r["word"] for r in unknown)]
    return "\n".join(out) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--report", type=Path, default=None, help="Markdown レポートの出力先")
    args = p.parse_args()

    rows = classify()
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "word-origin-classes.json").write_text(
        json.dumps({"results": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_DIR / "word-origin-classes.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({**r, "flags": " ".join(r["flags"])} for r in rows)

    print(f"{len(rows)}語を分類 -> out/word-origin-classes.json / .csv")
    for key in ("lineage", "formation"):
        print(f"\n[{key}]")
        for k, v in collections.Counter(r[key] for r in rows).most_common():
            print(f"  {k:<18}{v:>5}")
    print("\n[flags]")
    for k, v in collections.Counter(f for r in rows for f in r["flags"]).most_common():
        print(f"  {k:<18}{v:>5}")

    if args.report:
        args.report.write_text(report(rows), encoding="utf-8")
        print(f"\nレポート -> {args.report}")


if __name__ == "__main__":
    main()
