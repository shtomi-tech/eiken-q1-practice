"""ユーザー提供画像の英検1級模試を、模試第6回基準で構造化する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-9"
BLANK_RE = re.compile(r"\(\s+\)")
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


QUESTIONS = [
    {
        "stem": "The new modern art sculpture in the town center cost a lot of money. However, many local people regard it as an (   ) and have asked for it to be removed.",
        "choices": ["addendum", "monstrosity", "appendage", "infringement"],
        "answerIndex": 1,
        "translation": "町の中心部に新しく設置された現代美術の彫刻には多額の費用がかかった。しかし、多くの地元住民はそれをひどく醜いものと見なし、撤去を求めている。",
    },
    {
        "stem": "After the public heard Mayor Wilson expressing his racist and sexist views in a recording, he was (   ) by almost everyone.",
        "choices": ["exonerated", "calibrated", "repainted", "vilified"],
        "answerIndex": 3,
        "translation": "ウィルソン市長が録音の中で人種差別的・性差別的な見解を述べているのを世間が聞いた後、彼はほとんど全員から激しく非難された。",
    },
    {
        "stem": "Before they got their new heating system, the upstairs of their house was always hotter than the basement. Now, though, the heat is (   ) much more evenly than it was before.",
        "choices": ["dispersed", "attacked", "denigrated", "obstructed"],
        "answerIndex": 0,
        "translation": "新しい暖房システムを取り付ける前は、家の2階がいつも地下室より暑かった。しかし今では、熱が以前よりずっと均等に分散している。",
    },
    {
        "stem": "No one noticed as the magician (   ) placed the ball into his jacket pocket while pretending to take something else out of it.",
        "choices": ["stealthily", "persistently", "independently", "impartially"],
        "answerIndex": 0,
        "translation": "その手品師が別の物を取り出すふりをしながら、こっそりボールを上着のポケットに入れたことに誰も気づかなかった。",
    },
    {
        "stem": "This skincare product is recommended for those with lighter (   ) who tend to burn more easily in the sun than those with darker skin.",
        "choices": ["hues", "ornaments", "spectacles", "prophecies"],
        "answerIndex": 0,
        "translation": "このスキンケア製品は、肌の色が濃い人よりも日光で焼けやすい、肌の色合いが明るい人に推奨される。",
    },
    {
        "stem": "In the past, it was usual for people in some countries to take (   ) lessons in order to get rid of their regional accents. However, these days, such lessons are less common.",
        "choices": ["arbitration", "conceit", "pronunciation", "obliquity"],
        "answerIndex": 2,
        "translation": "かつて一部の国では、地域なまりをなくすために発音のレッスンを受けるのが普通だった。しかし最近では、そのようなレッスンはあまり一般的ではない。",
    },
    {
        "stem": "This painting by the famous artist depicts a typical (   ) scene of green fields and shepherds tending their sheep, with a little church in the background.",
        "choices": ["rustic", "pastoral", "fallacious", "deleterious"],
        "answerIndex": 1,
        "translation": "その有名な画家の絵は、緑の野原と羊の世話をする羊飼い、背景の小さな教会がある典型的な牧歌的風景を描いている。",
    },
    {
        "stem": "A: Oh, no. The heavy rain seems to have turned the rugby pitch into a (   ).\nB: I hope it dries out before the match on Saturday. It looks really slippery.",
        "choices": ["bog", "hazard", "illusion", "stagnation"],
        "answerIndex": 0,
        "translation": "A：ああ、大変。激しい雨でラグビー場が泥沼になったようだ。\nB：土曜日の試合までに乾くといいね。本当に滑りやすそうだ。",
    },
    {
        "stem": "Isaiah's friends tried to (   ) him into going to the party with them, but nothing they said could change his mind. He knew he needed to study for the test.",
        "choices": ["inveigle", "intensify", "disassociate", "vindicate"],
        "answerIndex": 0,
        "translation": "イザヤの友人たちは彼を巧みに説得して一緒にパーティーへ行こうとしたが、何を言っても彼の考えを変えられなかった。彼はテストの勉強が必要だと分かっていた。",
    },
    {
        "stem": "After the accident, the Prime Minister offered his (   ) to those who had lost their lives as well as their families. He also said he was praying for the speedy recovery of the injured.",
        "choices": ["sympathies", "prefaces", "aspirations", "adversities"],
        "answerIndex": 0,
        "translation": "事故の後、首相は命を失った人々とその家族に弔意を表した。また、負傷者が早く回復するよう祈っていると述べた。",
    },
    {
        "stem": "As well as Margo's jewelry collection, the thief also (   ) some very valuable works of art.",
        "choices": ["derived", "dispelled", "purloined", "embedded"],
        "answerIndex": 2,
        "translation": "その泥棒はマルゴの宝石コレクションだけでなく、とても貴重な美術品も盗んだ。",
    },
    {
        "stem": "The princess carried a (   ) lace handkerchief embroidered with a floral design. It gave her a soft and pleasing look.",
        "choices": ["cavernous", "deranged", "delicate", "hedonistic"],
        "answerIndex": 2,
        "translation": "その王女は花柄の刺繍が施された繊細なレースのハンカチを持っていた。それは彼女に柔らかく感じのよい印象を与えた。",
    },
    {
        "stem": "Although the company offered a pay increase, it was not enough to (   ) the angry union members. They will go on strike tomorrow if they do not get a better offer.",
        "choices": ["mollify", "retard", "encroach", "harass"],
        "answerIndex": 0,
        "translation": "会社は賃上げを提示したものの、怒った組合員たちをなだめるには不十分だった。もっとよい提案がなければ、彼らは明日ストライキを行う。",
    },
    {
        "stem": "The travel company offers exciting trips to the Amazon rainforest that are ideal for (   ) travelers who enjoy an adventure and do not mind sleeping in a tent.",
        "choices": ["indolent", "penurious", "damp", "adventurous"],
        "answerIndex": 3,
        "translation": "その旅行会社は、冒険を楽しみ、テントで寝ることを苦にしない冒険好きな旅行者に最適な、アマゾン熱帯雨林への刺激的な旅行を提供している。",
    },
    {
        "stem": "Despite the fact that it was his first major acting part, Michael performed the role of Hamlet with (   ) skill. In fact, he was so good that the audience gave him a standing ovation.",
        "choices": ["masterful", "substandard", "benign", "erratic"],
        "answerIndex": 0,
        "translation": "それが初めての主要な演技の役だったにもかかわらず、マイケルは熟達した技量でハムレットを演じた。実際、あまりに見事だったので観客はスタンディングオベーションを送った。",
    },
    {
        "stem": "The scientist jumped at the chance to speak at the global conference on climate change and accepted the invitation with (   ).",
        "choices": ["lethargy", "eagerness", "revulsion", "resilience"],
        "answerIndex": 1,
        "translation": "その科学者は気候変動に関する国際会議で話す機会に飛びつき、熱意をもって招待を受け入れた。",
    },
    {
        "stem": "A: So, what do you (   ) your success in business to?\nB: Well, it’s basically the result of one thing — hard work.",
        "choices": ["attribute", "deter", "slacken", "mock"],
        "answerIndex": 0,
        "translation": "A：では、あなたは仕事での成功を何のおかげだと考えていますか。\nB：そうですね、基本的には一つのこと、つまり努力の結果です。",
    },
    {
        "stem": "Next week, party members will gather at the convention to (   ) a new leader. Most experts believe that Jane Parker is the person who will be chosen.",
        "choices": ["integrate", "divert", "anoint", "irk"],
        "answerIndex": 2,
        "translation": "来週、党員たちは大会に集まり、新しい指導者を指名する。大半の専門家は、選ばれるのはジェーン・パーカーだと考えている。",
    },
    {
        "stem": "In the past, women in many societies were expected to accept an inferior role in a marriage and be (   ) to their husbands. This way of thinking, however, is now becoming a thing of the past.",
        "choices": ["thrifty", "inactive", "subservient", "sedentary"],
        "answerIndex": 2,
        "translation": "かつて多くの社会では、女性は結婚生活で劣った役割を受け入れ、夫に従属することを期待されていた。しかし、このような考え方は今では過去のものになりつつある。",
    },
    {
        "stem": "After arresting the man, Officer Templeton (   ) him. She felt something in his pocket, and that was how she found the drugs.",
        "choices": ["scolded", "glossed", "indented", "frisked"],
        "answerIndex": 3,
        "translation": "その男を逮捕した後、テンプルトン巡査は彼の身体検査をした。彼女は彼のポケットに何かを感じ、それで薬物を見つけた。",
    },
    {
        "stem": "Tina listened in (   ) as the orchestra began to play, and the beautiful music transported her to another world.",
        "choices": ["agitation", "indifference", "ascension", "rapture"],
        "answerIndex": 3,
        "translation": "オーケストラが演奏を始めると、ティナは恍惚として耳を傾け、その美しい音楽によって別世界へ運ばれた。",
    },
    {
        "stem": "Cheryl earned so little money at her company that she was unable to pay all her bills, so she (   ) her income by getting a part-time job in a supermarket.",
        "choices": ["forked over", "built up", "shook off", "riffled through"],
        "answerIndex": 1,
        "translation": "シェリルは会社でほとんどお金を稼げず、請求書をすべて払えなかったので、スーパーでアルバイトをして収入を増やした。",
    },
    {
        "stem": "The human resources director has decided to (   ) her efforts to provide long-term training for the new employees. Every month, she plans to review and improve the program further.",
        "choices": ["scale back", "sift through", "slow down", "ratchet up"],
        "answerIndex": 3,
        "translation": "人事部長は、新入社員向けの長期研修を提供する取り組みを段階的に強化することに決めた。毎月、プログラムを見直し、さらに改善する計画である。",
    },
    {
        "stem": "The hikers realized they had gone the wrong way when the track they were following became narrower and (   ). There was no way through the forest, so they turned back.",
        "choices": ["opened out", "acted up", "pitched in", "petered out"],
        "answerIndex": 3,
        "translation": "ハイカーたちは、たどっていた道がだんだん狭くなり、次第に消えていったとき、道を間違えたことに気づいた。森を抜ける道はなかったので、彼らは引き返した。",
    },
    {
        "stem": "The lawyer said that the charges against her client were (   ). She accused the police of presenting false evidence just to get a quick conviction.",
        "choices": ["trumped up", "belted out", "spurred on", "carted off"],
        "answerIndex": 0,
        "translation": "その弁護士は、依頼人に対する容疑はでっち上げられたものだと述べた。彼女は、早期の有罪判決を得るために警察が偽の証拠を提示したと非難した。",
    },
]


# meaning, POS, original example, example translation
DETAILS = {
    "addendum": ("付録、追補", "名詞", "The editor attached an addendum clarifying several statistics in the annual report.", "編集者は年次報告書のいくつかの統計を明確にする追補を添付した。"),
    "monstrosity": ("怪物のようなもの、ひどく醜いもの", "名詞", "Residents considered the enormous concrete tower a monstrosity in their historic neighborhood.", "住民たちは、巨大なコンクリート塔を歴史ある地区のひどく醜いものと考えた。"),
    "appendage": ("付属物、付加物", "名詞", "The decorative appendage served no practical purpose on the ceremonial vehicle.", "その装飾的な付属物は、儀礼用車両で実用的な目的を果たさなかった。"),
    "infringement": ("侵害", "名詞", "The court ruled that the unauthorized recording constituted an infringement of copyright law.", "裁判所は、無断録音が著作権法の侵害に当たると判断した。"),
    "exonerated": ("無実を証明された、潔白にされた", "動詞", "New evidence exonerated the driver after months of legal uncertainty.", "新たな証拠により、何か月もの法的な不確実さの後で運転手の潔白が証明された。"),
    "calibrated": ("調整した、較正した", "動詞", "Technicians calibrated the instrument before collecting measurements in the laboratory.", "技術者たちは研究室で測定値を集める前に、その器具を調整した。"),
    "repainted": ("塗り直した", "動詞", "The crew repainted the faded hallway before the museum reopened.", "作業員たちは博物館が再開する前に色あせた廊下を塗り直した。"),
    "vilified": ("激しく非難された、中傷された", "動詞", "The whistleblower was vilified online after exposing the fraudulent scheme.", "その内部告発者は詐欺計画を暴露した後、ネット上で激しく非難された。"),
    "dispersed": ("分散させた、分散した", "動詞", "The ventilation system dispersed warm air throughout the building evenly.", "換気システムは暖かい空気を建物全体に均等に分散させた。"),
    "attacked": ("攻撃した", "動詞", "The journalists were attacked by trolls after publishing the investigation.", "その記者たちは調査記事を発表した後、荒らしに攻撃された。"),
    "denigrated": ("けなした、軽視した", "動詞", "The critic denigrated the proposal without addressing its carefully documented evidence.", "その批評家は、注意深く記録された根拠に触れずに提案をけなした。"),
    "obstructed": ("妨げた、ふさいだ", "動詞", "Fallen branches obstructed traffic on the mountain road after the storm.", "嵐の後、倒れた枝が山道の交通を妨げた。"),
    "stealthily": ("こっそりと", "副詞", "The cat stealthily crossed the kitchen while everyone watched television.", "皆がテレビを見ている間、その猫はこっそり台所を横切った。"),
    "persistently": ("しつこく、粘り強く", "副詞", "The reporter persistently requested documents despite repeated refusals from officials.", "その記者は役人から何度も拒否されたにもかかわらず、粘り強く書類を求めた。"),
    "independently": ("独立して、自力で", "副詞", "The satellite can independently adjust its position during the mission.", "その衛星は任務中に自力で位置を調整できる。"),
    "impartially": ("公平に", "副詞", "The mediator listened impartially to both sides before proposing a settlement.", "調停者は解決策を提案する前に双方の話を公平に聞いた。"),
    "hues": ("色合い", "名詞", "The designer selected soft hues that complemented the room's natural light.", "デザイナーは部屋の自然光に合う柔らかな色合いを選んだ。"),
    "ornaments": ("装飾品", "名詞", "The family stored fragile ornaments carefully after removing them from the tree.", "その家族は木から取り外した壊れやすい装飾品を注意深く保管した。"),
    "spectacles": ("眼鏡、保護眼鏡", "名詞", "The optician recommended protective spectacles for workers in the factory.", "眼鏡店員は工場の作業員に保護眼鏡を勧めた。"),
    "prophecies": ("予言", "名詞", "Ancient prophecies were recorded on tablets preserved in the temple.", "古代の予言は、寺院に保存された石板に記録されていた。"),
    "arbitration": ("仲裁", "名詞", "The two companies entered arbitration after negotiations over the contract failed.", "契約をめぐる交渉が失敗した後、その2社は仲裁に入った。"),
    "conceit": ("うぬぼれ、思い上がり", "名詞", "His conceit made him dismiss helpful advice from experienced colleagues.", "彼のうぬぼれのため、経験豊かな同僚からの有益な助言を退けてしまった。"),
    "pronunciation": ("発音", "名詞", "Clear pronunciation allowed the tour guide to communicate across languages.", "明瞭な発音のおかげで、そのツアーガイドは言語の壁を越えて意思疎通できた。"),
    "obliquity": ("斜め、偏り、婉曲さ", "名詞", "The report's obliquity made the author's criticism difficult to identify.", "その報告書の婉曲さのため、著者の批判を特定するのは難しかった。"),
    "rustic": ("田舎風の、素朴な", "形容詞", "The restaurant's rustic interior featured wooden tables and handmade pottery.", "そのレストランの素朴な内装には、木のテーブルと手作りの陶器があった。"),
    "pastoral": ("牧歌的な、田園の", "形容詞", "The painter captured a pastoral scene beneath a cloudless summer sky.", "その画家は雲一つない夏空の下の牧歌的な風景を描いた。"),
    "fallacious": ("誤った、論理的に誤った", "形容詞", "The committee rejected the fallacious argument after checking the underlying data.", "委員会は基礎となるデータを確認した後、その誤った議論を退けた。"),
    "deleterious": ("有害な", "形容詞", "Long-term exposure to the chemical can have deleterious effects on health.", "その化学物質に長期間さらされると、健康に有害な影響が出る可能性がある。"),
    "bog": ("沼、泥沼", "名詞", "Heavy rain turned the unpaved road into a muddy bog overnight.", "激しい雨で未舗装道路は一晩のうちに泥沼になった。"),
    "hazard": ("危険、危険要因", "名詞", "The exposed wires posed a serious hazard to curious children nearby.", "むき出しの電線は、近くにいる好奇心旺盛な子どもたちに深刻な危険をもたらした。"),
    "illusion": ("幻想、錯覚", "名詞", "The distant lights were an illusion caused by heat above the highway.", "遠くの明かりは、高速道路上の熱によって生じた錯覚だった。"),
    "stagnation": ("停滞", "名詞", "Economic stagnation weakened local businesses and reduced employment opportunities.", "経済の停滞は地元企業を弱体化させ、雇用機会を減らした。"),
    "inveigle": ("巧みに説得して誘い込む", "動詞", "The salesman tried to inveigle customers into purchasing unnecessary insurance.", "その販売員は顧客を巧みに説得して不要な保険を買わせようとした。"),
    "intensify": ("強める、激しくする", "動詞", "The organizers hope to intensify security measures before the crowded festival begins.", "主催者たちは大勢の集まる祭りが始まる前に警備対策を強化したいと考えている。"),
    "disassociate": ("切り離す、関係を断つ", "動詞", "The company tried to disassociate itself from the controversial advertisement.", "その会社は問題のある広告から自らを切り離そうとした。"),
    "vindicate": ("潔白を証明する、正当性を示す", "動詞", "The laboratory results may vindicate the researcher accused of negligence.", "研究室の結果は、過失を責められた研究者の潔白を証明するかもしれない。"),
    "sympathies": ("同情、弔意", "名詞", "The mayor expressed his sympathies to families affected by the ferry disaster.", "市長はフェリー事故の影響を受けた家族に弔意を表した。"),
    "prefaces": ("序文、前書き", "名詞", "The collected essays include prefaces written by respected scholars.", "その論文集には、著名な学者が書いた序文が含まれている。"),
    "aspirations": ("志、熱望", "名詞", "Her professional aspirations encouraged her to pursue advanced medical training.", "専門職としての志が、彼女に高度な医学研修を受けるよう促した。"),
    "adversities": ("逆境、苦難", "名詞", "The memoir explains how the family endured several adversities together.", "その回想録は、家族がいくつもの苦難を共に耐え抜いた経緯を説明している。"),
    "derived": ("引き出した、由来した", "動詞", "The scientist derived a useful formula from repeated experimental observations.", "その科学者は繰り返した実験観察から有用な公式を導き出した。"),
    "dispelled": ("追い払った、払拭した", "動詞", "The clear explanation dispelled rumors that had worried the community.", "明確な説明が、地域社会を不安にさせていたうわさを払拭した。"),
    "purloined": ("盗んだ", "動詞", "The thief purloined several rare coins from the private collection.", "その泥棒は個人コレクションから珍しい硬貨を何枚も盗んだ。"),
    "embedded": ("埋め込んだ、組み込んだ", "動詞", "The engineer embedded a small sensor inside the replacement component.", "技術者は交換部品の内部に小さなセンサーを埋め込んだ。"),
    "cavernous": ("洞窟のように広大な", "形容詞", "The cavernous warehouse could accommodate thousands of boxes.", "洞窟のように広大な倉庫には、何千もの箱を収容できた。"),
    "deranged": ("錯乱した、常軌を逸した", "形容詞", "The deranged suspect shouted incoherently during the courtroom hearing.", "錯乱した容疑者は法廷での審理中に支離滅裂なことを叫んだ。"),
    "delicate": ("繊細な、壊れやすい", "形容詞", "She wrapped the delicate lace handkerchief in tissue paper.", "彼女は繊細なレースのハンカチを薄紙で包んだ。"),
    "hedonistic": ("快楽主義の", "形容詞", "His hedonistic lifestyle prioritized expensive meals and constant entertainment.", "彼の快楽主義的な生活は、高価な食事と絶え間ない娯楽を優先した。"),
    "mollify": ("なだめる、鎮める", "動詞", "The manager offered refunds to mollify customers angered by the delay.", "管理者は遅延に怒った顧客をなだめるため、返金を申し出た。"),
    "retard": ("遅らせる、妨げる", "動詞", "Poor drainage can retard plant growth during the rainy season.", "排水不良は雨期の植物の成長を遅らせることがある。"),
    "encroach": ("侵食する、食い込む", "動詞", "New construction began to encroach on the protected wetlands.", "新しい建設が保護された湿地を侵食し始めた。"),
    "harass": ("悩ませる、嫌がらせをする", "動詞", "Repeated calls continued to harass residents throughout the evening.", "繰り返しの電話が夕方を通して住民を悩ませ続けた。"),
    "indolent": ("怠惰な、ものぐさな", "形容詞", "The indolent employee avoided difficult assignments whenever the supervisor was absent.", "その怠惰な従業員は上司が不在になるといつも難しい仕事を避けた。"),
    "penurious": ("ひどくけちな、極端に倹約的な", "形容詞", "The penurious landlord refused to repair even essential plumbing.", "そのひどくけちな家主は、不可欠な配管さえ修理しようとしなかった。"),
    "damp": ("湿った、じめじめした", "形容詞", "The hikers rested in a damp shelter during the sudden storm.", "ハイカーたちは突然の嵐の間、湿った避難小屋で休んだ。"),
    "adventurous": ("冒険好きな、冒険的な", "形容詞", "Adventurous travelers often seek remote destinations beyond ordinary tourist routes.", "冒険好きな旅行者は、普通の観光ルートから離れた遠隔地をよく探す。"),
    "masterful": ("熟達した、見事な", "形容詞", "The conductor delivered a masterful interpretation of the difficult symphony.", "その指揮者は難しい交響曲を見事に解釈して演奏した。"),
    "substandard": ("標準以下の", "形容詞", "The inspector rejected the substandard materials before construction could begin.", "検査官は工事が始まる前に標準以下の資材を退けた。"),
    "benign": ("良性の、害のない", "形容詞", "The doctor assured her that the small growth was benign.", "医師はその小さな腫瘍が良性だと彼女に保証した。"),
    "erratic": ("不規則な、予測不能な", "形容詞", "Erratic rainfall made it difficult for farmers to plan harvests.", "不規則な降雨のため、農家は収穫の計画を立てにくかった。"),
    "lethargy": ("無気力、倦怠", "名詞", "After the illness, persistent lethargy kept him from returning to work.", "病気の後、持続する倦怠感のため彼は仕事に戻れなかった。"),
    "eagerness": ("熱意、切望", "名詞", "She accepted the research invitation with eagerness and genuine curiosity.", "彼女は熱意と純粋な好奇心をもって研究への招待を受け入れた。"),
    "revulsion": ("強い嫌悪", "名詞", "The witness described the scene with visible revulsion during testimony.", "証人は証言中、目に見える嫌悪感を示してその場面を説明した。"),
    "resilience": ("回復力、立ち直る力", "名詞", "The community showed remarkable resilience after the coastal storm.", "その地域社会は沿岸を襲った嵐の後、驚くべき回復力を示した。"),
    "attribute": ("〜のせい・おかげだと考える、帰する", "動詞", "Many historians attribute the empire's decline to prolonged internal conflict.", "多くの歴史家は帝国の衰退を長期にわたる内紛に帰している。"),
    "deter": ("思いとどまらせる、抑止する", "動詞", "Visible penalties may deter companies from violating environmental regulations.", "目に見える罰則は企業が環境規制に違反するのを抑止するかもしれない。"),
    "slacken": ("緩める、弱める", "動詞", "The wind began to slacken as the storm moved offshore.", "嵐が沖へ移動すると、風は弱まり始めた。"),
    "mock": ("あざける、からかう", "動詞", "Older students should never mock classmates for making honest mistakes.", "年上の生徒は、正直な間違いをした同級生を決してからかうべきではない。"),
    "integrate": ("統合する、組み入れる", "動詞", "The new software will integrate records from several independent databases.", "新しいソフトウェアは複数の独立したデータベースの記録を統合する。"),
    "divert": ("そらす、迂回させる", "動詞", "Officials must divert traffic while crews repair the damaged bridge.", "作業員が損傷した橋を修理している間、当局は交通を迂回させなければならない。"),
    "anoint": ("指名する、任命する、塗油する", "動詞", "Party leaders gathered to anoint a successor before the convention.", "党の指導者たちは大会前に後継者を指名するため集まった。"),
    "irk": ("いらだたせる", "動詞", "The manager's dismissive tone continued to irk the patient employee.", "管理者の見下した口調は、辛抱強い従業員をいらだたせ続けた。"),
    "thrifty": ("倹約的な", "形容詞", "Her thrifty habits helped the family save for a larger home.", "彼女の倹約的な習慣は、家族がより大きな家のために貯金するのに役立った。"),
    "inactive": ("活動していない、休止中の", "形容詞", "The account remained inactive until the customer submitted new identification.", "その口座は顧客が新しい身分証明書を提出するまで休止していた。"),
    "subservient": ("従属的な、卑屈な", "形容詞", "The policy treated local officials as subservient to distant authorities.", "その政策は地方役人を遠方の当局に従属する者として扱った。"),
    "sedentary": ("座りがちな、座業中心の", "形容詞", "A sedentary routine can increase health risks without regular exercise.", "定期的な運動がなければ、座りがちな生活習慣は健康リスクを高めることがある。"),
    "scolded": ("叱った", "動詞", "The teacher scolded the student for ignoring repeated safety instructions.", "教師は安全上の指示を何度も無視した生徒を叱った。"),
    "glossed": ("表面を取り繕った、軽く扱った", "動詞", "The article glossed over important evidence that challenged its conclusion.", "その記事は結論に異議を唱える重要な証拠を軽く扱った。"),
    "indented": ("字下げした、へこませた", "動詞", "The editor indented the first line of every paragraph consistently.", "編集者はすべての段落の最初の行を一貫して字下げした。"),
    "frisked": ("身体検査した", "動詞", "The officer frisked the suspect before placing him inside the vehicle.", "巡査は容疑者を車内に入れる前に身体検査をした。"),
    "agitation": ("動揺、興奮", "名詞", "The sudden announcement caused agitation among passengers waiting at the station.", "突然の発表は駅で待っていた乗客の間に動揺を引き起こした。"),
    "indifference": ("無関心", "名詞", "Her indifference to repeated warnings worried the entire research team.", "度重なる警告への彼女の無関心は研究チーム全体を心配させた。"),
    "ascension": ("上昇、即位", "名詞", "The monarch's ascension changed the balance of power across Europe.", "その君主の即位はヨーロッパ全体の勢力均衡を変えた。"),
    "rapture": ("有頂天、恍惚", "名詞", "The audience listened in rapture as the orchestra performed the finale.", "オーケストラが終楽章を演奏すると、聴衆は恍惚として耳を傾けた。"),
    "forked over": ("しぶしぶ支払った", "句動詞", "The contractor finally forked over the overdue payment after mediation.", "その請負業者は調停の後、ついに滞納していた支払いをしぶしぶ行った。"),
    "built up": ("増やした、築き上げた", "句動詞", "She built up her savings by accepting extra shifts each weekend.", "彼女は毎週末に追加勤務を引き受けて貯金を増やした。"),
    "shook off": ("振り切った、払いのけた", "句動詞", "The runner shook off fatigue and finished the final kilometer.", "その走者は疲労を振り切り、最後の1キロを走り終えた。"),
    "riffled through": ("ぱらぱらめくった、ざっと調べた", "句動詞", "The librarian riffled through the returned magazines before shelving them.", "司書は返却された雑誌を棚に戻す前にぱらぱらめくった。"),
    "scale back": ("縮小する、削減する", "句動詞", "The agency had to scale back its plans after funding declined.", "その機関は資金が減った後、計画を縮小しなければならなかった。"),
    "sift through": ("ふるいにかけて調べる", "句動詞", "Analysts will sift through the survey responses for recurring patterns.", "分析担当者は繰り返し現れるパターンを求めて調査回答を詳しく調べる。"),
    "slow down": ("遅らせる、減速させる", "句動詞", "Heavy traffic may slow down emergency vehicles during rush hour.", "ラッシュ時の激しい交通は救急車両を遅らせるかもしれない。"),
    "ratchet up": ("段階的に高める", "句動詞", "The director plans to ratchet up training requirements next year.", "責任者は来年、研修の要件を段階的に高める計画だ。"),
    "opened out": ("広がった、開けた", "句動詞", "The narrow trail opened out into a broad meadow beyond the trees.", "狭い道は木々の先で広い草原へと広がった。"),
    "acted up": ("調子が悪くなった、いたずらをした", "句動詞", "The printer acted up just before the important documents were due.", "重要書類の締切直前にプリンターの調子が悪くなった。"),
    "pitched in": ("協力した、手伝った", "句動詞", "Neighbors pitched in to clean the park after the storm.", "近所の人々は嵐の後に公園を掃除するため協力した。"),
    "petered out": ("次第に消えた、弱まった", "句動詞", "The hikers' conversation petered out as darkness covered the trail.", "暗闇が道を覆うにつれ、ハイカーたちの会話は次第に消えていった。"),
    "trumped up": ("でっち上げた、捏造した", "句動詞", "The defense argued that the charges were trumped up by rivals.", "弁護側は、その容疑はライバルによってでっち上げられたと主張した。"),
    "belted out": ("大声で歌った、叫んだ", "句動詞", "The singer belted out the anthem while the crowd waved flags.", "歌手が国歌を大声で歌う間、群衆は旗を振った。"),
    "spurred on": ("駆り立てた、励ました", "句動詞", "Her mentor's encouragement spurred on the young scientist during setbacks.", "指導者の励ましが、挫折の間も若い科学者を駆り立てた。"),
    "carted off": ("運び去った", "句動詞", "Workers carted off the damaged equipment before the inspection began.", "作業員たちは検査が始まる前に損傷した機器を運び去った。"),
}


ETYMOLOGY = {
    "addendum": "ラテン語 addere（加える）から、文書に追加する部分を表す。",
    "monstrosity": "ラテン語 monstrum（怪物、異常なもの）から、ひどく醜いものを表す。",
    "appendage": "ラテン語 appendere（つるす、付け加える）から、付属する部分を表す。",
    "infringement": "ラテン語 infringere（打ち砕く、破る）から、権利などの侵害を表す。",
    "exonerated": "ラテン語 exonerare（負担を取り除く）から、責任や罪を免れさせる意味になった。",
    "calibrated": "calibre（測定の基準となる寸法）から、計器を基準に合わせる意味を表す。",
    "repainted": "re-（再び）＋paint（塗る）から、もう一度塗る意味を表す。",
    "vilified": "ラテン語 vilis（価値のない、卑しい）から、人をひどく悪く言う意味になった。",
    "dispersed": "ラテン語 dispergere（散らす）から、広い範囲へ分散させる意味を表す。",
    "attacked": "古フランス語 attaquer（攻撃する）から、相手に攻撃を加える意味を表す。",
    "denigrated": "ラテン語 denigrare（黒くする）から、人や評判をけなす意味になった。",
    "obstructed": "ラテン語 obstruere（前に築いてふさぐ）から、通路などを妨げる意味を表す。",
    "stealthily": "古英語 stelan（盗む、こっそり取る）に由来する stealth に -ly が付いた語。",
    "persistently": "ラテン語 persistere（固く立つ、持続する）から、粘り強く続ける様子を表す。",
    "independently": "ラテン語 dependere（ぶら下がる、頼る）に in-（否定）を加え、頼らずに行う意味を表す。",
    "impartially": "ラテン語 pars（部分）から、どちらか一方に偏らない意味を表す。",
    "hues": "中英語 hue（色、外観）に由来し、物の色合いを表す。",
    "ornaments": "ラテン語 ornare（飾る）から、装飾品や飾りを表す。",
    "spectacles": "ラテン語 specere（見る）から、見るための眼鏡や光景を表す。",
    "prophecies": "ギリシャ語 prophetes（神の言葉を語る者）から、未来を告げる予言を表す。",
    "arbitration": "ラテン語 arbiter（判断する人）から、第三者による仲裁を表す。",
    "conceit": "ラテン語 concipere（心に取り込む、考える）から、自己評価を抱く意味へ広がった。",
    "pronunciation": "ラテン語 pronuntiare（公に告げる）から、語を発音して声に出すことを表す。",
    "obliquity": "ラテン語 obliquus（斜めの、曲がった）から、斜めの状態や婉曲さを表す。",
    "rustic": "ラテン語 rusticus（田舎の）から、田園風で素朴な性質を表す。",
    "pastoral": "ラテン語 pastor（羊飼い）から、羊飼いや牧歌的な田園を表す。",
    "fallacious": "ラテン語 fallere（だます）から、誤った根拠に基づく意味を表す。",
    "deleterious": "ギリシャ語 deleterios（害を与える）から、有害な性質を表す。",
    "bog": "北欧系の語に由来し、水がたまった湿地や泥沼を表す。",
    "hazard": "古フランス語 hasard（偶然、危険）から、危険や危険要因を表す。",
    "illusion": "ラテン語 illudere（からかう、だます）から、現実と違う見え方を表す。",
    "stagnation": "ラテン語 stagnare（動かずにたまる）から、流れや進歩の停滞を表す。",
    "inveigle": "古フランス語 enveigler（だまして誘う）に由来し、巧みに誘い込む意味を表す。",
    "intensify": "ラテン語 intensus（強く張った）から、強さを増す意味を表す。",
    "disassociate": "dis-（離れて）＋associate（結びつける）から、関係を切り離す意味を表す。",
    "vindicate": "ラテン語 vindicare（権利を主張する、取り戻す）から、正当性や潔白を示す意味になった。",
    "sympathies": "ギリシャ語 sympatheia（共に苦しむこと）から、相手への同情や弔意を表す。",
    "prefaces": "ラテン語 praefatio（前もって話すこと）から、本文の前置きとなる序文を表す。",
    "aspirations": "ラテン語 aspirare（息を吹きかける、強く望む）から、達成を望む志を表す。",
    "adversities": "ラテン語 adversus（向かい合った、敵対した）から、立ちはだかる逆境を表す。",
    "derived": "ラテン語 derivare（流れを別方向へ導く）から、源から引き出す意味を表す。",
    "dispelled": "ラテン語 dispellere（追い散らす）から、疑いや雲などを払う意味を表す。",
    "purloined": "古フランス語 purloigner（遠くへ持ち去る）から、こっそり盗む意味になった。",
    "embedded": "em-（中へ）＋bed（置く場所）から、内部にしっかり埋め込む意味を表す。",
    "cavernous": "ラテン語 caverna（洞窟）から、洞窟のように広く深い様子を表す。",
    "deranged": "フランス語 déranger（秩序を乱す）から、正常な状態を乱す意味を表す。",
    "delicate": "ラテン語 delicatus（心地よい、ぜいたくな）から、繊細で壊れやすい性質を表す。",
    "hedonistic": "ギリシャ語 hedone（快楽）から、快楽を重視する考え方を表す。",
    "mollify": "ラテン語 mollis（柔らかい）から、態度や感情を和らげる意味を表す。",
    "retard": "ラテン語 retardare（遅らせる）から、進行を遅くする意味を表す。",
    "encroach": "古フランス語 encrochier（鉤をかける）から、徐々に領域へ入り込む意味になった。",
    "harass": "フランス語 harasser（疲れさせる）から、繰り返し悩ませる意味を表す。",
    "indolent": "ラテン語 indolens（痛みを感じない）から、努力や活動を嫌う怠惰な性質へ広がった。",
    "penurious": "ラテン語 penuria（不足、貧困）から、極端にけちな性質を表す。",
    "damp": "中英語 damp（蒸気、湿気）に由来し、湿った状態を表す。",
    "adventurous": "ラテン語 adventura（起こるべきこと）から、危険や未知へ進む性質を表す。",
    "masterful": "master（師、熟達者）に -ful（満ちた）を加え、熟達した様子を表す。",
    "substandard": "sub-（下に）＋standard（基準）から、基準を下回る意味を表す。",
    "benign": "ラテン語 benignus（親切な、良い生まれの）から、害のない性質を表す。",
    "erratic": "ラテン語 errare（さまよう、誤る）から、一定せず予測できない様子を表す。",
    "lethargy": "ギリシャ語 lethargia（忘却、無気力）から、心身のだるさを表す。",
    "eagerness": "古フランス語 aigre（鋭い、熱烈な）に由来する eager から、強い熱意を表す。",
    "revulsion": "ラテン語 revellere（引きはがす、引き戻す）から、強い嫌悪で身を引くことを表す。",
    "resilience": "ラテン語 resilire（跳ね返る）から、困難から立ち直る力を表す。",
    "attribute": "ラテン語 attribuere（割り当てる）から、原因や功績を帰する意味を表す。",
    "deter": "ラテン語 deterrere（恐れさせて遠ざける）から、思いとどまらせる意味を表す。",
    "slacken": "slack（ゆるい、たるんだ）に -en を加え、勢いや緊張を弱める意味を表す。",
    "mock": "古フランス語 mocquer（あざける）に由来し、相手をからかう意味を表す。",
    "integrate": "ラテン語 integer（完全な、一つの）から、部分を一つにまとめる意味を表す。",
    "divert": "ラテン語 divertere（別方向へ向ける）から、流れや注意をそらす意味を表す。",
    "anoint": "ラテン語 inungere（油を塗る）から、儀礼的に任命する意味へ広がった。",
    "irk": "中英語 irken（疲れさせる、うんざりさせる）に由来し、いらだたせる意味を表す。",
    "thrifty": "thrive（繁栄する）に由来し、資源を無駄にせず暮らす性質を表す。",
    "inactive": "ラテン語 activus（活動的な）に in-（否定）を加え、活動していない意味を表す。",
    "subservient": "ラテン語 subservire（下で仕える）から、他者に従属する意味を表す。",
    "sedentary": "ラテン語 sedere（座る）から、座って過ごすことが多い状態を表す。",
    "scolded": "中英語 scolden（叱る）に由来し、厳しく注意する意味を表す。",
    "glossed": "ギリシャ語 glossa（舌、語句の説明）から、表面を飾る・問題を軽く扱う意味へ広がった。",
    "indented": "ラテン語 dens（歯）から、歯形の切れ込みや字下げを表す。",
    "frisked": "古い北欧・フランス系の frisk（活発に動く）に由来し、身体を手早く調べる意味を表す。",
    "agitation": "ラテン語 agitare（動かす、駆り立てる）から、心の動揺や騒ぎを表す。",
    "indifference": "ラテン語 differre（異なる）に in-（否定）を加え、どちらにも偏らない無関心を表す。",
    "ascension": "ラテン語 ascendere（上へ登る）から、上昇や王位への就任を表す。",
    "rapture": "ラテン語 rapere（奪い去る）から、感情に心を奪われた恍惚状態を表す。",
    "forked over": "fork（分岐する）＋over（相手側へ渡して）から、金をしぶしぶ渡す意味を表す。",
    "built up": "build（築く）＋up（積み上げて）から、量や力を徐々に増やす意味を表す。",
    "shook off": "shake（振る）＋off（離して）から、疲労や追跡者などを振り切る意味を表す。",
    "riffled through": "riffle（素早くめくる）＋through（端から端まで）から、ざっと目を通す意味を表す。",
    "scale back": "scale（規模を測る）＋back（後ろへ戻して）から、規模や計画を縮小する意味を表す。",
    "sift through": "sift（ふるいにかける）＋through（中を通して）から、情報を詳しく選別する意味を表す。",
    "slow down": "slow（遅くする）＋down（下げて）から、速度や進行を落とす意味を表す。",
    "ratchet up": "ratchet（歯止めで少しずつ動かす）＋up（上へ）から、段階的に高める意味を表す。",
    "opened out": "open（開く）＋out（外へ広げて）から、狭い所が広がる意味を表す。",
    "acted up": "act（振る舞う、作動する）＋up（通常の状態から外れて）から、誤作動やいたずらを表す。",
    "pitched in": "pitch（投げ入れる）＋in（中へ加わって）から、活動に加わり協力する意味を表す。",
    "petered out": "peter（少しずつ弱まる）＋out（外へ消えて）から、勢いや量が次第に尽きる意味を表す。",
    "trumped up": "trump（切り札を出す）＋up（作り上げて）から、容疑や話をでっち上げる意味を表す。",
    "belted out": "belt（ベルトで強く締める）から声を強く押し出し、勢いよく歌う意味を表す。",
    "spurred on": "spur（拍車をかける）＋on（前へ）から、人を励まして行動へ駆り立てる意味を表す。",
    "carted off": "cart（荷車で運ぶ）＋off（その場から離して）から、物を運び去る意味を表す。",
}


CORE_IMAGES = {
    "forked over": {"chain": [{"term": "fork", "gloss": "分岐する"}, {"term": "over", "gloss": "相手側へ渡して"}, {"gloss": "手元から相手へ渡して"}, {"gloss": "金をしぶしぶ支払う"}], "particle": "over"},
    "built up": {"chain": [{"term": "build", "gloss": "築く"}, {"term": "up", "gloss": "上へ積み上げて"}, {"gloss": "量や力を少しずつ積み重ねて"}, {"gloss": "増やす、築き上げる"}], "particle": "up", "particleSense": "raise", "siblings": [{"phrase": "lift up", "gloss": "持ち上げる"}, {"phrase": "pump up", "gloss": "膨らませる・高める"}, {"phrase": "rally up", "gloss": "結集させる"}]},
    "shook off": {"chain": [{"term": "shook", "gloss": "振った"}, {"term": "off", "gloss": "離して"}, {"gloss": "まとわりつくものを振り落として"}, {"gloss": "振り切る、払いのける"}], "particle": "off", "particleSense": "pull-away"},
    "riffled through": {"chain": [{"term": "riffled", "gloss": "素早くめくった"}, {"term": "through", "gloss": "中を通して"}, {"gloss": "ページを端から端までざっと見て"}, {"gloss": "ぱらぱらめくって調べる"}]},
    "scale back": {"chain": [{"term": "scale", "gloss": "規模を測る"}, {"term": "back", "gloss": "後ろへ戻して"}, {"gloss": "規模を前より小さくして"}, {"gloss": "縮小する"}], "particle": "back"},
    "sift through": {"chain": [{"term": "sift", "gloss": "ふるいにかける"}, {"term": "through", "gloss": "中を通して"}, {"gloss": "情報を一つずつ選別して"}, {"gloss": "詳しく調べる"}]},
    "slow down": {"chain": [{"term": "slow", "gloss": "遅くする"}, {"term": "down", "gloss": "下げて"}, {"gloss": "速度や進行を落として"}, {"gloss": "遅らせる、減速させる"}], "particle": "down", "particleSense": "reduce", "siblings": [{"phrase": "cool down", "gloss": "冷ます・落ち着かせる"}, {"phrase": "tone down", "gloss": "調子をやわらげる"}, {"phrase": "cut down", "gloss": "減らす"}]},
    "ratchet up": {"chain": [{"term": "ratchet", "gloss": "歯止めで少しずつ動かす"}, {"term": "up", "gloss": "上へ"}, {"gloss": "一段ずつ水準を上げて"}, {"gloss": "段階的に高める"}], "particle": "up", "particleSense": "raise"},
    "opened out": {"chain": [{"term": "open", "gloss": "開く"}, {"term": "out", "gloss": "外へ広げて"}, {"gloss": "狭い所から外へ広がって"}, {"gloss": "広がる、開ける"}], "particle": "out", "particleSense": "spread"},
    "acted up": {"chain": [{"term": "acted", "gloss": "振る舞った、作動した"}, {"term": "up", "gloss": "通常の状態から外れて"}, {"gloss": "機械や人が調子を乱して"}, {"gloss": "誤作動する、いたずらをする"}], "particle": "up", "particleSense": "disrupt"},
    "pitched in": {"chain": [{"term": "pitched", "gloss": "投げ入れた"}, {"term": "in", "gloss": "中へ加わって"}, {"gloss": "活動の中へ自分を加えて"}, {"gloss": "協力する"}], "particle": "in"},
    "petered out": {"chain": [{"term": "peter", "gloss": "少しずつ弱まる"}, {"term": "out", "gloss": "外へ消えて"}, {"gloss": "勢いや量が徐々に尽きて"}, {"gloss": "次第に消える"}], "particle": "out", "particleSense": "exhaust"},
    "trumped up": {"chain": [{"term": "trump", "gloss": "切り札を出す"}, {"term": "up", "gloss": "作り上げて"}, {"gloss": "根拠のない話を作り上げて"}, {"gloss": "でっち上げる"}], "particle": "up", "particleSense": "fabricate"},
    "belted out": {"chain": [{"term": "belt", "gloss": "強く締める"}, {"term": "out", "gloss": "外へ押し出して"}, {"gloss": "声を勢いよく外へ出して"}, {"gloss": "大声で歌う、叫ぶ"}], "particle": "out", "particleSense": "express"},
    "spurred on": {"chain": [{"term": "spur", "gloss": "拍車をかける"}, {"term": "on", "gloss": "前へ"}, {"gloss": "人を前へ進ませて"}, {"gloss": "励まして駆り立てる"}], "particle": "on", "particleSense": "continue"},
    "carted off": {"chain": [{"term": "cart", "gloss": "荷車で運ぶ"}, {"term": "off", "gloss": "その場から離して"}, {"gloss": "物を場所から離れた所へ運んで"}, {"gloss": "運び去る"}], "particle": "off", "particleSense": "pull-away"},
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
        raise ValueError("模試第9回は25問である必要があります")

    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != len(set(choices)):
        raise ValueError("選択肢に重複があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    missing_etymology = sorted(set(choices) - set(ETYMOLOGY))
    if missing_etymology:
        raise ValueError(f"語源情報がありません: {missing_etymology}")

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
        "source": "ユーザー提供画像（原本表記は模擬テスト第4回）を、依頼により模試第9回として構造化。既存語句との重複を避けるため一部選択肢を置換",
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
                "etymology": ETYMOLOGY[choice],
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
    write_json(DATA_DIR / "vocab_1_mock-9.json", vocab)
    write_json(DATA_DIR / "questions_1_mock-9.json", questions)
    print("mock-9: 25 questions / 100 items (84 words, 16 idioms)")


if __name__ == "__main__":
    main()
