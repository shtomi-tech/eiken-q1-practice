"""英検2級 Chapter 3 模擬テスト第3回のデータを生成する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-3"


QUESTIONS = [
    {
        "stem": "John's parents (   ) him by calling him by his childhood nickname in front of others. They all laughed when they heard it.",
        "choices": ["embarrassed", "thanked", "surrendered", "cheered"],
        "answerIndex": 0,
        "translation": "ジョンの両親は、人前で彼を子どもの頃のあだ名で呼んで恥ずかしい思いをさせた。皆、そのあだ名を聞いて笑った。",
    },
    {
        "stem": "Alan is afraid of going to bed, as he has been having a lot of scary (   ) recently.",
        "choices": ["victims", "prayers", "visions", "nightmares"],
        "answerIndex": 3,
        "translation": "アランは最近怖い悪夢をたくさん見ているので、寝るのを怖がっている。",
    },
    {
        "stem": "Letters used to be the only (   ) of communication with friends and family who live far away, but now there are many different ways to communicate.",
        "choices": ["method", "expense", "cast", "species"],
        "answerIndex": 0,
        "translation": "遠くに住む友人や家族との唯一の通信手段は、かつては手紙だったが、今ではさまざまな連絡方法がある。",
    },
    {
        "stem": "When the police officer asked Sharon where she had been on the night of the accident, she became very nervous and answered (   ).",
        "choices": ["certainly", "thickly", "hesitantly", "jealously"],
        "answerIndex": 2,
        "translation": "警察官が事故の夜にどこにいたのかシャロンに尋ねると、彼女はとても緊張し、ためらいながら答えた。",
    },
    {
        "stem": "Mr. and Mrs. Yamada forgot to put the bananas in the fridge before going on a two-week trip. After returning home, they found that the bananas had (   ) and turned black.",
        "choices": ["piled", "spoiled", "bled", "beaten"],
        "answerIndex": 1,
        "translation": "山田夫妻は2週間の旅行に出る前、バナナを冷蔵庫に入れ忘れた。帰宅すると、バナナは腐って黒くなっていた。",
    },
    {
        "stem": "A: If you want to lose weight, you have to exercise more and (   ) the amount of calories in the food you eat. B: I understand. I'll do my best.",
        "choices": ["focus", "soak", "obey", "limit"],
        "answerIndex": 3,
        "translation": "A：体重を減らしたいなら、もっと運動して、食べ物に含まれるカロリーの量を制限しなければならない。B：分かりました。頑張ります。",
    },
    {
        "stem": "This new medical treatment is a discovery of great (   ) that will save many lives.",
        "choices": ["guarantee", "disorder", "significance", "architecture"],
        "answerIndex": 2,
        "translation": "この新しい医療法は、多くの命を救う大きな意義のある発見だ。",
    },
    {
        "stem": "A: The sky is so clear here in the country. The stars are (   )! B: I know. That's one reason I love coming out here.",
        "choices": ["eager", "incredible", "ungrateful", "political"],
        "answerIndex": 1,
        "translation": "A：この田舎では空がとても澄んでいる。星がすごいね。B：そうだね。ここへ来るのが好きな理由の一つだよ。",
    },
    {
        "stem": "Following the release of her new album, the singer was (   ) on the cover of a number of magazines all over the world.",
        "choices": ["urged", "featured", "appealed", "sighed"],
        "answerIndex": 1,
        "translation": "新しいアルバムの発売後、その歌手は世界中の多くの雑誌の表紙で特集された。",
    },
    {
        "stem": "Billy was very close to his grandmother, so he suffered a lot of (   ) after she passed away. It took him several weeks to recover.",
        "choices": ["grief", "trash", "courage", "fuel"],
        "answerIndex": 0,
        "translation": "ビリーは祖母ととても親しかったので、祖母が亡くなった後、大きな悲しみに苦しんだ。立ち直るのに数週間かかった。",
    },
    {
        "stem": "A: I want to quit my job. My boss is always finding (   ) with me. B: It might be better to find a job where you can be happy.",
        "choices": ["care", "problems", "detail", "approval"],
        "answerIndex": 1,
        "translation": "A：仕事を辞めたい。上司はいつも私のあら探しをしている。B：幸せになれる仕事を探した方がいいかもしれない。",
    },
    {
        "stem": "Josh liked to play video games instead of doing his homework. When he was older, though, he (   ) to understand that he needed to study harder.",
        "choices": ["opened", "related", "met", "came"],
        "answerIndex": 3,
        "translation": "ジョシュは宿題をする代わりにビデオゲームをするのが好きだった。しかし、年齢を重ねると、もっと一生懸命勉強する必要があると理解するようになった。",
    },
    {
        "stem": "A: I believe this topic is unsuitable for your report. (   ), you'll have to choose a new theme. B: OK. I'll start again from the beginning.",
        "choices": ["in that case", "in your favor", "for example", "at any time"],
        "answerIndex": 0,
        "translation": "A：このテーマはあなたのレポートには適さないと思います。その場合、新しいテーマを選ばなければなりません。B：分かりました。最初からやり直します。",
    },
    {
        "stem": "A: I'm really angry at Pam. I can't (   ) her behavior anymore. B: I understand how you feel. She needs to change.",
        "choices": ["look down on", "deal with", "get along with", "make up for"],
        "answerIndex": 1,
        "translation": "A：パムに本当に腹を立てています。もう彼女の行動には対処できません。B：気持ちは分かります。彼女は変わる必要があります。",
    },
    {
        "stem": "A: Hi, Sam. Are you still busy with your projects? B: Yes. In fact, I'm (   ) all day long.",
        "choices": ["out of stock", "on the go", "in sight", "under the circumstances"],
        "answerIndex": 1,
        "translation": "A：やあ、サム。まだプロジェクトで忙しいの？B：うん。実際、一日中動き回っているよ。",
    },
    {
        "stem": "A: I'm sorry I didn't come to class for the final test. I woke up late. B: You also didn't do any homework, so I have no (   ) but to fail you this semester.",
        "choices": ["choice", "chance", "kind", "field"],
        "answerIndex": 0,
        "translation": "A：期末試験のために授業へ行けなくてすみません。寝坊しました。B：宿題も全くしなかったので、今学期はあなたを落とすしかありません。",
    },
    {
        "stem": "A: Congratulations on the birth of your baby. What's his name? B: Charles. He's named (   ) his grandfather.",
        "choices": ["from", "near", "under", "in memory of"],
        "answerIndex": 3,
        "translation": "A：赤ちゃんの誕生おめでとう。名前は何？B：チャールズ。祖父を記念して名付けたんだ。",
    },
    {
        "stem": "The actor was happy to be given a part in the new movie Stormy Night. The movie was certain (   ) a big hit.",
        "choices": ["had become", "to become", "became", "become"],
        "answerIndex": 1,
        "translation": "その俳優は新作映画『Stormy Night』で役をもらえてうれしかった。その映画は大ヒットになることが確実だった。",
    },
    {
        "stem": "With Madeline (   ) me with the cleaning, we'll have the whole house clean within another two hours.",
        "choices": ["helping", "waiting", "sitting", "visiting"],
        "answerIndex": 0,
        "translation": "マデリンが掃除を手伝ってくれているので、あと2時間以内に家全体をきれいにできるだろう。",
    },
    {
        "stem": "Timmy was a little upset the first time his mother left him at school. (   ) he started to play with the other children, however, he was fine.",
        "choices": ["the time", "once", "ahead", "the next"],
        "answerIndex": 1,
        "translation": "ティミーは初めて母親に学校へ置いていかれたとき、少し動揺した。しかし、いったん他の子どもたちと遊び始めると大丈夫だった。",
    },
]


DETAILS = {
    "embarrassed": ("恥ずかしい思いをさせた", "動詞", "The sudden question embarrassed the student in front of the entire class.", "突然の質問はクラス全員の前でその生徒を恥ずかしい思いにさせた。"),
    "thanked": ("感謝した", "動詞", "The visitors thanked the guide after the long tour of the museum.", "訪問者たちは美術館の長い見学の後でガイドに感謝した。"),
    "surrendered": ("降伏した、引き渡した", "動詞", "The tired soldiers surrendered after their supplies ran out completely.", "疲れた兵士たちは物資が完全に尽きた後で降伏した。"),
    "cheered": ("声援を送った、元気づけた", "動詞", "The crowd cheered loudly when the home team scored first.", "地元チームが先制すると、観客は大声で声援を送った。"),
    "victims": ("犠牲者たち", "名詞", "The charity provides meals and blankets for earthquake victims each winter.", "その慈善団体は毎年冬に地震の犠牲者へ食事と毛布を提供する。"),
    "prayers": ("祈り", "名詞", "The family said prayers together before the important operation began.", "その家族は重要な手術が始まる前に一緒に祈りをささげた。"),
    "visions": ("幻、光景", "名詞", "The patient described strange visions after taking the strong medicine.", "その患者は強い薬を飲んだ後、奇妙な幻を描写した。"),
    "nightmares": ("悪夢", "名詞", "The child had nightmares after watching the frightening movie alone.", "その子どもは怖い映画を一人で見た後、悪夢を見た。"),
    "method": ("方法、手段", "名詞", "This method of communication is still useful during emergencies.", "この通信方法は緊急時にも役立つ。"),
    "expense": ("費用、出費", "名詞", "The unexpected expense forced the family to change its travel plans.", "予想外の出費のため、その家族は旅行計画を変更せざるを得なかった。"),
    "cast": ("配役、鋳型、投げること", "名詞", "The director announced the cast of the school play on Monday.", "監督は月曜日に学校劇の配役を発表した。"),
    "species": ("種、種類", "名詞", "Scientists discovered a new species of frog in the mountain forest.", "科学者たちは山の森でカエルの新種を発見した。"),
    "certainly": ("確かに、必ず", "副詞", "The new plan will certainly improve safety at the station.", "新しい計画は駅の安全を確実に改善するだろう。"),
    "thickly": ("厚く、濃く", "副詞", "The painter spread the blue color thickly across the wooden door.", "その画家は木製のドア全体に青い色を厚く塗った。"),
    "hesitantly": ("ためらいながら", "副詞", "The witness hesitantly answered the lawyer's difficult question.", "その証人は弁護士の難しい質問にためらいながら答えた。"),
    "jealously": ("嫉妬して", "副詞", "The young actor jealously watched his rival receive the award.", "その若い俳優はライバルが賞を受け取るのを嫉妬して見ていた。"),
    "piled": ("積み重なった、積み上げた", "動詞", "Snow piled high beside the road during the long winter storm.", "長い冬の嵐の間、道路のそばに雪が高く積もった。"),
    "spoiled": ("腐った、だめになった", "動詞", "The warm weather spoiled the fresh milk before breakfast the next day.", "暖かい天候のため、新鮮な牛乳は翌日の朝食前に腐った。"),
    "bled": ("出血した", "動詞", "The injured hiker bled until a rescue worker arrived at the camp.", "けがをしたハイカーは救助員がキャンプに着くまで出血した。"),
    "beaten": ("打ち負かされた、たたかれた", "動詞", "The beaten team promised to practice harder before the next match.", "負けたチームは次の試合までにもっと練習すると約束した。"),
    "focus": ("集中する、焦点を合わせる", "動詞", "The camera can focus on a small object from a distance.", "そのカメラは遠くから小さな物体に焦点を合わせられる。"),
    "soak": ("浸す、びしょぬれにする", "動詞", "Please soak the beans in water before cooking them tonight.", "今夜料理する前に豆を水に浸してください。"),
    "obey": ("従う", "動詞", "All passengers must obey the safety instructions during the flight.", "すべての乗客は飛行中、安全指示に従わなければならない。"),
    "limit": ("制限する", "動詞", "Parents sometimes limit the amount of television their children watch.", "親は子どもが見るテレビの量を制限することがある。"),
    "guarantee": ("保証", "名詞", "The store offers a one-year guarantee on every new appliance.", "その店はすべての新品家電に1年間の保証を付けている。"),
    "disorder": ("障害、無秩序", "名詞", "The doctor explained how the disorder affects the patient's sleep.", "医師はその障害が患者の睡眠にどう影響するか説明した。"),
    "significance": ("重要性、意義", "名詞", "The guide explained the historical significance of the old bridge.", "ガイドはその古い橋の歴史的重要性を説明した。"),
    "architecture": ("建築、建築様式", "名詞", "The students studied the architecture of the ancient temple carefully.", "生徒たちは古代寺院の建築を注意深く学んだ。"),
    "eager": ("熱望して、切望して", "形容詞", "The eager students arrived early to meet the visiting scientist.", "熱心な生徒たちは訪問した科学者に会うため早く到着した。"),
    "incredible": ("信じられない、すばらしい", "形容詞", "The team made an incredible recovery during the final minutes.", "そのチームは最後の数分間にすばらしい立て直しを見せた。"),
    "ungrateful": ("感謝を知らない", "形容詞", "It seemed ungrateful to complain about such a generous gift.", "そのように寛大な贈り物に不満を言うのは感謝知らずに思えた。"),
    "political": ("政治の、政治的な", "形容詞", "The newspaper avoided political topics in its weekend family section.", "その新聞は週末の家族向け欄では政治的な話題を避けた。"),
    "urged": ("強く促した", "動詞", "The doctor urged the patient to rest for several more days.", "医師は患者にあと数日休むよう強く促した。"),
    "featured": ("特集した、呼び物にした", "動詞", "The travel magazine featured a quiet island in its spring issue.", "その旅行雑誌は春号で静かな島を特集した。"),
    "appealed": ("訴えた、魅力があった", "動詞", "The colorful advertisement appealed to young customers in the city.", "その色鮮やかな広告は街の若い客の心をつかんだ。"),
    "sighed": ("ため息をついた", "動詞", "The exhausted worker sighed after finishing the long report.", "疲れた会社員は長い報告書を終えた後でため息をついた。"),
    "grief": ("深い悲しみ", "名詞", "The family shared its grief with close friends after the funeral.", "その家族は葬儀の後、親しい友人と深い悲しみを分かち合った。"),
    "trash": ("ごみ、くだらないもの", "名詞", "The volunteers collected trash from the beach before the festival.", "ボランティアは祭りの前に浜辺からごみを集めた。"),
    "courage": ("勇気", "名詞", "It took courage for the child to speak before the audience.", "その子どもが聴衆の前で話すには勇気が必要だった。"),
    "fuel": ("燃料、活力", "名詞", "The bus stopped because it did not have enough fuel.", "そのバスは十分な燃料がなかったので止まった。"),
    "care": ("世話、注意", "名詞", "The nurse took great care of the elderly patient overnight.", "看護師は一晩中、高齢の患者をとてもよく世話した。"),
    "problems": ("問題、困難", "名詞", "The manager kept finding problems with the new computer system.", "その管理者は新しいコンピューターシステムの問題を見つけ続けた。"),
    "detail": ("細部、詳細", "名詞", "The artist checked every detail of the portrait before displaying it.", "その画家は肖像画を展示する前に細部をすべて確認した。"),
    "approval": ("承認、賛成", "名詞", "The proposal received approval from the board after a careful review.", "その提案は慎重な審査の後、理事会の承認を受けた。"),
    "opened": ("開いた、始めた", "動詞", "The museum opened a new exhibit about local history last month.", "その博物館は先月、地域の歴史に関する新しい展示を始めた。"),
    "related": ("関係づけた、関連した", "動詞", "The speaker related the personal story to the larger social issue.", "講演者は個人的な話をより大きな社会問題と関連づけた。"),
    "met": ("会った、満たした", "動詞", "The small company met its sales goal earlier than expected.", "その小さな会社は予想より早く売上目標を達成した。"),
    "came": ("来た、至った", "動詞", "After several discussions, the committee came to a final decision.", "何度か話し合った後、委員会は最終決定に至った。"),
    "in that case": ("その場合は", "副詞句", "In that case, we should postpone the outdoor event until tomorrow.", "その場合は、屋外イベントを明日まで延期すべきだ。"),
    "in your favor": ("あなたに有利で", "前置詞句", "The final decision was in your favor after a careful review.", "慎重な審査の後、最終決定はあなたに有利なものとなった。"),
    "for example": ("例えば", "副詞句", "Some sports, for example tennis, can be played throughout the year.", "例えばテニスのように、一年中できるスポーツもある。"),
    "at any time": ("いつでも", "副詞句", "You can contact the help desk at any time during the conference.", "会議中はいつでも案内窓口へ連絡できる。"),
    "look down on": ("見下す", "句動詞", "Good leaders do not look down on people with less experience.", "よい指導者は経験の少ない人を見下さない。"),
    "deal with": ("対処する、扱う", "句動詞", "The counselor helped the student deal with stress before the exam.", "カウンセラーは試験前のストレスに対処するよう生徒を助けた。"),
    "get along with": ("うまく付き合う", "句動詞", "Mika can get along with her new classmates surprisingly well.", "ミカは新しいクラスメートとうまく付き合える。"),
    "make up for": ("埋め合わせる", "句動詞", "The extra practice helped make up for the missed training session.", "追加の練習が欠席した訓練の埋め合わせに役立った。"),
    "out of stock": ("在庫切れで", "形容詞句", "The popular camera was out of stock at every nearby store.", "その人気のカメラは近くのどの店でも在庫切れだった。"),
    "on the go": ("活動し続けて、忙しく動き回って", "副詞句", "Traveling nurses are often on the go from morning until night.", "訪問看護師は朝から夜まで忙しく動き回ることが多い。"),
    "in sight": ("見えて、視界に入って", "副詞句", "After three hours at sea, no island was in sight.", "海上で3時間過ごした後も、島はどこにも見えなかった。"),
    "under the circumstances": ("この状況では", "副詞句", "Under the circumstances, the coach decided to cancel the practice.", "この状況では、コーチは練習を中止することにした。"),
    "choice": ("選択、選択肢", "名詞", "The customer had no choice but to wait for a replacement.", "その客には交換品を待つしか選択肢がなかった。"),
    "chance": ("機会、可能性", "名詞", "There is little chance of finishing the road before winter.", "冬になる前に道路を完成させる可能性はほとんどない。"),
    "kind": ("種類、親切な", "名詞", "What kind of music does your brother listen to after school?", "あなたの弟は放課後どんな種類の音楽を聴くのですか。"),
    "field": ("分野、野原", "名詞", "She hopes to work in the field of environmental science.", "彼女は環境科学の分野で働きたいと思っている。"),
    "from": ("〜から", "前置詞", "The package came from a small shop near the harbor.", "その荷物は港の近くの小さな店から届いた。"),
    "near": ("〜の近くに", "前置詞", "A quiet library stands near the entrance to the park.", "静かな図書館が公園の入口の近くに建っている。"),
    "under": ("〜の下に、〜未満で", "前置詞", "The cat hid under the table during the loud storm.", "大きな嵐の間、猫はテーブルの下に隠れた。"),
    "in memory of": ("〜を記念して", "前置詞句", "The family planted a tree in memory of their grandfather.", "その家族は祖父を記念して木を植えた。"),
    "had become": ("なっていた", "助動詞句", "By sunrise, the quiet street had become crowded with visitors.", "日の出までに、静かな通りは訪問者で混雑していた。"),
    "to become": ("なること", "不定詞句", "She hopes to become a doctor who serves rural communities.", "彼女は地方の地域社会に尽くす医師になりたいと思っている。"),
    "became": ("なった", "動詞", "The small village became famous after the film was released.", "その小さな村は映画が公開された後で有名になった。"),
    "become": ("なる", "動詞", "Many students become nervous before speaking to a large audience.", "多くの生徒は大勢の聴衆の前で話す前に緊張する。"),
    "helping": ("手伝っている", "動詞", "Helping older neighbors with shopping can strengthen a community.", "高齢の近所の人の買い物を手伝うことは地域を強くできる。"),
    "waiting": ("待っている", "動詞", "Waiting outside the theater, the fans talked about the new play.", "劇場の外で待ちながら、ファンたちは新しい劇について話した。"),
    "sitting": ("座っている", "動詞", "Sitting by the window, the artist sketched the passing boats.", "窓のそばに座り、その画家は通り過ぎる船をスケッチした。"),
    "visiting": ("訪れている", "動詞", "Visiting local farms gives children a better idea of where food comes from.", "地元の農場を訪れると、子どもたちは食べ物がどこから来るかよく分かる。"),
    "the time": ("その時", "名詞句", "The time for the meeting was changed because of the storm.", "嵐のため会議の時間が変更された。"),
    "once": ("いったん〜すると、かつて", "接続詞", "Once the rain stopped, the children returned to the playground.", "雨がやむと、子どもたちは遊び場へ戻った。"),
    "ahead": ("前方に、先に", "副詞", "A long journey lay ahead, so the travelers rested early.", "長い旅が待っていたので、旅行者たちは早く休んだ。"),
    "the next": ("次の", "形容詞句", "The next train will arrive at the platform in ten minutes.", "次の列車は10分後にホームへ到着する。"),
}


CORE_IMAGES = {
    "in that case": {"chain": [{"term": "in", "gloss": "状況の中で"}, {"term": "case", "gloss": "場合"}, {"gloss": "その場合は"}]},
    "in your favor": {"chain": [{"term": "in", "gloss": "状態の中に"}, {"term": "favor", "gloss": "味方、有利な扱い"}, {"gloss": "あなたに有利で"}]},
    "for example": {"chain": [{"term": "for", "gloss": "対象として"}, {"term": "example", "gloss": "例"}, {"gloss": "例えば"}]},
    "at any time": {"chain": [{"term": "at", "gloss": "ある時点で"}, {"term": "time", "gloss": "時間"}, {"gloss": "いつでも"}]},
    "look down on": {"chain": [{"term": "look", "gloss": "見る"}, {"term": "down", "gloss": "下へ向けて"}, {"gloss": "相手を下に見て見下す"}]},
    "deal with": {"chain": [{"term": "deal", "gloss": "取り扱う"}, {"term": "with", "gloss": "対象とともに"}, {"gloss": "〜に対処する"}]},
    "get along with": {"chain": [{"term": "get", "gloss": "ある状態になる"}, {"term": "along", "gloss": "一緒に進んで"}, {"gloss": "相手とうまく付き合う"}]},
    "make up for": {"chain": [{"term": "make", "gloss": "作る"}, {"term": "up", "gloss": "足りない分を埋めて"}, {"gloss": "不足を埋め合わせる"}]},
    "out of stock": {"chain": [{"term": "out", "gloss": "外へ出て"}, {"term": "stock", "gloss": "在庫"}, {"gloss": "在庫の外に出て、在庫切れで"}]},
    "on the go": {"chain": [{"term": "on", "gloss": "活動に接して"}, {"term": "go", "gloss": "進むこと"}, {"gloss": "動き続けて、忙しく"}]},
    "in sight": {"chain": [{"term": "in", "gloss": "範囲の中に"}, {"term": "sight", "gloss": "視界"}, {"gloss": "視界に入って"}]},
    "under the circumstances": {"chain": [{"term": "under", "gloss": "条件の下で"}, {"term": "circumstances", "gloss": "周囲の事情"}, {"gloss": "この状況では"}]},
    "in memory of": {"chain": [{"term": "in", "gloss": "状態の中に"}, {"term": "memory", "gloss": "記憶"}, {"gloss": "〜を記念して"}]},
    "had become": {"chain": [{"term": "had", "gloss": "過去のある時点までに"}, {"term": "become", "gloss": "ある状態になる"}, {"gloss": "その時までになっていた"}]},
    "to become": {"chain": [{"term": "to", "gloss": "向かうことを示して"}, {"term": "become", "gloss": "ある状態になる"}, {"gloss": "〜になること"}]},
    "the time": {"chain": [{"term": "time", "gloss": "時間"}, {"gloss": "その時間"}]},
    "the next": {"chain": [{"term": "next", "gloss": "次の"}, {"gloss": "次のもの"}]},
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 20:
        raise ValueError("2級模試第3回は20問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 80 or len(choices) != len(set(choices)):
        raise ValueError("選択肢は重複しない80件である必要があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    idioms = {choice for choice in choices if " " in choice}
    if idioms != set(CORE_IMAGES):
        raise ValueError(f"核心イメージの定義が一致しません: {sorted(idioms ^ set(CORE_IMAGES))}")

    meta = {
        "grade": "英検2級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "ユーザー提供のChapter 3 模擬テスト第3回原稿を基に構造化。訳・例文・語句情報は学習用に作成",
        "counts": {"questions": 20, "words": 63, "idioms": 17, "total": 80},
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
            }
            if " " in choice:
                item["type"] = "idiom"
                item["phrase"] = choice
                item["coreImage"] = CORE_IMAGES[choice]
                idiom_items.append(item)
            else:
                item["word"] = choice
                words.append(item)
    if (len(words), len(idiom_items)) != (63, 17):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idiom_items)}")
    return {"meta": meta, "words": words, "idioms": idiom_items}, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / "vocab_2_mock-3.json", vocab)
    write_json(DATA_DIR / "questions_2_mock-3.json", questions)
    print("eiken2 mock-3: 20 questions / 80 items (63 words, 17 idioms)")


if __name__ == "__main__":
    main()
