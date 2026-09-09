"""英検1級 模試第10回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-10 の割り当てに従う。
既存の英検1級セット・全級の熟語 phrase・data/lemmas.json とは重複しない。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-10"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "The keynote speaker began with a short (   ) about her first day at the laboratory, and the audience immediately relaxed.",
        "choices": ["turmoil", "larceny", "prowess", "anecdote"],
        "answerIndex": 3,
        "translation": "基調講演者は研究所での初日についての短い逸話から話を始め、聴衆はすぐに緊張がほぐれた。",
    },
    {
        "stem": "The airline's decision to charge for carry-on bags provoked such a fierce (   ) from passengers that it was withdrawn within a week.",
        "choices": ["fissure", "brevity", "backlash", "tenet"],
        "answerIndex": 2,
        "translation": "機内持ち込み手荷物を有料にするという航空会社の決定は乗客から激しい反発を招き、1週間以内に撤回された。",
    },
    {
        "stem": "Wealthy investors exploited a (   ) in the tax code for years before lawmakers finally closed it.",
        "choices": ["loophole", "skirmish", "prelude", "morsel"],
        "answerIndex": 0,
        "translation": "富裕な投資家たちは何年も税法の抜け穴を利用し、議員たちがついにそれをふさいだ。",
    },
    {
        "stem": "The driver showed no (   ) whatsoever in court, which the judge cited when handing down the maximum sentence.",
        "choices": ["euphoria", "apathy", "remorse", "zeal"],
        "answerIndex": 2,
        "translation": "その運転手は法廷で後悔の念をまったく示さず、裁判官は最高刑を言い渡す際にその点に言及した。",
    },
    {
        "stem": "Poor roads remain the greatest (   ) to economic growth in the region, according to the World Bank report.",
        "choices": ["impediment", "precedent", "gadget", "ambush"],
        "answerIndex": 0,
        "translation": "世界銀行の報告書によれば、劣悪な道路が依然としてその地域の経済成長にとって最大の障害である。",
    },
    {
        "stem": "Campaigners have worked for decades to remove the (   ) attached to mental illness so that patients seek help earlier.",
        "choices": ["tundra", "stigma", "hoard", "deceit"],
        "answerIndex": 1,
        "translation": "活動家たちは、患者がより早く助けを求められるよう、精神疾患に付きまとう汚名を取り除こうと何十年も取り組んできた。",
    },
    {
        "stem": "The detective had no evidence at that stage, just a (   ) that the missing key would turn up in the garden.",
        "choices": ["rebuke", "servitude", "foray", "hunch"],
        "answerIndex": 3,
        "translation": "その刑事はその段階で証拠は何もなく、なくなった鍵が庭で見つかるだろうという勘があるだけだった。",
    },
    {
        "stem": "The novelist deliberately (   ) social media throughout her career, believing that constant online attention would damage her writing.",
        "choices": ["entangled", "eschewed", "ransacked", "garbled"],
        "answerIndex": 1,
        "translation": "その小説家は経歴を通じて意図的にソーシャルメディアを避けた。絶え間ないネット上の注目が自分の執筆を損なうと考えていたからだ。",
    },
    {
        "stem": "Cutting the budget for street cleaning only (   ) the rat problem that residents had been complaining about.",
        "choices": ["replenished", "mitigated", "exacerbated", "retracted"],
        "answerIndex": 2,
        "translation": "街路清掃の予算削減は、住民が苦情を訴えていたネズミの問題を悪化させただけだった。",
    },
    {
        "stem": "Under the confidentiality agreement, neither company (   ) the detailed terms of the final settlement to reporters.",
        "choices": ["divulged", "baffled", "hoisted", "punctuated"],
        "answerIndex": 0,
        "translation": "秘密保持契約に基づき、どちらの会社も最終的な和解の詳細な条件を記者に漏らさなかった。",
    },
    {
        "stem": "Party members (   ) their leader after three consecutive election defeats and chose a younger replacement.",
        "choices": ["enlisted", "sauntered", "dilated", "ousted"],
        "answerIndex": 3,
        "translation": "党員たちは3回連続の選挙敗北の後に党首を追放し、より若い後任を選んだ。",
    },
    {
        "stem": "Security footage from the parking garage (   ) the witness's account of what had happened that night.",
        "choices": ["demoralized", "gnawed", "corroborated", "splurged"],
        "answerIndex": 2,
        "translation": "駐車場の防犯映像は、その夜に起きたことについての目撃者の証言を裏付けた。",
    },
    {
        "stem": "Marcus (   ) for weeks and ended up writing the entire report during the night before the deadline.",
        "choices": ["fumbled", "coalesced", "gleaned", "procrastinated"],
        "answerIndex": 3,
        "translation": "マーカスは何週間もぐずぐずと先延ばしにし、結局は締め切り前夜に報告書全体を書くことになった。",
    },
    {
        "stem": "A clause in the contract (   ) the artist from selling similar designs to any competitor for two years.",
        "choices": ["excavated", "precluded", "smuggled", "chided"],
        "answerIndex": 1,
        "translation": "契約の条項は、その芸術家が2年間どの競合他社にも類似のデザインを売ることを妨げた。",
    },
    {
        "stem": "Staff made (   ) copies of the documents and passed them to the regulator without telling their managers.",
        "choices": ["surreptitious", "callous", "hilarious", "redolent"],
        "answerIndex": 0,
        "translation": "職員たちは書類の複写をひそかに取り、上司に告げずに規制当局へ渡した。",
    },
    {
        "stem": "Laboratories handling the virus must meet (   ) safety standards that are inspected twice a year.",
        "choices": ["stringent", "vicarious", "ambient", "palatial"],
        "answerIndex": 0,
        "translation": "そのウイルスを扱う研究所は、年に2回検査される厳格な安全基準を満たさなければならない。",
    },
    {
        "stem": "It would be (   ) to put your entire savings into a single company, however promising it looks.",
        "choices": ["residual", "imprudent", "endemic", "garish"],
        "answerIndex": 1,
        "translation": "どれほど有望に見えても、貯蓄の全額を1社につぎ込むのは軽率だろう。",
    },
    {
        "stem": "After a month, Elena found the small office surprisingly (   ), largely because her colleagues shared her sense of humor.",
        "choices": ["illegible", "abject", "forensic", "congenial"],
        "answerIndex": 3,
        "translation": "1か月後、エレナはその小さな職場が驚くほど居心地よいと感じた。主に同僚たちが彼女と同じユーモアの感覚を持っていたからだ。",
    },
    {
        "stem": "The duchess was so (   ) that she barely acknowledged the villagers who had waited hours to greet her.",
        "choices": ["bereaved", "contrived", "haughty", "solvent"],
        "answerIndex": 2,
        "translation": "公爵夫人はひどく高慢で、何時間も待って出迎えた村人たちにほとんど目もくれなかった。",
    },
    {
        "stem": "Two officials were found to have been (   ) in the scheme, having approved the payments while knowing their true purpose.",
        "choices": ["repugnant", "invariable", "complicit", "perverse"],
        "answerIndex": 2,
        "translation": "2人の役人がその計画に加担していたことが判明した。支払いの本当の目的を知りながら承認していたのである。",
    },
    {
        "stem": "Rain fell only (   ) during the dry season, so the reservoir never refilled completely.",
        "choices": ["blatantly", "sporadically", "eloquently", "belatedly"],
        "answerIndex": 1,
        "translation": "乾期には雨が散発的にしか降らなかったため、貯水池は完全には満たされなかった。",
    },
    {
        "stem": "After the deficit grew for a third year, the city finally (   ) spending on new construction projects.",
        "choices": ["reined in", "dished out", "chipped in", "tapped into"],
        "answerIndex": 0,
        "translation": "赤字が3年目も拡大した後、市はついに新規建設事業への支出を抑制した。",
    },
    {
        "stem": "The champion (   ) the criticism and said she would let her performance in the final answer her critics.",
        "choices": ["dawned on", "shrugged off", "wolfed down", "spruced up"],
        "answerIndex": 1,
        "translation": "そのチャンピオンは批判を意に介さず、決勝での成績が批評家への答えになるだろうと述べた。",
    },
    {
        "stem": "Detectives (   ) arson as a cause once the fire investigator confirmed that the wiring had failed.",
        "choices": ["jotted down", "ruled out", "pinned down", "fended off"],
        "answerIndex": 1,
        "translation": "火災調査官が配線の故障を確認すると、刑事たちは原因として放火を除外した。",
    },
    {
        "stem": "Against every prediction, the small studio (   ) one of the most profitable films of the decade.",
        "choices": ["trailed off", "harped on", "opted for", "pulled off"],
        "answerIndex": 3,
        "translation": "あらゆる予想に反して、その小さな制作会社は10年で最も収益性の高い映画の1つを成功させた。",
    },
]


DETAILS = {
    # Q1
    "turmoil": ("混乱、動揺", "名詞", "The country fell into political turmoil after the sudden resignation of its president.", "その国は大統領の突然の辞任の後、政治的混乱に陥った。"),
    "larceny": ("窃盗", "名詞", "He was charged with larceny after taking equipment from the construction site.", "彼は建設現場から機材を持ち去り、窃盗の罪で告発された。"),
    "prowess": ("卓越した技量、優れた腕前", "名詞", "Her musical prowess was obvious to everyone who heard the audition.", "彼女の音楽的な技量は、オーディションを聞いた誰の目にも明らかだった。"),
    "anecdote": ("逸話、エピソード", "名詞", "The professor illustrated the theory with an anecdote from his own fieldwork.", "その教授は自身の現地調査からの逸話を用いてその理論を説明した。"),
    # Q2
    "fissure": ("亀裂、割れ目", "名詞", "Engineers discovered a deep fissure running along the base of the dam.", "技術者たちはダムの基部に沿って走る深い亀裂を発見した。"),
    "brevity": ("簡潔さ、短さ", "名詞", "Readers praised the report for its brevity and its unusually clear conclusions.", "読者はその報告書の簡潔さと異例なほど明快な結論を称賛した。"),
    "backlash": ("反発、強い反動", "名詞", "The proposed pension reform met a furious backlash from public sector workers.", "提案された年金改革は公務員から猛烈な反発を受けた。"),
    "tenet": ("信条、教義", "名詞", "Respect for evidence is a central tenet of scientific training everywhere.", "証拠の尊重は、どこでも科学教育の中心的な信条である。"),
    # Q3
    "loophole": ("抜け穴、法の盲点", "名詞", "Lawyers found a loophole that allowed the company to avoid the new levy.", "弁護士たちはその会社が新たな課徴金を回避できる抜け穴を見つけた。"),
    "skirmish": ("小競り合い、小規模な戦闘", "名詞", "A brief skirmish broke out near the border before observers arrived.", "監視団が到着する前に、国境付近で短い小競り合いが起こった。"),
    "prelude": ("前触れ、前奏", "名詞", "The strike proved to be a prelude to months of industrial conflict.", "そのストライキは何か月にも及ぶ労働争議の前触れだと分かった。"),
    "morsel": ("一口、少量", "名詞", "She offered the puppy a morsel of chicken from her own plate.", "彼女は自分の皿から鶏肉を一口、子犬に差し出した。"),
    # Q4
    "euphoria": ("強い幸福感、陶酔", "名詞", "The euphoria after the victory faded once the team saw the injury list.", "勝利後の高揚感は、チームが負傷者リストを見ると薄れていった。"),
    "apathy": ("無関心", "名詞", "Voter apathy was blamed for the lowest turnout in forty years.", "40年で最低の投票率は有権者の無関心のせいだとされた。"),
    "remorse": ("後悔、良心の呵責", "名詞", "He expressed genuine remorse for the harm his careless words had caused.", "彼は自分の不注意な言葉が招いた害について心からの後悔を表した。"),
    "zeal": ("熱意、熱心さ", "名詞", "The young teacher pursued the reform with a zeal that surprised her colleagues.", "その若い教師は同僚を驚かせるほどの熱意でその改革を進めた。"),
    # Q5
    "impediment": ("障害、妨げ", "名詞", "A shortage of trained nurses is the main impediment to reopening the ward.", "訓練を受けた看護師の不足が、その病棟の再開に対する主な障害である。"),
    "precedent": ("先例、前例", "名詞", "The ruling set a precedent that lower courts have followed ever since.", "その判決は先例となり、下級裁判所はそれ以来それに従っている。"),
    "gadget": ("小型の装置、便利な小道具", "名詞", "He bought a gadget that measures humidity in every room of the house.", "彼は家中のどの部屋でも湿度を測る小型の装置を買った。"),
    "ambush": ("待ち伏せ攻撃", "名詞", "The convoy was halted by an ambush on the narrow mountain road.", "その車列は狭い山道での待ち伏せ攻撃によって停止させられた。"),
    # Q6
    "tundra": ("ツンドラ、凍土帯", "名詞", "Reindeer cross the frozen tundra in search of lichen every spring.", "トナカイは毎春、地衣類を求めて凍ったツンドラを横断する。"),
    "stigma": ("汚名、社会的な烙印", "名詞", "The charity works to reduce the stigma surrounding addiction treatment.", "その慈善団体は依存症治療を取り巻く汚名を減らすために活動している。"),
    "hoard": ("蓄え、隠し財産", "名詞", "Archaeologists uncovered a hoard of silver coins beneath the farmhouse floor.", "考古学者たちは農家の床下から銀貨の蓄えを発掘した。"),
    "deceit": ("欺瞞、ごまかし", "名詞", "The whole scheme rested on deceit about where the money actually went.", "その計画全体は、金が実際どこへ行ったのかについての欺瞞に基づいていた。"),
    # Q7
    "rebuke": ("叱責、非難", "名詞", "The coach issued a sharp rebuke to players who skipped the morning session.", "監督は朝の練習を欠席した選手たちに厳しい叱責を与えた。"),
    "servitude": ("隷属、束縛", "名詞", "The memoir describes years of servitude in a household far from home.", "その回想録は、故郷から遠い家庭での長年の隷属の日々を描いている。"),
    "foray": ("進出、初めての試み", "名詞", "The bakery's first foray into online sales exceeded everyone's modest expectations.", "そのパン屋のオンライン販売への最初の進出は、皆のささやかな予想を上回った。"),
    "hunch": ("勘、直感", "名詞", "Acting on a hunch, she checked the storeroom and found the missing file.", "勘を頼りに、彼女は倉庫を調べて紛失した書類を見つけた。"),
    # Q8
    "entangled": ("絡ませた、巻き込んだ", "動詞", "The storm entangled the fishing nets in the propeller of the small boat.", "嵐が漁網を小舟のプロペラに絡ませた。"),
    "eschewed": ("避けた、控えた", "動詞", "The monastery eschewed modern comforts and kept its centuries-old daily routine.", "その修道院は現代的な快適さを避け、何世紀も続く日課を守った。"),
    "ransacked": ("荒らし回った、くまなく探した", "動詞", "Thieves ransacked the office and left every drawer lying on the floor.", "泥棒たちは事務所を荒らし回り、すべての引き出しを床に放置した。"),
    "garbled": ("(内容を)ゆがめた、不明瞭にした", "動詞", "A poor connection garbled the pilot's instructions to the control tower.", "接続不良がパイロットから管制塔への指示を不明瞭にした。"),
    # Q9
    "replenished": ("補充した、満たし直した", "動詞", "Volunteers replenished the shelter's supplies before the second wave of evacuees arrived.", "ボランティアたちは第2陣の避難者が到着する前に避難所の物資を補充した。"),
    "mitigated": ("和らげた、軽減した", "動詞", "Early warnings mitigated the damage from the flood in several coastal villages.", "早期の警報がいくつかの沿岸の村での洪水被害を軽減した。"),
    "exacerbated": ("悪化させた", "動詞", "The delay in repairs exacerbated the leak that had started in the basement.", "修理の遅れが地下室で始まった水漏れを悪化させた。"),
    "retracted": ("撤回した", "動詞", "The journal retracted the paper after the authors admitted errors in the data.", "著者たちがデータの誤りを認めた後、その学術誌は論文を撤回した。"),
    # Q10
    "divulged": ("漏らした、明かした", "動詞", "A former employee divulged the recipe to a rival manufacturer last spring.", "元従業員が昨春、そのレシピを競合メーカーに漏らした。"),
    "baffled": ("当惑させた", "動詞", "The disappearance of the aircraft baffled investigators for more than a decade.", "その航空機の消失は10年以上にわたり調査員たちを当惑させた。"),
    "hoisted": ("引き上げた、掲げた", "動詞", "Workers hoisted the steel beam to the ninth floor with a crane.", "作業員たちはクレーンで鉄骨を9階まで引き上げた。"),
    "punctuated": ("(時折)中断させた、区切った", "動詞", "Loud applause punctuated the mayor's speech at least a dozen times.", "大きな拍手が市長の演説を少なくとも十数回中断させた。"),
    # Q11
    "enlisted": ("(協力を)得た、入隊させた", "動詞", "The museum enlisted local students to catalog the photographs each weekend.", "その博物館は毎週末に写真を目録化するため地元の学生の協力を得た。"),
    "sauntered": ("ぶらぶら歩いた", "動詞", "He sauntered along the riverbank as though he had nowhere to be.", "彼はどこにも行く当てがないかのように川岸をぶらぶら歩いた。"),
    "dilated": ("拡張した、広がった", "動詞", "The patient's pupils dilated as soon as the room lights were dimmed.", "部屋の照明が暗くなるとすぐに患者の瞳孔が拡張した。"),
    "ousted": ("追放した、追い出した", "動詞", "Shareholders ousted the chairman at a meeting that lasted only twenty minutes.", "株主たちはわずか20分の会合で会長を追放した。"),
    # Q12
    "demoralized": ("意気消沈させた", "動詞", "Repeated last-minute losses demoralized a squad that had started the season well.", "土壇場での敗戦が続き、好調に開幕した選手団を意気消沈させた。"),
    "gnawed": ("かじった、少しずつ蝕んだ", "動詞", "Mice gnawed the cables behind the refrigerator and caused the outage.", "ネズミが冷蔵庫の裏のケーブルをかじり、停電を引き起こした。"),
    "corroborated": ("裏付けた、確証した", "動詞", "Two independent laboratories corroborated the results of the original experiment.", "2つの独立した研究所が元の実験の結果を裏付けた。"),
    "splurged": ("大金を使った、散財した", "動詞", "They splurged on a week in Kyoto after saving for three years.", "彼らは3年間貯金した後、京都での1週間に大金を使った。"),
    # Q13
    "fumbled": ("手探りした、しくじった", "動詞", "She fumbled with the lock in the dark and finally dropped her keys.", "彼女は暗闇の中で鍵穴を手探りし、ついに鍵を落としてしまった。"),
    "coalesced": ("合体した、まとまった", "動詞", "Several small protest groups coalesced into a single national movement.", "いくつかの小さな抗議団体が合体して1つの全国的な運動になった。"),
    "gleaned": ("(苦労して)集めた、拾い集めた", "動詞", "Historians gleaned the details from letters stored in a village archive.", "歴史家たちは村の文書館に保管された手紙からその詳細を拾い集めた。"),
    "procrastinated": ("先延ばしにした、ぐずぐずした", "動詞", "He procrastinated until the application window had almost completely closed.", "彼は応募期間がほとんど締め切られるまで先延ばしにした。"),
    # Q14
    "excavated": ("発掘した、掘り出した", "動詞", "The team excavated a Roman bathhouse beneath the modern parking lot.", "調査団は現代の駐車場の下からローマ時代の浴場を発掘した。"),
    "precluded": ("妨げた、不可能にした", "動詞", "His injury precluded any possibility of competing in the national championship.", "彼のけがは全国選手権に出場する可能性を一切なくした。"),
    "smuggled": ("密輸した", "動詞", "Customs officers found rare orchids smuggled inside hollowed-out books.", "税関職員は中をくり抜いた本の中に密輸された希少なランを発見した。"),
    "chided": ("たしなめた、小言を言った", "動詞", "The librarian gently chided the students for talking near the reading desks.", "司書は閲覧席の近くで話す学生たちを穏やかにたしなめた。"),
    # Q15
    "surreptitious": ("こっそりとした、内密の", "形容詞", "A surreptitious recording of the meeting later appeared on a news website.", "会議のひそかな録音が後にニュースサイトに現れた。"),
    "callous": ("冷淡な、無情な", "形容詞", "His callous remark about the layoffs offended almost the entire department.", "人員削減についての彼の冷淡な発言は、部署のほぼ全員を不快にさせた。"),
    "hilarious": ("とてもおかしい", "形容詞", "The children found the puppet's clumsy dance absolutely hilarious.", "子どもたちはその人形のぎこちない踊りを実におかしいと思った。"),
    "redolent": ("(においを)漂わせる、思い起こさせる", "形容詞", "The kitchen was redolent of cinnamon and freshly baked bread.", "台所はシナモンと焼きたてのパンの香りを漂わせていた。"),
    # Q16
    "stringent": ("厳格な、厳しい", "形容詞", "Exporters must comply with stringent rules on packaging and labeling.", "輸出業者は包装と表示に関する厳格な規則を守らなければならない。"),
    "vicarious": ("他人の経験を通して感じる、代理の", "形容詞", "Parents often take vicarious pleasure in the achievements of their children.", "親はしばしば子どもの成果に自分のことのような喜びを感じる。"),
    "ambient": ("周囲の、環境の", "形容詞", "The sensor adjusts the display according to the ambient light in the room.", "そのセンサーは部屋の周囲の光に応じて画面表示を調整する。"),
    "palatial": ("宮殿のような、豪壮な", "形容詞", "The hotel lobby was palatial, with marble columns and enormous chandeliers.", "そのホテルのロビーは宮殿のようで、大理石の柱と巨大なシャンデリアがあった。"),
    # Q17
    "residual": ("残りの、残留の", "形容詞", "Technicians measured the residual heat in the reactor twelve hours later.", "技術者たちは12時間後に原子炉の残留熱を測定した。"),
    "imprudent": ("軽率な、思慮の足りない", "形容詞", "It was imprudent of him to sign the lease without reading it.", "契約書を読まずに賃貸借契約に署名したのは彼にとって軽率だった。"),
    "endemic": ("(その土地に)特有の、風土性の", "形容詞", "The bird is endemic to a single valley on the northern island.", "その鳥は北の島の1つの谷にのみ生息している。"),
    "garish": ("けばけばしい、派手すぎる", "形容詞", "The new signs were so garish that neighbors petitioned for their removal.", "新しい看板はあまりにけばけばしく、近隣住民は撤去を請願した。"),
    # Q18
    "illegible": ("読めない、判読できない", "形容詞", "The doctor's handwriting on the form was almost completely illegible.", "その用紙に書かれた医師の字はほとんど完全に判読できなかった。"),
    "abject": ("惨めな、みじめなほどの", "形容詞", "Millions still live in abject poverty despite decades of economic growth.", "何十年もの経済成長にもかかわらず、何百万もの人々が今なお極貧の中で暮らしている。"),
    "forensic": ("法医学の、犯罪科学の", "形容詞", "A forensic examination of the laptop revealed messages deleted months earlier.", "そのノートパソコンの法医学的検査により、数か月前に削除されたメッセージが判明した。"),
    "congenial": ("感じのよい、気の合う", "形容詞", "The village proved a congenial place for a writer seeking quiet.", "その村は静けさを求める作家にとって感じのよい場所だと分かった。"),
    # Q19
    "bereaved": ("(近親者を)亡くした", "形容詞", "Counselors were sent to support bereaved families after the mining accident.", "鉱山事故の後、遺族を支えるために相談員が派遣された。"),
    "contrived": ("わざとらしい、不自然な", "形容詞", "Critics called the film's ending contrived and emotionally unconvincing.", "批評家たちはその映画の結末をわざとらしく、感情的に説得力がないと評した。"),
    "haughty": ("高慢な、横柄な", "形容詞", "His haughty manner made him unpopular with the junior staff.", "彼の高慢な態度は若手職員の間で彼を不人気にした。"),
    "solvent": ("支払い能力のある", "形容詞", "The charity remained solvent only because of an anonymous donation last December.", "その慈善団体は昨年12月の匿名の寄付のおかげでのみ支払い能力を保った。"),
    # Q20
    "repugnant": ("不快な、嫌悪を催させる", "形容詞", "The committee found the proposal morally repugnant and rejected it outright.", "委員会はその提案を道徳的に不快とみなし、即座に却下した。"),
    "invariable": ("不変の、常に一定の", "形容詞", "His invariable routine begins with a walk before six every morning.", "彼の変わらぬ日課は、毎朝6時前の散歩から始まる。"),
    "complicit": ("共謀した、加担した", "形容詞", "The auditor was complicit in hiding losses from the board for years.", "その監査人は何年も取締役会から損失を隠すことに加担していた。"),
    "perverse": ("ひねくれた、道理に反した", "形容詞", "She takes perverse satisfaction in arguing against positions she privately holds.", "彼女は内心では支持している立場に反論することにひねくれた満足を覚える。"),
    # Q21
    "blatantly": ("露骨に、あからさまに", "副詞", "The advertisement was blatantly misleading about the product's actual battery life.", "その広告は製品の実際の電池寿命について露骨に誤解を招くものだった。"),
    "sporadically": ("散発的に、時折", "副詞", "The old radio worked only sporadically after the antenna was damaged.", "アンテナが損傷した後、その古いラジオは散発的にしか作動しなかった。"),
    "eloquently": ("雄弁に、説得力をもって", "副詞", "She spoke eloquently about the need to protect the wetlands.", "彼女は湿地を守る必要性について雄弁に語った。"),
    "belatedly": ("遅ればせながら、手遅れになってから", "副詞", "The manufacturer belatedly recalled the heaters after a second fire.", "そのメーカーは2件目の火災の後、遅ればせながらヒーターを回収した。"),
    # Q22
    "reined in": ("抑制した、手綱を引き締めた", "句動詞", "The central bank reined in lending with a sharp rise in interest rates.", "中央銀行は金利の急上昇によって融資を抑制した。"),
    "dished out": ("(気前よく)与えた、配った", "句動詞", "The referee dished out five yellow cards in the opening half alone.", "その主審は前半だけで5枚のイエローカードを出した。"),
    "chipped in": ("(金や労力を)出し合った、口を挟んだ", "句動詞", "Everyone in the office chipped in to buy the retiring caretaker a gift.", "職場の全員がお金を出し合い、退職する管理人に贈り物を買った。"),
    "tapped into": ("(資源などを)活用した、引き出した", "句動詞", "The campaign tapped into a widespread frustration with rising rents.", "その運動は家賃上昇への広範な不満をうまく取り込んだ。"),
    # Q23
    "dawned on": ("(考えが)分かり始めた、思い当たった", "句動詞", "It slowly dawned on him that the office had been closed all week.", "事務所が1週間ずっと閉まっていたことが、彼にはゆっくりと分かってきた。"),
    "shrugged off": ("意に介さなかった、受け流した", "句動詞", "The veteran pitcher shrugged off the boos and finished the inning calmly.", "そのベテラン投手はブーイングを受け流し、落ち着いてその回を投げ終えた。"),
    "wolfed down": ("がつがつ食べた", "句動詞", "The hikers wolfed down their sandwiches before the rain reached the ridge.", "登山者たちは雨が尾根に達する前にサンドイッチをがつがつ食べた。"),
    "spruced up": ("きれいに整えた、手入れした", "句動詞", "The owners spruced up the cottage before putting it on the market.", "所有者たちは売りに出す前にその別荘をきれいに整えた。"),
    # Q24
    "jotted down": ("書き留めた、メモした", "句動詞", "She jotted down the license plate number before the van turned the corner.", "彼女はそのバンが角を曲がる前にナンバープレートの番号を書き留めた。"),
    "ruled out": ("除外した、可能性を排除した", "句動詞", "The doctor ruled out an allergy after reviewing the blood test results.", "医師は血液検査の結果を検討した後、アレルギーの可能性を除外した。"),
    "pinned down": ("特定した、動けなくした", "句動詞", "Engineers finally pinned down the fault to a single faulty sensor.", "技術者たちはついに不具合を1つの故障したセンサーに特定した。"),
    "fended off": ("撃退した、かわした", "句動詞", "The candidate fended off questions about her business dealings for an hour.", "その候補者は自分の商取引に関する質問を1時間かわし続けた。"),
    # Q25
    "trailed off": ("(声などが)次第に消えた", "句動詞", "His voice trailed off as he realized nobody was listening anymore.", "誰ももう聞いていないと気づくにつれ、彼の声は次第に消えていった。"),
    "harped on": ("くどくど言い続けた", "句動詞", "Her uncle harped on the same complaint at every family gathering.", "彼女のおじは家族の集まりのたびに同じ不満をくどくど言い続けた。"),
    "opted for": ("(~を)選んだ", "句動詞", "The council opted for a smaller library rather than closing the branch entirely.", "議会は支所を完全に閉鎖するのではなく、より小さな図書館を選んだ。"),
    "pulled off": ("やってのけた、成し遂げた", "句動詞", "The relay team pulled off a comeback that nobody in the stadium expected.", "そのリレーチームは競技場の誰も予想しなかった逆転を成し遂げた。"),
}


CORE_IMAGES = {
    "reined in": {
        "chain": [
            {"term": "rein", "gloss": "手綱で御する"},
            {"term": "in", "gloss": "内側へ引き戻して"},
            {"gloss": "外へ広がる動きを内側へ引き戻して"},
            {"gloss": "抑制する、引き締める"},
        ],
        "particle": "in",
    },
    "dished out": {
        "chain": [
            {"term": "dish", "gloss": "皿に盛る"},
            {"term": "out", "gloss": "外へ配って"},
            {"gloss": "手元の物を次々と外へ配って"},
            {"gloss": "気前よく与える、次々と出す"},
        ],
        "particle": "out",
        "particleSense": "delegate",
    },
    "chipped in": {
        "chain": [
            {"term": "chip", "gloss": "小片を出す"},
            {"term": "in", "gloss": "中へ加えて"},
            {"gloss": "自分の分を全体の中へ加えて"},
            {"gloss": "出し合う、口を挟む"},
        ],
        "particle": "in",
    },
    "tapped into": {
        "chain": [
            {"term": "tap", "gloss": "栓を開けて取り出す"},
            {"term": "into", "gloss": "中へ入り込んで"},
            {"gloss": "たまっている物の中へ管を差し込んで"},
            {"gloss": "資源や感情を引き出して活用する"},
        ],
        "particle": "into",
    },
    "dawned on": {
        "chain": [
            {"term": "dawn", "gloss": "夜が明ける"},
            {"term": "on", "gloss": "その人の意識へ届いて"},
            {"gloss": "薄明かりのように考えが意識へ差してきて"},
            {"gloss": "だんだん分かってくる"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "shrugged off": {
        "chain": [
            {"term": "shrug", "gloss": "肩をすくめる"},
            {"term": "off", "gloss": "肩から払い落として"},
            {"gloss": "のしかかるものを肩から払い落として"},
            {"gloss": "意に介さない、受け流す"},
        ],
        "particle": "off",
        "particleSense": "pull-away",
    },
    "wolfed down": {
        "chain": [
            {"term": "wolf", "gloss": "オオカミのように食う"},
            {"term": "down", "gloss": "喉の下へ送り込んで"},
            {"gloss": "噛まずに次々と胃へ送り込んで"},
            {"gloss": "がつがつ食べる"},
        ],
        "particle": "down",
        "particleSense": "descend",
    },
    "spruced up": {
        "chain": [
            {"term": "spruce", "gloss": "こざっぱりさせる"},
            {"term": "up", "gloss": "見栄えを整えて"},
            {"gloss": "人前に出せる状態まで整えて"},
            {"gloss": "きれいに手入れする"},
        ],
        "particle": "up",
        "particleSense": "prepare",
    },
    "jotted down": {
        "chain": [
            {"term": "jot", "gloss": "ちょっと書きつける"},
            {"term": "down", "gloss": "紙の上へ落ち着けて"},
            {"gloss": "頭に浮かんだことを紙の上へ落ち着けて"},
            {"gloss": "手早く書き留める"},
        ],
        "particle": "down",
        "particleSense": "settle",
    },
    "ruled out": {
        "chain": [
            {"term": "rule", "gloss": "線を引いて定める"},
            {"term": "out", "gloss": "枠の外へ取り除いて"},
            {"gloss": "候補に線を引いて枠の外へ出して"},
            {"gloss": "可能性を除外する"},
        ],
        "particle": "out",
        "particleSense": "remove",
    },
    "pinned down": {
        "chain": [
            {"term": "pin", "gloss": "ピンで留める"},
            {"term": "down", "gloss": "押さえつけて動かなくして"},
            {"gloss": "曖昧なものを一点に押さえつけて"},
            {"gloss": "特定する、動けなくする"},
        ],
        "particle": "down",
        "particleSense": "suppress",
    },
    "fended off": {
        "chain": [
            {"term": "fend", "gloss": "防ぐ"},
            {"term": "off", "gloss": "手前で押し離して"},
            {"gloss": "迫ってくるものを手前で押し離して"},
            {"gloss": "撃退する、かわす"},
        ],
        "particle": "off",
        "particleSense": "pull-away",
    },
    "trailed off": {
        "chain": [
            {"term": "trail", "gloss": "後ろへ細く引きずる"},
            {"term": "off", "gloss": "離れて弱まって"},
            {"gloss": "尾を引きながら次第に弱まって"},
            {"gloss": "声や勢いが次第に消える"},
        ],
        "particle": "off",
        "particleSense": "weaken",
    },
    "harped on": {
        "chain": [
            {"term": "harp", "gloss": "竪琴の同じ弦をかき鳴らす"},
            {"term": "on", "gloss": "同じ話題に乗ったまま続けて"},
            {"gloss": "同じ調子を延々と鳴らし続けて"},
            {"gloss": "くどくど言い続ける"},
        ],
        "particle": "on",
        "particleSense": "continue",
    },
    "pulled off": {
        "chain": [
            {"term": "pull", "gloss": "強く引く"},
            {"term": "off", "gloss": "引き離して自分のものにして"},
            {"gloss": "難しい賞品を引き離して手にして"},
            {"gloss": "やってのける、成功させる"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "opted for": {
        "chain": [
            {"term": "opt", "gloss": "選ぶ"},
            {"term": "for", "gloss": "その対象を求めて"},
            {"gloss": "複数の中から一つを求めて選び取って"},
            {"gloss": "~のほうを選ぶ"},
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
        raise ValueError("模試第10回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-10 割り当てに従う",
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
