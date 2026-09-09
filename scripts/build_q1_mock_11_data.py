"""英検1級 模試第11回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-11 の割り当てに従う。
Q18 の forlorn は同一セットの forlornly と紛らわしいため、余剰在庫の diffident へ差し替えた。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-11"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "A small (   ) of senior editors decided which stories appeared on the front page, and other reporters had no say at all.",
        "choices": ["blotch", "clique", "pinnacle", "bounty"],
        "answerIndex": 1,
        "translation": "上級編集者の小さな仲間内の集団がどの記事を一面に載せるかを決めており、他の記者にはまったく発言権がなかった。",
    },
    {
        "stem": "The trial was widely condemned as a (   ), since the verdict had clearly been decided long before it began.",
        "choices": ["prelate", "farce", "offshoot", "platitude"],
        "answerIndex": 1,
        "translation": "その裁判は茶番だと広く非難された。判決が始まるずっと前に明らかに決まっていたからである。",
    },
    {
        "stem": "Party members gathered for a (   ) in the state capital to choose their candidate for governor.",
        "choices": ["caucus", "testament", "juncture", "enmity"],
        "answerIndex": 0,
        "translation": "党員たちは知事候補を選ぶため、州都で党員集会に集まった。",
    },
    {
        "stem": "A generous (   ) from a former student allows the college to offer twelve scholarships every year.",
        "choices": ["periphery", "deferral", "endowment", "commotion"],
        "answerIndex": 2,
        "translation": "卒業生からの気前のよい寄付基金のおかげで、その大学は毎年12件の奨学金を提供できている。",
    },
    {
        "stem": "Studying his family's (   ), Daniel discovered that his great-grandparents had arrived from Portugal in 1904.",
        "choices": ["genealogy", "propensity", "extrovert", "contention"],
        "answerIndex": 0,
        "translation": "家系を調べていて、ダニエルは曽祖父母が1904年にポルトガルから渡ってきたことを知った。",
    },
    {
        "stem": "The dentist found a small (   ) in one of the back teeth and filled it the same afternoon.",
        "choices": ["reformation", "socialite", "fugitive", "cavity"],
        "answerIndex": 3,
        "translation": "歯科医は奥歯の1本に小さな虫歯を見つけ、その日の午後のうちに詰め物をした。",
    },
    {
        "stem": "The instrument measures the (   ) of the wind at the top of the tower every ten seconds.",
        "choices": ["trance", "upstart", "velocity", "ember"],
        "answerIndex": 2,
        "translation": "その計器は10秒ごとに塔の頂上での風の速度を測定する。",
    },
    {
        "stem": "The construction firm (   ) on its loans last winter, and the bank seized two of its unfinished properties.",
        "choices": ["defaulted", "revitalized", "gargled", "amplified"],
        "answerIndex": 0,
        "translation": "その建設会社は昨冬に融資の返済を怠り、銀行は未完成の物件2件を差し押さえた。",
    },
    {
        "stem": "The proclamation of 1863 (   ) enslaved people in the rebelling states, although enforcement took several more years.",
        "choices": ["abated", "emancipated", "distorted", "delineated"],
        "answerIndex": 1,
        "translation": "1863年の宣言は反乱州の奴隷にされていた人々を解放したが、その執行には何年もかかった。",
    },
    {
        "stem": "The puppy (   ) at the door for an hour after its owner left for work.",
        "choices": ["liquidated", "floundered", "whimpered", "pecked"],
        "answerIndex": 2,
        "translation": "その子犬は飼い主が仕事に出かけた後、1時間ドアのところでくんくん鳴いていた。",
    },
    {
        "stem": "Hospital staff (   ) every surface in the isolation ward twice a day during the outbreak.",
        "choices": ["sanitized", "rejuvenated", "bartered", "mustered"],
        "answerIndex": 0,
        "translation": "感染拡大の間、職員は病棟のあらゆる表面を1日2回消毒した。",
    },
    {
        "stem": "Two men (   ) the businessman outside his hotel and demanded a ransom from his company.",
        "choices": ["cringed", "orchestrated", "vanquished", "abducted"],
        "answerIndex": 3,
        "translation": "2人の男がホテルの外でその実業家を拉致し、彼の会社に身代金を要求した。",
    },
    {
        "stem": "Using a wooden paddle, the dairy workers (   ) the cream by hand for nearly an hour until the butter finally formed.",
        "choices": ["swirled", "fraternized", "beguiled", "churned"],
        "answerIndex": 3,
        "translation": "木のかい棒を使い、酪農場の作業員たちは1時間近く手作業でクリームをかき回し、バターになるまで固くした。",
    },
    {
        "stem": "Decades of civil war (   ) a country that had once exported grain to its neighbors.",
        "choices": ["impoverished", "tilted", "accrued", "ruminated"],
        "answerIndex": 0,
        "translation": "数十年に及ぶ内戦は、かつて近隣諸国に穀物を輸出していた国を貧困に陥れた。",
    },
    {
        "stem": "It is (   ) that every passenger be accounted for before the ferry leaves the dock.",
        "choices": ["astronomical", "satirical", "acrimonious", "imperative"],
        "answerIndex": 3,
        "translation": "フェリーが埠頭を離れる前に全乗客の所在を確認することが絶対に必要である。",
    },
    {
        "stem": "After weeks of hostile exchanges, the minister adopted a (   ) tone and invited the union leaders back to the negotiating table.",
        "choices": ["derelict", "perfunctory", "conciliatory", "pervasive"],
        "answerIndex": 2,
        "translation": "何週間もの敵対的なやり取りの後、大臣は融和的な口調をとり、組合の指導者たちを交渉の席に呼び戻した。",
    },
    {
        "stem": "A (   ) technician noticed the tiny crack and grounded the aircraft before its next flight.",
        "choices": ["venerable", "cognizant", "equitable", "conscientious"],
        "answerIndex": 3,
        "translation": "実直な整備士が小さな亀裂に気づき、次の飛行の前にその航空機を運航停止にした。",
    },
    {
        "stem": "Too (   ) to raise his hand in class, Owen wrote his questions in the margin instead.",
        "choices": ["diffident", "antagonistic", "brash", "venomous"],
        "answerIndex": 0,
        "translation": "自信がなくて授業中に手を挙げられず、オーウェンは代わりに余白に質問を書いた。",
    },
    {
        "stem": "The industry was still (   ) in 1995, when there were fewer than a dozen firms worldwide.",
        "choices": ["stocky", "nascent", "feasible", "commensurate"],
        "answerIndex": 1,
        "translation": "その産業は1995年にはまだ生まれたばかりで、世界中でも十数社にも満たなかった。",
    },
    {
        "stem": "The treaty was the most (   ) step in the region's modern history, ending a conflict that had lasted three generations.",
        "choices": ["legible", "jocular", "facetious", "momentous"],
        "answerIndex": 3,
        "translation": "その条約は3世代にわたって続いた紛争を終わらせる、その地域の近代史で最も重大な一歩だった。",
    },
    {
        "stem": "For three years the cause of the outbreak hovered (   ) beyond the reach of investigators, despite intensive laboratory work.",
        "choices": ["abysmally", "elusively", "forlornly", "nominally"],
        "answerIndex": 1,
        "translation": "集中的な実験室での作業にもかかわらず、その集団感染の原因は3年間、捉えどころなく調査員の手の届かないところにあり続けた。",
    },
    {
        "stem": "Public anger at the long water shortage (   ) into daily demonstrations outside the regional headquarters.",
        "choices": ["kicked in", "muddled through", "ironed out", "spilled over"],
        "answerIndex": 3,
        "translation": "水不足への怒りは、地域本部の外での連日のデモにまで波及した。",
    },
    {
        "stem": "The family (   ) heating all winter so that they could afford the trip in August.",
        "choices": ["vouched for", "scrimped on", "nailed down", "ramped up"],
        "answerIndex": 1,
        "translation": "その家族は8月の旅行の費用をまかなうため、冬中ずっと暖房を切り詰めた。",
    },
    {
        "stem": "The medical council (   ) the surgeon after finding that he had falsified his qualifications.",
        "choices": ["washed out", "locked away", "struck off", "loused up"],
        "answerIndex": 2,
        "translation": "医療評議会は、その外科医が資格を偽っていたと認定して彼を登録から抹消した。",
    },
    {
        "stem": "He (   ) the young investors for months, promising returns that his fund could never deliver.",
        "choices": ["railed against", "pepped up", "led on", "stowed away"],
        "answerIndex": 2,
        "translation": "彼は自分のファンドには到底出せない利回りを約束して、若い投資家たちを何か月もだまし続けた。",
    },
]


DETAILS = {
    # Q1
    "blotch": ("しみ、斑点", "名詞", "A dark blotch of ink spread across the corner of the manuscript.", "インクの黒いしみが原稿の隅に広がった。"),
    "clique": ("徒党、閉鎖的な仲間内の集団", "名詞", "A tight clique of veterans controlled every committee in the club.", "ベテランたちの結束した閉鎖的な集団が、そのクラブのあらゆる委員会を支配していた。"),
    "pinnacle": ("頂点、絶頂", "名詞", "Winning the tournament marked the pinnacle of her long career.", "その大会での優勝は彼女の長い経歴の頂点を示すものだった。"),
    "bounty": ("報奨金、豊富な恵み", "名詞", "The government offered a bounty for every rat brought to the depot.", "政府は集積所へ持ち込まれたネズミ1匹ごとに報奨金を出した。"),
    # Q2
    "prelate": ("高位聖職者", "名詞", "A visiting prelate presided over the ceremony in the cathedral.", "訪問中の高位聖職者が大聖堂での式典を執り行った。"),
    "farce": ("茶番、ばかげた出来事", "名詞", "The election became a farce once the opposition candidates withdrew.", "野党候補が撤退すると、その選挙は茶番になった。"),
    "offshoot": ("派生したもの、分派", "名詞", "The research center began as an offshoot of a small engineering department.", "その研究センターは小さな工学部から派生したものとして始まった。"),
    "platitude": ("決まり文句、陳腐な言葉", "名詞", "The speech offered nothing but a platitude about hard work and patience.", "その演説は勤勉と忍耐についての決まり文句以外に何も示さなかった。"),
    # Q3
    "caucus": ("党員集会、幹部会", "名詞", "The caucus lasted four hours before a single nominee emerged.", "その党員集会は候補者が1人に絞られるまで4時間続いた。"),
    "testament": ("証、あかし", "名詞", "The restored bridge stands as a testament to the engineers' patience.", "修復された橋は技術者たちの忍耐の証として建っている。"),
    "juncture": ("(重要な)時点、局面", "名詞", "At this juncture, withdrawing the product would cost more than fixing it.", "この段階では、製品を回収するほうが修理するより費用がかかるだろう。"),
    "enmity": ("敵意、憎しみ", "名詞", "Long-standing enmity between the two villages faded after the flood.", "2つの村の間の長年の敵意は、洪水の後に薄れていった。"),
    # Q4
    "periphery": ("周辺部、外縁", "名詞", "New housing appeared on the periphery of the city throughout the decade.", "その10年を通じて、市の周辺部に新しい住宅が現れた。"),
    "deferral": ("延期、猶予", "名詞", "The bank agreed to a six-month deferral of the couple's mortgage payments.", "銀行はその夫婦の住宅ローン返済を6か月猶予することに同意した。"),
    "endowment": ("寄付基金", "名詞", "Income from the endowment covers a third of the museum's running costs.", "寄付基金からの収入がその博物館の運営費の3分の1を賄っている。"),
    "commotion": ("騒動、騒ぎ", "名詞", "A commotion in the corridor interrupted the examination for several minutes.", "廊下での騒ぎが試験を数分間中断させた。"),
    # Q5
    "genealogy": ("家系、系譜", "名詞", "The library holds records useful for anyone tracing a local genealogy.", "その図書館は地元の家系をたどる人に有用な記録を所蔵している。"),
    "propensity": ("傾向、性癖", "名詞", "The breed has a propensity to bark at anything that moves.", "その犬種は動くものに何でも吠える傾向がある。"),
    "extrovert": ("外向的な人", "名詞", "As an extrovert, he found the months of remote work unexpectedly draining.", "外向的な人である彼にとって、数か月の在宅勤務は思いのほか消耗するものだった。"),
    "contention": ("主張、論争", "名詞", "It is the union's contention that the safety rules were ignored.", "安全規則が無視されたというのが労働組合の主張である。"),
    # Q6
    "reformation": ("改革、改善", "名詞", "The prison's reformation of its training program reduced repeat offenses.", "その刑務所による訓練計画の改革は再犯を減らした。"),
    "socialite": ("社交界の名士", "名詞", "The magazine profiled a socialite who had funded three city galleries.", "その雑誌は市内の3つの画廊に資金を出した社交界の名士を特集した。"),
    "fugitive": ("逃亡者", "名詞", "The fugitive was recognized by a hotel clerk in a coastal town.", "その逃亡者は沿岸の町のホテル従業員に気づかれた。"),
    "cavity": ("虫歯、空洞", "名詞", "An untreated cavity can eventually damage the nerve inside a tooth.", "治療されない虫歯は最終的に歯の内部の神経を傷つけることがある。"),
    # Q7
    "trance": ("恍惚状態、うっとりした状態", "名詞", "The drumming put several dancers into something close to a trance.", "その太鼓の響きは何人かの踊り手をほとんど恍惚状態に近い状態にした。"),
    "upstart": ("成り上がり者、新興勢力", "名詞", "An upstart from outside the industry now sells more units than either giant.", "業界外から来た新興企業が、今ではどちらの大手よりも多く販売している。"),
    "velocity": ("速度、速さ", "名詞", "Engineers calculated the velocity of the falling weight from the video footage.", "技術者たちは映像から落下する重りの速度を計算した。"),
    "ember": ("燃えさし、残り火", "名詞", "A single ember from the campfire started the blaze on the hillside.", "たき火からの1つの燃えさしが斜面での大火を引き起こした。"),
    # Q8
    "defaulted": ("(債務を)履行しなかった", "動詞", "The borrower defaulted after the interest rate doubled within a year.", "1年のうちに金利が倍になった後、その借り手は返済不履行に陥った。"),
    "revitalized": ("再活性化させた", "動詞", "A new tram line revitalized the neglected district within three years.", "新しい路面電車の路線は3年のうちに寂れた地区を再生させた。"),
    "gargled": ("うがいをした", "動詞", "He gargled with warm salt water twice a day for his sore throat.", "彼は喉の痛みのために1日2回、温かい塩水でうがいをした。"),
    "amplified": ("増幅した、拡大した", "動詞", "Social media amplified a rumor that had begun in a single message.", "ソーシャルメディアは1通のメッセージから始まったうわさを増幅させた。"),
    # Q9
    "abated": ("弱まった、和らいだ", "動詞", "The wind finally abated shortly before dawn on the third day.", "風は3日目の夜明け前になってようやく弱まった。"),
    "emancipated": ("解放した", "動詞", "The reform emancipated tenant farmers who had worked the land for generations.", "その改革は何世代もその土地を耕してきた小作農を解放した。"),
    "distorted": ("ゆがめた", "動詞", "The cheap lens distorted the edges of every photograph he took.", "その安価なレンズは彼が撮るすべての写真の端をゆがめた。"),
    "delineated": ("(輪郭を)明確に示した", "動詞", "The contract delineated the duties of each party in careful detail.", "その契約は各当事者の義務を注意深く詳細に明示した。"),
    # Q10
    "liquidated": ("(資産を)処分した、清算した", "動詞", "The family liquidated its remaining shares to pay the inheritance tax.", "その一家は相続税を払うために残りの株式を処分した。"),
    "floundered": ("もがいた、まごついた", "動詞", "The team floundered in the second half and lost its early advantage.", "そのチームは後半にもたつき、序盤の優位を失った。"),
    "whimpered": ("めそめそ泣いた、くんくん鳴いた", "動詞", "The injured fox whimpered quietly until the rescue team arrived.", "けがをしたキツネは救助隊が到着するまで静かにくんくん鳴いていた。"),
    "pecked": ("(くちばしで)つついた", "動詞", "The hens pecked at the grain scattered across the yard.", "めんどりたちは庭にまかれた穀物をつついた。"),
    # Q11
    "sanitized": ("消毒した、無害化した", "動詞", "The crew sanitized the aircraft cabin between every scheduled flight.", "乗務員は定期便のたびに機内を消毒した。"),
    "rejuvenated": ("若返らせた、活気づけた", "動詞", "A week by the sea rejuvenated the exhausted researchers completely.", "海辺での1週間は疲れ切った研究者たちをすっかり元気にした。"),
    "bartered": ("物々交換した", "動詞", "Villagers bartered eggs and firewood when banknotes became worthless.", "紙幣が価値を失うと、村人たちは卵とまきを物々交換した。"),
    "mustered": ("(勇気などを)奮い起こした、召集した", "動詞", "She mustered enough courage to speak at the shareholders' meeting.", "彼女は株主総会で発言するのに十分な勇気を奮い起こした。"),
    # Q12
    "cringed": ("身がすくんだ、縮こまった", "動詞", "He cringed at the sound of his own recorded voice.", "彼は録音された自分の声を聞いて思わず身がすくんだ。"),
    "orchestrated": ("画策した、周到に組織した", "動詞", "A handful of executives orchestrated the takeover over several quiet months.", "少数の幹部が数か月かけてひそかにその買収を画策した。"),
    "vanquished": ("打ち負かした", "動詞", "The general vanquished a much larger army on the frozen river.", "その将軍は凍った川の上ではるかに大きな軍を打ち負かした。"),
    "abducted": ("誘拐した、拉致した", "動詞", "Kidnappers abducted the diplomat's driver but released him unharmed.", "誘拐犯は外交官の運転手を拉致したが、無傷で解放した。"),
    # Q13
    "swirled": ("渦を巻いた", "動詞", "Autumn leaves swirled around the courtyard whenever the gate opened.", "門が開くたびに秋の落ち葉が中庭を渦巻いた。"),
    "fraternized": ("親しく交わった", "動詞", "Officers who fraternized with residents of the occupied town faced disciplinary action.", "占領された町の住民と親しく交わった将校たちは懲戒処分を受けた。"),
    "beguiled": ("だました、魅了した", "動詞", "The salesman beguiled the elderly couple into signing a costly contract.", "そのセールスマンは老夫婦をだまして高額な契約に署名させた。"),
    "churned": ("激しくかき回した、泡立てた", "動詞", "The ferry's propellers churned the muddy water of the estuary.", "フェリーのプロペラが河口の濁った水を激しくかき回した。"),
    # Q14
    "impoverished": ("貧困に陥れた", "動詞", "The blight impoverished farming communities across the entire province.", "その病害は州全体の農村を貧困に陥れた。"),
    "tilted": ("傾けた、傾いた", "動詞", "He tilted the lamp so that the light fell on the map.", "彼は明かりが地図に当たるようにランプを傾けた。"),
    "accrued": ("(利息などが)生じた、蓄積した", "動詞", "Interest accrued on the unpaid balance at four percent annually.", "未払い残高には年4パーセントの利息が生じた。"),
    "ruminated": ("じっくり考えた、反すうした", "動詞", "She ruminated on the offer for a week before turning it down.", "彼女はその申し出を1週間じっくり考えてから断った。"),
    # Q15
    "imperative": ("絶対に必要な、緊急の", "形容詞", "Regular inspection is imperative for equipment used at these depths.", "この深度で使われる機器には定期点検が絶対に必要である。"),
    "astronomical": ("天文学的な、莫大な", "形容詞", "Rebuilding the stadium would carry an astronomical price for a small city.", "その競技場の建て替えは小さな市にとって天文学的な費用を伴うだろう。"),
    "satirical": ("風刺的な", "形容詞", "The magazine published a satirical cartoon about the new parking rules.", "その雑誌は新しい駐車規則についての風刺漫画を掲載した。"),
    "acrimonious": ("辛辣な、とげとげしい", "形容詞", "Their acrimonious dispute over the boundary lasted eleven years.", "境界をめぐる彼らの辛辣な争いは11年続いた。"),
    # Q16
    "derelict": ("見捨てられた、荒廃した", "形容詞", "Artists moved into a derelict warehouse near the old canal.", "芸術家たちは古い運河の近くの廃れた倉庫に移り住んだ。"),
    "perfunctory": ("おざなりの、通り一遍の", "形容詞", "The inspector gave the boiler a perfunctory glance and signed the form.", "検査官はボイラーをおざなりに一瞥して書類に署名した。"),
    "conciliatory": ("融和的な、なだめるような", "形容詞", "A conciliatory letter from the principal calmed most of the parents.", "校長からの融和的な手紙は保護者の大半を落ち着かせた。"),
    "pervasive": ("広く行き渡った", "形容詞", "Distrust of the census was pervasive in the northern districts.", "国勢調査への不信は北部の地区に広く行き渡っていた。"),
    # Q17
    "conscientious": ("良心的な、実直な", "形容詞", "A conscientious clerk noticed that two invoices had the same number.", "実直な事務員が2枚の請求書に同じ番号があることに気づいた。"),
    "venerable": ("尊敬すべき、由緒ある", "形容詞", "The venerable law firm has occupied the same building since 1878.", "その由緒ある法律事務所は1878年から同じ建物を使っている。"),
    "cognizant": ("認識している、気づいている", "形容詞", "Investors must be fully cognizant of the risks before signing.", "投資家は署名する前にリスクを十分に認識していなければならない。"),
    "equitable": ("公平な、公正な", "形容詞", "The mediator proposed an equitable division of the shared land.", "調停者は共有地の公平な分割を提案した。"),
    # Q18
    "diffident": ("自信のない、内気な", "形容詞", "Too diffident to apply, he let the deadline for the fellowship pass.", "応募するには内気すぎて、彼はその奨学研究員の締め切りを見送った。"),
    "antagonistic": ("敵対的な", "形容詞", "The two departments grew openly antagonistic after the budget was split.", "予算が分割された後、2つの部署は公然と敵対的になった。"),
    "brash": ("生意気な、無遠慮な", "形容詞", "His brash comments at the reception embarrassed the entire delegation.", "歓迎会での彼の無遠慮な発言は代表団全員に恥をかかせた。"),
    "venomous": ("有毒な、悪意に満ちた", "形容詞", "Only two venomous snake species live on the island.", "その島には有毒なヘビは2種しか生息していない。"),
    # Q19
    "stocky": ("ずんぐりした", "形容詞", "A stocky man in a raincoat waited beside the ticket machine.", "レインコートを着たずんぐりした男が券売機のそばで待っていた。"),
    "nascent": ("生まれたばかりの、初期の", "形容詞", "The nascent union had only forty members in its first year.", "生まれたばかりのその労働組合は初年度に組合員が40人しかいなかった。"),
    "feasible": ("実行可能な", "形容詞", "Engineers judged the tunnel route feasible but extremely expensive.", "技術者たちはそのトンネル経路を実行可能だが極めて高額だと判断した。"),
    "commensurate": ("釣り合った、相応の", "形容詞", "The salary offered was hardly commensurate with the responsibilities involved.", "提示された給与は伴う責任にほとんど見合っていなかった。"),
    # Q20
    "legible": ("読みやすい、判読できる", "形容詞", "Only half the inscription is still legible after four centuries.", "4世紀を経て、その碑文は半分しか判読できない。"),
    "jocular": ("冗談好きな、おどけた", "形容詞", "His jocular manner put nervous patients at ease immediately.", "彼のおどけた態度は緊張した患者をすぐに安心させた。"),
    "facetious": ("ふざけた、おどけた", "形容詞", "His facetious reply annoyed the officials who had asked a serious question.", "彼のふざけた返答は、真剣な質問をした当局者たちをいらだたせた。"),
    "momentous": ("重大な、重要な", "形容詞", "The council faced a momentous choice about the future of the harbor.", "議会は港の将来に関する重大な選択に直面した。"),
    # Q21
    "abysmally": ("ひどく、最悪なほどに", "副詞", "The heating system performed abysmally during the coldest week of January.", "その暖房設備は1月の最も寒い週にひどい働きしかしなかった。"),
    "elusively": ("捉えどころなく、巧みに逃れて", "副詞", "The suspect moved elusively between three cities over several months.", "容疑者は数か月かけて3つの都市の間を巧みに逃れながら移動した。"),
    "forlornly": ("寂しげに、わびしく", "副詞", "The empty swing creaked forlornly in the deserted playground.", "誰もいない遊び場で、空のブランコが寂しげにきしんだ。"),
    "nominally": ("名目上は", "副詞", "The territory was nominally independent but relied entirely on foreign troops.", "その地域は名目上は独立していたが、完全に外国軍に依存していた。"),
    # Q22
    "spilled over": ("波及した、あふれ出た", "句動詞", "The dispute spilled over into neighboring towns within a fortnight.", "その争いは2週間のうちに近隣の町にまで波及した。"),
    "kicked in": ("効き始めた、作動し始めた", "句動詞", "The painkiller kicked in about twenty minutes after the injection.", "その鎮痛剤は注射のおよそ20分後に効き始めた。"),
    "muddled through": ("どうにか切り抜けた", "句動詞", "Without a manual, the volunteers muddled through the first weekend somehow.", "手引きもないまま、ボランティアたちは最初の週末をどうにか切り抜けた。"),
    "ironed out": ("(問題を)解決した、調整した", "句動詞", "Negotiators ironed out the last differences shortly before midnight.", "交渉担当者たちは真夜中の少し前に最後の相違点を解決した。"),
    # Q23
    "vouched for": ("(~を)保証した、請け合った", "句動詞", "Her former supervisor vouched for the accuracy of every figure.", "彼女の元上司はすべての数字の正確さを保証した。"),
    "scrimped on": ("(~を)切り詰めた、けちった", "句動詞", "The builder scrimped on insulation, and the owners paid for it later.", "その建築業者は断熱材をけちり、所有者たちが後でその代償を払った。"),
    "nailed down": ("(細部を)確定した", "句動詞", "The committee nailed down the schedule after two long meetings.", "委員会は2回の長い会議の後に日程を確定した。"),
    "ramped up": ("増強した、段階的に強化した", "句動詞", "The factory ramped up production ahead of the holiday season.", "その工場は年末商戦を前に生産を増強した。"),
    # Q24
    "washed out": ("(雨で)流失させた、中止にした", "句動詞", "Heavy rain washed out the bridge on the only road into the valley.", "豪雨がその谷への唯一の道にかかる橋を流失させた。"),
    "locked away": ("しまい込んだ、閉じ込めた", "句動詞", "The curator locked away the fragile manuscripts every evening.", "学芸員は毎晩、壊れやすい写本をしまい込んで施錠した。"),
    "struck off": ("(登録から)除名した、抹消した", "句動詞", "The board struck off two members who had ignored repeated warnings.", "理事会は再三の警告を無視した2人の会員を登録から抹消した。"),
    "loused up": ("台無しにした、しくじった", "句動詞", "A single misplaced decimal loused up the entire quarterly forecast.", "小数点1つの置き違いが四半期の予測全体を台無しにした。"),
    # Q25
    "railed against": ("(~を)激しく非難した", "句動詞", "The columnist railed against the closure of rural post offices.", "そのコラムニストは地方の郵便局の閉鎖を激しく非難した。"),
    "pepped up": ("元気づけた、活気づけた", "句動詞", "A short walk and strong coffee pepped up the whole afternoon shift.", "短い散歩と濃いコーヒーが午後の勤務全体を元気づけた。"),
    "led on": ("(思わせぶりに)だました", "句動詞", "She realized she had been led on when the promised contract never appeared.", "約束された契約が一向に現れず、彼女はだまされていたと気づいた。"),
    "stowed away": ("(こっそり)積み込んだ、しまい込んだ", "句動詞", "The crew found a cat that had stowed away among the cargo.", "乗組員は貨物の間に紛れ込んでいた猫を見つけた。"),
}


CORE_IMAGES = {
    "spilled over": {
        "chain": [
            {"term": "spill", "gloss": "こぼれる"},
            {"term": "over", "gloss": "縁を越えて"},
            {"gloss": "器の縁を越えて外へ流れ出て"},
            {"gloss": "影響が別の領域へ波及する"},
        ],
        "particle": "over",
    },
    "kicked in": {
        "chain": [
            {"term": "kick", "gloss": "蹴る"},
            {"term": "in", "gloss": "作動する側へ入って"},
            {"gloss": "蹴り込まれて仕組みが動き出して"},
            {"gloss": "効き始める、作動し始める"},
        ],
        "particle": "in",
    },
    "muddled through": {
        "chain": [
            {"term": "muddle", "gloss": "ごたごたさせる"},
            {"term": "through", "gloss": "最後まで通り抜けて"},
            {"gloss": "手探りのまま最後まで通り抜けて"},
            {"gloss": "どうにか切り抜ける"},
        ],
    },
    "ironed out": {
        "chain": [
            {"term": "iron", "gloss": "アイロンをかける"},
            {"term": "out", "gloss": "しわを伸ばして解消して"},
            {"gloss": "でこぼこを平らに伸ばして"},
            {"gloss": "問題や相違を解決する"},
        ],
        "particle": "out",
        "particleSense": "resolve",
    },
    "vouched for": {
        "chain": [
            {"term": "vouch", "gloss": "保証する"},
            {"term": "for", "gloss": "その対象を引き受けて"},
            {"gloss": "相手に代わって責任を引き受けて"},
            {"gloss": "~を保証する、請け合う"},
        ],
    },
    "scrimped on": {
        "chain": [
            {"term": "scrimp", "gloss": "切り詰める"},
            {"term": "on", "gloss": "その項目に的を絞って"},
            {"gloss": "特定の費目に的を絞って出費を削って"},
            {"gloss": "~を切り詰める、けちる"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "nailed down": {
        "chain": [
            {"term": "nail", "gloss": "くぎで打ちつける"},
            {"term": "down", "gloss": "動かない位置へ据えて"},
            {"gloss": "揺れていた案を一点へ打ちつけて"},
            {"gloss": "細部を確定する"},
        ],
        "particle": "down",
        "particleSense": "settle",
    },
    "ramped up": {
        "chain": [
            {"term": "ramp", "gloss": "傾斜をつける"},
            {"term": "up", "gloss": "水準を上げて"},
            {"gloss": "坂を上るように水準を段階的に上げて"},
            {"gloss": "増強する"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "washed out": {
        "chain": [
            {"term": "wash", "gloss": "洗い流す"},
            {"term": "out", "gloss": "外へ押し流して取り除いて"},
            {"gloss": "水の力でその場から押し流して"},
            {"gloss": "流失させる、中止に追い込む"},
        ],
        "particle": "out",
        "particleSense": "remove",
    },
    "locked away": {
        "chain": [
            {"term": "lock", "gloss": "鍵をかける"},
            {"term": "away", "gloss": "手の届かない所へ離して"},
            {"gloss": "鍵をかけて人の手が届かない所へ離して"},
            {"gloss": "しまい込む、閉じ込める"},
        ],
        "particle": "away",
    },
    "struck off": {
        "chain": [
            {"term": "strike", "gloss": "線を引いて消す"},
            {"term": "off", "gloss": "名簿から切り離して"},
            {"gloss": "名前に線を引いて名簿から切り離して"},
            {"gloss": "登録から抹消する"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "loused up": {
        "chain": [
            {"term": "louse", "gloss": "しらみをたからせる"},
            {"term": "up", "gloss": "状態を乱して"},
            {"gloss": "全体に手を入れて台無しの状態にして"},
            {"gloss": "台無しにする、しくじる"},
        ],
        "particle": "up",
        "particleSense": "disrupt",
    },
    "railed against": {
        "chain": [
            {"term": "rail", "gloss": "ののしる"},
            {"term": "against", "gloss": "対象に向かい合って"},
            {"gloss": "相手に正面から言葉をぶつけて"},
            {"gloss": "~を激しく非難する"},
        ],
    },
    "pepped up": {
        "chain": [
            {"term": "pep", "gloss": "元気を与える"},
            {"term": "up", "gloss": "勢いを高めて"},
            {"gloss": "沈んだ調子を上向きに引き上げて"},
            {"gloss": "元気づける"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "led on": {
        "chain": [
            {"term": "lead", "gloss": "導く"},
            {"term": "on", "gloss": "その先へ引っぱり続けて"},
            {"gloss": "期待を持たせたまま先へ引っぱり続けて"},
            {"gloss": "思わせぶりにだます"},
        ],
        "particle": "on",
        "particleSense": "continue",
    },
    "stowed away": {
        "chain": [
            {"term": "stow", "gloss": "詰め込む"},
            {"term": "away", "gloss": "目につかない所へ離して"},
            {"gloss": "荷物の奥の目につかない所へ詰め込んで"},
            {"gloss": "こっそり積み込む、しまい込む"},
        ],
        "particle": "away",
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
        raise ValueError("模試第11回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-11 割り当てに従う",
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
