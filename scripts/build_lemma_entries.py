"""Build the learning-only lemma dictionary in ``data/lemmas.json``.

The vocabulary JSON files remain the source for surfaces and meanings.  This
script only aggregates those rows into the display dictionary; it never edits
the vocabulary files or progress data.  IPA can be fetched from the same
Datamuse/CMU conversion used by ``enrich_flashcard_fields.py``.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from enrich_flashcard_fields import datamuse_fields


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LEMMA_PATH = DATA_DIR / "lemmas.json"

# These are the cases where the source rows intentionally contain different
# inflectional or lexicalized translations.  Keep all learned senses, but
# present them as dictionary-style Japanese meanings.
MEANING_OVERRIDES = {
    "accede": "同意する、就任する",
    "acclimate": "慣らす、順応させる",
    "acquiesce": "黙って従う、同意する",
    "acquire": "取得する、身につける",
    "affix": "貼り付ける、付加する",
    "alleviate": "軽減する、和らげる",
    "apex": "頂点",
    "apologize": "謝る",
    "appease": "なだめる、満足させる",
    "appraise": "評価する、査定する",
    "avert": "避ける、回避する",
    "balk": "ためらう、難色を示す",
    "beckon": "手招きする、呼び寄せる",
    "bellow": "怒鳴る",
    "bequeath": "遺贈する",
    "blank": "（記憶が）真っ白になる",
    "blanket": "毛布",
    "bluff": "はったりをかける",
    "bolt": "急に走り去る",
    "bowl": "ボウル、鉢",
    "bulge": "膨らむ、突き出る",
    "bungle": "へまをする、しくじる",
    "busker": "路上演奏者",
    "buttress": "支える、強化する；支え、補強",
    "canter": "馬が軽速歩する",
    "canvass": "戸別訪問で勧誘する、調査する",
    "capitalize": "利用する、活用する",
    "character": "登場人物、性格",
    "chuckle": "くすくす笑う",
    "clinch": "勝ち取る、確定する",
    "clobber": "めちゃくちゃに打ち負かす",
    "coax": "うまく説得する",
    "collect": "集める、落ち着かせる",
    "commute": "通勤する、（刑を）減刑する",
    "commuter": "通勤者",
    "composer": "作曲家",
    "compound": "悪化させる、複合する",
    "conciliate": "和解させる、懐柔する",
    "concoct": "でっち上げる、調合する",
    "condense": "凝縮する、短縮する",
    "conserve": "保存する、節約する",
    "consolidate": "統合する、固める",
    "contort": "ねじ曲げる、ゆがめる",
    "convene": "招集する、集まる",
    "corrode": "腐食する、蝕む",
    "cradle": "抱える、そっと支える",
    "curfew": "門限、外出禁止令",
    "danger": "危険、危険性",
    "dart": "素早く走る、突進する",
    "debar": "締め出す、資格を奪う",
    "debrief": "任務後に事情聴取する",
    "decree": "布告する、命令する",
    "deduce": "推論して導き出す",
    "defect": "離反する",
    "deflect": "そらす、かわす",
    "degenerate": "悪化する、退化する",
    "dehydrate": "脱水する",
    "deify": "神格化する",
    "delusion": "妄想、思い込み",
    "delve": "掘り下げて調べる",
    "deploy": "配置する、展開する",
    "depreciate": "価値を下げる、減価する",
    "deteriorate": "悪化する",
    "detonate": "爆発させる",
    "detract": "損なう、減じる",
    "devour": "むさぼり食う",
    "dice": "さいの目に切る",
    "dilapidate": "荒廃させる、ぼろぼろにする",
    "disappear": "消える、姿を消す",
    "disembark": "下船する、降りる",
    "dishevel": "乱す、だらしなくする",
    "disparity": "格差",
    "dispatch": "派遣する、発送する",
    "dispirit": "落胆させる",
    "dissect": "解剖する",
    "doom": "運命づける、破滅する運命にする",
    "dredge": "さらう、掘り起こす",
    "droop": "うなだれる、しおれる",
    "dupe": "だます、だまされやすい人",
    "emanate": "発する、発生する",
    "encrypt": "暗号化する",
    "enrapture": "有頂天にする、夢中にさせる",
    "enroll": "登録する、入学する",
    "entail": "伴う、必要とする",
    "enter": "入る、入力する、参加する",
    "enumerate": "列挙する",
    "envoy": "使節、特使",
    "equivocate": "言葉を濁す、曖昧に答える",
    "esteem": "尊敬、評価；尊敬する、評価する",
    "evade": "免れる、回避する",
    "evoke": "呼び起こす、想起させる",
    "exhort": "強く促す、激励する",
    "explosion": "爆発",
    "expound": "詳しく説明する",
    "expropriate": "収用する",
    "extol": "大いに褒める",
    "fabricate": "でっち上げる、捏造する",
    "facade": "外見、建物の正面",
    "faction": "派閥",
    "fare": "うまくいく、進む",
    "faze": "動じさせる",
    "ferment": "発酵させる、発酵する",
    "figure": "図、数字",
    "filter": "ろ過する、選別する",
    "flap": "ばたつく",
    "flourish": "繁栄する、生い茂る",
    "flout": "公然と無視する、軽視する",
    "fluctuate": "変動する",
    "forecast": "予報、予測する",
    "fringe": "周辺、縁",
    "fumigate": "燻蒸消毒する",
    "gallery": "美術館、展示室",
    "glimmer": "かすかな光、兆し",
    "glitch": "小さな不具合、障害",
    "graft": "接ぎ木する、移植する；汚職、贈収賄",
    "gripe": "不満、愚痴を言う",
    "grouch": "不平を言う人、不満",
    "haggle": "値段を交渉する",
    "hasten": "急ぐ、促進する",
    "hitch": "障害、支障",
    "hone": "磨く、鍛える",
    "illuminate": "照らす、明らかにする",
    "impel": "駆り立てる",
    "implement": "道具、器具；実行する",
    "implore": "懇願する",
    "incarcerate": "投獄する",
    "individual": "個人、個々の",
    "infringe": "侵害する",
    "ingredient": "材料、成分",
    "inhale": "吸い込む、吸入する",
    "insect": "昆虫",
    "installer": "設置業者",
    "invader": "侵略者、侵入者",
    "invigorate": "活力を与える、元気づける",
    "jilt": "（恋人を）振る",
    "juxtapose": "並置する",
    "ledger": "元帳、台帳",
    "liaison": "連絡、連携、協力関係；密通",
    "log": "記録する；丸太、記録",
    "maneuver": "（巧みな）動き、策略、軍事演習",
    "market": "市場、マーケット",
    "matriculate": "入学手続きをする",
    "modulate": "調整する、変調する",
    "muddle": "混乱させる、混ぜ合わせる",
    "mull": "熟考する、思案する",
    "nomination": "ノミネート、指名",
    "nullify": "無効にする",
    "obliterate": "完全に破壊する、消し去る",
    "omit": "省く、記載しない",
    "palace": "宮殿",
    "pamper": "甘やかす",
    "participant": "参加者",
    "pawn": "質に入れる；質草、手先",
    "peddle": "売り歩く、広める",
    "percolate": "浸透する、ろ過する",
    "perk": "特典、福利厚生",
    "permeate": "浸透する、行き渡る",
    "perplex": "困惑させる",
    "perspective": "見方、観点",
    "pique": "興味をそそる、立腹させる",
    "pitfall": "落とし穴、潜在的な問題",
    "placate": "なだめる",
    "plantation": "大農園",
    "pledge": "誓う、約束する",
    "plummet": "急落する",
    "poach": "密猟する、引き抜く",
    "policy": "方針、政策",
    "ponder": "熟考する",
    "pose": "ポーズをとる；（問題を）引き起こす",
    "position": "地位、役職",
    "pretext": "口実",
    "proclaim": "宣言する、公言する",
    "profess": "公言する、称する",
    "proliferate": "急増する",
    "propose": "提案する、申し込む",
    "proscribe": "禁止する",
    "provision": "条項、備え；食料、備蓄",
    "proviso": "条件、但し書き",
    "purge": "除去する、一掃する",
    "puzzle": "パズル、難問；困惑させる",
    "quench": "消す、癒やす",
    "quiver": "震える",
    "radiate": "放射する、輝く",
    "rant": "わめく、激しく不平を言う",
    "ray": "光線",
    "rebel": "反抗する、反乱を起こす",
    "reciprocate": "返礼する、応じる",
    "rectify": "訂正する、是正する",
    "reduce": "減らす、縮小する",
    "reduction": "削減、縮小",
    "regime": "政権、体制",
    "regurgitate": "吐き戻す、逆流させる",
    "relent": "折れる、態度を和らげる",
    "relish": "楽しむ、味わう",
    "renounce": "放棄する、断念する",
    "reprisal": "報復措置",
    "repulse": "反感を抱かせる、退ける",
    "requisite": "必要条件、必須品",
    "rescind": "取り消す",
    "resonate": "共鳴する、響く",
    "revel": "大いに楽しむ",
    "revert": "元に戻る",
    "rope": "ロープ、綱",
    "sanctify": "神聖化する、清める",
    "sanctuary": "聖域、保護区",
    "saturate": "浸透させる、飽和させる",
    "scamper": "走り回る、ちょこちょこ走る、走り去る",
    "scatter": "まき散らす、散らばる",
    "scowl": "しかめ面をする",
    "shear": "刈り取る、切り落とす",
    "shrug": "肩をすくめる",
    "shuffle": "混ぜる、とぼとぼ歩く",
    "slant": "傾ける、傾斜する、偏らせる",
    "slouch": "前かがみでだらしなく座る",
    "snowball": "雪だるま式に増える",
    "soar": "急上昇する、高く舞い上がる",
    "socket": "ソケット、受け口",
    "solicit": "求める、懇願する、勧誘する",
    "solidify": "固まる、強固にする",
    "spearhead": "主導する",
    "splash": "はねかける",
    "stake": "賭け金、利害；賭ける",
    "stammer": "どもる",
    "statue": "像、彫像",
    "sterilize": "殺菌する、不妊にする",
    "streak": "疾走する",
    "strut": "気取って歩く",
    "succumb": "屈する、負ける",
    "suggestion": "提案",
    "suppose": "〜だと思う、〜することになっている",
    "surmise": "推測する",
    "swill": "がぶ飲みする",
    "synthesize": "合成する、統合する",
    "tarnish": "変色させる、傷つける",
    "teeter": "危うく揺れる",
    "tether": "つなぎ留める",
    "thwart": "妨げる",
    "topple": "倒す、倒れる",
    "torment": "苦しみ、苦痛；苦しめる",
    "tout": "称賛して売り込む",
    "trample": "踏みつける、踏みにじる",
    "transfer": "異動させる、移す",
    "trickle": "少しずつ流れる",
    "trigger": "引き起こす",
    "truncate": "切り詰める、省略する",
    "twitch": "ぴくぴく動く",
    "typify": "典型的に示す",
    "venture": "冒険；事業",
    "vestige": "名残、痕跡",
    "vie": "競い合う",
    "visa": "ビザ、査証",
    "wave": "手を振る；波",
    "wedge": "差し込む、押し込む",
    "whet": "研ぐ、刺激する",
    "whine": "泣き言を言う、鼻にかかった声で鳴く",
    "waylay": "待ち伏せする",
    "wonder": "〜だろうかと思う、不思議に思う",
    "wreck": "難破させる、破壊する",
}

# 語彙データ側に混在する出題形の品詞を、その原形の辞書見出し用に
# 固定する。未掲載の語は canonical_pos() の補助推定を使うが、ここに
# 追加した値は再生成時にも失われないレビュー済みの正本とする。
POS_OVERRIDES = {
    "deify": "動詞",
    "incarcerate": "動詞",
    "liaison": "名詞",
}
POS_LABEL_ORDER = ("名詞", "動詞", "形容詞", "副詞", "前置詞", "代名詞", "接続詞", "間投詞", "限定詞")

# 全出典語義と統合後語義を人手で確認した時点のスナップショット。
# 語彙データまたは MEANING_OVERRIDES が変わると不一致になり、再確認なしでは
# data/lemmas.json を再生成できない。値は audit_lemma_entries() の
# meaningReviewDigest を確認した後にだけ更新する。
REVIEWED_MEANING_DIGEST = "690379f22d412ce608b000d98cace36b7631ee6737c4233287ef8674bcdfd5ce"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audio_slug(value: str) -> str:
    normalized = str(value or "").lower().replace("’", "'")
    normalized = re.sub(r"\b(one's|his|her|my|your|our|their|its)\b", "@poss", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    if not slug:
        raise ValueError(f"音声ファイル名を作れない原形です: {value!r}")
    return slug


def word_rows() -> dict[str, list[dict[str, Any]]]:
    data = load_json(LEMMA_PATH)
    mapping = {str(key).lower(): str(value).strip().lower() for key, value in data.get("lemmas", {}).items()}
    targets = set(mapping.values())
    grouped = {lemma: [] for lemma in sorted(targets)}
    for path in sorted(DATA_DIR.glob("vocab_*.json")):
        vocab = load_json(path)
        for item in vocab.get("words", []):
            surface = str(item.get("word", "")).strip()
            key = surface.lower()
            lemma = mapping.get(key, key if key in targets else "")
            if not lemma:
                continue
            grouped[lemma].append({
                "file": path.name,
                "surface": surface,
                "meaning": str(item.get("meaning", "")).strip(),
                "ipa": str(item.get("ipa", "")).strip(),
                "pos": str(item.get("pos", "")).strip(),
            })
    return grouped


def normalize_meaning(value: str) -> str:
    meaning = str(value or "").strip()
    meaning = re.sub(r"[（(]複数[）)]", "", meaning)
    meaning = re.sub(r"\s+", " ", meaning)
    meaning = re.sub(r"する[（(]こと[）)]", "する", meaning)
    meaning = re.sub(r"[（(]こと[）)]", "", meaning)
    meaning = meaning.replace("／", "、")
    meaning = meaning.strip(" 、")
    return meaning


def fallback_meaning(lemma: str, rows: list[dict[str, Any]]) -> str:
    if lemma in MEANING_OVERRIDES:
        return MEANING_OVERRIDES[lemma]
    meanings: list[str] = []
    for row in rows:
        meaning = normalize_meaning(row["meaning"])
        if meaning and meaning not in meanings:
            meanings.append(meaning)
    return "；".join(meanings)


def canonical_pos(lemma: str, rows: list[dict[str, Any]]) -> str:
    values: set[str] = set()
    for row in rows:
        labels = re.split(r"[・、/]", row["pos"])
        # The source data sometimes labels a past participle as an adjective.
        # Once that surface is represented by its verb lemma, expose the
        # dictionary POS instead of the inflected-surface POS.
        if row["surface"].lower() != lemma and re.search(r"(?:ed|ing)$", row["surface"].lower()):
            labels = ["動詞" if value.strip() == "形容詞" else value for value in labels]
        for value in labels:
            value = re.sub(r"\(-ing\)", "", value).strip()
            if value:
                values.add(value)
    return "・".join(label for label in POS_LABEL_ORDER if label in values)


def meaning_review_snapshot(groups: dict[str, list[dict[str, Any]]]) -> list[list[Any]]:
    snapshot: list[list[Any]] = []
    for lemma, source_rows in sorted(groups.items()):
        source_meanings = sorted({
            meaning
            for row in source_rows
            if (meaning := normalize_meaning(row["meaning"]))
        })
        merged = MEANING_OVERRIDES.get(lemma) or fallback_meaning(lemma, source_rows)
        snapshot.append([lemma, source_meanings, merged])
    return snapshot


def meaning_review_digest(groups: dict[str, list[dict[str, Any]]]) -> str:
    payload = json.dumps(
        meaning_review_snapshot(groups),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def audit_lemma_entries(data: dict[str, Any]) -> dict[str, Any]:
    groups = word_rows()
    digest = meaning_review_digest(groups)
    review_current = digest == REVIEWED_MEANING_DIGEST
    rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    meaning_owners: defaultdict[str, list[str]] = defaultdict(list)
    for lemma, source_rows in groups.items():
        merged = MEANING_OVERRIDES.get(lemma) or fallback_meaning(lemma, source_rows)
        source_meanings = []
        seen_meanings: set[str] = set()
        for row in source_rows:
            meaning = normalize_meaning(row["meaning"])
            if meaning and meaning not in seen_meanings:
                seen_meanings.add(meaning)
                source_meanings.append({
                    "file": row["file"],
                    "surface": row["surface"],
                    "meaning": meaning,
                    "disposition": "retained" if meaning == merged else "merged-as-dictionary-form",
                    "mergedAs": merged,
                })
        row_warnings: list[str] = []
        if not source_meanings:
            row_warnings.append("元データの意味が空です")
        if len(seen_meanings) > 1 and lemma not in MEANING_OVERRIDES:
            row_warnings.append("複数の語義を手動統合してください")
        if not merged:
            row_warnings.append("統合後の意味が空です")
        if not review_current:
            row_warnings.append("語義レビューのスナップショットが未承認です")
        if row_warnings:
            warnings.append({"lemma": lemma, "warnings": row_warnings})
        meaning_owners[merged].append(lemma)
        rows.append({
            "lemma": lemma,
            "surfaces": sorted({row["surface"] for row in source_rows}, key=lambda value: (value.lower(), value)),
            "sourceFiles": sorted({row["file"] for row in source_rows}),
            "sourceMeanings": source_meanings,
            "mergedMeaning": merged,
            "pos": POS_OVERRIDES.get(lemma) or canonical_pos(lemma, source_rows),
            "warnings": row_warnings,
        })
    duplicates = [
        {"meaning": meaning, "lemmas": lemmas}
        for meaning, lemmas in sorted(meaning_owners.items())
        if meaning and len(lemmas) > 1
    ]
    return {
        "schemaVersion": 2,
        "entryCount": len(rows),
        "reviewedEntryCount": len(rows) if review_current else 0,
        "meaningReviewDigest": digest,
        "expectedMeaningReviewDigest": REVIEWED_MEANING_DIGEST,
        "reviewCurrent": review_current,
        "rows": rows,
        "warnings": warnings,
        "duplicateMeanings": duplicates,
    }


def fetch_missing_ipa(entries: dict[str, dict[str, Any]], lemmas: list[str], refresh: bool = False) -> None:
    for index, lemma in enumerate(lemmas, start=1):
        if not refresh and entries.get(lemma, {}).get("ipa") and entries.get(lemma, {}).get("pos"):
            continue
        ipa, pos = datamuse_fields(lemma)
        if ipa:
            entries.setdefault(lemma, {})["ipa"] = ipa
        if pos and not entries.setdefault(lemma, {}).get("pos"):
            entries[lemma]["pos"] = pos
        if index == 1 or index % 25 == 0 or index == len(lemmas):
            print(f"IPA取得: {index}/{len(lemmas)}")


def build_entries(data: dict[str, Any], fetch_ipa: bool, refresh_fields: bool = False) -> dict[str, dict[str, Any]]:
    groups = word_rows()
    review_current = meaning_review_digest(groups) == REVIEWED_MEANING_DIGEST
    entries: dict[str, dict[str, Any]] = {}
    old_entries = data.get("entries", {}) if isinstance(data.get("entries"), dict) else {}
    for lemma, rows in groups.items():
        old = old_entries.get(lemma, {}) if isinstance(old_entries.get(lemma), dict) else {}
        surfaces = sorted({row["surface"] for row in rows}, key=lambda value: (value.lower(), value))
        entries[lemma] = {
            "meaning": MEANING_OVERRIDES.get(lemma) or old.get("meaning") or fallback_meaning(lemma, rows),
            "ipa": str(old.get("ipa") or "").strip(),
            "audio": f"assets/audio/lemma/{audio_slug(lemma)}.mp3",
            "pos": POS_OVERRIDES.get(lemma) or canonical_pos(lemma, rows),
            "surfaces": surfaces,
            "reviewed": review_current,
        }
    if fetch_ipa:
        fetch_missing_ipa(entries, sorted(entries), refresh=refresh_fields)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="候補を検証するだけでJSONを書き換えない")
    parser.add_argument("--fetch-ipa", action="store_true", help="不足する原形IPAをDatamuseから取得する")
    parser.add_argument("--refresh-fields", action="store_true", help="既存のIPA・品詞もDatamuseで更新する")
    parser.add_argument("--audit", action="store_true", help="出題形・元の意味・出典を一覧化する")
    parser.add_argument("--audit-output", type=Path, help="監査JSONの出力先。省略時は標準出力")
    args = parser.parse_args()

    data = load_json(LEMMA_PATH)
    if args.audit:
        audit = audit_lemma_entries(data)
        rendered = json.dumps(audit, ensure_ascii=False, indent=2) + "\n"
        if args.audit_output:
            args.audit_output.write_text(rendered, encoding="utf-8")
            print(f"監査出力: {args.audit_output}")
        else:
            print(rendered, end="")
        print(f"監査対象: {audit['entryCount']}原形 / 警告: {len(audit['warnings'])}件 / 意味重複: {len(audit['duplicateMeanings'])}件")
        return 0
    mapping = data.get("lemmas", {})
    if not isinstance(mapping, dict) or not mapping:
        raise SystemExit("data/lemmas.json の lemmas が空です")
    entries = build_entries(data, args.fetch_ipa or args.refresh_fields, refresh_fields=args.refresh_fields)
    groups = word_rows()
    review_digest = meaning_review_digest(groups)
    review_current = review_digest == REVIEWED_MEANING_DIGEST
    expected = sorted({str(value).strip().lower() for value in mapping.values()})
    missing = [lemma for lemma in expected if lemma not in entries]
    empty_ipa = [lemma for lemma in expected if not entries.get(lemma, {}).get("ipa")]
    empty_meaning = [lemma for lemma in expected if not entries.get(lemma, {}).get("meaning")]
    if missing or empty_ipa or empty_meaning or not review_current:
        if missing:
            print(f"辞書エントリ不足: {', '.join(missing)}")
        if empty_ipa:
            print(f"IPA不足: {', '.join(empty_ipa)}")
        if empty_meaning:
            print(f"意味不足: {', '.join(empty_meaning)}")
        if not review_current:
            print(f"語義レビュー未承認: {review_digest}")
        if not args.dry_run:
            raise SystemExit("不足項目があるため書き込みを中止しました")

    print(f"原形マップ: {len(mapping)}件 / 辞書エントリ: {len(entries)}件")
    print(f"原形スロット: {sum(len(entry['surfaces']) for entry in entries.values())}件")
    if args.dry_run:
        return 0

    data["meta"] = {
        "schemaVersion": 2,
        "note": "暗記カード・意味4択用の原形辞書。進捗キーと本番形式問題には使わない。",
        "scope": "words only (idioms は対象外)",
        "meaningReviewedEntries": len(entries),
        "meaningReviewedSourceMeanings": sum(len(row[1]) for row in meaning_review_snapshot(groups)),
        "meaningReviewDigest": review_digest,
        "posReviewedEntries": len(entries),
        "reviewCommand": "py -3 scripts/build_lemma_entries.py --audit",
    }
    data["entries"] = {lemma: entries[lemma] for lemma in expected}
    LEMMA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"更新: {LEMMA_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
