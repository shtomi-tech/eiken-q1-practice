"""国際医療福祉大学の基礎試験セット第2回をQ1形式のJSONへ出力する。

第1回（build_q1_iuhw_set_1_data.py）と同型。相違点は次の2つ。

1. 出典: 第2回は原本を持たない完全自作。meta.source に「AI生成（英検過去問の
   引用なし）・人手校閲」と明記する。第1回で踏襲した題材（医療人材のグローバル化／
   医師の働き方・地域偏在／社会保障財政・高齢化／図表・統計の道具語）と難易度を保つ。
2. 熟語: 第1回は58語+熟語2。第2回は「熟語で出題しそうなもの」を増やす依頼を受け、
   Q13〜Q15の3問（12件）を熟語問題にした。48語+熟語12=60語句。

収録60語句は第1回の60語と語形の揺れを含めて重複しない（references/CHECKS.md の
選定プレチェックで確認済み）。lemmas.json・全配信セットの熟語phraseとも衝突しない。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_q1_data import surfaces_match  # noqa: E402  同じ活用照合を使い回す

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "set-2"
TRANSLATION_BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")

# 見出し語句 -> (意味, 品詞, 例文, 例文訳)
WORD_LIST = {
    # Q1 医師・看護師の不足（名詞）
    "shortage": ("不足", "名詞", "A shortage of nurses forced the ward to limit new admissions.", "看護師の不足のため、その病棟は新規の入院受け入れを制限せざるを得なかった。"),
    "surplus": ("余剰、過剰", "名詞", "A surplus of applicants let the city hospital raise its hiring standards.", "応募者の余剰により、その市立病院は採用基準を引き上げることができた。"),
    "outbreak": ("発生、流行", "名詞", "The outbreak of influenza pushed the emergency department past its limit.", "インフルエンザの流行で、救急科は限界を超える負担を負った。"),
    "closure": ("閉鎖", "名詞", "The closure of the local maternity unit left families with a long drive.", "地元の産科病棟の閉鎖により、家族は長距離の移動を強いられた。"),

    # Q2 海外からの人材確保（動詞）
    "recruit": ("（人材を）募る、採用する", "動詞", "The ministry sent officials abroad to recruit dentists for understaffed towns.", "省は職員を海外へ送り、人員不足の町のために歯科医を採用させた。"),
    "dismiss": ("解雇する", "動詞", "Managers may not dismiss staff simply for joining a labor union.", "管理者は、労働組合に加入したというだけで職員を解雇してはならない。"),
    "educate": ("教育する、養成する", "動詞", "Universities educate far more pharmacists than rural clinics can hire.", "大学は、地方の診療所が雇用できる数をはるかに超える薬剤師を養成している。"),
    "sponsor": ("（就労・ビザを）支援する", "動詞", "Large hospitals often sponsor foreign doctors so they can obtain working visas.", "大規模病院はしばしば、外国人医師が就労ビザを取得できるよう支援する。"),

    # Q3 有資格者（形容詞）
    "qualified": ("有資格の", "形容詞", "Only a qualified midwife may deliver a baby without a doctor present.", "医師の立ち会いなしに出産を介助できるのは、有資格の助産師だけである。"),
    "retired": ("退職した", "形容詞", "The town relies on retired physicians who return to work part-time.", "その町は、パートタイムで復職した退職医師に頼っている。"),
    "temporary": ("一時的な、臨時の", "形容詞", "The hospital hired temporary staff to cover the winter flu season.", "その病院は冬のインフルエンザ時期をしのぐため臨時職員を雇った。"),
    "junior": ("下級の、若手の", "形容詞", "A junior nurse must consult a supervisor before changing any dosage.", "若手の看護師は、投与量を変更する前に必ず指導者に相談しなければならない。"),

    # Q4 地方の医療（形容詞）
    "rural": ("地方の、農村部の", "形容詞", "Many rural towns share a single doctor who visits twice a week.", "多くの地方の町は、週2回巡回する1人の医師を共同で頼っている。"),
    "private": ("民間の", "形容詞", "A private hospital can set its own fees within limits fixed by law.", "民間病院は、法で定められた範囲内で独自に料金を設定できる。"),
    "urban": ("都市の", "形容詞", "Large urban hospitals attract young doctors with research posts and training.", "大都市の大病院は、研究職や研修で若い医師を引きつける。"),
    "overseas": ("海外の", "形容詞", "Some graduates take overseas posts before returning to work in Japan.", "一部の卒業生は、日本で働く前に海外の職に就く。"),

    # Q5 医師の地理的偏在（名詞）
    "distribution": ("分布、配置", "名詞", "The map shows an uneven distribution of hospital beds between prefectures.", "その地図は、都道府県間の病床の不均等な分布を示している。"),
    "retention": ("定着、引き留め", "名詞", "Better childcare support has improved the retention of female surgeons.", "育児支援の充実により、女性外科医の定着が改善した。"),
    "admission": ("入院、入学許可", "名詞", "The patient's admission was delayed because no bed was free.", "空いている病床がなかったため、その患者の入院は遅れた。"),
    "shift": ("交代勤務", "名詞", "A night shift in the emergency room often lasts sixteen hours.", "救急外来の夜勤は16時間に及ぶことが多い。"),

    # Q6 長時間労働の負担（名詞）
    "burden": ("負担", "名詞", "The nursing shortage shifts an unfair burden onto the remaining staff.", "看護師不足は、残った職員に不公平な負担を押しつける。"),
    "allowance": ("手当", "名詞", "Staff on remote islands receive a monthly allowance for travel costs.", "離島勤務の職員は、交通費として毎月の手当を受け取る。"),
    "leave": ("休暇", "名詞", "Doctors rarely take their full annual leave because of short staffing.", "人手不足のため、医師が年次休暇を完全に取ることはまれである。"),
    "quota": ("割当、定員", "名詞", "Each medical school is given a small quota of places for rural applicants.", "各医学部には、地方出身の志願者向けにわずかな定員が割り当てられている。"),

    # Q7 都市部への集中（名詞）
    "concentration": ("集中", "名詞", "The concentration of clinics in the city center leaves the suburbs poorly served.", "都心部への診療所の集中により、郊外は医療が手薄になっている。"),
    "expansion": ("拡大", "名詞", "The expansion of home care has reduced the need for long hospital stays.", "在宅ケアの拡大により、長期入院の必要性が減った。"),
    "decline": ("減少", "名詞", "A steady decline in births has emptied many rural pediatric wards.", "出生数の着実な減少により、多くの地方の小児科病棟が空になった。"),
    "turnover": ("離職率", "名詞", "High turnover among night staff raises the cost of training.", "夜勤職員の高い離職率は、研修費用を押し上げる。"),

    # Q8 人口動態（形容詞）
    "aging": ("高齢化する", "形容詞", "An aging workforce means many rural doctors will retire within a decade.", "高齢化する労働力のもとでは、多くの地方の医師が10年以内に引退する。"),
    "shrinking": ("縮小する", "形容詞", "A shrinking tax base makes it harder to fund local hospitals.", "縮小する税基盤により、地域の病院への財源確保が難しくなる。"),
    "neighboring": ("近隣の", "形容詞", "Patients often cross into a neighboring city for specialist care.", "患者は専門的な治療を求めて、しばしば近隣の市へ出向く。"),
    "leading": ("主要な", "形容詞", "Diabetes is now a leading reason for regular clinic visits.", "糖尿病は今や、定期的な通院の主要な理由の一つである。"),

    # Q9 高齢者・診療科（形容詞）
    "elderly": ("高齢の", "形容詞", "An elderly man living alone may skip meals when he feels unwell.", "一人暮らしの高齢の男性は、体調が悪いと食事を抜くことがある。"),
    "chronic": ("慢性の", "形容詞", "A chronic illness such as high blood pressure needs lifelong monitoring.", "高血圧のような慢性の病気は、生涯にわたる管理を要する。"),
    "mental": ("精神の、心の", "形容詞", "Rural areas have very few clinics for mental health problems.", "地方には、心の健康問題に対応する診療所が非常に少ない。"),
    "dental": ("歯科の", "形容詞", "Regular dental care is often dropped first when money is tight.", "家計が苦しいと、定期的な歯科ケアが真っ先に後回しにされることが多い。"),

    # Q10 社会保険料（名詞）
    "contributions": ("拠出金、（社会保険の）保険料", "名詞", "Higher pension contributions leave younger workers with less take-home pay.", "年金保険料の引き上げにより、若い労働者の手取りは減る。"),
    "wages": ("賃金", "名詞", "Nurses' wages have not kept pace with the rising cost of living.", "看護師の賃金は、上昇する生活費に追いついていない。"),
    "refunds": ("払い戻し", "名詞", "Patients can claim refunds for costs above a monthly ceiling.", "患者は、月ごとの上限を超えた費用について払い戻しを請求できる。"),
    "fines": ("罰金", "名詞", "Clinics that ignore the reporting rule face small fines.", "報告規則を無視した診療所は、少額の罰金を科される。"),

    # Q11 制度の関係者（名詞）
    "recipients": ("受給者", "名詞", "Benefit recipients must report any change in household income promptly.", "給付の受給者は、世帯所得の変化を速やかに届け出なければならない。"),
    "taxpayers": ("納税者", "名詞", "Ordinary taxpayers fund most of what the health system spends each year.", "一般の納税者が、医療制度の年間支出の大半を負担している。"),
    "employers": ("雇用主", "名詞", "Large employers must offer health checks to all full-time staff.", "大規模な雇用主は、常勤の全職員に健康診断を提供しなければならない。"),
    "volunteers": ("ボランティア", "名詞", "Trained volunteers drive patients in wheelchairs to distant hospitals.", "訓練を受けたボランティアが、車いすの患者を遠方の病院まで送迎する。"),

    # Q12 保障範囲（名詞）
    "coverage": ("保障範囲", "名詞", "Dental coverage under the public plan is narrower than many patients expect.", "公的制度の歯科の保障範囲は、多くの患者が思うより狭い。"),
    "premium": ("保険料（毎月の掛け金）", "名詞", "The monthly premium rises with age and household income.", "毎月の保険料は、年齢と世帯所得に応じて上がる。"),
    "enrollment": ("加入", "名詞", "Enrollment in the national scheme is automatic for new employees.", "新入社員は、国民制度への加入が自動的に行われる。"),
    "eligibility": ("受給資格", "名詞", "Eligibility for reduced fees depends on last year's taxable income.", "料金減免の受給資格は、前年の課税所得によって決まる。"),

    # Q13 観点・条件（前置詞句の熟語）
    "in terms of": ("〜の観点では", "熟語", "In terms of cost, home care is cheaper than a long hospital stay.", "費用の観点では、在宅ケアは長期入院より安い。"),
    "regardless of": ("〜に関わらず", "熟語", "Emergency treatment is given regardless of a patient's ability to pay.", "救急の処置は、患者の支払い能力に関わらず行われる。"),
    "prior to": ("〜より前に", "熟語", "Prior to the reform, each town ran its own insurance fund.", "改革以前は、各町が独自の保険財政を運営していた。"),
    "in favor of": ("〜に賛成して", "熟語", "The council voted in favor of a new clinic near the station.", "議会は、駅近くの新しい診療所の設置に賛成の票を投じた。"),

    # Q14 文をつなぐ（副詞句の熟語）
    "as a result": ("その結果", "熟語", "Fewer young families live in the village, and as a result the clinic closes early.", "村に住む若い家族が減り、その結果、診療所は早い時間に閉まる。"),
    "for instance": ("例えば", "熟語", "Some tasks can move to nurses; blood pressure checks, for instance, need no doctor.", "一部の業務は看護師に移せる。例えば血圧測定に医師は要らない。"),
    "in particular": ("とりわけ", "熟語", "Staff shortages hit night shifts in particular, when few doctors are on call.", "人手不足はとりわけ、待機医師が少ない夜勤にこたえる。"),
    "by contrast": ("対照的に", "熟語", "City hospitals turn applicants away; rural ones, by contrast, cannot fill their posts.", "都市の病院は応募者を断る。対照的に、地方の病院は職を埋められない。"),

    # Q15 割合・因果・対処（動詞句の熟語）
    "account for": ("（割合を）占める", "熟語", "Outpatient visits account for most of the clinic's yearly income.", "外来受診が、その診療所の年間収入の大半を占める。"),
    "lead to": ("〜を引き起こす", "熟語", "Skipping regular checkups can lead to costly emergency treatment later.", "定期健診を怠ると、後で高額な救急処置につながることがある。"),
    "refer to": ("〜を参照する", "熟語", "When unsure of a dose, nurses refer to a printed chart on the wall.", "投与量が不確かなとき、看護師は壁の印刷された表を参照する。"),
    "cope with": ("〜に対処する", "熟語", "Small clinics struggle to cope with a sudden rise in flu patients.", "小さな診療所は、インフルエンザ患者の急増に対処するのに苦労する。"),
}

# 熟語カードに表示する核心イメージ。第1回と同じく particle 機構は使わず、
# term ステップ2件 + 導出結果1件の3段チェーンに統一する。
IDIOM_CORE_IMAGES = {
    "in terms of": {
        "chain": [
            {"term": "in", "gloss": "ある枠の中で"},
            {"term": "terms", "gloss": "言葉・条件・見る枠"},
            {"gloss": "ある見方の枠内で捉えて、〜の点では"},
        ]
    },
    "regardless of": {
        "chain": [
            {"term": "regardless", "gloss": "注意を向けずに"},
            {"term": "of", "gloss": "〜について"},
            {"gloss": "〜を考慮に入れずに、〜に関わらず"},
        ]
    },
    "prior to": {
        "chain": [
            {"term": "prior", "gloss": "前の"},
            {"term": "to", "gloss": "ある時点へ"},
            {"gloss": "ある時点より前に"},
        ]
    },
    "in favor of": {
        "chain": [
            {"term": "in", "gloss": "その状態の中に"},
            {"term": "favor", "gloss": "好意・支持"},
            {"gloss": "〜を支持する側に立って、〜に賛成して"},
        ]
    },
    "as a result": {
        "chain": [
            {"term": "as", "gloss": "〜として"},
            {"term": "result", "gloss": "結果・帰結"},
            {"gloss": "前の事柄の帰結として、その結果"},
        ]
    },
    "for instance": {
        "chain": [
            {"term": "for", "gloss": "〜のために挙げる"},
            {"term": "instance", "gloss": "具体例・事例"},
            {"gloss": "一例として挙げると、例えば"},
        ]
    },
    "in particular": {
        "chain": [
            {"term": "in", "gloss": "範囲を絞った中で"},
            {"term": "particular", "gloss": "個別の・特定の"},
            {"gloss": "他と区別して特に、とりわけ"},
        ]
    },
    "by contrast": {
        "chain": [
            {"term": "by", "gloss": "〜に即して"},
            {"term": "contrast", "gloss": "対比・対照"},
            {"gloss": "前の事柄と対比させると、対照的に"},
        ]
    },
    "account for": {
        "chain": [
            {"term": "account", "gloss": "計算・説明の対象"},
            {"term": "for", "gloss": "〜のぶんとして"},
            {"gloss": "全体のうちその分を占める、〜を説明する"},
        ]
    },
    "lead to": {
        "chain": [
            {"term": "lead", "gloss": "導く"},
            {"term": "to", "gloss": "ある結果へ"},
            {"gloss": "ある結果へ導く、〜を引き起こす"},
        ]
    },
    "refer to": {
        "chain": [
            {"term": "refer", "gloss": "目を向ける"},
            {"term": "to", "gloss": "対象・情報源へ"},
            {"gloss": "情報源へ目を向ける、〜を参照する"},
        ]
    },
    "cope with": {
        "chain": [
            {"term": "cope", "gloss": "渡り合う"},
            {"term": "with", "gloss": "相手・事態を伴って"},
            {"gloss": "困難な事態とうまく渡り合う、〜に対処する"},
        ]
    },
}

# choices は空所に入れたときの語形、items は WORD_LIST の見出し語句（同じ並び）。
# 第2回は全問が同一品詞の4択（mixed 0/15）で、choices と items は一致する。
QUESTIONS = [
    {
        "stem": "Remote areas of Japan face a serious ( ) of doctors, and some clinics cannot fill their open posts.",
        "choices": ["surplus", "shortage", "outbreak", "closure"],
        "items": ["surplus", "shortage", "outbreak", "closure"],
        "answerIndex": 1,
        "translation": "日本の遠隔地は深刻な医師不足に直面しており、一部の診療所は空いた職を埋められない。",
    },
    {
        "stem": "Hospital teams travel to job fairs abroad, where they interview and ( ) trained nurses on the spot.",
        "choices": ["dismiss", "educate", "recruit", "sponsor"],
        "items": ["dismiss", "educate", "recruit", "sponsor"],
        "answerIndex": 2,
        "translation": "病院のチームは海外の就職フェアへ出向き、その場で訓練を受けた看護師を面接して採用する。",
    },
    {
        "stem": "A clinic may employ only ( ) staff for tasks such as giving injections, so unlicensed helpers cannot do them.",
        "choices": ["qualified", "retired", "temporary", "junior"],
        "items": ["qualified", "retired", "temporary", "junior"],
        "answerIndex": 0,
        "translation": "診療所は注射などの業務に有資格の職員しか充てられないため、無資格の補助者はそれを行えない。",
    },
    {
        "stem": "Doctors are spread unevenly: crowded cities have more than enough, while many ( ) districts have almost none.",
        "choices": ["private", "urban", "overseas", "rural"],
        "items": ["private", "urban", "overseas", "rural"],
        "answerIndex": 3,
        "translation": "医師の配置は不均等で、過密な都市には十分すぎるほどいる一方、多くの地方の地区にはほとんどいない。",
    },
    {
        "stem": "The report focuses on where doctors choose to work: their uneven ( ) between city and countryside, not their total number.",
        "choices": ["retention", "distribution", "admission", "shift"],
        "items": ["retention", "distribution", "admission", "shift"],
        "answerIndex": 1,
        "translation": "その報告書は、医師の総数ではなく、医師がどこで働くことを選ぶか、すなわち都市と地方の間の不均等な分布（偏在）に注目している。",
    },
    {
        "stem": "Night duty places a heavy ( ) on younger doctors, who may work more than thirty hours at a stretch.",
        "choices": ["allowance", "leave", "burden", "quota"],
        "items": ["allowance", "leave", "burden", "quota"],
        "answerIndex": 2,
        "translation": "夜間勤務は若手医師に重い負担を課し、彼らは一度に30時間以上働くこともある。",
    },
    {
        "stem": "A high ( ) of specialists in a few big cities means that other regions may have no heart surgeon at all.",
        "choices": ["concentration", "expansion", "decline", "turnover"],
        "items": ["concentration", "expansion", "decline", "turnover"],
        "answerIndex": 0,
        "translation": "少数の大都市への専門医の高い集中は、他の地域には心臓外科医が一人もいないことがありうることを意味する。",
    },
    {
        "stem": "In a steadily ( ) society, people over sixty-five make up a larger share of the population each year, even where the total number of residents is not falling.",
        "choices": ["leading", "shrinking", "neighboring", "aging"],
        "items": ["leading", "shrinking", "neighboring", "aging"],
        "answerIndex": 3,
        "translation": "着実に高齢化する社会では、住民の総数が減っていない地域でも、65歳を超える人々が人口に占める割合が年々大きくなる。",
    },
    {
        "stem": "Home visits mostly serve ( ) people well into their nineties who are too frail to travel to a clinic.",
        "choices": ["dental", "elderly", "mental", "chronic"],
        "items": ["dental", "elderly", "mental", "chronic"],
        "answerIndex": 1,
        "translation": "訪問診療の主な対象は、通院するには虚弱すぎる、90代も深まった高齢の人々である。",
    },
    {
        "stem": "Employees and companies each pay monthly ( ) that fund pensions and medical insurance.",
        "choices": ["wages", "refunds", "contributions", "fines"],
        "items": ["wages", "refunds", "contributions", "fines"],
        "answerIndex": 2,
        "translation": "従業員と会社は、年金と医療保険を支える毎月の保険料をそれぞれ負担する。",
    },
    {
        "stem": "Most ( ) of public assistance are households of pensioners or people who cannot work because of illness.",
        "choices": ["recipients", "taxpayers", "employers", "volunteers"],
        "items": ["recipients", "taxpayers", "employers", "volunteers"],
        "answerIndex": 0,
        "translation": "公的扶助の受給者の多くは、年金生活者の世帯や、病気のために働けない人々である。",
    },
    {
        "stem": "Basic insurance ( ) includes hospital care and prescription medicine, but not cosmetic surgery.",
        "choices": ["premium", "enrollment", "eligibility", "coverage"],
        "items": ["premium", "enrollment", "eligibility", "coverage"],
        "answerIndex": 3,
        "translation": "基本的な保険の保障範囲には入院診療や処方薬が含まれるが、美容整形は含まれない。",
    },
    {
        "stem": "( ) staff numbers per patient, small island clinics score far worse than mainland hospitals on this one measure.",
        "choices": ["Regardless of", "In terms of", "Prior to", "In favor of"],
        "items": ["regardless of", "in terms of", "prior to", "in favor of"],
        "answerIndex": 1,
        "translation": "患者一人あたりの職員数というこの一つの指標では、離島の小さな診療所は本土の病院よりはるかに劣る。",
    },
    {
        "stem": "Rural birth numbers keep falling, and ( ) the last maternity ward in the valley will close next spring.",
        "choices": ["for instance", "in particular", "as a result", "by contrast"],
        "items": ["for instance", "in particular", "as a result", "by contrast"],
        "answerIndex": 2,
        "translation": "地方の出生数は減り続けており、その結果、その谷で最後に残った産科病棟も来春に閉鎖される。",
    },
    {
        "stem": "Long-term care and medicine together ( ) nearly half of all the money the region spends on welfare.",
        "choices": ["account for", "lead to", "refer to", "cope with"],
        "items": ["account for", "lead to", "refer to", "cope with"],
        "answerIndex": 0,
        "translation": "長期介護と医薬品で合わせて、その地域が福祉に支出する金額のほぼ半分を占める。",
    },
]


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text))


def occurrences(text: str, needle: str) -> int:
    return len(re.findall(rf"\b{re.escape(needle)}\b", text, flags=re.IGNORECASE))


def write_json(path: Path, value: dict) -> None:
    newline = "\r\n" if path.exists() and b"\r\n" in path.read_bytes() else "\n"
    content = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if newline == "\r\n":
        content = content.replace("\n", "\r\n")
    path.write_bytes(content.encode("utf-8"))


def build() -> tuple[dict, dict]:
    if len(WORD_LIST) != 60:
        raise ValueError(f"見出し語句は60件である必要があります: {len(WORD_LIST)}")
    if len(QUESTIONS) != 15:
        raise ValueError("IUHWセットは15問である必要があります")
    idiom_keys = {item for item in WORD_LIST if " " in item}
    if idiom_keys != set(IDIOM_CORE_IMAGES):
        raise ValueError(f"熟語の核心イメージ定義が一致しません: {sorted(idiom_keys ^ set(IDIOM_CORE_IMAGES))}")
    if len(idiom_keys) != 12:
        raise ValueError(f"第2回の熟語は12件の想定です: {len(idiom_keys)}")

    used = [item for question in QUESTIONS for item in question["items"]]
    if len(used) != len(set(used)):
        raise ValueError("同じ見出し語を2回使っています")
    if sorted(used) != sorted(WORD_LIST):
        missing = sorted(set(WORD_LIST) - set(used))
        extra = sorted(set(used) - set(WORD_LIST))
        raise ValueError(f"見出し語の使用が一致しません: 未使用={missing} / 一覧外={extra}")

    answer_positions = [0, 0, 0, 0]
    mixed = 0
    for question in QUESTIONS:
        choices, items = question["choices"], question["items"]
        if len(choices) != 4 or len(items) != 4 or question["answerIndex"] not in range(4):
            raise ValueError(f"4択または正答位置が不正です: {question['stem']}")
        answer_positions[question["answerIndex"]] += 1
        if str(question["stem"]).count("( )") != 1:
            raise ValueError(f"設問文の空所が不正です: {question['stem']}")
        if not question.get("translation"):
            raise ValueError(f"設問文訳がありません: {question['stem']}")
        if TRANSLATION_BLANK_RE.search(str(question["translation"])):
            raise ValueError(f"設問文訳に空所記号があります: {question['stem']}")
        for choice, item in zip(choices, items):
            if not surfaces_match(choice, item):
                raise ValueError(f"選択肢と見出し語が対応していません: {choice} / {item}")
            if occurrences(question["stem"], choice):
                raise ValueError(f"選択肢が設問文に出ています: {choice}")
        details = [WORD_LIST[item] for item in items]
        if len({detail[0] for detail in details}) != 4:
            raise ValueError(f"同一設問内で意味が重複しています: {items}")
        answer_pos = details[question["answerIndex"]][1]
        if len({detail[1] for detail in details}) != 1:
            mixed += 1
            same_pos = sum(detail[1] == answer_pos for detail in details)
            same_form = len({choice[-2:] for choice in choices}) == 1
            if same_pos < 2 and not same_form:
                raise ValueError(f"選択肢の品詞も語形も揃っていません: {items}")
        for item, (_, _, example, _) in zip(items, details):
            if word_count(example) < 8:
                raise ValueError(f"例文が8語未満です: {item}")
            if occurrences(example, item) != 1:
                raise ValueError(f"例文に見出し語が1回ありません: {item}")

    if any(count < 3 or count > 5 for count in answer_positions):
        raise ValueError(f"正答位置の分散が3〜5から外れています: {answer_positions}")

    meta = {
        "grade": "国際医療福祉大学",
        "round": ROUND_ID,
        "section": "基礎試験 英語（選択肢文の語彙）",
        "source": "AI生成（英検過去問の引用なし）・人手校閲。第1回の題材傾向に沿った学習用自作文",
        "counts": {"questions": 15, "words": len(WORD_LIST) - len(idiom_keys), "idioms": len(idiom_keys), "total": len(WORD_LIST)},
    }
    question_data = {
        "meta": meta,
        "questions": [
            {
                "q": index,
                "stem": question["stem"],
                "choices": question["choices"],
                "answerIndex": question["answerIndex"],
                "translation": question["translation"],
            }
            for index, question in enumerate(QUESTIONS, start=1)
        ],
    }
    words = []
    idioms = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, item in enumerate(question["items"]):
            meaning, pos, example, example_translation = WORD_LIST[item]
            if item in idiom_keys:
                idioms.append({
                    "q": q,
                    "is_answer": index == question["answerIndex"],
                    "type": "idiom",
                    "phrase": item,
                    "pos": pos,
                    "coreImage": IDIOM_CORE_IMAGES[item],
                    "meaning": meaning,
                    "example": example,
                    "exampleTranslation": example_translation,
                })
            else:
                words.append({
                    "q": q,
                    "word": item,
                    "is_answer": index == question["answerIndex"],
                    "pos": pos,
                    "meaning": meaning,
                    "example": example,
                    "exampleTranslation": example_translation,
                })
    print(f"品詞混在の設問: {mixed}/15 / 正答位置分散: {answer_positions}")
    return {"meta": meta, "words": words, "idioms": idioms}, question_data


def main() -> int:
    vocab, questions = build()
    write_json(DATA_DIR / f"vocab_iuhw_{ROUND_ID}.json", vocab)
    write_json(DATA_DIR / f"questions_iuhw_{ROUND_ID}.json", questions)
    counts = vocab["meta"]["counts"]
    print(f"生成: {len(questions['questions'])}問 / {counts['total']}語句（単語{counts['words']}・熟語{counts['idioms']}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
