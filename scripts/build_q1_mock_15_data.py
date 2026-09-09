"""英検1級 模試第15回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-15 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-15"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "News of the discovery set off a media (   ) that lasted for almost a fortnight.",
        "choices": ["frenzy", "subordination", "groove", "protrusion"],
        "answerIndex": 0,
        "translation": "その発見の報せは、2週間近く続く報道の熱狂を引き起こした。",
    },
    {
        "stem": "The clinic treats minor (   ) so that the hospital can concentrate on serious cases.",
        "choices": ["semblance", "ailments", "figments", "hindrances"],
        "answerIndex": 1,
        "translation": "その診療所は軽い病気を扱い、病院が重症例に集中できるようにしている。",
    },
    {
        "stem": "The commander's (   ) led him to ignore the warnings of every officer around him.",
        "choices": ["amenity", "hubris", "profanity", "deposition"],
        "answerIndex": 1,
        "translation": "指揮官の傲慢さは、周囲のすべての将校の警告を無視させることになった。",
    },
    {
        "stem": "He built an odd (   ) of wire and rubber bands that actually watered the plants.",
        "choices": ["inundation", "anonymity", "contraption", "conjunction"],
        "answerIndex": 2,
        "translation": "彼は針金と輪ゴムで妙な仕掛けを作ったが、それは実際に植物に水をやってくれた。",
    },
    {
        "stem": "Under the auction rules, the (   ) is on the seller to prove that the painting is genuine.",
        "choices": ["precept", "humiliation", "libel", "onus"],
        "answerIndex": 3,
        "translation": "競売の規則では、その絵が本物であることを証明する責任は売り手にある。",
    },
    {
        "stem": "Her (   ) to the small provincial orchestra never wavered, even during the long years without pay.",
        "choices": ["dowry", "fidelity", "conglomeration", "inhalation"],
        "answerIndex": 1,
        "translation": "地方の小さな楽団への彼女の忠実さは、無給の長い年月の間でさえ揺らぐことがなかった。",
    },
    {
        "stem": "He has a strong (   ) to crowds and books his travel for the quietest hours.",
        "choices": ["aversion", "augmentation", "configuration", "perjury"],
        "answerIndex": 0,
        "translation": "彼は人混みを強く嫌い、最も静かな時間帯に移動の予約をする。",
    },
    {
        "stem": "A short public apology did very little to (   ) the anger of the residents near the plant.",
        "choices": ["dawdle", "drool", "assuage", "debunk"],
        "answerIndex": 2,
        "translation": "短い公式の謝罪は、工場近くの住民の怒りを和らげる役にはほとんど立たなかった。",
    },
    {
        "stem": "The mule would not (   ) an inch, however hard the driver pulled the rope.",
        "choices": ["conjure", "budge", "impeach", "repudiate"],
        "answerIndex": 1,
        "translation": "御者がどれほど強く綱を引いても、そのラバは1インチも動こうとしなかった。",
    },
    {
        "stem": "Cheap imported cotton gradually (   ) the coarse wool that was produced in the northern valleys.",
        "choices": ["plagiarized", "engulfed", "articulated", "supplanted"],
        "answerIndex": 3,
        "translation": "安価な輸入綿花は、北部の谷で生産される粗い羊毛に徐々に取って代わった。",
    },
    {
        "stem": "Surgeons had to (   ) the badly damaged nerve before they could begin to repair the artery.",
        "choices": ["sever", "lampoon", "extrapolate", "pollinate"],
        "answerIndex": 0,
        "translation": "外科医たちは動脈の修復に取りかかる前に、ひどく損傷した神経を切断しなければならなかった。",
    },
    {
        "stem": "The chief accountant (   ) more than a million pounds from the charity over eleven quiet years.",
        "choices": ["marshaled", "litigated", "collocated", "embezzled"],
        "answerIndex": 3,
        "translation": "その主任会計士は、目立たない11年の間に慈善団体から100万ポンド以上を横領した。",
    },
    {
        "stem": "The engineers eventually (   ) the tidal current to generate electric power for the whole island.",
        "choices": ["enlightened", "harnessed", "demurred", "shoved"],
        "answerIndex": 1,
        "translation": "技術者たちはついに潮の流れを利用して島全体の電力を生み出した。",
    },
    {
        "stem": "The reforms (   ) a level of trust that had been absent for a generation.",
        "choices": ["prowled", "levitated", "sprouted", "engendered"],
        "answerIndex": 3,
        "translation": "その改革は、一世代にわたり失われていた水準の信頼を生み出した。",
    },
    {
        "stem": "The study examined whether (   ) messages in television advertising really affect what ordinary shoppers buy.",
        "choices": ["subliminal", "flamboyant", "abrasive", "unwitting"],
        "answerIndex": 0,
        "translation": "その研究は、テレビ広告の中の潜在意識に働きかけるメッセージが一般の買い物客の購買に本当に影響するかどうかを調べた。",
    },
    {
        "stem": "His reply was so (   ) that the visitor assumed she had offended him somehow.",
        "choices": ["anemic", "deceased", "brusque", "garrulous"],
        "answerIndex": 2,
        "translation": "彼の返事があまりにぶっきらぼうだったので、訪問者は自分が何か彼の気分を害したのだと思った。",
    },
    {
        "stem": "The soup was barely (   ), but the climbers were far too hungry to complain.",
        "choices": ["sordid", "plenary", "truculent", "palatable"],
        "answerIndex": 3,
        "translation": "そのスープはかろうじて口にできる程度だったが、登山者たちは空腹すぎて文句を言わなかった。",
    },
    {
        "stem": "A (   ) glance at the accounts was enough to show that something was wrong.",
        "choices": ["cursory", "abortive", "inscrutable", "illicit"],
        "answerIndex": 0,
        "translation": "帳簿をざっと一瞥しただけで、何かがおかしいと分かった。",
    },
    {
        "stem": "The whole argument became (   ) once the original signed documents were finally produced in court.",
        "choices": ["demure", "gallant", "untenable", "lethargic"],
        "answerIndex": 2,
        "translation": "署名入りの原本が法廷についに提出されると、その主張全体が成り立たなくなった。",
    },
    {
        "stem": "The new coating makes the fabric (   ) to water without trapping any heat inside the jacket.",
        "choices": ["delirious", "impervious", "prolific", "carnivorous"],
        "answerIndex": 1,
        "translation": "その新しい加工は、上着の内部に熱をこもらせることなく生地を水を通さないものにする。",
    },
    {
        "stem": "The number of registered users grew (   ) during the first eighteen months after the launch.",
        "choices": ["dismally", "exponentially", "scrupulously", "altruistically"],
        "answerIndex": 1,
        "translation": "登録利用者数は開始後の最初の18か月で指数関数的に増加した。",
    },
    {
        "stem": "The charity had to (   ) its reserves to keep the shelter open through the winter.",
        "choices": ["dip into", "cast off", "head off", "dumb down"],
        "answerIndex": 0,
        "translation": "その慈善団体は冬の間ずっと避難所を開け続けるため、蓄えに手をつけなければならなかった。",
    },
    {
        "stem": "For weeks, older colleagues (   ) the young apprentice until he finally agreed to enter the national competition.",
        "choices": ["let up on", "stood in for", "egged on", "got down to"],
        "answerIndex": 2,
        "translation": "何週間もの間、年上の同僚たちは、その若い見習いが全国大会に出ると承知するまでけしかけ続けた。",
    },
    {
        "stem": "She (   ) of the meeting when her carefully prepared proposal was dismissed without any discussion.",
        "choices": ["loaded up", "pushed back", "piled into", "stormed out"],
        "answerIndex": 3,
        "translation": "入念に準備した提案が何の議論もなく退けられると、彼女は激怒して会議から出て行った。",
    },
    {
        "stem": "The campaign gradually (   ) after its two main organizers moved to other cities for work.",
        "choices": ["glanced off", "tipped off", "fizzled out", "plowed through"],
        "answerIndex": 2,
        "translation": "その運動は、中心となる2人の主催者が仕事で別の都市へ移った後、次第に尻すぼみに終わった。",
    },
]


DETAILS = {
    # Q1
    "frenzy": ("熱狂、逆上", "名詞", "The bargain sale produced a frenzy at the door of the store.", "その安売りは店の入り口で熱狂的な騒ぎを生んだ。"),
    "subordination": ("従属、下位に置くこと", "名詞", "The general resented the subordination of his forces to a foreign command.", "その将軍は自軍が外国の指揮下に置かれることに憤慨した。"),
    "groove": ("溝、決まりきったやり方", "名詞", "A shallow groove in the stone shows where the rope once ran.", "石の浅い溝が、かつて綱が通っていた場所を示している。"),
    "protrusion": ("突起、隆起", "名詞", "A small protrusion on the casing marks the position of the sensor.", "筐体の小さな突起がセンサーの位置を示している。"),
    # Q2
    "semblance": ("外見、うわべ", "名詞", "Order returned, or at least a semblance of it, by Thursday.", "木曜日までに秩序が、少なくともその外見だけは戻った。"),
    "ailments": ("(軽い)病気、不調", "名詞", "The pharmacy stocks remedies for the ailments people treat at home.", "その薬局は人々が家庭で手当てする不調のための薬を置いている。"),
    "figments": ("作り事、想像の産物", "名詞", "The lawyer dismissed the reports as figments of a nervous imagination.", "弁護士はそれらの報告を神経質な想像の産物として退けた。"),
    "hindrances": ("妨げ、障害", "名詞", "Poor signage and narrow doors were the main hindrances for wheelchair users.", "分かりにくい表示と狭い扉が車椅子利用者にとっての主な障害だった。"),
    # Q3
    "amenity": ("快適な設備、便利さ", "名詞", "The only amenity in the village is a small covered bus stop.", "その村にある唯一の便利な設備は、小さな屋根付きのバス停だけである。"),
    "hubris": ("傲慢、思い上がり", "名詞", "The collapse of the fund was a textbook case of hubris.", "そのファンドの破綻は、傲慢さの教科書的な事例だった。"),
    "profanity": ("冒とく的な言葉、悪態", "名詞", "The recording was released with the profanity removed.", "その録音は悪態の部分を削除して公開された。"),
    "deposition": ("宣誓証言、堆積", "名詞", "The lawyer read the deposition aloud to the jury.", "弁護士は陪審に向けてその宣誓証言を読み上げた。"),
    # Q4
    "inundation": ("氾濫、殺到", "名詞", "The inundation of the lower fields happens almost every March.", "低地の畑の氾濫はほぼ毎年3月に起こる。"),
    "anonymity": ("匿名性", "名詞", "The witness spoke on condition of complete anonymity.", "その証人は完全な匿名を条件に話した。"),
    "contraption": ("珍妙な仕掛け、変な装置", "名詞", "A wooden contraption in the corner turned out to be a loom.", "隅にあった木製の珍妙な装置は、結局は織機だった。"),
    "conjunction": ("結合、同時に起こること", "名詞", "The festival is held in conjunction with the harvest market.", "その祭りは収穫市と合わせて開催される。"),
    # Q5
    "precept": ("教訓、行動規範", "名詞", "The school was founded on a single precept about honest work.", "その学校は正直な労働についての1つの教訓の上に創設された。"),
    "humiliation": ("屈辱", "名詞", "The public humiliation of the defeat stayed with the team for years.", "その敗北の公然たる屈辱は何年もチームに残った。"),
    "libel": ("文書による名誉毀損", "名詞", "The magazine settled the libel case out of court.", "その雑誌は名誉毀損訴訟を法廷外で和解した。"),
    "onus": ("責任、負担", "名詞", "The onus of proof rests with the party making the accusation.", "立証の責任は告発する側にある。"),
    # Q6
    "dowry": ("持参金", "名詞", "The custom of providing a dowry disappeared in the region after the war.", "持参金を用意する習慣は、戦後その地域から消えた。"),
    "fidelity": ("忠実さ、忠誠", "名詞", "The translation is praised for its fidelity to the original rhythm.", "その翻訳は原文のリズムへの忠実さで称賛されている。"),
    "conglomeration": ("寄せ集め、集合体", "名詞", "The site is a conglomeration of workshops built over two centuries.", "その敷地は2世紀にわたって建てられた工房の寄せ集めである。"),
    "inhalation": ("吸入", "名詞", "Treatment for smoke inhalation began at the scene.", "煙の吸入に対する処置は現場で始められた。"),
    # Q7
    "aversion": ("嫌悪、反感", "名詞", "His aversion to publicity kept him out of every photograph.", "彼の人目に触れることへの嫌悪は、彼をあらゆる写真から遠ざけた。"),
    "augmentation": ("増加、増強", "名詞", "The augmentation of the choir required rebuilding the entire gallery.", "聖歌隊の増員は回廊全体の作り直しを必要とした。"),
    "configuration": ("配置、構成", "名詞", "A different configuration of the seats would fit twelve more people.", "座席の配置を変えれば12人多く収容できるだろう。"),
    "perjury": ("偽証", "名詞", "He was later charged with perjury for the evidence he gave.", "彼は自分がした証言について後に偽証罪で告発された。"),
    # Q8
    "dawdle": ("のろのろする、ぐずぐずする", "動詞", "Children tend to dawdle on the way home when the weather is fine.", "子どもは天気がよいと帰り道でのろのろしがちである。"),
    "drool": ("よだれを垂らす", "動詞", "The medication can make patients drool during the first week.", "その薬は最初の週の間、患者によだれを垂らさせることがある。"),
    "assuage": ("和らげる、なだめる", "動詞", "Nothing the manager said could assuage the crowd outside the gate.", "支配人が何を言っても、門の外の群衆をなだめることはできなかった。"),
    "debunk": ("(誤りを)暴く、通説を覆す", "動詞", "The book sets out to debunk several myths about medieval diet.", "その本は中世の食事に関するいくつかの俗説を覆そうとしている。"),
    # Q9
    "conjure": ("呼び起こす、手品で出す", "動詞", "The scent of pine can conjure memories of childhood winters.", "松の香りは子ども時代の冬の記憶を呼び起こすことがある。"),
    "budge": ("わずかに動く、譲歩する", "動詞", "The window would not budge until we removed six layers of paint.", "6層の塗料を落とすまで、その窓はびくとも動かなかった。"),
    "impeach": ("弾劾する、告発する", "動詞", "The assembly voted to impeach the governor in a single afternoon.", "議会は1回の午後の審議で知事を弾劾することを可決した。"),
    "repudiate": ("拒絶する、否認する", "動詞", "The scientist was forced to repudiate a paper he had co-authored.", "その科学者は自ら共著した論文を否認せざるを得なくなった。"),
    # Q10
    "plagiarized": ("盗用した、剽窃した", "動詞", "A committee found that the candidate had plagiarized two chapters.", "委員会はその候補者が2章を盗用していたと認定した。"),
    "engulfed": ("飲み込んだ、包み込んだ", "動詞", "Flames engulfed the roof before the first engine arrived.", "最初の消防車が到着する前に炎が屋根を飲み込んだ。"),
    "articulated": ("明確に述べた", "動詞", "She articulated the objection more clearly than anyone else at the meeting.", "彼女は会議の誰よりも明確にその異議を述べた。"),
    "supplanted": ("取って代わった", "動詞", "Digital maps have almost entirely supplanted the printed atlas.", "デジタル地図は印刷された地図帳にほぼ完全に取って代わった。"),
    # Q11
    "sever": ("切断する、断ち切る", "動詞", "The company decided to sever its remaining ties with the supplier.", "その会社は納入業者との残る関係を断ち切ることを決めた。"),
    "lampoon": ("風刺する、こきおろす", "動詞", "The cartoonist chose to lampoon all three candidates equally.", "その風刺画家は3人の候補者を等しくこきおろすことを選んだ。"),
    "extrapolate": ("外挿する、推定する", "動詞", "It is risky to extrapolate national trends from a single district.", "1つの地区から全国的な傾向を推定するのは危うい。"),
    "pollinate": ("受粉させる", "動詞", "Growers rent hives to pollinate the almond orchards each spring.", "栽培者は毎春、アーモンド園を受粉させるために巣箱を借りる。"),
    # Q12
    "marshaled": ("整列させた、結集した", "動詞", "The organizers marshaled two thousand volunteers in under an hour.", "主催者たちは1時間足らずで2000人のボランティアを整然と配置した。"),
    "litigated": ("訴訟で争った", "動詞", "The boundary was litigated for a decade before the families settled.", "その境界は両家が和解するまで10年間訴訟で争われた。"),
    "collocated": ("(語が)共に用いられた、隣接配置した", "動詞", "The two verbs are rarely collocated with the same nouns.", "その2つの動詞が同じ名詞と共に用いられることはめったにない。"),
    "embezzled": ("横領した", "動詞", "A trusted treasurer embezzled funds from the club for years.", "信頼されていた会計係が何年もクラブの資金を横領していた。"),
    # Q13
    "enlightened": ("啓発した、教え導いた", "動詞", "A single lecture enlightened him about the causes of the famine.", "1回の講義が飢饉の原因について彼を啓発した。"),
    "harnessed": ("(自然の力を)利用した、活用した", "動詞", "Early mills harnessed the river to grind grain for the village.", "初期の水車小屋は村のために川の力を利用して穀物をひいた。"),
    "demurred": ("難色を示した、異議を唱えた", "動詞", "The treasurer demurred when asked to approve the extra payment.", "追加の支払いを承認するよう求められると、会計係は難色を示した。"),
    "shoved": ("押しのけた、乱暴に押した", "動詞", "Someone shoved the door open and shouted into the corridor.", "誰かがドアを乱暴に押し開け、廊下に向かって叫んだ。"),
    # Q14
    "prowled": ("(獲物を求めて)うろついた", "動詞", "A fox prowled the allotments long after midnight.", "キツネが真夜中を過ぎてからずっと市民農園をうろついていた。"),
    "levitated": ("空中に浮かせた、浮上した", "動詞", "The magician appeared to have levitated the table by a few centimeters.", "手品師はテーブルを数センチ浮かせたように見えた。"),
    "sprouted": ("芽を出した", "動詞", "The beans sprouted three days after the first warm rain.", "その豆は最初の暖かい雨の3日後に芽を出した。"),
    "engendered": ("生じさせた、引き起こした", "動詞", "The open accounts engendered a level of confidence nobody expected.", "公開された会計は、誰も予想しなかった水準の信頼を生み出した。"),
    # Q15
    "subliminal": ("潜在意識に働きかける", "形容詞", "Regulators banned subliminal images from television advertising in 1958.", "規制当局は1958年にテレビ広告での潜在意識に働きかける画像を禁止した。"),
    "flamboyant": ("派手な、けばけばしい", "形容詞", "His flamboyant coat was recognizable from the far end of the platform.", "彼の派手なコートはホームの反対の端からでも見分けがついた。"),
    "abrasive": ("(態度が)とげとげしい、研磨性の", "形容詞", "Her abrasive manner cost her the support of the junior staff.", "彼女のとげとげしい態度は若手職員の支持を失わせた。"),
    "unwitting": ("知らないでした、無意識の", "形容詞", "He became an unwitting participant in a scheme he never understood.", "彼は自分の理解しない計画に知らぬまま加わることになった。"),
    # Q16
    "anemic": ("貧血の、活気のない", "形容詞", "Growth remained anemic despite three separate stimulus packages.", "3度にわたる景気刺激策にもかかわらず、成長は低調なままだった。"),
    "deceased": ("死亡した、故人の", "形容詞", "The estate of the deceased owner was divided among four cousins.", "亡くなった所有者の遺産は4人のいとこの間で分けられた。"),
    "brusque": ("ぶっきらぼうな、無愛想な", "形容詞", "The porter's brusque reply discouraged any further questions.", "そのポーターのぶっきらぼうな返事は、それ以上の質問を思いとどまらせた。"),
    "garrulous": ("おしゃべりな、冗長な", "形容詞", "A garrulous neighbor delayed him by twenty minutes at the gate.", "おしゃべりな隣人が門のところで彼を20分足止めした。"),
    # Q17
    "sordid": ("汚らわしい、卑劣な", "形容詞", "The biography does not conceal the sordid details of the affair.", "その伝記はその一件の汚らわしい詳細を隠してはいない。"),
    "plenary": ("全員出席の、完全な", "形容詞", "The plenary session opened with reports from all six committees.", "本会議は6つの委員会すべてからの報告で始まった。"),
    "truculent": ("けんか腰の、好戦的な", "形容詞", "A truculent passenger was removed from the aircraft before departure.", "けんか腰の乗客が出発前に機内から降ろされた。"),
    "palatable": ("口に合う、受け入れやすい", "形容詞", "The compromise was more palatable to the members than another strike.", "その妥協案は、さらなるストライキよりも会員には受け入れやすかった。"),
    # Q18
    "cursory": ("ざっとした、大ざっぱな", "形容詞", "A cursory inspection missed the crack in the rear axle.", "ざっとした点検では後車軸の亀裂を見落としてしまった。"),
    "abortive": ("失敗に終わった、不首尾の", "形容詞", "After two abortive attempts, the crew waited for calmer weather.", "2度の失敗の後、乗組員はより穏やかな天候を待った。"),
    "inscrutable": ("計り知れない、なぞめいた", "形容詞", "His inscrutable expression gave the negotiators nothing to work with.", "彼のなぞめいた表情は、交渉担当者に手がかりを何も与えなかった。"),
    "illicit": ("違法の、不正な", "形容詞", "Customs seized an illicit shipment of protected timber.", "税関は保護対象の木材の違法な積み荷を差し押さえた。"),
    # Q19
    "demure": ("控えめな、しとやかな", "形容詞", "She gave a demure smile and said nothing about the award.", "彼女は控えめにほほえみ、その賞について何も言わなかった。"),
    "gallant": ("勇敢な、礼儀正しい", "形容詞", "A gallant rescue by two fishermen saved everyone on board.", "2人の漁師による勇敢な救助が乗っていた全員を救った。"),
    "untenable": ("擁護できない、成り立たない", "形容詞", "His position became untenable once the emails were published.", "電子メールが公表されると、彼の立場は擁護できないものになった。"),
    "lethargic": ("無気力な、けだるい", "形容詞", "The heat left the whole class lethargic by early afternoon.", "暑さは午後の早い時間までにクラス全員を無気力にさせた。"),
    # Q20
    "delirious": ("うわごとを言う、逆上した", "形容詞", "The patient was delirious for two days before the fever broke.", "その患者は熱が下がるまでの2日間、うわごとを言う状態だった。"),
    "impervious": ("(水などを)通さない、動じない", "形容詞", "The clay layer is impervious and keeps the pond from draining.", "その粘土層は水を通さず、池の水が抜けるのを防いでいる。"),
    "prolific": ("多作の、繁殖力の強い", "形容詞", "He was a prolific correspondent who wrote four letters a day.", "彼は1日に4通の手紙を書く多作な文通家だった。"),
    "carnivorous": ("肉食の", "形容詞", "The island has no large carnivorous mammals at all.", "その島には大型の肉食哺乳類はまったくいない。"),
    # Q21
    "dismally": ("惨めに、ひどく", "副詞", "The scheme failed dismally in its first year of operation.", "その計画は運用初年度に惨めな失敗に終わった。"),
    "exponentially": ("指数関数的に、急激に", "副詞", "Storage costs have fallen exponentially since the early 2000s.", "記憶装置の費用は2000年代初頭以降、指数関数的に下がってきた。"),
    "scrupulously": ("几帳面に、良心的に", "副詞", "The accounts were scrupulously kept for over forty years.", "その帳簿は40年以上にわたり几帳面につけられていた。"),
    "altruistically": ("利他的に", "副詞", "Some species appear to behave altruistically toward unrelated individuals.", "一部の種は血縁のない個体に対しても利他的に振る舞うように見える。"),
    # Q22
    "dip into": ("(蓄えに)手をつける、拾い読みする", "句動詞", "They had to dip into their savings to replace the roof.", "彼らは屋根を葺き替えるために貯金に手をつけなければならなかった。"),
    "cast off": ("(綱を)解く、捨て去る", "句動詞", "The crew prepared to cast off as soon as the tide turned.", "乗組員は潮が変わり次第もやい綱を解く用意をした。"),
    "head off": ("未然に防ぐ、進路をふさぐ", "句動詞", "Quick talks helped head off a strike at the depot.", "迅速な話し合いが車庫でのストライキを未然に防ぐ助けとなった。"),
    "dumb down": ("(内容を)平易にしすぎる", "句動詞", "Producers refused to dumb down the series for a wider audience.", "制作者たちは、視聴者層を広げるために番組を安易にすることを拒んだ。"),
    # Q23
    "let up on": ("(~への圧力を)緩める", "句動詞", "The coach refused to let up on the squad before the final.", "監督は決勝前に選手団への厳しさを緩めることを拒んだ。"),
    "stood in for": ("(~の)代役を務めた", "句動詞", "A junior lecturer stood in for the professor for three weeks.", "若手の講師が3週間その教授の代役を務めた。"),
    "egged on": ("けしかけた、あおった", "句動詞", "His friends egged on the argument instead of calming it.", "彼の友人たちは言い争いを鎮めるどころか、あおり立てた。"),
    "got down to": ("(仕事に)本気で取りかかった", "句動詞", "After an hour of talk they finally got down to the accounts.", "1時間話した後、彼らはようやく帳簿に本気で取りかかった。"),
    # Q24
    "loaded up": ("いっぱいに積み込んだ", "句動詞", "The volunteers loaded up two vans with donated blankets.", "ボランティアたちは寄付された毛布を2台のバンにいっぱいに積み込んだ。"),
    "pushed back": ("反発した、押し返した", "句動詞", "Several departments pushed back against the shortened deadline.", "いくつかの部署は短縮された期限に反発した。"),
    "piled into": ("(乗り物に)どっと乗り込んだ", "句動詞", "Twelve of us piled into a car built for five.", "5人乗りの車に私たち12人がどっと乗り込んだ。"),
    "stormed out": ("怒って飛び出した", "句動詞", "He stormed out before the vote was even counted.", "彼は票が数えられる前に怒って出て行った。"),
    # Q25
    "glanced off": ("かすめてそれた", "句動詞", "The ball glanced off the post and went out for a corner.", "ボールはポストをかすめてそれ、コーナーキックになった。"),
    "tipped off": ("(こっそり)知らせた、密告した", "句動詞", "Someone tipped off the inspectors about the unrecorded shifts.", "誰かが記録されていない勤務について検査官に密告した。"),
    "fizzled out": ("尻すぼみに終わった", "句動詞", "The protest fizzled out after the first week of rain.", "その抗議は雨の続いた最初の1週間の後、尻すぼみに終わった。"),
    "plowed through": ("(困難を)押し進んだ、一気に片づけた", "句動詞", "She plowed through the remaining applications before lunch.", "彼女は昼食前に残りの応募書類を一気に片づけた。"),
}


CORE_IMAGES = {
    "dip into": {
        "chain": [
            {"term": "dip", "gloss": "ちょっと浸す"},
            {"term": "into", "gloss": "中へ入れて"},
            {"gloss": "蓄えの中へ手を少しだけ入れて"},
            {"gloss": "貯えに手をつける"},
        ],
        "particle": "into",
    },
    "cast off": {
        "chain": [
            {"term": "cast", "gloss": "投げる、放つ"},
            {"term": "off", "gloss": "つなぎを切り離して"},
            {"gloss": "船と岸をつなぐ綱を投げ離して"},
            {"gloss": "もやいを解く、捨て去る"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "head off": {
        "chain": [
            {"term": "head", "gloss": "先頭へ向かう"},
            {"term": "off", "gloss": "進路から外れさせて"},
            {"gloss": "先回りして相手の進路から外れさせて"},
            {"gloss": "未然に防ぐ"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "dumb down": {
        "chain": [
            {"term": "dumb", "gloss": "知的でなくする"},
            {"term": "down", "gloss": "水準を下げて"},
            {"gloss": "中身の水準を落として分かりやすくして"},
            {"gloss": "内容を安易にする"},
        ],
        "particle": "down",
        "particleSense": "lower",
    },
    "let up on": {
        "chain": [
            {"term": "let", "gloss": "手を放す"},
            {"term": "up", "gloss": "握った力を放して"},
            {"gloss": "かけ続けていた圧力から手を放して"},
            {"gloss": "~への厳しさを緩める"},
        ],
        "particle": "up",
        "particleSense": "release",
    },
    "stood in for": {
        "chain": [
            {"term": "stand", "gloss": "立つ"},
            {"term": "in", "gloss": "その位置の中へ入って"},
            {"gloss": "空いた持ち場の中へ入って立って"},
            {"gloss": "~の代役を務める"},
        ],
        "particle": "in",
    },
    "egged on": {
        "chain": [
            {"term": "egg", "gloss": "せき立てる"},
            {"term": "on", "gloss": "さらに先へ続けさせて"},
            {"gloss": "横から突いて先へ進み続けさせて"},
            {"gloss": "けしかける"},
        ],
        "particle": "on",
        "particleSense": "continue",
    },
    "got down to": {
        "chain": [
            {"term": "get", "gloss": "その状態に至る"},
            {"term": "down", "gloss": "腰を据えて"},
            {"gloss": "机に向かって腰を据えた状態に至って"},
            {"gloss": "本気で取りかかる"},
        ],
        "particle": "down",
        "particleSense": "settle",
    },
    "loaded up": {
        "chain": [
            {"term": "load", "gloss": "積む"},
            {"term": "up", "gloss": "いっぱいになるまで"},
            {"gloss": "空きがなくなるまで積み込んで"},
            {"gloss": "いっぱいに積み込む"},
        ],
        "particle": "up",
        "particleSense": "complete",
    },
    "pushed back": {
        "chain": [
            {"term": "push", "gloss": "押す"},
            {"term": "back", "gloss": "来た方向へ押し返して"},
            {"gloss": "迫ってくる要求を来た方向へ押し返して"},
            {"gloss": "反発する"},
        ],
        "particle": "back",
    },
    "piled into": {
        "chain": [
            {"term": "pile", "gloss": "積み重なる"},
            {"term": "into", "gloss": "中へ入り込んで"},
            {"gloss": "大勢が重なるように中へ入り込んで"},
            {"gloss": "どっと乗り込む"},
        ],
        "particle": "into",
    },
    "stormed out": {
        "chain": [
            {"term": "storm", "gloss": "嵐のように荒れる"},
            {"term": "out", "gloss": "外へ出て"},
            {"gloss": "怒りを表したまま勢いよく外へ出て"},
            {"gloss": "怒って飛び出す"},
        ],
        "particle": "out",
        "particleSense": "social",
    },
    "glanced off": {
        "chain": [
            {"term": "glance", "gloss": "かすめる"},
            {"term": "off", "gloss": "触れて離れて"},
            {"gloss": "表面に軽く触れてすぐ離れて"},
            {"gloss": "かすめてそれる"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "tipped off": {
        "chain": [
            {"term": "tip", "gloss": "そっと伝える"},
            {"term": "off", "gloss": "内側から外へ出して"},
            {"gloss": "内輪の情報をそっと外へ出して"},
            {"gloss": "密告する、こっそり知らせる"},
        ],
        "particle": "off",
        "particleSense": "express",
    },
    "fizzled out": {
        "chain": [
            {"term": "fizzle", "gloss": "しゅーっと音を立てて消える"},
            {"term": "out", "gloss": "勢いを出し切って"},
            {"gloss": "泡が音を立てて勢いを出し切って"},
            {"gloss": "尻すぼみに終わる"},
        ],
        "particle": "out",
        "particleSense": "exhaust",
    },
    "plowed through": {
        "chain": [
            {"term": "plow", "gloss": "すきで土を掘り進む"},
            {"term": "through", "gloss": "端から端まで通して"},
            {"gloss": "抵抗を押し分けて端まで進み通して"},
            {"gloss": "困難を押して一気に片づける"},
        ],
    },
}



def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def surface_variants(value: str) -> set[str]:
    base = " ".join(str(value or "").lower().split())
    variants = {base}
    if base.endswith("ies") and len(base) > 3:
        variants.add(base[:-3] + "y")
    if base.endswith("ied") and len(base) > 3:
        variants.add(base[:-3] + "y")
    if base.endswith("es") and len(base) > 3:
        variants.add(base[:-2])
    if base.endswith("s") and len(base) > 2:
        variants.add(base[:-1])
    if base.endswith("ed") and len(base) > 3:
        stem = base[:-2]
        variants.add(stem)
        if len(stem) > 1 and stem[-1] == stem[-2]:
            variants.add(stem[:-1])
        if stem.endswith("i"):
            variants.add(stem[:-1] + "y")
        variants.add(stem + "e")
    if base.endswith("ing") and len(base) > 4:
        stem = base[:-3]
        variants.add(stem)
        if len(stem) > 1 and stem[-1] == stem[-2]:
            variants.add(stem[:-1])
        variants.add(stem + "e")
    return variants


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 25:
        raise ValueError("模試第15回は25問である必要があります")

    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != len(set(choices)):
        raise ValueError("選択肢に重複があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    extra = sorted(set(DETAILS) - set(choices))
    if extra:
        raise ValueError(f"使われていない語句情報があります: {extra}")

    for question in QUESTIONS:
        if question["stem"].count("(   )") != 1:
            raise ValueError(f"空所は1か所である必要があります: {question['stem'][:40]}")
        stem_words = {word.lower() for word in WORD_RE.findall(question["stem"])}
        for choice in question["choices"]:
            # 熟語の不変化詞・前置詞は機能語なので、本文に出ていても手掛かりにならない。
            for part in choice.split():
                if part.lower() in PARTICLES:
                    continue
                if part.lower() in stem_words:
                    raise ValueError(f"選択肢の語が設問文に出ています: {choice} / {part}")
        for mark in ("(", "（"):
            if mark in question["translation"]:
                raise ValueError(f"和訳に空所記号が残っています: {question['translation'][:30]}")
        meanings = [DETAILS[choice][0] for choice in question["choices"]]
        if len(meanings) != len(set(meanings)):
            raise ValueError(f"同一設問内で意味が重複しています: {question['choices']}")
        parts_of_speech = {DETAILS[choice][1] for choice in question["choices"]}
        if len(parts_of_speech) != 1:
            raise ValueError(f"同一設問内で品詞が揃っていません: {question['choices']}")

    answer_positions = [question["answerIndex"] for question in QUESTIONS]
    for index in range(4):
        if answer_positions.count(index) < 4:
            raise ValueError(f"正答位置が偏っています: {[answer_positions.count(i) for i in range(4)]}")

    meta = {
        "grade": "英検1級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-15 割り当てに従う",
        "counts": {"words": 84, "idioms": 16, "total": 100},
    }
    question_data = {
        "meta": meta,
        "questions": [
            {"q": index, **question} for index, question in enumerate(QUESTIONS, start=1)
        ],
    }

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    words = []
    idioms = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            meaning, pos, example, example_translation = DETAILS[choice]
            if len(WORD_RE.findall(example)) < 8:
                raise ValueError(f"{choice}の例文が8語未満です")
            pattern = r"\b" + re.escape(choice) + r"\b"
            if len(re.findall(pattern, example, flags=re.IGNORECASE)) != 1:
                raise ValueError(f"{choice}の例文に見出し語句が1回ありません")
            example_key = re.sub(pattern, "( )", example, count=1, flags=re.IGNORECASE)
            example_key = " ".join(example_key.lower().split())
            if example_key in seen_examples:
                raise ValueError(f"例文の骨格が重複しています: {choice} / {seen_examples[example_key]}")
            seen_examples[example_key] = choice
            for variant in surface_variants(choice):
                if variant in seen_surfaces:
                    raise ValueError(f"同一セット内で語形が重複しています: {choice} / {seen_surfaces[variant]}")
                seen_surfaces[variant] = choice

            item = {
                "q": q,
                "is_answer": index == question["answerIndex"],
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
                "pos": pos,
            }
            if " " in choice:
                if choice not in CORE_IMAGES:
                    raise ValueError(f"核心イメージがありません: {choice}")
                item["phrase"] = choice
                item["coreImage"] = CORE_IMAGES[choice]
                idioms.append(item)
            else:
                item["word"] = choice
                words.append(item)

    if (len(words), len(idioms)) != (84, 16):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idioms)}")
    return {"meta": meta, "words": words, "idioms": idioms}, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / f"vocab_1_{ROUND_ID}.json", vocab)
    write_json(DATA_DIR / f"questions_1_{ROUND_ID}.json", questions)
    print(f"{ROUND_ID}: 25 questions / 100 items (84 words, 16 idioms)")


if __name__ == "__main__":
    main()
