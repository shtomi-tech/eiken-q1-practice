"""英検2級 Chapter 3 模擬テスト第4回のデータを生成する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-4"


QUESTIONS = [
    {
        "stem": "Gina became very (   ) at her retirement party. She even cried when she gave a speech to thank everyone for their support.",
        "choices": ["emotional", "romantic", "jealous", "invisible"],
        "answerIndex": 0,
        "translation": "ジーナは退職祝いの会でとても感情的になった。支えてくれた皆に感謝するスピーチをしたときには泣きさえした。",
    },
    {
        "stem": "Rick's and his wife's personalities are (   ), so they see the world differently and often disagree on things. Despite that, they get along well.",
        "choices": ["legends", "citizens", "strangers", "opposites"],
        "answerIndex": 3,
        "translation": "リックと妻の性格は正反対なので、物事の見方が異なり、よく意見が合わない。それでも二人は仲良くやっている。",
    },
    {
        "stem": "Police caught a robber who had a bag filled with stolen goods. He (   ) that he had robbed several houses on the street.",
        "choices": ["referred", "admitted", "folded", "raised"],
        "answerIndex": 1,
        "translation": "警察は盗品でいっぱいの袋を持った強盗を捕まえた。彼はその通りの数軒の家に押し入ったことを認めた。",
    },
    {
        "stem": "Among the top three people who applied to become hotel manager, Bridget Reardon was chosen due to her (   ). It was important to have someone who loved their work.",
        "choices": ["complexity", "geometry", "structure", "enthusiasm"],
        "answerIndex": 3,
        "translation": "ホテルの支配人に応募した上位3人の中で、ブリジット・リアドンは熱意を理由に選ばれた。仕事を愛する人を選ぶことが重要だった。",
    },
    {
        "stem": "The researchers (   ) the results of their experiment and realized that they had made a major scientific discovery.",
        "choices": ["evaluated", "composed", "violated", "destroyed"],
        "answerIndex": 0,
        "translation": "研究者たちは実験結果を評価し、自分たちが重大な科学的発見をしたことに気づいた。",
    },
    {
        "stem": "A: Thanks for taking care of my dog while I was away. Can I pick him up this afternoon? B: Sure, but can you call (   )? I have to go out for a little while this afternoon.",
        "choices": ["concretely", "seriously", "beforehand", "permanently"],
        "answerIndex": 2,
        "translation": "A：留守中に犬の世話をしてくれてありがとう。今日の午後に迎えに行ってもいい？B：もちろん。でも、前もって電話してくれる？午後に少し出かけなければならないんだ。",
    },
    {
        "stem": "The runner was one of the fastest in his country, but he failed to (   ) in the Summer Olympics because of an injury.",
        "choices": ["spare", "memorize", "intend", "compete"],
        "answerIndex": 3,
        "translation": "その走者は国内で最も速い選手の一人だったが、けがのため夏季オリンピックに出場できなかった。",
    },
    {
        "stem": "A: We just moved to a nature-loving community called Eco-Village. We all work hard to take care of the nature around us. B: What a great (   )! I'd love to see your new place.",
        "choices": ["concept", "license", "psychology", "violence"],
        "answerIndex": 0,
        "translation": "A：私たちはエコ・ビレッジという自然を愛する地域に引っ越したばかりです。皆で周囲の自然を大切にするために努力しています。B：なんてすばらしい構想でしょう。新しい場所を見てみたいです。",
    },
    {
        "stem": "The developers (   ) the old farmhouse into a fashionable hotel with a large spa and swimming pool.",
        "choices": ["tracked", "rotated", "declared", "converted"],
        "answerIndex": 3,
        "translation": "開発業者たちは古い農家を、大きなスパとプールのあるおしゃれなホテルに改装した。",
    },
    {
        "stem": "Ken decided to continue studying after university because he wanted to get more (   ) to do scientific research in the future.",
        "choices": ["souvenirs", "prospects", "shifts", "vacancies"],
        "answerIndex": 1,
        "translation": "ケンは将来科学研究をする機会をもっと得たいと思い、大学卒業後も勉強を続けることにした。",
    },
    {
        "stem": "A: The movie is starting soon. Do you think Joseph is still coming? B: Yes, I'm sure he'll be here soon. It's (   ) him to be a few minutes late.",
        "choices": ["similar to", "bound for", "typical of", "engaged in"],
        "answerIndex": 2,
        "translation": "A：もうすぐ映画が始まります。ジョセフはまだ来ると思いますか。B：はい、すぐ来るはずです。彼が数分遅れるのはいつものことです。",
    },
    {
        "stem": "A: Is it possible for me to do my interview online? B: Yes, that's possible for the first interview, but we'd prefer to meet you (   ) for the second one.",
        "choices": ["in person", "at present", "in writing", "on hand"],
        "answerIndex": 0,
        "translation": "A：面接をオンラインで受けることはできますか。B：最初の面接なら可能ですが、2回目は直接お会いしたいと思います。",
    },
    {
        "stem": "A: Dad, I'm going camping tomorrow. B: Take this $20 (   ) you need anything.",
        "choices": ["now that", "as if", "in case", "every time"],
        "answerIndex": 2,
        "translation": "A：お父さん、明日キャンプに行くんだ。B：何か必要な場合に備えて、この20ドルを持っていきなさい。",
    },
    {
        "stem": "Wendy did not admit that she was wrong because she did not want to lose (   ) in front of her friends.",
        "choices": ["back", "money", "face", "way"],
        "answerIndex": 2,
        "translation": "ウェンディは友人の前で面目を失いたくなかったので、自分が間違っていたと認めなかった。",
    },
    {
        "stem": "A: We've got to work faster, or we won't finish on time. B: But we have so much work and only have an hour left. We're not going to (   ) it.",
        "choices": ["try", "get", "manage", "own"],
        "answerIndex": 2,
        "translation": "A：もっと速く働かないと、時間内に終わりません。B：でも仕事が多すぎるし、残り1時間しかありません。私たちには対処しきれません。",
    },
    {
        "stem": "A: So, Jane, are you still planning to buy a house? B: Well, I've been having (   ). An apartment may be cheaper.",
        "choices": ["social issues", "new beginnings", "shared values", "second thoughts"],
        "answerIndex": 3,
        "translation": "A：それで、ジェーン、まだ家を買うつもりですか。B：そうですね、考え直しています。アパートの方が安いかもしれません。",
    },
    {
        "stem": "Charles (   ) a sign to his office door using tape and asking delivery people to leave any packages outside.",
        "choices": ["filled", "stuck", "wasted", "meant"],
        "answerIndex": 1,
        "translation": "チャールズは配達員に荷物を外に置いていくよう求める標識を事務所のドアに貼った。",
    },
    {
        "stem": "Trent felt bad about (   ) so much money on a new watch, so he returned it to the store before his wife found out about it.",
        "choices": ["spent", "having spent", "has spent", "had spent"],
        "answerIndex": 1,
        "translation": "トレントは新しい時計にそれほど多くのお金を使ったことを後悔したので、妻に知られる前に店へ返品した。",
    },
    {
        "stem": "A: I'm pretty sure I can repair the dishwasher this time, Mom. B: No matter (   ) you do it, please make sure I don't have any more problems.",
        "choices": ["why", "since", "how", "what"],
        "answerIndex": 2,
        "translation": "A：今回は食器洗い機をきっと修理できると思うよ、母さん。B：どのように修理するにしても、これ以上問題が起きないようにしてちょうだい。",
    },
    {
        "stem": "Sam overslept, and his alarm clock was still turned off. He (   ) set his alarm clock. As a result, he woke up too late to get to the station on time.",
        "choices": ["will not have", "would not have", "should not have", "must not have"],
        "answerIndex": 3,
        "translation": "サムは目覚まし時計をセットしなかったに違いない。彼は駅に時間どおり着くには遅すぎる時間に起きた。",
    },
]


DETAILS = {
    "emotional": ("感情的な、感動した", "形容詞", "The emotional student thanked her teachers at the graduation ceremony.", "その感動した生徒は卒業式で先生たちに感謝した。"),
    "romantic": ("ロマンチックな", "形容詞", "They chose a romantic restaurant beside the river for their anniversary.", "彼らは記念日に川沿いのロマンチックなレストランを選んだ。"),
    "jealous": ("嫉妬した", "形容詞", "The jealous child did not want to share the new toy.", "嫉妬した子どもは新しいおもちゃを共有したがらなかった。"),
    "invisible": ("目に見えない", "形容詞", "Some forms of pollution are invisible but still dangerous to people.", "汚染には目に見えなくても人々に危険なものがある。"),
    "legends": ("伝説、伝説的人物", "名詞", "The museum displays legends about the island's first settlers.", "その博物館は島の最初の入植者たちに関する伝説を展示している。"),
    "citizens": ("市民、国民", "名詞", "The citizens gathered to discuss plans for the new park.", "市民は新しい公園の計画について話し合うため集まった。"),
    "strangers": ("見知らぬ人々", "名詞", "The two strangers started talking while they waited for the bus.", "その見知らぬ二人はバスを待つ間に話し始めた。"),
    "opposites": ("正反対のもの", "名詞", "The twins are complete opposites, but their parents respect both views.", "その双子は正反対だが、両親は両方の考えを尊重している。"),
    "referred": ("言及した、参照した", "動詞", "The speaker referred to several studies during the lecture.", "講演者は講義中にいくつかの研究に言及した。"),
    "admitted": ("認めた", "動詞", "The driver admitted that he had ignored the warning sign.", "その運転手は警告標識を無視したことを認めた。"),
    "folded": ("折りたたんだ", "動詞", "She folded the map carefully before putting it in her bag.", "彼女は地図をバッグに入れる前に注意深く折りたたんだ。"),
    "raised": ("上げた、育てた", "動詞", "The farmer raised healthy animals on the small mountain pasture.", "その農家は小さな山の牧草地で健康な動物を育てた。"),
    "complexity": ("複雑さ", "名詞", "The engineer explained the complexity of the new machine to us.", "技術者は新しい機械の複雑さを私たちに説明した。"),
    "geometry": ("幾何学", "名詞", "The students practiced geometry before the difficult mathematics test.", "生徒たちは難しい数学の試験の前に幾何学を練習した。"),
    "structure": ("構造、仕組み", "名詞", "The architect examined the structure of the old hotel carefully.", "建築家は古いホテルの構造を注意深く調べた。"),
    "enthusiasm": ("熱意、情熱", "名詞", "Her enthusiasm for cooking encouraged everyone to join the class.", "料理への彼女の熱意が皆を授業へ参加させた。"),
    "evaluated": ("評価した", "動詞", "The scientists evaluated the data before publishing their final report.", "科学者たちは最終報告を発表する前にデータを評価した。"),
    "composed": ("構成した、作曲した", "動詞", "The musician composed a short song for the school festival.", "その音楽家は学校祭のために短い曲を作曲した。"),
    "violated": ("違反した、侵害した", "動詞", "The company violated the safety rules during the construction project.", "その会社は建設工事中に安全規則に違反した。"),
    "destroyed": ("破壊した", "動詞", "The strong storm destroyed several small boats near the harbor.", "激しい嵐は港の近くにあった小さな船を数隻破壊した。"),
    "concretely": ("具体的に", "副詞", "The manager explained concretely how the new schedule would work.", "管理者は新しい予定がどう機能するか具体的に説明した。"),
    "seriously": ("真剣に、深刻に", "副詞", "The doctor seriously considered changing the patient's treatment plan.", "医師は患者の治療計画を変更することを真剣に検討した。"),
    "beforehand": ("前もって", "副詞", "Please reserve a seat beforehand because the hall fills quickly.", "会場はすぐ満員になるので、前もって席を予約してください。"),
    "permanently": ("永久に、恒久的に", "副詞", "The family permanently moved to the island after many visits.", "その家族は何度も訪れた後、島へ永久に移住した。"),
    "spare": ("割く、予備の", "動詞", "Could you spare a few minutes to help me today?", "今日、数分を割いて私を手伝ってくれませんか。"),
    "memorize": ("暗記する", "動詞", "Students were asked to memorize the poem for next week's class.", "生徒たちは来週の授業のためにその詩を暗記するよう求められた。"),
    "intend": ("意図する、つもりである", "動詞", "We intend to finish the community garden before summer begins.", "私たちは夏が始まる前に地域の庭を完成させるつもりだ。"),
    "compete": ("競争する、出場する", "動詞", "More than one hundred athletes will compete in the national event.", "100人を超える選手が全国大会に出場する。"),
    "concept": ("概念、構想", "名詞", "The architect presented a new concept for an energy-saving house.", "建築家は省エネルギー住宅の新しい構想を示した。"),
    "license": ("免許、許可証", "名詞", "You need a special license to operate this large vehicle.", "この大型車を運転するには特別な免許が必要だ。"),
    "psychology": ("心理学", "名詞", "She decided to study psychology at a university near her home.", "彼女は自宅近くの大学で心理学を学ぶことにした。"),
    "violence": ("暴力", "名詞", "The school teaches students how to solve conflicts without violence.", "その学校は生徒に暴力を使わず対立を解決する方法を教えている。"),
    "tracked": ("追跡した、記録した", "動詞", "The hikers tracked their route with a map and compass.", "ハイカーたちは地図とコンパスで進んだ道を記録した。"),
    "rotated": ("回転させた、交代した", "動詞", "The technician rotated the wheel to test the new equipment.", "技術者は新しい装置を試すため車輪を回転させた。"),
    "declared": ("宣言した、申告した", "動詞", "The mayor declared the summer festival open on Saturday morning.", "市長は土曜日の朝、夏祭りの開幕を宣言した。"),
    "converted": ("変えた、改装した", "動詞", "The company converted an empty warehouse into a modern library.", "その会社は空の倉庫を現代的な図書館に改装した。"),
    "souvenirs": ("お土産", "名詞", "The tourists bought souvenirs at the station before leaving town.", "観光客たちは町を出る前に駅でお土産を買った。"),
    "prospects": ("見込み、可能性、機会", "名詞", "The internship improved her prospects of finding a research position.", "そのインターンシップは研究職を見つける見込みを高めた。"),
    "shifts": ("交代勤務、変化", "名詞", "The hospital changed the nurses' shifts during the holiday period.", "その病院は休暇期間中、看護師の勤務シフトを変更した。"),
    "vacancies": ("空き、空室、欠員", "名詞", "The hotel has no vacancies during the festival weekend.", "そのホテルは祭りの週末には空室がない。"),
    "similar to": ("〜に似て", "形容詞句", "The new design is similar to the one used last year.", "新しいデザインは昨年使われたものに似ている。"),
    "bound for": ("〜行きの", "形容詞句", "The train bound for Osaka leaves from platform three.", "大阪行きの列車は3番ホームから出発する。"),
    "typical of": ("〜に典型的な、〜らしい", "形容詞句", "It is typical of Joseph to arrive a few minutes late.", "ジョセフが数分遅れて到着するのは彼らしい。"),
    "engaged in": ("〜に従事して", "形容詞句", "The students were engaged in a lively discussion about the novel.", "生徒たちはその小説について活発な議論をしていた。"),
    "in person": ("直接会って", "副詞句", "The manager prefers to meet new employees in person.", "その管理者は新入社員と直接会うことを好む。"),
    "at present": ("現在は", "副詞句", "At present, the clinic has no open appointments.", "現在、その診療所には空いている予約枠がない。"),
    "in writing": ("書面で", "副詞句", "Please send the final request in writing before Friday.", "金曜日までに最終依頼を書面で送ってください。"),
    "on hand": ("手元に、用意して", "副詞句", "The store keeps several replacement parts on hand.", "その店は交換部品をいくつか手元に用意している。"),
    "now that": ("今や〜なので", "接続詞句", "Now that the weather is warmer, we can open the windows.", "今や天気が暖かくなったので、窓を開けられる。"),
    "as if": ("まるで〜のように", "接続詞句", "He spoke as if he had already visited the distant country.", "彼はまるでその遠い国をすでに訪れたかのように話した。"),
    "in case": ("〜の場合に備えて", "接続詞句", "Take an umbrella in case the weather changes suddenly.", "天気が急に変わる場合に備えて、傘を持っていきなさい。"),
    "every time": ("〜するたびに", "接続詞句", "Every time the bell rings, the students change rooms.", "ベルが鳴るたびに、生徒たちは教室を移動する。"),
    "back": ("背中、後ろ、戻って", "名詞", "The swimmer hurt his back during practice yesterday afternoon.", "その水泳選手は昨日の午後、練習中に背中を痛めた。"),
    "money": ("お金", "名詞", "The child saved money for a bicycle throughout the summer.", "その子どもは夏の間ずっと自転車のためにお金を貯めた。"),
    "face": ("面目、顔", "名詞", "She tried to keep a calm face during the difficult interview.", "彼女は難しい面接中も落ち着いた顔を保とうとした。"),
    "way": ("方法、道", "名詞", "The guide showed us the safest way to the mountain lake.", "ガイドは山の湖へ行く最も安全な道を教えてくれた。"),
    "try": ("試す、努力する", "動詞", "The children will try a new sport at the summer camp.", "子どもたちはサマーキャンプで新しいスポーツを試す。"),
    "get": ("得る、到着する", "動詞", "We need to get more information before making a decision.", "決定する前にもっと情報を得る必要がある。"),
    "manage": ("何とか対処する、やり遂げる", "動詞", "We must manage the difficult project carefully before the deadline arrives.", "締め切りが来る前に、私たちはその難しい計画を慎重に何とか進めなければならない。"),
    "own": ("所有する", "動詞", "Many families own a small car for weekend trips.", "多くの家庭が週末の旅行用に小さな車を所有している。"),
    "social issues": ("社会問題", "名詞句", "The course examines social issues affecting young families.", "その講座は若い家庭に影響する社会問題を扱う。"),
    "new beginnings": ("新しい始まり", "名詞句", "Moving to the coast gave her hope for new beginnings.", "海岸へ引っ越したことで、彼女は新しい始まりへの希望を持った。"),
    "shared values": ("共有する価値観", "名詞句", "The two organizations cooperate because they have shared values.", "その二つの組織は共有する価値観があるので協力している。"),
    "second thoughts": ("再考、迷い", "名詞句", "After reading the contract, she had second thoughts about signing it.", "契約書を読んだ後、彼女は署名することを考え直した。"),
    "filled": ("満たした、詰めた", "動詞", "The worker filled the box with books for the school library.", "作業員は学校図書館用の本で箱を満たした。"),
    "stuck": ("貼り付けた、動けなくなった", "動詞", "Charles stuck a notice to the office door before leaving.", "チャールズは出かける前に事務所のドアへ掲示を貼った。"),
    "wasted": ("無駄にした", "動詞", "The student wasted an entire afternoon watching old videos.", "その生徒は午後を丸ごと古い動画を見て無駄にした。"),
    "meant": ("意味した、意図した", "動詞", "The message meant that visitors should use the side entrance.", "そのメッセージは訪問者が側面入口を使うべきだという意味だった。"),
    "spent": ("使った、過ごした", "動詞", "She spent the weekend organizing old photographs with her mother.", "彼女は週末を母親と古い写真の整理に使った。"),
    "having spent": ("使ったこと", "動詞句", "Having spent all morning on the report, he took a short break.", "報告書に午前中ずっと取り組んだので、彼は短い休憩を取った。"),
    "has spent": ("使ってきた、過ごした", "助動詞句", "She has spent several years studying insects in the rainforest.", "彼女は数年間、熱帯雨林で昆虫を研究してきた。"),
    "had spent": ("使っていた、過ごしていた", "助動詞句", "By noon, the visitors had spent three hours inside the museum.", "正午までに、訪問者たちは博物館の中で3時間過ごしていた。"),
    "why": ("なぜ、理由", "副詞", "Nobody understood why the machine stopped during the test.", "試験中に機械が止まった理由を誰も理解しなかった。"),
    "since": ("〜以来、〜なので", "接続詞", "Since the road was closed, we took a longer route home.", "道路が閉鎖されていたので、私たちは家へ長い道を通った。"),
    "how": ("どのように", "副詞", "The manual explains how the dishwasher should be repaired safely.", "説明書は食器洗い機を安全に修理する方法を説明している。"),
    "what": ("何、〜すること", "代名詞", "Please tell me what caused the sudden change in temperature.", "急な気温の変化を引き起こしたものを教えてください。"),
    "will not have": ("持っていないことになるだろう", "助動詞句", "By tomorrow, the store will not have any fresh bread left.", "明日までには、その店には新鮮なパンが残っていないだろう。"),
    "would not have": ("持っていなかっただろう", "助動詞句", "Without your advice, I would not have made the right decision.", "あなたの助言がなければ、私は正しい決定をしていなかっただろう。"),
    "should not have": ("〜すべきではなかった", "助動詞句", "You should not have left the medicine near the young child.", "幼い子どもの近くに薬を置くべきではなかった。"),
    "must not have": ("〜したはずがない、〜しなかったに違いない", "助動詞句", "The lights are off, so they must not have arrived home yet.", "明かりが消えているので、彼らはまだ帰宅していないに違いない。"),
}


CORE_IMAGES = {
    "similar to": {"chain": [{"term": "similar", "gloss": "似た"}, {"term": "to", "gloss": "対象へ向けて"}, {"gloss": "〜に似て"}]},
    "bound for": {"chain": [{"term": "bound", "gloss": "向かうことが決まった"}, {"term": "for", "gloss": "目的地へ向けて"}, {"gloss": "〜行きの"}]},
    "typical of": {"chain": [{"term": "typical", "gloss": "典型的な"}, {"term": "of", "gloss": "対象について"}, {"gloss": "〜に典型的な"}]},
    "engaged in": {"chain": [{"term": "engaged", "gloss": "関わっている"}, {"term": "in", "gloss": "中に入り込んで"}, {"gloss": "〜に従事して"}]},
    "in person": {"chain": [{"term": "in", "gloss": "状態の中に"}, {"term": "person", "gloss": "本人"}, {"gloss": "本人が直接"}]},
    "at present": {"chain": [{"term": "at", "gloss": "ある時点で"}, {"term": "present", "gloss": "現在"}, {"gloss": "現在は"}]},
    "in writing": {"chain": [{"term": "in", "gloss": "状態の中に"}, {"term": "writing", "gloss": "書かれたもの"}, {"gloss": "書面で"}]},
    "on hand": {"chain": [{"term": "on", "gloss": "接して"}, {"term": "hand", "gloss": "手元"}, {"gloss": "手元に、用意して"}]},
    "now that": {"chain": [{"term": "now", "gloss": "今"}, {"term": "that", "gloss": "そのことを受けて"}, {"gloss": "今や〜なので"}]},
    "as if": {"chain": [{"term": "as", "gloss": "同じように"}, {"term": "if", "gloss": "仮の条件として"}, {"gloss": "まるで〜のように"}]},
    "in case": {"chain": [{"term": "in", "gloss": "中に"}, {"term": "case", "gloss": "場合"}, {"gloss": "〜の場合に備えて"}]},
    "every time": {"chain": [{"term": "every", "gloss": "すべての"}, {"term": "time", "gloss": "時"}, {"gloss": "〜するたびに"}]},
    "social issues": {"chain": [{"term": "social", "gloss": "社会の"}, {"term": "issues", "gloss": "問題"}, {"gloss": "社会問題"}]},
    "new beginnings": {"chain": [{"term": "new", "gloss": "新しい"}, {"term": "beginnings", "gloss": "始まり"}, {"gloss": "新しい始まり"}]},
    "shared values": {"chain": [{"term": "shared", "gloss": "共有された"}, {"term": "values", "gloss": "価値観"}, {"gloss": "共有する価値観"}]},
    "second thoughts": {"chain": [{"term": "second", "gloss": "二度目の"}, {"term": "thoughts", "gloss": "考え"}, {"gloss": "考え直し、迷い"}]},
    "having spent": {"chain": [{"term": "having", "gloss": "経験・完了を持って"}, {"term": "spent", "gloss": "使った"}, {"gloss": "使ったこと"}]},
    "has spent": {"chain": [{"term": "has", "gloss": "現在まで続いて"}, {"term": "spent", "gloss": "使った"}, {"gloss": "使ってきた"}]},
    "had spent": {"chain": [{"term": "had", "gloss": "過去の時点までに"}, {"term": "spent", "gloss": "使った"}, {"gloss": "その時までに使っていた"}]},
    "will not have": {"chain": [{"term": "will", "gloss": "未来を示して"}, {"term": "have", "gloss": "持つ"}, {"gloss": "未来に持っていないことになる"}]},
    "would not have": {"chain": [{"term": "would", "gloss": "仮定の結果を示して"}, {"term": "have", "gloss": "持つ"}, {"gloss": "持っていなかっただろう"}]},
    "should not have": {"chain": [{"term": "should", "gloss": "望ましさを示して"}, {"term": "have", "gloss": "持つ・する"}, {"gloss": "〜すべきではなかった"}]},
    "must not have": {"chain": [{"term": "must", "gloss": "強い判断を示して"}, {"term": "have", "gloss": "持つ・する"}, {"gloss": "〜したはずがない"}]},
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 20:
        raise ValueError("2級模試第4回は20問である必要があります")
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
        "source": "ユーザー提供のChapter 3 模擬テスト第4回原稿を基に構造化。訳・例文・語句情報は学習用に作成",
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
    write_json(DATA_DIR / "vocab_2_mock-4.json", vocab)
    write_json(DATA_DIR / "questions_2_mock-4.json", questions)
    print("eiken2 mock-4: 20 questions / 80 items (57 words, 23 idioms)")


if __name__ == "__main__":
    main()
