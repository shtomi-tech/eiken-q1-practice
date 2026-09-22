"""Jev点検（2026-09-22）で確認した1級文脈推測データの修正を、原稿と語彙データへ適用する。

context_1_*.json は生成物のため、正本である data/context-src/eiken1-*.json と
data/vocab_1_*.json を直す。適用後は build-q1-context-datasets.mjs で再生成する。

    python scripts/apply_jev_context_fixes.py
    node scripts/build-q1-context-datasets.mjs
    node scripts/check-context-eiken1-datasets.cjs
"""

from __future__ import annotations

import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def src_item(data: dict, target: str) -> dict:
    hits = [i for i in data["items"] if i["target"] == target]
    if len(hits) != 1:
        raise SystemExit(f"{target}: 原稿に{len(hits)}件（1件であるべき）")
    return hits[0]


def vocab_entry(data: dict, target: str) -> dict:
    hits = [
        x
        for key in ("words", "idioms")
        for x in (data.get(key) or [])
        if x.get("word") == target or x.get("phrase") == target
    ]
    if len(hits) != 1:
        raise SystemExit(f"{target}: 語彙データに{len(hits)}件（1件であるべき）")
    return hits[0]


def set_field(obj: dict, key: str, old: str, new: str) -> None:
    if obj[key] == new:  # 適用済み
        return
    if obj[key] != old:
        raise SystemExit(f"{key}: 想定と異なる値 {obj[key]!r}")
    obj[key] = new


