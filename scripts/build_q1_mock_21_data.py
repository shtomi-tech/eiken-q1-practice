"""英検1級 模試第21回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-21 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-21"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "Every page of the report carries a (   ) stating that the figures are provisional.",
        "choices": ["disclaimer", "ramification", "stowage", "innuendo"],
        "answerIndex": 0,
        "translation": "その報告書のどのページにも、数値が暫定的なものであると記した免責事項が付されている。",
    },
    {
        "stem": "The polished brass had lost none of its (   ) after eighty years in the hallway.",
        "choices": ["misgiving", "yardstick", "debacle", "luster"],
        "answerIndex": 3,
        "translation": "磨かれた真鍮は玄関ホールでの80年を経ても、その光沢をまったく失っていなかった。",
    },
    {
        "stem": "The (   ) is far better than it was even ten years ago for this type of injury.",
        "choices": ["paradigm", "exhilaration", "prognosis", "doctrine"],
        "answerIndex": 2,
        "translation": "この種のけがについての予後は、10年前と比べてさえはるかに良好である。",
    },
    {
        "stem": "The court case acted as a (   ) for reforms that had been discussed for decades.",
        "choices": ["volition", "catalyst", "dissidence", "finesse"],
        "answerIndex": 1,
        "translation": "その裁判は、何十年も議論されてきた改革の触媒として働いた。",
    },
    {
        "stem": "Clinical trials showed the (   ) of the vaccine falling steadily after about eight months.",
        "choices": ["efficacy", "regimen", "foliage", "timidity"],
        "answerIndex": 0,
        "translation": "臨床試験は、そのワクチンの有効性がおよそ8か月後から着実に低下することを示した。",
    },
    {
        "stem": "Engineers were asked to report on the (   ) of a tunnel beneath the estuary.",
        "choices": ["tinge", "impeachment", "contraband", "feasibility"],
        "answerIndex": 3,
        "translation": "技術者たちは、河口の下にトンネルを掘る実現可能性について報告するよう求められた。",
    },
    {
        "stem": "The (   ) of these rare plants depends entirely on a single species of moth.",
        "choices": ["impudence", "acquittal", "propagation", "tyranny"],
        "answerIndex": 2,
        "translation": "これらの希少な植物の繁殖は、たった1種のガに完全に依存している。",
    },
    {
        "stem": "New arrivals were encouraged to (   ) with local residents rather than keep to themselves.",
        "choices": ["precipitate", "mingle", "brandish", "elude"],
        "answerIndex": 1,
        "translation": "新しく来た人たちは、内にこもるのではなく地元の住民と交流するよう促された。",
    },
    {
        "stem": "Other laboratories were completely unable to (   ) the result reported in the original paper.",
        "choices": ["replicate", "indulge", "inundate", "contrive"],
        "answerIndex": 0,
        "translation": "他の研究所は、元の論文で報告された結果をまったく再現できなかった。",
    },
    {
        "stem": "Neighboring states gradually came to (   ) the deep harbor that had made the city rich.",
        "choices": ["cripple", "espouse", "heave", "covet"],
        "answerIndex": 3,
        "translation": "近隣の諸国は次第に、その都市を豊かにした深い港を欲しがるようになった。",
    },
    {
        "stem": "Customs officers may (   ) any vehicle that has been substantially altered without official approval.",
        "choices": ["embellish", "adjoin", "impound", "hamper"],
        "answerIndex": 2,
        "translation": "税関職員は、正式な承認なく大幅に改造された車両をいかなるものでも押収できる。",
    },
    {
        "stem": "Three separate studies now (   ) the old claim that the practice actually improves recovery.",
        "choices": ["engross", "refute", "jiggle", "ensue"],
        "answerIndex": 1,
        "translation": "現在では3つの別々の研究が、その方法が実際に回復を改善するという古い主張に反証している。",
    },
    {
        "stem": "Rats began to (   ) the lower floors as soon as the building stood empty.",
        "choices": ["infest", "inflict", "incubate", "squash"],
        "answerIndex": 0,
        "translation": "建物が空になるとすぐに、ネズミが下の階に大量発生し始めた。",
    },
    {
        "stem": "The club was (   ) to the second division after a single disastrous season last year.",
        "choices": ["verified", "dazzled", "squabbled", "relegated"],
        "answerIndex": 3,
        "translation": "そのクラブは昨年の1シーズンの惨敗の後、2部へ降格させられた。",
    },
    {
        "stem": "Anything (   ) has to be moved into the cold store within two hours of delivery.",
        "choices": ["apolitical", "strenuous", "perishable", "prophetic"],
        "answerIndex": 2,
        "translation": "傷みやすいものはすべて、納品から2時間以内に冷蔵庫へ移さなければならない。",
    },
    {
        "stem": "The article was criticized as (   ) rather than analytical, since it read like a campaign speech for the plan.",
        "choices": ["complacent", "fervent", "laborious", "ludicrous"],
        "answerIndex": 1,
        "translation": "その記事は計画の応援演説のように読めたため、分析的というより熱に浮かされたものだと批判された。",
    },
    {
        "stem": "The hall is (   ), with gilded columns and a ceiling covered in painted clouds.",
        "choices": ["ostentatious", "antiseptic", "infantile", "omniscient"],
        "answerIndex": 0,
        "translation": "その広間は金箔の柱と雲を描いた天井を備えた、これ見よがしに華美なつくりである。",
    },
    {
        "stem": "A (   ) editor would have noticed that the two dates cannot both be correct.",
        "choices": ["inquisitive", "irascible", "exquisite", "discerning"],
        "answerIndex": 3,
        "translation": "見識のある編集者なら、その2つの日付が両方とも正しいはずがないと気づいただろう。",
    },
    {
        "stem": "The dispute has already proved (   ), and three separate mediators have withdrawn from it.",
        "choices": ["shoddy", "furtive", "intractable", "despondent"],
        "answerIndex": 2,
        "translation": "その争いはすでに手に負えないものであることが分かり、3人の調停者が手を引いている。",
    },
    {
        "stem": "The tribunal described the long delay as (   ) and awarded the family their full costs.",
        "choices": ["adept", "reprehensible", "volatile", "prescient"],
        "answerIndex": 1,
        "translation": "審判所はその長い遅延を非難に値するものと述べ、その一家に費用の全額を認めた。",
    },
    {
        "stem": "The appeal was (   ) rejected without a hearing, and the family were given no chance to reply.",
        "choices": ["summarily", "wryly", "conspicuously", "warily"],
        "answerIndex": 0,
        "translation": "その上訴は審理もないまま即座に退けられ、その一家には反論の機会も与えられなかった。",
    },
    {
        "stem": "The roof of the old barn finally (   ) under the weight of the wet snow.",
        "choices": ["fired away", "mulled over", "blew away", "caved in"],
        "answerIndex": 3,
        "translation": "古い納屋の屋根は湿った雪の重みでついに崩れ落ちた。",
    },
    {
        "stem": "The whole street was (   ) with lanterns for the three nights of the festival.",
        "choices": ["cracked up", "rolled in", "decked out", "played down"],
        "answerIndex": 2,
        "translation": "通り全体が祭りの3晩の間、提灯で飾り立てられていた。",
    },
    {
        "stem": "The family (   ) on one small pension for the whole of that difficult winter.",
        "choices": ["hunkered down", "scraped by", "limbered up", "snapped off"],
        "answerIndex": 1,
        "translation": "その一家はその厳しい冬の間ずっと、わずかな年金1つでどうにか食いつないだ。",
    },
    {
        "stem": "The crew (   ) the storm in a sheltered bay and reached port two days late.",
        "choices": ["rode out", "jockeyed for", "buttered up", "pored over"],
        "answerIndex": 0,
        "translation": "乗組員は入り江に避難して嵐を乗り切り、2日遅れで港に着いた。",
    },
]


DETAILS = {
    # Q1
    "disclaimer": ("免責事項、権利放棄", "名詞", "A short disclaimer appears at the foot of every page.", "各ページの下部に短い免責事項が記載されている。"),
    "ramification": ("(思わぬ)影響、派生的な結果", "名詞", "One ramification of the ruling was an immediate rise in premiums.", "その判決の一つの余波は、保険料の即座の上昇だった。"),
    "stowage": ("収納、積み込み", "名詞", "Stowage below deck is limited to four crates per passenger.", "甲板下の収納は乗客1人につき4箱までに制限されている。"),
    "innuendo": ("当てこすり、ほのめかし", "名詞", "The article relies on innuendo rather than on any documented fact.", "その記事は記録された事実ではなく当てこすりに頼っている。"),
    # Q2
    "misgiving": ("不安、疑念", "名詞", "She had one serious misgiving about signing the lease.", "彼女はその賃貸契約に署名することについて一つ重大な不安を抱いていた。"),
    "luster": ("光沢、輝き", "名詞", "The varnish restores the luster of the wood without darkening it at all.", "そのニスは木材を暗くすることなく光沢を取り戻す。"),
    "yardstick": ("判断基準、尺度", "名詞", "Attendance is a poor yardstick for the value of a museum.", "入館者数は博物館の価値を測る尺度としては不十分である。"),
    "debacle": ("大失敗、総崩れ", "名詞", "The launch was a debacle that cost the company two years.", "その発売は会社に2年を失わせる大失敗だった。"),
    # Q3
    "paradigm": ("枠組み、模範", "名詞", "The discovery forced a new paradigm on the whole field.", "その発見は分野全体に新しい枠組みを強いた。"),
    "exhilaration": ("爽快感、高揚", "名詞", "The exhilaration of the first descent stayed with him for weeks.", "最初の滑降の爽快感は何週間も彼の中に残った。"),
    "prognosis": ("予後、見通し", "名詞", "The prognosis depends heavily on how early the condition is found.", "予後はその病気がどれだけ早く見つかるかに大きく左右される。"),
    "doctrine": ("教義、主義", "名詞", "The doctrine was not formally abandoned until the 1970s.", "その主義が正式に放棄されたのは1970年代になってからだった。"),
    # Q4
    "volition": ("自由意志、意欲", "名詞", "He left the company of his own volition and without complaint.", "彼は不平も言わず、自らの意志でその会社を去った。"),
    "dissidence": ("反体制的な意見、異議", "名詞", "Open dissidence was punished severely throughout those difficult years.", "あの時代、公然たる反体制の言動は厳しく罰された。"),
    "finesse": ("巧妙さ、手際のよさ", "名詞", "The repair was carried out with remarkable finesse and very little noise.", "その修理は目覚ましい手際のよさで行われた。"),
    "catalyst": ("触媒、きっかけ", "名詞", "The photograph became a catalyst for a national conversation.", "その写真は全国的な議論のきっかけとなった。"),
    # Q5
    "efficacy": ("有効性、効き目", "名詞", "The efficacy of the treatment varies quite widely between different age groups.", "その治療の有効性は年齢層によって大きく異なる。"),
    "regimen": ("(治療や運動の)規定計画", "名詞", "Patients follow a strict regimen of daily exercise and careful diet.", "患者は運動と食事の厳格な計画に従う。"),
    "foliage": ("葉、群葉", "名詞", "The dense foliage hides the house almost completely during the summer.", "夏には密生した葉がその家をすっかり隠してしまう。"),
    "timidity": ("臆病、内気", "名詞", "His timidity in large meetings was often mistaken for indifference.", "会議での彼の内気さは無関心と取り違えられた。"),
    # Q6
    "tinge": ("かすかな色合い、気味", "名詞", "There was a tinge of green in the winter sky that evening.", "その晩の冬空にはかすかな緑の色合いがあった。"),
    "impeachment": ("弾劾", "名詞", "The impeachment proceedings in the senate lasted almost six months.", "その弾劾手続きは6か月近く続いた。"),
    "feasibility": ("実現可能性", "名詞", "A full feasibility study will take at least eighteen months to complete.", "実現可能性の調査には少なくとも18か月かかるだろう。"),
    "contraband": ("密輸品、禁制品", "名詞", "Officers found contraband hidden inside the fuel tank of the van.", "職員は燃料タンクの中に隠された密輸品を発見した。"),
    # Q7
    "impudence": ("厚かましさ、生意気", "名詞", "He had the impudence to ask for a refund on a used ticket.", "彼は使用済みの切符の払い戻しを求める厚かましさを持っていた。"),
    "acquittal": ("無罪判決", "名詞", "The acquittal came after a retrial that had lasted eleven weeks.", "無罪判決は11週間続いた再審の後に下された。"),
    "tyranny": ("圧政、専制", "名詞", "The pamphlet describes in detail the tyranny of the previous regime.", "その小冊子は前政権の圧政を描いている。"),
    "propagation": ("繁殖、普及", "名詞", "Propagation from cuttings is much quicker than growing these shrubs from seed.", "挿し木による繁殖は種から育てるより早い。"),
    # Q8
    "mingle": ("交ざる、交流する", "動詞", "Guests were invited to mingle in the garden before dinner.", "客たちは夕食前に庭で歓談するよう促された。"),
    "precipitate": ("引き起こす、早める", "動詞", "A minor accident can precipitate a much larger dispute.", "小さな事故がはるかに大きな争いを引き起こすことがある。"),
    "brandish": ("振り回す、誇示する", "動詞", "It is an offense to brandish any blade in a public place.", "公共の場で刃物を振り回すことは犯罪である。"),
    "elude": ("巧みに逃れる、思い出せない", "動詞", "The name continued to elude him for the rest of the evening.", "その名前はその晩ずっと彼の記憶から逃れ続けた。"),
    # Q9
    "indulge": ("(欲求を)満たす、甘やかす", "動詞", "He allows himself to indulge in one good cigar a month.", "彼は月に1本だけ上等な葉巻を楽しむことを自分に許している。"),
    "inundate": ("殺到させる、水浸しにする", "動詞", "A single broadcast can inundate the office with enquiries.", "1回の放送が事務所を問い合わせで埋め尽くすことがある。"),
    "replicate": ("再現する、複製する", "動詞", "Students must replicate the experiment twice before writing it up.", "学生は報告書を書く前に実験を2回再現しなければならない。"),
    "contrive": ("たくらむ、工夫して作る", "動詞", "They managed to contrive a shelter from two sheets of plastic.", "彼らは2枚のビニールシートでどうにか避難所をこしらえた。"),
    # Q10
    "cripple": ("機能を損なう、不自由にする", "動詞", "A strike at the port could cripple the island's whole economy.", "港でのストライキは島の経済全体を麻痺させかねない。"),
    "espouse": ("(主義を)支持する、奉じる", "動詞", "Few politicians openly espouse a policy of higher taxes.", "増税政策を公然と支持する政治家はほとんどいない。"),
    "heave": ("持ち上げる、投げる", "動詞", "It took four of them to heave the crate onto the platform.", "その木箱をホームへ持ち上げるのに4人がかりだった。"),
    "covet": ("切望する、欲しがる", "動詞", "Collectors covet the early editions with the misprinted cover.", "収集家は誤植のある表紙の初期版を切望する。"),
    # Q11
    "embellish": ("飾る、脚色する", "動詞", "He tends to embellish the story a little more each year.", "彼は毎年その話を少しずつ脚色する傾向がある。"),
    "adjoin": ("隣接する", "動詞", "The two gardens adjoin along a low stone wall.", "その2つの庭は低い石垣に沿って隣接している。"),
    "hamper": ("妨げる、邪魔する", "動詞", "Deep snow will hamper the search for at least another day.", "深い雪は少なくともあと1日は捜索を妨げるだろう。"),
    "impound": ("押収する、留置する", "動詞", "Police may impound a vehicle left blocking the fire exit.", "警察は非常口をふさいで放置された車両を押収できる。"),
    # Q12
    "engross": ("夢中にさせる、没頭させる", "動詞", "A good mystery can engross even a reluctant reader.", "よくできた推理小説は気の進まない読者さえ夢中にさせる。"),
    "jiggle": ("小刻みに揺らす", "動詞", "You have to jiggle the handle before the door will close.", "扉が閉まる前に取っ手を小刻みに動かさなければならない。"),
    "squash": ("押しつぶす、押し込む", "動詞", "Try not to squash the fruit at the bottom of the basket.", "かごの底の果物を押しつぶさないようにしなさい。"),
    "refute": ("反証する、論破する", "動詞", "It takes only one counterexample to refute the general claim.", "その一般的な主張を覆すには反例が1つあれば足りる。"),
    # Q13
    "inflict": ("(苦痛などを)与える", "動詞", "Storms of this size inflict damage on every harbor along the coast.", "この規模の嵐は沿岸のあらゆる港に被害を与える。"),
    "incubate": ("(卵を)抱く、培養する", "動詞", "The birds incubate the eggs for about nineteen days.", "その鳥は19日ほど卵を温める。"),
    "ensue": ("続いて起こる", "動詞", "A long silence will usually ensue after such a question.", "そのような質問の後には、たいてい長い沈黙が続く。"),
    "infest": ("(害虫などが)はびこる", "動詞", "Beetles infest the timber if it is stored while still damp.", "湿ったまま保管されると、甲虫がその木材にはびこる。"),
    # Q14
    "verified": ("検証した、確認した", "動詞", "Two auditors verified every entry in the ledger.", "2人の監査人が元帳のすべての記入を確認した。"),
    "dazzled": ("目をくらませた、感嘆させた", "動詞", "Low sunlight dazzled drivers on the eastbound carriageway.", "低い日差しが東行き車線の運転者の目をくらませた。"),
    "squabbled": ("つまらぬ口論をした", "動詞", "The children squabbled over the last piece of cake.", "子どもたちは最後のケーキ1切れをめぐって口論した。"),
    "relegated": ("降格させた、追いやった", "動詞", "The painting was relegated to a corridor on the top floor.", "その絵は最上階の廊下へ追いやられた。"),
    # Q15
    "perishable": ("傷みやすい、腐りやすい", "形容詞", "Perishable goods travel in a separate refrigerated van.", "傷みやすい品物は別の冷蔵車で運ばれる。"),
    "apolitical": ("政治に無関心な、非政治的な", "形容詞", "The society is strictly apolitical and takes no position on elections.", "その団体は厳密に非政治的で、選挙について立場を取らない。"),
    "strenuous": ("骨の折れる、精力的な", "形容詞", "Patients should avoid strenuous exercise for six weeks.", "患者は6週間、激しい運動を避けるべきである。"),
    "prophetic": ("預言的な、先を見通した", "形容詞", "His warning about the bridge proved prophetic within a year.", "橋についての彼の警告は1年のうちに預言的だったと分かった。"),
    # Q16
    "complacent": ("独りよがりの、現状に安住した", "形容詞", "The team grew complacent after four easy victories.", "そのチームは4度の楽な勝利の後、現状に安住するようになった。"),
    "laborious": ("骨の折れる、手間のかかる", "形容詞", "Copying the register by hand was a laborious business.", "登録簿を手で書き写すのは手間のかかる仕事だった。"),
    "ludicrous": ("ばかげた、こっけいな", "形容詞", "The proposed timetable was ludicrous for a crew of only four.", "提案された日程は4人だけの乗組員にはばかげたものだった。"),
    "fervent": ("熱烈な、熱心な", "形容詞", "He was a fervent supporter of the canal project from the start.", "彼は当初からその運河計画の熱烈な支持者だった。"),
    # Q17
    "ostentatious": ("これ見よがしの、派手な", "形容詞", "The house is comfortable and welcoming without ever being ostentatious.", "その家はこれ見よがしでないながらも快適である。"),
    "antiseptic": ("殺菌の、消毒の", "形容詞", "Nurses clean the area with an antiseptic wipe first.", "看護師はまず消毒用の拭き取り布でその部分を清める。"),
    "infantile": ("幼稚な、子どもじみた", "形容詞", "The argument quickly descended into infantile name-calling on both sides.", "その議論は子どもじみた悪口の言い合いに堕した。"),
    "omniscient": ("全知の、何でも知っている", "形容詞", "The novel is told by an omniscient narrator who judges everyone.", "その小説は誰をも裁く全知の語り手によって語られる。"),
    # Q18
    "discerning": ("見識のある、目の肥えた", "形容詞", "The shop caters to a small but discerning group of collectors.", "その店は少数ながら目の肥えた収集家の一団を相手にしている。"),
    "inquisitive": ("知りたがる、詮索好きな", "形容詞", "An inquisitive child will take any machine apart.", "知りたがりの子どもはどんな機械でも分解してしまう。"),
    "irascible": ("怒りっぽい", "形容詞", "The irascible old man complained about every parked car.", "その怒りっぽい老人は駐車している車すべてに文句を言った。"),
    "exquisite": ("この上なく美しい、精巧な", "形容詞", "The lid of the box is decorated with exquisite silver inlay.", "そのふたは精巧な銀の象眼で装飾されている。"),
    # Q19
    "intractable": ("手に負えない、扱いにくい", "形容詞", "Traffic in the old center remains an intractable problem.", "旧市街の交通は依然として手に負えない問題である。"),
    "shoddy": ("粗悪な、いいかげんな", "形容詞", "Shoddy workmanship on the roof caused the leak in the first place.", "屋根の粗雑な仕事がその雨漏りを引き起こした。"),
    "furtive": ("こそこそした、人目を忍ぶ", "形容詞", "He cast a furtive glance at the clock behind the speaker.", "彼は話し手の後ろの時計にこそっと目をやった。"),
    "despondent": ("落胆した、意気消沈した", "形容詞", "She grew despondent after the fourth rejection letter.", "4通目の不採用通知の後、彼女は意気消沈していった。"),
    # Q20
    "reprehensible": ("非難に値する", "形容詞", "The inquiry called the delay reprehensible but stopped short of calling it criminal.", "調査はその遅延を非難に値するが犯罪ではないと述べた。"),
    "adept": ("熟達した", "形容詞", "She is adept at repairing instruments nobody else will touch.", "彼女は他の誰も手を出さない楽器の修理に長けている。"),
    "volatile": ("不安定な、揮発性の", "形容詞", "The market has been volatile since the announcement in June.", "6月の発表以来、市場は不安定な状態が続いている。"),
    "prescient": ("先見の明のある", "形容詞", "His prescient memo warned of the shortage two years early.", "彼の先見の明のある覚書は2年早く不足を警告していた。"),
    # Q21
    "summarily": ("即座に、略式に", "副詞", "The committee summarily rejected all three proposals at its first meeting.", "委員会は最初の会合で3つの提案すべてを即座に退けた。"),
    "wryly": ("皮肉っぽく、苦々しげに", "副詞", "He smiled wryly and said nothing about the mistake.", "彼は苦笑いを浮かべ、その間違いについて何も言わなかった。"),
    "conspicuously": ("目立って、著しく", "副詞", "The chairman was conspicuously absent from the second meeting.", "議長は2回目の会合に目立って欠席していた。"),
    "warily": ("用心深く", "副詞", "The fox watched the farmhouse warily from the edge of the field.", "そのキツネは畑の端から用心深く農家をうかがっていた。"),
    # Q22
    "caved in": ("陥没した、屈した", "句動詞", "Part of the tunnel caved in during the heavy rain.", "豪雨の間にトンネルの一部が陥没した。"),
    "fired away": ("(質問などを)どんどん始めた", "句動詞", "The reporters fired away as soon as the door opened.", "扉が開くやいなや、記者たちは次々と質問を浴びせ始めた。"),
    "mulled over": ("じっくり考えた", "句動詞", "He mulled over the offer for a fortnight before replying.", "彼は返事をする前に2週間その申し出をじっくり考えた。"),
    "blew away": ("吹き飛ばした、圧倒した", "句動詞", "The gale blew away half the tiles on the south side.", "強風が南側の瓦の半分を吹き飛ばした。"),
    # Q23
    "cracked up": ("大笑いした、参ってしまった", "句動詞", "The whole class cracked up when the model collapsed.", "模型が崩れたとき、クラス全員が大笑いした。"),
    "decked out": ("飾り立てた", "句動詞", "The hall was decked out with flags for the anniversary.", "そのホールは記念日のために旗で飾り立てられていた。"),
    "rolled in": ("続々と入ってきた", "句動詞", "Donations rolled in for a fortnight after the broadcast.", "放送の後、寄付が2週間にわたって続々と寄せられた。"),
    "played down": ("重要性を低く見せた", "句動詞", "The company played down the number of affected customers.", "その会社は影響を受けた顧客の数を実際より少なく見せた。"),
    # Q24
    "hunkered down": ("身を潜めた、腰を据えた", "句動詞", "The team hunkered down and worked through the entire weekend.", "そのチームは腰を据えて週末をまるごと働き通した。"),
    "limbered up": ("準備運動をした", "句動詞", "Dancers limbered up in the corridor before the rehearsal.", "ダンサーたちはリハーサルの前に廊下で準備運動をした。"),
    "scraped by": ("どうにか食いつないだ", "句動詞", "They scraped by on savings until the new contract began.", "彼らは新しい契約が始まるまで貯金でどうにか食いつないだ。"),
    "snapped off": ("ぽきりと折れた、折り取った", "句動詞", "A branch snapped off and landed across the drive.", "枝がぽきりと折れて私道をふさぐように落ちた。"),
    # Q25
    "jockeyed for": ("(有利な位置を)争った", "句動詞", "Three deputies jockeyed for the position all summer.", "3人の次官がその職をめぐって夏中争った。"),
    "buttered up": ("お世辞を言って機嫌を取った", "句動詞", "He buttered up the caretaker to get the keys early.", "彼は早めに鍵をもらうため管理人におべっかを使った。"),
    "pored over": ("(資料を)熟読した", "句動詞", "Researchers pored over the parish records for three months.", "研究者たちは3か月にわたって教区の記録を熟読した。"),
    "rode out": ("(困難を)乗り切った", "句動詞", "The firm rode out the recession without a single redundancy.", "その会社は1人の解雇も出さずに不況を乗り切った。"),
}


CORE_IMAGES = {
    "caved in": {
        "chain": [
            {"term": "cave", "gloss": "空洞になる"},
            {"term": "in", "gloss": "内側へ落ち込んで"},
            {"gloss": "支えを失って内側へ落ち込んで"},
            {"gloss": "陥没する、屈する"},
        ],
        "particle": "in",
    },
    "fired away": {
        "chain": [
            {"term": "fire", "gloss": "撃つ"},
            {"term": "away", "gloss": "続けざまに放って"},
            {"gloss": "間を置かず続けざまに撃ち出して"},
            {"gloss": "どんどん質問を始める"},
        ],
        "particle": "away",
    },
    "mulled over": {
        "chain": [
            {"term": "mull", "gloss": "温めてじっくり煮出す"},
            {"term": "over", "gloss": "全体を繰り返し"},
            {"gloss": "考えを繰り返し温め直して"},
            {"gloss": "じっくり考える"},
        ],
        "particle": "over",
    },
    "blew away": {
        "chain": [
            {"term": "blow", "gloss": "吹く"},
            {"term": "away", "gloss": "その場から離して"},
            {"gloss": "風の力でその場から遠くへ離して"},
            {"gloss": "吹き飛ばす"},
        ],
        "particle": "away",
    },
    "cracked up": {
        "chain": [
            {"term": "crack", "gloss": "ひびが入る"},
            {"term": "up", "gloss": "抑えが利かなくなって"},
            {"gloss": "こらえていたものにひびが入って崩れて"},
            {"gloss": "大笑いする、参ってしまう"},
        ],
        "particle": "up",
        "particleSense": "disrupt",
    },
    "decked out": {
        "chain": [
            {"term": "deck", "gloss": "飾る"},
            {"term": "out", "gloss": "外から見える形に広げて"},
            {"gloss": "外から見えるように一面に飾りを広げて"},
            {"gloss": "飾り立てる"},
        ],
        "particle": "out",
        "particleSense": "spread",
    },
    "rolled in": {
        "chain": [
            {"term": "roll", "gloss": "転がる"},
            {"term": "in", "gloss": "中へ次々入って"},
            {"gloss": "波が転がり込むように次々と中へ入って"},
            {"gloss": "続々と入ってくる"},
        ],
        "particle": "in",
    },
    "played down": {
        "chain": [
            {"term": "play", "gloss": "演じて見せる"},
            {"term": "down", "gloss": "評価を下げて"},
            {"gloss": "実際より小さく見えるように見せて"},
            {"gloss": "重要性を低く見せる"},
        ],
        "particle": "down",
        "particleSense": "lower",
    },
    "hunkered down": {
        "chain": [
            {"term": "hunker", "gloss": "しゃがみ込む"},
            {"term": "down", "gloss": "腰を据えて"},
            {"gloss": "その場にしゃがんで腰を据えて"},
            {"gloss": "身を潜める、腰を据えて取り組む"},
        ],
        "particle": "down",
        "particleSense": "settle",
    },
    "limbered up": {
        "chain": [
            {"term": "limber", "gloss": "体を柔らかくする"},
            {"term": "up", "gloss": "動ける状態に整えて"},
            {"gloss": "体をほぐして動ける状態に整えて"},
            {"gloss": "準備運動をする"},
        ],
        "particle": "up",
        "particleSense": "prepare",
    },
    "scraped by": {
        "chain": [
            {"term": "scrape", "gloss": "かき集める"},
            {"term": "by", "gloss": "そばをすり抜けて"},
            {"gloss": "わずかな蓄えでどうにかすり抜けて"},
            {"gloss": "かろうじて食いつなぐ"},
        ],
        "particle": "by",
    },
    "snapped off": {
        "chain": [
            {"term": "snap", "gloss": "ぽきりと折る"},
            {"term": "off", "gloss": "本体から切り離して"},
            {"gloss": "音を立てて本体から折れ離れて"},
            {"gloss": "ぽきりと折れる"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "jockeyed for": {
        "chain": [
            {"term": "jockey", "gloss": "騎手のように位置を取り合う"},
            {"term": "for", "gloss": "その地位を求めて"},
            {"gloss": "有利な位置を求めて互いに押し合って"},
            {"gloss": "~を巡って争う"},
        ],
    },
    "buttered up": {
        "chain": [
            {"term": "butter", "gloss": "バターを塗る"},
            {"term": "up", "gloss": "すっかり塗り込めて"},
            {"gloss": "相手をすっかり滑らかに塗り込めて"},
            {"gloss": "お世辞で機嫌を取る"},
        ],
        "particle": "up",
        "particleSense": "complete",
    },
    "pored over": {
        "chain": [
            {"term": "pore", "gloss": "熱心に見入る"},
            {"term": "over", "gloss": "全体に目を通して"},
            {"gloss": "紙面の上に身をかがめて全体に目を通して"},
            {"gloss": "熟読する"},
        ],
        "particle": "over",
    },
    "rode out": {
        "chain": [
            {"term": "ride", "gloss": "乗る"},
            {"term": "out", "gloss": "外へ抜け出て"},
            {"gloss": "波に乗ったまま嵐の外へ抜け出て"},
            {"gloss": "困難を乗り切る"},
        ],
        "particle": "out",
        "particleSense": "escape",
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
        raise ValueError("模試第21回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-21 割り当てに従う",
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
