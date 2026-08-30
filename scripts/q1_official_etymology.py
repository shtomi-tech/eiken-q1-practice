"""公式1級Q1の語源説明を、既存JSONと公式ビルダーで共有する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_IDS = ("2025-2", "2025-3", "2026-1")


# 現在の語源辞書にない語と、C型除外語はここで説明を確定する。
# 既存のA/B型は、word_origins.jsonのderivationを再利用する。
ETYMOLOGY_OVERRIDES = {
    "embezzlement": "古フランス語 embesiler（誤用する、浪費する）に由来。",
    "notoriety": "ラテン語 notorius（知られた）に由来。notus（知られた）と関係する。",
    "fortitude": "ラテン語 fortitudo（強さ、勇気）に由来。fortis（強い）と関係する。",
    "clatter": "反復する騒音を表す英語 clatter に由来。語源は擬音的とされる。",
    "acclaim": "ラテン語 acclamare（大声で呼ぶ、称賛する）に由来。",
    "bigotry": "フランス語 bigot（偽善的な信者）に由来。詳しい語形成は不確か。",
    "dogma": "ギリシャ語 dogma（意見、教義）に由来。dokein（思う）と関係する。",
    "gaunt": "古フランス語 gant（手袋）とは別系統で、詳しい語源は不確か。",
    "meager": "古フランス語 maigre（やせた、乏しい）に由来。",
    "rife": "古英語 rīfe（豊富な、広がった）に由来。",
    "virile": "ラテン語 virilis（男の、力強い）に由来。vir（男）と関係する。",
    "provincial": "ラテン語 provincia（属州）に由来する province＋-ial。",
    "tenuous": "ラテン語 tenuis（薄い、細い）に由来。",
    "collate": "ラテン語 conferre（ともに運ぶ、照合する）を経た collate。",
    "bemoan": "be-（強意）＋moan（うめく）からなる英語の語。",
    "paramount": "古フランス語 par amont（上方で、最も上に）に由来。",
    "haphazard": "hap（偶然）＋hazard（危険、運）からなる英語の複合語。",
    "pristine": "ラテン語 pristinus（以前の、原初の）に由来。",
    "heedless": "heed（注意）＋-less（〜のない）からなる英語。heedは古英語 hēdanに由来。",
    "implored": "ラテン語 implorare（泣いて願う）に由来する implore＋-ed。",
    "purged": "ラテン語 purgare（清める）に由来する purge＋-ed。",
    "bravado": "イタリア語 bravata（勇ましい言動）に由来。bravo（勇敢な）と関係する。",
    "jarring": "jar（激しく揺する、耳障りな音）＋-ing。jarの詳しい語源は不確か。",
    "tedious": "ラテン語 taediosus（うんざりさせる）に由来。taedere（うんざりする）と関係する。",
    "proclaimed": "ラテン語 proclamare（公に叫ぶ）に由来する proclaim＋-ed。",
    "quenched": "古英語 cwencan（消す）に由来する quench＋-ed。",
    "credence": "ラテン語 credere（信じる）に由来。",
    "germination": "ラテン語 germinare（芽を出す）に由来。germen（芽）と関係する。",
    "sequentially": "sequence（続くもの）＋-ial＋-ly。sequenceはラテン語 sequi（従う）に由来。",
    "slenderly": "slender（細長い）＋-ly。slenderは古フランス語系の語。",
    "entreaty": "古フランス語 entraiter（扱う、懇願する）に由来する entreat＋-y。",
    "buttressing": "buttress（支え、支える）＋-ing。buttressはフランス語 bouter（押す）と関係する。",
    "assassination": "assassin（暗殺者）＋-ation。assassinはアラビア語 ḥashshāshīnに由来。",
    "coup": "フランス語 coup（打撃、一撃）に由来。",
    "spurious": "ラテン語 spurius（私生児の、偽の）に由来。",
    "overt": "古フランス語 ouvert（開いた）に由来。ouvrir（開く）と関係する。",
    "jilted": "jilt（恋人を捨てる）＋-ed。jiltの詳しい語源は不確か。",
    "duped": "dupe（だます、だまされた人）＋-ed。dupeはフランス語 dupe（だまされやすい人）に由来。",
    "scampered": "scamper（軽快に走る）＋-ed。scamperの詳しい語源は不確か。",
    "scrawl": "scrawl（乱雑に書く、走り書き）に由来。詳しい語源は不確か。",
    "percolate": "ラテン語 percolare（通り抜けてろ過する）に由来。",
    "sully": "古フランス語 soiller（汚す）に由来。",
    "thwart": "thwart（横木、妨げる）に由来。詳しい語源は不確か。",
    "grafted": "graft（接ぎ木、結び付ける）＋-ed。graftの詳しい語源は不確か。",
    "impregnable": "ラテン語 in-（否定）＋prehendere（つかむ）に由来。",
    "synthesized": "ギリシャ語 syn-（ともに）＋tithenai（置く）に由来する synthesize＋-ed。",
    "heresy": "ギリシャ語 hairesis（選択、学派）に由来。",
    "slanted": "slant（斜めに傾く）＋-ed。slantの詳しい語源は不確か。",
    "outreach": "out（外へ）＋reach（届く）からなる英語の複合語。",
    "hindsight": "hind（後ろ）＋sight（見ること）からなる英語の複合語。",
    "appeased": "ラテン語 pacare（平和にする、なだめる）を経た appease＋-ed。",
    "peddled": "peddle（行商する、広める）＋-ed。peddleの詳しい語源は不確か。",
    "grime": "grime（すす、汚れ）に由来。詳しい語源は不確か。",
    "ridge": "古英語 hrycg（背、尾根）に由来。",
    "glaze": "中英語 glasen（ガラスをかける）に由来。glassと関係する。",
    "niche": "フランス語 niche（壁のくぼみ）に由来。",
    "posterity": "ラテン語 posterus（後の、未来の）に由来。",
    "quarantine": "イタリア語 quarantina（40日間）に由来。quaranta（40）と関係する。",
    "tempest": "ラテン語 tempestas（天候、嵐）に由来。tempus（時間、時期）と関係する。",
    "saturation": "ラテン語 saturare（満たす）に由来。satur（満ちた）と関係する。",
    "grievance": "古フランス語 grevance（苦痛、苦情）に由来。grever（重くする）と関係する。",
    "enigma": "ギリシャ語 ainigma（なぞ）に由来。ainissesthai（ほのめかす）と関係する。",
    "query": "ラテン語 quaerere（尋ねる、求める）に由来。",
    "fastidious": "ラテン語 fastidiosus（嫌悪を抱かせる、気難しい）に由来。",
    "unassuming": "un-（否定）＋assume（仮定する、引き受ける）＋-ing。",
    "brusquely": "フランス語 brusque（突然の、ぶっきらぼうな）に由来する brusque＋-ly。",
    "surreptitiously": "ラテン語 surripere（ひそかに奪う）に由来する surreptitious＋-ly。",
    "ploddingly": "plod（重い足取りで歩く）＋-ing＋-ly。plodの詳しい語源は不確か。",
    "jeopardy": "古フランス語 jeu parti（分かれたゲーム、危険な賭け）に由来。",
    "futility": "ラテン語 futilis（役に立たない、漏れる）に由来。",
    "plantations": "ラテン語 plantare（植える）に由来する plantation＋複数形 -s。",
    "sockets": "socket（くぼみ、受け口）＋複数形 -s。socketは古フランス語 soc（くびき）と関係する。",
    "percolated": "ラテン語 percolare（通り抜けてろ過する）に由来する percolate＋-ed。",
    "contorted": "ラテン語 contorquere（ねじり合わせる）に由来する contort＋-ed。",
    "tarnished": "古フランス語 ternir（曇らせる）に由来する tarnish＋-ed。",
    "appraised": "古フランス語 preisier（価値を評価する）に由来する appraise＋-ed。",
    "buttress": "フランス語 bouter（押す）に由来。壁を押して支えるもの。",
    "cajole": "フランス語 cajoler（甘言でなだめる）に由来。",
    "redeem": "ラテン語 redimere（買い戻す）に由来。re-（再び）＋emere（買う）。",
    "fortuitous": "ラテン語 fortuitus（偶然の）に由来。fors（運、偶然）と関係する。",
    "inane": "ラテン語 inanis（空の、無意味な）に由来。",
    "pampered": "pampere（甘やかす）に由来する pamper＋-ed。詳しい語源は不確か。",
    "scamper": "scamper（軽快に走る）に由来。詳しい語源は不確か。",
    "wrest": "古英語 wrǣstan（ねじる、もぎ取る）に由来。",
    "peek": "peek（ちらりとのぞく）に由来。詳しい語源は不確か。",
    "belittle": "be-（動詞化）＋little（小さい）からなる英語。",
    "rotund": "ラテン語 rotundus（丸い）に由来。rota（車輪）と関係する。",
    "malevolent": "ラテン語 male（悪く）＋volens（望む）に由来。",
    "squeamish": "squeam（吐き気を催す）＋-ish。squeamの詳しい語源は不確か。",
    "enraptured": "en-（中へ、完全に）＋rapture（恍惚）に由来する enrapture＋-ed。",
    "lanky": "lank（ひょろ長い）＋-y。lankは古英語 hlancに由来。",
    "vivacious": "ラテン語 vivax（生き生きした）に由来。vivere（生きる）と関係する。",
    "caustic": "ギリシャ語 kaustikos（焼く性質の）に由来。kaiein（焼く）と関係する。",
    "ticklish": "tickle（くすぐる）＋-ish。tickleの詳しい語源は不確か。",
    "impromptu": "ラテン語 in promptu（準備された状態でなく、その場で）に由来。",
    "extolled": "ラテン語 extollere（高く持ち上げる）に由来する extol＋-ed。",
    "bungled": "bungle（不器用に扱う、へまをする）＋-ed。詳しい語源は不確か。",
    "backlog": "back（後ろ）＋log（記録）からなる英語の複合語。",
    "upheaval": "up（上へ）＋heave（持ち上げる）からなる英語の複合語。",
    "mutter": "mutter（ぶつぶつ言う）に由来。反復音を表す語とされる。",
    "bolster": "古英語 bolster（長いクッション）に由来。支えるものの意へ。",
    "lament": "ラテン語 lamentari（嘆く）に由来。",
    "spar": "古ノルド語 sparra（梁、棒）に由来し、軽く打ち合う意へ。",
    "torments": "ラテン語 torquere（ねじる、苦しめる）に由来する torment＋複数形 -s。",
    "buskers": "busk（大道芸をする）＋-er＋複数形 -s。buskの詳しい語源は不確か。",
    "vestiges": "ラテン語 vestigium（足跡、痕跡）に由来する vestige＋複数形 -s。",
    "stooge": "stooge（手先、道化役）に由来。詳しい語源は不確か。",
    "pilgrim": "ラテン語 peregrinus（外国の、旅の）に由来。",
    "eccentric": "ギリシャ語 ek（外へ）＋kentron（中心）に由来。",
    "ornate": "ラテン語 ornare（飾る）に由来。",
    "pertinent": "ラテン語 pertinere（関係する）に由来。per-（通して）＋tenere（保つ）。",
    "dubious": "ラテン語 dubius（疑わしい）に由来。dubitare（疑う）と関係する。",
    "lucrative": "ラテン語 lucrativus（利益を生む）に由来。lucrum（利益）と関係する。",
    "obliterated": "ラテン語 oblitterare（文字を消す）に由来する obliterate＋-ed。",
    "concocted": "ラテン語 concoquere（ともに煮る）に由来する concoct＋-ed。",
    "acclimated": "フランス語 acclimater（気候に慣らす）に由来する acclimate＋-ed。",
    "queasy": "旧語 quease（吐き気を催させる）＋-y。詳しい語源は不確か。",
    "porous": "ラテン語 porosus（穴の多い）に由来。porus（小さな穴）と関係する。",
    "scruffy": "scruff（首筋、だらしない外見）＋-y。scruffの詳しい語源は不確か。",
    "ditch": "古英語 dīc（溝、堤防）に由来。",
    "gist": "古フランス語 gist（横たわっている）に由来し、話の要点の意へ。",
    "omen": "ラテン語 omen（前兆）に由来。",
    "loot": "ヒンディー語 lūt（略奪品）に由来。",
    "sentiment": "ラテン語 sentire（感じる）に由来。",
    "dearth": "古英語 dēorþ（高価さ、希少さ）に由来。",
    "ward": "古英語 weard（守る者）に由来。",
    "entailed": "古フランス語 entail（切り込んで固定する）に由来する entail＋-ed。",
    "mulled": "mull（粉砕する、熟考する）＋-ed。mullの詳しい語源は不確か。",
    "alacrity": "ラテン語 alacritas（快活さ）に由来。alacer（活発な）と関係する。",
    "prevarication": "ラテン語 praevaricari（まっすぐな道から外れる）に由来。",
    "flouted": "中英語 flouten（笛を吹く、あざける）に由来する flout＋-ed。",
    "deified": "ラテン語 deus（神）に由来する deify＋-ed。",
    "fermented": "ラテン語 fermentare（発酵させる）に由来する ferment＋-ed。",
    "coaxed": "coax（うまく言いくるめる）＋-ed。coaxの詳しい語源は不確か。",
    "boisterous": "中英語 boistous（粗野な、荒々しい）に由来。詳しい語源は不確か。",
    "suave": "ラテン語 suavis（甘い、心地よい）を経たフランス語 suave。",
    "perennial": "ラテン語 perennis（年中続く）に由来。per（通して）＋annus（年）。",
    "solvency": "ラテン語 solvere（解く、支払う）に由来。",
    "tenure": "ラテン語 tenere（保つ）に由来。",
    "censure": "ラテン語 censura（評価、批判）に由来。censere（判断する）と関係する。",
    "unruly": "un-（否定）＋rule（規則、支配）＋-yからなる英語。",
    "lackluster": "lack（欠く）＋luster（輝き）からなる英語の複合語。",
    "nebulous": "ラテン語 nebulosus（雲の多い）に由来。nebula（雲、霧）と関係する。",
    "dissipate": "ラテン語 dissipare（投げ散らす）に由来。",
    "staunch": "古フランス語 estanche（漏れない、堅固な）に由来。",
    "convergence": "ラテン語 convergere（ともに向かう）に由来。con-（ともに）＋vergere（向かう）。",
    "nostalgia": "ギリシャ語 nostos（帰郷）＋algos（苦痛）に由来。",
    "pungent": "ラテン語 pungere（刺す）に由来。",
    "pony up": "pony（小額の金）＋up（差し出して）からなる口語的な句動詞。",
    "buckle down": "buckle（留め金で固定する）＋down（下へ）からなる句動詞。",
    "foul up": "foul（汚す、失敗させる）＋up（すっかり）からなる句動詞。",
    "cast down": "cast（投げる）＋down（下へ）からなる句動詞。気分を下げること。",
    "breeze in": "breeze（そよ風、軽々と進む）＋in（中へ）からなる句動詞。",
    "branch off": "branch（枝）＋off（分かれて）からなる句動詞。",
    "crack down": "crack（強く打つ）＋down（押さえつけて）からなる句動詞。",
    "lop off": "lop（切り落とす）＋off（切り離して）からなる句動詞。",
    "dwell on": "dwell（とどまる）＋on（〜の上に）からなる句動詞。",
    "reel off": "reel（糸巻きから繰り出す）＋off（外へ）からなる句動詞。",
    "rustle up": "rustle（さらさら音を立てる、急いで集める）＋up（用意して）からなる句動詞。",
    "haul off": "haul（引っ張る）＋off（離れて）からなる句動詞。",
    "fritter away": "fritter（細かく砕く）＋away（消耗して）からなる句動詞。",
    "rip off": "rip（引き裂く）＋off（離して）からなる句動詞。",
    "sound off": "sound（音を出す）＋off（外へ）からなる句動詞。",
    "crop up": "crop（作物、突然現れるもの）＋up（上へ）からなる句動詞。",
    "nod off": "nod（うなずく）＋off（意識が離れて）からなる句動詞。",
    "pipe down": "pipe（笛、声を出す）＋down（下げて）からなる句動詞。",
    "drone on": "drone（単調な音）＋on（続けて）からなる句動詞。",
    "crank out": "crank（ハンドルを回す）＋out（外へ）からなる句動詞。",
    "tail off": "tail（尾）＋off（細く消えて）からなる句動詞。",
    "patch up": "patch（継ぎ当て）＋up（修復して）からなる句動詞。",
    "choke off": "choke（息を詰まらせる）＋off（遮断して）からなる句動詞。",
    "own up": "own（自分のものと認める）＋up（明らかにして）からなる句動詞。",
    "hush up": "hush（静かにさせる）＋up（完全に）からなる句動詞。",
    "get behind": "get（得る、移る）＋behind（後ろに）からなる句動詞。",
    "plug in": "plug（栓、差し込む）＋in（中へ）からなる句動詞。",
    "farm out": "farm（請け負わせる）＋out（外へ）からなる句動詞。",
    "sit by": "sit（座る）＋by（そばで）からなる句動詞。",
    "dive in": "dive（飛び込む）＋in（中へ）からなる句動詞。",
    "strike back": "strike（打つ）＋back（返して）からなる句動詞。",
    "pan out": "pan（砂金をより分ける皿）＋out（外へ）からなる句動詞。",
    "identify with": "identify（同一視する）＋with（〜とともに）からなる句動詞。",
    "reel in": "reel（糸を巻き取る）＋in（中へ）からなる句動詞。",
    "polish off": "polish（磨く）＋off（仕上げて）からなる句動詞。",
    "black out": "black（黒くする）＋out（外へ、完全に）からなる句動詞。",
    "turn up": "turn（回す）＋up（上へ）からなる句動詞。",
    "grow on": "grow（成長する）＋on（〜に接して）からなる句動詞。",
    "build in": "build（組み立てる）＋in（中へ）からなる句動詞。",
    "churn out": "churn（かき混ぜる）＋out（外へ）からなる句動詞。",
    "tamper with": "tamper（勝手にいじる）＋with（〜とともに）からなる句動詞。",
    "ease off": "ease（和らぐ）＋off（離れて）からなる句動詞。",
    "trump up": "trump（切り札、でっち上げる）＋up（作り上げて）からなる句動詞。",
    "branch out": "branch（枝）＋out（外へ）からなる句動詞。",
    "dole out": "dole（少しずつ分け与える）＋out（外へ）からなる句動詞。",
    "clam up": "clam（貝、口を閉ざす）＋up（閉じて）からなる句動詞。",
    "mete out": "mete（量を割り当てる）＋out（外へ）からなる句動詞。",
    "pluck up": "pluck（引き抜く）＋up（上へ）からなる句動詞。",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_map() -> dict[str, str]:
    data = _load(DATA_DIR / "lemmas.json")
    return {
        str(surface).lower(): str(lemma).lower()
        for surface, lemma in (data.get("lemmas") or {}).items()
    }


def _existing_derivations() -> dict[str, str]:
    data = _load(DATA_DIR / "word_origins.json")
    return {
        str(key).lower(): str(value.get("derivation", ""))
        for key, value in (data.get("origins") or {}).items()
        if isinstance(value, dict) and value.get("derivation")
    }


def build_etymology_by_round() -> dict[str, dict[str, str]]:
    canonical = _canonical_map()
    derivations = _existing_derivations()
    result: dict[str, dict[str, str]] = {}
    for round_id in ROUND_IDS:
        vocab = _load(DATA_DIR / f"vocab_1_{round_id}.json")
        entries: dict[str, str] = {}
        for item in [*vocab.get("words", []), *vocab.get("idioms", [])]:
            surface = str(item.get("phrase") or item.get("word") or "").strip()
            if surface in ETYMOLOGY_OVERRIDES:
                entries[surface] = ETYMOLOGY_OVERRIDES[surface]
                continue
            lemma = canonical.get(surface.lower(), surface.lower())
            if lemma in derivations:
                entries[surface] = derivations[lemma]
        result[round_id] = entries
    return result


ETYMOLOGY_BY_ROUND = build_etymology_by_round()
