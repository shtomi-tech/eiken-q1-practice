"""英検1級 模試第13回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-13 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-13"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "A narrow (   ) cut through the limestone, and the river far below was invisible from the road above.",
        "choices": ["gorge", "duplicity", "prudence", "conurbation"],
        "answerIndex": 0,
        "translation": "狭い峡谷が石灰岩を貫いており、はるか下の川は上の道路からは見えなかった。",
    },
    {
        "stem": "At the trial the defense pleaded (   ) and submitted three separate psychiatric evaluations to the court.",
        "choices": ["deviation", "insanity", "fallacy", "subjugation"],
        "answerIndex": 1,
        "translation": "その裁判で弁護側は心神喪失を主張し、3通の別々の精神鑑定書を法廷に提出した。",
    },
    {
        "stem": "Engineers used a carefully controlled (   ) to bring down the tower without damaging the buildings beside it.",
        "choices": ["snag", "exponent", "implosion", "remission"],
        "answerIndex": 2,
        "translation": "技術者たちは慎重に制御した内部爆破を用いて、隣の建物を傷つけずに塔を倒した。",
    },
    {
        "stem": "The town organized a week of free concerts to mark the queen's silver (   ) in June.",
        "choices": ["tedium", "exodus", "impulse", "jubilee"],
        "answerIndex": 3,
        "translation": "町は6月の女王在位25周年記念を祝うため、1週間の無料コンサートを企画した。",
    },
    {
        "stem": "The article offers a patient (   ) of a theory that most general readers find impenetrable.",
        "choices": ["elucidation", "ordeal", "commutation", "reprieve"],
        "answerIndex": 0,
        "translation": "その記事は、一般の読者の大半が難解だと感じる理論を辛抱強く解明している。",
    },
    {
        "stem": "The bank refused the loan because the young couple could offer no (   ) beyond a secondhand car.",
        "choices": ["retention", "collateral", "scarcity", "solace"],
        "answerIndex": 1,
        "translation": "その若い夫婦は中古車以外に担保を差し出せなかったため、銀行は融資を断った。",
    },
    {
        "stem": "As (   ), the pilgrim walked the final twenty kilometers to the shrine without shoes.",
        "choices": ["swarm", "absurdity", "penance", "compliance"],
        "answerIndex": 2,
        "translation": "罪の償いとして、その巡礼者は聖堂までの最後の20キロを靴を履かずに歩いた。",
    },
    {
        "stem": "He (   ) his fists at his sides and said nothing at all while the verdict was read out.",
        "choices": ["nauseated", "deplored", "accredited", "clenched"],
        "answerIndex": 3,
        "translation": "評決が読み上げられる間、彼は両脇で拳を固く握りしめ、何も言わなかった。",
    },
    {
        "stem": "Students spent the first month learning how Latin verbs are (   ) in each of the six tenses.",
        "choices": ["conjugated", "perturbed", "converged", "forestalled"],
        "answerIndex": 0,
        "translation": "学生たちは最初の1か月を、ラテン語の動詞が6つの時制それぞれでどう活用されるかを学ぶことに費やした。",
    },
    {
        "stem": "A sudden gust (   ) the tablecloth and sent the paper napkins across the terrace.",
        "choices": ["repatriated", "rumpled", "estranged", "commiserated"],
        "answerIndex": 1,
        "translation": "突風がテーブルクロスをくしゃくしゃにし、紙ナプキンをテラス中に吹き飛ばした。",
    },
    {
        "stem": "The minister (   ) every attempt to reopen the negotiations during the whole of last spring.",
        "choices": ["laundered", "jumbled", "rebuffed", "desensitized"],
        "answerIndex": 2,
        "translation": "大臣は昨春の間中、交渉を再開しようとするあらゆる試みをはねつけた。",
    },
    {
        "stem": "The king (   ) in December 1936 and left the country by ship within a fortnight.",
        "choices": ["mangled", "germinated", "eavesdropped", "abdicated"],
        "answerIndex": 3,
        "translation": "国王は1936年12月に退位し、2週間以内に船で国を去った。",
    },
    {
        "stem": "She (   ) her frustration in a long letter that she wisely decided never to send.",
        "choices": ["vented", "prevaricated", "slandered", "catapulted"],
        "answerIndex": 0,
        "translation": "彼女は長い手紙の中で不満をぶちまけたが、賢明にもそれを決して送らないことにした。",
    },
    {
        "stem": "Airport officials (   ) the bottles at the gate because they exceeded the permitted volume.",
        "choices": ["fractured", "confiscated", "resuscitated", "incapacitated"],
        "answerIndex": 1,
        "translation": "空港職員は、許可された容量を超えていたためゲートでその瓶を没収した。",
    },
    {
        "stem": "An (   ) reader of detective novels, Marta finished three of them during the flight to Lisbon.",
        "choices": ["uptight", "uncanny", "avid", "frivolous"],
        "answerIndex": 2,
        "translation": "推理小説の熱心な読者であるマルタは、リスボンへの飛行中に3冊を読み終えた。",
    },
    {
        "stem": "Her approach to the shortage was entirely (   ): she used whichever method actually worked.",
        "choices": ["morbid", "skittish", "profane", "pragmatic"],
        "answerIndex": 3,
        "translation": "その不足への彼女の取り組み方は徹底して実利的だった。実際に機能する方法なら何でも使ったのである。",
    },
    {
        "stem": "The committee gave an (   ) answer that left no room whatever for further interpretation.",
        "choices": ["unequivocal", "brazen", "intrinsic", "flimsy"],
        "answerIndex": 0,
        "translation": "委員会は明確な回答を示し、それ以上の解釈の余地をまったく残さなかった。",
    },
    {
        "stem": "After a week of cold and (   ) weather, the children were desperate to play outside again.",
        "choices": ["impetuous", "dreary", "tantamount", "decrepit"],
        "answerIndex": 1,
        "translation": "寒く陰鬱な天気が1週間続いた後、子どもたちはまた外で遊びたくてたまらなかった。",
    },
    {
        "stem": "The dial is coated with a compound that keeps the numbers (   ) for hours after sunset.",
        "choices": ["recalcitrant", "convoluted", "luminous", "disparate"],
        "answerIndex": 2,
        "translation": "その文字盤は、日没後も何時間も数字が光り続ける化合物で覆われている。",
    },
    {
        "stem": "The declaration describes these rights as (   ), meaning that no government may take them away.",
        "choices": ["hereditary", "culpable", "salient", "inalienable"],
        "answerIndex": 3,
        "translation": "その宣言はこれらの権利を譲り渡すことのできないものと述べており、いかなる政府も奪えないという意味である。",
    },
    {
        "stem": "He (   ) deleted the entire folder while he was trying to rename one file inside it.",
        "choices": ["inadvertently", "crucially", "horrendously", "listlessly"],
        "answerIndex": 0,
        "translation": "彼は中の1つのファイルの名前を変えようとしていて、うっかりフォルダ全体を削除してしまった。",
    },
    {
        "stem": "Wages in the region (   ) the national average for most of the past decade.",
        "choices": ["whiled away", "lagged behind", "marked up", "braced for"],
        "answerIndex": 1,
        "translation": "その地域の賃金は過去10年のほとんどの期間、全国平均に後れを取っていた。",
    },
    {
        "stem": "A wave of relief (   ) her when the surgeon finally said that the operation had succeeded.",
        "choices": ["packed off", "cut across", "washed over", "toyed with"],
        "answerIndex": 2,
        "translation": "外科医がついに手術が成功したと言ったとき、安堵の波が彼女を包み込んだ。",
    },
    {
        "stem": "She (   ) the entrance examination without difficulty and began the two-year course in April.",
        "choices": ["knocked back", "dragged off", "flew at", "sailed through"],
        "answerIndex": 3,
        "translation": "彼女は入学試験を難なく突破し、4月に2年間の課程を始めた。",
    },
    {
        "stem": "The engineers (   ) a temporary antenna out of scrap metal and restored the signal that evening.",
        "choices": ["pined for", "rigged up", "bore up", "circled back"],
        "answerIndex": 1,
        "translation": "技術者たちは廃材から仮設のアンテナを間に合わせで作り、その晩のうちに信号を回復させた。",
    },
]


DETAILS = {
    # Q1
    "gorge": ("峡谷", "名詞", "A footbridge crosses the gorge about a kilometer above the falls.", "滝の約1キロ上流で、歩道橋がその峡谷を渡っている。"),
    "duplicity": ("二枚舌、欺瞞", "名詞", "The memoir accuses two ministers of open duplicity during the crisis.", "その回想録は2人の大臣が危機の間に露骨な二枚舌を使ったと非難している。"),
    "prudence": ("慎重さ、思慮分別", "名詞", "Financial prudence kept the small firm solvent through two recessions.", "財務上の慎重さがその小企業を2度の不況の間も健全に保った。"),
    "conurbation": ("大都市圏、都市集合体", "名詞", "The conurbation now stretches almost fifty kilometers along the coast.", "その大都市圏は今や海岸沿いに50キロ近く広がっている。"),
    # Q2
    "deviation": ("逸脱、偏差", "名詞", "Any deviation from the flight plan must be reported immediately.", "飛行計画からのいかなる逸脱も直ちに報告されなければならない。"),
    "insanity": ("狂気、精神障害", "名詞", "The plea of insanity was rejected after a second examination.", "心神喪失の主張は2度目の鑑定の後に退けられた。"),
    "fallacy": ("誤った考え、誤謬", "名詞", "It is a common fallacy that lightning never strikes twice.", "雷は同じ場所に二度落ちないというのはよくある誤った考えである。"),
    "subjugation": ("征服、服従させること", "名詞", "The chronicle records the subjugation of the northern tribes in detail.", "その年代記は北方部族の征服を詳細に記録している。"),
    # Q3
    "snag": ("思わぬ障害、支障", "名詞", "The project hit a snag when the supplier went out of business.", "納入業者が倒産したとき、その計画は思わぬ障害にぶつかった。"),
    "exponent": ("代表的な提唱者、擁護者", "名詞", "She became the leading exponent of the technique in Europe.", "彼女はヨーロッパにおけるその技法の第一の提唱者となった。"),
    "implosion": ("内部破裂、内向きの崩壊", "名詞", "The implosion of the old stadium took less than eight seconds.", "古い競技場の内部爆破解体は8秒もかからなかった。"),
    "remission": ("(病気の)寛解、軽減", "名詞", "Her cancer has been in remission for almost four years.", "彼女のがんは4年近く寛解の状態にある。"),
    # Q4
    "tedium": ("退屈、単調さ", "名詞", "The tedium of the night shift was broken only by the radio.", "夜勤の退屈を紛らわせるものはラジオだけだった。"),
    "exodus": ("大量脱出、大移動", "名詞", "The drought caused an exodus from the villages to the capital.", "干ばつは村々から首都への大量脱出を引き起こした。"),
    "impulse": ("衝動、はずみ", "名詞", "On a sudden impulse, he bought a ticket for the night train.", "突然の衝動から、彼は夜行列車の切符を買った。"),
    "jubilee": ("記念祝典、周年祝賀", "名詞", "The cathedral held a jubilee to mark eight centuries of worship.", "その大聖堂は800年にわたる礼拝を記念して祝典を開いた。"),
    # Q5
    "elucidation": ("解明、説明", "名詞", "The footnotes provide elucidation of several obscure passages.", "脚注はいくつかの難解な箇所についての解明を示している。"),
    "ordeal": ("厳しい試練、苦難", "名詞", "The three weeks at sea were an ordeal none of them discussed afterward.", "海上での3週間は、その後誰も口にしない厳しい試練だった。"),
    "commutation": ("(刑の)減刑", "名詞", "The governor granted a commutation to a prisoner who had served forty years.", "知事は40年服役した受刑者に減刑を認めた。"),
    "reprieve": ("執行猶予、一時的な救済", "名詞", "The factory won a brief reprieve when a buyer appeared in October.", "10月に買い手が現れ、その工場は短い猶予を得た。"),
    # Q6
    "retention": ("保持、維持", "名詞", "Staff retention improved sharply after the shift patterns changed.", "勤務時間の組み方が変わった後、職員の定着率は急激に改善した。"),
    "collateral": ("担保", "名詞", "The warehouse was pledged as collateral for the second loan.", "その倉庫は2件目の融資の担保として差し入れられた。"),
    "scarcity": ("不足、欠乏", "名詞", "A scarcity of clean water forced the camp to move twice.", "清潔な水の不足がその野営地に2度の移動を強いた。"),
    "solace": ("慰め", "名詞", "He found solace in long walks along the winter shore.", "彼は冬の海岸沿いの長い散歩に慰めを見いだした。"),
    # Q7
    "swarm": ("(虫などの)群れ", "名詞", "A swarm of bees settled on the branch above the gate.", "ミツバチの群れが門の上の枝に群がった。"),
    "absurdity": ("不合理、ばかばかしさ", "名詞", "The absurdity of the rule became obvious the first time it was applied.", "その規則の不合理さは、初めて適用されたときに明らかになった。"),
    "penance": ("罪の償い、苦行", "名詞", "He performed penance by working in the hospital for a year.", "彼は1年間その病院で働くことで罪の償いをした。"),
    "compliance": ("順守、従うこと", "名詞", "Compliance with the safety code is checked every six months.", "安全規定の順守は半年ごとに点検される。"),
    # Q8
    "nauseated": ("吐き気を催させた", "動詞", "The smell of diesel nauseated several passengers on the crossing.", "ディーゼルのにおいが航行中の何人かの乗客に吐き気を催させた。"),
    "deplored": ("非難した、嘆いた", "動詞", "The archbishop deplored the destruction of the medieval windows.", "大司教は中世のステンドグラスの破壊を嘆き非難した。"),
    "accredited": ("認可した、公認した", "動詞", "The ministry accredited the college as a teacher-training institution.", "省庁はその大学を教員養成機関として認可した。"),
    "clenched": ("(拳や歯を)固く握りしめた", "動詞", "He clenched the steering wheel as the car slid on the ice.", "車が氷の上で滑ったとき、彼はハンドルを固く握りしめた。"),
    # Q9
    "conjugated": ("(動詞を)活用させた", "動詞", "The textbook conjugated every irregular verb in a single table.", "その教科書はすべての不規則動詞を1つの表に活用させて示した。"),
    "perturbed": ("動揺させた、乱した", "動詞", "The delay perturbed passengers who had connecting flights to catch.", "その遅延は乗り継ぎ便に乗る必要のある乗客たちを動揺させた。"),
    "converged": ("集まった、収束した", "動詞", "Three marches converged on the square shortly before noon.", "3つの行進が正午の少し前に広場へ集まった。"),
    "forestalled": ("未然に防いだ、先手を打った", "動詞", "Quick repairs forestalled a shutdown of the entire production line.", "迅速な修理が生産ライン全体の停止を未然に防いだ。"),
    # Q10
    "repatriated": ("本国へ送還した", "動詞", "The museum repatriated the carvings to the community that made them.", "その博物館は彫刻を、それを作った共同体へ返還した。"),
    "rumpled": ("しわくちゃにした", "動詞", "The cat rumpled the bedspread every afternoon while nobody watched.", "その猫は誰も見ていない午後のたびにベッドカバーをしわくちゃにした。"),
    "estranged": ("疎遠にした、仲たがいさせた", "動詞", "The inheritance dispute estranged two brothers for over twenty years.", "遺産をめぐる争いが2人の兄弟を20年以上疎遠にした。"),
    "commiserated": ("同情した、慰め合った", "動詞", "The players commiserated with each other in the changing room afterward.", "選手たちは試合後、更衣室で互いを慰め合った。"),
    # Q11
    "laundered": ("(不正な金を)洗浄した、洗濯した", "動詞", "Investigators showed that the group laundered money through a chain of restaurants.", "捜査官たちはその集団がレストランチェーンを通じて資金洗浄をしていたことを示した。"),
    "jumbled": ("ごちゃ混ぜにした", "動詞", "The move jumbled files that had been in order for decades.", "移転は何十年も整理されていた書類をごちゃ混ぜにした。"),
    "rebuffed": ("はねつけた、拒絶した", "動詞", "The gallery rebuffed three offers before accepting the fourth.", "その画廊は3件の申し出をはねつけてから4件目を受け入れた。"),
    "desensitized": ("鈍感にした、感覚を麻痺させた", "動詞", "Constant coverage of the war desensitized much of the viewing public.", "戦争の絶え間ない報道は、視聴者の多くを鈍感にした。"),
    # Q12
    "mangled": ("ずたずたにした、めちゃくちゃにした", "動詞", "The machine mangled the sheet of metal beyond any possible repair.", "その機械は金属板を修理不可能なほどずたずたにした。"),
    "germinated": ("発芽した、発芽させた", "動詞", "The seeds germinated within nine days in the warm greenhouse.", "その種は暖かい温室で9日以内に発芽した。"),
    "eavesdropped": ("立ち聞きした、盗み聞きした", "動詞", "A junior clerk eavesdropped on the conversation from the next room.", "若い事務員が隣の部屋からその会話を盗み聞きした。"),
    "abdicated": ("退位した、(責任を)放棄した", "動詞", "The emperor abdicated in favor of his younger brother.", "皇帝は弟に譲るために退位した。"),
    # Q13
    "vented": ("(感情を)ぶちまけた、発散させた", "動詞", "He vented his anger on the nearest available piece of furniture.", "彼は手近にあった家具に怒りをぶつけた。"),
    "prevaricated": ("言葉を濁した、はぐらかした", "動詞", "The witness prevaricated for an hour before admitting the truth.", "その証人は真実を認めるまで1時間言葉を濁し続けた。"),
    "slandered": ("中傷した", "動詞", "He claimed the newspaper had slandered him in three separate articles.", "彼はその新聞が3つの別々の記事で自分を中傷したと主張した。"),
    "catapulted": ("急に押し上げた、投射した", "動詞", "A single film catapulted the unknown actor to international fame.", "1本の映画がその無名の俳優を国際的な名声へと一気に押し上げた。"),
    # Q14
    "fractured": ("骨折させた、ひびを入れた", "動詞", "She fractured her wrist during the second half of the match.", "彼女は試合の後半で手首を骨折した。"),
    "confiscated": ("没収した", "動詞", "Customs confiscated the ivory carvings found in the suitcase.", "税関はスーツケースから見つかった象牙の彫刻を没収した。"),
    "resuscitated": ("蘇生させた", "動詞", "Paramedics resuscitated the swimmer on the beach within four minutes.", "救急隊員は4分以内に浜辺でその遊泳者を蘇生させた。"),
    "incapacitated": ("(能力を)奪った、無力にした", "動詞", "A back injury incapacitated the driver for the rest of the season.", "背中のけががそのドライバーをシーズンの残り期間、活動不能にした。"),
    # Q15
    "uptight": ("神経質な、堅苦しい", "形容詞", "He gets uptight whenever anyone rearranges the tools on his bench.", "彼は誰かが作業台の工具を並べ替えるといつも神経質になる。"),
    "uncanny": ("不気味なほどの、驚くほどの", "形容詞", "She has an uncanny ability to remember faces from decades ago.", "彼女は何十年も前の顔を思い出す驚異的な能力を持っている。"),
    "avid": ("熱心な、貪欲な", "形容詞", "An avid gardener, he grows sixty varieties of tomato.", "熱心な園芸家である彼は60種類のトマトを栽培している。"),
    "frivolous": ("軽薄な、つまらない", "形容詞", "The judge dismissed the claim as frivolous and awarded costs.", "裁判官はその請求を軽薄なものとして退け、訴訟費用を命じた。"),
    # Q16
    "morbid": ("病的な、陰気な", "形容詞", "He has a morbid interest in the details of famous shipwrecks.", "彼は有名な難破船の詳細に病的な関心を持っている。"),
    "skittish": ("(馬などが)おびえやすい、落ち着かない", "形容詞", "The mare is skittish around machinery but calm with children.", "その雌馬は機械のそばではおびえやすいが、子どもには穏やかである。"),
    "profane": ("不敬な、冒とく的な", "形容詞", "The bishop objected to the profane language in the second act.", "司教は第2幕の冒とく的な言葉遣いに異議を唱えた。"),
    "pragmatic": ("実利的な、現実的な", "形容詞", "A pragmatic compromise satisfied neither side but ended the strike.", "現実的な妥協はどちらの側も満足させなかったが、ストライキを終わらせた。"),
    # Q17
    "unequivocal": ("明確な、あいまいでない", "形容詞", "The laboratory returned an unequivocal result within forty-eight hours.", "研究所は48時間以内に明確な結果を返した。"),
    "brazen": ("厚かましい、ずうずうしい", "形容詞", "It was a brazen theft carried out in front of twenty witnesses.", "それは20人の目撃者の前で行われた厚かましい窃盗だった。"),
    "intrinsic": ("本質的な、固有の", "形容詞", "The stone has little intrinsic value but great historical importance.", "その石には本質的な価値はほとんどないが、歴史的な重要性は大きい。"),
    "flimsy": ("薄っぺらな、根拠の弱い", "形容詞", "The shelter was a flimsy structure of plastic sheeting and rope.", "その避難小屋はビニールシートとロープでできた薄っぺらな造りだった。"),
    # Q18
    "impetuous": ("衝動的な、性急な", "形容詞", "One impetuous decision cost the company its largest client.", "1つの性急な決定が、その会社に最大の顧客を失わせた。"),
    "dreary": ("陰鬱な、退屈な", "形容詞", "November in that valley is dreary, wet and almost sunless.", "その谷の11月は陰鬱で、雨が多く、ほとんど日が差さない。"),
    "tantamount": ("(~に)等しい、同然の", "形容詞", "Refusing to answer was tantamount to admitting the charge.", "答えることを拒むのは、その容疑を認めるのに等しかった。"),
    "decrepit": ("老朽化した、おいぼれた", "形容詞", "A decrepit bus carried the workers over the mountain each morning.", "老朽化したバスが毎朝、作業員たちを山越えで運んでいた。"),
    # Q19
    "recalcitrant": ("反抗的な、扱いにくい", "形容詞", "Two recalcitrant students refused to leave the corridor.", "2人の反抗的な生徒が廊下から出ることを拒んだ。"),
    "convoluted": ("複雑に入り組んだ", "形容詞", "The plot is so convoluted that few viewers follow it entirely.", "その筋書きは複雑に入り組んでいて、完全に理解できる視聴者はほとんどいない。"),
    "luminous": ("光を発する、輝く", "形容詞", "Luminous paint marks the emergency exits on every deck.", "夜光塗料がどの甲板でも非常口を示している。"),
    "disparate": ("本質的に異なる、種々雑多な", "形容詞", "The report combines disparate sources into a single narrative.", "その報告書は互いに異質な資料を1つの物語にまとめている。"),
    # Q20
    "hereditary": ("遺伝性の、世襲の", "形容詞", "The condition is hereditary and appears in every second generation.", "その疾患は遺伝性で、一世代おきに現れる。"),
    "culpable": ("責任のある、とがめられるべき", "形容詞", "The inquiry found the contractor culpable for the collapse.", "調査は倒壊についてその請負業者に責任があると認定した。"),
    "salient": ("顕著な、際立った", "形容詞", "The summary lists the salient points on a single page.", "その要約は際立った要点を1ページにまとめている。"),
    "inalienable": ("譲り渡せない、奪えない", "形容詞", "The charter treats freedom of conscience as an inalienable right.", "その憲章は良心の自由を奪うことのできない権利として扱っている。"),
    # Q21
    "inadvertently": ("うっかりと、不注意に", "副詞", "The clerk inadvertently sent the invoice to the wrong address.", "その事務員はうっかり請求書を誤った住所へ送ってしまった。"),
    "crucially": ("決定的に、重要なことに", "副詞", "Crucially, the sample was stored at the correct temperature.", "決定的に重要なことに、その試料は正しい温度で保管されていた。"),
    "horrendously": ("ひどく、恐ろしく", "副詞", "The first draft was horrendously long and had to be cut.", "初稿は恐ろしく長く、削らなければならなかった。"),
    "listlessly": ("気だるそうに、物憂げに", "副詞", "The patient stirred his soup listlessly and pushed the bowl away.", "その患者は気だるそうにスープをかき混ぜ、器を押しやった。"),
    # Q22
    "whiled away": ("(時間を)のんびり過ごした", "句動詞", "They whiled away the delay playing cards in the departure lounge.", "彼らは出発ロビーでトランプをしながら遅延の時間をのんびり過ごした。"),
    "lagged behind": ("後れを取った", "句動詞", "Rural broadband speeds lagged behind those in the cities for years.", "地方のブロードバンド速度は何年も都市部に後れを取っていた。"),
    "marked up": ("値段を上げた、加筆した", "句動詞", "The dealer marked up every item before the sale began.", "その業者はセールが始まる前にすべての品の値段を上げた。"),
    "braced for": ("(~に)身構えた、備えた", "句動詞", "Coastal towns braced for a storm that never actually arrived.", "沿岸の町々は結局来なかった嵐に備えて身構えた。"),
    # Q23
    "packed off": ("(人を)追いやった、送り出した", "句動詞", "The children were packed off to their grandmother for the summer.", "子どもたちは夏の間、祖母のもとへ送り出された。"),
    "cut across": ("(~を)横切った、超えた", "句動詞", "The issue cut across party lines in an unusual way.", "その問題は異例の形で党派の境界を超えて広がった。"),
    "washed over": ("(感情が)押し寄せた", "句動詞", "A strange calm washed over the crowd as the music began.", "音楽が始まると、不思議な静けさが群衆を包み込んだ。"),
    "toyed with": ("(考えを)もてあそんだ、いじった", "句動詞", "He toyed with the idea of moving abroad but never applied.", "彼は海外移住の考えをもてあそんだが、応募することはなかった。"),
    # Q24
    "knocked back": ("(酒などを)一気に飲んだ、はねつけた", "句動詞", "He knocked back the coffee and hurried to the platform.", "彼はコーヒーを一気に飲み干し、急いでホームへ向かった。"),
    "dragged off": ("引きずって連れ去った", "句動詞", "Security guards dragged off the protester before the speech resumed.", "警備員たちは演説が再開される前にその抗議者を引きずって連れ去った。"),
    "flew at": ("(~に)食ってかかった", "句動詞", "The old man flew at the driver who had blocked his gate.", "その老人は門をふさいだ運転手に食ってかかった。"),
    "sailed through": ("楽々と通過した", "句動詞", "The bill sailed through the upper house without a single amendment.", "その法案は修正一つなく上院を楽々と通過した。"),
    # Q25
    "pined for": ("(~を)恋しがった、切望した", "句動詞", "The dog pined for its owner throughout the long hospital stay.", "その犬は長い入院の間ずっと飼い主を恋しがっていた。"),
    "rigged up": ("間に合わせで作った", "句動詞", "They rigged up a shower from a barrel and a garden hose.", "彼らは樽と庭用ホースで間に合わせのシャワーを作った。"),
    "bore up": ("持ちこたえた、気丈に耐えた", "句動詞", "She bore up remarkably well during the months of treatment.", "彼女は数か月の治療の間、驚くほど気丈に持ちこたえた。"),
    "circled back": ("(話題に)戻った、引き返した", "句動詞", "The chair circled back to the budget question near the end.", "議長は終わり近くで予算の問題に話を戻した。"),
}


CORE_IMAGES = {
    "whiled away": {
        "chain": [
            {"term": "while", "gloss": "時を過ごす"},
            {"term": "away", "gloss": "少しずつ消え去らせて"},
            {"gloss": "手持ちの時間を少しずつ消え去らせて"},
            {"gloss": "のんびり時間をつぶす"},
        ],
        "particle": "away",
    },
    "lagged behind": {
        "chain": [
            {"term": "lag", "gloss": "遅れる"},
            {"term": "behind", "gloss": "後方に取り残されて"},
            {"gloss": "先頭から離れて後方に取り残されて"},
            {"gloss": "後れを取る"},
        ],
        "particle": "behind",
    },
    "marked up": {
        "chain": [
            {"term": "mark", "gloss": "印をつける"},
            {"term": "up", "gloss": "値を高いほうへ引き上げて"},
            {"gloss": "値札の数字を上へ書き換えて"},
            {"gloss": "値段を上げる"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "braced for": {
        "chain": [
            {"term": "brace", "gloss": "支えて固める"},
            {"term": "for", "gloss": "来るものに備えて"},
            {"gloss": "来る衝撃に向けて体を固めて"},
            {"gloss": "~に備えて身構える"},
        ],
    },
    "packed off": {
        "chain": [
            {"term": "pack", "gloss": "荷造りする"},
            {"term": "off", "gloss": "その場から送り離して"},
            {"gloss": "荷物をまとめて別の場所へ送り出して"},
            {"gloss": "追いやる、送り出す"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "cut across": {
        "chain": [
            {"term": "cut", "gloss": "切って進む"},
            {"term": "across", "gloss": "境界を横切って"},
            {"gloss": "区切り線を無視して横切って"},
            {"gloss": "枠を超えて広がる"},
        ],
        "particle": "across",
    },
    "washed over": {
        "chain": [
            {"term": "wash", "gloss": "水が流れる"},
            {"term": "over", "gloss": "上を覆うように"},
            {"gloss": "波が全身を覆うように押し寄せて"},
            {"gloss": "感情が押し寄せる"},
        ],
        "particle": "over",
    },
    "toyed with": {
        "chain": [
            {"term": "toy", "gloss": "おもちゃにする"},
            {"term": "with", "gloss": "その対象を相手に"},
            {"gloss": "本気にならずに手先で転がして"},
            {"gloss": "考えをもてあそぶ"},
        ],
    },
    "knocked back": {
        "chain": [
            {"term": "knock", "gloss": "打ち込む"},
            {"term": "back", "gloss": "喉の奥へ送り返して"},
            {"gloss": "一息に喉の奥へ打ち込んで"},
            {"gloss": "一気に飲み干す"},
        ],
        "particle": "back",
    },
    "dragged off": {
        "chain": [
            {"term": "drag", "gloss": "引きずる"},
            {"term": "off", "gloss": "その場から引き離して"},
            {"gloss": "抵抗する相手を引きずって場から離して"},
            {"gloss": "引きずって連れ去る"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "flew at": {
        "chain": [
            {"term": "fly", "gloss": "飛びかかる"},
            {"term": "at", "gloss": "相手めがけて"},
            {"gloss": "相手めがけて勢いよく飛びかかって"},
            {"gloss": "食ってかかる"},
        ],
    },
    "sailed through": {
        "chain": [
            {"term": "sail", "gloss": "帆走する"},
            {"term": "through", "gloss": "最後まで通り抜けて"},
            {"gloss": "追い風を受けたまま難所を通り抜けて"},
            {"gloss": "楽々と通過する"},
        ],
    },
    "pined for": {
        "chain": [
            {"term": "pine", "gloss": "思い焦がれてやつれる"},
            {"term": "for", "gloss": "その対象を求めて"},
            {"gloss": "離れた相手を求めて衰えるほど思って"},
            {"gloss": "~を恋しがる"},
        ],
    },
    "rigged up": {
        "chain": [
            {"term": "rig", "gloss": "帆や索具を装備する"},
            {"term": "up", "gloss": "使える形に組み上げて"},
            {"gloss": "ありあわせの材料を使える形に組み上げて"},
            {"gloss": "間に合わせで作る"},
        ],
        "particle": "up",
        "particleSense": "prepare",
    },
    "bore up": {
        "chain": [
            {"term": "bear", "gloss": "支える、耐える"},
            {"term": "up", "gloss": "気力を上向きに保って"},
            {"gloss": "重みの下でも気力を上向きに保って"},
            {"gloss": "気丈に持ちこたえる"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "circled back": {
        "chain": [
            {"term": "circle", "gloss": "円を描いて回る"},
            {"term": "back", "gloss": "元の地点へ戻って"},
            {"gloss": "ひと回りして元の地点へ戻って"},
            {"gloss": "話題に立ち返る"},
        ],
        "particle": "back",
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
        raise ValueError("模試第13回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-13 割り当てに従う",
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
