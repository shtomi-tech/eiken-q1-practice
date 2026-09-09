"""英検1級 模試第18回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-18 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-18"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "A sudden power (   ) last night left three northern districts without any heating for almost eleven hours.",
        "choices": ["partisan", "outage", "progeny", "redress"],
        "answerIndex": 1,
        "translation": "昨夜の突然の停電により、北部の3地区が11時間近くまったく暖房のない状態に置かれた。",
    },
    {
        "stem": "Women in the colony won full (   ) more than a decade before the mother country did.",
        "choices": ["suffrage", "rampage", "rampart", "fruition"],
        "answerIndex": 0,
        "translation": "その植民地の女性は、本国よりも10年以上早く完全な選挙権を勝ち取った。",
    },
    {
        "stem": "A dreadful (   ) from the drains drove customers out of the restaurant that evening.",
        "choices": ["acrimony", "hegemony", "blunder", "stench"],
        "answerIndex": 3,
        "translation": "その晩、排水口からのひどい悪臭が客をレストランの外へ追い出した。",
    },
    {
        "stem": "The (   ) of the local engineers kept the ferry running with no spare parts at all.",
        "choices": ["rubble", "ingenuity", "clout", "kickback"],
        "answerIndex": 1,
        "translation": "地元技術者の創意工夫が、予備部品がまったくない状態でそのフェリーを動かし続けた。",
    },
    {
        "stem": "She keeps a small (   ) from every city she has worked in on the shelf above her desk.",
        "choices": ["tycoon", "scruple", "memento", "protagonist"],
        "answerIndex": 2,
        "translation": "彼女は勤務したすべての都市の小さな記念品を机の上の棚に置いている。",
    },
    {
        "stem": "The new agreement finally established (   ) between the wages of full-time and part-time staff.",
        "choices": ["inhibition", "haven", "bureaucrat", "parity"],
        "answerIndex": 3,
        "translation": "その新しい協定はついに常勤職員と非常勤職員の賃金の間に同等性を確立した。",
    },
    {
        "stem": "The pond returned to (   ) about six months after the new plants were introduced.",
        "choices": ["denizen", "ruckus", "equilibrium", "lineage"],
        "answerIndex": 2,
        "translation": "その池は新しい水草が導入されてからおよそ半年で均衡を取り戻した。",
    },
    {
        "stem": "The old fireworks could easily burn or (   ) anyone standing nearby, and two children lost fingers last year.",
        "choices": ["maim", "pare", "scorn", "wriggle"],
        "answerIndex": 0,
        "translation": "その古い花火は近くに立つ人にやけどや重傷を負わせかねず、昨年は2人の子どもが指を失った。",
    },
    {
        "stem": "Two engineers were accused of trying to (   ) the pumps before they left the site.",
        "choices": ["mesmerize", "behold", "sabotage", "remit"],
        "answerIndex": 2,
        "translation": "2人の技術者が、現場を去る前にポンプを破壊工作しようとしたとして告発された。",
    },
    {
        "stem": "Vandals (   ) the war memorial with red paint on the night before the ceremony.",
        "choices": ["yielded", "transpired", "adjourned", "defaced"],
        "answerIndex": 3,
        "translation": "破壊行為者たちは式典の前夜、その戦争記念碑を赤いペンキで汚した。",
    },
    {
        "stem": "A stranger (   ) him outside the station and asked for money in a threatening way.",
        "choices": ["accosted", "parried", "fathomed", "forfeited"],
        "answerIndex": 0,
        "translation": "見知らぬ男が駅の外で彼に近づき、脅すような態度で金を求めた。",
    },
    {
        "stem": "The committee (   ) the remaining funds among four small rural clinics in December last year.",
        "choices": ["wagered", "rustled", "ambled", "allotted"],
        "answerIndex": 3,
        "translation": "委員会は昨年の12月に、残りの資金を4つの小さな地方診療所に割り当てた。",
    },
    {
        "stem": "The crew had to (   ) the vessel rather than let it fall into enemy hands.",
        "choices": ["dangle", "allude", "galvanize", "scuttle"],
        "answerIndex": 3,
        "translation": "乗組員は船を敵の手に渡すよりも自沈させなければならなかった。",
    },
    {
        "stem": "Careful questioning finally (   ) the one small detail that the first interview had missed.",
        "choices": ["lured", "elicited", "lambasted", "plundered"],
        "answerIndex": 1,
        "translation": "慎重な質問がついに、最初の聴取では取りこぼしたただ一つの小さな細部を引き出した。",
    },
    {
        "stem": "The gallery eventually discovered that two of its most admired old drawings were in fact (   ).",
        "choices": ["counterfeit", "insidious", "defamatory", "meticulous"],
        "answerIndex": 0,
        "translation": "その画廊はやがて、最も称賛されていた古い素描のうち2点が実は贋作であることを知った。",
    },
    {
        "stem": "His explanation of the missing hours was frankly (   ), since three witnesses had seen him leave the building.",
        "choices": ["nonchalant", "implausible", "dogmatic", "voracious"],
        "answerIndex": 1,
        "translation": "3人の証人が彼が建物を出るのを見ていたので、空白の時間についての彼の説明は率直に言ってありそうもなかった。",
    },
    {
        "stem": "The hut stood in a (   ) position on a ledge above the frozen lake.",
        "choices": ["lugubrious", "banal", "precarious", "nocturnal"],
        "answerIndex": 2,
        "translation": "その小屋は凍った湖を見下ろす岩棚の上の危なっかしい場所に建っていた。",
    },
    {
        "stem": "The evidence for the earlier date is thin and frankly (   ) in several important respects.",
        "choices": ["languid", "chivalrous", "insubstantial", "homely"],
        "answerIndex": 2,
        "translation": "より早い年代を示す証拠は乏しく、いくつかの重要な点で率直に言って実質を欠いている。",
    },
    {
        "stem": "An (   ) repair by the driver got the bus back on the road within twenty minutes.",
        "choices": ["subdued", "lurid", "trite", "adroit"],
        "answerIndex": 3,
        "translation": "運転手の巧みな修理により、そのバスは20分以内に運行に戻った。",
    },
    {
        "stem": "Repeated late nights were clearly (   ) to the quality of the work he produced.",
        "choices": ["barbaric", "detrimental", "desultory", "derisive"],
        "answerIndex": 1,
        "translation": "度重なる夜更かしは彼が生み出す仕事の質にとって明らかに有害だった。",
    },
    {
        "stem": "The second sample was only (   ) better than the first one they had tested.",
        "choices": ["marginally", "bashfully", "intently", "tenaciously"],
        "answerIndex": 0,
        "translation": "2つ目の試料は、最初に検査したものよりわずかに優れていただけだった。",
    },
    {
        "stem": "The board (   ) her twice for promotion before she finally moved to a rival firm.",
        "choices": ["doted on", "stitched up", "whisked away", "passed over"],
        "answerIndex": 3,
        "translation": "取締役会は彼女を2度昇進で見送り、彼女はついに競合会社へ移った。",
    },
    {
        "stem": "The whole legal argument (   ) a single letter that nobody has ever actually produced.",
        "choices": ["raked in", "swore by", "hinged on", "snuffed out"],
        "answerIndex": 2,
        "translation": "その法的な議論全体は、誰も実際に提出したことのない1通の手紙にかかっていた。",
    },
    {
        "stem": "The guide (   ) the names of every peak in the range without pausing once.",
        "choices": ["lived up to", "rattled off", "stood out from", "zeroed in on"],
        "answerIndex": 1,
        "translation": "案内人は一度も間を置かずに、その山脈のすべての峰の名前をすらすらと挙げた。",
    },
    {
        "stem": "Good secondhand instruments are notoriously hard to (   ) in a town of this size.",
        "choices": ["come by", "chime in", "answer back", "crouch down"],
        "answerIndex": 0,
        "translation": "この規模の町では、状態のよい中古の楽器を手に入れるのは周知のとおり難しい。",
    },
]


DETAILS = {
    # Q1
    "partisan": ("熱烈な支持者、パルチザン", "名詞", "He was too much of a partisan to chair a neutral inquiry.", "彼は熱烈な支持者でありすぎて、中立な調査の議長は務まらなかった。"),
    "outage": ("停電、供給停止", "名詞", "The outage affected every household on the eastern side of town.", "その停電は町の東側の全世帯に影響した。"),
    "progeny": ("子孫", "名詞", "The stallion's progeny won three major races that season.", "その種牡馬の子孫はその季節に3つの大レースを勝った。"),
    "redress": ("救済、是正", "名詞", "Tenants sought redress through a tribunal rather than the courts.", "借家人たちは裁判所ではなく審判所を通じて救済を求めた。"),
    # Q2
    "suffrage": ("選挙権、参政権", "名詞", "Universal suffrage was not achieved here until after the war.", "ここで普通選挙が実現したのは戦後になってからだった。"),
    "rampage": ("暴れ回ること", "名詞", "An elephant on the rampage destroyed two fences and a shed.", "暴れ回るゾウが2つの柵と小屋を壊した。"),
    "rampart": ("城壁、防壁", "名詞", "Visitors can still walk along the medieval rampart above the river.", "訪問者は今も川の上の中世の城壁の上を歩くことができる。"),
    "fruition": ("結実、実現", "名詞", "The plan came to fruition eleven years after it was first drawn.", "その計画は最初に描かれてから11年後に実を結んだ。"),
    # Q3
    "acrimony": ("辛辣さ、激しい恨み", "名詞", "The partnership ended in acrimony and a long legal dispute.", "その提携は激しい反目と長い法廷闘争のうちに終わった。"),
    "hegemony": ("覇権、支配権", "名詞", "The port lost its commercial hegemony in the eighteenth century.", "その港は18世紀に商業上の覇権を失った。"),
    "blunder": ("大失策", "名詞", "A simple blunder in the schedule cost the tour two performances.", "日程表の単純な失策がその公演旅行から2公演を失わせた。"),
    "stench": ("悪臭", "名詞", "The stench of the tannery reached the village whenever the wind turned.", "風向きが変わるたびに、なめし工場の悪臭が村まで届いた。"),
    # Q4
    "rubble": ("瓦礫", "名詞", "Volunteers cleared the rubble from the school yard by hand.", "ボランティアたちは校庭の瓦礫を手作業で片づけた。"),
    "ingenuity": ("創意工夫、独創性", "名詞", "The design shows real ingenuity in the use of very cheap materials.", "その設計は非常に安価な材料の使い方に真の創意工夫を示している。"),
    "clout": ("影響力、権勢", "名詞", "A small union with surprising clout blocked the whole reorganization.", "驚くほどの影響力を持つ小さな組合が組織再編全体を阻止した。"),
    "kickback": ("リベート、不正な謝礼", "名詞", "Two inspectors were dismissed for accepting a kickback from the contractor.", "2人の検査官が請負業者からのリベートを受け取り解雇された。"),
    # Q5
    "tycoon": ("大立者、実業界の大物", "名詞", "A shipping tycoon paid for the entire concert hall.", "海運業の大物がそのコンサートホール全体の費用を出した。"),
    "scruple": ("良心のとがめ、ためらい", "名詞", "He had not the slightest scruple about reading other people's mail.", "彼は他人の郵便物を読むことに少しの良心のとがめも持たなかった。"),
    "memento": ("記念品、形見", "名詞", "The watch is a memento of her first year at sea.", "その腕時計は彼女の海上勤務1年目の記念品である。"),
    "protagonist": ("主人公、主要人物", "名詞", "The protagonist of the novel never speaks in the first three chapters.", "その小説の主人公は最初の3章で一言も話さない。"),
    # Q6
    "inhibition": ("抑制、ためらい", "名詞", "The drug reduces inhibition, which is why driving is forbidden.", "その薬は抑制を弱めるため、運転が禁止されている。"),
    "haven": ("避難所、安息の地", "名詞", "The marshes are a haven for birds that winter in the south.", "その湿地は南で越冬する鳥にとっての安息の地である。"),
    "bureaucrat": ("官僚、お役所仕事の人", "名詞", "A cautious bureaucrat delayed the permit for another eight months.", "慎重な官僚がその許可をさらに8か月遅らせた。"),
    "parity": ("同等、等価", "名詞", "The union demanded parity with workers at the northern plant.", "組合は北部工場の労働者との同等の待遇を要求した。"),
    # Q7
    "denizen": ("居住者、生息するもの", "名詞", "The otter is a shy denizen of these upland streams.", "カワウソはこれらの高地の小川に生息する臆病な住人である。"),
    "ruckus": ("騒動、大騒ぎ", "名詞", "A ruckus in the corridor brought two members of staff running.", "廊下での騒動に職員2人が駆けつけた。"),
    "equilibrium": ("均衡、平衡", "名詞", "The market found a new equilibrium after the tariffs were removed.", "関税が撤廃された後、市場は新たな均衡を見いだした。"),
    "lineage": ("血統、系統", "名詞", "The family traces its lineage to a fourteenth-century merchant.", "その一族は自らの血統を14世紀の商人までたどっている。"),
    # Q8
    "maim": ("重傷を負わせる、不具にする", "動詞", "Landmines continue to maim farmers decades after the fighting ended.", "地雷は戦闘が終わって何十年もたった今も農民に重傷を負わせ続けている。"),
    "pare": ("(皮を)むく、削減する", "動詞", "The council had to pare its cultural budget by a third.", "議会は文化予算を3分の1削減しなければならなかった。"),
    "mesmerize": ("魅了する、うっとりさせる", "動詞", "A skilled storyteller can mesmerize an audience of any age.", "熟練した語り手はどの年代の聴衆でも魅了できる。"),
    "wriggle": ("身をよじる、くねくね動く", "動詞", "The puppy would wriggle out of any collar they tried.", "その子犬はどの首輪からも身をよじって抜け出してしまった。"),
    # Q9
    "scorn": ("軽蔑する", "動詞", "Purists scorn any recording made outside a concert hall.", "純粋主義者はコンサートホール以外で作られた録音を軽蔑する。"),
    "behold": ("(目にして)眺める", "動詞", "Visitors climb the tower to behold the whole valley at once.", "訪問者は谷全体を一望するために塔に登る。"),
    "sabotage": ("破壊工作をする、妨害する", "動詞", "Someone tried to sabotage the ventilation system during the night shift.", "何者かが夜勤の間に換気システムを妨害しようとした。"),
    "remit": ("送金する、免除する", "動詞", "Workers remit part of their wages to families in the south every month.", "労働者たちは毎月、賃金の一部を南部の家族へ送金する。"),
    # Q10
    "defaced": ("(表面を)汚した、傷つけた", "動詞", "Someone defaced every poster along the station platform.", "何者かが駅のホーム沿いのすべてのポスターを汚した。"),
    "yielded": ("生み出した、譲った", "動詞", "The orchard yielded twice as much fruit as the previous season.", "その果樹園は前の季節の2倍の果実を生み出した。"),
    "transpired": ("(事が)判明した、起こった", "動詞", "It transpired that the letter had been sent to the wrong department.", "その手紙が誤った部署へ送られていたことが判明した。"),
    "adjourned": ("(会議を)休会にした", "動詞", "The chair adjourned the meeting until the following Tuesday.", "議長は会議を翌週の火曜日まで休会にした。"),
    # Q11
    "accosted": ("(見知らぬ人に)近づいて話しかけた", "動詞", "A journalist accosted the minister as he left the building.", "記者は建物を出る大臣に近づいて話しかけた。"),
    "parried": ("受け流した、かわした", "動詞", "She parried the question with a joke about the weather.", "彼女は天気についての冗談でその質問を受け流した。"),
    "fathomed": ("(真意などを)理解した", "動詞", "Nobody has ever fathomed why the letters were never posted.", "その手紙がなぜ一度も投函されなかったのか、誰にも理解できていない。"),
    "forfeited": ("(権利を)失った、没収された", "動詞", "The team forfeited the match by arriving two hours late.", "そのチームは2時間遅刻したことで試合を没収された。"),
    # Q12
    "wagered": ("賭けた", "動詞", "He wagered a week's wages on a horse he had never seen.", "彼は見たこともない馬に1週間分の賃金を賭けた。"),
    "rustled": ("かさかさ音を立てた、家畜を盗んだ", "動詞", "Dry leaves rustled underfoot along the whole length of the path.", "小道全体にわたり、乾いた葉が足元でかさかさと音を立てた。"),
    "ambled": ("ぶらぶら歩いた", "動詞", "The old horse ambled across the field toward the gate.", "その老馬は門に向かって野原をゆっくりと歩いていった。"),
    "allotted": ("割り当てた", "動詞", "The organizers allotted each speaker exactly twelve minutes for the presentation.", "主催者は各講演者に発表のためきっかり12分を割り当てた。"),
    # Q13
    "scuttle": ("(船を)自沈させる、急いで走る", "動詞", "The captain gave the order to scuttle the ship at dawn.", "船長は夜明けにその船を自沈させるよう命じた。"),
    "dangle": ("ぶら下げる、ぶら下がる", "動詞", "Do not dangle your feet over the side of the boat.", "船べりから足をぶら下げてはいけない。"),
    "allude": ("それとなく言及する", "動詞", "The report does not allude to the earlier investigation at all.", "その報告書は以前の調査についてまったく言及していない。"),
    "galvanize": ("活気づける、刺激して行動させる", "動詞", "A single photograph can galvanize public opinion overnight.", "1枚の写真が一夜にして世論を奮い立たせることがある。"),
    # Q14
    "lured": ("おびき寄せた、誘い込んだ", "動詞", "Cheap rents lured young designers into the disused mill.", "安い家賃が若いデザイナーたちを使われなくなった工場へ誘い込んだ。"),
    "elicited": ("引き出した、聞き出した", "動詞", "The survey elicited responses from more than nine thousand households.", "その調査は9000を超える世帯から回答を引き出した。"),
    "lambasted": ("こっぴどく非難した", "動詞", "Reviewers lambasted the production for its careless translation.", "批評家たちはその公演を杜撰な翻訳ゆえにこっぴどく非難した。"),
    "plundered": ("略奪した", "動詞", "Invading armies plundered the abbey and burned its library.", "侵攻した軍隊は修道院を略奪し、その図書室を焼いた。"),
    # Q15
    "counterfeit": ("偽造の、贋物の", "形容詞", "Bank staff are trained to recognize counterfeit notes by touch.", "銀行員は触感で偽札を見分けるよう訓練されている。"),
    "insidious": ("知らぬ間に進行する、陰険な", "形容詞", "Damp is an insidious problem that appears only years later.", "湿気は何年もたってから現れる、知らぬ間に進行する問題である。"),
    "defamatory": ("名誉毀損の、中傷的な", "形容詞", "The publisher withdrew a chapter said to be defamatory.", "出版社は名誉毀損に当たるとされた1章を撤回した。"),
    "meticulous": ("細心の、綿密な", "形容詞", "His meticulous notes made the later reconstruction of the machine possible.", "彼の綿密な記録が後の機械の復元を可能にした。"),
    # Q16
    "nonchalant": ("無頓着な、平然とした", "形容詞", "He was oddly nonchalant about losing the entire deposit.", "彼は預けた金を全額失ったことに奇妙なほど平然としていた。"),
    "implausible": ("ありそうもない、信じがたい", "形容詞", "The alibi seemed implausible from the very first hearing.", "そのアリバイは最初の審理から信じがたいものに思われた。"),
    "dogmatic": ("独断的な", "形容詞", "He is dogmatic about methods he has never actually tested.", "彼は実際に試したことのない方法について独断的である。"),
    "voracious": ("貪欲な、大食の", "形容詞", "She is a voracious reader who finishes a novel every two days.", "彼女は2日に1冊の小説を読み終える貪欲な読書家である。"),
    # Q17
    "lugubrious": ("陰気な、もの悲しい", "形容詞", "A lugubrious tune from the next room made everyone quiet.", "隣室からのもの悲しい調べが全員を黙らせた。"),
    "banal": ("陳腐な、ありふれた", "形容詞", "The dialogue is banal, though the photography is remarkable.", "撮影は見事だが、せりふは陳腐である。"),
    "precarious": ("不安定な、危なっかしい", "形容詞", "The ladder rested in a precarious position against the wet wall.", "はしごは濡れた壁に危なっかしい角度で立てかけられていた。"),
    "nocturnal": ("夜行性の、夜の", "形容詞", "Most of the mammals on the island are strictly nocturnal.", "その島の哺乳類のほとんどは完全に夜行性である。"),
    # Q18
    "languid": ("気だるい、力のない", "形容詞", "A languid breeze barely moved the flags above the entrance.", "気だるい風は入り口の上の旗をほとんど動かさなかった。"),
    "chivalrous": ("騎士道的な、礼儀正しい", "形容詞", "A chivalrous gesture from the older player won over the crowd.", "年長の選手の礼儀正しい振る舞いが観衆の心をつかんだ。"),
    "insubstantial": ("実質のない、薄弱な", "形容詞", "The case against her was insubstantial and quickly collapsed.", "彼女に対する立件は根拠が薄弱で、すぐに崩れた。"),
    "homely": ("家庭的な、飾り気のない", "形容詞", "The inn serves homely food at a very fair price.", "その宿は家庭的な料理をとても手頃な値段で出す。"),
    # Q19
    "adroit": ("巧みな、器用な", "形容詞", "An adroit chairman kept the meeting to its allotted hour.", "巧みな議長が会議を割り当てられた1時間に収めた。"),
    "subdued": ("控えめな、元気のない", "形容詞", "The mood in the office was subdued after the announcement.", "発表の後、職場の雰囲気は沈んでいた。"),
    "lurid": ("どぎつい、けばけばしい", "形容詞", "The paper printed a lurid account of a very ordinary quarrel.", "その新聞はごくありふれた口論をどぎつく書き立てた。"),
    "trite": ("使い古された、陳腐な", "形容詞", "The advice sounds trite but works remarkably well in practice.", "その助言は使い古されて聞こえるが、実際には驚くほどよく効く。"),
    # Q20
    "barbaric": ("野蛮な、残虐な", "形容詞", "The practice was outlawed as barbaric in the previous century.", "その慣行は前世紀に野蛮なものとして禁止された。"),
    "detrimental": ("有害な、不利益な", "形容詞", "Constant interruption is detrimental to any careful work.", "絶え間ない中断はあらゆる緻密な作業にとって有害である。"),
    "desultory": ("散漫な、とりとめのない", "形容詞", "A desultory conversation continued until the train arrived.", "列車が来るまで、とりとめのない会話が続いた。"),
    "derisive": ("あざけるような", "形容詞", "A derisive laugh from the back row unsettled the speaker.", "後列からのあざけるような笑いが話し手を動揺させた。"),
    # Q21
    "marginally": ("わずかに", "副詞", "The second design is marginally cheaper but much heavier.", "2つ目の設計はわずかに安いが、はるかに重い。"),
    "bashfully": ("恥ずかしそうに", "副詞", "He bashfully accepted the prize and left the stage quickly.", "彼は恥ずかしそうに賞を受け取り、素早く舞台を降りた。"),
    "intently": ("熱心に、じっと", "副詞", "The children watched intently as the potter shaped the bowl.", "陶工が鉢の形を作る様子を、子どもたちはじっと見つめていた。"),
    "tenaciously": ("粘り強く、執拗に", "副詞", "She tenaciously pursued the records through four separate archives.", "彼女は4つの別々の文書館を通じて粘り強くその記録を追った。"),
    # Q22
    "passed over": ("(昇進などで)見送った", "句動詞", "He was passed over for the post he had been promised.", "彼は約束されていた職への昇進を見送られた。"),
    "doted on": ("溺愛した", "句動詞", "Their grandmother doted on the youngest child quite openly.", "彼らの祖母は末の子を実にあからさまに溺愛していた。"),
    "stitched up": ("(人を)はめた、縫い合わせた", "句動詞", "The witness claimed he had been stitched up by his own partner.", "その証人は自分の相棒にはめられたと主張した。"),
    "whisked away": ("さっと連れ去った", "句動詞", "Officials whisked away the visiting minister before anyone could ask questions.", "職員たちは誰も質問できないうちに来訪した大臣をさっと連れ去った。"),
    # Q23
    "raked in": ("(金を)荒稼ぎした", "句動詞", "The stall raked in more money on Saturday than all week.", "その屋台は土曜日だけで平日1週間分より多くの金を稼いだ。"),
    "swore by": ("(~を)絶対だと信じた", "句動詞", "My grandfather swore by cold water for every minor ailment.", "祖父はどんな軽い不調にも冷水が一番だと固く信じていた。"),
    "hinged on": ("(~に)かかっていた", "句動詞", "Everything hinged on whether the ferry could sail that night.", "すべてはその夜フェリーが出られるかどうかにかかっていた。"),
    "snuffed out": ("(火や希望を)消した", "句動詞", "A late goal snuffed out any hope of promotion that season.", "終盤のゴールがその季節の昇格の望みを断ち切った。"),
    # Q24
    "rattled off": ("すらすらと述べた", "句動詞", "The child rattled off the names of every planet in order.", "その子どもはすべての惑星の名前を順にすらすらと言ってのけた。"),
    "lived up to": ("(期待に)応えた", "句動詞", "The restaurant lived up to everything the guidebook had promised.", "そのレストランは案内書が約束していたすべてに応えた。"),
    "stood out from": ("(~より)際立った", "句動詞", "Her application stood out from four hundred others on the pile.", "彼女の応募書類は積まれた400通の中で際立っていた。"),
    "zeroed in on": ("(~に)狙いを定めた", "句動詞", "Investigators zeroed in on a single supplier within a week.", "捜査員たちは1週間のうちに1社の納入業者に狙いを絞った。"),
    # Q25
    "come by": ("手に入れる、立ち寄る", "句動詞", "Fresh milk was hard to come by in the mountain villages.", "山村では新鮮な牛乳を手に入れるのは難しかった。"),
    "chime in": ("口を挟む、相づちを打つ", "句動詞", "A neighbor would chime in whenever the subject of parking arose.", "駐車の話題が出るたびに、近所の人が口を挟むのだった。"),
    "answer back": ("口答えする", "句動詞", "Pupils here are not afraid to answer back when they disagree.", "ここの生徒は納得できないときに口答えすることを恐れない。"),
    "crouch down": ("しゃがみ込む", "句動詞", "You have to crouch down to get through the low doorway.", "その低い戸口を通るにはしゃがまなければならない。"),
}


CORE_IMAGES = {
    "passed over": {
        "chain": [
            {"term": "pass", "gloss": "通り過ぎる"},
            {"term": "over", "gloss": "その上を越して"},
            {"gloss": "候補者の上を素通りして次へ行って"},
            {"gloss": "昇進などで見送る"},
        ],
        "particle": "over",
    },
    "doted on": {
        "chain": [
            {"term": "dote", "gloss": "夢中になる"},
            {"term": "on", "gloss": "その相手に向けて"},
            {"gloss": "愛情を一人の相手に注ぎ続けて"},
            {"gloss": "溺愛する"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "stitched up": {
        "chain": [
            {"term": "stitch", "gloss": "縫う"},
            {"term": "up", "gloss": "すっかり縫い閉じて"},
            {"gloss": "逃げ道がなくなるまで縫い閉じて"},
            {"gloss": "人をはめる、仕立て上げる"},
        ],
        "particle": "up",
        "particleSense": "complete",
    },
    "whisked away": {
        "chain": [
            {"term": "whisk", "gloss": "さっと動かす"},
            {"term": "away", "gloss": "その場から離して"},
            {"gloss": "人目につく前にさっとその場から離して"},
            {"gloss": "さっと連れ去る"},
        ],
        "particle": "away",
    },
    "raked in": {
        "chain": [
            {"term": "rake", "gloss": "熊手でかき集める"},
            {"term": "in", "gloss": "手元へ集めて"},
            {"gloss": "散らばった金を熊手で手元へかき集めて"},
            {"gloss": "荒稼ぎする"},
        ],
        "particle": "in",
    },
    "swore by": {
        "chain": [
            {"term": "swear", "gloss": "誓う"},
            {"term": "by", "gloss": "それをよりどころにして"},
            {"gloss": "そのものにかけて誓えるほど頼りにして"},
            {"gloss": "~を絶対だと信じる"},
        ],
        "particle": "by",
    },
    "hinged on": {
        "chain": [
            {"term": "hinge", "gloss": "蝶番でつながる"},
            {"term": "on", "gloss": "その一点を支えにして"},
            {"gloss": "扉が蝶番一つで動くようにその一点に支えられて"},
            {"gloss": "~にかかっている"},
        ],
        "particle": "on",
        "particleSense": "rely",
    },
    "snuffed out": {
        "chain": [
            {"term": "snuff", "gloss": "ろうそくの芯をつまむ"},
            {"term": "out", "gloss": "火を消し尽くして"},
            {"gloss": "芯をつまんで炎を消し尽くして"},
            {"gloss": "火や望みを絶つ"},
        ],
        "particle": "out",
        "particleSense": "exhaust",
    },
    "rattled off": {
        "chain": [
            {"term": "rattle", "gloss": "がたがたと連続音を立てる"},
            {"term": "off", "gloss": "次々と口から出して"},
            {"gloss": "間を置かず次々と口から出して"},
            {"gloss": "すらすらと述べる"},
        ],
        "particle": "off",
        "particleSense": "express",
    },
    "lived up to": {
        "chain": [
            {"term": "live", "gloss": "生きる、行動する"},
            {"term": "up to", "gloss": "求められる水準まで"},
            {"gloss": "掲げられた水準に届くように行動して"},
            {"gloss": "期待に応える"},
        ],
        "particle": "up to",
        "particleSense": "standard",
    },
    "stood out from": {
        "chain": [
            {"term": "stand", "gloss": "立つ"},
            {"term": "out", "gloss": "他より外へ突き出て"},
            {"gloss": "並んだものの列から外へ突き出て"},
            {"gloss": "~より際立つ"},
        ],
        "particle": "out",
        "particleSense": "spread",
    },
    "zeroed in on": {
        "chain": [
            {"term": "zero", "gloss": "照準を合わせる"},
            {"term": "in", "gloss": "的の中心へ入って"},
            {"gloss": "照準を的の中心へ絞り込んで"},
            {"gloss": "~に狙いを定める"},
        ],
        "particle": "in",
    },
    "come by": {
        "chain": [
            {"term": "come", "gloss": "来る"},
            {"term": "by", "gloss": "そばを通りがかって"},
            {"gloss": "通りがかりに手元へ来て"},
            {"gloss": "手に入れる"},
        ],
        "particle": "by",
    },
    "chime in": {
        "chain": [
            {"term": "chime", "gloss": "鐘が鳴る"},
            {"term": "in", "gloss": "話の中へ入って"},
            {"gloss": "鐘の音が加わるように話の中へ入って"},
            {"gloss": "口を挟む"},
        ],
        "particle": "in",
    },
    "answer back": {
        "chain": [
            {"term": "answer", "gloss": "答える"},
            {"term": "back", "gloss": "相手へ言い返して"},
            {"gloss": "言われたことをそのまま相手へ言い返して"},
            {"gloss": "口答えする"},
        ],
        "particle": "back",
    },
    "crouch down": {
        "chain": [
            {"term": "crouch", "gloss": "身をかがめる"},
            {"term": "down", "gloss": "低い位置へ下げて"},
            {"gloss": "膝を折って体を低い位置へ下げて"},
            {"gloss": "しゃがみ込む"},
        ],
        "particle": "down",
        "particleSense": "descend",
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
        raise ValueError("模試第18回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-18 割り当てに従う",
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
