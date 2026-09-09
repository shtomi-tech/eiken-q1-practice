"""英検1級 模試第20回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-20 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-20"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "Passing military plans to a foreign government was, at that time, punishable as (   ).",
        "choices": ["treason", "pilgrimage", "acolyte", "grudge"],
        "answerIndex": 0,
        "translation": "軍事計画を外国政府に渡すことは、当時は反逆罪として処罰の対象だった。",
    },
    {
        "stem": "Investors should read the (   ) very carefully before committing any of their money to the fund.",
        "choices": ["remuneration", "prospectus", "electorate", "glint"],
        "answerIndex": 1,
        "translation": "投資家はそのファンドに自分の資金を投じる前に、目論見書を非常に注意深く読むべきである。",
    },
    {
        "stem": "He was laid up for a fortnight with a nasty (   ) of influenza in February.",
        "choices": ["consternation", "summation", "bout", "calamity"],
        "answerIndex": 2,
        "translation": "彼は2月にひどいインフルエンザにかかり、2週間寝込んでいた。",
    },
    {
        "stem": "The gardener cut each (   ) at an angle before putting the flowers in water.",
        "choices": ["patronage", "projectile", "concoction", "stalk"],
        "answerIndex": 3,
        "translation": "庭師は花を水に生ける前に、それぞれの茎を斜めに切った。",
    },
    {
        "stem": "A faint (   ) crossed his face when the auditor first mentioned the missing receipts.",
        "choices": ["smirk", "contingency", "stalwart", "dissertation"],
        "answerIndex": 0,
        "translation": "監査人が紛失した領収書に初めて触れたとき、彼の顔にかすかな薄笑いがよぎった。",
    },
    {
        "stem": "The whole argument rests on the (   ) that the two samples came from the same tree.",
        "choices": ["interlude", "premise", "repertoire", "reparation"],
        "answerIndex": 1,
        "translation": "その議論全体は、2つの試料が同じ木から採られたという前提の上に成り立っている。",
    },
    {
        "stem": "The final (   ) on the tractor is due at the end of the harvest season.",
        "choices": ["arson", "penchant", "installment", "gratuity"],
        "answerIndex": 2,
        "translation": "そのトラクターの最後の分割払いは、収穫期の終わりに支払期日を迎える。",
    },
    {
        "stem": "The illness may not (   ) itself for another twenty years after a person's initial exposure.",
        "choices": ["jeopardize", "guzzle", "taunt", "manifest"],
        "answerIndex": 3,
        "translation": "その病気は最初のばく露の後さらに20年間、症状として現れないこともある。",
    },
    {
        "stem": "Rescuers had to (   ) the entire hillside in the dark before they found the second climber.",
        "choices": ["scour", "slaughter", "maroon", "inaugurate"],
        "answerIndex": 0,
        "translation": "救助隊は2人目の登山者を見つけるまでに、暗闇の中でその斜面全体をくまなく捜索しなければならなかった。",
    },
    {
        "stem": "Two men tried to (   ) elderly customers out of their life savings over the telephone.",
        "choices": ["stratify", "swindle", "appall", "instill"],
        "answerIndex": 1,
        "translation": "2人の男が電話で高齢の客から老後の蓄えをだまし取ろうとした。",
    },
    {
        "stem": "Younger players almost always (   ) the habits of the captain whom they most admire.",
        "choices": ["encapsulate", "adjudicate", "emulate", "lob"],
        "answerIndex": 2,
        "translation": "若い選手はほとんどの場合、自分が最も尊敬する主将の習慣を見習う。",
    },
    {
        "stem": "The inspector chose to (   ) the driver rather than report him to the licensing office.",
        "choices": ["encumber", "advocate", "inscribe", "reprimand"],
        "answerIndex": 3,
        "translation": "検査官は運転手を免許当局へ通報するのではなく、口頭で叱責することを選んだ。",
    },
    {
        "stem": "Officials tried to (   ) the leak, describing it merely as a routine maintenance issue.",
        "choices": ["downplay", "embolden", "siphon", "incinerate"],
        "answerIndex": 0,
        "translation": "当局はその漏出を単なる通常の保守上の問題だと述べて、軽く見せようとした。",
    },
    {
        "stem": "The archbishop was the first to publicly (   ) the practice as a form of slavery.",
        "choices": ["entice", "denounce", "fetter", "demonize"],
        "answerIndex": 1,
        "translation": "大司教はその慣行を奴隷制の一形態として公然と非難した最初の人物だった。",
    },
    {
        "stem": "There was a (   ) sense of relief in the hall when the announcement finally came.",
        "choices": ["inept", "unkempt", "palpable", "indignant"],
        "answerIndex": 2,
        "translation": "ついに発表があったとき、会場にははっきりと感じ取れる安堵が広がった。",
    },
    {
        "stem": "He remained (   ) throughout the whole of the party and left without speaking to anyone at all.",
        "choices": ["laconic", "obsequious", "quarrelsome", "aloof"],
        "answerIndex": 3,
        "translation": "彼はパーティーの間ずっとよそよそしく、誰ともまったく話さずに帰っていった。",
    },
    {
        "stem": "The climb is (   ) rather than technical, and stamina matters far more than skill.",
        "choices": ["arduous", "sultry", "vociferous", "altruistic"],
        "answerIndex": 0,
        "translation": "その登攀は技術的というより骨の折れるもので、技能よりも持久力がはるかに物を言う。",
    },
    {
        "stem": "Critics quickly suspected an (   ) motive that the donor was taking great care to conceal.",
        "choices": ["scrumptious", "ulterior", "poised", "comatose"],
        "answerIndex": 1,
        "translation": "批評家たちはすぐに、寄付者が懸命に隠そうとしている下心があるのではないかと疑った。",
    },
    {
        "stem": "The witness gave an (   ) answer that seemed to avoid the question almost entirely.",
        "choices": ["assiduous", "strident", "oblique", "extenuating"],
        "answerIndex": 2,
        "translation": "その証人は質問をほとんど完全に避けているように見える遠回しな答えをした。",
    },
    {
        "stem": "The company's influence in the region has been (   ) since it lost the government contract.",
        "choices": ["impermeable", "generic", "succulent", "waning"],
        "answerIndex": 3,
        "translation": "その地域におけるその会社の影響力は、政府との契約を失って以来衰えつつある。",
    },
    {
        "stem": "He lifted the cracked bowl (   ), taking great care not to widen the fracture any further.",
        "choices": ["gingerly", "sparingly", "aptly", "doggedly"],
        "answerIndex": 0,
        "translation": "彼はひび割れをこれ以上広げないよう細心の注意を払いながら、その鉢を恐る恐る持ち上げた。",
    },
    {
        "stem": "The foreman (   ) two of the apprentices in front of the whole workshop that morning.",
        "choices": ["boxed up", "chewed out", "dispensed with", "rode on"],
        "answerIndex": 1,
        "translation": "その日の朝、現場監督は作業場全員の前で見習いのうち2人をどなりつけた。",
    },
    {
        "stem": "It would be fairer to (   ) the tenants about how long the repairs will take.",
        "choices": ["shoot for", "bulk up", "level with", "lean on"],
        "answerIndex": 2,
        "translation": "修理にどれくらいかかるのかを借家人に正直に打ち明けるほうが公平だろう。",
    },
    {
        "stem": "Junior staff who (   ) the manager were promoted ahead of far better and more experienced workers.",
        "choices": ["came in for", "leapt out at", "bore down on", "sucked up to"],
        "answerIndex": 3,
        "translation": "部長にごまをすった若手職員が、はるかに優秀で経験豊富な労働者を差し置いて昇進した。",
    },
    {
        "stem": "The second boat steadily (   ) the leaders over the final three kilometers of the race.",
        "choices": ["gained on", "weeded out", "beefed up", "lashed out"],
        "answerIndex": 0,
        "translation": "2番目のボートはレース最後の3キロで着実に先頭集団に迫った。",
    },
]


DETAILS = {
    # Q1
    "treason": ("反逆罪、国家反逆", "名詞", "The charge of treason carried the death penalty until 1965.", "反逆罪の罪状は1965年まで死刑を伴っていた。"),
    "pilgrimage": ("巡礼、聖地への旅", "名詞", "Thousands make the pilgrimage on foot every August.", "毎年8月、何千人もが徒歩でその巡礼を行う。"),
    "acolyte": ("従者、助手", "名詞", "The professor arrived with an acolyte carrying both briefcases.", "その教授は2つの書類鞄を抱えた助手を伴って到着した。"),
    "grudge": ("恨み、遺恨", "名詞", "He bore a grudge against the referee for the rest of his career.", "彼は現役の残りの期間ずっとその審判に恨みを抱いていた。"),
    # Q2
    "prospectus": ("目論見書、要項", "名詞", "The prospectus lists every fee the investor will eventually pay.", "その目論見書は投資家が最終的に払うすべての手数料を列挙している。"),
    "remuneration": ("報酬、給与", "名詞", "Remuneration for the post is fixed by the national scale.", "その職の報酬は全国の給与表で定められている。"),
    "electorate": ("有権者全体、選挙民", "名詞", "The electorate has grown by ninety thousand since the last census.", "有権者は前回の国勢調査以来9万人増えた。"),
    "glint": ("きらめき、輝き", "名詞", "A glint of metal in the grass turned out to be a coin.", "草むらの金属のきらめきは、結局は硬貨だった。"),
    # Q3
    "consternation": ("驚愕、狼狽", "名詞", "The announcement caused consternation among the assembled staff.", "その発表は集まった職員の間に狼狽を引き起こした。"),
    "summation": ("要約、総括", "名詞", "The judge's summation lasted almost the whole afternoon.", "裁判官の総括は午後のほぼ全部を費やした。"),
    "bout": ("(病気などの)発作、ひと勝負", "名詞", "A bout of pneumonia kept him out of the water for months.", "肺炎にかかったため、彼は何か月も水から遠ざかっていた。"),
    "calamity": ("大災害、惨事", "名詞", "The flood of 1953 remains the worst calamity in the region's history.", "1953年の洪水はその地域の歴史で最悪の惨事であり続けている。"),
    # Q4
    "patronage": ("後援、支援", "名詞", "The theater survived for decades on the patronage of two families.", "その劇場は2つの一族の後援で何十年も存続した。"),
    "projectile": ("発射物、飛来物", "名詞", "A projectile from the machine shattered the workshop window.", "その機械から飛んだ物体が作業場の窓を割った。"),
    "concoction": ("調合物、でっち上げ", "名詞", "His grandmother gave him a concoction of honey and lemon.", "祖母は彼に蜂蜜とレモンを混ぜたものを与えた。"),
    "stalk": ("茎、柄", "名詞", "Each stalk carries three or four heavy seed heads.", "1本の茎には3つか4つの重い穂が付いている。"),
    # Q5
    "smirk": ("薄ら笑い、にやにや笑い", "名詞", "The smirk on his face annoyed everyone at the table.", "彼の顔の薄ら笑いは食卓の全員をいらだたせた。"),
    "contingency": ("不測の事態、偶発事件", "名詞", "Every contingency is covered by a separate section of the plan.", "あらゆる不測の事態が、計画の別々の節で扱われている。"),
    "stalwart": ("忠実な支持者、屈強な人", "名詞", "A stalwart of the club, she has attended every meeting since 1994.", "クラブの中心的存在である彼女は1994年以来すべての集会に出席している。"),
    "dissertation": ("学位論文", "名詞", "Her dissertation on coastal dialects took five years to complete.", "沿岸方言についての彼女の学位論文は完成に5年を要した。"),
    # Q6
    "interlude": ("幕間、合間", "名詞", "There is a short musical interlude between the two acts.", "2つの幕の間に短い音楽の幕間がある。"),
    "premise": ("前提", "名詞", "The plan rests on the premise that fuel prices will stay low.", "その計画は燃料価格が低いままだという前提に基づいている。"),
    "repertoire": ("レパートリー、演目", "名詞", "The quartet added four modern pieces to its repertoire.", "そのカルテットは演目に現代曲を4曲加えた。"),
    "reparation": ("賠償、償い", "名詞", "The treaty required reparation for damage done to the harbor.", "その条約は港湾に与えた損害への賠償を求めた。"),
    # Q7
    "arson": ("放火", "名詞", "Investigators ruled out arson within a day of the fire.", "捜査員は火災の翌日までに放火の可能性を排除した。"),
    "penchant": ("強い好み、傾向", "名詞", "He has a penchant for buying maps he will never use.", "彼には決して使わない地図を買い込む癖がある。"),
    "installment": ("分割払いの1回分、一部", "名詞", "The first installment is due thirty days after delivery.", "第1回の分割払いは納品の30日後が期日である。"),
    "gratuity": ("心づけ、チップ", "名詞", "A modest gratuity is included in the printed price.", "ささやかな心づけが表示価格に含まれている。"),
    # Q8
    "manifest": ("(症状などが)現れる、明示する", "動詞", "The fault will manifest only under a heavy electrical load.", "その不具合は重い電気負荷の下でのみ現れる。"),
    "jeopardize": ("危険にさらす", "動詞", "One careless message could jeopardize the entire negotiation.", "1通の不用意なメッセージが交渉全体を危険にさらしかねない。"),
    "guzzle": ("がぶ飲みする、大量消費する", "動詞", "The old van will guzzle fuel on any long journey.", "その古いバンは長距離ではどうしても燃料を大量に食う。"),
    "taunt": ("あざける、なじる", "動詞", "Supporters continued to taunt the visiting goalkeeper all evening.", "サポーターは一晩中、遠征チームのゴールキーパーをあざけり続けた。"),
    # Q9
    "slaughter": ("虐殺する、食肉処理する", "動詞", "It is illegal to slaughter animals outside a licensed facility.", "認可施設以外で動物を食肉処理することは違法である。"),
    "maroon": ("置き去りにする", "動詞", "A broken bridge can maroon the village for several days.", "橋が壊れると、その村は数日間孤立することがある。"),
    "scour": ("くまなく捜す、磨く", "動詞", "Volunteers helped scour the woodland for the missing dog.", "ボランティアが行方不明の犬を捜して森をくまなく調べるのを手伝った。"),
    "inaugurate": ("開始する、就任させる", "動詞", "The mayor will inaugurate the new line on Saturday morning.", "市長は土曜の朝に新路線の開業式を行う予定である。"),
    # Q10
    "stratify": ("層に分ける、階層化する", "動詞", "Researchers stratify the sample by age before analysing it.", "研究者は分析の前に標本を年齢で層に分ける。"),
    "appall": ("ぞっとさせる、あきれさせる", "動詞", "The condition of the kennels will appall most visitors.", "その犬舎の状態はたいていの訪問者をぞっとさせるだろう。"),
    "swindle": ("だまし取る、詐取する", "動詞", "They tried to swindle the widow out of her late husband's pension.", "彼らはその未亡人から亡夫の年金をだまし取ろうとした。"),
    "instill": ("(考えを)徐々に教え込む", "動詞", "Good coaches instill habits that outlast any single season.", "よい指導者は1シーズンを超えて残る習慣を教え込む。"),
    # Q11
    "encapsulate": ("要約する、包み込む", "動詞", "One photograph can encapsulate an entire decade of change.", "1枚の写真が10年分の変化を凝縮して示すことがある。"),
    "adjudicate": ("裁定する、判定する", "動詞", "An independent panel will adjudicate the remaining claims.", "独立した審査団が残りの請求を裁定する。"),
    "emulate": ("見習う、まねる", "動詞", "Small towns tried to emulate the success of the coastal festival.", "小さな町々はその沿岸の祭りの成功にならおうとした。"),
    "lob": ("ゆるやかに投げる", "動詞", "He would lob the ball over the wall and run around to fetch it.", "彼はボールを壁越しにふわりと投げては、回り込んで取りに行った。"),
    # Q12
    "reprimand": ("叱責する、戒告する", "動詞", "The board decided to reprimand rather than dismiss the officer.", "理事会はその職員を解雇するのではなく戒告することにした。"),
    "encumber": ("妨げる、重荷を負わせる", "動詞", "Heavy equipment can encumber a team working in narrow tunnels.", "重い装備は狭いトンネルで作業する隊の動きを妨げることがある。"),
    "advocate": ("主張する、擁護する", "動詞", "Few economists now advocate a return to the old system.", "今では旧制度への回帰を主張する経済学者はほとんどいない。"),
    "inscribe": ("刻む、記す", "動詞", "The mason will inscribe the date beneath the family name.", "石工は姓の下にその日付を刻むことになっている。"),
    # Q13
    "downplay": ("軽く見せる、控えめに言う", "動詞", "Ministers tried to downplay the size of the shortfall.", "閣僚たちはその不足額の大きさを小さく見せようとした。"),
    "embolden": ("大胆にする、勇気づける", "動詞", "The early success seemed to embolden a very cautious board.", "初期の成功は非常に慎重な理事会を大胆にしたようだった。"),
    "siphon": ("吸い上げる、抜き取る", "動詞", "Thieves used a hose to siphon fuel from parked lorries.", "泥棒たちはホースを使って駐車中のトラックから燃料を抜き取った。"),
    "incinerate": ("焼却する", "動詞", "Hospitals must incinerate this category of waste on site.", "病院はこの区分の廃棄物を敷地内で焼却しなければならない。"),
    # Q14
    "denounce": ("公然と非難する、告発する", "動詞", "Several bishops chose to denounce the new law from the pulpit.", "何人かの司教は説教壇からその新法を非難することを選んだ。"),
    "entice": ("誘惑する、そそのかす", "動詞", "Low fares entice travellers onto the early morning flights.", "安い運賃が旅行者を早朝便へと誘い込む。"),
    "fetter": ("束縛する、足かせをはめる", "動詞", "Excessive paperwork can fetter even the most willing volunteer.", "過度の書類仕事は、最も意欲的なボランティアさえ縛りつけかねない。"),
    "demonize": ("悪者扱いする", "動詞", "It is easy to demonize an industry nobody fully understands.", "誰も十分に理解していない産業を悪者扱いするのは簡単である。"),
    # Q15
    "palpable": ("はっきりと感じられる", "形容詞", "There was a palpable chill between the two delegations.", "2つの代表団の間には、はっきりと感じられる冷ややかさがあった。"),
    "inept": ("不器用な、無能な", "形容詞", "An inept translation made the manual almost useless.", "拙劣な翻訳がその取扱説明書をほとんど役に立たないものにした。"),
    "unkempt": ("手入れされていない、だらしない", "形容詞", "The garden was unkempt but full of unexpected flowers.", "その庭は手入れされていなかったが、思いがけない花であふれていた。"),
    "indignant": ("憤慨した", "形容詞", "Parents were indignant about the change to the bus route.", "保護者たちはバス路線の変更に憤慨していた。"),
    # Q16
    "aloof": ("よそよそしい、距離を置いた", "形容詞", "The new director seemed aloof for the first few months.", "新しい所長は最初の数か月はよそよそしく見えた。"),
    "laconic": ("言葉数の少ない、簡潔な", "形容詞", "His laconic replies made the interview unusually short.", "彼の素っ気ない返答が、その面接を異例に短くした。"),
    "obsequious": ("こびへつらう", "形容詞", "An obsequious waiter hovered by the table all evening.", "こびへつらう給仕が一晩中テーブルのそばをうろついていた。"),
    "quarrelsome": ("けんか好きな", "形容詞", "Two quarrelsome neighbors kept the whole street awake.", "けんか好きな2人の隣人が通り全体を眠らせなかった。"),
    # Q17
    "sultry": ("蒸し暑い", "形容詞", "August here is sultry, and few people work after midday.", "ここの8月は蒸し暑く、正午以降に働く人はほとんどいない。"),
    "vociferous": ("声高な、やかましい", "形容詞", "A vociferous minority delayed the decision by two months.", "声高な少数派がその決定を2か月遅らせた。"),
    "arduous": ("骨の折れる、困難な", "形容詞", "The arduous work of cataloguing took three summers.", "目録を作るという骨の折れる作業には3度の夏を要した。"),
    "altruistic": ("利他的な", "形容詞", "Their motives were more altruistic than anyone expected.", "彼らの動機は誰もが思っていたより利他的だった。"),
    # Q18
    "scrumptious": ("とてもおいしい", "形容詞", "The bakery on the corner makes a scrumptious almond tart.", "角のパン屋はとてもおいしいアーモンドタルトを作る。"),
    "ulterior": ("隠された、下心のある", "形容詞", "She suspected an ulterior purpose behind the sudden invitation.", "彼女は突然の招待の背後に隠された目的を疑った。"),
    "poised": ("落ち着いた、身構えた", "形容詞", "The young violinist remained poised despite the broken string.", "その若いバイオリン奏者は弦が切れても落ち着きを保っていた。"),
    "comatose": ("昏睡状態の", "形容詞", "The patient remained comatose for eleven days after the accident.", "その患者は事故の後、11日間昏睡状態のままだった。"),
    # Q19
    "oblique": ("遠回しの、斜めの", "形容詞", "He made an oblique reference to the earlier dispute.", "彼は以前の争いに遠回しに言及した。"),
    "assiduous": ("勤勉な、たゆまぬ", "形容詞", "Assiduous record-keeping saved the museum from a costly error.", "たゆまぬ記録管理が、その博物館を高くつく誤りから救った。"),
    "strident": ("耳障りな、押しつけがましい", "形容詞", "A strident alarm sounded every time the door was opened.", "扉が開くたびに耳障りな警報が鳴った。"),
    "extenuating": ("(罪を)軽減する、酌量すべき", "形容詞", "The court found extenuating circumstances and reduced the fine.", "裁判所は酌量すべき事情を認め、罰金を減額した。"),
    # Q20
    "waning": ("衰えつつある、欠けていく", "形容詞", "Interest in the sport has been waning since the last championship.", "その競技への関心は前回の選手権以来衰えつつある。"),
    "impermeable": ("浸透しない、不透過性の", "形容詞", "The lower layer is impermeable and holds water near the surface.", "下層は水を通さず、地表近くに水を保っている。"),
    "generic": ("一般的な、総称の", "形容詞", "The pharmacy stocks a generic version at a third of the price.", "その薬局は3分の1の値段で後発の同等品を置いている。"),
    "succulent": ("汁の多い、みずみずしい", "形容詞", "The stall sells succulent peaches for two months of the year.", "その屋台は年に2か月間、みずみずしい桃を売る。"),
    # Q21
    "gingerly": ("慎重に、恐る恐る", "副詞", "She stepped gingerly across the frozen puddles in the yard.", "彼女は庭の凍った水たまりを恐る恐る渡って歩いた。"),
    "sparingly": ("控えめに、節約して", "副詞", "Use the oil sparingly, since a little goes a long way.", "少量で足りるので、その油は控えめに使いなさい。"),
    "aptly": ("適切に、うまく", "副詞", "The village is aptly named after the spring beside the church.", "その村は教会のそばの泉にちなんで適切に名づけられている。"),
    "doggedly": ("粘り強く、頑固に", "副詞", "He doggedly repeated the experiment until the result held.", "彼は結果が安定するまで粘り強く実験を繰り返した。"),
    # Q22
    "chewed out": ("どなりつけた、厳しく叱った", "句動詞", "The sergeant chewed out the recruit who had lost his kit.", "軍曹は装備をなくした新兵を厳しく叱りつけた。"),
    "boxed up": ("箱詰めした", "句動詞", "They boxed up the entire archive in a single weekend.", "彼らは1回の週末で記録全体を箱詰めした。"),
    "dispensed with": ("(~を)なしで済ませた、省いた", "句動詞", "The committee dispensed with the reading of the previous minutes.", "委員会は前回の議事録の読み上げを省いた。"),
    "rode on": ("(~に)かかっていた", "句動詞", "A great deal rode on the result of that single inspection.", "その1回の検査の結果に多くがかかっていた。"),
    # Q23
    "level with": ("(~に)正直に打ち明ける", "句動詞", "It is better to level with patients about the likely outcome.", "起こりうる結果について患者に正直に伝えるほうがよい。"),
    "shoot for": ("(~を)目指す", "句動詞", "The department decided to shoot for a ten percent reduction.", "その部署は10パーセントの削減を目指すことにした。"),
    "bulk up": ("かさを増す、体を大きくする", "句動詞", "Players who bulk up too quickly often pick up injuries.", "急激に体を大きくした選手はけがをしやすい。"),
    "lean on": ("(~を)頼る、圧力をかける", "句動詞", "Small firms often lean on a single supplier for everything.", "小さな会社はしばしばすべてを1社の納入業者に頼っている。"),
    # Q24
    "sucked up to": ("(~に)ごまをすった", "句動詞", "Nobody respects a colleague who has sucked up to the boss for years.", "何年も上司にごまをすってきた同僚を尊敬する者はいない。"),
    "came in for": ("(批判などを)受けた", "句動詞", "The design came in for heavy criticism from local architects.", "その設計は地元の建築家から厳しい批判を受けた。"),
    "leapt out at": ("(~の)目に飛び込んできた", "句動詞", "One name leapt out at her from the long list of donors.", "長い寄付者名簿の中から1つの名前が彼女の目に飛び込んできた。"),
    "bore down on": ("(~に)迫った、圧力をかけた", "句動詞", "The storm bore down on the coast faster than forecast.", "嵐は予報より速く沿岸に迫った。"),
    # Q25
    "gained on": ("(~に)追い迫った", "句動詞", "The chasing pack gained on the leader with every lap.", "追走集団は周回ごとに先頭に追い迫った。"),
    "weeded out": ("(不要なものを)取り除いた", "句動詞", "The first sift weeded out half of the applications.", "最初のふるい分けで応募の半分が除かれた。"),
    "beefed up": ("強化した", "句動詞", "The museum beefed up security after the second break-in.", "その博物館は2度目の侵入の後、警備を強化した。"),
    "lashed out": ("激しく非難した、殴りかかった", "句動詞", "The manager lashed out at reporters after the third defeat.", "監督は3度目の敗戦の後、記者たちに激しく食ってかかった。"),
}


CORE_IMAGES = {
    "chewed out": {
        "chain": [
            {"term": "chew", "gloss": "かみ砕く"},
            {"term": "out", "gloss": "言葉を外へ浴びせて"},
            {"gloss": "相手をかみ砕くように言葉を浴びせて"},
            {"gloss": "厳しく叱りつける"},
        ],
        "particle": "out",
        "particleSense": "express",
    },
    "boxed up": {
        "chain": [
            {"term": "box", "gloss": "箱に入れる"},
            {"term": "up", "gloss": "中へ収め切って"},
            {"gloss": "残らず箱の中へ収めて閉じて"},
            {"gloss": "箱詰めする"},
        ],
        "particle": "up",
        "particleSense": "contain",
    },
    "dispensed with": {
        "chain": [
            {"term": "dispense", "gloss": "分け与える、施す"},
            {"term": "with", "gloss": "その対象について"},
            {"gloss": "必要なものとして扱うのをやめて"},
            {"gloss": "~をなしで済ませる"},
        ],
    },
    "rode on": {
        "chain": [
            {"term": "ride", "gloss": "乗る"},
            {"term": "on", "gloss": "その一点に乗って"},
            {"gloss": "結果が一つの土台の上に乗って"},
            {"gloss": "~にかかっている"},
        ],
        "particle": "on",
        "particleSense": "rely",
    },
    "level with": {
        "chain": [
            {"term": "level", "gloss": "水平にする"},
            {"term": "with", "gloss": "その相手と"},
            {"gloss": "相手と同じ高さに立って隠さずに"},
            {"gloss": "~に正直に打ち明ける"},
        ],
    },
    "shoot for": {
        "chain": [
            {"term": "shoot", "gloss": "撃つ、狙う"},
            {"term": "for", "gloss": "その的を目がけて"},
            {"gloss": "定めた的を目がけて放って"},
            {"gloss": "~を目指す"},
        ],
    },
    "bulk up": {
        "chain": [
            {"term": "bulk", "gloss": "かさを増す"},
            {"term": "up", "gloss": "量を高めて"},
            {"gloss": "全体の量を意図的に高めて"},
            {"gloss": "かさを増す、体を大きくする"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "lean on": {
        "chain": [
            {"term": "lean", "gloss": "寄りかかる"},
            {"term": "on", "gloss": "その相手に接して"},
            {"gloss": "体重を相手に預けて寄りかかって"},
            {"gloss": "~を頼る、圧力をかける"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "sucked up to": {
        "chain": [
            {"term": "suck", "gloss": "吸いつく"},
            {"term": "up", "gloss": "上の相手へ近づいて"},
            {"gloss": "上の立場の相手へすり寄って吸いついて"},
            {"gloss": "ごまをする"},
        ],
        "particle": "up",
        "particleSense": "approach",
    },
    "came in for": {
        "chain": [
            {"term": "come", "gloss": "来る"},
            {"term": "in", "gloss": "受ける側の位置に入って"},
            {"gloss": "批判が向かう先の位置に入って"},
            {"gloss": "批判などを受ける"},
        ],
        "particle": "in",
    },
    "leapt out at": {
        "chain": [
            {"term": "leap", "gloss": "跳ぶ"},
            {"term": "out", "gloss": "他より外へ飛び出して"},
            {"gloss": "並びの中から外へ飛び出して見える"},
            {"gloss": "目に飛び込んでくる"},
        ],
        "particle": "out",
        "particleSense": "spread",
    },
    "bore down on": {
        "chain": [
            {"term": "bear", "gloss": "重みをかける"},
            {"term": "down", "gloss": "上から押さえつけて"},
            {"gloss": "重みをかけながら相手へ近づいて"},
            {"gloss": "~に迫る、圧力をかける"},
        ],
        "particle": "down",
        "particleSense": "suppress",
    },
    "gained on": {
        "chain": [
            {"term": "gain", "gloss": "得る、増す"},
            {"term": "on", "gloss": "相手に接するほど"},
            {"gloss": "差を縮めて相手に接するほど近づいて"},
            {"gloss": "~に追い迫る"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "weeded out": {
        "chain": [
            {"term": "weed", "gloss": "雑草を抜く"},
            {"term": "out", "gloss": "外へ取り除いて"},
            {"gloss": "不要なものを抜いて外へ取り除いて"},
            {"gloss": "選り分けて除く"},
        ],
        "particle": "out",
        "particleSense": "remove",
    },
    "beefed up": {
        "chain": [
            {"term": "beef", "gloss": "肉付けする"},
            {"term": "up", "gloss": "厚みを高めて"},
            {"gloss": "中身に肉を付けて厚みを高めて"},
            {"gloss": "強化する"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "lashed out": {
        "chain": [
            {"term": "lash", "gloss": "むちで打つ"},
            {"term": "out", "gloss": "外へ打ち出して"},
            {"gloss": "怒りを外へ勢いよく打ち出して"},
            {"gloss": "激しく非難する"},
        ],
        "particle": "out",
        "particleSense": "express",
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
        raise ValueError("模試第20回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-20 割り当てに従う",
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
