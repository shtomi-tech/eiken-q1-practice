"""準2級の自作模試第3回をQ1形式のJSONへ出力する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-3"


QUESTIONS = [
    {
        "stem": "The island's old (   ) sent a bright signal to ships that were approaching the rocky coast after sunset.",
        "choices": ["museum", "harbor", "lighthouse", "shore"],
        "answerIndex": 2,
        "translation": "その島の古い灯台は、日没後に岩の多い海岸へ近づく船に明るい信号を送った。",
    },
    {
        "stem": "A: Why are so many students in the gym? B: The school is holding a (   ) to collect money for the new library, and local shops donated prizes.",
        "choices": ["volunteer", "donation", "charity", "fundraiser"],
        "answerIndex": 3,
        "translation": "A：どうして体育館にそんなにたくさんの生徒がいるの？ B：新しい図書館のためのお金を集める募金活動を学校が開いていて、地元の店が賞品を寄付したんだ。",
    },
    {
        "stem": "Could you send me the (   ) for that vegetable soup? I want to know which herbs and spices you used yesterday.",
        "choices": ["recipe", "flavor", "plate", "oven"],
        "answerIndex": 0,
        "translation": "あの野菜スープのレシピを送ってくれますか。昨日どのハーブと香辛料を使ったのか知りたいです。",
    },
    {
        "stem": "A: Who is responsible for fixing the broken heater? B: The (   ) promised to visit this afternoon, so the tenants should stay home.",
        "choices": ["apartment", "landlord", "tourist", "elevator"],
        "answerIndex": 1,
        "translation": "A：壊れた暖房器具を直す責任があるのは誰？ B：大家が今日の午後に来ると約束したから、入居者は家にいたほうがいいよ。",
    },
    {
        "stem": "Traffic moved slowly because a delivery truck stopped in the middle of the (   ), blocking cars arriving from four directions outside the station.",
        "choices": ["bridge", "park", "intersection", "sidewalk"],
        "answerIndex": 2,
        "translation": "駅の外で、配達トラックが交差点の中央に止まり、四方向から来る車をふさいだため、交通の流れが遅くなった。",
    },
    {
        "stem": "The village was so (   ) that we could hear birds and running water from our room all night.",
        "choices": ["ancient", "modern", "dangerous", "peaceful"],
        "answerIndex": 3,
        "translation": "その村はとても穏やかだったので、私たちは一晩中、部屋から鳥の声と流れる水の音を聞くことができた。",
    },
    {
        "stem": "A: Was the new bus route easy to use? B: Yes, it was very (   ) because the stop is beside our apartment.",
        "choices": ["convenient", "comfortable", "surprising", "necessary"],
        "answerIndex": 0,
        "translation": "A：新しいバス路線は使いやすかった？ B：うん、停留所が私たちのアパートの隣だから、とても便利だったよ。",
    },
    {
        "stem": "After the final customer left, the shop looked completely (   ) from the street, so the workers locked the doors and counted the money.",
        "choices": ["proud", "empty", "gentle", "bright"],
        "answerIndex": 1,
        "translation": "最後の客が出ていった後、外から見ると店は完全に空に見えたので、従業員たちはドアを閉めてお金を数えた。",
    },
    {
        "stem": "During the walk, we used a narrow footbridge to (   ) the river and reach the village before sunset.",
        "choices": ["discover", "invite", "cross", "follow"],
        "answerIndex": 2,
        "translation": "散歩の途中、日没前に村へ着くため、私たちは狭い歩道橋を使って川を渡った。",
    },
    {
        "stem": "A: What should we do with these chairs? B: Let's (   ) them in a circle before the guest speaker arrives, leaving space near the door.",
        "choices": ["improve", "solve", "join", "arrange"],
        "answerIndex": 3,
        "translation": "A：この椅子をどうしようか？ B：ゲスト講演者が到着する前に、ドアの近くを空けて椅子を円形に並べよう。",
    },
    {
        "stem": "A: What did the students need to create for the festival? B: They had to (   ) an original song for the closing ceremony.",
        "choices": ["come up with", "bring up", "catch up with", "put up with"],
        "answerIndex": 0,
        "translation": "A：生徒たちは祭りのために何を作る必要があったの？ B：閉会式のためにオリジナル曲を考え出さなければならなかった。",
    },
    {
        "stem": "Before the workshop began, the organizer had to (   ) name tags to every participant, so nobody had to ask for one.",
        "choices": ["clean up", "hand out", "check out", "turn out"],
        "answerIndex": 1,
        "translation": "ワークショップが始まる前に、主催者は参加者全員に名札を配らなければならなかったので、誰も名札をくださいと頼む必要がなかった。",
    },
    {
        "stem": "The hikers changed their route (   ) the official severe-weather warning and the strong wind near the trail.",
        "choices": ["in the absence of", "on the point of", "in view of", "toward the edge of"],
        "answerIndex": 2,
        "translation": "公式の悪天候警報と道の近くの強風を考慮して、ハイカーたちはルートを変更した。",
    },
    {
        "stem": "A: Why does the library stay open later this month? B: It changed the hours (   ) many students, who had formally asked for a quiet place to study.",
        "choices": ["as a result of", "in relation to", "in contrast to", "at the request of"],
        "answerIndex": 3,
        "translation": "A：どうして今月は図書館が遅くまで開いているの？ B：静かに勉強できる場所を求めた多くの生徒の要望に応じて、開館時間を変えたんだ。",
    },
    {
        "stem": "The store gave the customer a new phone (   ) the damaged one after checking the receipt and testing the replacement.",
        "choices": ["in exchange for", "with the permission of", "under the influence of", "at the invitation of"],
        "answerIndex": 0,
        "translation": "店はレシートを確認し交換品を試した後、壊れた電話と引き換えに客へ新しい電話を渡した。",
    },
]


DETAILS = {
    "museum": ("博物館", "名詞", "The museum displays maps and photographs from the island's history.", "その博物館は島の歴史に関する地図や写真を展示している。"),
    "harbor": ("港", "名詞", "Fishing boats returned to the harbor before the storm arrived.", "嵐が来る前に漁船は港へ戻った。"),
    "lighthouse": ("灯台", "名詞", "The lighthouse sent a bright signal across the dark sea.", "灯台は暗い海の向こうへ明るい信号を送った。"),
    "shore": ("岸、海岸", "名詞", "We walked along the shore and collected smooth pieces of glass.", "私たちは海岸を歩き、滑らかなガラス片を集めた。"),
    "volunteer": ("ボランティア、志願者", "名詞", "Each volunteer received gloves before helping at the community garden.", "各ボランティアは地域の共同菜園を手伝う前に手袋を受け取った。"),
    "donation": ("寄付", "名詞", "Her donation bought warm blankets for families at the shelter.", "彼女の寄付で避難所の家族に暖かい毛布を買った。"),
    "charity": ("慈善団体、慈善", "名詞", "The charity provides free meals to children during the summer.", "その慈善団体は夏の間、子どもたちに無料の食事を提供する。"),
    "fundraiser": ("募金活動、資金集めの催し", "名詞", "The student council organized a fundraiser for the new library.", "生徒会は新しい図書館のための募金活動を企画した。"),
    "recipe": ("レシピ、調理法", "名詞", "This recipe uses tomatoes, onions, and herbs from our garden.", "このレシピでは庭で採れたトマト、玉ねぎ、ハーブを使う。"),
    "flavor": ("味、風味", "名詞", "The lemon gives the soup a fresh flavor without much salt.", "レモンは、塩をあまり使わずにスープにさわやかな風味を加える。"),
    "plate": ("皿", "名詞", "Please put the clean plate beside the bowl on the table.", "きれいな皿をテーブルのボウルの横に置いてください。"),
    "oven": ("オーブン", "名詞", "The baker checked the oven before putting in the bread.", "パン職人はパンを入れる前にオーブンを確認した。"),
    "landlord": ("家主、大家", "名詞", "The landlord promised to repair the heater before winter.", "大家は冬になる前に暖房器具を修理すると約束した。"),
    "tourist": ("観光客", "名詞", "The tourist bought a guidebook before exploring the old town.", "その観光客は古い町を見て回る前に案内書を買った。"),
    "apartment": ("アパート、マンションの部屋", "名詞", "Their apartment has a small balcony facing the river.", "彼らのアパートには川に面した小さなバルコニーがある。"),
    "elevator": ("エレベーター", "名詞", "The elevator stopped at every floor during the morning rush.", "そのエレベーターは朝のラッシュ時にすべての階で止まった。"),
    "park": ("公園", "名詞", "Families gathered in the park for a community sports day.", "地域のスポーツデーのために家族連れが公園に集まった。"),
    "bridge": ("橋", "名詞", "The wooden bridge crosses a stream behind the village.", "その木の橋は村の裏手にある小川に架かっている。"),
    "intersection": ("交差点", "名詞", "The police officer stood near the intersection during the parade.", "パレードの間、警察官は交差点の近くに立っていた。"),
    "sidewalk": ("歩道", "名詞", "Please keep bicycles off the sidewalk outside the school.", "学校の外の歩道に自転車を置かないでください。"),
    "ancient": ("古代の、非常に古い", "形容詞", "The museum displays ancient tools used by farmers long ago.", "その博物館は昔の農民が使った古代の道具を展示している。"),
    "modern": ("現代的な", "形容詞", "This modern library has quiet rooms and many computers.", "この現代的な図書館には静かな部屋と多くのコンピューターがある。"),
    "peaceful": ("平和な、穏やかな", "形容詞", "The village was peaceful after the visitors returned home.", "訪問者たちが家へ帰った後、村は穏やかだった。"),
    "dangerous": ("危険な", "形容詞", "The river becomes dangerous after several hours of heavy rain.", "数時間大雨が降ると、その川は危険になる。"),
    "comfortable": ("快適な", "形容詞", "These comfortable shoes are suitable for a long walk.", "この快適な靴は長い散歩に向いている。"),
    "convenient": ("便利な", "形容詞", "The convenient bus stop is only two minutes from our house.", "便利なバス停は私たちの家からわずか2分のところにある。"),
    "surprising": ("驚くべき、意外な", "形容詞", "It was surprising to see snow during the warm spring festival.", "暖かい春祭りの間に雪を見たのは意外だった。"),
    "necessary": ("必要な", "形容詞", "A passport is necessary for travelers crossing the border.", "国境を越える旅行者にはパスポートが必要だ。"),
    "proud": ("誇りに思う、誇らしげな", "形容詞", "The proud parents smiled when their daughter received the school award.", "娘が学校の賞を受け取ったとき、誇らしげな両親はほほえんだ。"),
    "empty": ("空の、誰もいない", "形容詞", "The classroom was empty after the final bell rang.", "最後のベルが鳴った後、教室は空だった。"),
    "gentle": ("穏やかな、優しい", "形容詞", "The gentle dog waited quietly beside the young child.", "その穏やかな犬は幼い子どものそばで静かに待った。"),
    "bright": ("明るい、輝く", "形容詞", "A bright lamp made the narrow hallway easier to see.", "明るいランプのおかげで狭い廊下が見やすくなった。"),
    "discover": ("発見する", "動詞", "We hope to discover a quiet beach during our island trip.", "私たちは島への旅行中に静かな浜辺を発見したい。"),
    "invite": ("招待する", "動詞", "The club will invite local artists to speak with students.", "そのクラブは地元の芸術家を招いて生徒たちと話してもらう。"),
    "follow": ("ついて行く、従う", "動詞", "Please follow the blue signs to reach the hospital entrance.", "病院の入口へ行くには青い標識に従ってください。"),
    "cross": ("横切る、渡る", "動詞", "Use the footbridge to cross the river before sunset.", "日没前に川を渡るには歩道橋を使ってください。"),
    "improve": ("改善する、向上させる", "動詞", "Regular exercise can improve your health and help you sleep better.", "定期的な運動は健康を改善し、よりよく眠るのに役立つ。"),
    "solve": ("解決する", "動詞", "Working together helped the children solve the difficult puzzle.", "一緒に取り組むことで、子どもたちは難しいパズルを解くことができた。"),
    "arrange": ("整える、並べる、手配する", "動詞", "We need to arrange the chairs before the meeting begins.", "会議が始まる前に、私たちは椅子を並べる必要がある。"),
    "join": ("参加する、加わる", "動詞", "Would you like to join our team for the weekend project?", "週末のプロジェクトで私たちのチームに加わりませんか。"),
    "come up with": ("〜を考え出す", "句動詞", "Our team asked us to come up with a simple plan for the weekend clean-up.", "私たちのチームは、週末の清掃活動のために簡単な計画を考えるよう私たちに頼んだ。"),
    "bring up": ("話題に出す、育てる", "句動詞", "She decided to bring up the safety problem at the next meeting.", "彼女は次の会議で安全上の問題を話題に出すことにした。"),
    "catch up with": ("〜に追いつく", "句動詞", "After missing a week of class, Ken worked hard to catch up with his classmates.", "1週間授業を休んだ後、ケンはクラスメートに追いつくため一生懸命勉強した。"),
    "put up with": ("〜を我慢する", "句動詞", "Our neighbors put up with the noise while the community hall was repaired.", "公民館が修理されている間、近所の人たちはその騒音を我慢した。"),
    "hand out": ("〜を配る", "句動詞", "The organizer will hand out name tags before the workshop begins.", "主催者はワークショップが始まる前に名札を配る。"),
    "clean up": ("〜を掃除する、片づける", "句動詞", "The volunteers will clean up the community hall after the evening event.", "ボランティアたちは夜の行事の後、公民館を掃除する。"),
    "check out": ("〜を調べる、確認する", "句動詞", "Please check out these name tags before you give them to visitors.", "来訪者に渡す前に、これらの名札を確認してください。"),
    "turn out": ("〜を作り出す、判明する", "句動詞", "The small workshop can turn out hundreds of name tags in a day.", "その小さな作業場は1日に何百枚もの名札を作ることができる。"),
    "in the absence of": ("〜がない場合に、〜がない状態で", "前置詞句", "In the absence of clear directions, the hikers stayed near the camp.", "明確な指示がないので、ハイカーたちはキャンプの近くにとどまった。"),
    "on the point of": ("まさに〜しようとして", "前置詞句", "I was on the point of leaving when the phone rang.", "電話が鳴ったとき、私はまさに出発しようとしていた。"),
    "in view of": ("〜を考慮して、〜のために", "前置詞句", "The hikers turned back in view of the dark clouds.", "暗い雲を考慮して、ハイカーたちは引き返した。"),
    "toward the edge of": ("〜の端の方向へ", "前置詞句", "The child carefully walked toward the edge of the shallow pond.", "その子どもは浅い池の端の方向へ注意深く歩いた。"),
    "as a result of": ("〜の結果として、〜のために", "前置詞句", "The match was canceled as a result of heavy rain.", "大雨の結果、試合は中止された。"),
    "in relation to": ("〜に関して、〜との関係で", "前置詞句", "The teacher explained the rule in relation to the new project.", "先生は新しいプロジェクトとの関係でその規則を説明した。"),
    "in contrast to": ("〜と対照的に", "前置詞句", "In contrast to last year, this summer has been unusually cool.", "昨年とは対照的に、今年の夏は珍しく涼しい。"),
    "at the request of": ("〜の要請で", "前置詞句", "The library extended its hours at the request of many students.", "図書館は多くの生徒の要請で開館時間を延長した。"),
    "with the permission of": ("〜の許可を得て", "前置詞句", "The class used the hall with the permission of the principal.", "クラスは校長の許可を得てホールを使った。"),
    "under the influence of": ("〜の影響下で、〜に酔って", "前置詞句", "The driver was arrested under the influence of alcohol.", "その運転手は飲酒運転で逮捕された。"),
    "in exchange for": ("〜と引き換えに", "前置詞句", "The store gave her a new phone in exchange for the damaged one.", "店は壊れた電話と引き換えに彼女へ新しい電話を渡した。"),
    "at the invitation of": ("〜の招待で", "前置詞句", "We attended the ceremony at the invitation of the mayor.", "私たちは市長の招待で式典に出席した。"),
}


ETYMOLOGY = {
    "museum": "ギリシャ語 Mouseion「ムーサの神殿」。芸術や資料を集めて展示する場所。",
    "harbor": "古英語 herebeorg「軍の避難所」。船が安全に休める場所。",
    "lighthouse": "light（光）+ house（建物）。船へ光を送る建物。",
    "shore": "古英語 scor「海岸、岸」。水と陸の境目。",
    "volunteer": "ラテン語 voluntarius「自発的な」。自分から申し出る人。",
    "donation": "donate（与える）+ -ion。与えられた金品や行為。",
    "charity": "ラテン語 caritas「愛、親切」。人を助ける慈善活動。",
    "fundraiser": "fund（資金）+ raise（集める人・催し）。資金を集める活動。",
    "recipe": "ラテン語 recipe「受け取れ、取りなさい」。調理の指示書の冒頭語。",
    "flavor": "ラテン語 flare「香りを放つ」。食べ物の味や風味。",
    "plate": "フランス語 plate「平らな」。平たい食器。",
    "oven": "ラテン語 ofen「かまど、オーブン」。熱で食物を焼く設備。",
    "landlord": "land（土地）+ lord（主人）。土地や建物を貸す所有者。",
    "tourist": "tour（旅行、巡回）+ -ist。観光や旅行をする人。",
    "apartment": "ラテン語 partire「分ける」から。分けられた一つの住居。",
    "elevator": "elevate（持ち上げる）+ -or。人や物を上下させる装置。",
    "park": "ラテン語 parricus「囲われた場所」。人が休んだり遊んだりする場所。",
    "bridge": "古英語 brycg。川や道の上に渡した構造物。",
    "intersection": "inter-（間で）+ sect（切る）。道が切り合う場所。",
    "sidewalk": "side（側）+ walk（歩く場所）。道路の側の歩行用部分。",
    "ancient": "ラテン語 ante「前に」+ -cient。遠い過去のもの。",
    "modern": "ラテン語 modo「今、たった今」。現在の時代に属する。",
    "peaceful": "peace（平和）+ -ful（満ちた）。争いがなく穏やかな状態。",
    "dangerous": "danger（危険）+ -ous。危険を含む状態。",
    "comfortable": "comfort（安楽）+ -able。心地よく過ごせる。",
    "convenient": "ラテン語 convenire「一緒に来る、都合が合う」。使いやすく都合がよい。",
    "surprising": "surprise（驚かせる）+ -ing。予想を越えて驚かせる性質。",
    "necessary": "ラテン語 necessarius「避けられない」。なくてはならない。",
    "proud": "古フランス語 prud「価値のある、誇り高い」。誇りを感じる。",
    "empty": "古フランス語 emptier「空にする」。中身がない状態。",
    "gentle": "ラテン語 gentilis「同じ一族の」。身分のよさから穏やかで優しい意味へ。",
    "bright": "古英語 beorht「輝く、明るい」。光を放つ状態。",
    "discover": "dis-（覆いを取って）+ cover（覆う）。隠れていたものを見つける。",
    "invite": "ラテン語 invitare「招く」。人に来るよう声をかける。",
    "follow": "古英語 folgian「後について行く」。後から同じ道を進む。",
    "cross": "古英語 cros「十字架」。線を横切る動きから「渡る」。",
    "improve": "古フランス語 en + pro「よりよく」。状態をよりよくする。",
    "solve": "ラテン語 solvere「ほどく、解く」。問題の結び目をほどく。",
    "arrange": "フランス語 arranger「整える」。物を適切な順序や場所に置く。",
    "join": "古フランス語 joindre、ラテン語 jungere「つなぐ」。人や物を一つにつなぐ。",
    "come up with": "come（来る）+ up（上へ）+ with（伴って）。考えを持ち上げて「考え出す」。",
    "bring up": "bring（持ってくる）+ up（上へ）。話題を表へ持ち上げて「話題に出す」。",
    "catch up with": "catch（つかまえる）+ up（追いついて）+ with（対象に）。同じ位置まで追いつく。",
    "put up with": "put（置く）+ up（内側へ保って）+ with（伴って）。不快なことを抱えて「我慢する」。",
    "hand out": "hand（手渡す）+ out（外へ）。手元から外へ渡して「配る」。",
    "clean up": "clean（きれいにする）+ up（整えて）。散らかった状態を片づける。",
    "check out": "check（確認する）+ out（外へ取り出して）。対象を取り出して「調べる」。",
    "turn out": "turn（向きを変える）+ out（外へ）。作り出して外へ出し、「生産する」。",
    "in the absence of": "absence（不在、欠如）の中に in。何かがない状態で。",
    "on the point of": "point（点、時点）の上に on。まさにその時点にある。",
    "in view of": "view（見えること、考慮）に in。見えている事情を考慮して。",
    "toward the edge of": "toward（〜の方向へ）+ edge（端）。端へ向かう位置や動き。",
    "as a result of": "result（結果）を理由として示す表現。結果として起きたこと。",
    "in relation to": "relation（関係）の中で in。別の対象との関係を示す。",
    "in contrast to": "contrast（対照）の中で in。別のものとの違いを示す。",
    "at the request of": "request（要請）をきっかけにする at。要請を受けて。",
    "with the permission of": "permission（許可）を伴って with。許可を得た状態。",
    "under the influence of": "influence（影響）の下に under。影響を受けている状態。",
    "in exchange for": "exchange（交換）の中で in。別の物と交換する条件。",
    "at the invitation of": "invitation（招待）をきっかけにする at。招待を受けて。",
}


CORE_IMAGES = {
    "come up with": {"particle": "up", "particleSense": "fabricate", "chain": [{"term": "come", "gloss": "来る"}, {"term": "up", "gloss": "上へ作り上げて"}, {"gloss": "案を考え出して形にする"}]},
    "bring up": {"particle": "up", "particleSense": "raise", "chain": [{"term": "bring", "gloss": "持ってくる"}, {"term": "up", "gloss": "上へ持ち上げて"}, {"gloss": "話題を表に出す"}]},
    "catch up with": {"particle": "up", "particleSense": "approach", "chain": [{"term": "catch", "gloss": "つかまえる"}, {"term": "up", "gloss": "追いついて"}, {"gloss": "同じ位置まで追いつく"}]},
    "put up with": {"particle": "up", "particleSense": "contain", "chain": [{"term": "put", "gloss": "置く"}, {"term": "up", "gloss": "内側へ保って"}, {"gloss": "不快なことを抱えて我慢する"}]},
    "hand out": {"particle": "out", "particleSense": "delegate", "siblings": [{"phrase": "contract out", "gloss": "外注する"}, {"phrase": "send out", "gloss": "外へ出す"}, {"phrase": "parcel out", "gloss": "分配する"}], "chain": [{"term": "hand", "gloss": "手渡す"}, {"term": "out", "gloss": "外へ"}, {"gloss": "手元から人へ配る"}]},
    "clean up": {"particle": "up", "particleSense": "settle", "chain": [{"term": "clean", "gloss": "きれいにする"}, {"term": "up", "gloss": "整えて"}, {"gloss": "散らかった場所を片づける"}]},
    "check out": {"particle": "out", "particleSense": "reserve", "chain": [{"term": "check", "gloss": "確認する"}, {"term": "out", "gloss": "選び出して"}, {"gloss": "対象を選び出して確かめる"}]},
    "turn out": {"particle": "out", "particleSense": "produce", "siblings": [{"phrase": "spit out", "gloss": "吐き出す"}, {"phrase": "roll out", "gloss": "新製品を出す"}, {"phrase": "print out", "gloss": "印刷する"}], "chain": [{"term": "turn", "gloss": "向きを変える"}, {"term": "out", "gloss": "外へ"}, {"gloss": "作り出して外へ出す"}]},
    "in the absence of": {"chain": [{"term": "absence", "gloss": "不在、欠如"}, {"term": "of", "gloss": "〜がない状態で"}, {"gloss": "〜がない場合に、〜がない状態で"}]},
    "on the point of": {"chain": [{"term": "point", "gloss": "一点、時点"}, {"term": "of", "gloss": "〜に向けて"}, {"gloss": "まさに〜しようとして"}]},
    "in view of": {"chain": [{"term": "view", "gloss": "見えている事情"}, {"term": "of", "gloss": "〜を考慮して"}, {"gloss": "〜を考慮して、〜のために"}]},
    "toward the edge of": {"chain": [{"term": "toward", "gloss": "〜の方向へ"}, {"term": "edge", "gloss": "端"}, {"gloss": "〜の端の方向へ"}]},
    "as a result of": {"chain": [{"term": "result", "gloss": "結果"}, {"term": "of", "gloss": "〜から生じて"}, {"gloss": "〜の結果として、〜のために"}]},
    "in relation to": {"chain": [{"term": "relation", "gloss": "関係"}, {"term": "to", "gloss": "〜へ向けて"}, {"gloss": "〜に関して、〜との関係で"}]},
    "in contrast to": {"chain": [{"term": "contrast", "gloss": "対照"}, {"term": "to", "gloss": "〜と比べて"}, {"gloss": "〜と対照的に"}]},
    "at the request of": {"chain": [{"term": "request", "gloss": "要請"}, {"term": "of", "gloss": "〜からの"}, {"gloss": "〜の要請で"}]},
    "with the permission of": {"chain": [{"term": "permission", "gloss": "許可"}, {"term": "of", "gloss": "〜からの"}, {"gloss": "〜の許可を得て"}]},
    "under the influence of": {"chain": [{"term": "influence", "gloss": "影響"}, {"term": "of", "gloss": "〜による"}, {"gloss": "〜の影響下で、〜に酔って"}]},
    "in exchange for": {"chain": [{"term": "exchange", "gloss": "交換"}, {"term": "for", "gloss": "〜と引き替えに"}, {"gloss": "〜と引き換えに"}]},
    "at the invitation of": {"chain": [{"term": "invitation", "gloss": "招待"}, {"term": "of", "gloss": "〜からの"}, {"gloss": "〜の招待で"}]},
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 15:
        raise ValueError("準2級模試第3回は15問である必要があります")
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
    write_json(DATA_DIR / "vocab_p2_mock-3.json", vocab)
    write_json(DATA_DIR / "questions_p2_mock-3.json", questions)
    print("p2 mock-3: 15 questions / 60 items (40 words, 20 idioms)")


if __name__ == "__main__":
    main()
