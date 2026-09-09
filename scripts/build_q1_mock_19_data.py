"""英検1級 模試第19回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-19 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-19"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "The wooden bridge was only ever meant as a (   ) until the concrete one was finished.",
        "choices": ["stopgap", "rationale", "asylum", "homage"],
        "answerIndex": 0,
        "translation": "その木橋は、コンクリート橋が完成するまでの間に合わせとしてしか考えられていなかった。",
    },
    {
        "stem": "Researchers attribute the (   ) of these islanders to their diet and their daily walking.",
        "choices": ["rift", "longevity", "adversary", "jetty"],
        "answerIndex": 1,
        "translation": "研究者はこれらの島民の長寿を、食事と日々の歩行によるものだとしている。",
    },
    {
        "stem": "The society openly preached (   ) in all things, including food, drink, dress and conversation.",
        "choices": ["dissipation", "infamy", "temperance", "payoff"],
        "answerIndex": 2,
        "translation": "その団体は食事も酒も服装も会話も含め、あらゆることにおける節制を公然と説いた。",
    },
    {
        "stem": "The so-called doctor turned out to be a (   ) with no medical training whatsoever.",
        "choices": ["pundit", "agility", "vortex", "charlatan"],
        "answerIndex": 3,
        "translation": "自称医師は、医学教育をまったく受けていない偽医者であることが判明した。",
    },
    {
        "stem": "The dispute falls outside the (   ) of this court and must be heard elsewhere.",
        "choices": ["jurisdiction", "rendezvous", "feat", "layman"],
        "answerIndex": 0,
        "translation": "その争いはこの裁判所の管轄外であり、別の場で審理されなければならない。",
    },
    {
        "stem": "The soprano gave a (   ) of the aria that the composer himself would have admired.",
        "choices": ["vulgarity", "rendition", "veracity", "snitch"],
        "answerIndex": 1,
        "translation": "そのソプラノ歌手は、作曲家自身が称賛したであろうアリアの演奏を聴かせた。",
    },
    {
        "stem": "The cartoon is a cruel (   ) of a man who was in fact rather generous.",
        "choices": ["onrush", "truancy", "redolence", "caricature"],
        "answerIndex": 3,
        "translation": "その風刺画は、実際はかなり気前のよかった男を残酷に戯画化したものである。",
    },
    {
        "stem": "The chef likes to (   ) each plate with a few leaves picked that morning.",
        "choices": ["garnish", "suffocate", "debase", "meddle"],
        "answerIndex": 0,
        "translation": "そのシェフはその朝に摘んだ葉を数枚添えて、各皿を飾るのを好む。",
    },
    {
        "stem": "The little harbor town seems to (   ) almost everything visitors imagine about that coast.",
        "choices": ["satiate", "retaliate", "epitomize", "purport"],
        "answerIndex": 2,
        "translation": "その小さな港町は、訪問者がその海岸について思い描くほとんどすべてを体現しているように見える。",
    },
    {
        "stem": "The sheep (   ) together against the stone wall whenever the wind rose after dark.",
        "choices": ["huddled", "tempered", "perished", "arbitrated"],
        "answerIndex": 0,
        "translation": "日が暮れて風が強まるたび、羊たちは石壁の際に身を寄せ合った。",
    },
    {
        "stem": "It took four hours to (   ) the driver from the wreckage of the lorry.",
        "choices": ["exhale", "juggle", "extricate", "improvise"],
        "answerIndex": 2,
        "translation": "トラックの残骸から運転手を救い出すのに4時間かかった。",
    },
    {
        "stem": "Readers who see only the headline are likely to (   ) the meaning of the whole report.",
        "choices": ["discard", "smear", "misconstrue", "syndicate"],
        "answerIndex": 2,
        "translation": "見出しだけを見る読者は、報告書全体の意味を誤解しがちである。",
    },
    {
        "stem": "The treasurer (   ) with the entire building fund and was never seen in the town again.",
        "choices": ["avenged", "garnered", "scrounged", "absconded"],
        "answerIndex": 3,
        "translation": "会計係は建設基金の全額を持ち逃げし、二度とその町に姿を見せなかった。",
    },
    {
        "stem": "Trained negotiators are often able to (   ) tensions between hostile parties before any violence breaks out.",
        "choices": ["manipulate", "reprove", "defuse", "defraud"],
        "answerIndex": 2,
        "translation": "訓練された交渉人は、暴力沙汰になる前に敵対する当事者間の緊張をしばしば和らげることができる。",
    },
    {
        "stem": "The exhibition includes a (   ) painting of a skeleton playing a violin at a funeral.",
        "choices": ["opulent", "macabre", "redundant", "obstinate"],
        "answerIndex": 1,
        "translation": "その展覧会には、葬儀でバイオリンを弾く骸骨を描いた不気味な絵が含まれている。",
    },
    {
        "stem": "The photographs taken that summer provide (   ) proof that the wall was standing here in 1890.",
        "choices": ["gaudy", "raucous", "sadistic", "irrefutable"],
        "answerIndex": 3,
        "translation": "その夏に撮られた写真は、1890年にここに壁が立っていたという反論できない証拠を提供している。",
    },
    {
        "stem": "The orchard produced a (   ) crop in the year after the old trees were pruned.",
        "choices": ["prodigious", "leery", "impalpable", "flagrant"],
        "answerIndex": 0,
        "translation": "その果樹園は古木を剪定した翌年に驚異的な量の実を付けた。",
    },
    {
        "stem": "The (   ) noise from the building site continued from seven until dusk every day.",
        "choices": ["invincible", "pitiless", "incessant", "incremental"],
        "answerIndex": 2,
        "translation": "建設現場からの絶え間ない騒音は、毎日7時から日暮れまで続いた。",
    },
    {
        "stem": "The path becomes so (   ) after the second bridge that walkers need both hands.",
        "choices": ["measly", "savvy", "precipitous", "fluorescent"],
        "answerIndex": 2,
        "translation": "2つ目の橋を過ぎるとその道は非常に険しくなり、歩く人は両手を使う必要がある。",
    },
    {
        "stem": "Even the most (   ) forecasters did not expect the harvest to double this year.",
        "choices": ["listless", "inflatable", "exorbitant", "sanguine"],
        "answerIndex": 3,
        "translation": "最も楽観的な予測者でさえ、今年の収穫が倍になるとは予想していなかった。",
    },
    {
        "stem": "He was speaking (   ), of course, but two newspapers reported the remark as fact.",
        "choices": ["figuratively", "diabolically", "adamantly", "fervently"],
        "answerIndex": 0,
        "translation": "もちろん彼は比喩的に言っていたのだが、2つの新聞はその発言を事実として報じた。",
    },
    {
        "stem": "Anyone building anything on this coast will (   ) the same problem of constantly shifting sand.",
        "choices": ["run up against", "look back on", "fall in with", "simmer down"],
        "answerIndex": 0,
        "translation": "この海岸で何かを建てる人は誰でも、砂が絶えず移動するという同じ問題に突き当たることになる。",
    },
    {
        "stem": "It took the goalkeeper three seasons to (   ) a single mistake in that final.",
        "choices": ["horse around", "live down", "hike up", "thumb through"],
        "answerIndex": 1,
        "translation": "そのゴールキーパーが決勝での1つのミスを忘れ去られるまでに3シーズンかかった。",
    },
    {
        "stem": "Reviewers (   ) the novel without once mentioning that its author had died in March.",
        "choices": ["squared off against", "ganged up on", "tore into", "got away with"],
        "answerIndex": 2,
        "translation": "批評家たちは、著者が3月に亡くなっていたことに一度も触れずにその小説を酷評した。",
    },
    {
        "stem": "The entire dispute (   ) the question of who owns the strip of land behind the church.",
        "choices": ["boils down to", "comes down on", "gets back at", "smooths over"],
        "answerIndex": 0,
        "translation": "その争い全体は、教会の裏の細長い土地を誰が所有しているのかという問題に帰着する。",
    },
]


DETAILS = {
    # Q1
    "stopgap": ("間に合わせ、一時しのぎ", "名詞", "The tent served as a stopgap while the roof was being replaced.", "屋根の葺き替えの間、そのテントが一時しのぎの役目を果たした。"),
    "rationale": ("論理的根拠、理由づけ", "名詞", "The rationale for closing the branch was never explained to staff.", "支店を閉鎖する根拠は職員に一度も説明されなかった。"),
    "asylum": ("亡命、保護施設", "名詞", "The family was granted asylum after a three-year legal process.", "その一家は3年に及ぶ法的手続きの末に庇護を認められた。"),
    "homage": ("敬意、賛辞", "名詞", "The film is an open homage to the westerns of the 1950s.", "その映画は1950年代の西部劇へのあからさまな敬意の表明である。"),
    # Q2
    "rift": ("亀裂、不和", "名詞", "A rift opened between the two founders over the sale of shares.", "株式の売却をめぐって2人の創業者の間に亀裂が生じた。"),
    "longevity": ("長寿、長続きすること", "名詞", "The longevity of the design owes much to its simplicity.", "その設計の息の長さは単純さに負うところが大きい。"),
    "adversary": ("敵、対戦相手", "名詞", "He faced the same adversary in three consecutive finals.", "彼は3年連続の決勝で同じ相手と対戦した。"),
    "jetty": ("桟橋、防波堤", "名詞", "The old jetty is closed whenever the swell exceeds two meters.", "うねりが2メートルを超えるときはいつでも、その古い桟橋は閉鎖される。"),
    # Q3
    "dissipation": ("散逸、放蕩", "名詞", "Heat dissipation is the main limit on how fast the chip can run.", "熱の放散が、そのチップの動作速度の主な制約である。"),
    "infamy": ("悪評、汚名", "名詞", "The trial brought the small firm a degree of infamy it never lost.", "その裁判は小さな会社に、決して消えることのない悪評をもたらした。"),
    "temperance": ("節制、禁酒", "名詞", "The temperance movement gathered strength in the 1840s.", "禁酒運動は1840年代に勢いを増した。"),
    "payoff": ("報い、見返り", "名詞", "The payoff for those long nights came four years later.", "あの長い夜々の見返りは4年後にやってきた。"),
    # Q4
    "pundit": ("評論家、専門家", "名詞", "A television pundit predicted the opposite result on every occasion.", "あるテレビ評論家は、毎回反対の結果を予想していた。"),
    "agility": ("敏捷さ、機敏さ", "名詞", "The agility of the older players surprised the visiting coach.", "年長の選手たちの敏捷さは、遠征してきた監督を驚かせた。"),
    "vortex": ("渦、渦巻き", "名詞", "A vortex forms below the weir whenever the river is running high.", "川の水位が高いときはいつも、堰の下に渦ができる。"),
    "charlatan": ("いかさま師、偽医者", "名詞", "The village was taken in by a charlatan selling coloured water.", "その村は色水を売るいかさま師にだまされた。"),
    # Q5
    "jurisdiction": ("管轄、司法権", "名詞", "The river marks the northern limit of the city's jurisdiction.", "その川が市の管轄の北の境界を示している。"),
    "rendezvous": ("待ち合わせ、会合", "名詞", "The crews agreed on a rendezvous ten kilometers offshore.", "両乗組員は沖合10キロでの合流地点を取り決めた。"),
    "feat": ("偉業、離れ業", "名詞", "Crossing the range on foot in winter was a remarkable feat.", "冬にその山脈を徒歩で越えたのは目覚ましい偉業だった。"),
    "layman": ("素人、門外漢", "名詞", "The guide explains the chemistry in terms any layman can follow.", "その解説書は、素人でも理解できる言葉で化学を説明している。"),
    # Q6
    "vulgarity": ("下品さ、俗悪", "名詞", "The vulgarity of the decoration offended the older members.", "その装飾の俗悪さは年配の会員たちを不快にさせた。"),
    "rendition": ("演奏、表現", "名詞", "Her rendition of the folk song silenced the whole hall.", "彼女の民謡の歌唱はホール全体を静まり返らせた。"),
    "veracity": ("真実性、正確さ", "名詞", "Nobody has questioned the veracity of the original diary.", "その原本の日記の真実性を疑う者はいない。"),
    "snitch": ("密告者", "名詞", "In that prison a snitch could not expect much protection.", "その刑務所では、密告者はたいした保護を期待できなかった。"),
    # Q7
    "onrush": ("突進、殺到", "名詞", "The onrush of water carried away two footbridges.", "水の奔流は2つの歩道橋を押し流した。"),
    "truancy": ("無断欠席、ずる休み", "名詞", "Truancy fell sharply after the school changed its start time.", "学校が始業時刻を変えた後、無断欠席は急減した。"),
    "redolence": ("芳香、におい", "名詞", "The redolence of fresh pine filled the small workshop every morning.", "新しい松の香りが毎朝その小さな工房を満たしていた。"),
    "caricature": ("風刺画、戯画化", "名詞", "The portrait is closer to a caricature than to a likeness.", "その肖像は似姿というより風刺画に近い。"),
    # Q8
    "garnish": ("(料理を)飾る、添える", "動詞", "Cooks here garnish the soup with a single sprig of dill.", "ここの料理人はスープにディルの小枝を1本添える。"),
    "suffocate": ("窒息させる", "動詞", "Thick smoke can suffocate people long before flames reach them.", "濃い煙は炎が届くずっと前に人を窒息させることがある。"),
    "debase": ("価値を落とす、卑しめる", "動詞", "Printing more notes only served to debase the currency further.", "紙幣を増刷することは通貨の価値をさらに下げるだけだった。"),
    "meddle": ("干渉する、口出しする", "動詞", "Officials should not meddle in decisions the committee has already made.", "役人は委員会がすでに下した決定に口出しすべきではない。"),
    # Q9
    "satiate": ("十分に満たす、飽きさせる", "動詞", "A single bowl of that stew will satiate almost anyone.", "そのシチューを1杯食べれば、ほとんど誰でも十分満足する。"),
    "retaliate": ("報復する", "動詞", "The union threatened to retaliate with a further two-day strike.", "組合はさらに2日間のストライキで報復すると警告した。"),
    "epitomize": ("典型を示す、体現する", "動詞", "These narrow lanes epitomize the old quarter of the city.", "これらの狭い路地はその街の旧市街を象徴している。"),
    "purport": ("(~と)称する、意味する", "動詞", "The letters purport to come from a soldier in the same regiment.", "それらの手紙は同じ連隊の兵士から来たものだと称している。"),
    # Q10
    "huddled": ("身を寄せ合った", "動詞", "The passengers huddled under the canopy until the shower passed.", "乗客たちはにわか雨が過ぎるまで日よけの下で身を寄せ合った。"),
    "tempered": ("和らげた、鍛えた", "動詞", "Experience tempered his early enthusiasm for grand schemes.", "経験は壮大な計画への彼の初期の熱意を和らげた。"),
    "perished": ("死んだ、滅びた", "動詞", "Almost the entire crew perished when the vessel struck the reef.", "船が岩礁に乗り上げたとき、乗組員のほぼ全員が命を落とした。"),
    "arbitrated": ("仲裁した", "動詞", "A retired judge arbitrated the dispute over the shared driveway.", "退職した裁判官が共用の私道をめぐる争いを仲裁した。"),
    # Q11
    "exhale": ("息を吐く", "動詞", "Divers are taught to exhale steadily as they rise.", "潜水者は浮上する際に一定して息を吐くよう教えられる。"),
    "juggle": ("やりくりする、お手玉をする", "動詞", "She has to juggle two jobs and a course in the evenings.", "彼女は夜に2つの仕事と講座をやりくりしなければならない。"),
    "extricate": ("救い出す、脱出させる", "動詞", "It is easier to enter such an agreement than to extricate yourself later.", "そうした契約は結ぶほうが、後で抜け出すよりも簡単である。"),
    "improvise": ("即興で作る、間に合わせる", "動詞", "The band had to improvise when the sheet music went missing.", "楽譜がなくなったとき、その楽団は即興で演奏しなければならなかった。"),
    # Q12
    "discard": ("捨てる、処分する", "動詞", "Please discard any container that shows signs of damage.", "損傷の跡がある容器はすべて廃棄してください。"),
    "smear": ("塗りつける、中傷する", "動詞", "Someone tried to smear the candidate with an old photograph.", "何者かが古い写真でその候補者を中傷しようとした。"),
    "misconstrue": ("誤解する、曲解する", "動詞", "It is easy to misconstrue politeness as agreement in that culture.", "その文化では礼儀正しさを同意と誤解しやすい。"),
    "syndicate": ("(記事などを)配信する、共同出資する", "動詞", "The paper began to syndicate the column to nine other titles.", "その新聞はそのコラムを他の9紙へ配信し始めた。"),
    # Q13
    "avenged": ("復讐した、報いた", "動詞", "The younger brother avenged the insult twenty years later.", "弟は20年後にその侮辱に報いた。"),
    "garnered": ("(支持などを)集めた", "動詞", "The petition garnered ninety thousand signatures in a fortnight.", "その請願は2週間で9万人の署名を集めた。"),
    "scrounged": ("かき集めた、せしめた", "動詞", "They scrounged enough timber to rebuild the shed themselves.", "彼らは自分たちで小屋を建て直すのに十分な木材をかき集めた。"),
    "absconded": ("持ち逃げした、逃亡した", "動詞", "The bookkeeper absconded before the audit was completed.", "その経理係は監査が終わる前に逃亡した。"),
    # Q14
    "manipulate": ("操作する、巧みに操る", "動詞", "It is possible to manipulate the results by choosing the sample carefully.", "標本を慎重に選ぶことで結果を操作することは可能である。"),
    "reprove": ("たしなめる、叱る", "動詞", "The abbot would reprove any monk who spoke during the meal.", "修道院長は食事中に話す修道士を誰であれたしなめた。"),
    "defuse": ("(緊張を)和らげる、信管を外す", "動詞", "A single joke can sometimes defuse an argument entirely.", "たった1つの冗談が口論をすっかり収めてしまうこともある。"),
    "defraud": ("だまし取る、詐取する", "動詞", "He was convicted of trying to defraud his own insurer.", "彼は自分の保険会社から金を詐取しようとした罪で有罪となった。"),
    # Q15
    "opulent": ("豪華な、富裕な", "形容詞", "The opulent dining room seats forty under three chandeliers.", "その豪華な食堂は3つのシャンデリアの下に40人を収容する。"),
    "macabre": ("不気味な、死を思わせる", "形容詞", "The museum keeps a macabre collection of surgical instruments.", "その博物館は不気味な外科器具のコレクションを所蔵している。"),
    "redundant": ("余分な、冗長な", "形容詞", "The second paragraph is redundant and can simply be cut.", "第2段落は余分であり、単に削ってよい。"),
    "obstinate": ("頑固な", "形容詞", "An obstinate stain remained on the carpet after three attempts.", "3度試した後も、頑固なしみがじゅうたんに残っていた。"),
    # Q16
    "gaudy": ("けばけばしい、派手な", "形容詞", "He wore a gaudy tie that everyone remembered afterward.", "彼は皆が後々まで覚えているような派手なネクタイをしていた。"),
    "raucous": ("耳障りな、騒々しい", "形容詞", "Raucous laughter from the next room drowned the announcement.", "隣室からの騒々しい笑い声が知らせをかき消した。"),
    "sadistic": ("加虐的な、残忍な", "形容詞", "The sadistic villain of the novel is oddly convincing to most readers.", "その小説の残忍な悪役は、たいていの読者に奇妙なほど説得力がある。"),
    "irrefutable": ("反論できない", "形容詞", "The water samples provided irrefutable evidence of long-term contamination.", "その水の試料は長期にわたる汚染の反論できない証拠を提供した。"),
    # Q17
    "prodigious": ("驚異的な、莫大な", "形容詞", "He had a prodigious memory for names, dates and old telephone numbers.", "彼は名前や日付、古い電話番号について驚異的な記憶力を持っていた。"),
    "leery": ("警戒している、疑っている", "形容詞", "Investors are leery of promises that sound too precise.", "投資家は正確すぎる響きの約束を警戒している。"),
    "impalpable": ("触れられない、感じ取れない", "形容詞", "There was an impalpable tension in the room before the vote.", "採決の前、部屋には形にならない緊張が漂っていた。"),
    "flagrant": ("目に余る、露骨な", "形容詞", "The referee sent him off for a flagrant foul.", "主審は目に余る反則で彼を退場させた。"),
    # Q18
    "invincible": ("無敵の、打ち負かせない", "形容詞", "The team looked invincible until the final ten minutes.", "そのチームは最後の10分まで無敵に見えた。"),
    "pitiless": ("情け容赦のない", "形容詞", "A pitiless wind swept the ridge for the whole afternoon.", "情け容赦のない風が午後中ずっと尾根を吹き抜けた。"),
    "incessant": ("絶え間ない", "形容詞", "Incessant rain kept the excavation closed for a fortnight.", "絶え間ない雨が2週間その発掘現場を閉ざしたままにした。"),
    "incremental": ("漸進的な、少しずつの", "形容詞", "The gains were incremental but they held year after year.", "その伸びはわずかずつだったが、年ごとに維持された。"),
    # Q19
    "measly": ("わずかな、けちな", "形容詞", "They offered a measly discount that nobody bothered to claim.", "彼らはわずかな割引を提示したが、誰もわざわざ請求しなかった。"),
    "savvy": ("実務に明るい、抜け目のない", "形容詞", "A savvy buyer would have checked the roof before bidding.", "抜け目のない買い手なら入札の前に屋根を確認しただろう。"),
    "precipitous": ("非常に険しい、急激な", "形容詞", "The precipitous slope above the village is planted with vines.", "村の上の急峻な斜面にはブドウが植えられている。"),
    "fluorescent": ("蛍光の", "形容詞", "Workers wear fluorescent jackets on every part of the site.", "作業員は現場のどの区域でも蛍光色の上着を着用する。"),
    # Q20
    "listless": ("気力のない、物憂げな", "形容詞", "The heat left the horses listless for most of the day.", "暑さは一日のほとんど、馬たちを気力のない状態にした。"),
    "inflatable": ("膨らませられる", "形容詞", "Each boat carries an inflatable raft under the rear seat.", "各ボートは後部座席の下に膨らませられる救命いかだを積んでいる。"),
    "exorbitant": ("法外な、途方もない", "形容詞", "The garage charged an exorbitant fee for a simple repair.", "その修理工場は簡単な修理に法外な料金を請求した。"),
    "sanguine": ("楽観的な", "形容詞", "She remains sanguine about the harvest despite the dry spring.", "乾いた春にもかかわらず、彼女は収穫について楽観的なままである。"),
    # Q21
    "figuratively": ("比喩的に", "副詞", "He meant it figuratively, though the phrase sounded alarming.", "その言い回しは物騒に聞こえたが、彼は比喩的な意味で言っていた。"),
    "diabolically": ("悪魔のように、極悪に", "副詞", "The puzzle is diabolically difficult in its final stage.", "そのパズルは最終段階が悪魔的に難しい。"),
    "adamantly": ("断固として", "副詞", "The owners adamantly refused to sell any part of the land.", "所有者たちはその土地のいかなる部分も売ることを断固拒否した。"),
    "fervently": ("熱烈に、熱心に", "副詞", "He fervently hoped that the letter had gone astray.", "彼はその手紙が行方不明になっていることを熱烈に願った。"),
    # Q22
    "run up against": ("(困難に)突き当たる", "句動詞", "Anyone restoring these houses will run up against the same damp.", "これらの家を修復する者は誰でも同じ湿気の問題に突き当たる。"),
    "look back on": ("(~を)振り返る", "句動詞", "She can look back on forty years in the same classroom.", "彼女は同じ教室での40年を振り返ることができる。"),
    "fall in with": ("(~と)親しくなる、同調する", "句動詞", "He began to fall in with a group that met behind the station.", "彼は駅の裏で集まる一団と付き合い始めた。"),
    "simmer down": ("落ち着く、静まる", "句動詞", "The crowd began to simmer down once the music stopped.", "音楽が止まると群衆は落ち着き始めた。"),
    # Q23
    "horse around": ("ふざけ回る", "句動詞", "The boys would horse around in the corridor between lessons.", "少年たちは授業の合間に廊下でふざけ回っていた。"),
    "live down": ("(汚名を)そそぐ、忘れさせる", "句動詞", "He never managed to live down the nickname he earned that summer.", "彼はその夏についたあだ名を、ついに忘れさせることができなかった。"),
    "hike up": ("(値段を)つり上げる、引き上げる", "句動詞", "Sellers hike up prices in the week before the festival.", "売り手は祭りの前の週に値段をつり上げる。"),
    "thumb through": ("(本などを)ざっとめくる", "句動詞", "He would thumb through the atlas whenever he was waiting.", "彼は待たされるといつも地図帳をぱらぱらとめくっていた。"),
    # Q24
    "squared off against": ("(~と)対決した", "句動詞", "The champion squared off against a challenger fifteen years younger.", "その王者は15歳年下の挑戦者と対決した。"),
    "ganged up on": ("(~を)寄ってたかって攻撃した", "句動詞", "Three of the older birds ganged up on the newcomer.", "年長の鳥3羽が新入りに寄ってたかって攻撃した。"),
    "tore into": ("(~を)激しく攻撃した、酷評した", "句動詞", "The columnist tore into a policy she had once supported.", "そのコラムニストは、かつて自ら支持した政策を激しく攻撃した。"),
    "got away with": ("(罰を受けずに)済ませた", "句動詞", "For years he got away with charging tourists double.", "何年もの間、彼は観光客に倍額を請求しても罰を免れていた。"),
    # Q25
    "boils down to": ("結局(~に)帰着する", "句動詞", "The whole question boils down to who pays for the repairs.", "問題全体は結局、誰が修理費を払うのかに帰着する。"),
    "comes down on": ("(~を)厳しく取り締まる、叱る", "句動詞", "The city comes down on drivers who park across the cycle lane.", "市は自転車レーンをふさいで駐車する運転者を厳しく取り締まる。"),
    "gets back at": ("(~に)仕返しをする", "句動詞", "Nobody benefits when one department gets back at another.", "ある部署が別の部署に仕返しをしても、誰の得にもならない。"),
    "smooths over": ("(問題を)丸く収める", "句動詞", "A good chair smooths over disagreements before they harden.", "優れた議長は、対立が固まる前にそれを丸く収める。"),
}


CORE_IMAGES = {
    "run up against": {
        "chain": [
            {"term": "run", "gloss": "進む"},
            {"term": "up", "gloss": "そこまで近づいて"},
            {"gloss": "進んだ先で壁のような相手に近づいて"},
            {"gloss": "困難に突き当たる"},
        ],
        "particle": "up",
        "particleSense": "approach",
    },
    "look back on": {
        "chain": [
            {"term": "look", "gloss": "見る"},
            {"term": "back", "gloss": "過ぎた方へ戻して"},
            {"gloss": "視線を過ぎた時間の方へ戻して"},
            {"gloss": "~を振り返る"},
        ],
        "particle": "back",
    },
    "fall in with": {
        "chain": [
            {"term": "fall", "gloss": "落ちる、加わる"},
            {"term": "in", "gloss": "その一団の中へ入って"},
            {"gloss": "歩調を合わせて一団の中へ入って"},
            {"gloss": "~と親しくなる、同調する"},
        ],
        "particle": "in",
    },
    "simmer down": {
        "chain": [
            {"term": "simmer", "gloss": "ぐつぐつ煮える"},
            {"term": "down", "gloss": "火勢を落として"},
            {"gloss": "煮立ちが弱まるように勢いを落として"},
            {"gloss": "落ち着く"},
        ],
        "particle": "down",
        "particleSense": "reduce",
    },
    "horse around": {
        "chain": [
            {"term": "horse", "gloss": "馬のように跳ね回る"},
            {"term": "around", "gloss": "あたりを動き回って"},
            {"gloss": "目的もなくあたりを跳ね回って"},
            {"gloss": "ふざけ回る"},
        ],
        "particle": "around",
    },
    "live down": {
        "chain": [
            {"term": "live", "gloss": "生きて過ごす"},
            {"term": "down", "gloss": "評判を静めて"},
            {"gloss": "時間をかけて悪い評判を静めて"},
            {"gloss": "汚名を忘れさせる"},
        ],
        "particle": "down",
        "particleSense": "reduce",
    },
    "hike up": {
        "chain": [
            {"term": "hike", "gloss": "ぐいと引き上げる"},
            {"term": "up", "gloss": "高いほうへ"},
            {"gloss": "値や位置をぐいと高いほうへ引き上げて"},
            {"gloss": "つり上げる"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "thumb through": {
        "chain": [
            {"term": "thumb", "gloss": "親指でめくる"},
            {"term": "through", "gloss": "端から端まで通して"},
            {"gloss": "親指でページを端から端まで送って"},
            {"gloss": "ざっとめくって見る"},
        ],
    },
    "squared off against": {
        "chain": [
            {"term": "square", "gloss": "身構える"},
            {"term": "off", "gloss": "距離を取って向き合って"},
            {"gloss": "間合いを取って正面から向き合って"},
            {"gloss": "~と対決する"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "ganged up on": {
        "chain": [
            {"term": "gang", "gloss": "徒党を組む"},
            {"term": "up", "gloss": "一団にまとまって"},
            {"gloss": "何人もが一団にまとまって一人へ向かって"},
            {"gloss": "寄ってたかって攻撃する"},
        ],
    },
    "tore into": {
        "chain": [
            {"term": "tear", "gloss": "引き裂く"},
            {"term": "into", "gloss": "相手の中へ入り込んで"},
            {"gloss": "相手の内側まで引き裂くように攻めて"},
            {"gloss": "激しく攻撃する、酷評する"},
        ],
        "particle": "into",
    },
    "got away with": {
        "chain": [
            {"term": "get", "gloss": "手に入れる"},
            {"term": "away", "gloss": "その場から離れて"},
            {"gloss": "咎めを受けずに手にしたまま離れて"},
            {"gloss": "罰を免れる"},
        ],
        "particle": "away",
    },
    "boils down to": {
        "chain": [
            {"term": "boil", "gloss": "煮詰める"},
            {"term": "down", "gloss": "量を減らして"},
            {"gloss": "煮詰めて中身を減らし要点だけ残して"},
            {"gloss": "結局~に帰着する"},
        ],
        "particle": "down",
        "particleSense": "reduce",
    },
    "comes down on": {
        "chain": [
            {"term": "come", "gloss": "来る"},
            {"term": "down", "gloss": "上から押さえつけて"},
            {"gloss": "権限のある側が上から押さえつけて"},
            {"gloss": "厳しく取り締まる"},
        ],
        "particle": "down",
        "particleSense": "suppress",
    },
    "gets back at": {
        "chain": [
            {"term": "get", "gloss": "手を出す"},
            {"term": "back", "gloss": "受けた分を返して"},
            {"gloss": "やられた分を相手へ返して"},
            {"gloss": "仕返しをする"},
        ],
        "particle": "back",
    },
    "smooths over": {
        "chain": [
            {"term": "smooth", "gloss": "なめらかにする"},
            {"term": "over", "gloss": "全体を覆うように"},
            {"gloss": "ざらついた部分を全体になでつけて"},
            {"gloss": "問題を丸く収める"},
        ],
        "particle": "over",
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
        raise ValueError("模試第19回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-19 割り当てに従う",
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
