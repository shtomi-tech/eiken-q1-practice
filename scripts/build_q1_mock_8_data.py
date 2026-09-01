"""ユーザー提供画像の英検1級模試を、模試第6回基準で構造化する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-8"
BLANK_RE = re.compile(r"\(\s+\)")
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


QUESTIONS = [
    {
        "stem": "At first, Patricia enjoyed being the manager of the local football club, but over time the numerous administrative duties became an (   ) task that she no longer enjoyed.",
        "choices": ["amiable", "onerous", "sporadic", "incongruous"],
        "answerIndex": 1,
        "translation": "最初、パトリシアは地元のサッカークラブの責任者であることを楽しんでいたが、やがて数多くの事務的な職務が、楽しめない負担の大きい仕事になった。",
    },
    {
        "stem": "After the public heard Mayor Wilson expressing his racist and sexist views in a recording, he was (   ) by almost everyone.",
        "choices": ["grappled", "dismantled", "scuffed", "reviled"],
        "answerIndex": 3,
        "translation": "ウィルソン市長が録音の中で人種差別的・性差別的な見解を述べているのを世間が聞いた後、彼はほとんど全員から激しく非難された。",
    },
    {
        "stem": "Before they got their new heating system, the upstairs of their house was always hotter than the basement. Now, though, the heat is (   ) much more evenly than it was before.",
        "choices": ["diffused", "assailed", "maligned", "shirked"],
        "answerIndex": 0,
        "translation": "新しい暖房システムを取り付ける前は、家の2階がいつも地下室より暑かった。しかし今では、熱が以前よりずっと均等に拡散している。",
    },
    {
        "stem": "No one noticed as the magician (   ) placed the ball into his jacket pocket while pretending to take something else out of it.",
        "choices": ["furtively", "chronically", "autonomously", "equitably"],
        "answerIndex": 0,
        "translation": "その手品師が別の物を取り出すふりをしながら、こっそりボールを上着のポケットに入れたことに誰も気づかなかった。",
    },
    {
        "stem": "This skincare product is recommended for those with lighter (   ) who tend to burn more easily in the sun than those with darker skin.",
        "choices": ["complexions", "shimmers", "undertones", "prophets"],
        "answerIndex": 0,
        "translation": "このスキンケア製品は、肌の色が濃い人よりも日光で焼けやすい、肌の色が明るい人に推奨される。",
    },
    {
        "stem": "In the past, it was usual for people in some countries to take (   ) lessons in order to get rid of their regional accents. However, these days, such lessons are less common.",
        "choices": ["restitution", "vanity", "enunciation", "ambiguity"],
        "answerIndex": 2,
        "translation": "かつて一部の国では、地域なまりをなくすために発音のレッスンを受けるのが普通だった。しかし最近では、そのようなレッスンはあまり一般的ではない。",
    },
    {
        "stem": "This painting by the famous artist depicts a typical (   ) scene of green fields and shepherds tending their sheep, with a little church in the background.",
        "choices": ["debonair", "bucolic", "erroneous", "pernicious"],
        "answerIndex": 1,
        "translation": "その有名な画家の絵は、緑の野原と羊の世話をする羊飼い、背景の小さな教会がある典型的な牧歌的風景を描いている。",
    },
    {
        "stem": "A: Oh, no. The heavy rain seems to have turned the rugby pitch into a (   ).\nB: I hope it dries out before the match on Saturday. It looks really slippery.",
        "choices": ["quagmire", "menace", "mirage", "plateau"],
        "answerIndex": 0,
        "translation": "A：ああ、大変。激しい雨でラグビー場が泥沼になったようだ。\nB：土曜日の試合までに乾くといいね。本当に滑りやすそうだ。",
    },
    {
        "stem": "Isaiah's friends tried to (   ) him into going to the party with them, but nothing they said could change his mind. He knew he needed to study for the test.",
        "choices": ["persuade", "accentuate", "inhibit", "absolve"],
        "answerIndex": 0,
        "translation": "イザヤの友人たちは彼を説得して一緒にパーティーへ行こうとしたが、何を言っても彼の考えを変えられなかった。彼はテストの勉強が必要だと分かっていた。",
    },
    {
        "stem": "After the accident, the Prime Minister offered his (   ) to those who had lost their lives as well as their families. He also said he was praying for the speedy recovery of the injured.",
        "choices": ["condolences", "prologues", "pretensions", "tribulations"],
        "answerIndex": 0,
        "translation": "事故の後、首相は命を失った人々とその家族に哀悼の意を表した。また、負傷者が早く回復するよう祈っていると述べた。",
    },
    {
        "stem": "A: I heard you're selling your art on the Internet, Alison.\nB: Yes, it's a great way to (   ) my income. I made an extra $700 last month.",
        "choices": ["deplete", "augment", "smother", "repress"],
        "answerIndex": 1,
        "translation": "A：アリソン、インターネットで作品を売っているんだってね。\nB：うん、収入を増やすいい方法だよ。先月は700ドル余分に稼いだんだ。",
    },
    {
        "stem": "In his public statement, the defendant expressed (   ) for his crimes, stating that he was deeply sorry and that he would do his best to make up for his mistakes.",
        "choices": ["dexterity", "contrition", "mayhem", "aridity"],
        "answerIndex": 1,
        "translation": "被告は公式声明で、自分の犯罪について深い悔恨を示し、心から申し訳なく思っており、過ちを償うために最善を尽くすと述べた。",
    },
    {
        "stem": "After more than 20 years as manager, Fernando was reluctant to (   ) control of the department. However, he knew that it was time for someone new to take over.",
        "choices": ["bewail", "disparage", "relinquish", "transpose"],
        "answerIndex": 2,
        "translation": "20年以上管理職を務めたフェルナンドは、部署の統率を手放すことに気が進まなかった。しかし、新しい人が引き継ぐ時期だと分かっていた。",
    },
    {
        "stem": "The travel company offers exciting trips to the Amazon rainforest that are ideal for (   ) travelers who enjoy adventure and do not mind sleeping in a tent.",
        "choices": ["opaque", "avaricious", "dank", "venturesome"],
        "answerIndex": 3,
        "translation": "その旅行会社は、冒険を楽しみ、テントで寝ることを苦にしない冒険好きな旅行者に最適な、アマゾン熱帯雨林への刺激的な旅行を提供している。",
    },
    {
        "stem": "Despite the fact that it was his first major acting part, Michael performed the role of Hamlet with (   ) skill. In fact, he was so good that the audience gave him a standing ovation.",
        "choices": ["consummate", "amateurish", "malignant", "neurotic"],
        "answerIndex": 0,
        "translation": "それが初めての主要な演技の役だったにもかかわらず、マイケルは完璧な技量でハムレットを演じた。実際、あまりに見事だったので観客はスタンディングオベーションを送った。",
    },
    {
        "stem": "Dara was looking forward to a nice hot bath after her long journey. However, the thermostat in her house was not working properly and only (   ) water came out of the tap.",
        "choices": ["fallible", "tepid", "murky", "coarse"],
        "answerIndex": 1,
        "translation": "ダーラは長旅の後に熱い風呂に入るのを楽しみにしていた。しかし家の温度調節器が正常に働かず、蛇口からはぬるい水しか出なかった。",
    },
    {
        "stem": "After reading an article (   ) the art and architecture of Italy, Jasmine decided it would be her next travel destination. If it was half as good as the article said, she would definitely enjoy it.",
        "choices": ["ostracizing", "bridling", "lauding", "pulverizing"],
        "answerIndex": 2,
        "translation": "イタリアの美術と建築を賞賛する記事を読んだ後、ジャスミンは次の旅行先をイタリアにしようと決めた。記事に書かれていたことの半分でも本当なら、きっと楽しめるだろう。",
    },
    {
        "stem": "In his first speech, the presidential candidate assured the audience that he was committed to ending both racial and religious (   ) within the government.",
        "choices": ["reverie", "gamut", "tirade", "discrimination"],
        "answerIndex": 3,
        "translation": "大統領候補は初演説で、政府内の人種差別と宗教差別の両方を終わらせる決意だと聴衆に保証した。",
    },
    {
        "stem": "The newspaper columnist is in the habit of making cruel and (   ) remarks about celebrities. However, his recent comments went too far and led to a record number of complaints.",
        "choices": ["derogatory", "bereft", "tactful", "laudatory"],
        "answerIndex": 0,
        "translation": "その新聞コラムニストは、有名人について残酷で軽蔑的な発言をする癖がある。しかし、最近の発言は行き過ぎ、過去最多の苦情につながった。",
    },
    {
        "stem": "Upper management had been trying to keep the pay cuts a secret, but news about them gradually began to (   ) down among the staff. Now, almost everyone knows about the changes.",
        "choices": ["swagger", "reconvene", "implode", "seep"],
        "answerIndex": 3,
        "translation": "経営陣は賃金カットを秘密にしようとしていたが、その知らせは徐々に職員の間へ染み出るように広まった。今ではほとんど全員が変更を知っている。",
    },
    {
        "stem": "The tax officer ordered a full investigation of the company's finances after noticing several (   ) in their annual tax report.",
        "choices": ["barrages", "blemishes", "allegiances", "discrepancies"],
        "answerIndex": 3,
        "translation": "税務署員は、年次納税報告書にいくつかの不一致があることに気づいた後、会社の財務について全面的な調査を命じた。",
    },
    {
        "stem": "When Professor Briggs was sick, the university could not find anyone to (   ) him, so all of his lectures were canceled.",
        "choices": ["sit in for", "talk back to", "walk out on", "pick up on"],
        "answerIndex": 0,
        "translation": "ブリッグス教授が病気になったとき、大学は彼の代理を務める人を見つけられなかったので、彼の講義はすべて中止された。",
    },
    {
        "stem": "When the runner twisted his ankle during the marathon, he was forced to (   ) 10 kilometers before the finish.",
        "choices": ["come around", "spout off", "roll back", "bow out"],
        "answerIndex": 3,
        "translation": "そのランナーはマラソン中に足首をひねり、ゴールまで10キロのところで棄権せざるを得なかった。",
    },
    {
        "stem": "A: Pamela, do you have any ideas for how I can (   ) more business for my café?\nB: Why don't you make some flyers and hand them out on the street? That worked well when I first opened my restaurant.",
        "choices": ["bring in", "mark out", "trim down", "force down"],
        "answerIndex": 0,
        "translation": "A：パメラ、どうしたらカフェにもっと客を呼び込めるか、何かアイデアはある？\nB：チラシを作って通りで配ったら？私が初めてレストランを開いたときにはうまくいったよ。",
    },
    {
        "stem": "Last year, the housing market improved, so many people (   ) low interest rates, which were available through their home loans.",
        "choices": ["got in on", "capitalized on", "wriggled out of", "shrank away from"],
        "answerIndex": 1,
        "translation": "昨年は住宅市場が改善したため、多くの人が住宅ローンで利用できた低金利を活用した。",
    },
]


# meaning, POS, original example, example translation
DETAILS = {
    "amiable": ("愛想のよい、親しみやすい", "形容詞", "The amiable receptionist calmly guided visitors through the crowded lobby.", "その愛想のよい受付係は、混雑したロビーを訪問者に落ち着いて案内した。"),
    "onerous": ("骨の折れる、負担の大きい", "形容詞", "The onerous paperwork delayed the small charity's emergency response.", "負担の大きい書類仕事が、小さな慈善団体の緊急対応を遅らせた。"),
    "sporadic": ("散発的な、断続的な", "形容詞", "Sporadic power failures disrupted several evening classes last winter.", "散発的な停電が、昨冬いくつかの夜間授業を妨げた。"),
    "incongruous": ("場違いな、不調和な", "形容詞", "The incongruous statue looked strange beside the traditional village shrine.", "その場違いな像は、伝統的な村の神社のそばで奇妙に見えた。"),
    "grappled": ("取り組んだ、取っ組み合った", "動詞", "The committee grappled with an ethical problem before approving the experiment.", "委員会は実験を承認する前に、倫理的な問題に取り組んだ。"),
    "dismantled": ("解体した、取り外した", "動詞", "Workers dismantled the unsafe bridge before the rainy season began.", "作業員たちは雨期が始まる前に危険な橋を解体した。"),
    "scuffed": ("こすって傷をつけた", "動詞", "The heavy furniture scuffed the wooden floor during the hurried move.", "急いだ引っ越しの間に、重い家具が木の床をこすって傷つけた。"),
    "reviled": ("激しく非難された、ののしられた", "動詞", "The corrupt official was reviled after investigators revealed the hidden payments.", "隠された支払いを捜査官が明らかにした後、その腐敗した役人は激しく非難された。"),
    "diffused": ("拡散した、広がった", "動詞", "The warm air diffused through the building after the vents were repaired.", "通気口が修理された後、暖かい空気が建物全体に拡散した。"),
    "assailed": ("激しく攻撃した、悩ませた", "動詞", "The hikers were assailed by icy winds throughout the exposed mountain pass.", "ハイカーたちは風雨にさらされた山道で、終始冷たい風に襲われた。"),
    "maligned": ("中傷した", "動詞", "The journalist was maligned online after criticizing the popular proposal.", "その記者は人気のある提案を批判した後、オンラインで中傷された。"),
    "shirked": ("怠った、回避した", "動詞", "The employee shirked his responsibilities whenever the supervisor left the office.", "その従業員は上司が事務所を離れるたびに責任を回避した。"),
    "furtively": ("こっそりと", "副詞", "The student furtively checked the clock while the lecture continued.", "講義が続く間、その生徒はこっそり時計を確認した。"),
    "chronically": ("慢性的に", "副詞", "The region is chronically short of water during the summer months.", "その地域は夏の間、慢性的に水不足である。"),
    "autonomously": ("自律的に", "副詞", "The research robot navigated autonomously through the unfamiliar laboratory.", "その研究ロボットは、見慣れない研究室を自律的に移動した。"),
    "equitably": ("公平に", "副詞", "The mediator distributed the limited relief funds equitably among villages.", "調停者は限られた救援資金を村々に公平に分配した。"),
    "complexions": ("顔色、肌の色", "名詞", "The cosmetics line offers shades designed for a wide range of complexions.", "その化粧品シリーズは幅広い肌の色向けの色合いを提供している。"),
    "shimmers": ("きらめき、揺らめき", "名詞", "At sunset, the lake has gentle shimmers that attract photographers.", "夕暮れ時、その湖には写真家を引きつける穏やかなきらめきがある。"),
    "undertones": ("色調、肌などの下色", "名詞", "The artist mixed several pigments to capture the painting's warm undertones.", "その画家は絵の温かな下色を表すため、いくつかの顔料を混ぜた。"),
    "prophets": ("預言者たち", "名詞", "The museum displays manuscripts describing prophets from several ancient traditions.", "その博物館は、いくつかの古代の伝統に登場する預言者を記した写本を展示している。"),
    "restitution": ("返還、賠償", "名詞", "The court ordered restitution for families whose land had been seized illegally.", "裁判所は土地を不法に奪われた家族への賠償を命じた。"),
    "vanity": ("虚栄心、うぬぼれ", "名詞", "His vanity prevented him from admitting that the first plan had failed.", "彼の虚栄心のため、最初の計画が失敗したと認められなかった。"),
    "enunciation": ("発音、明瞭な発声", "名詞", "Clear enunciation helped the actor deliver every line to the audience.", "明瞭な発声のおかげで、その俳優は観客に一言一言を届けられた。"),
    "ambiguity": ("曖昧さ", "名詞", "The contract's ambiguity led both companies to interpret the clause differently.", "契約の曖昧さのため、両社はその条項を異なるように解釈した。"),
    "debonair": ("洗練された、愛想のよい", "形容詞", "The debonair host welcomed every guest with effortless confidence.", "その洗練された主人は、自然な自信をもってすべての客を迎えた。"),
    "bucolic": ("牧歌的な、田園の", "形容詞", "The hikers photographed a bucolic valley surrounded by quiet hills.", "ハイカーたちは静かな丘に囲まれた牧歌的な谷を撮影した。"),
    "erroneous": ("誤った", "形容詞", "The analyst corrected an erroneous figure before publishing the financial report.", "分析官は財務報告書を公表する前に、誤った数値を訂正した。"),
    "pernicious": ("有害な、悪影響を及ぼす", "形容詞", "The doctor warned that the pernicious habit could damage the patient's heart.", "医師は、その有害な習慣が患者の心臓を傷つける可能性があると警告した。"),
    "quagmire": ("泥沼、難局", "名詞", "The peacekeeping mission became a political quagmire after the agreement collapsed.", "和平維持活動は合意が崩壊した後、政治的な泥沼になった。"),
    "menace": ("脅威", "名詞", "The abandoned factory became a serious menace to children in the neighborhood.", "廃工場は近隣の子どもたちにとって深刻な脅威になった。"),
    "mirage": ("蜃気楼、幻想", "名詞", "The travelers mistook a distant lake for a mirage in the desert.", "旅行者たちは砂漠の遠くの湖を蜃気楼と間違えた。"),
    "plateau": ("高原、停滞期", "名詞", "After years of rapid growth, the company reached a sales plateau.", "急成長が何年も続いた後、その会社の売上は停滞期に入った。"),
    "persuade": ("説得する", "動詞", "The nurse managed to persuade the frightened child to accept treatment.", "看護師は怯えた子どもを説得して治療を受けさせることに成功した。"),
    "accentuate": ("強調する", "動詞", "The lighting was designed to accentuate the sculpture's delicate details.", "その照明は彫刻の繊細な細部を強調するよう設計された。"),
    "inhibit": ("抑制する、妨げる", "動詞", "Fear of criticism can inhibit young researchers from sharing useful ideas.", "批判への恐れは、若い研究者が有益な考えを共有するのを妨げることがある。"),
    "absolve": ("免除する、潔白にする", "動詞", "The evidence did not absolve the manager of responsibility for the accident.", "その証拠は事故の責任から管理者を免除するものではなかった。"),
    "condolences": ("哀悼、弔意", "名詞", "The ambassador sent condolences to the victims' families after the disaster.", "大使は災害の後、犠牲者の家族に哀悼の意を伝えた。"),
    "prologues": ("序章、前口上", "名詞", "The anthology includes prologues that explain each story's historical setting.", "その作品集には、各物語の歴史的背景を説明する序章が含まれている。"),
    "pretensions": ("気取り、主張、権利", "名詞", "The critic mocked the restaurant's pretensions to culinary greatness.", "その批評家は、料理の偉大さを主張するレストランの気取りを笑った。"),
    "tribulations": ("苦難", "名詞", "The memoir describes the family's tribulations during the long civil conflict.", "その回想録は長い内戦中の家族の苦難を描いている。"),
    "deplete": ("枯渇させる", "動詞", "The prolonged drought will deplete the reservoir before autumn arrives.", "長引く干ばつは秋が来る前に貯水池を枯渇させるだろう。"),
    "augment": ("増やす、強化する", "動詞", "The museum plans to augment its collection with several regional artifacts.", "その博物館は地域の遺物をいくつか加えて収蔵品を増やす計画だ。"),
    "smother": ("窒息させる、抑え込む", "動詞", "The blanket helped smother the small flames before they spread.", "毛布が火が広がる前に小さな炎を消すのに役立った。"),
    "repress": ("抑圧する、押し殺す", "動詞", "The regime tried to repress public criticism through strict censorship.", "その政権は厳しい検閲によって世論の批判を抑圧しようとした。"),
    "dexterity": ("器用さ、手先の巧みさ", "名詞", "The surgeon's dexterity was essential during the delicate operation.", "その外科医の手先の器用さは、繊細な手術中に不可欠だった。"),
    "contrition": ("深い後悔、悔恨", "名詞", "The defendant's visible contrition influenced the judge's final decision.", "被告の目に見える悔恨が、裁判官の最終判断に影響した。"),
    "mayhem": ("大混乱、騒乱", "名詞", "A sudden alarm caused mayhem as passengers rushed toward the exits.", "突然の警報で乗客が出口へ殺到し、大混乱が起きた。"),
    "aridity": ("乾燥、無味乾燥", "名詞", "The aridity of the region makes agriculture difficult without irrigation.", "その地域の乾燥のため、灌漑なしで農業を行うのは難しい。"),
    "bewail": ("嘆き悲しむ", "動詞", "The poet continued to bewail the loss of his homeland in verse.", "その詩人は詩の中で祖国を失ったことを嘆き続けた。"),
    "relinquish": ("手放す、放棄する", "動詞", "The founder agreed to relinquish authority so younger leaders could serve.", "創設者は、若い指導者が務められるよう権限を手放すことに同意した。"),
    "transpose": ("入れ替える、移調する", "動詞", "The editor had to transpose two paragraphs to improve the article's flow.", "編集者は記事の流れを改善するため、2つの段落を入れ替えなければならなかった。"),
    "disparage": ("けなす、軽視する", "動詞", "It is unfair to disparage a proposal before examining its evidence.", "根拠を調べる前に提案をけなすのは不公平だ。"),
    "opaque": ("不透明な、理解しにくい", "形容詞", "The opaque explanation left investors uncertain about the project's costs.", "不透明な説明のため、投資家はプロジェクトの費用について確信を持てなかった。"),
    "avaricious": ("強欲な", "形容詞", "The avaricious landlord raised rents despite the tenants' financial hardship.", "その強欲な家主は、借主が経済的に苦しいにもかかわらず家賃を上げた。"),
    "dank": ("湿っぽくて薄暗い", "形容詞", "The explorers rested in a dank cave during the afternoon storm.", "探検家たちは午後の嵐の間、湿っぽく薄暗い洞窟で休んだ。"),
    "venturesome": ("冒険好きな、向こう見ずな", "形容詞", "The venturesome travelers crossed the remote desert without a guide.", "その冒険好きな旅行者たちは、案内人なしで人里離れた砂漠を横断した。"),
    "consummate": ("完璧な、熟達した", "形容詞", "The pianist gave a consummate performance despite the difficult acoustics.", "そのピアニストは難しい音響条件にもかかわらず完璧な演奏を披露した。"),
    "amateurish": ("素人っぽい、未熟な", "形容詞", "The amateurish video lacked the careful editing expected by viewers.", "その素人っぽい動画には、視聴者が期待する丁寧な編集が欠けていた。"),
    "malignant": ("悪性の、有害な", "形容詞", "Doctors removed the malignant growth before it spread to nearby tissue.", "医師たちは周辺組織へ広がる前に悪性の腫瘍を取り除いた。"),
    "neurotic": ("神経症的な、神経質な", "形容詞", "His neurotic concern about minor errors slowed the entire review process.", "些細な誤りへの彼の神経質な心配が、審査全体を遅らせた。"),
    "fallible": ("誤りやすい", "形容詞", "Even experienced judges are fallible when the evidence is incomplete.", "経験豊富な裁判官でさえ、証拠が不十分なら誤ることがある。"),
    "tepid": ("なまぬるい、熱意のない", "形容詞", "The soup was tepid because it had been left on the counter.", "そのスープはカウンターに置かれていたため、なまぬるかった。"),
    "murky": ("濁った、薄暗い", "形容詞", "The investigators could not see through the river's murky water.", "捜査官たちは川の濁った水を通して見ることができなかった。"),
    "coarse": ("粗い、下品な", "形容詞", "The blanket's coarse fabric irritated the child's sensitive skin.", "その毛布の粗い布地が、子どもの敏感な肌を刺激した。"),
    "ostracizing": ("仲間外れにしている", "動詞", "The group was ostracizing a new member for asking difficult questions.", "そのグループは難しい質問をした新しいメンバーを仲間外れにしていた。"),
    "bridling": ("腹を立てて抑える、手綱を取る", "動詞", "The horse was bridling at the unfamiliar noise near the stable.", "その馬は厩の近くの聞き慣れない音に腹を立てていた。"),
    "lauding": ("賞賛している", "動詞", "Several respected reviewers were lauding the director's thoughtful documentary.", "何人もの著名な批評家が、その監督の思慮深いドキュメンタリーを賞賛していた。"),
    "pulverizing": ("粉砕している", "動詞", "The industrial machine is pulverizing the stone into fine powder.", "その工業用機械は石を細かい粉末へ粉砕している。"),
    "reverie": ("夢想、空想", "名詞", "She drifted into a reverie while watching clouds above the meadow.", "彼女は牧草地の上の雲を見ながら夢想にふけった。"),
    "gamut": ("範囲、全領域", "名詞", "The exhibition covers the full gamut of modern photographic techniques.", "その展覧会は現代写真技術の全範囲を扱っている。"),
    "tirade": ("長広舌、激しい非難", "名詞", "The manager launched a furious tirade against the careless contractor.", "その管理者は不注意な請負業者に対して激しい非難を浴びせた。"),
    "discrimination": ("差別、識別", "名詞", "The new policy prohibits discrimination in hiring and promotion decisions.", "新しい方針は採用や昇進の判断における差別を禁じている。"),
    "derogatory": ("軽蔑的な", "形容詞", "The report contained derogatory comments about several minority communities.", "その報告書にはいくつかの少数派コミュニティーに対する軽蔑的なコメントが含まれていた。"),
    "bereft": ("奪われた、欠いている", "形容詞", "The village was bereft of medical supplies after the roads closed.", "道路が閉鎖された後、その村は医療用品を欠いていた。"),
    "tactful": ("機転の利く、如才ない", "形容詞", "The tactful interviewer changed the subject before the guest became upset.", "その機転の利くインタビュアーは、客が動揺する前に話題を変えた。"),
    "laudatory": ("賞賛する、賞賛の", "形容詞", "The laudatory review praised the scientist's careful research.", "その賞賛に満ちた批評は、その科学者の周到な研究を称賛した。"),
    "swagger": ("いばって歩く、威張る", "動詞", "The victorious athlete began to swagger through the crowded stadium.", "勝利した選手は混雑した競技場をいばって歩き始めた。"),
    "reconvene": ("再招集する、再開する", "動詞", "The committee will reconvene next week after reviewing the new evidence.", "委員会は新しい証拠を検討した後、来週再招集される。"),
    "implode": ("内破する、突然崩壊する", "動詞", "The unstable structure could implode if engineers ignored the warning signs.", "技術者が警告の兆候を無視すれば、その不安定な構造物は内破する可能性がある。"),
    "seep": ("染み出る、徐々に広まる", "動詞", "Rumors began to seep through the office despite management's warnings.", "経営陣の警告にもかかわらず、うわさがオフィス中に徐々に広まった。"),
    "barrages": ("砲撃、集中質問", "名詞", "The spokesperson faced barrages of questions after the policy announcement.", "政策発表の後、その報道官は質問の集中砲火を浴びた。"),
    "blemishes": ("しみ、欠点", "名詞", "The editor removed minor blemishes from the scanned historical photograph.", "編集者はスキャンした歴史写真から小さな汚れを取り除いた。"),
    "allegiances": ("忠誠、所属", "名詞", "The treaty forced several regional leaders to reconsider their allegiances.", "その条約は複数の地域指導者に忠誠の対象を考え直させた。"),
    "discrepancies": ("相違、不一致", "名詞", "Auditors discovered discrepancies between the invoices and the delivery records.", "監査人たちは請求書と納品記録の間に不一致を発見した。"),
    "sit in for": ("〜の代理を務める", "句動詞", "A senior lecturer agreed to sit in for the absent professor.", "上級講師は欠席した教授の代理を務めることに同意した。"),
    "talk back to": ("〜に口答えする", "句動詞", "The student apologized after she started to talk back to her teacher.", "その生徒は教師に口答えし始めた後、謝罪した。"),
    "walk out on": ("〜を見捨てる、途中で放棄する", "句動詞", "He promised never to walk out on his family during difficult times.", "彼は困難な時期に家族を決して見捨てないと約束した。"),
    "pick up on": ("〜に気づく、理解する", "句動詞", "The detective will quickly pick up on a contradiction in the witness's story.", "その刑事は証人の話の矛盾にすぐ気づくだろう。"),
    "come around": ("意識を取り戻す、考えを変える", "句動詞", "The patient began to come around after the emergency treatment.", "その患者は緊急治療の後、意識を取り戻し始めた。"),
    "spout off": ("べらべらしゃべる、まくしたてる", "句動詞", "The commentator likes to spout off without checking the available facts.", "その評論家は入手できる事実を確認せずにまくしたてるのが好きだ。"),
    "roll back": ("巻き戻す、撤回する", "句動詞", "The city decided to roll back the fee after residents protested.", "住民が抗議した後、市はその料金を撤回することに決めた。"),
    "bow out": ("身を引く、辞退する", "句動詞", "The injured runner had to bow out before reaching the final stage.", "負傷したランナーは最終区間に達する前に棄権しなければならなかった。"),
    "bring in": ("もたらす、呼び込む", "句動詞", "The festival should bring in visitors from neighboring towns.", "その祭りは近隣の町から訪問者を呼び込むはずだ。"),
    "mark out": ("印を付ける、選び出す", "句動詞", "The coach used cones to mark out a safe practice area.", "コーチはコーンを使って安全な練習区域の印を付けた。"),
    "trim down": ("削減する、細くする", "句動詞", "The agency must trim down its budget before the next fiscal year.", "その機関は次の会計年度の前に予算を削減しなければならない。"),
    "force down": ("無理に飲み込ませる", "句動詞", "The nurse could not force down the medicine while the child cried.", "子どもが泣いている間、看護師は薬を無理に飲ませることができなかった。"),
    "got in on": ("参加した、便乗した", "句動詞", "Several neighbors got in on the community garden project last spring.", "昨春、近所の人々が何人も地域の菜園プロジェクトに参加した。"),
    "capitalized on": ("利用して利益を得た", "句動詞", "The small retailer capitalized on the sudden demand for repair services.", "その小売店は修理サービスへの突然の需要を利用して利益を得た。"),
    "wriggled out of": ("うまく逃れた", "句動詞", "The defendant wriggled out of the question by changing the subject.", "被告は話題を変えることで、その質問をうまく逃れた。"),
    "shrank away from": ("〜からひるんで避けた", "句動詞", "The volunteer never shrank away from difficult conversations with residents.", "そのボランティアは住民との難しい会話を決して避けなかった。"),
}


CORE_IMAGES = {
    "sit in for": {"chain": [{"term": "sit", "gloss": "座る、代わる位置に入る"}, {"term": "in", "gloss": "中へ入り"}, {"term": "for", "gloss": "対象の代わりに"}, {"gloss": "代理を務める"}]},
    "talk back to": {"chain": [{"term": "talk", "gloss": "話す"}, {"term": "back", "gloss": "返して"}, {"term": "to", "gloss": "相手へ"}, {"gloss": "相手に口答えする"}]},
    "walk out on": {"chain": [{"term": "walk", "gloss": "歩く"}, {"term": "out", "gloss": "外へ"}, {"term": "on", "gloss": "対象を残して"}, {"gloss": "相手を見捨てて立ち去る"}]},
    "pick up on": {"chain": [{"term": "pick", "gloss": "拾う"}, {"term": "up", "gloss": "取り上げて"}, {"term": "on", "gloss": "対象に"}, {"gloss": "手がかりに気づく"}]},
    "come around": {"chain": [{"term": "come", "gloss": "来る"}, {"term": "around", "gloss": "周囲を回って"}, {"gloss": "元の意識や考えへ戻って"}, {"gloss": "意識を取り戻す、考えを変える"}]},
    "spout off": {"chain": [{"term": "spout", "gloss": "噴き出す"}, {"term": "off", "gloss": "外へ"}, {"gloss": "言葉を次々に吐き出して"}, {"gloss": "べらべらしゃべる"}]},
    "roll back": {"chain": [{"term": "roll", "gloss": "転がす"}, {"term": "back", "gloss": "後ろへ"}, {"gloss": "前の状態へ戻して"}, {"gloss": "撤回する、巻き戻す"}]},
    "bow out": {"chain": [{"term": "bow", "gloss": "身をかがめる"}, {"term": "out", "gloss": "外へ"}, {"gloss": "場の外へ身を引いて"}, {"gloss": "辞退する、棄権する"}]},
    "bring in": {"chain": [{"term": "bring", "gloss": "運ぶ"}, {"term": "in", "gloss": "中へ"}, {"gloss": "客や利益を中へもたらして"}, {"gloss": "呼び込む、もたらす"}]},
    "mark out": {"chain": [{"term": "mark", "gloss": "印を付ける"}, {"term": "out", "gloss": "外へ区切って"}, {"gloss": "区域を示して"}, {"gloss": "印を付ける、選び出す"}]},
    "trim down": {"chain": [{"term": "trim", "gloss": "整えて切る"}, {"term": "down", "gloss": "下げて"}, {"gloss": "量や大きさを減らして"}, {"gloss": "削減する"}]},
    "force down": {"chain": [{"term": "force", "gloss": "力を加える"}, {"term": "down", "gloss": "下へ"}, {"gloss": "口から下へ押し込んで"}, {"gloss": "無理に飲み込ませる"}]},
    "got in on": {"chain": [{"term": "got", "gloss": "得て、入り"}, {"term": "in", "gloss": "中へ"}, {"term": "on", "gloss": "対象に加わって"}, {"gloss": "機会や計画に参加した"}]},
    "capitalized on": {"chain": [{"term": "capitalize", "gloss": "資本化する"}, {"term": "on", "gloss": "対象を利用して"}, {"gloss": "機会を利益に結びつけて"}, {"gloss": "利用して利益を得た"}]},
    "wriggled out of": {"chain": [{"term": "wriggle", "gloss": "身をくねらせる"}, {"term": "out", "gloss": "外へ抜けて"}, {"term": "of", "gloss": "対象から"}, {"gloss": "困難や責任を巧みに逃れた"}]},
    "shrank away from": {"chain": [{"term": "shrink", "gloss": "縮む"}, {"term": "away", "gloss": "遠ざかって"}, {"term": "from", "gloss": "対象から"}, {"gloss": "恐れて避けた"}]},
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
        raise ValueError("模試 第8回は25問である必要があります")

    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != len(set(choices)):
        raise ValueError("選択肢に重複があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")

    seen_surfaces: dict[str, str] = {}
    seen_examples: dict[str, str] = {}
    for index, question in enumerate(QUESTIONS, start=1):
        if len(question["choices"]) != 4 or question["answerIndex"] not in range(4):
            raise ValueError(f"Q{index}の4択または正答位置が不正です")
        if len(BLANK_RE.findall(question["stem"])) != 1:
            raise ValueError(f"Q{index}の空所が1か所ではありません")
        if any(re.search(rf"\b{re.escape(choice)}\b", question["stem"], flags=re.IGNORECASE) for choice in question["choices"]):
            raise ValueError(f"Q{index}の選択肢が設問文に含まれています")
        if re.search(r"\(\s*\)|（\s*）", question["translation"]):
            raise ValueError(f"Q{index}の和訳に空所記号があります")

    for phrase in choices:
        if " " in phrase and phrase not in CORE_IMAGES:
            raise ValueError(f"熟語の核心イメージがありません: {phrase}")

    meta = {
        "grade": "英検1級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "ユーザー提供画像（原本表記は模試第3回）を、依頼により模試第8回として構造化。既存語句との重複を避けるため一部選択肢を置換",
        "counts": {"words": 84, "idioms": 16, "total": 100},
    }
    question_data = {
        "meta": meta,
        "questions": [
            {"q": index, **question}
            for index, question in enumerate(QUESTIONS, start=1)
        ],
    }

    words = []
    idioms = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            meaning, pos, example, example_translation = DETAILS[choice]
            if len(WORD_RE.findall(example)) < 8:
                raise ValueError(f"{choice}の例文が8語未満です")
            if len(re.findall(re.escape(choice), example, flags=re.IGNORECASE)) != 1:
                raise ValueError(f"{choice}の例文に見出し語句が1回ありません")
            example_key = re.sub(re.escape(choice), "( )", example, count=1, flags=re.IGNORECASE)
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
    write_json(DATA_DIR / "vocab_1_mock-8.json", vocab)
    write_json(DATA_DIR / "questions_1_mock-8.json", questions)
    print("mock-8: 25 questions / 100 items (84 words, 16 idioms)")


if __name__ == "__main__":
    main()
