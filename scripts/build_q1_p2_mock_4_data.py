"""準2級の自作模試第4回をQ1形式のJSONへ出力する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-4"


QUESTIONS = [
    {
        "stem": "The school placed the exam timetable on the (   ) near the main entrance, where every student could read it before class.",
        "choices": ["library", "board", "project", "supply"],
        "answerIndex": 1,
        "translation": "学校は試験の予定表を正面玄関近くの掲示板に貼り、授業前に全生徒が読めるようにした。",
    },
    {
        "stem": "A: Why did the doctor ask about the pain? B: She wanted to understand the (   ) before choosing the right treatment for the patient.",
        "choices": ["clinic", "medicine", "symptom", "exam"],
        "answerIndex": 2,
        "translation": "A：どうして医師は痛みについて尋ねたの？ B：患者に合う治療を選ぶ前に、その症状を理解したかったんだよ。",
    },
    {
        "stem": "Passengers should wait on the correct (   ) before boarding, because the train to the coast leaves from a different part of the station today.",
        "choices": ["captain", "driver", "ticket", "platform"],
        "answerIndex": 3,
        "translation": "乗客は乗車前に正しいホームで待つべきだ。今日は海岸行きの列車が駅の別の場所から出発するからだ。",
    },
    {
        "stem": "Following a major natural disaster, the insurance company sent an expert to measure the (   ) to houses along the coast.",
        "choices": ["damage", "flood", "garden", "weather"],
        "answerIndex": 0,
        "translation": "大きな自然災害の後、保険会社は海岸沿いの家屋への被害を測るため専門家を派遣した。",
    },
    {
        "stem": "A: Is this sports (   ) strong enough for the mountain trip? B: Yes, the club bought it last year and checks it after every use.",
        "choices": ["machine", "factory", "equipment", "worker"],
        "answerIndex": 2,
        "translation": "A：このスポーツ用品は山への旅行に十分な強度がある？ B：うん、クラブが去年買って、使うたびに点検しているよ。",
    },
    {
        "stem": "The small business had a very (   ) year, so it hired two more workers and opened a second shop.",
        "choices": ["careless", "quiet", "regular", "successful"],
        "answerIndex": 3,
        "translation": "その小さな会社にとって非常にうまくいった一年だったので、従業員を2人増やし、2軒目の店を開いた。",
    },
    {
        "stem": "A: Why is the fish so hard? B: It is still (   ), so please leave it in the refrigerator until tomorrow.",
        "choices": ["fresh", "frozen", "healthy", "simple"],
        "answerIndex": 1,
        "translation": "A：どうして魚がこんなに硬いの？ B：まだ凍っているから、明日まで冷蔵庫に入れておいて。",
    },
    {
        "stem": "The road closure is only (   ); workers expect to finish the bridge repairs before the holiday begins.",
        "choices": ["temporary", "valuable", "central", "public"],
        "answerIndex": 0,
        "translation": "道路の閉鎖は一時的なものにすぎない。作業員は休暇が始まる前に橋の修理を終える予定だ。",
    },
    {
        "stem": "A: When will the principal tell everyone about the new club? B: She will (   ) the plan at tomorrow's morning meeting.",
        "choices": ["avoid", "depend", "increase", "announce"],
        "answerIndex": 3,
        "translation": "A：校長はいつ新しいクラブについてみんなに知らせるの？ B：明日の朝の集会で計画を発表するよ。",
    },
    {
        "stem": "Before buying a laptop, compare the prices and (   ) the model that has enough memory for your schoolwork.",
        "choices": ["lend", "save", "choose", "forget"],
        "answerIndex": 2,
        "translation": "ノートパソコンを買う前に価格を比べ、学校の勉強に十分なメモリーがある機種を選びなさい。",
    },
    {
        "stem": "The committee decided to (   ) making the final decision until next Friday because two members were away from town.",
        "choices": ["hold off", "cut down on", "sort out", "take on"],
        "answerIndex": 0,
        "translation": "委員会は2人のメンバーが町を離れていたため、最終決定を次の金曜日まで延期することにした。",
    },
    {
        "stem": "A: Can you hear me in the online class? B: Not yet. Please (   ) the microphone so the teacher can hear you.",
        "choices": ["hang up", "turn on", "break down", "put down"],
        "answerIndex": 1,
        "translation": "A：オンライン授業で私の声が聞こえる？ B：まだ聞こえないよ。先生に声が聞こえるように、マイクの電源を入れてください。",
    },
    {
        "stem": "The artist left one corner of the painting blank (   ), because she wanted visitors to imagine their own ending for the story.",
        "choices": ["in the meantime", "at the moment", "for now", "on purpose"],
        "answerIndex": 3,
        "translation": "その画家は、来館者に物語の結末を自分で想像してほしかったので、絵の隅を一か所わざと塗らずに残した。",
    },
    {
        "stem": "A: Why did the hospital close the side entrance? B: It is under repair; (   ), visitors must use the main entrance.",
        "choices": ["in no way", "for this reason", "on the whole", "in the long run"],
        "answerIndex": 1,
        "translation": "A：どうして病院は側面の入口を閉めたの？ B：側面の入口が修理中だから、来訪者は建物に入るため正面玄関を使わなければならないんだ。",
    },
    {
        "stem": "The medicine was carefully provided (   ) small tablets, making it easy for young children to swallow.",
        "choices": ["in the form of", "in spite of", "due to", "at the time of"],
        "answerIndex": 0,
        "translation": "その薬は小さな錠剤の形で注意深く提供されたので、幼い子どもにも飲み込みやすかった。",
    },
]


DETAILS = {
    "library": ("図書館", "名詞", "The library opens early so students can study before their first class.", "図書館は生徒が1時間目の前に勉強できるよう早く開く。"),
    "board": ("掲示板、板", "名詞", "The board near the main office displays club information.", "職員室の近くにある掲示板には、クラブの情報が掲示されている。"),
    "project": ("計画、プロジェクト", "名詞", "Our science project requires careful planning and a short presentation.", "私たちの科学プロジェクトには慎重な計画と短い発表が必要だ。"),
    "supply": ("供給、備品", "名詞", "The teacher checked the supply cupboard before the art lesson.", "先生は美術の授業の前に備品棚を確認した。"),
    "clinic": ("診療所、クリニック", "名詞", "The village clinic offers basic medical advice on weekday mornings.", "村の診療所は平日の朝に基本的な医療相談を行う。"),
    "medicine": ("薬、医学", "名詞", "This medicine should be kept away from direct sunlight.", "この薬は直射日光を避けて保管すべきだ。"),
    "symptom": ("症状", "名詞", "A high fever can be a symptom of several common illnesses.", "高熱は、いくつかのよくある病気の症状である可能性がある。"),
    "exam": ("試験、検査", "名詞", "The doctor ordered an exam before choosing the right treatment.", "医師は適切な治療を選ぶ前に検査を指示した。"),
    "captain": ("船長、キャプテン", "名詞", "The captain welcomed every passenger before the ship left the port.", "船が港を出る前に、船長は乗客全員を歓迎した。"),
    "driver": ("運転手", "名詞", "The driver checked the bus carefully before leaving the station.", "運転手は駅を出発する前にバスを注意深く点検した。"),
    "ticket": ("切符、チケット", "名詞", "I bought a train ticket online and printed it at home.", "私はオンラインで列車の切符を買い、自宅で印刷した。"),
    "platform": ("プラットホーム、台", "名詞", "The train waited on platform three beside the quiet station.", "列車は静かな駅の3番ホームで待っていた。"),
    "garden": ("庭、公園", "名詞", "The children planted flowers in the garden behind the community center.", "子どもたちは公民館の裏の庭に花を植えた。"),
    "flood": ("洪水", "名詞", "The flood closed the road and damaged nearby farms.", "洪水で道路が閉鎖され、近くの農場が被害を受けた。"),
    "damage": ("損害、被害", "名詞", "The workers photographed the damage before repairing the roof.", "作業員たちは屋根を修理する前に被害を写真に撮った。"),
    "weather": ("天気、気象", "名詞", "The weather changed quickly after dark clouds covered the valley.", "暗い雲が谷を覆った後、天気は急に変わった。"),
    "equipment": ("設備、用具", "名詞", "The sports club stores its equipment in a locked room.", "そのスポーツクラブは用具を鍵のかかる部屋に保管している。"),
    "machine": ("機械", "名詞", "The new machine saves time by sorting small packages.", "その新しい機械は小包を仕分けして時間を節約する。"),
    "factory": ("工場", "名詞", "The factory employs local workers and recycles its water.", "その工場は地元の作業員を雇い、水を再利用している。"),
    "worker": ("作業員、労働者", "名詞", "Every worker received a helmet before entering the building.", "作業員は全員、建物に入る前にヘルメットを受け取った。"),
    "successful": ("成功した、うまくいった", "形容詞", "The successful event attracted more visitors than the organizers expected.", "成功した催しには主催者の予想より多くの来訪者が集まった。"),
    "careless": ("不注意な", "形容詞", "A careless mistake caused the team to lose valuable time.", "不注意なミスでチームは貴重な時間を失った。"),
    "quiet": ("静かな", "形容詞", "The quiet room is available for students during lunch.", "その静かな部屋は昼食時に生徒が利用できる。"),
    "regular": ("規則的な、通常の", "形容詞", "Regular exercise helps many people sleep better at night.", "規則的な運動は多くの人が夜によく眠る助けになる。"),
    "fresh": ("新鮮な", "形容詞", "We bought fresh bread from the bakery near the station.", "私たちは駅の近くのパン屋で焼きたてのパンを買った。"),
    "frozen": ("凍った、冷凍の", "形容詞", "The frozen vegetables can be cooked quickly in a pan.", "冷凍野菜はフライパンですぐに調理できる。"),
    "healthy": ("健康な、健康によい", "形容詞", "A healthy breakfast gives children energy for a busy morning.", "健康的な朝食は忙しい朝を過ごす子どもたちに活力を与える。"),
    "simple": ("簡単な、単純な", "形容詞", "This simple recipe is easy for beginners to follow.", "この簡単なレシピは初心者にも実行しやすい。"),
    "valuable": ("価値のある、貴重な", "形容詞", "The museum protects valuable paintings with special glass.", "博物館は特別なガラスで貴重な絵画を守っている。"),
    "central": ("中心の、中央の", "形容詞", "The central station connects the town with several villages.", "中央駅は町といくつもの村を結んでいる。"),
    "public": ("公共の、公の", "形容詞", "The public garden closes its gates after sunset.", "その公共庭園は日没後に門を閉める。"),
    "temporary": ("一時的な", "形容詞", "The temporary office will close when the main building reopens.", "本館が再開すると、一時的な事務所は閉鎖される。"),
    "announce": ("発表する、知らせる", "動詞", "The principal will announce the competition results after lunch.", "校長は昼食後にコンテストの結果を発表する。"),
    "avoid": ("避ける", "動詞", "Please avoid the wet floor near the entrance.", "入口近くの濡れた床を避けてください。"),
    "depend": ("頼る、次第である", "動詞", "Small shops often depend on local customers during winter.", "小さな店は冬の間、地元の客に頼ることが多い。"),
    "increase": ("増やす、増加する", "動詞", "The city plans to increase bus services during the festival.", "市は祭りの間、バスの運行本数を増やす計画だ。"),
    "forget": ("忘れる", "動詞", "Do not forget the appointment when you check your calendar tonight.", "今夜カレンダーを確認するとき、約束を忘れないでください。"),
    "choose": ("選ぶ", "動詞", "You can choose a seat near the window if it is free.", "空いていれば窓の近くの席を選べます。"),
    "lend": ("貸す", "動詞", "Could you lend me your umbrella until the rain stops?", "雨がやむまであなたの傘を貸してくれませんか。"),
    "save": ("蓄える、節約する、救う", "動詞", "We should save enough money for the school trip.", "私たちは校外学習のために十分なお金を貯めるべきだ。"),
    "hold off": ("延期する、引き止める", "句動詞", "The committee decided to hold off making the final decision until Friday because two members were away.", "委員会は2人のメンバーが不在だったため、最終決定を金曜日まで延期することにした。"),
    "cut down on": ("〜を減らす", "句動詞", "The school wants students to cut down on plastic bottles during the summer.", "学校は夏の間、生徒たちにペットボトルを減らしてほしいと考えている。"),
    "sort out": ("〜を整理する、解決する", "句動詞", "The staff met to sort out the seating problem before the event.", "職員たちは行事の前に座席の問題を解決するため集まった。"),
    "take on": ("〜を引き受ける", "句動詞", "Mika decided to take on a new role in the school festival committee.", "ミカは学校祭の委員会で新しい役割を引き受けることにした。"),
    "hang up": ("電話を切る", "句動詞", "Please hang up the phone after you leave your message.", "メッセージを残したら、電話を切ってください。"),
    "turn on": ("〜の電源を入れる", "句動詞", "Please turn on the microphone before the online class begins.", "オンライン授業が始まる前にマイクの電源を入れてください。"),
    "break down": ("〜を分解する、故障する", "句動詞", "The mechanic had to break down the old machine before moving it.", "整備士は古い機械を運ぶ前に分解しなければならなかった。"),
    "put down": ("〜を置く、書き留める", "句動詞", "Please put down your bag before you sit beside the emergency exit.", "非常口のそばに座る前に、かばんを置いてください。"),
    "in the meantime": ("その間に、それまでは", "副詞句", "The repairs may take two days; in the meantime, visitors should use another entrance.", "修理には2日かかるかもしれない。その間、来訪者は別の入口を使うべきだ。"),
    "at the moment": ("今、現在", "副詞句", "The manager is busy at the moment, so please leave a message.", "マネージャーは今忙しいので、伝言を残してください。"),
    "for now": ("今のところ、当面は", "副詞句", "We will use this smaller room for now while the hall is repaired.", "ホールを修理している間、当面はこの小さな部屋を使う。"),
    "on purpose": ("わざと、故意に", "副詞句", "He did not break the window on purpose; the ball slipped from his hands.", "彼はわざと窓を割ったのではない。ボールが手から滑ったのだ。"),
    "in no way": ("決して〜ない、少しも〜ない", "副詞句", "The long journey was in no way a waste of time for the students.", "その長旅は生徒たちにとって決して時間の無駄ではなかった。"),
    "for this reason": ("この理由で、そのため", "副詞句", "The bridge is unsafe; for this reason, everyone must use the bus.", "その橋は危険だ。このため、全員がバスを使わなければならない。"),
    "on the whole": ("全体として、概して", "副詞句", "On the whole, the new timetable works well for our class.", "全体として、新しい時刻表は私たちのクラスにとってうまくいっている。"),
    "in the long run": ("長い目で見れば、結局は", "副詞句", "In the long run, regular practice will make this difficult skill easier to learn.", "長い目で見れば、定期的な練習によってこの難しい技能も学びやすくなる。"),
    "in the form of": ("〜の形で、〜という形で", "前置詞句", "The medicine is available in the form of small tablets.", "その薬は小さな錠剤の形で入手できる。"),
    "in spite of": ("〜にもかかわらず", "前置詞句", "In spite of the heavy rain, the outdoor market remained open.", "大雨にもかかわらず、屋外市場は開いたままだった。"),
    "due to": ("〜が原因で、〜のために", "前置詞句", "The match was canceled due to heavy rain near the stadium.", "競技場の近くの大雨が原因で、試合は中止された。"),
    "at the time of": ("〜の時に、〜の際に", "前置詞句", "At the time of the festival, the town streets are closed to cars.", "祭りの時には、町の通りは車両通行止めになる。"),
}


ETYMOLOGY = {
    "library": "ラテン語 liber「本」から。書物を集める場所。",
    "board": "古英語 bord「板」。知らせや予定を貼る板。",
    "project": "ラテン語 proicere「前へ投げる」。前へ進める計画。",
    "supply": "ラテン語 supplere「満たす」。必要な物を満たして与えること。",
    "clinic": "ギリシャ語 kline「ベッド」。病床のそばで行う診療所。",
    "medicine": "ラテン語 mederi「治す」。病気を治す薬や学問。",
    "symptom": "ギリシャ語 syn「共に」+ piptein「落ちる」。病気と共に現れる兆候。",
    "exam": "ラテン語 examinare「調べる」。状態を詳しく調べる検査や試験。",
    "captain": "ラテン語 caput「頭」。集団の頭に立つ人。",
    "driver": "drive（運転する）+ -er。乗り物を運転する人。",
    "ticket": "フランス語 etiquette「札、ラベル」。入場や乗車を示す札。",
    "platform": "フランス語 plateforme「平らな場所」。列車が止まる台や舞台。",
    "garden": "古フランス語 jardin「囲われた場所」。花や植物を育てる場所。",
    "flood": "古英語 flod「流れ」。水があふれて広がること。",
    "damage": "ラテン語 damnificare「損失を与える」。壊れた状態や損害。",
    "weather": "古英語 weder「空気、天候」。空の状態。",
    "equipment": "フランス語 équiper「装備する」。目的のために備えた道具。",
    "machine": "ギリシャ語 mēkhanē「仕掛け、機械」。仕事をする仕組み。",
    "factory": "ラテン語 facere「作る」。物を作る場所。",
    "worker": "work（働く）+ -er。働く人。",
    "successful": "success（成功）+ -ful。望んだ結果を得た状態。",
    "careless": "care（注意、世話）+ -less（ない）。注意を欠く。",
    "quiet": "ラテン語 quietus「休んだ、静かな」。音や動きが少ない。",
    "regular": "ラテン語 regula「定規、規則」。規則に沿っている。",
    "fresh": "古英語 fersc「新しい、塩気のない」。新しく清らかな。",
    "frozen": "freeze（凍る）の過去分詞。古英語 freosan から。",
    "healthy": "health（健康）+ -y。健康に関する、健康な。",
    "simple": "ラテン語 simplex「一つに折れた」。複雑に分かれていない。",
    "valuable": "value（価値）+ -able。価値を持つ。",
    "central": "ラテン語 centrum「中心点」。中心にある。",
    "public": "ラテン語 publicus「人々の」。個人ではなく皆のもの。",
    "temporary": "ラテン語 tempus「時間」。限られた期間だけの。",
    "announce": "ラテン語 ad-（〜へ）+ nuntiare（知らせる）。公に知らせる。",
    "avoid": "ラテン語 ab-（離れて）+ via（道）。道を外れて避ける。",
    "depend": "ラテン語 de-（下に）+ pendere（ぶら下がる）。何かにぶら下がって頼る。",
    "increase": "ラテン語 in-（上へ）+ crescere（成長する）。量や程度が増える。",
    "forget": "古英語 forgietan「失念する」。心から離れて覚えていない。",
    "choose": "古英語 ceosan「選ぶ」。複数から一つを取る。",
    "lend": "古英語 lænan「貸す」。一時的に使わせる。",
    "save": "ラテン語 salvare「安全にする」。危険から守る、蓄える。",
    "hold off": "hold（保つ）+ off（離して）。予定を手元から離して「延期する」。",
    "cut down on": "cut（切る）+ down（下げて）+ on（対象に）。対象への量を下げて「減らす」。",
    "sort out": "sort（分類する）+ out（外へ）。混乱から取り出して「整理・解決する」。",
    "take on": "take（取る）+ on（対象に向けて）。役割を引き受けて身に付ける。",
    "hang up": "hang（受話器を掛ける）+ up（終わりまで）。受話器を掛けて通話を終える。",
    "turn on": "turn（向きを変える）+ on（対象へ作用させて）。機器へ作用させて「電源を入れる」。",
    "break down": "break（壊す）+ down（下へ分けて）。機械を分けて「分解する」。",
    "put down": "put（置く）+ down（下へ）。物を下へ置く。",
    "in the meantime": "mean（中間）+ time（時間）。二つの時点の間に。",
    "at the moment": "moment（瞬間、現在の時点）を基準にする at。",
    "for now": "now（今）を期間の目安にする for。今のところ。",
    "on purpose": "purpose（意図、目的）に沿って on。意図的に。",
    "in no way": "way（方法、程度）のどの道にも in no。決して〜ない。",
    "for this reason": "reason（理由）を原因として for。この理由で。",
    "on the whole": "whole（全体）を見渡す on。全体として。",
    "in the long run": "long（長い）+ run（進行）。長い時間の流れ全体で見れば。",
    "in the form of": "form（形）の中に in。ある形や形式で現れることを示す。",
    "in spite of": "spite（悪意、反対する気持ち）にもかかわらず、という逆接を表す。",
    "due to": "due（当然支払われる、起因する）+ to（〜へ）。原因が〜に帰せられる。",
    "at the time of": "time（時）を基準にする at。ある時点や機会に。",
}


CORE_IMAGES = {
    "hold off": {"particle": "off", "particleSense": "pull-away", "siblings": [{"phrase": "pay off", "gloss": "金を渡して黙らせる"}, {"phrase": "call off", "gloss": "中止させる"}, {"phrase": "warn off", "gloss": "警告して手を引かせる"}], "chain": [{"term": "hold", "gloss": "保つ"}, {"term": "off", "gloss": "離して"}, {"gloss": "予定を延期して遠ざける"}]},
    "cut down on": {"particle": "down", "particleSense": "reduce", "siblings": [{"phrase": "slow down", "gloss": "速度を落とす"}, {"phrase": "cool down", "gloss": "冷ます"}, {"phrase": "tone down", "gloss": "調子をやわらげる"}], "chain": [{"term": "cut", "gloss": "切る"}, {"term": "down", "gloss": "下げて"}, {"gloss": "対象への量を減らす"}]},
    "sort out": {"particle": "out", "particleSense": "resolve", "siblings": [{"phrase": "figure out", "gloss": "理解して解決する"}, {"phrase": "iron out", "gloss": "問題を解消する"}, {"phrase": "straighten out", "gloss": "整理する"}], "chain": [{"term": "sort", "gloss": "分類する"}, {"term": "out", "gloss": "外へほどいて"}, {"gloss": "混乱を整理して解決する"}]},
    "take on": {"particle": "on", "particleSense": "contact", "chain": [{"term": "take", "gloss": "取る"}, {"term": "on", "gloss": "対象に向けて"}, {"gloss": "役割を引き受ける"}]},
    "hang up": {"particle": "up", "particleSense": "complete", "chain": [{"term": "hang", "gloss": "受話器を掛ける"}, {"term": "up", "gloss": "終わりまで"}, {"gloss": "受話器を掛けて通話を終える"}]},
    "turn on": {"particle": "on", "particleSense": "contact", "chain": [{"term": "turn", "gloss": "向きを変える"}, {"term": "on", "gloss": "対象へ作用させて"}, {"gloss": "機器の電源を入れる"}]},
    "break down": {"particle": "down", "particleSense": "reduce", "chain": [{"term": "break", "gloss": "壊す"}, {"term": "down", "gloss": "下へ分けて"}, {"gloss": "機械を分解する"}]},
    "put down": {"particle": "down", "particleSense": "descend", "chain": [{"term": "put", "gloss": "置く"}, {"term": "down", "gloss": "下へ"}, {"gloss": "物を下へ置く"}]},
    "in the meantime": {"chain": [{"term": "meantime", "gloss": "中間の時間"}, {"term": "in", "gloss": "その中で"}, {"gloss": "その間に、それまでは"}]},
    "at the moment": {"chain": [{"term": "moment", "gloss": "現在の時点"}, {"term": "at", "gloss": "その時点で"}, {"gloss": "今、現在"}]},
    "for now": {"chain": [{"term": "now", "gloss": "今"}, {"term": "for", "gloss": "その期間にわたって"}, {"gloss": "今のところ、当面は"}]},
    "on purpose": {"chain": [{"term": "purpose", "gloss": "意図、目的"}, {"term": "on", "gloss": "その意図に沿って"}, {"gloss": "わざと、故意に"}]},
    "in no way": {"chain": [{"term": "way", "gloss": "方法、程度"}, {"term": "in", "gloss": "その範囲の中で"}, {"gloss": "決して〜ない、少しも〜ない"}]},
    "for this reason": {"chain": [{"term": "reason", "gloss": "理由"}, {"term": "for", "gloss": "そのために"}, {"gloss": "この理由で、そのため"}]},
    "on the whole": {"chain": [{"term": "whole", "gloss": "全体"}, {"term": "on", "gloss": "その上に視点を置いて"}, {"gloss": "全体として、概して"}]},
    "in the long run": {"chain": [{"term": "long", "gloss": "長い"}, {"term": "run", "gloss": "時間の流れ"}, {"gloss": "長い目で見れば、結局は"}]},
    "in the form of": {"chain": [{"term": "form", "gloss": "形、形式"}, {"term": "of", "gloss": "〜として"}, {"gloss": "〜の形で、〜という形で"}]},
    "in spite of": {"chain": [{"term": "spite", "gloss": "反対する事情"}, {"term": "of", "gloss": "〜がある中で"}, {"gloss": "〜にもかかわらず"}]},
    "due to": {"chain": [{"term": "due", "gloss": "起因する"}, {"term": "to", "gloss": "〜へ"}, {"gloss": "〜が原因で"}]},
    "at the time of": {"chain": [{"term": "time", "gloss": "時"}, {"term": "of", "gloss": "〜の際に"}, {"gloss": "〜の時に"}]},
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 15:
        raise ValueError("準2級模試第4回は15問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 60 or len(choices) != len(set(choices)):
        raise ValueError("選択肢は重複しない60件である必要があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    missing_etymology = sorted(set(choices) - set(ETYMOLOGY))
    if missing_etymology:
        raise ValueError(f"語源情報がありません: {missing_etymology}")
    idioms = {choice for choice in choices if " " in choice}
    if idioms != set(CORE_IMAGES):
        raise ValueError(f"核心イメージの定義が一致しません: {sorted(idioms ^ set(CORE_IMAGES))}")
    if sum(bool(CORE_IMAGES[phrase].get("particle")) for phrase in idioms) < 4:
        raise ValueError("句動詞の核心イメージが4件未満です")

    meta = {
        "grade": "英検準2級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "AI生成（英検過去問の引用なし）・人手校閲",
        "counts": {"questions": 15, "words": 40, "idioms": 20, "total": 60},
    }
    question_data = {
        "meta": meta,
        "questions": [{"q": index, **question} for index, question in enumerate(QUESTIONS, start=1)],
    }
    words = []
    idiom_items = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            meaning, pos, example, example_translation = DETAILS[choice]
            item = {
                "q": q,
                "is_answer": index == question["answerIndex"],
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
                "pos": pos,
                "etymology": ETYMOLOGY[choice],
            }
            if " " in choice:
                item["type"] = "idiom"
                item["phrase"] = choice
                item["coreImage"] = CORE_IMAGES[choice]
                idiom_items.append(item)
            else:
                item["word"] = choice
                words.append(item)
    if (len(words), len(idiom_items)) != (40, 20):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idiom_items)}")
    return {"meta": meta, "words": words, "idioms": idiom_items}, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / "vocab_p2_mock-4.json", vocab)
    write_json(DATA_DIR / "questions_p2_mock-4.json", questions)
    print("p2 mock-4: 15 questions / 60 items (40 words, 20 idioms)")


if __name__ == "__main__":
    main()
