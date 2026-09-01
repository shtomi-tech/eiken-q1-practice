"""ユーザー提供画像の英検1級模試を、第6回のQ1形式へ構造化する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-6"
BLANK_RE = re.compile(r"\(\s+\)")


QUESTIONS = [
    {
        "stem": "Politicians have been (   ) about the budget for months, but it looks like they have finally reached an agreement.",
        "choices": ["billowing", "wrangling", "embarking", "rambling"],
        "answerIndex": 1,
        "translation": "政治家たちは何か月も予算について論争してきたが、ようやく合意に達したようだ。",
    },
    {
        "stem": "Ever since she was a small child, Emma has had a (   ) for botany. While her friends were playing with toys indoors, she much preferred to examine leaves and plants in the garden.",
        "choices": ["predilection", "depreciation", "countenance", "resurgence"],
        "answerIndex": 0,
        "translation": "エマは幼い頃から植物学を特に好んでいた。友達が屋内でおもちゃで遊んでいる間も、彼女は庭で葉や植物を観察するほうをずっと好んでいた。",
    },
    {
        "stem": "Due to the large number of visa applications they have been receiving, the immigration office is trying to (   ) processing times. They are hoping to speed them up by at least 20 percent.",
        "choices": ["accelerate", "soothe", "mumble", "dodge"],
        "answerIndex": 0,
        "translation": "大量のビザ申請を受け付けているため、入国管理局は処理時間を短縮しようとしている。少なくとも20パーセント速めたいと考えている。",
    },
    {
        "stem": "Mark's doctor told him that it was his constant overeating that had (   ) his stomach.",
        "choices": ["distended", "blared", "perused", "savored"],
        "answerIndex": 0,
        "translation": "マークの医師は、胃を膨張させたのは彼の絶え間ない過食だと伝えた。",
    },
    {
        "stem": "The number of female CEOs stood at around 18 percent last year. Although there is room for improvement, it is encouraging to see more women ascending to the upper (   ) of business management.",
        "choices": ["contours", "epitaphs", "strata", "amalgams"],
        "answerIndex": 2,
        "translation": "昨年、女性CEOの数は約18パーセントだった。改善の余地はあるものの、より多くの女性が経営の上層階級へ昇進しているのは心強いことだ。",
    },
    {
        "stem": "The young men were behaving in a very (   ) manner, shouting and cursing loudly. In the end, the restaurant manager had no choice but to ask them to leave.",
        "choices": ["uncouth", "decorous", "insular", "methodical"],
        "answerIndex": 0,
        "translation": "その若者たちは大声で叫び、悪態をつくなど、非常に無作法な態度を取っていた。結局、レストランの店長は彼らに出て行くよう頼むしかなかった。",
    },
    {
        "stem": "Vincent sighed (   ), wondering how he was ever going to explain why he had made such a stupid mistake to his boss.",
        "choices": ["mechanically", "lethally", "ruefully", "coarsely"],
        "answerIndex": 2,
        "translation": "ヴィンセントは、なぜあんな愚かなミスをしたのか上司にどう説明すればよいのか思い悩みながら、後悔の念を込めてため息をついた。",
    },
    {
        "stem": "After the lecture, students will be able to ask the guest speaker some questions. However, as we do not have much time, we'd like to request that you keep your questions short and (   ) to the main theme.",
        "choices": ["kindred", "germane", "seditious", "laudable"],
        "answerIndex": 1,
        "translation": "講義の後、学生は講演者にいくつか質問できます。ただし時間があまりないので、質問は短く、主題に関連したものにしてください。",
    },
    {
        "stem": "Around the time the boy crashed his bicycle, his mother had a sudden (   ) that her son had been involved in an accident of some kind.",
        "choices": ["emulation", "premonition", "naturalization", "persecution"],
        "answerIndex": 1,
        "translation": "その少年が自転車で事故を起こした頃、母親は息子が何らかの事故に巻き込まれたという突然の予感を覚えた。",
    },
    {
        "stem": "Ellen was trying to study for her chemistry test, but her little brother kept (   ) her, so it was impossible to concentrate.",
        "choices": ["fortifying", "amassing", "bestowing", "pestering"],
        "answerIndex": 3,
        "translation": "エレンは化学の試験勉強をしようとしていたが、弟がしつこく邪魔をし続けたので、集中できなかった。",
    },
    {
        "stem": "After graduating from cooking school, Crystal (   ) her skills at a local restaurant for several years. It was during this period that she really mastered the techniques the school had taught her.",
        "choices": ["shelved", "neglected", "sharpened", "evicted"],
        "answerIndex": 2,
        "translation": "料理学校を卒業した後、クリスタルは数年間、地元のレストランで腕を磨いた。この時期に、学校で習った技術を本当に身につけたのだ。",
    },
    {
        "stem": "It can be very difficult to get people to change their attitudes and ideas. This is especially so if their ideas have become deeply (   ) over many years.",
        "choices": ["obscure", "insatiable", "urbane", "entrenched"],
        "answerIndex": 3,
        "translation": "人々の態度や考えを変えさせるのはとても難しいことがある。長年にわたって考えが深く定着している場合は、特にそうである。",
    },
    {
        "stem": "At first, the teachers in the school dismissed the unusually low test scores as an (   ). However, it was later discovered that there had been a mistake in the electronic marking system.",
        "choices": ["indemnity", "anomaly", "epoch", "amnesty"],
        "answerIndex": 1,
        "translation": "最初、学校の教師たちは異常に低いテストの点数を例外的な事象だとして片づけた。しかし後に、電子採点システムにミスがあったことが分かった。",
    },
    {
        "stem": "Due to recent budget cuts, the public library system has had to (   ) purchasing of new books and CDs.",
        "choices": ["celebrate", "curtail", "chastise", "perambulate"],
        "answerIndex": 1,
        "translation": "最近の予算削減のため、公立図書館制度は新しい本やCDの購入を削減しなければならなかった。",
    },
    {
        "stem": "When visiting the temple, the visitors wore pants and shirts with long sleeves in (   ) to the local custom, which requires both men and women to dress conservatively.",
        "choices": ["deference", "ardor", "acuity", "candor"],
        "answerIndex": 0,
        "translation": "寺を訪れた際、訪問者たちは男女とも保守的な服装を求める地元の習慣に敬意を表し、ズボンと長袖のシャツを着た。",
    },
    {
        "stem": "It seems that the country is entering a new period of (   ). The current situation has been compared to the period following the Second World War when foods were rationed, and many goods were in short supply.",
        "choices": ["chauvinism", "austerity", "derision", "arrogance"],
        "answerIndex": 1,
        "translation": "その国は緊縮の新たな時代に入りつつあるようだ。現在の状況は、食料が配給され、多くの物資が不足していた第二次世界大戦後の時期と比較されている。",
    },
    {
        "stem": "Some of the students in Professor Power's class complained that many of the grades they received seemed to be (   ) and not in line with the official grading policies of the college.",
        "choices": ["arbitrary", "makeshift", "presumptuous", "sagacious"],
        "answerIndex": 0,
        "translation": "パワー教授の授業の学生の一部は、受け取った成績の多くが恣意的で、大学の公式な成績評価方針に沿っていないようだと不満を述べた。",
    },
    {
        "stem": "A: Did you hear that Glen and Mohammed have (   ) a plan to cycle across the whole country together?\nB: Yeah, I always wonder where they get those crazy ideas. They'll quit on the first day.",
        "choices": ["allayed", "hatched", "deformed", "sapped"],
        "answerIndex": 1,
        "translation": "A：グレンとモハメドが一緒に国全体を自転車で横断する計画を企てたって聞いた？\nB：ああ、いつもあの突拍子もない考えをどこから思いつくのか不思議に思うよ。初日にやめるだろうけどね。",
    },
    {
        "stem": "Before any operation, patients are asked to read and sign a (   ). This is to ensure that all patients understand both the benefits of the procedure as well as any possible complications that might occur.",
        "choices": ["waiver", "fortress", "faculty", "dissension"],
        "answerIndex": 0,
        "translation": "手術の前に、患者は書類を読み、権利放棄書に署名するよう求められる。これは、処置の利点と起こり得る合併症の両方をすべての患者が理解するようにするためである。",
    },
    {
        "stem": "A: What's Charlie like? It seems everyone has met him except me!\nB: He's really outgoing and (   ). He loves parties and meeting people.",
        "choices": ["gregarious", "insouciant", "sullen", "nomadic"],
        "answerIndex": 0,
        "translation": "A：チャーリーってどんな人？私以外はみんな彼に会ったことがあるみたい！\nB：彼は本当に社交的で、人付き合いが好きだよ。パーティーや人に会うのが大好きなんだ。",
    },
    {
        "stem": "Although he is well over 80, James's grandfather is still in (   ) health. In fact, he goes to the gym several times a week and takes his dog for daily walks near his home.",
        "choices": ["robust", "frail", "marginal", "ferocious"],
        "answerIndex": 0,
        "translation": "80歳を大きく超えているにもかかわらず、ジェームズの祖父は今も健やかな健康状態にある。実際、週に数回ジムへ行き、自宅の近くで毎日犬を散歩させている。",
    },
    {
        "stem": "A: I wish David wouldn't spend so much time with Adam. That boy's always in trouble, and I'm worried that his behavior will (   ) Charlie.\nB: I agree, but we can't choose Charlie's friends for him.",
        "choices": ["shy away from", "rub off on", "turn off", "make off with"],
        "answerIndex": 1,
        "translation": "A：デイビッドにはアダムとそんなに長く一緒にいてほしくないな。あの子はいつも問題を起こしているし、その行動がチャーリーにうつらないか心配だよ。\nB：同感だけど、チャーリーの友達を彼のために選ぶことはできないよ。",
    },
    {
        "stem": "Kelly felt so guilty about stealing the candy that she went back to the store to (   ). The store's owner said he would forgive her if she promised never to steal again.",
        "choices": ["hang around", "wait around", "poke around", "come clean"],
        "answerIndex": 3,
        "translation": "ケリーはキャンディーを盗んだことをとても申し訳なく思い、白状するため店に戻った。店主は、二度と盗まないと約束するなら許すと言った。",
    },
    {
        "stem": "Despite receiving a generous severance package when he lost his job, Carlos (   ) the money on gambling in just a few months.",
        "choices": ["reckoned on", "rooted for", "dashed down", "threw away"],
        "answerIndex": 3,
        "translation": "カルロスは失職した際に多額の退職金を受け取ったにもかかわらず、わずか数か月でそのお金をギャンブルに浪費した。",
    },
    {
        "stem": "During the seminar, the professor told his students to (   ) on the discussion at any time. He said they should not be afraid to give their opinions.",
        "choices": ["float around", "weigh in", "stack up", "squeak by"],
        "answerIndex": 1,
        "translation": "セミナー中、教授は学生たちにいつでも議論に意見を述べるよう伝えた。自分の意見を述べることを恐れてはいけないと言った。",
    },
]


DETAILS = {
    "billowing": ("（煙などが）渦巻きながら広がる", "動詞", "Billowing smoke obscured the mountain road after the fire.", "火事の後、渦巻く煙が山道を覆い隠した。"),
    "wrangling": ("議論する、交渉する", "動詞", "The committee spent the afternoon wrangling over the proposed budget.", "委員会は午後を提案された予算について議論して過ごした。"),
    "embarking": ("乗り出す、着手する", "動詞", "The crew was embarking on a long voyage across the Atlantic.", "乗組員たちは大西洋を横断する長い航海に乗り出そうとしていた。"),
    "rambling": ("とりとめのない", "動詞", "His rambling explanation left the committee unsure about the proposal.", "彼のとりとめのない説明で、委員会は提案について確信を持てなかった。"),
    "predilection": ("特に好む傾向", "名詞", "Her predilection for rare plants filled the apartment with greenery.", "珍しい植物を特に好む彼女の傾向で、アパートは緑に満ちていた。"),
    "depreciation": ("価値の下落、減価償却", "名詞", "Rapid depreciation reduced the car's resale value within two years.", "急速な減価償却によって、その車の再販価値は2年以内に下がった。"),
    "countenance": ("顔つき、表情；容認", "名詞", "His stern countenance frightened the children at first.", "彼の厳しい顔つきに、子どもたちは最初おびえた。"),
    "resurgence": ("復活、再興", "名詞", "The region has seen a resurgence of small independent bookstores.", "その地域では小規模な個人書店が再び盛んになっている。"),
    "accelerate": ("加速する、促進する", "動詞", "New software helped accelerate the processing of permit applications.", "新しいソフトウェアは許可申請の処理を速めるのに役立った。"),
    "soothe": ("なだめる、和らげる", "動詞", "A warm drink may soothe the child's sore throat before bed.", "温かい飲み物は就寝前に子どもの喉の痛みを和らげるかもしれない。"),
    "mumble": ("ぼそぼそ言う", "動詞", "He began to mumble an apology after realizing his mistake.", "彼は自分の間違いに気づいた後、謝罪をぼそぼそと言い始めた。"),
    "dodge": ("素早く避ける", "動詞", "The driver swerved to dodge a fallen branch on the road.", "運転手は道路に落ちた枝を避けるため、急にハンドルを切った。"),
    "distended": ("膨張した", "動詞", "The patient's abdomen appeared distended after the operation.", "手術後、患者の腹部は膨張しているように見えた。"),
    "blared": ("（音を）大音量で鳴らした", "動詞", "A warning siren blared across the harbor at midnight.", "警告サイレンが真夜中の港じゅうに大音量で鳴り響いた。"),
    "perused": ("熟読した、ざっと調べた", "動詞", "She perused the contract carefully before signing the final page.", "彼女は最後のページに署名する前に契約書を注意深く読んだ。"),
    "savored": ("味わった、満喫した", "動詞", "The hikers savored the meal after a long day outdoors.", "ハイカーたちは屋外で長い一日を過ごした後、食事を味わった。"),
    "contours": ("輪郭、等高線", "名詞", "The architect studied the contours of the hillside before drawing the plan.", "建築家は設計図を描く前に丘の斜面の輪郭を調べた。"),
    "epitaphs": ("墓碑銘", "名詞", "The historian photographed the epitaphs carved into the old cemetery stones.", "歴史家は古い墓地の石に刻まれた墓碑銘を写真に撮った。"),
    "strata": ("層、階層", "名詞", "Researchers compared the upper strata of the company's management structure.", "研究者たちはその会社の経営構造の上層階級を比較した。"),
    "amalgams": ("混合物、融合体", "名詞", "The sculptures are striking amalgams of metal, glass, and stone.", "その彫刻は金属、ガラス、石の印象的な融合体だ。"),
    "uncouth": ("無作法な", "形容詞", "His uncouth remarks embarrassed everyone at the formal dinner.", "彼の無作法な発言は正式な夕食会の全員を困らせた。"),
    "decorous": ("礼儀正しい、上品な", "形容詞", "The guests maintained a decorous silence during the memorial service.", "客たちは追悼式の間、礼儀正しく静かにしていた。"),
    "insular": ("島の；偏狭な、閉鎖的な", "形容詞", "The once-insular community now welcomes visitors from many countries.", "かつて閉鎖的だった地域社会は、今では多くの国からの訪問者を歓迎している。"),
    "methodical": ("几帳面な、手順を踏む", "形容詞", "Her methodical approach helped the team detect a tiny error.", "彼女の几帳面な取り組み方が、チームによる小さな誤りの発見に役立った。"),
    "mechanically": ("機械的に、無意識に", "副詞", "The tired worker mechanically repeated the same instructions all afternoon.", "疲れた作業員は午後じゅう同じ指示を機械的に繰り返した。"),
    "lethally": ("致死的に", "副詞", "The chemical is lethally toxic if it is swallowed in large amounts.", "その化学物質は大量に飲み込むと致死的な毒性を示す。"),
    "ruefully": ("後悔して、申し訳なさそうに", "副詞", "He smiled ruefully when the photograph revealed his mistake.", "写真によって自分のミスが明らかになると、彼は後悔したように笑った。"),
    "coarsely": ("粗野に、下品に", "副詞", "The comedian coarsely mocked the actor during the interview.", "そのコメディアンはインタビュー中に俳優を下品にからかった。"),
    "kindred": ("同類の、共通点のある", "形容詞", "The two researchers discovered kindred interests in historical linguistics.", "その2人の研究者は歴史言語学に共通の関心があることに気づいた。"),
    "germane": ("密接に関係のある", "形容詞", "Please include only evidence germane to the central question.", "中心となる問いに密接に関係する証拠だけを含めてください。"),
    "seditious": ("扇動的な、反政府的な", "形容詞", "The regime accused the journalist of publishing seditious material.", "政権はその記者が反政府的な資料を発表したと非難した。"),
    "laudable": ("称賛に値する", "形容詞", "The volunteers made a laudable effort to restore the neglected park.", "ボランティアたちは荒れた公園を復旧するため称賛に値する努力をした。"),
    "emulation": ("模倣、競争心", "名詞", "The younger athlete trained in emulation of her Olympic hero.", "若い選手はオリンピックの英雄を見習って練習した。"),
    "premonition": ("予感、虫の知らせ", "名詞", "A strange premonition kept him from boarding the late-night train.", "奇妙な予感が、彼を深夜の列車に乗ることから思いとどまらせた。"),
    "naturalization": ("帰化", "名詞", "Her naturalization ceremony took place at the courthouse in June.", "彼女の帰化式は6月に裁判所で行われた。"),
    "persecution": ("迫害", "名詞", "The family fled the country to escape religious persecution.", "その家族は宗教的迫害から逃れるため国を離れた。"),
    "fortifying": ("強化している", "動詞", "The hikers were fortifying the shelter before the storm arrived.", "ハイカーたちは嵐が来る前に避難所を強化していた。"),
    "amassing": ("蓄積している", "動詞", "The foundation is amassing funds for a new research center.", "その財団は新しい研究センターのための資金を蓄積している。"),
    "bestowing": ("授与している", "動詞", "The committee is bestowing the award on an outstanding teacher.", "委員会は優れた教師に賞を授与している。"),
    "pestering": ("しつこく悩ませている", "動詞", "The child kept pestering his father for another bedtime story.", "その子どもはもう一つ就寝前のお話をしてほしいと父親にしつこくせがみ続けた。"),
    "shelved": ("棚上げした、保留した", "動詞", "The curator shelved the damaged manuscripts until they could be restored.", "学芸員は損傷した写本を修復できるまで棚上げした。"),
    "neglected": ("怠った、顧みなかった", "動詞", "The curator neglected the fragile manuscripts for years, leaving them covered in dust.", "学芸員は壊れやすい写本を何年も顧みず、ほこりをかぶったままにした。"),
    "sharpened": ("磨きをかけた、研ぎ澄ました", "動詞", "Daily practice sharpened the pianist's technique before the competition.", "毎日の練習が大会前にそのピアニストの技術を磨いた。"),
    "evicted": ("立ち退かせた", "動詞", "The landlord evicted the tenants after months of unpaid rent.", "家主は何か月も家賃を払わなかった入居者を立ち退かせた。"),
    "obscure": ("不明瞭な、目立たない", "形容詞", "The obscure village rarely appeared on maps of the region.", "その人目につかない村は、その地域の地図にめったに載らなかった。"),
    "insatiable": ("飽くことを知らない", "形容詞", "The reporter had an insatiable curiosity about the remote expedition.", "その記者は遠隔地への探検について飽くことのない好奇心を持っていた。"),
    "urbane": ("洗練された、都会的な", "形容詞", "The urbane host made every guest feel comfortable at the reception.", "洗練された司会者は歓迎会ですべての客をくつろがせた。"),
    "entrenched": ("根深く定着した", "形容詞", "The entrenched policy survived several changes in leadership.", "その根深く定着した政策は、指導者が何度も変わっても残った。"),
    "indemnity": ("補償、賠償", "名詞", "The contract provides indemnity against losses caused by natural disasters.", "その契約は自然災害による損失への補償を定めている。"),
    "anomaly": ("異常、例外", "名詞", "The single low reading was treated as an anomaly in the experiment.", "1回だけ低かった測定値は、その実験における例外として扱われた。"),
    "epoch": ("時代", "名詞", "The invention of the printing press marked a new epoch in communication.", "印刷機の発明は、コミュニケーションにおける新たな時代の到来を示した。"),
    "amnesty": ("恩赦、大赦", "名詞", "The government offered amnesty to rebels who surrendered peacefully.", "政府は平和的に降伏した反乱者に恩赦を申し出た。"),
    "celebrate": ("祝う", "動詞", "The town gathered to celebrate the opening of the restored theater.", "町の人々は修復された劇場の開館を祝うため集まった。"),
    "curtail": ("削減する、短縮する", "動詞", "The agency had to curtail travel expenses during the financial crisis.", "その機関は金融危機の間、旅費を削減しなければならなかった。"),
    "chastise": ("厳しく叱る", "動詞", "The coach did not chastise the player for making an honest mistake.", "コーチは正直なミスをした選手を厳しく叱らなかった。"),
    "perambulate": ("歩き回る", "動詞", "Visitors may perambulate through the gardens after the guided tour.", "訪問者はガイドツアーの後、庭園を歩き回ってもよい。"),
    "deference": ("敬意、服従", "名詞", "The visitors lowered their voices in deference to local customs.", "訪問者たちは地元の習慣に敬意を表して声を落とした。"),
    "ardor": ("熱意", "名詞", "She pursued her scientific research with remarkable ardor.", "彼女は並外れた熱意をもって科学研究に取り組んだ。"),
    "acuity": ("鋭さ、（視力などの）明晰さ", "名詞", "The surgeon's visual acuity was tested before the delicate procedure.", "その外科医は繊細な処置の前に視力の鋭さを検査された。"),
    "candor": ("率直さ", "名詞", "His candor helped the committee understand the project's risks.", "彼の率直さは委員会が計画のリスクを理解する助けになった。"),
    "chauvinism": ("盲目的な愛国心、優越意識", "名詞", "The novel criticizes national chauvinism and its destructive consequences.", "その小説は盲目的な国家優越意識と、その破壊的な結果を批判している。"),
    "austerity": ("緊縮、質素さ", "名詞", "Years of austerity forced the city to close several libraries.", "何年もの緊縮政策によって、その市は複数の図書館を閉鎖せざるを得なかった。"),
    "derision": ("あざけり、嘲笑", "名詞", "The proposal was met with derision during the heated debate.", "その提案は白熱した議論の中で嘲笑を浴びた。"),
    "arrogance": ("傲慢さ", "名詞", "His arrogance prevented him from accepting useful advice.", "彼の傲慢さは、役に立つ助言を受け入れる妨げになった。"),
    "arbitrary": ("恣意的な、独断的な", "形容詞", "The judge rejected the arbitrary rule as unfair to applicants.", "裁判官は、その恣意的な規則は申請者に不公平だとして退けた。"),
    "makeshift": ("間に合わせの", "形容詞", "The rescue team built a makeshift bridge from wooden boards.", "救助隊は木の板で間に合わせの橋を作った。"),
    "presumptuous": ("出しゃばった、厚かましい", "形容詞", "It was presumptuous of him to speak for the entire committee.", "委員会全体を代表して話すとは、彼は出しゃばっていた。"),
    "sagacious": ("賢明な、思慮深い", "形容詞", "The sagacious leader listened carefully before making a difficult decision.", "賢明な指導者は難しい決断をする前に注意深く話を聞いた。"),
    "allayed": ("和らげた、鎮めた", "動詞", "The doctor allayed the patient's fears by explaining the treatment.", "医師は治療について説明して患者の不安を和らげた。"),
    "hatched": ("（計画を）企てた", "動詞", "The committee hatched a plan to improve access to public transit.", "委員会は公共交通機関へのアクセスを改善する計画を企てた。"),
    "deformed": ("変形した", "動詞", "The metal frame was deformed by the intense heat.", "金属の枠は激しい熱で変形した。"),
    "sapped": ("弱らせた、奪った", "動詞", "Months of uncertainty sapped the workers' confidence in the project.", "何か月もの不確実さが、作業員たちの計画への自信を奪った。"),
    "waiver": ("権利放棄書、免除", "名詞", "The athlete signed a waiver before joining the dangerous expedition.", "その選手は危険な探検に参加する前に権利放棄書へ署名した。"),
    "fortress": ("要塞", "名詞", "The ancient fortress overlooks the narrow entrance to the harbor.", "その古代の要塞は港の狭い入口を見下ろしている。"),
    "faculty": ("学部、教授陣", "名詞", "The university faculty approved the revised course requirements.", "大学の教授陣は改訂された履修要件を承認した。"),
    "dissension": ("意見の対立、内紛", "名詞", "Open dissension weakened the coalition during the election campaign.", "選挙運動中、公然とした意見の対立が連合を弱体化させた。"),
    "gregarious": ("社交的な", "形容詞", "Her gregarious nature made it easy for her to make friends.", "彼女の社交的な性格のおかげで、友達を作るのは簡単だった。"),
    "insouciant": ("無頓着な、のんきな", "形容詞", "His insouciant attitude annoyed colleagues who were working under pressure.", "プレッシャーの下で働いていた同僚たちは、彼の無頓着な態度にいら立った。"),
    "sullen": ("不機嫌な、むっつりした", "形容詞", "The sullen teenager refused to discuss the disagreement at dinner.", "その不機嫌な十代の若者は夕食時に意見の対立について話そうとしなかった。"),
    "nomadic": ("遊牧の、放浪する", "形容詞", "The nomadic community moves with its herds between seasonal camps.", "その遊牧民の共同体は季節ごとの野営地の間を家畜とともに移動する。"),
    "robust": ("強健な", "形容詞", "The doctor said the patient remained in robust health after treatment.", "医師は治療後も患者が健やかな健康状態を保っていると述べた。"),
    "frail": ("虚弱な、もろい", "形容詞", "The frail bird needed shelter until its injured wing healed.", "その虚弱な鳥は傷ついた翼が治るまで保護が必要だった。"),
    "marginal": ("わずかな、限界の", "形容詞", "The report found only a marginal improvement in water quality.", "その報告書は水質にわずかな改善しか見いださなかった。"),
    "ferocious": ("猛烈な、凶暴な", "形容詞", "The hikers turned back when a ferocious storm reached the valley.", "猛烈な嵐が谷に到達したため、ハイカーたちは引き返した。"),
    "shy away from": ("〜を避ける、尻込みする", "句動詞", "The young scientist did not shy away from challenging established theories.", "その若い科学者は、定説に挑むことを避けなかった。"),
    "rub off on": ("〜に影響が伝わる、性質がうつる", "句動詞", "His enthusiasm began to rub off on the rest of the team.", "彼の熱意がチームの他のメンバーにも伝わり始めた。"),
    "turn off": ("（人を）うんざりさせる、興味を失わせる", "句動詞", "Loud advertisements can turn off customers who value quiet design.", "騒々しい広告は、静かなデザインを重視する顧客をうんざりさせることがある。"),
    "make off with": ("〜を持ち逃げする", "句動詞", "The thief tried to make off with a bicycle near the station.", "その泥棒は駅の近くで自転車を持ち逃げしようとした。"),
    "hang around": ("ぶらぶらする、近くで待つ", "句動詞", "We decided to hang around after the meeting and discuss the proposal.", "私たちは会議の後もぶらぶら残って、その提案について話し合うことにした。"),
    "wait around": ("ぶらぶら待つ", "句動詞", "Passengers had to wait around for an hour after the train was canceled.", "乗客たちは列車が運休した後、1時間ぶらぶら待たなければならなかった。"),
    "poke around": ("あちこち探る", "句動詞", "The investigator continued to poke around for clues in the abandoned warehouse.", "捜査官は廃倉庫で手がかりを求めてあちこち探り続けた。"),
    "come clean": ("白状する、隠し事を打ち明ける", "句動詞", "The employee decided to come clean about the missing files.", "その従業員はなくなったファイルについて白状することにした。"),
    "reckoned on": ("〜を当てにした、予期した", "句動詞", "We had not reckoned on such severe weather during the crossing.", "私たちは横断中にこれほど厳しい天候になるとは予期していなかった。"),
    "rooted for": ("〜を応援した", "句動詞", "The entire town rooted for the underdog in the final match.", "町全体が決勝戦でその弱小チームを応援した。"),
    "dashed down": ("急いで書き留めた", "句動詞", "She dashed down a few notes before the lecture ended.", "彼女は講義が終わる前にいくつかメモを急いで書き留めた。"),
    "threw away": ("浪費した、捨てた", "句動詞", "He threw away the receipt before noticing the refund policy.", "彼は返金規定に気づく前にレシートを捨ててしまった。"),
    "float around": ("（うわさなどが）広まる、漂う", "句動詞", "Several explanations began to float around the office after the leak.", "情報漏えいの後、いくつかの説明が社内に広まり始めた。"),
    "weigh in": ("意見を述べる、議論に加わる", "句動詞", "The director chose to weigh in after hearing both sides.", "監督は双方の話を聞いた後、意見を述べることにした。"),
    "stack up": ("比較してつり合う、積み上がる", "句動詞", "The new proposal does not stack up against the cheaper alternative.", "新しい提案は、より安価な代案と比べると見劣りする。"),
    "squeak by": ("かろうじて切り抜ける", "句動詞", "The small business managed to squeak by during the difficult winter.", "その小さな会社は厳しい冬の間、何とか切り抜けた。"),
}


CORE_IMAGES = {
    "shy away from": {
        "chain": [
            {"term": "shy", "gloss": "尻込みする"},
            {"term": "away", "gloss": "離れる方向へ"},
            {"gloss": "対象から身を引く"},
            {"gloss": "〜を避ける、尻込みする"},
        ],
        "particle": "away",
    },
    "rub off on": {
        "chain": [
            {"term": "rub", "gloss": "こする"},
            {"term": "off", "gloss": "表面から離して"},
            {"term": "on", "gloss": "次の対象へ移して"},
            {"gloss": "影響や性質を別の対象へ伝える"},
        ],
        "particle": "on",
        "particleSense": "transmit",
    },
    "turn off": {
        "chain": [
            {"term": "turn", "gloss": "向きを変える"},
            {"term": "off", "gloss": "対象から離して"},
            {"gloss": "相手を気持ちの対象から離す"},
            {"gloss": "（人を）うんざりさせる、興味を失わせる"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "make off with": {
        "chain": [
            {"term": "make", "gloss": "動かす、行う"},
            {"term": "off", "gloss": "離れた方へ持ち去って"},
            {"gloss": "手元から離して持ち逃げする"},
            {"gloss": "〜を持ち逃げする"},
        ],
        "particle": "off",
        "particleSense": "pull-away",
    },
    "hang around": {
        "chain": [
            {"term": "hang", "gloss": "ぶら下がる"},
            {"term": "around", "gloss": "周囲にとどまって"},
            {"gloss": "周囲にぶら下がるように留まる"},
            {"gloss": "ぶらぶらする、近くで待つ"},
        ],
        "particle": "around",
    },
    "wait around": {
        "chain": [
            {"term": "wait", "gloss": "待つ"},
            {"term": "around", "gloss": "周囲にとどまって"},
            {"gloss": "周囲で待ち続ける"},
            {"gloss": "ぶらぶら待つ"},
        ],
        "particle": "around",
    },
    "poke around": {
        "chain": [
            {"term": "poke", "gloss": "つつく"},
            {"term": "around", "gloss": "周囲をあちこち"},
            {"gloss": "周囲をつつきながら探る"},
            {"gloss": "あちこち探る"},
        ],
        "particle": "around",
    },
    "reckoned on": {
        "chain": [
            {"term": "reckon", "gloss": "計算する"},
            {"term": "on", "gloss": "前提として頼って"},
            {"gloss": "計算の中に前提として置く"},
            {"gloss": "〜を当てにした、予期した"},
        ],
        "particle": "on",
        "particleSense": "rely",
    },
    "dashed down": {
        "chain": [
            {"term": "dash", "gloss": "勢いよく走る"},
            {"term": "down", "gloss": "下へ書きつけて"},
            {"gloss": "紙の上へ勢いよく落とす"},
            {"gloss": "急いで書き留めた"},
        ],
        "particle": "down",
        "particleSense": "descend",
    },
    "threw away": {
        "chain": [
            {"term": "throw", "gloss": "投げる"},
            {"term": "away", "gloss": "離れた方へ"},
            {"gloss": "手元から投げ捨てる"},
            {"gloss": "浪費した、捨てた"},
        ],
        "particle": "away",
    },
    "float around": {
        "chain": [
            {"term": "float", "gloss": "浮かぶ"},
            {"term": "around", "gloss": "周囲へ"},
            {"gloss": "周囲を漂う"},
            {"gloss": "（うわさなどが）広まる、漂う"},
        ],
        "particle": "around",
    },
    "weigh in": {
        "chain": [
            {"term": "weigh", "gloss": "重さを測る"},
            {"term": "in", "gloss": "中へ"},
            {"gloss": "判断材料を議論の中へ加える"},
            {"gloss": "意見を述べる、議論に加わる"},
        ],
        "particle": "in",
    },
    "stack up": {
        "chain": [
            {"term": "stack", "gloss": "積み重ねる"},
            {"term": "up", "gloss": "上へ積み上げて"},
            {"gloss": "積み上げて比べる"},
            {"gloss": "比較してつり合う、積み上がる"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "squeak by": {
        "chain": [
            {"term": "squeak", "gloss": "きしむ音を立てる"},
            {"term": "by", "gloss": "そばを通り抜けて"},
            {"gloss": "ぎりぎり通過する"},
            {"gloss": "かろうじて切り抜ける"},
        ],
        "particle": "by",
    },
    "come clean": {
        "chain": [
            {"term": "come", "gloss": "来る"},
            {"term": "clean", "gloss": "隠し事のない状態"},
            {"gloss": "隠し事のない状態に出てきて"},
            {"gloss": "白状する、隠し事を打ち明ける"},
        ],
    },
    "rooted for": {
        "chain": [
            {"term": "root", "gloss": "根を張る"},
            {"term": "for", "gloss": "〜を支持して"},
            {"gloss": "支持する側に根を張って"},
            {"gloss": "〜を応援した"},
        ],
    },
}

C_PHRASES = {}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 25:
        raise ValueError("模試 第6回は25問である必要があります")

    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != len(set(choices)):
        raise ValueError("選択肢に重複があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")

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
        if " " in phrase and phrase not in CORE_IMAGES and phrase not in C_PHRASES:
            raise ValueError(f"熟語の核心イメージまたはC型理由がありません: {phrase}")

    meta = {
        "grade": "英検1級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "ユーザー提供画像（原本表記は模試第1回）を、依頼により模試第6回として構造化。既存語句との重複を避けるため一部選択肢を置換",
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
            item = {
                "q": q,
                "is_answer": index == question["answerIndex"],
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
                "pos": pos,
            }
            if " " in choice:
                item["phrase"] = choice
                if choice in CORE_IMAGES:
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
    write_json(DATA_DIR / "vocab_1_mock-6.json", vocab)
    write_json(DATA_DIR / "questions_1_mock-6.json", questions)
    print("mock-6: 25 questions / 100 items (84 words, 16 idioms)")


if __name__ == "__main__":
    main()
