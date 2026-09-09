"""英検1級 模試第16回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-16 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-16"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "The opening night was a complete (   ): the sound failed twice and half the cast missed their cues.",
        "choices": ["fiasco", "allure", "treatise", "tatter"],
        "answerIndex": 0,
        "translation": "初日は完全な失敗だった。音響は2度止まり、出演者の半数が出のきっかけを外した。",
    },
    {
        "stem": "The laboratory lost its (   ) last year after inspectors found that several records had been altered.",
        "choices": ["delegation", "accreditation", "severance", "deluge"],
        "answerIndex": 1,
        "translation": "検査官がいくつかの記録の改ざんを発見した後、その研究所は昨年、認定を失った。",
    },
    {
        "stem": "Branch managers are given considerable (   ) in deciding how to spend the local budget.",
        "choices": ["hassle", "retaliation", "latitude", "truce"],
        "answerIndex": 2,
        "translation": "支店長には地域予算の使い方を決めるうえでかなりの裁量が与えられている。",
    },
    {
        "stem": "Observers called the vote a (   ) of democracy, since only one name appeared on the ballot.",
        "choices": ["spree", "credulity", "profusion", "travesty"],
        "answerIndex": 3,
        "translation": "投票用紙に名前が1つしか載っていなかったため、監視団はその投票を民主主義の茶番だと呼んだ。",
    },
    {
        "stem": "He has a real (   ) for settling office arguments long before anyone raises their voice.",
        "choices": ["knack", "zenith", "pertinence", "capitulation"],
        "answerIndex": 0,
        "translation": "彼には誰かが声を荒げるずっと前に職場の口論を収めてしまう本物のこつがある。",
    },
    {
        "stem": "The airline found itself in a (   ) when both replacement crews were delayed abroad.",
        "choices": ["conflagration", "predicament", "throng", "cowardice"],
        "answerIndex": 1,
        "translation": "交代の乗務員が2組とも海外で足止めされ、その航空会社は苦境に陥った。",
    },
    {
        "stem": "The (   ) of the smaller publisher gave the group a strong position in textbooks.",
        "choices": ["abstention", "inception", "acquisition", "statute"],
        "answerIndex": 2,
        "translation": "その小規模出版社の買収は、そのグループに教科書分野で強固な地位をもたらした。",
    },
    {
        "stem": "The villagers (   ) the governor to reopen the only road that crosses the mountains.",
        "choices": ["beseeched", "ameliorated", "disconcerted", "bewildered"],
        "answerIndex": 0,
        "translation": "村人たちは山を越える唯一の道路を再開してほしいと知事に懇願した。",
    },
    {
        "stem": "The two departments (   ) over the use of office space for most of the financial year.",
        "choices": ["cowered", "bickered", "incurred", "invoked"],
        "answerIndex": 1,
        "translation": "その2つの部署は会計年度のほとんどの期間、事務所の使い方をめぐって言い争っていた。",
    },
    {
        "stem": "Under heavy pressure from the authorities, the astronomer publicly (   ) the findings he had published, admitting that his earlier conclusions were wrong.",
        "choices": ["interspersed", "flaunted", "recanted", "grilled"],
        "answerIndex": 2,
        "translation": "当局からの強い圧力を受け、その天文学者は自分が発表した研究結果を公に撤回し、以前の結論が誤りだったと認めた。",
    },
    {
        "stem": "Health workers (   ) more than twelve thousand children across the province in the autumn of last year.",
        "choices": ["meandered", "pervaded", "inculcated", "inoculated"],
        "answerIndex": 3,
        "translation": "保健員たちは昨年の秋に、州全体で1万2000人を超える子どもに予防接種を行った。",
    },
    {
        "stem": "His careless remark about the budget (   ) the very committee whose support he most needed, turning its members into open enemies for the rest of his term.",
        "choices": ["antagonized", "foraged", "tangled", "presided"],
        "answerIndex": 0,
        "translation": "予算についての彼の不用意な発言は、まさに最も支持を必要としていた委員会を敵に回し、任期の残りの間その委員たちを公然たる敵にしてしまった。",
    },
    {
        "stem": "She (   ) surprise at the announcement, although she had known about it for weeks.",
        "choices": ["intercepted", "feigned", "languished", "coddled"],
        "answerIndex": 1,
        "translation": "彼女はその発表に驚いたふりをしたが、何週間も前からそれを知っていた。",
    },
    {
        "stem": "The mayor (   ) the offer of a free car and returned it to the dealership the same day.",
        "choices": ["segregated", "circumvented", "petrified", "spurned"],
        "answerIndex": 3,
        "translation": "市長は無料の車の申し出をはねつけ、その日のうちに販売店へ返した。",
    },
    {
        "stem": "The photographs show an (   ) village of stone cottages, narrow lanes and grazing sheep.",
        "choices": ["idyllic", "putrid", "apathetic", "deplorable"],
        "answerIndex": 0,
        "translation": "その写真は石造りの小屋と細い小道、草をはむ羊のいる牧歌的な村を写している。",
    },
    {
        "stem": "Soft lighting and quiet music are (   ) to the sort of conversation the clinic wants.",
        "choices": ["frigid", "conducive", "pallid", "innocuous"],
        "answerIndex": 1,
        "translation": "柔らかな照明と静かな音楽は、その診療所が望むような会話を促すのに役立つ。",
    },
    {
        "stem": "The high plateau is (   ), with no trees and no human settlement for eighty kilometers.",
        "choices": ["shrewd", "menial", "desolate", "dispassionate"],
        "answerIndex": 2,
        "translation": "その高地の高原は荒涼としていて、80キロにわたり樹木も人の集落もない。",
    },
    {
        "stem": "Fame in that industry is (   ), and few performers last more than a couple of seasons.",
        "choices": ["obnoxious", "celibate", "emblematic", "ephemeral"],
        "answerIndex": 3,
        "translation": "その業界での名声はつかの間のもので、2シーズンを超えて続く演者はほとんどいない。",
    },
    {
        "stem": "His (   ) praise for the new design embarrassed the architect who had drawn it.",
        "choices": ["effusive", "ostensible", "chronic", "buoyant"],
        "answerIndex": 0,
        "translation": "新しい設計への彼の大げさな称賛は、それを描いた建築家を当惑させた。",
    },
    {
        "stem": "The lake was completely (   ) that morning, without so much as a ripple near the shore.",
        "choices": ["quaint", "provident", "placid", "ineligible"],
        "answerIndex": 2,
        "translation": "その朝、湖は完全に穏やかで、岸辺にはさざ波一つ立っていなかった。",
    },
    {
        "stem": "He denounced the proposal so (   ), shouting down two interruptions, that the chair had to suspend the sitting.",
        "choices": ["gallantly", "vehemently", "sheepishly", "irreparably"],
        "answerIndex": 1,
        "translation": "彼は2度の野次をどなり返して黙らせるほど激しくその提案を非難したので、議長は審議を中断せざるを得なかった。",
    },
    {
        "stem": "A national campaign eventually (   ) the disease in the western provinces altogether within a decade.",
        "choices": ["stamped out", "whipped up", "dashed off", "palmed off"],
        "answerIndex": 0,
        "translation": "全国的な運動が最終的に10年のうちに西部の州からその病気を完全に根絶した。",
    },
    {
        "stem": "The committee (   ) the proposal for a month, weighing every advantage in detail, before asking for a second opinion.",
        "choices": ["blurted out", "stripped out", "chewed over", "waved aside"],
        "answerIndex": 2,
        "translation": "委員会は別の見解を求める前に、1か月かけて利点を細かく比較しながらその提案をじっくり検討した。",
    },
    {
        "stem": "The annual report (   ) the shortfall rather than explaining to shareholders how it had arisen.",
        "choices": ["blended in", "papered over", "tripped up", "drowned out"],
        "answerIndex": 1,
        "translation": "その年次報告書は、不足がどう生じたかを株主に説明するのではなく、体裁を取り繕って覆い隠した。",
    },
    {
        "stem": "The director quietly (   ) two of the senior staff before announcing the restructuring to everyone.",
        "choices": ["sounded out", "fussed over", "talked down", "racked up"],
        "answerIndex": 0,
        "translation": "その部長は全員に組織再編を発表する前に、静かに幹部職員のうち2人の意向を打診した。",
    },
]


DETAILS = {
    # Q1
    "fiasco": ("大失敗", "名詞", "The launch turned into a fiasco when the software crashed on stage.", "壇上でソフトウェアが停止し、その発表会は大失敗になった。"),
    "allure": ("魅力、魅惑", "名詞", "The allure of the old harbor attracts painters every summer.", "その古い港の魅力は毎夏、画家たちを引き寄せる。"),
    "treatise": ("論文、専門書", "名詞", "He published a treatise on coastal erosion that is still cited.", "彼は今なお引用される海岸浸食についての論文を発表した。"),
    "tatter": ("ぼろ切れ", "名詞", "A single tatter of cloth was all that remained of the flag.", "その旗に残っていたのはぼろ切れ1枚だけだった。"),
    # Q2
    "delegation": ("代表団、委任", "名詞", "A delegation of teachers met the minister on Thursday morning.", "教員の代表団が木曜の朝に大臣と面会した。"),
    "accreditation": ("認定、公認", "名詞", "The course lost its accreditation and had to be rewritten.", "その課程は認定を失い、書き直さなければならなかった。"),
    "severance": ("解雇手当、切断", "名詞", "Each employee received twelve weeks of severance after the plant closed.", "工場が閉鎖された後、各従業員は12週間分の解雇手当を受け取った。"),
    "deluge": ("大洪水、殺到", "名詞", "A deluge of complaints followed the change to the timetable.", "時刻表の変更の後に苦情が殺到した。"),
    # Q3
    "hassle": ("面倒、いざこざ", "名詞", "Getting the permit renewed is a hassle that takes several visits.", "許可証の更新は何度も足を運ぶ必要のある面倒な手続きである。"),
    "retaliation": ("報復", "名詞", "The tariffs were imposed in retaliation for last year's restrictions.", "その関税は昨年の規制への報復として課された。"),
    "latitude": ("裁量の自由、緯度", "名詞", "Editors are allowed some latitude in choosing the cover image.", "編集者には表紙の画像を選ぶ際にいくらかの裁量が認められている。"),
    "truce": ("休戦、停戦", "名詞", "A three-day truce allowed relief supplies to reach the town.", "3日間の休戦により救援物資が町に届いた。"),
    # Q4
    "spree": ("度を越した行為、浪費", "名詞", "A shopping spree in January emptied the account by February.", "1月の買い物三昧は2月までに口座を空にした。"),
    "credulity": ("信じやすさ、軽信", "名詞", "The scheme relied entirely on the credulity of elderly investors.", "その計画は高齢の投資家の信じやすさに完全に依存していた。"),
    "profusion": ("豊富、あふれるほどの量", "名詞", "Wildflowers grow in profusion along the disused railway line.", "廃線となった線路沿いには野生の花があふれるほど咲いている。"),
    "travesty": ("茶番、ひどい見せかけ", "名詞", "Critics called the adaptation a travesty of a much-loved novel.", "批評家たちはその翻案を、広く愛された小説のひどい歪曲だと呼んだ。"),
    # Q5
    "knack": ("こつ、才覚", "名詞", "She has a knack for repairing machines nobody else understands.", "彼女には誰も理解できない機械を修理するこつがある。"),
    "zenith": ("絶頂、頂点", "名詞", "The company reached its zenith in the early 1970s.", "その会社は1970年代初頭に絶頂を迎えた。"),
    "pertinence": ("適切さ、関連性", "名詞", "The pertinence of the question became clear only much later.", "その質問の的確さがはっきりしたのはずっと後になってからだった。"),
    "capitulation": ("降伏、屈服", "名詞", "The capitulation of the garrison ended the siege in November.", "守備隊の降伏は11月にその包囲戦を終わらせた。"),
    # Q6
    "conflagration": ("大火災", "名詞", "The conflagration destroyed four streets of wooden houses.", "その大火災は木造家屋の並ぶ4つの通りを焼き尽くした。"),
    "predicament": ("苦境、窮地", "名詞", "The family was in a predicament with no money and no passports.", "その一家は金もパスポートもない窮地にあった。"),
    "throng": ("群衆", "名詞", "A throng of visitors filled the courtyard before the doors opened.", "扉が開く前から、訪問者の群衆が中庭を埋めていた。"),
    "cowardice": ("臆病、卑怯", "名詞", "He was accused of cowardice for leaving before the vote.", "彼は採決の前に立ち去ったことで臆病だと非難された。"),
    # Q7
    "abstention": ("棄権、控えること", "名詞", "The motion passed with two votes against and one abstention.", "その動議は反対2票、棄権1票で可決された。"),
    "inception": ("開始、発端", "名詞", "The fund has grown steadily since its inception in 1994.", "そのファンドは1994年の発足以来、着実に成長している。"),
    "acquisition": ("買収、取得", "名詞", "The acquisition of the rival brand doubled the group's factories.", "競合ブランドの買収により、そのグループの工場は倍になった。"),
    "statute": ("法令、成文法", "名詞", "A nineteenth-century statute still governs fishing in the estuary.", "19世紀の法令が今なおその河口での漁業を規定している。"),
    # Q8
    "beseeched": ("懇願した", "動詞", "The refugees beseeched the guards to let the children through.", "難民たちは子どもだけでも通してほしいと警備兵に懇願した。"),
    "ameliorated": ("改善した、緩和した", "動詞", "Better drainage ameliorated conditions in the lower fields.", "排水の改善が低地の畑の状態をよくした。"),
    "presided": ("議長を務めた、統括した", "動詞", "A retired judge presided over the inquiry for eighteen months.", "退職した裁判官が18か月にわたりその調査の議長を務めた。"),
    "bewildered": ("当惑させた", "動詞", "The new ticketing system bewildered passengers for the first week.", "新しい発券システムは最初の1週間、乗客を当惑させた。"),
    # Q9
    "cowered": ("縮こまった、すくんだ", "動詞", "The dog cowered under the table during the thunderstorm.", "その犬は雷雨の間、テーブルの下で縮こまっていた。"),
    "bickered": ("口論した、言い争った", "動詞", "The brothers bickered about the inheritance for eleven years.", "その兄弟は遺産のことで11年間言い争った。"),
    "incurred": ("(損失や非難を)招いた", "動詞", "The delay incurred penalties of nearly forty thousand euros.", "その遅延は4万ユーロ近い違約金を招いた。"),
    "invoked": ("(法などを)発動した、引き合いに出した", "動詞", "The government invoked emergency powers for the third time that year.", "政府はその年3度目となる緊急権限を発動した。"),
    # Q10
    "interspersed": ("間に散りばめた", "動詞", "The author interspersed the argument with letters from the period.", "著者は議論の間に当時の書簡を散りばめた。"),
    "flaunted": ("見せびらかした", "動詞", "He flaunted his new watch at every opportunity that week.", "彼はその週、機会あるごとに新しい腕時計を見せびらかした。"),
    "recanted": ("(前言を)撤回した", "動詞", "The witness recanted her statement on the second day of the trial.", "その証人は裁判の2日目に自分の供述を撤回した。"),
    "grilled": ("厳しく問いただした、焼いた", "動詞", "Reporters grilled the minister for forty minutes about the contract.", "記者たちはその契約について大臣を40分間問い詰めた。"),
    # Q11
    "meandered": ("曲がりくねって進んだ", "動詞", "The river meandered across the flat plain toward the sea.", "その川は平坦な平野を曲がりくねりながら海へ向かった。"),
    "pervaded": ("(全体に)行き渡った", "動詞", "A smell of wet wool pervaded the crowded waiting room.", "濡れた毛織物のにおいが混み合った待合室に立ちこめていた。"),
    "inculcated": ("(考えを)教え込んだ", "動詞", "The academy inculcated discipline through a rigid daily timetable.", "その学校は厳格な日課によって規律を教え込んだ。"),
    "inoculated": ("予防接種をした", "動詞", "Vets inoculated the whole herd against the virus in March.", "獣医たちは3月にその群れ全体にウイルスの予防接種をした。"),
    # Q12
    "antagonized": ("敵に回した、反感を買った", "動詞", "His tone antagonized the residents he had come to reassure.", "彼の口調は、安心させに来たはずの住民の反感を買った。"),
    "foraged": ("食料をあさった、探し回った", "動詞", "The birds foraged along the tideline for most of the morning.", "その鳥たちは午前中のほとんど、潮境に沿って餌をあさっていた。"),
    "tangled": ("もつれさせた", "動詞", "The wind tangled the ropes at the top of the mast.", "風がマストの先端のロープをもつれさせた。"),
    "disconcerted": ("うろたえさせた", "動詞", "The silence that followed disconcerted even the experienced speaker.", "その後に続いた沈黙は、経験豊富な講演者さえうろたえさせた。"),
    # Q13
    "intercepted": ("途中で捕らえた、傍受した", "動詞", "Coastguards intercepted the vessel eleven kilometers from the port.", "沿岸警備隊は港から11キロの地点でその船を臨検した。"),
    "feigned": ("装った、ふりをした", "動詞", "The cat feigned indifference until the packet was opened.", "その猫は袋が開けられるまで無関心を装っていた。"),
    "languished": ("放置された、衰弱した", "動詞", "The proposal languished in a subcommittee for two whole years.", "その提案は小委員会で丸2年間、放置された。"),
    "coddled": ("甘やかした、大事にしすぎた", "動詞", "Critics said the scheme coddled firms that should have failed.", "批評家たちは、その制度は本来倒れるべき企業を甘やかしたと述べた。"),
    # Q14
    "segregated": ("分離した、隔離した", "動詞", "The plant segregated waste into six separate streams.", "その工場は廃棄物を6つの別々の流れに分別した。"),
    "circumvented": ("回避した、迂回した", "動詞", "The firm circumvented the ban by registering in another country.", "その会社は別の国で登記することによって禁止措置を回避した。"),
    "petrified": ("すくませた、石化させた", "動詞", "The noise from the cellar petrified the children upstairs.", "地下室からの物音は2階の子どもたちをすくみ上がらせた。"),
    "spurned": ("はねつけた、拒絶した", "動詞", "She spurned three job offers before accepting the fourth.", "彼女は3つの求人を断ってから4つ目を受け入れた。"),
    # Q15
    "idyllic": ("牧歌的な、のどかな", "形容詞", "They spent an idyllic week in a cabin beside the lake.", "彼らは湖畔の小屋でのどかな1週間を過ごした。"),
    "putrid": ("腐敗した、悪臭を放つ", "形容詞", "A putrid smell led inspectors to the blocked drain.", "腐敗した悪臭が検査官を詰まった排水管へ導いた。"),
    "apathetic": ("無関心な", "形容詞", "Younger voters were apathetic about an election with no real choice.", "実質的な選択肢のない選挙に対して、若い有権者は無関心だった。"),
    "deplorable": ("嘆かわしい、ひどい", "形容詞", "The housing was in a deplorable state when the family moved in.", "その一家が入居したとき、住宅は嘆かわしい状態だった。"),
    # Q16
    "frigid": ("極寒の、よそよそしい", "形容詞", "Frigid air from the north kept the pass closed for a week.", "北からの極寒の空気が1週間その峠を閉ざしたままにした。"),
    "conducive": ("(~を)促す、助けとなる", "形容詞", "An open plan office is not always conducive to concentration.", "開放的な事務所は必ずしも集中を助けるとは限らない。"),
    "pallid": ("青白い、生気のない", "形容詞", "He looked pallid and asked to sit down for a moment.", "彼は青白い顔をしており、少し座らせてほしいと言った。"),
    "innocuous": ("無害な、当たり障りのない", "形容詞", "The plant looks dangerous but is entirely innocuous.", "その植物は危険そうに見えるが、まったく無害である。"),
    # Q17
    "shrewd": ("抜け目のない、鋭い", "形容詞", "A shrewd purchase in 1998 made the family's fortune.", "1998年の抜け目のない買い物が一家の財を築いた。"),
    "menial": ("単調で低賃金の、卑しい", "形容詞", "He took menial work in the docks while studying at night.", "彼は夜に勉強しながら港で単調な仕事に就いた。"),
    "desolate": ("荒涼とした、寂れた", "形容詞", "The desolate moor offers no shelter of any kind.", "その荒涼とした湿原にはいかなる避難場所もない。"),
    "dispassionate": ("冷静な、公平な", "形容詞", "The report gives a dispassionate account of a bitter dispute.", "その報告書は激しい紛争を冷静に記述している。"),
    # Q18
    "obnoxious": ("非常に不快な", "形容詞", "An obnoxious guest ruined the atmosphere within ten minutes.", "非常に不快な客が10分でその場の雰囲気を台無しにした。"),
    "celibate": ("独身の、禁欲の", "形容詞", "The order requires its members to remain celibate for life.", "その修道会は会員に生涯独身であることを求めている。"),
    "emblematic": ("象徴的な", "形容詞", "The chimney is emblematic of the town's industrial past.", "その煙突は町の産業の過去を象徴している。"),
    "ephemeral": ("つかの間の、はかない", "形容詞", "Snow on the coast is ephemeral and rarely lasts a day.", "沿岸の雪ははかなく、1日ももたないことが多い。"),
    # Q19
    "effusive": ("大げさな、感情をあらわにした", "形容詞", "Her effusive thanks made the young volunteer uncomfortable.", "彼女の大げさな感謝は、その若いボランティアを居心地悪くさせた。"),
    "ostensible": ("表向きの、うわべの", "形容詞", "The ostensible reason for the visit was a routine inspection.", "その訪問の表向きの理由は定期点検だった。"),
    "chronic": ("慢性の、長期にわたる", "形容詞", "A chronic shortage of housing has troubled the city for decades.", "慢性的な住宅不足が何十年もその都市を悩ませてきた。"),
    "buoyant": ("浮力のある、上向きの", "形容詞", "The market remained buoyant despite the gloomy forecasts.", "暗い予測にもかかわらず、市場は活況を保った。"),
    # Q20
    "quaint": ("風変わりで趣のある", "形容詞", "The village has a quaint bakery that still uses a wood oven.", "その村には今も薪窯を使う趣のあるパン屋がある。"),
    "provident": ("先を見越した、用心深い", "形容詞", "A provident farmer keeps two seasons of feed in store.", "先を見越した農場主は2季分の飼料を蓄えておく。"),
    "placid": ("穏やかな、静かな", "形容詞", "The placid surface of the bay hid a very strong current.", "その入り江の穏やかな水面は非常に強い流れを隠していた。"),
    "ineligible": ("資格のない", "形容詞", "Part-time staff were ineligible for the housing allowance.", "非常勤職員は住宅手当の対象外だった。"),
    # Q21
    "gallantly": ("勇敢に、礼儀正しく", "副詞", "The crew gallantly returned twice to search for survivors.", "乗組員たちは生存者を捜すため勇敢に2度引き返した。"),
    "vehemently": ("激しく、猛烈に", "副詞", "She vehemently denied ever having seen the document.", "彼女はその文書を見たことは一度もないと激しく否定した。"),
    "sheepishly": ("きまり悪そうに", "副詞", "He sheepishly admitted that he had forgotten the tickets.", "彼はきまり悪そうに切符を忘れたと認めた。"),
    "irreparably": ("修復できないほどに", "副詞", "The flood irreparably damaged the archive in the basement.", "洪水は地下の記録保管室を修復不可能なほど損傷させた。"),
    # Q22
    "stamped out": ("根絶した、踏み消した", "句動詞", "Vaccination stamped out the disease in that country by 1979.", "予防接種は1979年までにその国からその病気を根絶した。"),
    "whipped up": ("手早く作った、あおり立てた", "句動詞", "He whipped up a meal for eight people in under an hour.", "彼は1時間足らずで8人分の食事を手早く作った。"),
    "dashed off": ("走り書きした、急いで書いた", "句動詞", "She dashed off a note and left it under the windscreen wiper.", "彼女は走り書きのメモを書き、ワイパーの下に挟んで置いた。"),
    "palmed off": ("(偽物を)押しつけた", "句動詞", "The trader palmed off a damaged violin as a restored antique.", "その業者は傷んだバイオリンを修復済みの骨董品と偽って押しつけた。"),
    # Q23
    "blurted out": ("思わず口走った", "句動詞", "The boy blurted out the answer before the question had ended.", "その少年は質問が終わる前に思わず答えを口走った。"),
    "stripped out": ("取り除いた、抜き取った", "句動詞", "Builders stripped out the wiring before the survey began.", "建築業者は調査が始まる前に配線を撤去した。"),
    "chewed over": ("じっくり考えた", "句動詞", "They chewed over the offer during a long walk by the river.", "彼らは川沿いの長い散歩の間、その申し出をじっくり考えた。"),
    "waved aside": ("(意見などを)一蹴した", "句動詞", "The chairman waved aside the objection and moved to a vote.", "議長はその異議を一蹴し、採決に移った。"),
    # Q24
    "blended in": ("溶け込んだ、目立たなかった", "句動詞", "The new bricks blended in surprisingly well with the old wall.", "新しいれんがは古い壁に驚くほどよくなじんだ。"),
    "papered over": ("(問題を)取り繕った", "句動詞", "The statement papered over a serious disagreement inside the cabinet.", "その声明は内閣内部の深刻な意見の対立を取り繕ったものだった。"),
    "tripped up": ("しくじらせた、つまずかせた", "句動詞", "One careless date tripped up an otherwise flawless application.", "1つの不注意な日付が、それ以外は完璧な申請をしくじらせた。"),
    "drowned out": ("(音を)かき消した", "句動詞", "The helicopter drowned out every word of the ceremony.", "ヘリコプターが式典の言葉を一つ残らずかき消した。"),
    # Q25
    "sounded out": ("(意向を)打診した", "句動詞", "The party sounded out three candidates before the announcement.", "その政党は発表の前に3人の候補者の意向を打診した。"),
    "fussed over": ("(~を)構いすぎた、大騒ぎした", "句動詞", "His aunt fussed over the guests until they asked her to sit.", "彼のおばは客たちが座るように頼むまで彼らの世話を焼き続けた。"),
    "talked down": ("見下した話し方をした、説き伏せた", "句動詞", "The instructor never talked down to beginners in his classes.", "その指導者は授業で初心者を見下した話し方をすることが決してなかった。"),
    "racked up": ("(得点や損失を)積み上げた", "句動詞", "The team racked up nine wins before losing a single match.", "そのチームは1敗もせずに9勝を積み上げた。"),
}


CORE_IMAGES = {
    "stamped out": {
        "chain": [
            {"term": "stamp", "gloss": "踏みつける"},
            {"term": "out", "gloss": "外へ取り除いて"},
            {"gloss": "火を踏みつけて跡形なく取り除いて"},
            {"gloss": "根絶する"},
        ],
        "particle": "out",
        "particleSense": "remove",
    },
    "whipped up": {
        "chain": [
            {"term": "whip", "gloss": "手早くかき混ぜる"},
            {"term": "up", "gloss": "形になるまで整えて"},
            {"gloss": "材料を手早くかき混ぜて形にして"},
            {"gloss": "手早く作る"},
        ],
        "particle": "up",
        "particleSense": "prepare",
    },
    "dashed off": {
        "chain": [
            {"term": "dash", "gloss": "勢いよく走る"},
            {"term": "off", "gloss": "手元から切り離して"},
            {"gloss": "一気に書いて手元から離して"},
            {"gloss": "走り書きする"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "palmed off": {
        "chain": [
            {"term": "palm", "gloss": "手のひらに隠す"},
            {"term": "off", "gloss": "自分から切り離して"},
            {"gloss": "中身を隠したまま自分から手放して"},
            {"gloss": "偽物を押しつける"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "blurted out": {
        "chain": [
            {"term": "blurt", "gloss": "だしぬけに言う"},
            {"term": "out", "gloss": "口の外へ出して"},
            {"gloss": "考える前に言葉を口の外へ出して"},
            {"gloss": "思わず口走る"},
        ],
        "particle": "out",
        "particleSense": "express",
    },
    "stripped out": {
        "chain": [
            {"term": "strip", "gloss": "はぎ取る"},
            {"term": "out", "gloss": "内部から取り除いて"},
            {"gloss": "中身をはぎ取って外へ出して"},
            {"gloss": "取り除く"},
        ],
        "particle": "out",
        "particleSense": "remove",
    },
    "chewed over": {
        "chain": [
            {"term": "chew", "gloss": "かむ"},
            {"term": "over", "gloss": "全体を繰り返し"},
            {"gloss": "考えを何度もかみ砕いて"},
            {"gloss": "じっくり考える"},
        ],
        "particle": "over",
    },
    "waved aside": {
        "chain": [
            {"term": "wave", "gloss": "手を振る"},
            {"term": "aside", "gloss": "脇へどけて"},
            {"gloss": "手を振って話を脇へどけて"},
            {"gloss": "一蹴する"},
        ],
    },
    "blended in": {
        "chain": [
            {"term": "blend", "gloss": "混ざり合う"},
            {"term": "in", "gloss": "周りの中へ入って"},
            {"gloss": "周囲の色や形の中へ混ざり込んで"},
            {"gloss": "溶け込む、目立たない"},
        ],
        "particle": "in",
    },
    "papered over": {
        "chain": [
            {"term": "paper", "gloss": "紙を貼る"},
            {"term": "over", "gloss": "上から覆って"},
            {"gloss": "ひび割れの上から紙を貼って覆って"},
            {"gloss": "問題を取り繕う"},
        ],
        "particle": "over",
    },
    "tripped up": {
        "chain": [
            {"term": "trip", "gloss": "つまずかせる"},
            {"term": "up", "gloss": "足をすくって"},
            {"gloss": "小さな段差で足をすくって"},
            {"gloss": "しくじらせる"},
        ],
        "particle": "up",
        "particleSense": "disrupt",
    },
    "drowned out": {
        "chain": [
            {"term": "drown", "gloss": "水に沈める"},
            {"term": "out", "gloss": "外へ押し出して消して"},
            {"gloss": "大きな音で小さな音を沈めて消して"},
            {"gloss": "音をかき消す"},
        ],
        "particle": "out",
        "particleSense": "remove",
    },
    "sounded out": {
        "chain": [
            {"term": "sound", "gloss": "測深して深さを測る"},
            {"term": "out", "gloss": "探り出して"},
            {"gloss": "相手の考えの深さを少しずつ探り出して"},
            {"gloss": "意向を打診する"},
        ],
    },
    "fussed over": {
        "chain": [
            {"term": "fuss", "gloss": "気をもんで騒ぐ"},
            {"term": "over", "gloss": "その対象を覆うように"},
            {"gloss": "対象に覆いかぶさるように気を回して"},
            {"gloss": "構いすぎる"},
        ],
        "particle": "over",
    },
    "talked down": {
        "chain": [
            {"term": "talk", "gloss": "話す"},
            {"term": "down", "gloss": "相手を下に置いて"},
            {"gloss": "相手を一段下に置いた調子で話して"},
            {"gloss": "見下した話し方をする"},
        ],
        "particle": "down",
        "particleSense": "lower",
    },
    "racked up": {
        "chain": [
            {"term": "rack", "gloss": "棚に並べる"},
            {"term": "up", "gloss": "上へ積み上げて"},
            {"gloss": "得点や損失を棚に並べて積み上げて"},
            {"gloss": "積み上げる"},
        ],
        "particle": "up",
        "particleSense": "raise",
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
        raise ValueError("模試第16回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-16 割り当てに従う",
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