def main() -> None:
    changes: list[str] = []

    # 1. glaze: 文中はケーキのつや出し。語彙データの語義が陶芸の「釉薬」のままで、
    #    同じ項目の exampleTranslation（糖衣）とも食い違っていた。
    p = Path("data/vocab_1_2025-3.json")
    v = load(p)
    set_field(vocab_entry(v, "glaze"), "meaning", "釉薬、光沢", "糖衣、つや出し")
    save(p, v)
    p = Path("data/context-src/eiken1-2025-3.json")
    s = load(p)
    set_field(src_item(s, "glaze"), "sense", "釉薬", "糖衣、つや出し")
    save(p, s)
    changes.append("glaze: 語義を「釉薬、光沢」から「糖衣、つや出し」へ（語彙データ・原稿）")
    # 語源データは研究台帳から生成される。台帳側の meanings と derivation を直し、
    # word_origins.json は rebuild-word-origin-dictionaries.cjs で再生成する。
    for p in sorted(Path("data").glob("word_origin_research*.json")):
        led = load(p)
        entry = (led.get("entries") or {}).get("glaze")
        if entry is None:
            continue
        # meanings は正本の台帳だけが持つ（バッチ側には無い）
        if "meanings" in entry:
            set_field(entry, "meanings", ["釉薬、光沢"], ["糖衣、つや出し"])
        d = entry["display"].get("derivation")
        if d is not None and not d.endswith("→ 糖衣、つや出し"):
            if not d.endswith("→ 釉薬、光沢"):
                raise SystemExit(f"{p}: glaze の derivation 末尾が想定と異なる")
            entry["display"]["derivation"] = d[: -len("釉薬、光沢")] + "糖衣、つや出し"
        save(p, led)
    changes.append("glaze: 語源データの derivation 末尾を新しい語義へ追随")

    # 2. extricate: 文中は extricate yourself（再帰用法）。語義が他動詞の「救い出す」のままだった。
    p = Path("data/vocab_1_mock-19.json")
    v = load(p)
    set_field(vocab_entry(v, "extricate"), "meaning", "救い出す、脱出させる", "抜け出す、脱出する")
    save(p, v)
    p = Path("data/context-src/eiken1-mock-19.json")
    s = load(p)
    set_field(src_item(s, "extricate"), "sense", "救い出す", "抜け出す")
    # 3. squared off against: ring はボクシングのリング。解説の「土俵」は誤訳。
    item = src_item(s, "squared off against")
    set_field(
        item,
        "reason",
        "第一回、土俵の中央で互いに向かい合って立ったと述べられています",
        "第1ラウンド、リングの中央で互いに向かい合って立ったと述べられています",
    )
    save(p, s)
    # 語源データの gloss は vocab meaning の部分文字列である必要があるため追随させる
    for p in sorted(Path("data").glob("word_origin_research*.json")):
        led = load(p)
        if "entries" not in led:
            continue
        entry = led["entries"].get("extricate")
        if entry is None:
            continue
        if "meanings" in entry:
            set_field(entry, "meanings", ["救い出す、脱出させる"], ["抜け出す、脱出する"])
        if "gloss" in entry["display"]:
            set_field(entry["display"], "gloss", "救い出す", "抜け出す")
        # derivation の本文は台帳ごとに異なるため、末尾の語義だけを差し替える
        d = entry["display"].get("derivation")
        if d is not None and not d.endswith("→ 抜け出す、脱出する"):
            if not d.endswith("→ 救い出す、脱出させる"):
                raise SystemExit(f"{p}: extricate の derivation 末尾が想定と異なる")
            entry["display"]["derivation"] = d[: -len("救い出す、脱出させる")] + "抜け出す、脱出する"
        save(p, led)
    changes.append("extricate: 語義を「救い出す」から「抜け出す」へ（語彙データ・原稿・語源台帳）")
    changes.append("squared off against: 解説の「土俵」を「リング」へ（原稿）")

    # 4. goofed off: sat in the van は「バンの中に座っていた」。「運転席」は原文にない。
    # 5. astounded: 「at ninety」は単位が落ちており、英文だけでは金額を読み取れない。
    p = Path("data/context-src/eiken1-mock-14.json")
    s = load(p)
    set_field(
        src_item(s, "goofed off"),
        "reason",
        "道具を置き、二人は車が戻るまで運転席にいたと述べられています",
        "道具を置き、二人は車が戻るまでバンの中に座っていたと述べられています",
    )
    item = src_item(s, "astounded")
    if "ninety million" not in json.dumps(item, ensure_ascii=False):  # 未適用のときだけ置換
        item["sentences"] = [
            sent.replace("fell at ninety.", "fell at ninety million.") for sent in item["sentences"]
        ]
        item["clues"] = [
            [text.replace("fell at ninety", "fell at ninety million"), kind]
            for text, kind in item["clues"]
        ]
        if "ninety million" not in json.dumps(item, ensure_ascii=False):
            raise SystemExit("astounded: 置換できなかった")
    save(p, s)
    changes.append("goofed off: 解説の「運転席」を「バンの中」へ（原稿）")
    changes.append("astounded: 英文の「at ninety」に単位を補う（原稿）")

    # 6. arson: 1文目が「放火ではなかった」と述べており、手がかりが語義と逆を向いていた。
    #    1文目は語彙データの example と一致させる規則のため、例文ごと差し替える。
    example = "Investigators confirmed arson within a day of the fire."
    p = Path("data/vocab_1_mock-20.json")
    v = load(p)
    entry = vocab_entry(v, "arson")
    set_field(entry, "example", "Investigators ruled out arson within a day of the fire.", example)
    set_field(
        entry,
        "exampleTranslation",
        "捜査員は火災の翌日までに放火の可能性を排除した。",
        "捜査員は火災の翌日までに放火だと断定した。",
    )
    save(p, v)

    p = Path("data/context-src/eiken1-mock-20.json")
    s = load(p)
    item = src_item(s, "arson")
    clue1 = "Cans of fuel were found by the back door"
    clue2 = "a camera recorded someone leaving through it at midnight"
    item["sentences"] = [example, f"{clue1}, and {clue2}."]
    item["clues"] = [[clue1, "detail"], [clue2, "behavior"]]
    item["reason"] = (
        "裏口のそばで燃料の缶が見つかり、深夜にそこから立ち去る人物がカメラに記録されていたと述べられています"
    )
    save(p, s)
    changes.append("arson: 手がかりが語義と逆を向いていたため例文と文脈を差し替え（語彙データ・原稿）")

    for c in changes:
        print(c)


if __name__ == "__main__":
    main()
