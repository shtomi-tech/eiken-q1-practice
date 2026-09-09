"""英検2級 Chapter 3 模擬テスト第2回をQ1形式のJSONへ出力する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-2"


QUESTIONS = [
    {
        "stem": "A: I've been a lawyer for twelve years now. To tell you the truth, I haven't enjoyed it. B: Well then, I think it's time you thought about changing (   ).",
        "choices": ["barriers", "operations", "careers", "borders"],
        "answerIndex": 2,
        "translation": "A：私はもう12年間弁護士をしています。正直に言うと、楽しめていません。B：それなら、職業を変えることを考える時期だと思います。",
    },
    {
        "stem": "A: Oh, no. The GPS seems to be broken again. B: Just keep driving. I'll (   ).",
        "choices": ["straighten", "transport", "generate", "navigate"],
        "answerIndex": 3,
        "translation": "A：困った。GPSがまた壊れたみたい。B：そのまま運転して。私が道案内をするよ。",
    },
    {
        "stem": "A: What do you want for your birthday, Monty? B: Well, Mom, I'd like something (   ), like a new suit I can wear to my company.",
        "choices": ["competitive", "portable", "practical", "cruel"],
        "answerIndex": 2,
        "translation": "A：誕生日に何が欲しいの、モンティ？ B：そうだね、お母さん、実用的なものがいいな。会社に着ていける新しいスーツのようなもの。",
    },
    {
        "stem": "The teacher gave Kate more time to finish her final project considering the (   ) that her mother was sick and in the hospital and she was taking care of her family.",
        "choices": ["reservations", "expectations", "circumstances", "attractions"],
        "answerIndex": 2,
        "translation": "母親が病気で入院し、ケイトが家族の世話をしていたという事情を考慮して、教師は最終課題を終えるための時間をケイトに多く与えた。",
    },
    {
        "stem": "Anna applied for a passport on a site that she thought was a government website. After paying money, however, she realized that she had been (   ), so she contacted the police.",
        "choices": ["pretended", "deceived", "decreased", "provided"],
        "answerIndex": 1,
        "translation": "アンナは政府のウェブサイトだと思ったサイトでパスポートを申請した。しかし、お金を払った後、だまされていたことに気づき、警察に連絡した。",
    },
    {
        "stem": "When Kaori was waiting outside in the hot sun to buy concert tickets, a young woman (   ) on the street beside her. Kaori quickly called 119 while another person offered the young woman water.",
        "choices": ["collapsed", "overcame", "gestured", "functioned"],
        "answerIndex": 0,
        "translation": "カオリがコンサートのチケットを買うため暑い日差しの中で外に並んでいると、隣の通りで若い女性が倒れた。カオリはすぐ119番に電話し、別の人がその女性に水を差し出した。",
    },
    {
        "stem": "A: My son passed all his other classes, so may I ask on what (   ) you failed him in your class? B: The reasons are simple, Ms. Winters. He didn't turn in his homework very often and he failed the final test.",
        "choices": ["basis", "merit", "resource", "district"],
        "answerIndex": 0,
        "translation": "A：息子は他の授業にはすべて合格しました。先生の授業で不合格にした根拠を伺ってもよいでしょうか。B：理由は簡単です、ウィンターズさん。彼は宿題をあまり提出せず、期末試験にも落ちました。",
    },
    {
        "stem": "The construction of the public swimming pool will take (   ) three months. We will post information on the exact opening date on our website later this month.",
        "choices": ["needlessly", "vaguely", "suitably", "approximately"],
        "answerIndex": 3,
        "translation": "公共プールの建設にはおよそ3か月かかる。正確な開業日は今月後半にウェブサイトで知らせる。",
    },
    {
        "stem": "The chef would (   ) the choices on his restaurant's menu every month so that customers could eat a variety of different dishes.",
        "choices": ["link", "vary", "praise", "contrast"],
        "answerIndex": 1,
        "translation": "そのシェフは客がさまざまな料理を食べられるように、毎月レストランのメニューの選択肢を変えた。",
    },
    {
        "stem": "John and Mary met by chance wherever they went. It seemed that it was their (   ) to be together.",
        "choices": ["temper", "fault", "trade", "fate"],
        "answerIndex": 3,
        "translation": "ジョンとメアリーはどこへ行っても偶然出会った。2人が一緒になるのは運命のようだった。",
    },
    {
        "stem": "A: Your reports were excellent. However, (   ) of the two tests you took, you didn't do as well. That's why you received a B instead of an A. B: I see. Thank you for making it clear.",
        "choices": ["on top", "in terms", "in advance of", "in need of"],
        "answerIndex": 1,
        "translation": "A：あなたのレポートはすばらしかったです。しかし、受けた2つの試験に関しては、あまり良い成績ではありませんでした。そのためAではなくBになったのです。B：分かりました。説明してくださってありがとうございます。",
    },
    {
        "stem": "Cindy loves working at the restaurant, but some of the customers are not easily satisfied because they are (   ) their food.",
        "choices": ["proud of", "particular about", "engaged to", "stuck in"],
        "answerIndex": 1,
        "translation": "シンディはそのレストランで働くのが好きだが、客の中には食べ物にこだわりがあり、簡単には満足しない人もいる。",
    },
    {
        "stem": "A: Do you know where Mike is? B: He's in the park. He's (   ) his new skateboard.",
        "choices": ["turning off", "graduating from", "aiming at", "trying out"],
        "answerIndex": 3,
        "translation": "A：マイクがどこにいるか知っている？ B：公園にいるよ。新しいスケートボードを試しているんだ。",
    },
    {
        "stem": "A: When will the new rules be put (   ) practice? B: Sometime next month. We'll announce the exact date later.",
        "choices": ["within", "into", "through", "above"],
        "answerIndex": 1,
        "translation": "A：新しい規則はいつ実行に移されますか。B：来月のいつかです。正確な日付は後で発表します。",
    },
    {
        "stem": "Harold missed the beginning of the concert because he arrived at the concert hall late (   ) heavy traffic.",
        "choices": ["in return for", "with respect to", "as a consequence of", "despite"],
        "answerIndex": 2,
        "translation": "ハロルドは交通渋滞が原因でコンサートホールに遅れて到着し、コンサートの冒頭を聞き逃した。",
    },
    {
        "stem": "A: Mom, I finished cleaning my room. Can I go out? B: You're by no (   ) done. Put your toys on the shelf and then make your bed.",
        "choices": ["means", "plan", "time", "effort"],
        "answerIndex": 0,
        "translation": "A：お母さん、部屋の掃除が終わったよ。外へ行ってもいい？ B：とても終わったとは言えないわ。おもちゃを棚に置いて、それからベッドを整えなさい。",
    },
    {
        "stem": "The railway track had been out of (   ) for several years. It was completely covered in grass.",
        "choices": ["custom", "fashion", "use", "practice"],
        "answerIndex": 2,
        "translation": "その鉄道線路は何年も使われていなかった。草ですっかり覆われていた。",
    },
    {
        "stem": "The professor is planning to retire from his job at the university next year. When he retires, he (   ) at the university for 45 years.",
        "choices": ["will be teaching", "has taught", "will teach", "will have taught"],
        "answerIndex": 3,
        "translation": "その教授は来年、大学の仕事を退職する予定だ。退職するときには、大学で45年間教えたことになる。",
    },
    {
        "stem": "A: Here are three sets of keys for your new office. (   ) any more keys, let me know. B: Thank you.",
        "choices": ["can you require", "should you require", "did you require", "you required"],
        "answerIndex": 1,
        "translation": "A：新しい事務所の鍵を3組用意しました。もしさらに鍵が必要なら、知らせてください。B：ありがとう。",
    },
    {
        "stem": "The woman told her son that she wanted him to have his homework (   ) before dinner.",
        "choices": ["making", "done", "did", "do"],
        "answerIndex": 1,
        "translation": "その女性は息子に、夕食前に宿題を終わらせておいてほしいと言った。",
    },
]


DETAILS = {
    "barriers": ("障壁、妨げ", "名詞", "The language barriers made it difficult for visitors to ask for help.", "言葉の壁のため、訪問者は助けを求めるのが難しかった。"),
    "operations": ("操作、業務、手術", "名詞", "The hospital performs several operations every week for local patients.", "その病院は毎週、地元の患者にいくつもの手術を行っている。"),
    "careers": ("職業、経歴", "名詞", "People often change careers when their interests develop over time.", "人は興味が時間とともに変わると、職業を変えることがよくある。"),
    "borders": ("国境、境界", "名詞", "The travelers crossed several borders during their long train journey.", "旅行者たちは長い列車の旅の間にいくつもの国境を越えた。"),
    "straighten": ("まっすぐにする、整える", "動詞", "Please straighten the picture before you hang it on the wall.", "壁に掛ける前に、その絵をまっすぐにしてください。"),
    "transport": ("運ぶ、輸送する", "動詞", "Special trucks transport fresh vegetables from the farm each morning.", "専用トラックが毎朝、農場から新鮮な野菜を運ぶ。"),
    "generate": ("生み出す、発生させる", "動詞", "The solar panels generate enough electricity for the small building.", "その太陽光パネルは小さな建物に十分な電力を生み出す。"),
    "navigate": ("道案内をする、進路を決める", "動詞", "The guide used a map to navigate through the crowded city streets.", "ガイドは混雑した街路を進むために地図を使った。"),
    "competitive": ("競争力のある、競争好きな", "形容詞", "The company offers competitive prices to attract new customers.", "その会社は新しい客を引きつけるため競争力のある価格を提示している。"),
    "portable": ("持ち運びできる", "形容詞", "This portable speaker is small enough to fit inside my backpack.", "この持ち運びできるスピーカーはリュックに入るほど小さい。"),
    "practical": ("実用的な、現実的な", "形容詞", "A practical coat is a useful gift for someone who walks to work.", "実用的なコートは歩いて通勤する人への便利な贈り物だ。"),
    "cruel": ("残酷な", "形容詞", "It was cruel to leave the injured animal outside in the cold.", "けがをした動物を寒い外に置き去りにするのは残酷だった。"),
    "reservations": ("予約、懸念", "名詞", "We made reservations at a quiet restaurant near the theater.", "私たちは劇場近くの静かなレストランを予約した。"),
    "expectations": ("期待、予想", "名詞", "The young athlete performed beyond everyone's expectations at the event.", "その若い選手は大会で皆の期待を超える活躍をした。"),
    "circumstances": ("事情、状況", "名詞", "Under these circumstances, postponing the meeting seems like a wise choice.", "このような状況では、会議を延期するのが賢明な選択に思える。"),
    "attractions": ("呼び物、魅力", "名詞", "The city has several attractions that appeal to families with children.", "その都市には子どものいる家族を引きつける見どころがいくつかある。"),
    "pretended": ("ふりをした", "動詞", "The child pretended to be asleep when his father entered the room.", "父親が部屋に入ると、子どもは眠っているふりをした。"),
    "deceived": ("だました、だまされた", "動詞", "The customer realized that the advertisement had deceived her about the price.", "その客は広告が価格について自分をだましていたことに気づいた。"),
    "decreased": ("減少した、減らした", "動詞", "The number of visitors decreased after the museum raised its entrance fee.", "博物館が入場料を上げた後、訪問者数は減少した。"),
    "provided": ("提供した、与えた", "動詞", "The hotel provided every guest with a map of the local area.", "そのホテルは宿泊客全員に周辺地域の地図を提供した。"),
    "collapsed": ("倒れた、崩壊した", "動詞", "The old bridge collapsed after several days of heavy rain.", "古い橋は数日間の大雨の後に崩れ落ちた。"),
    "overcame": ("克服した", "動詞", "She overcame her fear of speaking and gave a clear presentation.", "彼女は話すことへの恐怖を克服し、明快な発表をした。"),
    "gestured": ("身ぶりをした、合図した", "動詞", "The officer gestured for the driver to stop beside the road.", "警官は運転手に道路脇で止まるよう身ぶりで合図した。"),
    "functioned": ("機能した、作動した", "動詞", "The emergency phone functioned even after the power went out.", "停電した後も非常電話は機能した。"),
    "basis": ("根拠、基準", "名詞", "The decision was made on the basis of reliable scientific evidence.", "その決定は信頼できる科学的証拠に基づいてなされた。"),
    "merit": ("価値、長所", "名詞", "The committee discussed the merit of each proposal before voting.", "委員会は投票前に各提案の長所を話し合った。"),
    "resource": ("資源、資料", "名詞", "The library is an important resource for students doing research.", "その図書館は研究をする生徒にとって重要な資料源だ。"),
    "district": ("地区、区域", "名詞", "The school district opened a new center for after-school activities.", "学区は放課後活動のための新しいセンターを開設した。"),
    "needlessly": ("不必要に", "副詞", "The driver needlessly repeated the same warning several times.", "その運転手は同じ警告を何度も不必要に繰り返した。"),
    "vaguely": ("あいまいに、漠然と", "副詞", "He vaguely remembered meeting the artist at a local event.", "彼は地元の行事でその芸術家に会ったことをぼんやり覚えていた。"),
    "suitably": ("適切に、ふさわしく", "副詞", "The hall was suitably decorated for the formal award ceremony.", "そのホールは正式な授賞式にふさわしく飾られていた。"),
    "approximately": ("およそ、約", "副詞", "The journey takes approximately two hours by express train.", "その旅は急行列車でおよそ2時間かかる。"),
    "link": ("つなぐ、関連づける", "動詞", "The website can link customers to useful information about recycling.", "そのウェブサイトは客をリサイクルに関する役立つ情報につなげられる。"),
    "vary": ("変える、異なる", "動詞", "The chef can vary the daily menu according to the season.", "そのシェフは季節に応じて毎日のメニューを変えられる。"),
    "praise": ("称賛する、ほめる", "動詞", "The coach continued to praise the players for their careful teamwork.", "監督は選手たちの慎重なチームワークをほめ続けた。"),
    "contrast": ("対照させる、対比する", "動詞", "The writer will contrast the quiet village with the noisy capital city in the next chapter.", "その作家は次の章で静かな村と騒がしい首都を対比する。"),
    "temper": ("気性、気分", "名詞", "The patient teacher rarely lost her temper during difficult lessons.", "その忍耐強い教師は難しい授業中にもめったに腹を立てなかった。"),
    "fault": ("欠点、責任、故障", "名詞", "The engineer found a fault in the machine before the test began.", "技術者は試験が始まる前に機械の故障を見つけた。"),
    "trade": ("貿易、職業、交換", "名詞", "International trade has changed greatly because of online shopping.", "オンラインショッピングによって国際貿易は大きく変わった。"),
    "fate": ("運命", "名詞", "The travelers felt that fate had brought them together at the station.", "旅行者たちは運命が駅で自分たちを引き合わせたと感じた。"),
    "on top": ("上に、さらに", "副詞句", "The keys were on top of the cabinet beside the window.", "鍵は窓のそばの戸棚の上にあった。"),
    "in terms": ("〜に関して、〜の点で", "前置詞句", "In terms of safety, this design is better than the older one.", "安全性の点では、この設計は古いものより優れている。"),
    "in advance of": ("〜に先立って", "前置詞句", "The staff prepared the room in advance of the important meeting.", "職員は重要な会議に先立って部屋を準備した。"),
    "in need of": ("〜を必要として", "前置詞句", "The old theater is in need of serious repairs before reopening.", "その古い劇場は再開前に大規模な修理を必要としている。"),
    "proud of": ("〜を誇りに思って", "形容詞句", "The parents were proud of their daughter's careful work.", "両親は娘の丁寧な仕事を誇りに思っていた。"),
    "particular about": ("〜にこだわって、〜について好みがうるさくて", "形容詞句", "My brother is particular about the quality of the coffee he drinks.", "私の兄は飲むコーヒーの品質にこだわっている。"),
    "engaged to": ("〜と婚約して", "形容詞句", "She is engaged to a doctor who works at the nearby hospital.", "彼女は近くの病院で働く医師と婚約している。"),
    "stuck in": ("〜にはまり込んで、〜から動けずに", "形容詞句", "The hikers were stuck in deep snow for several hours.", "ハイカーたちは数時間、深い雪にはまり込んでいた。"),
    "turning off": ("〜の電源を切る、〜を消す", "動詞句", "Turning off the lights before leaving can save a surprising amount of energy.", "出る前に照明を消すと、驚くほど多くのエネルギーを節約できる。"),
    "graduating from": ("〜を卒業して", "動詞句", "After graduating from college, she moved to a smaller city.", "大学を卒業した後、彼女はより小さな都市へ引っ越した。"),
    "aiming at": ("〜をねらって、〜を目指して", "動詞句", "The new advertising campaign is aiming at younger customers.", "新しい広告キャンペーンは若い客を対象としている。"),
    "trying out": ("〜を試している", "動詞句", "The players are trying out new equipment before the tournament.", "選手たちは大会前に新しい用具を試している。"),
    "within": ("〜以内に、〜の中に", "前置詞", "The package should arrive within three business days after shipping.", "荷物は発送後3営業日以内に届くはずだ。"),
    "into": ("〜の中へ、〜に", "前置詞", "The volunteers carried the boxes into the storage room carefully.", "ボランティアたちは箱を注意深く倉庫へ運び入れた。"),
    "through": ("〜を通って、〜を通じて", "前置詞", "The sunlight came through the curtains during the quiet morning.", "静かな朝、日光がカーテンを通って差し込んだ。"),
    "above": ("〜より上に、〜を超えて", "前置詞", "The temperature stayed above zero throughout the winter afternoon.", "冬の午後を通して気温は零度を上回っていた。"),
    "in return for": ("〜と引き換えに", "前置詞句", "The volunteer received a meal in return for helping at the event.", "そのボランティアは行事を手伝った引き換えに食事を受け取った。"),
    "with respect to": ("〜に関して", "前置詞句", "With respect to the schedule, we will send an update tomorrow.", "予定に関しては、明日最新情報を送る。"),
    "as a consequence of": ("〜の結果として、〜が原因で", "前置詞句", "The road closed as a consequence of severe flooding near the bridge.", "橋の近くの深刻な洪水の結果、その道路は閉鎖された。"),
    "despite": ("〜にもかかわらず", "前置詞", "Despite the heavy rain, the outdoor concert continued until midnight.", "大雨にもかかわらず、野外コンサートは深夜まで続いた。"),
    "means": ("手段、方法、意味", "名詞", "Public transportation is an affordable means of traveling around the city.", "公共交通機関は市内を移動する手頃な手段だ。"),
    "plan": ("計画", "名詞", "The team made a detailed plan before starting the difficult project.", "チームは難しい計画を始める前に詳細な計画を立てた。"),
    "time": ("時間、時", "名詞", "Please arrive on time so we can begin the lesson together.", "一緒に授業を始められるよう時間どおりに来てください。"),
    "effort": ("努力", "名詞", "Her effort to improve the neighborhood was appreciated by everyone.", "近所をよくしようとする彼女の努力は皆に感謝された。"),
    "custom": ("習慣、慣例", "名詞", "It is a local custom to share food with visitors during festivals.", "祭りの間に訪問者と食べ物を分け合うのは地元の習慣だ。"),
    "fashion": ("流行、方法", "名詞", "The designer created a jacket that was soon in fashion among students.", "そのデザイナーはすぐに学生の間で流行するジャケットを作った。"),
    "use": ("使用、用途", "名詞", "The old computer is still in use in the school office.", "その古いコンピューターは今も学校の事務室で使われている。"),
    "practice": ("練習、実行、慣行", "名詞", "Daily practice helped the young musician prepare for the concert.", "毎日の練習が若い音楽家のコンサート準備に役立った。"),
    "will be teaching": ("教えていることになるだろう", "助動詞句", "Next year, she will be teaching English at a school abroad.", "来年、彼女は海外の学校で英語を教えていることになる。"),
    "has taught": ("教えてきた、教えたことがある", "助動詞句", "He has taught science at this university since the new building opened.", "彼は新しい建物が開いて以来、この大学で科学を教えてきた。"),
    "will teach": ("教えるだろう", "助動詞句", "The visiting professor will teach a special class next Saturday.", "客員教授は来週の土曜日に特別授業を行うだろう。"),
    "will have taught": ("教えたことになるだろう", "助動詞句", "By next June, the professor will have taught here for forty-five years.", "来年6月までに、その教授はここで45年間教えたことになるだろう。"),
    "can you require": ("あなたは必要とできますか", "接続詞句", "The manager asked, Can you require any additional equipment for the event?", "マネージャーは、行事に追加の用具が必要かと尋ねた。"),
    "should you require": ("もしあなたが必要とするなら", "接続詞句", "Should you require further assistance, please contact the information desk.", "さらに助けが必要なら、案内所へ連絡してください。"),
    "did you require": ("あなたは必要としましたか", "接続詞句", "The clerk asked, Did you require a receipt for the purchase?", "店員は、その購入について領収書が必要か尋ねた。"),
    "you required": ("あなたが必要とした", "接続詞句", "The form records which documents you required for the application.", "その用紙には申請に必要とした書類が記録されている。"),
    "making": ("作ること、行うこと", "動詞", "Making a clear schedule can reduce stress before an important exam.", "明確な予定表を作ることは重要な試験前のストレスを減らせる。"),
    "done": ("終えた、済んだ", "動詞", "The work was done before the guests arrived at the house.", "客が家に着く前に作業は終わっていた。"),
    "did": ("した", "動詞", "She did everything possible to help the injured traveler.", "彼女はけがをした旅行者を助けるためできることをすべてした。"),
    "do": ("する、行う", "動詞", "What can we do to make the classroom more comfortable?", "教室をもっと快適にするために何ができるだろうか。"),
}


CORE_IMAGES = {
    "on top": {"chain": [{"term": "on", "gloss": "接して上に"}, {"term": "top", "gloss": "頂点"}, {"gloss": "上に、さらに"}]},
    "in terms": {"chain": [{"term": "in", "gloss": "範囲の中で"}, {"term": "terms", "gloss": "観点、条件"}, {"gloss": "〜に関して、〜の点で"}]},
    "in advance of": {"chain": [{"term": "advance", "gloss": "前へ進むこと"}, {"term": "of", "gloss": "〜に先立って"}, {"gloss": "〜に先立って"}]},
    "in need of": {"chain": [{"term": "need", "gloss": "必要"}, {"term": "of", "gloss": "対象について"}, {"gloss": "〜を必要として"}]},
    "proud of": {"chain": [{"term": "proud", "gloss": "誇りに思う"}, {"term": "of", "gloss": "対象について"}, {"gloss": "〜を誇りに思って"}]},
    "particular about": {"chain": [{"term": "particular", "gloss": "特定の点にこだわる"}, {"term": "about", "gloss": "対象について"}, {"gloss": "〜にこだわって"}]},
    "engaged to": {"chain": [{"term": "engaged", "gloss": "関わりを約束した"}, {"term": "to", "gloss": "相手へ結びついて"}, {"gloss": "〜と婚約して"}]},
    "stuck in": {"chain": [{"term": "stuck", "gloss": "動けずに固定された"}, {"term": "in", "gloss": "中に"}, {"gloss": "〜にはまり込んで"}]},
    "turning off": {"particle": "off", "particleSense": "separate", "chain": [{"term": "turn", "gloss": "向きを変える"}, {"term": "off", "gloss": "切り離して"}, {"gloss": "機器の作用を切って消す"}]},
    "graduating from": {"chain": [{"term": "graduating", "gloss": "段階を修了して"}, {"term": "from", "gloss": "〜から離れて"}, {"gloss": "〜を卒業して"}]},
    "aiming at": {"chain": [{"term": "aiming", "gloss": "ねらいを定めて"}, {"term": "at", "gloss": "対象へ向けて"}, {"gloss": "〜をねらって、〜を目指して"}]},
    "trying out": {"chain": [{"term": "trying", "gloss": "試して"}, {"term": "out", "gloss": "外へ出して確かめて"}, {"gloss": "実際に試してみる"}]},
    "in return for": {"chain": [{"term": "return", "gloss": "返すこと"}, {"term": "for", "gloss": "交換の対象として"}, {"gloss": "〜と引き換えに"}]},
    "with respect to": {"chain": [{"term": "respect", "gloss": "配慮、関係"}, {"term": "to", "gloss": "対象へ向けて"}, {"gloss": "〜に関して"}]},
    "as a consequence of": {"chain": [{"term": "consequence", "gloss": "結果"}, {"term": "of", "gloss": "〜について"}, {"gloss": "〜の結果として、〜が原因で"}]},
    "will be teaching": {"chain": [{"term": "will", "gloss": "未来を示して"}, {"term": "teaching", "gloss": "教えている"}, {"gloss": "将来その時点で教えていることになる"}]},
    "has taught": {"chain": [{"term": "has", "gloss": "現在まで持続して"}, {"term": "taught", "gloss": "教えた"}, {"gloss": "過去から現在まで教えてきた"}]},
    "will teach": {"chain": [{"term": "will", "gloss": "未来を示して"}, {"term": "teach", "gloss": "教える"}, {"gloss": "将来教えるだろう"}]},
    "will have taught": {"chain": [{"term": "will", "gloss": "未来を示して"}, {"term": "have", "gloss": "経験を持って"}, {"term": "taught", "gloss": "教えた"}, {"gloss": "未来の時点までに教え終えていることになる"}]},
    "can you require": {"chain": [{"term": "can", "gloss": "可能かを示して"}, {"term": "require", "gloss": "必要とする"}, {"gloss": "必要とできますかと尋ねる"}]},
    "should you require": {"chain": [{"term": "should", "gloss": "条件を示して"}, {"term": "require", "gloss": "必要とする"}, {"gloss": "もし必要なら"}]},
    "did you require": {"chain": [{"term": "did", "gloss": "過去の事実を尋ねて"}, {"term": "require", "gloss": "必要とする"}, {"gloss": "必要としましたかと尋ねる"}]},
    "you required": {"chain": [{"term": "you", "gloss": "相手が"}, {"term": "required", "gloss": "必要とした"}, {"gloss": "あなたが必要とした"}]},
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 20:
        raise ValueError("2級模試第2回は20問である必要があります")
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
        "source": "ユーザー提供のChapter 3 模擬テスト第2回原稿を基に構造化。訳・例文・語句情報は学習用に作成",
        "counts": {"questions": 20, "words": 57, "idioms": 23, "total": 80},
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
    if (len(words), len(idiom_items)) != (57, 23):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idiom_items)}")
    return {"meta": meta, "words": words, "idioms": idiom_items}, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / "vocab_2_mock-2.json", vocab)
    write_json(DATA_DIR / "questions_2_mock-2.json", questions)
    print("eiken2 mock-2: 20 questions / 80 items (57 words, 23 idioms)")


if __name__ == "__main__":
    main()
