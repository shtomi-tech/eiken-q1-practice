"""英検1級 模試第12回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-12 の割り当てに従う。
Q19 の erudite は同一セットの erudition と紛らわしいため、余剰在庫の atrocious へ差し替えた。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-12"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "Every (   ) of the movement was expected to attend the weekly meeting and pay a small monthly fee.",
        "choices": ["infirmity", "adherent", "speculation", "prodigy"],
        "answerIndex": 1,
        "translation": "その運動の支持者は全員、週例会に出席し、少額の月会費を払うことになっていた。",
    },
    {
        "stem": "The soprano received a standing (   ) that lasted almost ten minutes after the final aria.",
        "choices": ["ovation", "ebullience", "infatuation", "swathe"],
        "answerIndex": 0,
        "translation": "そのソプラノ歌手は最後のアリアの後、10分近く続くスタンディングオベーションを受けた。",
    },
    {
        "stem": "A strange (   ) came over the crew after three weeks without wind, and nobody wanted to work.",
        "choices": ["repercussion", "lassitude", "surge", "chivalry"],
        "answerIndex": 1,
        "translation": "3週間も風がない後、奇妙な倦怠感が乗組員を覆い、誰も働きたがらなかった。",
    },
    {
        "stem": "The nurse cleaned a deep (   ) on the climber's forearm before applying the dressing.",
        "choices": ["totem", "imposition", "laceration", "camaraderie"],
        "answerIndex": 2,
        "translation": "看護師は包帯を当てる前に、その登山者の前腕の深い裂傷を洗浄した。",
    },
    {
        "stem": "After a brief (   ) in Lisbon, the family continued south toward the coast for the summer.",
        "choices": ["blight", "swamp", "avarice", "sojourn"],
        "answerIndex": 3,
        "translation": "リスボンでの短い滞在の後、その一家は海岸に向かって南へ進んだ。",
    },
    {
        "stem": "The (   ) of the host made even the most reluctant guests feel welcome that evening.",
        "choices": ["amiability", "opulence", "mutation", "grind"],
        "answerIndex": 0,
        "translation": "主人の愛想のよさは、その晩、最も気の進まない客でさえ歓迎されていると感じさせた。",
    },
    {
        "stem": "Fishing has been the (   ) of the island economy since long before the railway arrived.",
        "choices": ["erudition", "consecration", "caliber", "mainstay"],
        "answerIndex": 3,
        "translation": "漁業は鉄道が来るずっと以前から、その島の経済の柱であり続けている。",
    },
    {
        "stem": "The overseer (   ) the workers on the plantation for years until the estate was finally sold.",
        "choices": ["tyrannized", "consoled", "groveled", "dwindled"],
        "answerIndex": 0,
        "translation": "その監督は、地所がついに売却されるまで何年も労働者たちを圧政的に扱った。",
    },
    {
        "stem": "The court ordered the company to (   ) from advertising the drug as a cure.",
        "choices": ["subsidize", "desist", "perpetuate", "satirize"],
        "answerIndex": 1,
        "translation": "裁判所はその会社に、その薬を治療薬として宣伝することをやめるよう命じた。",
    },
    {
        "stem": "It (   ) on and off for most of the afternoon, so the painters covered the scaffolding.",
        "choices": ["lunged", "masqueraded", "drizzled", "reiterated"],
        "answerIndex": 2,
        "translation": "午後のほとんどの時間、小雨が降ったりやんだりしたので、塗装工たちは足場に覆いをかけた。",
    },
    {
        "stem": "The judge ordered that the jury be (   ) in a hotel until the verdict was reached.",
        "choices": ["emaciated", "salivated", "sequestered", "lubricated"],
        "answerIndex": 2,
        "translation": "裁判官は評決に達するまで陪審員をホテルに隔離するよう命じた。",
    },
    {
        "stem": "Rebel forces (   ) the fortress for eight months before supplies inside finally ran out.",
        "choices": ["remunerated", "annotated", "venerated", "besieged"],
        "answerIndex": 3,
        "translation": "反乱軍は8か月にわたってその要塞を包囲し、ついに内部の物資が尽きた。",
    },
    {
        "stem": "Parliament (   ) the law in 1997 after two decades of campaigning by civil rights groups.",
        "choices": ["flexed", "blanched", "repealed", "lathered"],
        "answerIndex": 2,
        "translation": "議会は市民権団体による20年の運動の後、1997年にその法律を廃止した。",
    },
    {
        "stem": "A team of codebreakers took four years to (   ) the substitution cipher used in signals from the northern outpost.",
        "choices": ["deviate", "stymie", "inter", "decipher"],
        "answerIndex": 3,
        "translation": "暗号解読班は北の前哨基地からの通信に使われた換字式暗号を解読するのに4年を要した。",
    },
    {
        "stem": "The (   ) pace of the newsroom in the final hour before publication exhausted the interns.",
        "choices": ["frenetic", "condescending", "lavish", "scant"],
        "answerIndex": 0,
        "translation": "発行前の最後の1時間の編集室の熱狂的な慌ただしさは、実習生たちを疲れ果てさせた。",
    },
    {
        "stem": "Her report to the committee was admirably (   ), covering the whole investigation in barely two pages.",
        "choices": ["docile", "succinct", "pensive", "copious"],
        "answerIndex": 1,
        "translation": "彼女の報告書は感心するほど簡潔で、調査全体をわずか2ページで扱っていた。",
    },
    {
        "stem": "The candidate's (   ) style impressed nobody, since the grand phrases carried no actual policy.",
        "choices": ["bombastic", "tenacious", "anecdotal", "malleable"],
        "answerIndex": 0,
        "translation": "その候補者の大げさな話し方は誰にも感銘を与えなかった。壮大な言い回しに実際の政策が伴っていなかったからだ。",
    },
    {
        "stem": "An (   ) smell of burning plastic stung the workers' eyes and forced everyone out of the building.",
        "choices": ["immaculate", "pompous", "acrid", "explicit"],
        "answerIndex": 2,
        "translation": "焼けたプラスチックの刺激臭が作業員の目にしみ、全員を建物の外へ追い出した。",
    },
    {
        "stem": "The claim was so (   ) that even the defendant's own lawyer struggled not to laugh.",
        "choices": ["malicious", "atrocious", "premeditated", "preposterous"],
        "answerIndex": 3,
        "translation": "その主張はあまりに馬鹿げていて、被告自身の弁護士でさえ笑いをこらえるのに苦労した。",
    },
    {
        "stem": "After twenty years of touring, the drummer had grown (   ) with hotels and airports.",
        "choices": ["jaded", "posthumous", "submissive", "inanimate"],
        "answerIndex": 0,
        "translation": "20年のツアー生活の後、そのドラマーはホテルと空港にうんざりしていた。",
    },
    {
        "stem": "She arranged the small pastries (   ) on a large silver tray before the first guests arrived.",
        "choices": ["fraudulently", "daintily", "fortuitously", "benevolently"],
        "answerIndex": 1,
        "translation": "彼女は客が到着する前に、菓子を銀の盆の上に上品に並べた。",
    },
    {
        "stem": "He (   ) in the same position for a decade, doing just enough to avoid attention.",
        "choices": ["coasted along", "rallied around", "nibbled at", "grated on"],
        "answerIndex": 0,
        "translation": "彼は注意を引かない程度の仕事だけをして、10年間同じ職位で惰性で過ごした。",
    },
    {
        "stem": "The airline (   ) its regional schedule after fuel prices rose for a fourth quarter.",
        "choices": ["butted in", "forked out", "nosed around", "cut back"],
        "answerIndex": 3,
        "translation": "その航空会社は燃料価格が4四半期連続で上昇した後、地方路線の運航計画を縮小した。",
    },
    {
        "stem": "The ministry (   ) the new registration system in three provinces before extending it nationwide.",
        "choices": ["rolled out", "picked over", "threw back", "passed off"],
        "answerIndex": 0,
        "translation": "省庁は新しい登録制度を全国に広げる前に3つの州で展開した。",
    },
    {
        "stem": "The board (   ) several proposals informally before asking the consultants for a full report.",
        "choices": ["wallowed in", "kicked around", "sided with", "bundled up"],
        "answerIndex": 1,
        "translation": "取締役会はコンサルタントに詳細な報告を求める前に、いくつかの案を非公式に検討した。",
    },
]


DETAILS = {
    # Q1
    "infirmity": ("虚弱、病弱", "名詞", "Age and infirmity finally forced the violinist to stop performing.", "高齢と病弱がついにそのバイオリン奏者に演奏をやめさせた。"),
    "adherent": ("支持者、信奉者", "名詞", "As a lifelong adherent of the theory, he refused to consider alternatives.", "その理論の生涯にわたる信奉者として、彼は代替案を検討することを拒んだ。"),
    "speculation": ("憶測、投機", "名詞", "Wild speculation about the merger filled the financial pages for weeks.", "合併についての勝手な憶測が何週間も経済面を埋めた。"),
    "prodigy": ("神童、天才児", "名詞", "The young prodigy performed with the national orchestra at eleven.", "その若い神童は11歳で国立管弦楽団と共演した。"),
    # Q2
    "ovation": ("熱烈な拍手喝采", "名詞", "The retiring conductor received a warm ovation from the orchestra itself.", "引退する指揮者は楽団員自身から温かい拍手喝采を受けた。"),
    "ebullience": ("あふれる元気、熱狂", "名詞", "His natural ebullience made him the obvious choice to greet visitors.", "彼の生まれつきの快活さは、来客を迎える役に彼を明らかな適任者にした。"),
    "infatuation": ("のぼせ上がり、夢中になること", "名詞", "Her infatuation with the city faded after a winter of gray skies.", "灰色の空が続く冬の後、彼女のその街への熱中は冷めた。"),
    "swathe": ("広い一帯、細長い区域", "名詞", "Fire destroyed a wide swathe of forest north of the highway.", "火災は幹線道路の北側の森林の広い一帯を焼き尽くした。"),
    # Q3
    "repercussion": ("(好ましくない)影響、余波", "名詞", "The closure had a lasting repercussion for every supplier in the valley.", "その閉鎖はその谷のすべての納入業者に長く続く影響を及ぼした。"),
    "lassitude": ("倦怠感、気だるさ", "名詞", "A heavy lassitude settled over the ward during the hottest week.", "最も暑い週の間、重い倦怠感が病棟を覆った。"),
    "surge": ("急増、急激な高まり", "名詞", "A sudden surge in applications overwhelmed the small admissions office.", "応募の急増が小さな入学事務室を圧倒した。"),
    "chivalry": ("騎士道精神、礼儀正しさ", "名詞", "The poem celebrates chivalry as it was imagined in the twelfth century.", "その詩は12世紀に思い描かれた形での騎士道精神をたたえている。"),
    # Q4
    "totem": ("トーテム、象徴", "名詞", "A carved totem stood at the entrance to the coastal village.", "彫刻されたトーテムがその沿岸の村の入り口に立っていた。"),
    "imposition": ("押しつけ、面倒をかけること", "名詞", "He apologized for the imposition and offered to pay for the taxi.", "彼は面倒をかけたことを詫び、タクシー代を払うと申し出た。"),
    "laceration": ("裂傷", "名詞", "The surgeon closed the laceration with eleven stitches that afternoon.", "外科医はその日の午後、11針でその裂傷を縫合した。"),
    "camaraderie": ("仲間意識、同志愛", "名詞", "The camaraderie among the night staff kept the clinic running smoothly.", "夜勤職員の間の仲間意識が診療所を円滑に動かし続けた。"),
    # Q5
    "blight": ("(植物の)病害、荒廃の原因", "名詞", "A fungal blight destroyed most of the potato crop that season.", "菌による病害がその季節のジャガイモ作の大半を全滅させた。"),
    "swamp": ("沼地、湿地", "名詞", "Rare herons nest in the swamp behind the abandoned mill.", "珍しいサギが廃工場の裏の沼地で営巣している。"),
    "avarice": ("強欲、貪欲", "名詞", "The novel treats avarice as the source of the family's ruin.", "その小説は強欲を一家の破滅の原因として扱っている。"),
    "sojourn": ("(一時的な)滞在", "名詞", "Her sojourn in Kyoto produced the sketches now hanging in the gallery.", "彼女の京都滞在は、今その画廊に掛かっているスケッチを生んだ。"),
    # Q6
    "amiability": ("愛想のよさ、人当たりのよさ", "名詞", "The doctor's amiability put anxious children at ease within moments.", "その医師の人当たりのよさは、不安な子どもたちをたちまち安心させた。"),
    "opulence": ("豪奢、非常な富裕", "名詞", "Visitors were startled by the opulence of the ballroom upstairs.", "訪問者たちは2階の舞踏室の豪奢さに驚いた。"),
    "mutation": ("突然変異", "名詞", "A single mutation made the bacteria resistant to the common treatment.", "1つの突然変異がその細菌を一般的な治療に耐性のあるものにした。"),
    "grind": ("骨の折れる単調な仕事", "名詞", "The daily grind of paperwork left her little time for research.", "書類仕事という日々の単調な労苦は、彼女に研究の時間をほとんど残さなかった。"),
    # Q7
    "erudition": ("博学、学識", "名詞", "His erudition was obvious, though he never mentioned his three doctorates.", "彼は3つの博士号に触れることはなかったが、その学識は明らかだった。"),
    "consecration": ("聖別、奉献", "名詞", "The consecration of the chapel drew worshippers from every nearby parish.", "その礼拝堂の聖別式は近隣のすべての教区から信者を集めた。"),
    "caliber": ("力量、水準", "名詞", "Few musicians of that caliber ever visit such a small town.", "あれほどの力量の音楽家がこのような小さな町を訪れることはめったにない。"),
    "mainstay": ("大黒柱、支柱", "名詞", "Tourism remains the mainstay of the local economy in summer.", "観光業は夏の地域経済の支柱であり続けている。"),
    # Q8
    "tyrannized": ("圧政的に支配した", "動詞", "The landlord tyrannized his tenants until a new law protected them.", "その地主は新しい法律が借家人を守るまで、彼らを圧政的に支配した。"),
    "consoled": ("慰めた", "動詞", "She consoled the losing team with a short and genuinely kind speech.", "彼女は短く心からやさしい言葉で敗れたチームを慰めた。"),
    "groveled": ("卑屈にへつらった", "動詞", "He groveled before the committee, hoping to keep his license.", "彼は免許を保持したいと願い、委員会の前で卑屈にへつらった。"),
    "dwindled": ("次第に減少した", "動詞", "Membership dwindled from six hundred to fewer than fifty.", "会員数は600人から50人未満へと次第に減っていった。"),
    # Q9
    "subsidize": ("補助金を出す", "動詞", "The prefecture agreed to subsidize bus routes serving mountain villages.", "県は山間の村を通るバス路線に補助金を出すことに同意した。"),
    "desist": ("(行為を)やめる、思いとどまる", "動詞", "Officials warned the trader to desist or face immediate prosecution.", "当局はその業者に、やめなければ直ちに起訴されると警告した。"),
    "perpetuate": ("永続させる、存続させる", "動詞", "Careless reporting can perpetuate stereotypes for another generation.", "不注意な報道は固定観念をもう一世代にわたって存続させかねない。"),
    "satirize": ("風刺する", "動詞", "The playwright chose to satirize the customs of the wealthy suburbs.", "その劇作家は裕福な郊外の習慣を風刺することを選んだ。"),
    # Q10
    "lunged": ("突進した、突きかかった", "動詞", "The goalkeeper lunged to his left and just reached the ball.", "そのゴールキーパーは左へ飛び込み、辛うじてボールに届いた。"),
    "masqueraded": ("(~の)ふりをした、仮装した", "動詞", "For months he masqueraded as a licensed surveyor in three counties.", "何か月もの間、彼は3つの郡で免許を持つ測量士のふりをしていた。"),
    "drizzled": ("霧雨が降った", "動詞", "It drizzled steadily throughout the opening ceremony on Saturday morning.", "土曜の朝の開会式の間中、絶え間なく霧雨が降っていた。"),
    "reiterated": ("繰り返し述べた", "動詞", "The chairman reiterated that no decision had yet been taken.", "議長はまだ何の決定もなされていないと繰り返し述べた。"),
    # Q11
    "emaciated": ("(衰弱して)やせ細らせた", "動詞", "Months of illness emaciated a man who had once been an athlete.", "何か月もの病気が、かつては運動選手だった男をやせ細らせた。"),
    "salivated": ("よだれを流した", "動詞", "The dogs salivated as soon as they heard the cupboard open.", "犬たちは戸棚が開く音を聞くとすぐによだれを流した。"),
    "sequestered": ("隔離した、押収した", "動詞", "Authorities sequestered the herd until the test results came back.", "当局は検査結果が出るまでその家畜の群れを隔離した。"),
    "lubricated": ("潤滑油を差した", "動詞", "The mechanic lubricated the chain and adjusted the rear brake.", "整備士はチェーンに潤滑油を差し、後輪ブレーキを調整した。"),
    # Q12
    "remunerated": ("報酬を支払った", "動詞", "Volunteers were not remunerated but received meals and travel costs.", "ボランティアには報酬は支払われなかったが、食事と交通費は支給された。"),
    "annotated": ("注釈をつけた", "動詞", "She annotated the margins of the score with fingering suggestions.", "彼女は楽譜の余白に運指の提案を注釈として書き込んだ。"),
    "venerated": ("崇敬した、あがめた", "動詞", "Pilgrims venerated the relic for centuries before it was moved.", "巡礼者たちはその聖遺物が移されるまで何世紀もそれを崇敬した。"),
    "besieged": ("包囲した", "動詞", "Troops besieged the walled city throughout the winter of 1453.", "軍勢は1453年の冬中、その城壁都市を包囲した。"),
    # Q13
    "flexed": ("(筋肉を)曲げ伸ばしした", "動詞", "The swimmer flexed her shoulders carefully before entering the pool.", "その水泳選手はプールに入る前に注意深く肩を曲げ伸ばしした。"),
    "blanched": ("青ざめた、湯通しした", "動詞", "He blanched when the surgeon described the length of the recovery.", "外科医が回復にかかる期間を説明すると、彼は青ざめた。"),
    "repealed": ("(法律を)廃止した", "動詞", "The assembly repealed a statute that had stood for ninety years.", "議会は90年間存続していた法令を廃止した。"),
    "lathered": ("泡立てた", "動詞", "The barber lathered his face before reaching for the razor.", "理髪師はかみそりに手を伸ばす前に彼の顔に泡を立てた。"),
    # Q14
    "deviate": ("逸脱する、それる", "動詞", "Pilots must not deviate from the assigned route without permission.", "パイロットは許可なく指定された経路から逸脱してはならない。"),
    "stymie": ("妨害する、行き詰まらせる", "動詞", "A single objection can stymie the entire planning process for months.", "1件の異議が計画の全過程を何か月も行き詰まらせることがある。"),
    "inter": ("埋葬する", "動詞", "The village agreed to inter the remains beside the old chapel.", "村はその遺骨を古い礼拝堂のそばに埋葬することに同意した。"),
    "decipher": ("解読する", "動詞", "Scholars still cannot decipher the script carved on the older tablets.", "学者たちは今なお古いほうの粘土板に刻まれた文字を解読できていない。"),
    # Q15
    "frenetic": ("熱狂的な、慌ただしい", "形容詞", "The frenetic activity on the trading floor stopped exactly at four.", "取引所内の慌ただしい動きは4時ちょうどに止まった。"),
    "condescending": ("見下すような、恩着せがましい", "形容詞", "His condescending tone offended the very people he hoped to persuade.", "彼の見下すような口調は、まさに説得したいと望んでいた人々を怒らせた。"),
    "lavish": ("豪華な、気前のよい", "形容詞", "The company held a lavish reception for its overseas distributors.", "その会社は海外の販売代理店のために豪華な歓迎会を開いた。"),
    "scant": ("わずかな、乏しい", "形容詞", "Rescuers had scant information about how many people were inside.", "救助隊は中に何人いるのかについてわずかな情報しか持っていなかった。"),
    # Q16
    "docile": ("従順な、おとなしい", "形容詞", "The mare is docile enough for beginners to ride safely.", "その雌馬は初心者が安全に乗れるほど従順である。"),
    "succinct": ("簡潔な", "形容詞", "A succinct summary at the top saved readers a great deal of time.", "冒頭の簡潔な要約は読者に多くの時間を節約させた。"),
    "pensive": ("物思いに沈んだ", "形容詞", "She grew pensive whenever the conversation turned to her childhood.", "会話が子ども時代のことになると、彼女はいつも物思いに沈んだ。"),
    "copious": ("おびただしい、豊富な", "形容詞", "He took copious notes during every one of the lectures.", "彼はどの講義でもおびただしい量のノートを取った。"),
    # Q17
    "bombastic": ("大げさな、大言壮語の", "形容詞", "The general's bombastic broadcasts convinced almost nobody by the third year.", "その将軍の大げさな放送は3年目にはほとんど誰も納得させなかった。"),
    "tenacious": ("粘り強い、執拗な", "形容詞", "A tenacious reporter obtained the documents after eleven refusals.", "粘り強い記者が11回の拒否の後にその文書を入手した。"),
    "anecdotal": ("逸話的な、伝聞に基づく", "形容詞", "The evidence remains anecdotal until a controlled trial is completed.", "対照試験が完了するまで、その証拠は逸話的なままである。"),
    "malleable": ("順応性のある、可鍛性の", "形容詞", "Gold is malleable enough to be beaten into extremely thin sheets.", "金は極めて薄い板に打ち延ばせるほど可鍛性がある。"),
    # Q18
    "immaculate": ("汚れ一つない、完璧な", "形容詞", "The mechanic kept his tools in immaculate condition for thirty years.", "その整備士は30年間、工具を汚れ一つない状態に保っていた。"),
    "pompous": ("尊大な、もったいぶった", "形容詞", "A pompous introduction lasting ten minutes irritated the whole audience.", "10分に及ぶもったいぶった紹介は聴衆全体をいらだたせた。"),
    "acrid": ("刺激臭のある、辛辣な", "形容詞", "An acrid taste lingered after he swallowed the medicine.", "薬を飲み込んだ後も刺激的な味が残った。"),
    "explicit": ("明白な、はっきり述べられた", "形容詞", "The contract contains an explicit ban on subletting the apartment.", "その契約書にはアパートの又貸しの明確な禁止が含まれている。"),
    # Q19
    "malicious": ("悪意のある", "形容詞", "A malicious rumor cost the shopkeeper half of his regular customers.", "悪意のあるうわさがその店主の常連客の半分を失わせた。"),
    "atrocious": ("極悪な、ひどい", "形容詞", "The tribunal documented atrocious treatment of prisoners in three camps.", "法廷は3つの収容所での捕虜への残虐な扱いを記録した。"),
    "premeditated": ("あらかじめ計画された", "形容詞", "Prosecutors argued that the crime had been carefully premeditated.", "検察はその犯行が入念に計画されたものだと主張した。"),
    "preposterous": ("ばかげた、途方もない", "形容詞", "The suggestion that the ship sank twice is simply preposterous.", "その船が2度沈んだという説はまったくばかげている。"),
    # Q20
    "jaded": ("うんざりした、飽き飽きした", "形容詞", "Even jaded critics admitted that the staging was genuinely original.", "飽き飽きした批評家でさえ、その演出が本当に独創的だと認めた。"),
    "posthumous": ("死後の", "形容詞", "The novelist received a posthumous award twelve years after her death.", "その小説家は死後12年たって没後の賞を受けた。"),
    "submissive": ("従順な、服従的な", "形容詞", "The dog rolled over in a submissive posture when scolded.", "その犬は叱られると服従の姿勢で寝転がった。"),
    "inanimate": ("生命のない、無生物の", "形容詞", "Children often assign feelings to inanimate objects such as dolls.", "子どもは人形のような無生物にしばしば感情を割り当てる。"),
    # Q21
    "fraudulently": ("不正に、詐欺的に", "副詞", "He fraudulently claimed benefits for a household that no longer existed.", "彼はもはや存在しない世帯の給付金を不正に請求した。"),
    "daintily": ("上品に、繊細に", "副詞", "The child daintily picked the raisins out of her cereal.", "その子どもは上品な手つきでシリアルからレーズンをつまみ出した。"),
    "fortuitously": ("偶然に、思いがけなく", "副詞", "The two researchers met fortuitously at an airport in Helsinki.", "その2人の研究者はヘルシンキの空港で偶然に出会った。"),
    "benevolently": ("慈悲深く、好意的に", "副詞", "The old shopkeeper smiled benevolently at the nervous new assistant.", "年老いた店主は緊張した新しい店員に慈しみ深くほほえんだ。"),
    # Q22
    "coasted along": ("惰性で進んだ、楽をして過ごした", "句動詞", "The department coasted along on its reputation for almost a decade.", "その学部は10年近くも評判に頼って惰性で進んできた。"),
    "rallied around": ("(人を)支えて結集した", "句動詞", "Neighbors rallied around the family whose roof had blown off.", "近隣の人々は屋根が吹き飛ばされた一家を支えようと結集した。"),
    "nibbled at": ("少しずつかじった、少しずつ手をつけた", "句動詞", "She nibbled at the sandwich without any real appetite.", "彼女は食欲もないままサンドイッチを少しずつかじった。"),
    "grated on": ("(神経に)障った、いらだたせた", "句動詞", "The constant beeping grated on everyone in the waiting room.", "絶え間ない電子音が待合室の全員の神経に障った。"),
    # Q23
    "butted in": ("口を挟んだ、割り込んだ", "句動詞", "A stranger butted in and answered before she could finish.", "見知らぬ人が口を挟み、彼女が言い終える前に答えてしまった。"),
    "forked out": ("(しぶしぶ)大金を払った", "句動詞", "They forked out a fortune for tickets to the final.", "彼らは決勝のチケットに大金をはたいた。"),
    "nosed around": ("嗅ぎ回った、詮索した", "句動詞", "A journalist nosed around the depot for most of the week.", "記者がその週のほとんど、車庫の周辺を嗅ぎ回っていた。"),
    "cut back": ("削減した、縮小した", "句動詞", "The hospital cut back on agency staff to balance its budget.", "その病院は予算の均衡を図るため派遣職員を削減した。"),
    # Q24
    "rolled out": ("(新制度などを)展開した", "句動詞", "The bank rolled out its updated app to customers in stages.", "その銀行は更新したアプリを顧客に段階的に展開した。"),
    "picked over": ("えり分けた、あさった", "句動詞", "Shoppers had picked over the sale table long before noon.", "買い物客は正午よりずっと前にセール品の台をあさり尽くしていた。"),
    "threw back": ("投げ返した、元へ戻した", "句動詞", "The angler threw back every fish under thirty centimeters.", "その釣り人は30センチ未満の魚をすべて放流した。"),
    "passed off": ("(偽って)通用させた", "句動詞", "He passed off a copy as an original for almost two years.", "彼は2年近く模写を本物と偽って通用させた。"),
    # Q25
    "wallowed in": ("(感情に)ひたりきった", "句動詞", "The film wallowed in nostalgia without saying anything new.", "その映画は新しいことを何も語らず、懐古趣味にひたりきっていた。"),
    "kicked around": ("(案を)あれこれ検討した", "句動詞", "The team kicked around a dozen names before choosing one.", "チームは1つを選ぶ前に十数個の名前をあれこれ検討した。"),
    "sided with": ("(~の)味方をした", "句動詞", "The tribunal sided with the tenants on every disputed point.", "審判所は争点のすべてにおいて借家人の側についた。"),
    "bundled up": ("厚着した、包んだ", "句動詞", "The children bundled up before walking to school in the snow.", "子どもたちは雪の中を学校まで歩く前に厚着をした。"),
}


CORE_IMAGES = {
    "coasted along": {
        "chain": [
            {"term": "coast", "gloss": "惰力で滑るように進む"},
            {"term": "along", "gloss": "そのまま進み続けて"},
            {"gloss": "力を入れずに流れに乗って進み続けて"},
            {"gloss": "惰性で過ごす"},
        ],
        "particle": "along",
    },
    "rallied around": {
        "chain": [
            {"term": "rally", "gloss": "呼び集める"},
            {"term": "around", "gloss": "その人の周りに"},
            {"gloss": "困っている人の周りに人が集まって"},
            {"gloss": "支えようと結集する"},
        ],
        "particle": "around",
    },
    "nibbled at": {
        "chain": [
            {"term": "nibble", "gloss": "少しずつかじる"},
            {"term": "at", "gloss": "その一点に触れて"},
            {"gloss": "端に少しずつ歯を当てて"},
            {"gloss": "少しずつ手をつける"},
        ],
    },
    "grated on": {
        "chain": [
            {"term": "grate", "gloss": "こすってすりおろす"},
            {"term": "on", "gloss": "相手の神経に触れて"},
            {"gloss": "同じところを繰り返しこすって"},
            {"gloss": "神経に障る"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "butted in": {
        "chain": [
            {"term": "butt", "gloss": "頭で突く"},
            {"term": "in", "gloss": "話の中へ割り込んで"},
            {"gloss": "頭から他人の話の中へ突っ込んで"},
            {"gloss": "口を挟む"},
        ],
        "particle": "in",
    },
    "forked out": {
        "chain": [
            {"term": "fork", "gloss": "フォークで取り分ける"},
            {"term": "out", "gloss": "手元から外へ出して"},
            {"gloss": "自分の懐から金を外へ出して"},
            {"gloss": "しぶしぶ大金を払う"},
        ],
        "particle": "out",
        "particleSense": "delegate",
    },
    "nosed around": {
        "chain": [
            {"term": "nose", "gloss": "鼻を近づけて嗅ぐ"},
            {"term": "around", "gloss": "あちこち回って"},
            {"gloss": "鼻先をあちこちに向けて探って"},
            {"gloss": "嗅ぎ回る、詮索する"},
        ],
        "particle": "around",
    },
    "cut back": {
        "chain": [
            {"term": "cut", "gloss": "切る"},
            {"term": "back", "gloss": "元の水準まで戻して"},
            {"gloss": "伸びた分を切って前の水準へ戻して"},
            {"gloss": "削減する"},
        ],
        "particle": "back",
    },
    "rolled out": {
        "chain": [
            {"term": "roll", "gloss": "転がして広げる"},
            {"term": "out", "gloss": "外へ送り出して"},
            {"gloss": "巻いたものを転がして外へ広げて"},
            {"gloss": "新しい制度や製品を展開する"},
        ],
        "particle": "out",
        "particleSense": "produce",
    },
    "picked over": {
        "chain": [
            {"term": "pick", "gloss": "つまみ上げる"},
            {"term": "over", "gloss": "全体を一渡り"},
            {"gloss": "並んだ物を一つずつ一渡り調べて"},
            {"gloss": "えり分ける、あさる"},
        ],
        "particle": "over",
    },
    "threw back": {
        "chain": [
            {"term": "throw", "gloss": "投げる"},
            {"term": "back", "gloss": "元の場所へ戻して"},
            {"gloss": "手にした物を元の場所へ投げ戻して"},
            {"gloss": "投げ返す、放流する"},
        ],
        "particle": "back",
    },
    "passed off": {
        "chain": [
            {"term": "pass", "gloss": "通す、渡す"},
            {"term": "off", "gloss": "本物から切り離したまま"},
            {"gloss": "中身を偽ったまま相手へ通して"},
            {"gloss": "偽って通用させる"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "wallowed in": {
        "chain": [
            {"term": "wallow", "gloss": "泥の中で転げ回る"},
            {"term": "in", "gloss": "その中にどっぷり浸かって"},
            {"gloss": "感情の中にどっぷり浸かって転げ回って"},
            {"gloss": "ひたりきる"},
        ],
        "particle": "in",
    },
    "kicked around": {
        "chain": [
            {"term": "kick", "gloss": "蹴る"},
            {"term": "around", "gloss": "皆の間をあちこちへ"},
            {"gloss": "案をボールのように皆の間で蹴り回して"},
            {"gloss": "あれこれ検討する"},
        ],
        "particle": "around",
    },
    "sided with": {
        "chain": [
            {"term": "side", "gloss": "側につく"},
            {"term": "with", "gloss": "その相手と一緒に"},
            {"gloss": "対立する二者の一方と同じ側に立って"},
            {"gloss": "~の味方をする"},
        ],
    },
    "bundled up": {
        "chain": [
            {"term": "bundle", "gloss": "束ねる"},
            {"term": "up", "gloss": "中へ包み込んで"},
            {"gloss": "体をすっぽり包み込んで"},
            {"gloss": "厚着する、包む"},
        ],
        "particle": "up",
        "particleSense": "contain",
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
        raise ValueError("模試第12回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-12 割り当てに従う",
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
