"""英検1級 模試第17回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-17 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-17"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "A loud (   ) between two delivery drivers blocked the busy junction for almost twenty minutes yesterday.",
        "choices": ["debutante", "concession", "bombardment", "altercation"],
        "answerIndex": 3,
        "translation": "2人の配送運転手による大声の口論が、20分近くその混雑した交差点をふさいだ。",
    },
    {
        "stem": "The return of the swallows is traditionally regarded as a (   ) of spring in the region.",
        "choices": ["harbinger", "poise", "decorum", "insinuation"],
        "answerIndex": 0,
        "translation": "ツバメの帰還は、その地域では伝統的に春の前触れと見なされている。",
    },
    {
        "stem": "The government imposed an (   ) on all the timber leaving the northern ports last year.",
        "choices": ["bundle", "embargo", "reconnaissance", "havoc"],
        "answerIndex": 1,
        "translation": "政府は昨年、北部の港から出るすべての木材に禁輸措置を課した。",
    },
    {
        "stem": "Laboratory tests eventually confirmed the (   ) of the strain found during the second outbreak.",
        "choices": ["debris", "pleasantry", "virulence", "demarcation"],
        "answerIndex": 2,
        "translation": "実験室での検査は最終的に、2度目の流行の間に見つかった株の毒性の強さを裏付けた。",
    },
    {
        "stem": "Being asked to prove his own citizenship was a genuine (   ) to a man born in the town.",
        "choices": ["coercion", "respite", "inertia", "affront"],
        "answerIndex": 3,
        "translation": "自分の市民権を証明せよと求められたことは、その町で生まれた男にとって本当の侮辱だった。",
    },
    {
        "stem": "The (   ) of the sentence surprised even the lawyers who had followed the case closely.",
        "choices": ["severity", "oration", "eviction", "regression"],
        "answerIndex": 0,
        "translation": "その判決の厳しさは、事件を注意深く追ってきた弁護士たちさえ驚かせた。",
    },
    {
        "stem": "The whole discovery was pure (   ): she had been looking for something else entirely.",
        "choices": ["emblem", "felicity", "serendipity", "conveyance"],
        "answerIndex": 2,
        "translation": "その発見はまったくの偶然の産物だった。彼女はまるで別のものを探していたのである。",
    },
    {
        "stem": "The architect wanted to (   ) the whole building with a sense of calm and openness.",
        "choices": ["avail", "imbue", "foment", "pilfer"],
        "answerIndex": 1,
        "translation": "その建築家は建物全体に静けさと開放感を吹き込みたいと考えた。",
    },
    {
        "stem": "The head teacher (   ) the older pupils for leaving litter in the main corridor again.",
        "choices": ["admonished", "marred", "appended", "propelled"],
        "answerIndex": 0,
        "translation": "校長は本館の廊下にまたごみを残したことで上級生たちを戒めた。",
    },
    {
        "stem": "Thick curtains and heavy carpets (   ) almost every sound coming from the street outside.",
        "choices": ["spanned", "deposed", "stifled", "berated"],
        "answerIndex": 2,
        "translation": "厚いカーテンと重いじゅうたんが、外の通りから入ってくるほとんどすべての音を抑えていた。",
    },
    {
        "stem": "A single storm (   ) the seabird colony that had nested on the cliff for centuries.",
        "choices": ["regaled", "droned", "decimated", "consecrated"],
        "answerIndex": 2,
        "translation": "1度の嵐が、何世紀もその崖で営巣してきた海鳥の集団を壊滅させた。",
    },
    {
        "stem": "Her voice (   ) only once, when she mentioned the name of her old teacher.",
        "choices": ["faltered", "goaded", "incriminated", "detested"],
        "answerIndex": 0,
        "translation": "彼女の声が震えたのは一度だけで、それは昔の恩師の名前に触れたときだった。",
    },
    {
        "stem": "The exhausted garrison finally (   ) after eleven weeks without any fresh water or medicine.",
        "choices": ["blurred", "barricaded", "capitulated", "alienated"],
        "answerIndex": 2,
        "translation": "疲弊した守備隊は真水も薬もまったくない11週間の後、ついに降伏した。",
    },
    {
        "stem": "Technicians must (   ) the two large mirrors precisely, or the whole instrument becomes useless.",
        "choices": ["align", "crumple", "chant", "perpetrate"],
        "answerIndex": 0,
        "translation": "技術者は2枚の大きな鏡を正確に一直線に合わせなければならず、さもないと装置全体が役に立たなくなる。",
    },
    {
        "stem": "Public opinion on the new tax proved (   ), shifting twice within a single month.",
        "choices": ["verbose", "belligerent", "interim", "fickle"],
        "answerIndex": 3,
        "translation": "その新税に対する世論は移り気で、1か月のうちに2度も方向を変えた。",
    },
    {
        "stem": "He is an (   ) collector who has bought a book almost every week since 1980.",
        "choices": ["inveterate", "euphoric", "efficacious", "reticent"],
        "answerIndex": 0,
        "translation": "彼は1980年以来ほぼ毎週本を買い続けている筋金入りの収集家である。",
    },
    {
        "stem": "The senator was unusually (   ) in his answers to reporters, choosing every word with care and promising nothing at all.",
        "choices": ["propitious", "circumspect", "delinquent", "insufferable"],
        "answerIndex": 1,
        "translation": "その上院議員は記者への答え方が異例なほど慎重で、一語一語を注意深く選び、何一つ約束しなかった。",
    },
    {
        "stem": "The old equipment is far too (   ) to be carried up the narrow staircase.",
        "choices": ["poignant", "morose", "harrowing", "cumbersome"],
        "answerIndex": 3,
        "translation": "その古い装置は扱いにくく大きすぎて、狭い階段を運び上げることはできない。",
    },
    {
        "stem": "The factory itself has been (   ) since 1998, though its tall brick chimney is still standing.",
        "choices": ["personable", "recurrent", "astute", "defunct"],
        "answerIndex": 3,
        "translation": "その工場自体は1998年以来操業していないが、高いれんがの煙突は今も立っている。",
    },
    {
        "stem": "An (   ) shot from the far side of the pitch broke a window in the clubhouse.",
        "choices": ["errant", "obtrusive", "affable", "abhorrent"],
        "answerIndex": 0,
        "translation": "ピッチの反対側からの狙いを外れた一撃が、クラブハウスの窓を割った。",
    },
    {
        "stem": "The old kitchen was restored so (   ) that visitors assume it was never altered.",
        "choices": ["enviably", "immortally", "diversely", "impeccably"],
        "answerIndex": 3,
        "translation": "その古い台所は非の打ちどころなく修復され、訪問者はまったく手を加えられていないと思い込む。",
    },
    {
        "stem": "The scale of the response (   ) organizers who had expected a few hundred replies.",
        "choices": ["bowled over", "knuckled down", "drifted off", "scooted over"],
        "answerIndex": 0,
        "translation": "反響の規模は、数百件の返信を見込んでいた主催者たちを圧倒した。",
    },
    {
        "stem": "The climbers (   ) in a stone hut for two days until the blizzard passed.",
        "choices": ["carved up", "clogged up", "holed up", "choked up"],
        "answerIndex": 2,
        "translation": "登山者たちは吹雪が過ぎるまで2日間、石造りの小屋にこもっていた。",
    },
    {
        "stem": "Months of small disagreements (   ) the resignation that surprised almost nobody inside the firm.",
        "choices": ["stepped down from", "led up to", "picked up after", "fended for"],
        "answerIndex": 1,
        "translation": "何か月にも及ぶ小さな不一致が、社内のほとんど誰も驚かせなかったあの辞任へとつながっていった。",
    },
    {
        "stem": "Support for the whole scheme gradually (   ) once the promised government funding simply failed to appear.",
        "choices": ["keeled over", "ebbed away", "ducked out", "stopped off"],
        "answerIndex": 1,
        "translation": "約束された政府の資金が現れないと、その計画全体への支持は次第に薄れていった。",
    },
]


DETAILS = {
    # Q1
    "debutante": ("社交界にデビューする女性", "名詞", "The photograph shows a debutante being presented at court in 1935.", "その写真は1935年に宮廷に紹介される社交界デビューの女性を写している。"),
    "concession": ("譲歩、営業権", "名詞", "The union accepted one concession on hours but none on pay.", "組合は労働時間について1つの譲歩は受け入れたが、賃金については受け入れなかった。"),
    "bombardment": ("砲撃、集中攻撃", "名詞", "The bombardment lasted three nights and destroyed the cathedral roof.", "その砲撃は3晩続き、大聖堂の屋根を破壊した。"),
    "altercation": ("口論、いさかい", "名詞", "A brief altercation at the counter delayed everyone in the queue.", "カウンターでの短い口論が列の全員を待たせた。"),
    # Q2
    "harbinger": ("前触れ、先駆け", "名詞", "Falling orders were a harbinger of the difficulties that followed.", "受注の落ち込みは、その後の困難の前触れだった。"),
    "poise": ("落ち着き、物腰", "名詞", "She answered every question from the floor with remarkable poise.", "彼女は会場からのどの質問にも驚くべき落ち着きで答えた。"),
    "decorum": ("礼儀正しさ、品位", "名詞", "The court insists on a level of decorum that surprises first-time visitors.", "その法廷は初めて訪れる人が驚くほどの品位を求める。"),
    "insinuation": ("当てこすり、ほのめかし", "名詞", "He objected to the insinuation that he had known all along.", "彼は自分がずっと知っていたというほのめかしに異議を唱えた。"),
    # Q3
    "bundle": ("束、包み", "名詞", "A bundle of old letters was found behind the chimney breast.", "古い手紙の束が煙突の張り出しの裏から見つかった。"),
    "embargo": ("禁輸措置", "名詞", "The embargo on spare parts kept the fleet grounded for months.", "部品の禁輸措置により、その航空機群は何か月も飛べなかった。"),
    "reconnaissance": ("偵察", "名詞", "Aerial reconnaissance located the missing vessel within two hours.", "航空偵察は2時間以内に行方不明の船を発見した。"),
    "havoc": ("大混乱、大損害", "名詞", "The storm caused havoc on the roads throughout the county.", "その嵐は郡中の道路に大混乱をもたらした。"),
    # Q4
    "debris": ("破片、瓦礫", "名詞", "Crews cleared debris from the runway before the first flight.", "作業班は最初の便の前に滑走路から破片を取り除いた。"),
    "pleasantry": ("社交辞令、軽い冗談", "名詞", "They exchanged a pleasantry or two and returned to business.", "彼らは社交辞令を1つ2つ交わして、仕事に戻った。"),
    "virulence": ("毒性の強さ、悪意", "名詞", "The virulence of the new strain alarmed public health officials.", "新しい株の毒性の強さは公衆衛生当局を警戒させた。"),
    "demarcation": ("境界設定、区分", "名詞", "The treaty settled the demarcation of the border in 1912.", "その条約は1912年に国境の画定を決着させた。"),
    # Q5
    "coercion": ("強制、威圧", "名詞", "The confession was excluded because of clear coercion.", "その自白は明白な強要があったため証拠から除外された。"),
    "respite": ("小休止、猶予", "名詞", "The rain gave firefighters a brief respite on the second night.", "雨は2晩目に消防士たちにつかの間の休息を与えた。"),
    "inertia": ("惰性、不活発", "名詞", "Institutional inertia delayed the reform for another decade.", "組織の惰性がその改革をさらに10年遅らせた。"),
    "affront": ("侮辱", "名詞", "The remark was taken as an affront by the whole delegation.", "その発言は代表団全体から侮辱と受け取られた。"),
    # Q6
    "severity": ("厳しさ、深刻さ", "名詞", "The severity of the winter surprised even the older residents.", "その冬の厳しさは年配の住民さえ驚かせた。"),
    "oration": ("演説", "名詞", "His funeral oration lasted barely four minutes but moved everyone.", "彼の葬儀での弔辞は4分足らずだったが、全員を感動させた。"),
    "eviction": ("立ち退き、追い出し", "名詞", "The eviction notice gave the tenants twenty-eight days.", "その立ち退き通知は借家人に28日の猶予を与えた。"),
    "regression": ("後退、退行", "名詞", "Doctors observed a regression in the patient's speech after the fever.", "医師たちは発熱の後、患者の発話に後退が見られると観察した。"),
    # Q7
    "emblem": ("象徴、記章", "名詞", "The oak leaf is the emblem of the mountain rescue service.", "カシの葉はその山岳救助隊の記章である。"),
    "felicity": ("この上ない幸福、巧みさ", "名詞", "The letter is written with a felicity rare in official prose.", "その手紙は公文書にはまれな巧みさで書かれている。"),
    "serendipity": ("偶然の幸運な発見", "名詞", "Much of early chemistry advanced through simple serendipity.", "初期の化学の多くは単なる幸運な偶然によって進歩した。"),
    "conveyance": ("運搬、乗り物", "名詞", "The museum displays a horse-drawn conveyance from the 1880s.", "その博物館は1880年代の馬車を展示している。"),
    # Q8
    "avail": ("役立つ、利用する", "動詞", "Complaining now will not avail you anything at this very late stage.", "この期に及んで今さら苦情を言っても何の役にも立たないだろう。"),
    "imbue": ("(感情や性質を)吹き込む", "動詞", "Good teachers imbue their students with genuine curiosity.", "よい教師は生徒に本物の好奇心を吹き込む。"),
    "foment": ("(不和などを)助長する、扇動する", "動詞", "Agents were sent to foment unrest in the border provinces.", "工作員が国境の州で騒乱を扇動するために送り込まれた。"),
    "pilfer": ("こそ泥をする、くすねる", "動詞", "Staff were dismissed for continuing to pilfer stock from the warehouse.", "職員たちは倉庫から在庫をくすね続けたため解雇された。"),
    # Q9
    "admonished": ("戒めた、忠告した", "動詞", "The referee admonished both captains before the match restarted.", "主審は試合再開の前に両チームの主将を戒めた。"),
    "marred": ("台無しにした、傷つけた", "動詞", "Heavy rain marred an otherwise excellent opening ceremony.", "豪雨が、それ以外は見事だった開会式を台無しにした。"),
    "appended": ("付け加えた、添付した", "動詞", "The clerk appended a note explaining the missing signature.", "書記は署名がない理由を説明する注記を付け加えた。"),
    "propelled": ("推進した、駆り立てた", "動詞", "A strong tail wind propelled the boat across the channel.", "強い追い風がその船を海峡の向こうへ押し進めた。"),
    # Q10
    "spanned": ("(期間や距離に)及んだ、架け渡した", "動詞", "His career spanned five decades and three continents.", "彼の経歴は50年と3つの大陸に及んだ。"),
    "deposed": ("退位させた、証言した", "動詞", "The council deposed the abbot after a long inquiry.", "評議会は長い調査の後、修道院長を解任した。"),
    "stifled": ("抑えた、息苦しくさせた", "動詞", "She stifled a yawn during the second hour of the lecture.", "彼女は講義の2時間目にあくびをかみ殺した。"),
    "berated": ("厳しく叱った", "動詞", "The foreman berated the driver in front of the whole yard.", "現場監督は作業場全員の前でその運転手を厳しく叱った。"),
    # Q11
    "regaled": ("(話などで)楽しませた", "動詞", "He regaled the table with stories about his years at sea.", "彼は海で過ごした年月の話でテーブルの一同を楽しませた。"),
    "droned": ("単調に話した、ぶんぶんうなった", "動詞", "The speaker droned for an hour about procedural changes.", "その話し手は手続きの変更について1時間、単調に話し続けた。"),
    "decimated": ("激減させた、壊滅させた", "動詞", "Disease decimated the elm trees along every road in the county.", "病害が郡内のあらゆる道路沿いのニレの木を激減させた。"),
    "consecrated": ("聖別した、奉献した", "動詞", "The bishop consecrated the new chapel on a wet October morning.", "司教は雨の10月の朝に新しい礼拝堂を聖別した。"),
    # Q12
    "faltered": ("ためらった、揺らいだ", "動詞", "His confidence faltered when the second machine also failed.", "2台目の機械も故障すると、彼の自信は揺らいだ。"),
    "goaded": ("駆り立てた、けしかけた", "動詞", "Constant criticism goaded him into resigning from the board.", "絶え間ない批判が彼を理事辞任へと駆り立てた。"),
    "incriminated": ("罪を負わせた、有罪を示した", "動詞", "The recording incriminated two officials who had denied everything.", "その録音は、すべてを否定していた2人の職員の関与を示した。"),
    "detested": ("ひどく嫌った", "動詞", "He detested long meetings and kept every one under thirty minutes.", "彼は長い会議をひどく嫌い、どの会議も30分以内に収めた。"),
    # Q13
    "blurred": ("ぼやけさせた、あいまいにした", "動詞", "Steam blurred the lens and ruined most of the photographs.", "湯気がレンズをぼやけさせ、写真のほとんどを台無しにした。"),
    "barricaded": ("バリケードでふさいだ", "動詞", "Protesters barricaded the entrance with chairs and desks.", "抗議者たちは椅子と机で入り口をふさいだ。"),
    "capitulated": ("降伏した、屈した", "動詞", "The company capitulated and withdrew the advertisement completely.", "その会社は屈服し、その広告を完全に取り下げた。"),
    "alienated": ("疎外した、遠ざけた", "動詞", "The new rules alienated the volunteers the club depended on.", "新しい規則は、そのクラブが頼りにしていたボランティアを遠ざけた。"),
    # Q14
    "align": ("一直線にする、足並みをそろえる", "動詞", "Engineers must align the rails to within a millimeter.", "技術者はレールを1ミリ以内の精度で一直線にしなければならない。"),
    "crumple": ("くしゃくしゃにする、崩れる", "動詞", "He would crumple each draft and throw it toward the bin.", "彼は原稿を1枚ずつくしゃくしゃにしてはごみ箱へ投げていた。"),
    "chant": ("唱える、詠唱する", "動詞", "The monks chant for an hour before the first meal.", "修道士たちは最初の食事の前に1時間詠唱する。"),
    "perpetrate": ("(悪事を)働く、犯す", "動詞", "Only an insider could perpetrate a fraud of that size undetected.", "その規模の詐欺を気づかれずに働けるのは内部の人間だけだろう。"),
    # Q15
    "verbose": ("冗長な、言葉数の多い", "形容詞", "The contract is verbose and could easily be half its length.", "その契約書は冗長で、簡単に半分の長さにできるだろう。"),
    "belligerent": ("好戦的な、けんか腰の", "形容詞", "A belligerent tone made the negotiation harder than it needed to be.", "けんか腰の口調が、必要以上に交渉を難しくした。"),
    "interim": ("暫定の、仮の", "形容詞", "An interim director was appointed while the search continued.", "後任探しが続く間、暫定の所長が任命された。"),
    "fickle": ("移り気な、気まぐれな", "形容詞", "The weather here is fickle even by coastal standards.", "ここの天気は沿岸部の基準から見ても気まぐれである。"),
    # Q16
    "inveterate": ("常習的な、根深い", "形容詞", "An inveterate note-taker, he filled four notebooks a year.", "常習的なメモ魔である彼は、年に4冊のノートを埋めた。"),
    "euphoric": ("非常に高揚した", "形容詞", "The squad was euphoric after the late equalizing goal.", "その選手団は終盤の同点ゴールの後、大いに沸き立った。"),
    "efficacious": ("効き目のある", "形容詞", "The treatment proved efficacious in eight of the ten trials.", "その治療法は10回の試験のうち8回で効果があると分かった。"),
    "reticent": ("寡黙な、控えめな", "形容詞", "He remained reticent about his role in the negotiations.", "彼はその交渉での自分の役割について口を閉ざしたままだった。"),
    # Q17
    "propitious": ("好都合な、幸先のよい", "形容詞", "The calm weather was propitious for the launch scheduled that evening.", "穏やかな天候はその晩に予定された打ち上げにとって好都合だった。"),
    "circumspect": ("慎重な、用心深い", "形容詞", "Auditors are trained to be circumspect about verbal assurances.", "監査人は口頭の保証について慎重であるよう訓練されている。"),
    "delinquent": ("滞納している、非行の", "形容詞", "The account has been delinquent for more than ninety days.", "その口座は90日以上支払いが滞っている。"),
    "insufferable": ("我慢できない、鼻持ちならない", "形容詞", "His insufferable boasting emptied the room within half an hour.", "彼の鼻持ちならない自慢話は30分で部屋を空にした。"),
    # Q18
    "poignant": ("胸を打つ、痛切な", "形容詞", "The letter contains a poignant description of the last winter.", "その手紙には最後の冬についての胸を打つ描写が含まれている。"),
    "morose": ("むっつりした、不機嫌な", "形容詞", "He grew morose whenever the subject of the sale came up.", "売却の話題が出るたびに彼はむっつりと不機嫌になった。"),
    "harrowing": ("痛ましい、悲惨な", "形容詞", "Survivors gave a harrowing account of the night in the tunnel.", "生存者たちはトンネルでの一夜について痛ましい証言をした。"),
    "cumbersome": ("扱いにくい、煩雑な", "形容詞", "The application process is cumbersome and takes eleven separate forms.", "その申請手続きは煩雑で、11種類の書式を必要とする。"),
    # Q19
    "personable": ("感じのよい、人好きのする", "形容詞", "A personable guide made the long tour pass quickly.", "感じのよい案内人のおかげで長い見学もあっという間に過ぎた。"),
    "recurrent": ("再発する、繰り返し起こる", "形容詞", "Flooding in this valley is recurrent rather than exceptional.", "この谷での洪水は例外的というより繰り返し起こるものである。"),
    "astute": ("抜け目のない、鋭敏な", "形容詞", "An astute reader will notice the change of narrator.", "鋭い読者は語り手が変わっていることに気づくだろう。"),
    "defunct": ("機能しなくなった、廃止された", "形容詞", "The society has been defunct since its final meeting in 2004.", "その協会は2004年の最後の会合以来、活動を停止している。"),
    # Q20
    "errant": ("狙いを外れた、常道を外れた", "形容詞", "An errant shopping trolley scratched the side of the car.", "転がっていったショッピングカートが車の側面を傷つけた。"),
    "obtrusive": ("目障りな、出しゃばりな", "形容詞", "The new lighting is bright without being obtrusive.", "新しい照明は目障りにならずに明るい。"),
    "affable": ("愛想のよい、気さくな", "形容詞", "The affable landlord knew every regular customer by name.", "その気さくな主人は常連客全員の名前を知っていた。"),
    "abhorrent": ("忌まわしい、嫌悪すべき", "形容詞", "The practice is abhorrent to almost everyone who studies it.", "その慣行は、それを研究するほぼ誰にとっても忌まわしいものである。"),
    # Q21
    "enviably": ("うらやましいほどに", "副詞", "The team is enviably placed with four matches still to play.", "そのチームは残り4試合を残してうらやましいほどよい位置にいる。"),
    "immortally": ("不朽の形で、永遠に", "副詞", "The line is immortally associated with the actor who first spoke it.", "そのせりふは最初に口にした俳優と不朽の形で結びついている。"),
    "diversely": ("多様に、さまざまに", "副詞", "The committee is diversely composed by design rather than accident.", "その委員会は偶然ではなく意図的に多様な構成になっている。"),
    "impeccably": ("非の打ちどころなく", "副詞", "He was impeccably dressed even for the earliest rehearsal.", "彼は最も早い時間のリハーサルにさえ非の打ちどころのない身なりで来た。"),
    # Q22
    "bowled over": ("圧倒した、驚かせた", "句動詞", "The audience was bowled over by a performer nobody had heard of.", "聴衆は誰も知らなかった演者にすっかり圧倒された。"),
    "knuckled down": ("本腰を入れて取り組んだ", "句動詞", "She knuckled down in February and finished the thesis by June.", "彼女は2月に本腰を入れ、6月までに論文を仕上げた。"),
    "drifted off": ("うとうとと眠りに落ちた", "句動詞", "He drifted off in the armchair before the film had ended.", "彼は映画が終わる前に肘掛け椅子でうとうとと眠りに落ちた。"),
    "scooted over": ("席を詰めた、横へ寄った", "句動詞", "The children scooted over to make room on the bench.", "子どもたちはベンチに場所を空けるため横へ詰めた。"),
    # Q23
    "carved up": ("分割した、切り分けた", "句動詞", "The estate was carved up between four distant relatives.", "その地所は4人の遠縁の親族の間で分割された。"),
    "clogged up": ("詰まらせた", "句動詞", "Fallen leaves clogged up the gutters along the whole terrace.", "落ち葉がその一続きの家並みの雨どいを詰まらせた。"),
    "holed up": ("こもった、身を潜めた", "句動詞", "The writer holed up in a cottage for the whole of January.", "その作家は1月中ずっと小屋にこもっていた。"),
    "choked up": ("感極まって声が詰まった", "句動詞", "He got choked up while reading his brother's old letter aloud.", "彼は兄の古い手紙を読み上げながら、感極まって声を詰まらせた。"),
    # Q24
    "stepped down from": ("(職を)辞した", "句動詞", "She stepped down from the board after nineteen years of service.", "彼女は19年間の在任の後、理事会を退いた。"),
    "led up to": ("(~へ)つながっていった", "句動詞", "The events that led up to the closure are still disputed.", "閉鎖に至る出来事については今も見解が分かれている。"),
    "picked up after": ("(~の)後片付けをした", "句動詞", "He picked up after the whole crew in the shared kitchen every single evening.", "彼は毎晩、共用の台所で作業員全員の後片付けをしていた。"),
    "fended for": ("(自力で)やりくりした", "句動詞", "The older children fended for themselves during the harvest.", "年上の子どもたちは収穫期の間、自分たちで何とかやりくりした。"),
    # Q25
    "keeled over": ("倒れた、転覆した", "句動詞", "One of the marchers keeled over in the afternoon heat.", "行進していた1人が午後の暑さで倒れた。"),
    "ebbed away": ("次第に衰えた、引いていった", "句動詞", "His strength ebbed away steadily over the final fortnight.", "彼の体力は最後の2週間で着実に衰えていった。"),
    "ducked out": ("こっそり抜け出した、逃れた", "句動詞", "Two guests ducked out before the speeches even began.", "2人の客は演説が始まる前にこっそり抜け出した。"),
    "stopped off": ("途中で立ち寄った", "句動詞", "They stopped off at a bakery on the way to the station.", "彼らは駅へ向かう途中でパン屋に立ち寄った。"),
}


CORE_IMAGES = {
    "bowled over": {
        "chain": [
            {"term": "bowl", "gloss": "ボールを転がす"},
            {"term": "over", "gloss": "倒れるほど越えて"},
            {"gloss": "勢いよく当たって相手を倒して"},
            {"gloss": "圧倒する、驚かせる"},
        ],
        "particle": "over",
    },
    "knuckled down": {
        "chain": [
            {"term": "knuckle", "gloss": "こぶしを地につける"},
            {"term": "down", "gloss": "腰を据えて"},
            {"gloss": "こぶしをつけるほど身を低くして構えて"},
            {"gloss": "本腰を入れて取り組む"},
        ],
        "particle": "down",
        "particleSense": "settle",
    },
    "drifted off": {
        "chain": [
            {"term": "drift", "gloss": "漂う"},
            {"term": "off", "gloss": "意識が離れて薄れて"},
            {"gloss": "意識が漂うように離れて薄れて"},
            {"gloss": "うとうとと眠りに落ちる"},
        ],
        "particle": "off",
        "particleSense": "weaken",
    },
    "scooted over": {
        "chain": [
            {"term": "scoot", "gloss": "さっと動く"},
            {"term": "over", "gloss": "横へ移って"},
            {"gloss": "座ったまま横へさっと移って"},
            {"gloss": "席を詰める"},
        ],
        "particle": "over",
    },
    "carved up": {
        "chain": [
            {"term": "carve", "gloss": "切り分ける"},
            {"term": "up", "gloss": "残らず分け切って"},
            {"gloss": "一つの塊を残らず切り分けて"},
            {"gloss": "分割する"},
        ],
        "particle": "up",
        "particleSense": "complete",
    },
    "clogged up": {
        "chain": [
            {"term": "clog", "gloss": "詰まらせる"},
            {"term": "up", "gloss": "内側をふさいで"},
            {"gloss": "管の内側をふさいで通れなくして"},
            {"gloss": "詰まらせる"},
        ],
        "particle": "up",
        "particleSense": "contain",
    },
    "holed up": {
        "chain": [
            {"term": "hole", "gloss": "穴に入る"},
            {"term": "up", "gloss": "内側へ閉じこもって"},
            {"gloss": "穴の中へ入って外へ出ずに"},
            {"gloss": "こもる、身を潜める"},
        ],
        "particle": "up",
        "particleSense": "contain",
    },
    "choked up": {
        "chain": [
            {"term": "choke", "gloss": "息を詰まらせる"},
            {"term": "up", "gloss": "内側にこみ上げて"},
            {"gloss": "感情がこみ上げて喉をふさいで"},
            {"gloss": "感極まって声が詰まる"},
        ],
        "particle": "up",
        "particleSense": "contain",
    },
    "stepped down from": {
        "chain": [
            {"term": "step", "gloss": "足を踏み出す"},
            {"term": "down", "gloss": "その地位から降りて"},
            {"gloss": "高い地位から一段降りて"},
            {"gloss": "職を辞する"},
        ],
        "particle": "down",
        "particleSense": "descend",
    },
    "led up to": {
        "chain": [
            {"term": "lead", "gloss": "導く"},
            {"term": "up", "gloss": "その時点へ近づいて"},
            {"gloss": "出来事が順に並んでその時点へ近づいて"},
            {"gloss": "~へつながっていく"},
        ],
        "particle": "up",
        "particleSense": "approach",
    },
    "picked up after": {
        "chain": [
            {"term": "pick", "gloss": "拾い上げる"},
            {"term": "up", "gloss": "きれいに片づくまで"},
            {"gloss": "散らかった物を拾い上げてきれいにして"},
            {"gloss": "~の後片付けをする"},
        ],
        "particle": "up",
        "particleSense": "complete",
    },
    "fended for": {
        "chain": [
            {"term": "fend", "gloss": "防ぐ、しのぐ"},
            {"term": "for", "gloss": "その相手のために"},
            {"gloss": "助けなしに自分の分を自分でしのいで"},
            {"gloss": "自力でやりくりする"},
        ],
    },
    "keeled over": {
        "chain": [
            {"term": "keel", "gloss": "船底を上に向ける"},
            {"term": "over", "gloss": "ひっくり返って"},
            {"gloss": "船が横倒しになるように倒れて"},
            {"gloss": "ばったり倒れる"},
        ],
        "particle": "over",
    },
    "ebbed away": {
        "chain": [
            {"term": "ebb", "gloss": "潮が引く"},
            {"term": "away", "gloss": "少しずつ去って"},
            {"gloss": "潮が引くように少しずつ去って"},
            {"gloss": "次第に衰える"},
        ],
        "particle": "away",
    },
    "ducked out": {
        "chain": [
            {"term": "duck", "gloss": "身をかがめる"},
            {"term": "out", "gloss": "外へ抜け出て"},
            {"gloss": "身をかがめて人目を避けながら外へ出て"},
            {"gloss": "こっそり抜け出す"},
        ],
        "particle": "out",
        "particleSense": "escape",
    },
    "stopped off": {
        "chain": [
            {"term": "stop", "gloss": "止まる"},
            {"term": "off", "gloss": "本筋の道から外れて"},
            {"gloss": "目的地への道から一度外れて止まって"},
            {"gloss": "途中で立ち寄る"},
        ],
        "particle": "off",
        "particleSense": "separate",
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
        raise ValueError("模試第17回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-17 割り当てに従う",
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
