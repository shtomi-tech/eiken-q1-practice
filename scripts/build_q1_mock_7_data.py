"""ユーザー提供画像の英検1級模試を、模試第6回基準で構造化する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-7"
BLANK_RE = re.compile(r"\(\s+\)")


QUESTIONS = [
    {
        "stem": "When the interviewer criticized the Prime Minister's economic policy during the interview, he began to behave like a (   ) child. He gave her an angry look, and stubbornly refused to answer any more questions.",
        "choices": ["mediocre", "sluggish", "peevish", "deferential"],
        "answerIndex": 2,
        "translation": "面接官が首相の経済政策を批判すると、彼はいら立った子どものように振る舞い始めた。彼は面接官を怒った目で見て、その後の質問には頑として答えようとしなかった。",
    },
    {
        "stem": "The ranger told the campers that the best way to (   ) their campfire was to cover it with sand.",
        "choices": ["infer", "chisel", "douse", "dilute"],
        "answerIndex": 2,
        "translation": "レンジャーはキャンパーたちに、たき火を消す最善の方法は砂で覆うことだと伝えた。",
    },
    {
        "stem": "The survey researchers questioned a (   ) of people born in the late 1980s in different parts of the city to see how their background affected their future earning potential.",
        "choices": ["facet", "tantrum", "conundrum", "cohort"],
        "answerIndex": 3,
        "translation": "調査研究者たちは、出身地域が将来の収入の可能性にどう影響するかを見るため、市内の異なる地域で1980年代後半に生まれた人々の集団に質問した。",
    },
    {
        "stem": "The young police officer approached the crime scene with (   ). It was his first day on the job, and he was fearful of what he might see.",
        "choices": ["trepidation", "condemnation", "decimation", "destitution"],
        "answerIndex": 0,
        "translation": "その若い警察官は恐怖と不安を感じながら犯罪現場に近づいた。勤務初日で、何を見ることになるのか恐れていた。",
    },
    {
        "stem": "Although Evan inherited a large amount of money from his parents, he (   ) the entire amount. Two years later, he actually found himself in debt.",
        "choices": ["squandered", "kindled", "ascended", "cuddled"],
        "answerIndex": 0,
        "translation": "エバンは両親から多額の金を相続したが、その全額を浪費した。2年後、彼は実際に借金を抱えていた。",
    },
    {
        "stem": "The author complained that an editor had severely (   ) the original article she had written, cutting out several sections that she felt were essential to readers' understanding of the issue.",
        "choices": ["derided", "brewed", "abridged", "embittered"],
        "answerIndex": 2,
        "translation": "著者は、編集者が自分の書いた原稿を大幅に短縮したと不満を述べた。読者が問題を理解するのに不可欠だと感じた部分がいくつも削られていたからだ。",
    },
    {
        "stem": "The new club coach was shocked by the (   ) behavior of some of the younger players on the team. They were in the habit of using foul language and talking back to their coaches when scolded.",
        "choices": ["insubordinate", "reclusive", "virtuous", "steadfast"],
        "answerIndex": 0,
        "translation": "新しいクラブのコーチは、チームの若い選手たちの一部の反抗的な態度に衝撃を受けた。彼らは汚い言葉を使い、叱られるとコーチに口答えする習慣があった。",
    },
    {
        "stem": "Since neither leader was willing to compromise, the two nations have been moving (   ) toward war. Experts predict that the fighting will begin before the end of the year.",
        "choices": ["inexorably", "genially", "spuriously", "exquisitely"],
        "answerIndex": 0,
        "translation": "どちらの指導者も妥協する意思がなかったため、両国は戦争へ向かって避けられない形で進んでいる。専門家は年末までに戦闘が始まると予測している。",
    },
    {
        "stem": "Everyone was shocked by the King's sudden (   ) of the throne. No one had realized that his health condition was so serious.",
        "choices": ["incision", "renunciation", "abrasion", "combustion"],
        "answerIndex": 1,
        "translation": "国王が突然王位を放棄したことに、誰もが衝撃を受けた。健康状態がそれほど深刻だとは誰も気づいていなかった。",
    },
    {
        "stem": "Although her first novel was a bestseller, her second book (   ) its success, selling at least 10 times as many copies.",
        "choices": ["interjected", "attuned", "eclipsed", "despised"],
        "answerIndex": 2,
        "translation": "彼女の最初の小説はベストセラーだったが、2作目は少なくとも10倍の部数を売り、その成功をしのいだ。",
    },
    {
        "stem": "In Victorian London, many people lived in (   ), substandard housing with inadequate access to sanitation and clean water.",
        "choices": ["contemplative", "scrawny", "eminent", "squalid"],
        "answerIndex": 3,
        "translation": "ビクトリア朝のロンドンでは、多くの人々が衛生設備やきれいな水へのアクセスが不十分な、不潔でみすぼらしい粗末な住宅に住んでいた。",
    },
    {
        "stem": "Many drivers complained about having to pay such high fines for minor (   ) such as parking in the wrong area. They were especially angry because drivers who had committed much more serious offenses were given similar fines.",
        "choices": ["trysts", "rebuttals", "denominations", "violations"],
        "answerIndex": 3,
        "translation": "多くの運転手は、間違った場所に駐車するなどの軽微な違反行為に対して、これほど高額な罰金を払わなければならないことに不満を述べた。もっと重大な違反をした運転手にも同様の罰金が科されていたため、特に腹を立てていた。",
    },
    {
        "stem": "John did not do very well at school. It was not until much later that he discovered he had a (   ) talent for poetry.",
        "choices": ["scandalous", "latent", "reminiscent", "prudish"],
        "answerIndex": 1,
        "translation": "ジョンは学校であまり成績がよくなかった。ずっと後になって初めて、彼には詩の潜在的な才能があると分かった。",
    },
    {
        "stem": "A: Jesse, I just got this really (   ) text from our boss. I'm not sure if he wants me to do something or not.\nB: I would just ask him if I were you. He's in the habit of writing these kinds of confusing messages.",
        "choices": ["eloquent", "discernible", "cryptic", "jubilant"],
        "answerIndex": 2,
        "translation": "A：ジェシー、上司から本当に謎めいたメッセージが来たよ。何かしてほしいのかどうか、よく分からない。\nB：僕なら本人に聞くよ。彼はこういう分かりにくいメッセージを書く癖があるんだ。",
    },
    {
        "stem": "The (   ) against the ship's captain was led by one of the officers who was tired of seeing the sailors treated so badly. It only took a short time for the sailors to take control of the ship.",
        "choices": ["mutiny", "divergence", "expletive", "frivolity"],
        "answerIndex": 0,
        "translation": "船長に対する反乱は、船員たちがひどい扱いを受けるのを見かねた士官の一人が率いた。船員たちが船を掌握するまでには、短い時間しかかからなかった。",
    },
    {
        "stem": "Everyone agreed that the racing driver was lucky to have walked away from the accident (   ), especially since his car was completely wrecked.",
        "choices": ["unscathed", "unfounded", "concerted", "outmoded"],
        "answerIndex": 0,
        "translation": "レーシングドライバーは、車が完全に壊れていたことを考えれば、事故から無傷で立ち去れたのは幸運だったと誰もが認めた。",
    },
    {
        "stem": "A: Do you have any idea what Governor Kaufmann's policy on healthcare for the elderly is?\nB: I don't think anyone does. He's constantly (   ) on the issue.",
        "choices": ["obfuscating", "hibernating", "pontificating", "reverberating"],
        "answerIndex": 0,
        "translation": "A：カウフマン知事の高齢者医療政策がどんなものか、分かる？\nB：誰にも分からないと思う。彼はその問題をいつも曖昧にしているんだ。",
    },
    {
        "stem": "Mr. Ebel may be popular, but it is only because he (   ) to his students by letting them watch a lot of movies and not assigning homework.",
        "choices": ["panders", "flinches", "jangles", "abstains"],
        "answerIndex": 0,
        "translation": "エベル氏は人気があるかもしれないが、それは映画をたくさん見せ、宿題を出さないことで生徒に迎合しているからにすぎない。",
    },
    {
        "stem": "Many hackers seem to feel that they can behave with (   ). They are not at all worried that they will be prosecuted for their crimes.",
        "choices": ["impunity", "slumber", "temerity", "attire"],
        "answerIndex": 0,
        "translation": "多くのハッカーは処罰を受けずに振る舞えると感じているようだ。自分の犯罪で起訴されることをまったく心配していない。",
    },
    {
        "stem": "King Henry VIII of England had a reputation for being a (   ). It has been reported that he ate vast amounts of food every day and was fond of holding lavish banquets.",
        "choices": ["nemesis", "glutton", "paragon", "protégé"],
        "answerIndex": 1,
        "translation": "イングランド王ヘンリー8世は大食漢として知られていた。毎日大量の食べ物を食べ、豪華な宴会を開くのを好んだと伝えられている。",
    },
    {
        "stem": "The man was finally arrested in France and he is currently being (   ) to his own country, where he will be on trial for a crime he is said to have committed.",
        "choices": ["confounded", "relocated", "pillaged", "extradited"],
        "answerIndex": 3,
        "translation": "その男はついにフランスで逮捕され、現在、犯罪を犯したとされる自国へ引き渡されている。そこで裁判を受けることになる。",
    },
    {
        "stem": "During his month-long stay, Mr. Livingston was required by the hotel to (   ) his expenses for any services he used at the end of every week.",
        "choices": ["roll over", "thin out", "square up", "wind down"],
        "answerIndex": 2,
        "translation": "1か月の滞在中、リビングストン氏は、利用したサービスの費用を毎週末に精算するようホテルから求められた。",
    },
    {
        "stem": "The politician (   ) the accusation that he had accepted a bribe for helping a company win a government construction contract, saying it was not unusual for politicians to be paid for their advice.",
        "choices": ["hemmed in", "glossed over", "bailed out", "polished off"],
        "answerIndex": 1,
        "translation": "その政治家は、企業が政府の建設契約を得るのを助ける見返りに賄賂を受け取ったという非難を軽く扱ってごまかし、政治家が助言の報酬を受け取るのは珍しくないと述べた。",
    },
    {
        "stem": "When the new mayor was elected, he promised to (   ) crime. He said his main goal was to make the city a safer place to live.",
        "choices": ["muscle in on", "stock up on", "tie in with", "clamp down on"],
        "answerIndex": 3,
        "translation": "新しい市長が選出されたとき、彼は犯罪を厳しく取り締まると約束した。主な目標は、その都市をより安全に暮らせる場所にすることだと述べた。",
    },
    {
        "stem": "The author nearly gave up on finishing his mystery novel due to his inability to come up with a satisfying conclusion. Fortunately, he (   ) a great idea while taking a relaxing walk along the beach.",
        "choices": ["struck on", "pushed for", "hailed from", "set forth"],
        "answerIndex": 0,
        "translation": "その作家は、満足のいく結末を思いつけなかったため、推理小説を書き終えるのを諦めかけた。幸い、浜辺をゆっくり歩いているときに、すばらしい考えを思いついた。",
    },
]


DETAILS = {
    "mediocre": ("平凡な、二流の", "形容詞", "The committee rejected the mediocre proposal after comparing it with stronger alternatives.", "委員会は、より優れた代案と比較した後、その平凡な提案を退けた。"),
    "sluggish": ("動きの鈍い、活気のない", "形容詞", "The sluggish economy recovered only after interest rates were gradually reduced.", "景気の鈍い経済は、金利が徐々に引き下げられて初めて回復した。"),
    "peevish": ("いら立った、気難しい", "形容詞", "A peevish customer complained about every minor delay at the crowded airport.", "いら立った客は、混雑した空港で少しの遅れにも不満を述べた。"),
    "deferential": ("敬意を表す、へりくだった", "形容詞", "The young diplomat remained deferential when speaking with the respected ambassador.", "その若い外交官は、尊敬される大使と話すときもへりくだった態度を保った。"),
    "infer": ("推論する、推測する", "動詞", "Researchers infer hidden motives from patterns in a person's repeated choices.", "研究者は、人が繰り返す選択のパターンから隠れた動機を推測する。"),
    "chisel": ("のみで削る；だます", "動詞", "The craftsperson used a sharp tool to chisel intricate patterns into the stone.", "職人は鋭い道具を使って石に精巧な模様を彫った。"),
    "douse": ("（火などを）消す、液体を浴びせる", "動詞", "Firefighters quickly douse the burning curtains before flames reach the ceiling.", "消防士たちは炎が天井に届く前に、燃えているカーテンをすぐに消す。"),
    "dilute": ("薄める、弱める", "動詞", "The laboratory technician will dilute the solution before measuring its acidity.", "研究室の技術者は、酸性度を測る前に溶液を薄める。"),
    "facet": ("側面、面", "名詞", "The documentary explored one overlooked facet of migration through personal family stories.", "そのドキュメンタリーは、家族の個人的な物語を通して、見落とされていた移住の一側面を掘り下げた。"),
    "tantrum": ("癇癪", "名詞", "The exhausted child threw a tantrum when the amusement park finally closed.", "遊園地がついに閉まると、疲れた子どもは癇癪を起こした。"),
    "conundrum": ("難問、困難な問題", "名詞", "The committee faced a financial conundrum after two major donors withdrew unexpectedly.", "大口寄付者2人が突然撤退し、委員会は財政上の難問に直面した。"),
    "cohort": ("同じ属性を持つ集団", "名詞", "The researchers followed a cohort of graduates for fifteen years.", "研究者たちは、卒業生の一集団を15年間追跡した。"),
    "trepidation": ("恐怖、不安", "名詞", "She entered the abandoned theater with trepidation as thunder shook the windows.", "雷が窓を揺らす中、彼女は不安を抱えて廃劇場に入った。"),
    "condemnation": ("非難、糾弾", "名詞", "The mayor's condemnation of corruption won support from local residents.", "市長による汚職の糾弾は、地元住民の支持を得た。"),
    "decimation": ("大量殺戮、激減", "名詞", "The disease caused the decimation of several island bird populations.", "その病気は、いくつかの島の鳥の個体群を激減させた。"),
    "destitution": ("極貧、困窮", "名詞", "After the factory closed, many families were pushed into destitution.", "工場が閉鎖された後、多くの家庭が困窮に追い込まれた。"),
    "squandered": ("浪費した", "動詞", "He squandered his inheritance on expensive cars and impulsive overseas vacations.", "彼は相続財産を高級車と衝動的な海外旅行に浪費した。"),
    "kindled": ("火をつけた、感情を呼び起こした", "動詞", "The teacher kindled curiosity by bringing unusual historical artifacts into class.", "教師は珍しい歴史的遺物を授業に持ち込み、好奇心をかき立てた。"),
    "ascended": ("上昇した、昇進した", "動詞", "The climber ascended the narrow ridge before the weather deteriorated.", "天候が悪化する前に、登山者は狭い尾根を登った。"),
    "cuddled": ("抱きしめた", "動詞", "The child cuddled the frightened puppy until it stopped trembling.", "子どもは怯えた子犬が震えなくなるまで抱きしめた。"),
    "derided": ("あざ笑った、ばかにした", "動詞", "Several commentators derided the proposal before reading its detailed evidence.", "何人もの評論家が、詳しい根拠を読む前にその提案をあざ笑った。"),
    "brewed": ("（問題などを）引き起こした、醸造した", "動詞", "A dispute brewed quietly between the partners over the company's future.", "会社の将来をめぐって、共同経営者の間で争いがひそかに生じた。"),
    "abridged": ("切り詰めた、短縮した", "動詞", "The editor abridged the article to meet the magazine's strict word limit.", "編集者は雑誌の厳しい語数制限に合わせて記事を短縮した。"),
    "embittered": ("苦々しい思いをさせた", "動詞", "Years of unfair treatment embittered the worker and damaged his trust.", "何年にもわたる不公平な扱いがその労働者を苦々しい思いにさせ、信頼を損なった。"),
    "insubordinate": ("従順でない、反抗的な", "形容詞", "The insubordinate employee ignored repeated instructions from the department supervisor.", "その反抗的な従業員は、部門責任者からの再三の指示を無視した。"),
    "reclusive": ("隠遁した、世間から離れた", "形容詞", "The reclusive artist rarely attended public events or granted interviews.", "その隠遁した芸術家は、公の催しにほとんど参加せず、取材にも応じなかった。"),
    "virtuous": ("徳のある、道徳的な", "形容詞", "The virtuous leader refused a bribe despite facing severe political pressure.", "その道徳的な指導者は、強い政治的圧力に直面しても賄賂を断った。"),
    "steadfast": ("不動の、忠実な", "形容詞", "Her steadfast support helped the volunteers continue through the difficult winter.", "彼女の揺るぎない支援は、ボランティアが厳しい冬を乗り切る助けとなった。"),
    "inexorably": ("容赦なく、避けられない形で", "副詞", "The glacier moved inexorably downhill as warmer temperatures weakened the ice.", "気温が上がって氷が弱まるにつれ、氷河は容赦なく斜面を下った。"),
    "genially": ("愛想よく、親しげに", "副詞", "The host genially welcomed unexpected visitors despite the late hour.", "その主人は夜遅い時間にもかかわらず、突然の訪問者を愛想よく迎えた。"),
    "spuriously": ("偽って、見せかけだけで", "副詞", "The website spuriously claimed that the treatment could cure every illness.", "そのウェブサイトは、その治療法があらゆる病気を治せると偽って主張した。"),
    "exquisitely": ("非常に見事に、精妙に", "副詞", "The vase was exquisitely decorated with blue flowers and delicate gold lines.", "その花瓶は青い花と繊細な金色の線で非常に見事に装飾されていた。"),
    "incision": ("切開、切り込み", "名詞", "The surgeon made a careful incision near the patient's shoulder.", "外科医は患者の肩の近くに慎重な切開を施した。"),
    "renunciation": ("放棄、断念", "名詞", "The king's renunciation of the throne surprised citizens across the kingdom.", "国王による王位の放棄は、王国中の市民を驚かせた。"),
    "abrasion": ("擦り傷、摩擦", "名詞", "The cyclist cleaned a painful abrasion after falling on the gravel.", "その自転車選手は砂利道で転んだ後、痛む擦り傷を洗った。"),
    "combustion": ("燃焼", "名詞", "Complete combustion requires enough oxygen to burn the fuel efficiently.", "完全燃焼には、燃料を効率よく燃やすのに十分な酸素が必要だ。"),
    "interjected": ("口を挟んだ", "動詞", "She interjected a brief question before the lecturer moved to the next topic.", "講師が次の話題に移る前に、彼女は短い質問を差し挟んだ。"),
    "attuned": ("調和させた、敏感にした", "動詞", "The counselor stayed attuned to subtle changes in the student's mood.", "カウンセラーは生徒の気分の微妙な変化に敏感であり続けた。"),
    "eclipsed": ("（成功などを）しのいだ、影を薄くした", "動詞", "The sequel eclipsed the original film in both popularity and ticket sales.", "続編は人気と興行収入の両方で元の映画をしのいだ。"),
    "despised": ("軽蔑した", "動詞", "The corrupt official was despised by citizens who demanded accountability.", "その腐敗した役人は、説明責任を求める市民から軽蔑された。"),
    "contemplative": ("思索にふける", "形容詞", "The contemplative monk spent each morning beside the quiet mountain stream.", "その思索にふける修道士は、毎朝静かな山間の小川のそばで過ごした。"),
    "scrawny": ("やせこけた", "形容詞", "The scrawny stray cat gradually regained strength after receiving regular meals.", "そのやせこけた野良猫は、定期的に食事をもらって徐々に体力を取り戻した。"),
    "eminent": ("著名な、卓越した", "形容詞", "An eminent historian delivered the keynote lecture at the university.", "著名な歴史家が大学で基調講演を行った。"),
    "squalid": ("不潔でみすぼらしい", "形容詞", "Residents were forced to leave the squalid apartments after inspectors found mold.", "検査官がカビを見つけた後、住民は不潔でみすぼらしいアパートを出ざるを得なかった。"),
    "trysts": ("逢瀬、密会", "名詞", "The novel describes secret trysts between two people from rival families.", "その小説は、敵対する家の2人の間の秘密の逢瀬を描いている。"),
    "rebuttals": ("反論", "名詞", "The lawyer prepared several rebuttals to the government's technical arguments.", "弁護士は政府の技術的な主張に対する反論をいくつも準備した。"),
    "denominations": ("宗派；額面", "名詞", "The museum displays coins from many denominations and historical periods.", "その博物館は多くの額面と時代の硬貨を展示している。"),
    "violations": ("違反行為", "名詞", "The regulator recorded numerous violations during its inspection of the factory.", "規制当局は工場の検査中に多数の違反行為を記録した。"),
    "scandalous": ("醜聞の、けしからぬ", "形容詞", "The newspaper exposed a scandalous arrangement between the contractor and official.", "その新聞は請負業者と役人の間のけしからぬ取り決めを暴いた。"),
    "latent": ("潜在的な", "形容詞", "The program was designed to reveal latent talent among rural students.", "そのプログラムは地方の生徒たちの潜在的な才能を見いだすために設計された。"),
    "reminiscent": ("〜を思い起こさせる", "形容詞", "The melody is reminiscent of folk songs heard in her childhood.", "そのメロディーは彼女が子どもの頃に聞いた民謡を思い起こさせる。"),
    "prudish": ("堅苦しく潔癖な", "形容詞", "His prudish attitude made ordinary discussions about clothing surprisingly difficult.", "彼の堅苦しく潔癖な態度のため、服装についての普通の会話が意外なほど難しくなった。"),
    "eloquent": ("雄弁な、表現力豊かな", "形容詞", "Her eloquent presentation persuaded skeptical investors to support the community project.", "彼女の雄弁なプレゼンテーションは、懐疑的な投資家に地域プロジェクトを支援させた。"),
    "discernible": ("識別できる、明瞭な", "形容詞", "No discernible pattern appeared in the scattered survey responses.", "散在した調査回答には、識別できるパターンが現れなかった。"),
    "cryptic": ("謎めいた、難解な", "形容詞", "The message was so cryptic that even experienced analysts misunderstood it.", "そのメッセージは非常に難解だったので、経験豊富な分析官でさえ誤解した。"),
    "jubilant": ("歓喜に満ちた", "形容詞", "Jubilant supporters filled the streets after the team won the championship.", "チームが優勝すると、歓喜に満ちた支持者たちが通りを埋め尽くした。"),
    "mutiny": ("反乱、反乱を起こす", "名詞", "The crew organized a mutiny after the captain repeatedly endangered everyone.", "船長が何度も全員を危険にさらしたため、乗組員は反乱を組織した。"),
    "divergence": ("分岐、相違", "名詞", "A sharp divergence emerged between the two committees' recommendations.", "2つの委員会の勧告の間に大きな相違が生じた。"),
    "expletive": ("罵り言葉", "名詞", "The witness apologized after an expletive slipped out during the hearing.", "その証人は公聴会中に罵り言葉が口から出た後、謝罪した。"),
    "frivolity": ("軽薄さ、ふまじめさ", "名詞", "The judge warned that frivolity was inappropriate during the emergency meeting.", "裁判官は、緊急会議中のふまじめな態度は不適切だと警告した。"),
    "unscathed": ("無傷で", "形容詞", "The hikers escaped the falling rocks and reached the shelter unscathed.", "ハイカーたちは落石を逃れ、無傷で避難所にたどり着いた。"),
    "unfounded": ("根拠のない", "形容詞", "The newspaper withdrew its unfounded accusation after checking the official records.", "その新聞は公式記録を確認した後、根拠のない非難を撤回した。"),
    "concerted": ("協調した、合意の上の", "形容詞", "The neighbors made a concerted effort to restore the damaged playground.", "近隣住民は、壊れた遊び場を修復するため協力して努力した。"),
    "outmoded": ("時代遅れの", "形容詞", "The company replaced its outmoded software before security risks increased.", "その会社はセキュリティリスクが高まる前に、時代遅れのソフトウェアを交換した。"),
    "obfuscating": ("わかりにくくしている、曖昧にしている", "動詞", "The spokesperson kept obfuscating the issue instead of answering the direct question.", "広報担当者は直接の質問に答えず、問題を曖昧にし続けた。"),
    "hibernating": ("冬眠している", "動詞", "The bear was hibernating in a sheltered cave throughout the coldest months.", "そのクマは最も寒い数か月の間、風雨を避けられる洞窟で冬眠していた。"),
    "pontificating": ("偉そうに意見を述べている", "動詞", "The commentator kept pontificating about economics without examining the available data.", "その評論家は、入手できるデータを調べずに経済について偉そうに語り続けた。"),
    "reverberating": ("反響している", "動詞", "Loud music was reverberating through the station long after midnight.", "真夜中を過ぎても大音量の音楽が駅中に反響していた。"),
    "panders": ("迎合する", "動詞", "The candidate panders to popular fears instead of proposing practical solutions.", "その候補者は現実的な解決策を提案せず、大衆の不安に迎合する。"),
    "flinches": ("ひるむ", "動詞", "The goalkeeper never flinches when powerful shots approach at close range.", "そのゴールキーパーは強烈なシュートが近距離から来ても決してひるまない。"),
    "jangles": ("耳障りに鳴る、いら立たせる", "動詞", "The loose chain jangles against the bicycle frame whenever the wheel turns.", "緩んだチェーンは車輪が回るたびに自転車のフレームに当たって耳障りに鳴る。"),
    "abstains": ("控える", "動詞", "The senator abstains from voting when the evidence remains incomplete.", "その上院議員は証拠が不十分なとき、投票を控える。"),
    "impunity": ("処罰を受けないこと", "名詞", "The officials acted with impunity because no agency investigated their misconduct.", "どの機関も不正行為を調査しなかったため、その役人たちは処罰を受けないと思って行動した。"),
    "slumber": ("眠り、休止", "名詞", "The village remained in slumber until the first market bells rang.", "最初の市場の鐘が鳴るまで、その村は眠りの中にあった。"),
    "temerity": ("向こう見ずな大胆さ", "名詞", "She had the temerity to challenge the director during the public hearing.", "彼女には公開聴聞会で所長に異議を唱える向こう見ずな大胆さがあった。"),
    "attire": ("服装", "名詞", "The staff's formal attire reflected the ceremony's traditional character.", "職員の正式な服装は、その式典の伝統的な性格を反映していた。"),
    "nemesis": ("宿敵、かなわない相手", "名詞", "The detective finally confronted his old nemesis during the courtroom trial.", "その刑事はついに法廷で長年の宿敵と対峙した。"),
    "glutton": ("大食漢", "名詞", "The legendary glutton consumed an entire roast before the guests arrived.", "その伝説的な大食漢は、客が到着する前に丸ごとの焼き肉を食べきった。"),
    "paragon": ("模範、典型", "名詞", "The scholarship recipient was presented as a paragon of academic integrity.", "その奨学金受給者は学問的誠実さの模範として紹介された。"),
    "protégé": ("保護を受ける人、弟子", "名詞", "The senior editor introduced her talented protégé to the international publishing team.", "上級編集者は才能ある弟子を国際出版チームに紹介した。"),
    "confounded": ("困惑させた、混乱した", "動詞", "The unexpected results confounded researchers who had trusted the original model.", "予想外の結果は、元のモデルを信頼していた研究者たちを困惑させた。"),
    "relocated": ("移転させた、移転した", "動詞", "The family relocated to a smaller town after the factory closed.", "工場が閉鎖された後、その家族はより小さな町へ移転した。"),
    "pillaged": ("略奪した", "動詞", "Invaders pillaged the coastal village before withdrawing toward the mountains.", "侵略者たちは山へ撤退する前に海岸の村を略奪した。"),
    "extradited": ("送還した、引き渡した", "動詞", "The suspect was extradited after both countries approved the legal request.", "両国が法的要請を承認した後、その容疑者は引き渡された。"),
    "roll over": ("繰り越す", "句動詞", "The bank allowed customers to roll over unused credit into the next month.", "銀行は顧客が未使用の信用枠を翌月へ繰り越すことを認めた。"),
    "thin out": ("薄くする、間引く", "句動詞", "Rangers thin out the seedlings so the remaining trees receive enough sunlight.", "森林警備員は残った木々が十分な日光を受けられるよう苗木を間引く。"),
    "square up": ("精算する", "句動詞", "Please square up with the cashier before leaving the restaurant.", "レストランを出る前に、レジで精算してください。"),
    "wind down": ("徐々に終える、落ち着かせる", "句動詞", "The committee will wind down its activities after publishing the final report.", "委員会は最終報告書を発表した後、活動を徐々に終える。"),
    "hemmed in": ("閉じ込めた、行動を制限した", "句動詞", "The flooded river hemmed in the village and blocked every escape route.", "氾濫した川が村を取り囲み、あらゆる避難経路をふさいだ。"),
    "glossed over": ("問題などを軽く扱ってごまかした", "句動詞", "The report glossed over serious safety concerns to protect the company's reputation.", "その報告書は会社の評判を守るため、重大な安全上の懸念を軽く扱ってごまかした。"),
    "bailed out": ("救済した、保釈した", "句動詞", "The emergency fund bailed out several small businesses during the recession.", "その緊急基金は不況の間にいくつかの小企業を救済した。"),
    "polished off": ("片づけた、平らげた", "句動詞", "The hungry hikers polished off the remaining sandwiches before sunset.", "空腹のハイカーたちは日没前に残りのサンドイッチを平らげた。"),
    "muscle in on": ("〜に強引に割り込む", "句動詞", "A rival firm tried to muscle in on the profitable contract.", "競合企業がその利益の大きい契約に強引に割り込もうとした。"),
    "stock up on": ("〜を買い込む", "句動詞", "Families stock up on bottled water before severe storms arrive.", "激しい嵐が来る前に、家族はペットボトルの水を買い込む。"),
    "tie in with": ("〜と結びつく", "句動詞", "The new evidence may tie in with the witness's earlier statement.", "新しい証拠は、証人の以前の供述と結びつくかもしれない。"),
    "clamp down on": ("〜を厳しく取り締まる", "句動詞", "The city plans to clamp down on illegal dumping near rivers.", "市は川の近くでの不法投棄を厳しく取り締まる予定だ。"),
    "struck on": ("〜を思いついた、見つけた", "句動詞", "During a quiet walk, the novelist struck on a promising ending.", "小説家は静かな散歩の途中で、有望な結末を思いついた。"),
    "pushed for": ("〜を強く要求した", "句動詞", "The union pushed for safer equipment after several workplace accidents.", "労働組合は職場で事故が相次いだ後、より安全な設備を強く要求した。"),
    "hailed from": ("〜の出身である", "句動詞", "The renowned chef hailed from a small coastal town in Portugal.", "その有名な料理人は、ポルトガルの小さな海辺の町の出身だった。"),
    "set forth": ("〜を述べた、提示した", "句動詞", "The memorandum set forth clear procedures for handling future complaints.", "その覚書は、今後の苦情を処理する明確な手順を提示した。"),
}


CORE_IMAGES = {
    "roll over": {
        "chain": [
            {"term": "roll", "gloss": "転がる"},
            {"term": "over", "gloss": "境目を越えて"},
            {"gloss": "残高や期限を次の期間へ越して"},
            {"gloss": "繰り越す"},
        ],
        "particle": "over",
        "siblings": [
            {"phrase": "get over", "gloss": "乗り越える"},
            {"phrase": "read over", "gloss": "読み返す"},
            {"phrase": "start over", "gloss": "やり直す"},
        ],
    },
    "thin out": {
        "chain": [
            {"term": "thin", "gloss": "薄くする"},
            {"term": "out", "gloss": "外へ取り除いて"},
            {"gloss": "密度を下げて"},
            {"gloss": "薄くする、間引く"},
        ],
        "particle": "out",
        "particleSense": "remove",
    },
    "square up": {
        "chain": [
            {"term": "square", "gloss": "整える"},
            {"term": "up", "gloss": "整った状態まで"},
            {"gloss": "帳尻を合わせて"},
            {"gloss": "精算する"},
        ],
        "particle": "up",
        "particleSense": "settle",
    },
    "wind down": {
        "chain": [
            {"term": "wind", "gloss": "巻く、動かす"},
            {"term": "down", "gloss": "勢いや量を下げて"},
            {"gloss": "活動の勢いを落として"},
            {"gloss": "徐々に終える"},
        ],
        "particle": "down",
        "particleSense": "reduce",
        "siblings": [
            {"phrase": "slow down", "gloss": "速度を落とす"},
            {"phrase": "cool down", "gloss": "冷ます・落ち着かせる"},
            {"phrase": "tone down", "gloss": "調子をやわらげる"},
        ],
    },
    "hemmed in": {
        "chain": [
            {"term": "hem", "gloss": "縁取りで囲う"},
            {"term": "in", "gloss": "内側へ閉じ込める"},
            {"gloss": "周囲を囲んで動きを制限して"},
            {"gloss": "閉じ込めた"},
        ],
        "particle": "in",
    },
    "glossed over": {
        "chain": [
            {"term": "gloss", "gloss": "表面を飾る"},
            {"term": "over", "gloss": "上から覆う"},
            {"gloss": "問題の表面だけを覆って"},
            {"gloss": "軽く扱ってごまかした"},
        ],
        "particle": "over",
    },
    "bailed out": {
        "chain": [
            {"term": "bail", "gloss": "保釈金で助ける"},
            {"term": "out", "gloss": "状況の外へ出す"},
            {"gloss": "困難な状況から外へ救い出して"},
            {"gloss": "救済した"},
        ],
        "particle": "out",
        "particleSense": "escape",
    },
    "polished off": {
        "chain": [
            {"term": "polish", "gloss": "磨いて仕上げる"},
            {"term": "off", "gloss": "離れた状態まで"},
            {"gloss": "残りをすっかり片づけて"},
            {"gloss": "平らげた、処理した"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "muscle in on": {
        "chain": [
            {"term": "muscle", "gloss": "力で押し入る"},
            {"term": "in", "gloss": "内側へ入り込む"},
            {"term": "on", "gloss": "対象に向けて"},
            {"gloss": "力ずくで相手の領域に割り込む"},
        ],
        "particle": "in",
    },
    "stock up on": {
        "chain": [
            {"term": "stock", "gloss": "蓄える"},
            {"term": "up", "gloss": "いっぱいに整える"},
            {"term": "on", "gloss": "対象に向けて"},
            {"gloss": "対象を十分に買い込んで備える"},
        ],
        "particle": "up",
        "particleSense": "prepare",
    },
    "tie in with": {
        "chain": [
            {"term": "tie", "gloss": "結びつける"},
            {"term": "in", "gloss": "内側へ結びつけて"},
            {"term": "with", "gloss": "一緒に"},
            {"gloss": "別のものと関連づける"},
        ],
        "particle": "in",
    },
    "clamp down on": {
        "chain": [
            {"term": "clamp", "gloss": "締め具で固定する"},
            {"term": "down", "gloss": "下へ押さえつける"},
            {"term": "on", "gloss": "対象に向けて"},
            {"gloss": "対象を押さえつけて取り締まる"},
        ],
        "particle": "down",
        "particleSense": "suppress",
    },
    "struck on": {
        "chain": [
            {"term": "strike", "gloss": "打つ、ふと出会う"},
            {"term": "on", "gloss": "対象に触れて"},
            {"gloss": "考えにふと行き当たって"},
            {"gloss": "〜を思いついた"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "pushed for": {
        "chain": [
            {"term": "push", "gloss": "押す"},
            {"term": "for", "gloss": "目的へ向けて"},
            {"gloss": "実現へ向けて強く働きかけて"},
            {"gloss": "〜を強く要求した"},
        ],
    },
    "hailed from": {
        "chain": [
            {"term": "hail", "gloss": "呼びかける、出身である"},
            {"term": "from", "gloss": "起点から"},
            {"gloss": "出発点を示して"},
            {"gloss": "〜の出身である"},
        ],
    },
    "set forth": {
        "chain": [
            {"term": "set", "gloss": "置く"},
            {"term": "forth", "gloss": "前へ"},
            {"gloss": "考えを前へ出して"},
            {"gloss": "〜を述べた、提示した"},
        ],
    },
}

C_PHRASES = {}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 25:
        raise ValueError("模試 第7回は25問である必要があります")

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
        "source": "ユーザー提供画像（原本表記は模試第2回）を、依頼により模試第7回として構造化。既存語句との重複を避けるため一部選択肢を置換",
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
    write_json(DATA_DIR / "vocab_1_mock-7.json", vocab)
    write_json(DATA_DIR / "questions_1_mock-7.json", questions)
    print("mock-7: 25 questions / 100 items (84 words, 16 idioms)")


if __name__ == "__main__":
    main()
