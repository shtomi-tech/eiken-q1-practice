"""ユーザー提供の英検1級「模試 第1回」をQ1形式へ変換する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-1"


QUESTIONS = [
    {
        "stem": "Joey took a bad fall while he was snowboarding earlier this month. He hit his head, suffering a mild ( ). Doctors advised him to always wear a helmet in the future.",
        "choices": ["concussion", "infraction", "preclusion", "retribution"],
        "answerIndex": 0,
        "translation": "ジョーイは今月初め、スノーボード中にひどく転んだ。頭を打ち、軽い脳震盪を起こした。医師は今後必ずヘルメットを着用するよう助言した。",
    },
    {
        "stem": "In ( ), I probably should have finished college, but at the time all I could think about was traveling the world and meeting new people.",
        "choices": ["thrift", "affability", "dud", "retrospect"],
        "answerIndex": 3,
        "translation": "振り返ってみると、私はおそらく大学を卒業しておくべきだったが、当時は世界を旅して新しい人々に会うことしか考えられなかった。",
    },
    {
        "stem": "A: Diane, you have such good posture.\nB: Thank you. It's probably because my mom was always telling me to stop ( ) as a child.",
        "choices": ["darting", "slouching", "wedging", "defecting"],
        "answerIndex": 1,
        "translation": "A：ダイアン、姿勢がとてもいいね。\nB：ありがとう。子どものころ、母にいつも猫背をやめなさいと言われていたからだと思う。",
    },
    {
        "stem": "This new car-sharing app ( ) the recently popular sharing economy. It is a great example of how people are using technology to come together and help one another.",
        "choices": ["exhorts", "typifies", "dispirits", "omits"],
        "answerIndex": 1,
        "translation": "この新しいカーシェアリングアプリは、最近人気のシェアリングエコノミーを典型的に示している。人々がテクノロジーを使って集まり、助け合っている好例だ。",
    },
    {
        "stem": 'A: Hey, have you seen what they\'re saying on the news about Saving Our Kids?\nB: Yeah, that\'s really horrible. All these years they\'ve been taking charitable donations, but really it was all just a ( ).',
        "choices": ["clemency", "demise", "melancholy", "scam"],
        "answerIndex": 3,
        "translation": "A：Saving Our Kidsについてニュースで何と言われているか見た？\nB：うん、本当にひどいね。何年も慈善寄付を集めていたけれど、実は全部ただの詐欺だったんだ。",
    },
    {
        "stem": 'A: This is the dirtiest hotel I\'ve ever seen.\nB: Yeah, I think "Greenhill Luxury Suites" is a bit of a ( ). They should rename it "Garbage Rooms."',
        "choices": ["supposition", "quirk", "misnomer", "wrench"],
        "answerIndex": 2,
        "translation": "A：こんなに汚いホテルは初めて見た。\nB：そうだね。「グリーンヒル・ラグジュアリー・スイーツ」という名前は少し誤称だと思う。「ごみ部屋」に改名すべきだよ。",
    },
    {
        "stem": "After he managed to land the malfunctioning plane, the pilot was immediately ( ). They wanted to know exactly what had gone wrong during the flight.",
        "choices": ["filtered", "alleged", "tethered", "debriefed"],
        "answerIndex": 3,
        "translation": "故障した飛行機を何とか着陸させた後、パイロットはすぐに事情聴取を受けた。彼らは飛行中に何が起きたのかを正確に知りたかった。",
    },
    {
        "stem": "I got to visit the executive's condo in New York last weekend, which was just as ( ) as the man himself. It was stylish, clean, and clearly worth a lot of money.",
        "choices": ["abominable", "impertinent", "lethal", "sleek"],
        "answerIndex": 3,
        "translation": "先週末、ニューヨークにあるその重役のマンションを訪ねたが、本人と同じくらい洗練されていた。おしゃれで清潔で、明らかに高価だった。",
    },
    {
        "stem": "Only ten years ago, this technology was still quite ( ), and although it may seem advanced now, we are still only seeing a fraction of its true potential.",
        "choices": ["torrid", "irresolute", "rudimentary", "amenable"],
        "answerIndex": 2,
        "translation": "わずか10年前、この技術はまだかなり初歩的だった。今は先進的に見えるかもしれないが、私たちはまだ本当の可能性のほんの一部しか見ていない。",
    },
    {
        "stem": "A: It seems that Dr. Rogers isn't very popular among the other researchers.\nB: That's because he often shows ( ) in his remarks about what we do here. Our research is supposed to be top-secret.",
        "choices": ["stipulation", "provision", "annotation", "indiscretion"],
        "answerIndex": 3,
        "translation": "A：ロジャース博士は他の研究者たちにあまり人気がないようだね。\nB：ここで行っていることについて、発言で軽率に秘密を漏らすことが多いからだよ。私たちの研究は極秘のはずなのに。",
    },
    {
        "stem": "When Marissa found herself alone with the famous author, she ( ) on the opportunity to ask him questions about how to write good stories.",
        "choices": ["splashed", "hastened", "capitalized", "relented"],
        "answerIndex": 2,
        "translation": "マリッサは有名な作家と二人きりになると、よい物語の書き方について質問する機会を活用した。",
    },
    {
        "stem": "The mayor's popularity has ( ) throughout the year, as he has experienced times of both widespread admiration and considerable criticism.",
        "choices": ["fluctuated", "bolted", "deteriorated", "chuckled"],
        "answerIndex": 0,
        "translation": "市長は広く称賛される時期と激しく批判される時期の両方を経験し、年間を通じて人気が変動した。",
    },
    {
        "stem": "Jennifer did not realize that her work visa was no longer valid after changing jobs, and she faced ( ) for overstaying her visa.",
        "choices": ["deportation", "insurrection", "elocution", "disposition"],
        "answerIndex": 0,
        "translation": "ジェニファーは転職後、就労ビザがもう有効でないことに気づかず、滞在期間を超過したため強制送還に直面した。",
    },
    {
        "stem": "There were a few times when Marvin was sure that their business was going to fail, but his partner's ( ) attitude helped him to stay positive, and in the end the company was a huge success.",
        "choices": ["penitent", "studious", "soggy", "irrepressible"],
        "answerIndex": 3,
        "translation": "マービンが事業は失敗すると確信したことが何度かあったが、パートナーの抑えきれないほど前向きな態度が彼を明るく保ち、結局会社は大成功した。",
    },
    {
        "stem": "The woman was arrested by border authorities when she tried to use ( ) travel documents to gain access to the country.",
        "choices": ["roguish", "cerebral", "intricate", "fraudulent"],
        "answerIndex": 3,
        "translation": "その女性は入国するために偽造された旅行書類を使おうとして、国境当局に逮捕された。",
    },
    {
        "stem": "Everyone in the sales team was shocked when the new representative had the ( ) to blame their manager instead of acknowledging his own mistake.",
        "choices": ["spillage", "gristle", "audacity", "rehash"],
        "answerIndex": 2,
        "translation": "新しい担当者が自分の過ちを認めず、上司を責めるとは、その営業チームの全員がその厚かましさに驚いた。",
    },
    {
        "stem": "At that age, the baby birds are still not able to eat solid food, so the mother eats it first, then ( ) it for them to eat.",
        "choices": ["regurgitates", "illuminates", "truncates", "fumigates"],
        "answerIndex": 0,
        "translation": "その年齢では、ひな鳥はまだ固形物を食べられないため、母鳥が先に食べてから、ひなたちのために吐き戻す。",
    },
    {
        "stem": "A: How much does it cost to apply?\nB: Usually it costs $80. However, the school will ( ) the application fee for any low-income students.",
        "choices": ["exude", "debilitate", "waive", "diversify"],
        "answerIndex": 2,
        "translation": "A：申し込みにはいくらかかりますか。\nB：通常は80ドルです。ただし、学校は低所得の学生について申請料を免除します。",
    },
    {
        "stem": "They gave her the medicine via an ( ) drip, as that was more effective than taking it orally.",
        "choices": ["illustrious", "imperious", "extraneous", "intravenous"],
        "answerIndex": 3,
        "translation": "経口で服用するより効果的だったため、彼らは静脈内点滴で彼女に薬を投与した。",
    },
    {
        "stem": "After the car accident, doctors told Matthew that he'd be lucky to ever walk again, let alone run. However, he overcame seemingly ( ) odds, and ten years later he ran his first marathon.",
        "choices": ["insurmountable", "insolent", "roundabout", "senile"],
        "answerIndex": 0,
        "translation": "交通事故の後、医師はマシューに、走るどころか再び歩けたら幸運だと言った。しかし彼は一見克服不可能な困難を乗り越え、10年後には初めてマラソンを走った。",
    },
    {
        "stem": "After Rudy's son got into a fight with a bully at school, he told his son that, although he didn't ( ) violence, he sympathized with his desire to protect his classmate.",
        "choices": ["invert", "condone", "mortify", "embroil"],
        "answerIndex": 1,
        "translation": "ルディの息子が学校でいじめっ子とけんかをした後、ルディは暴力を容認はしないが、同級生を守りたい気持ちには共感すると息子に伝えた。",
    },
    {
        "stem": "The police have started ( ) on drunk drivers. Arrests for drinking and driving have gone up over 200% in the last month.",
        "choices": ["carrying over", "cracking down", "hanging out", "wasting away"],
        "answerIndex": 1,
        "translation": "警察は飲酒運転者の厳しい取り締まりを始めた。飲酒運転による逮捕者は先月、200％以上増加した。",
    },
    {
        "stem": "A: ( ) it, Wendy! If we don't finish this project tonight, we're going to fail this class.\nB: Sorry, Meg. I just keep thinking about what Vince said to me earlier.",
        "choices": ["Snap out of", "Act up to", "Hold out on", "Stand up to"],
        "answerIndex": 0,
        "translation": "A：ウェンディ、しっかりして！今夜この課題を終えなければ、この授業に落ちてしまうよ。\nB：ごめん、メグ。さっきヴィンスに言われたことが頭から離れないの。",
    },
    {
        "stem": "Steve tried to ( ) the reasons for his decision to quit his job, but his wife was not interested in hearing his explanation.",
        "choices": ["lay out", "drum up", "settle on", "seal off"],
        "answerIndex": 0,
        "translation": "スティーブは仕事を辞める決断の理由を説明しようとしたが、妻は彼の説明を聞くことに関心がなかった。",
    },
    {
        "stem": "A: I told my boss that I noticed some money missing from one of our accounts, and he offered to give me a raise if I just ignored it.\nB: He thinks that you can just be ( ) like that? What did you say to him?",
        "choices": ["bargained on", "bought off", "eked out", "soaked up"],
        "answerIndex": 1,
        "translation": "A：口座の一つからお金がなくなっていることに気づいたと上司に伝えたら、見て見ぬふりをすれば昇給すると言われた。\nB：そんなふうに買収できると思っているの？何て答えたの？",
    },
]


DETAILS = {
    "concussion": ("脳震盪", "名詞", "The doctor diagnosed him with a mild concussion after the fall.", "医師は転倒後、彼を軽い脳震盪と診断した。"),
    "infraction": ("（規則の）違反", "名詞", "The referee called the late tackle an infraction.", "審判は遅れて入ったタックルを反則と判定した。"),
    "preclusion": ("排除、妨げ", "名詞", "The rule allows preclusion of applicants who submit false documents.", "その規則は、虚偽の書類を提出した申請者を排除することを認めている。"),
    "retribution": ("報復、仕返し", "名詞", "The attack was presented as retribution for the earlier bombing.", "その攻撃は、先の爆撃への報復として説明された。"),
    "thrift": ("倹約", "名詞", "Her thrift allowed her to save enough for a small house.", "彼女は倹約によって小さな家を買えるだけのお金を貯めた。"),
    "affability": ("愛想のよさ、親しみやすさ", "名詞", "The host's affability made every guest feel welcome.", "司会者の愛想のよさで、すべての客が歓迎されていると感じた。"),
    "dud": ("失敗作、役立たず", "名詞", "The expensive gadget turned out to be a dud.", "その高価な機器は、結局のところ失敗作だった。"),
    "retrospect": ("回顧、振り返って", "名詞", "In retrospect, taking that job was the right decision.", "振り返ってみると、あの仕事を受けたのは正しい決断だった。"),
    "darting": ("素早く走る、突進する", "動詞", "A young deer was darting across the trail whenever hikers approached.", "ハイカーが近づくたびに、若いシカが小道を素早く横切っていた。"),
    "slouching": ("前かがみでだらしなく座ること", "動詞", "Slouching at a desk can cause back pain.", "机で前かがみになると、背中が痛くなることがある。"),
    "wedging": ("差し込む、押し込む", "動詞", "He was wedging a chair under the door handle.", "彼はドアの取っ手の下に椅子を押し込んでいた。"),
    "defecting": ("離反すること", "動詞", "The spy was arrested while defecting to the other side.", "そのスパイは相手側へ離反しようとして逮捕された。"),
    "exhorts": ("強く促す、激励する", "動詞", "The coach exhorts the players to keep trying.", "コーチは選手たちに挑戦し続けるよう強く促す。"),
    "typifies": ("典型的に示す", "動詞", "This quiet village typifies life in the northern region.", "この静かな村は北部地域の暮らしを典型的に示している。"),
    "dispirits": ("落胆させる", "動詞", "The defeat dispirits the determined team, but it keeps trying.", "その敗北は意志の強いチームを落胆させるが、チームは挑戦を続ける。"),
    "omits": ("省く、記載しない", "動詞", "The revised report omits several figures that the auditors need to verify.", "改訂版の報告書は、監査人が確認する必要のある数字をいくつか省いている。"),
    "clemency": ("慈悲、寛大な処置", "名詞", "The prisoner appealed to the governor for clemency.", "その囚人は知事に慈悲を求めた。"),
    "demise": ("死、終焉", "名詞", "The newspaper reported the demise of the old theater.", "その新聞は古い劇場の終焉を報じた。"),
    "melancholy": ("憂鬱、物悲しさ", "名詞", "The fading light over the empty harbor filled her with melancholy.", "無人の港に差す薄れゆく光を見て、彼女は物悲しい気持ちになった。"),
    "scam": ("詐欺", "名詞", "The email was a scam designed to steal bank details.", "そのメールは銀行情報を盗むための詐欺だった。"),
    "supposition": ("仮定、推測", "名詞", "His conclusion was based on a supposition rather than evidence.", "彼の結論は証拠ではなく推測に基づいていた。"),
    "quirk": ("風変わりな癖", "名詞", "One quirk of the old clock is that it rings twice at noon.", "その古時計の風変わりな癖の一つは、正午に2回鳴ることだ。"),
    "misnomer": ("誤った名称、誤称", "名詞", "Calling the tiny room a ballroom is a misnomer.", "その小さな部屋を舞踏室と呼ぶのは誤称だ。"),
    "wrench": ("激しい苦痛；ねじる道具", "名詞", "Leaving his childhood home was an emotional wrench for him.", "幼少期を過ごした家を離れることは、彼にとって精神的に大きな苦痛だった。"),
    "filtered": ("ろ過した、選別した", "動詞", "The technician filtered the water before testing it.", "技術者は検査前に水をろ過した。"),
    "alleged": ("申し立てられた、疑惑の", "形容詞", "The alleged fraud was investigated after several customers filed complaints.", "複数の顧客が苦情を申し立てた後、疑惑の詐欺が調査された。"),
    "tethered": ("つなぎ留めた", "動詞", "The hikers tethered the horses near the river.", "ハイカーたちは川の近くで馬をつないだ。"),
    "debriefed": ("任務後に事情聴取した", "動詞", "The rescue team was debriefed after returning to base.", "救助隊は基地に戻った後、任務について報告を求められた。"),
    "abominable": ("非常にひどい、忌まわしい", "形容詞", "The hikers abandoned the campsite because the bathroom conditions were abominable.", "浴室の状態がひどかったため、ハイカーたちはキャンプ場を後にした。"),
    "impertinent": ("生意気な、無礼な", "形容詞", "The clerk was dismissed for making an impertinent remark.", "その店員は生意気な発言をしたため解雇された。"),
    "lethal": ("致命的な", "形容詞", "The snake's bite can be lethal without treatment.", "そのヘビのかみ傷は、治療しなければ致命的になることがある。"),
    "sleek": ("なめらかで洗練された", "形容詞", "The company launched a sleek new electric car.", "その会社は洗練された新しい電気自動車を発表した。"),
    "torrid": ("猛暑の、灼熱の", "形容詞", "The players practiced through a torrid afternoon despite the oppressive heat.", "選手たちは、息苦しい暑さにもかかわらず、猛暑の午後を通して練習した。"),
    "irresolute": ("優柔不断な", "形容詞", "The irresolute committee postponed the vote for a third time.", "優柔不断な委員会は投票を3度目も延期した。"),
    "rudimentary": ("初歩的な、未発達な", "形容詞", "The remote clinic had only rudimentary equipment for emergency treatment.", "その遠隔地の診療所には、緊急治療用の初歩的な設備しかなかった。"),
    "amenable": ("受け入れやすい、従順な", "形容詞", "The committee was amenable to a reasonable compromise.", "委員会は妥当な妥協案を受け入れる用意があった。"),
    "stipulation": ("条件、規定", "名詞", "The contract includes a stipulation about working hours.", "その契約には勤務時間に関する条件が含まれている。"),
    "provision": ("条項、備え", "名詞", "The law contains a provision for emergency aid.", "その法律には緊急支援の条項がある。"),
    "annotation": ("注釈", "名詞", "The professor added an annotation to the difficult passage.", "教授は難しい箇所に注釈を加えた。"),
    "indiscretion": ("軽率な言動、秘密漏洩", "名詞", "One careless indiscretion exposed the confidential plan to the rival company.", "一度の軽率な言動で、秘密の計画が競合会社に知られてしまった。"),
    "splashed": ("はねかけた", "動詞", "The passing truck splashed mud on my coat.", "通り過ぎたトラックが私のコートに泥をはねかけた。"),
    "hastened": ("急いだ、促進した", "動詞", "She hastened to the station when she heard the announcement.", "彼女はアナウンスを聞くと駅へ急いだ。"),
    "capitalized": ("利用した、活用した", "動詞", "The small shop capitalized on the sudden tourist boom.", "その小さな店は突然の観光客増加を活用した。"),
    "relented": ("折れた、態度を和らげた", "動詞", "The teacher finally relented and extended the deadline.", "先生はついに折れて締め切りを延ばした。"),
    "fluctuated": ("変動した", "動詞", "The exchange rate fluctuated sharply as investors reacted to the unexpected announcement.", "投資家が予想外の発表に反応する中、為替レートは大きく変動した。"),
    "bolted": ("急に走り去った", "動詞", "The startled horse bolted toward the open field.", "驚いた馬は開けた野原へ急に走り去った。"),
    "deteriorated": ("悪化した", "動詞", "Road conditions deteriorated rapidly after heavy rain washed away the hillside.", "大雨で斜面が流された後、道路状況は急速に悪化した。"),
    "chuckled": ("くすくす笑った", "動詞", "The professor chuckled when a student offered an unexpectedly clever answer.", "学生が思いがけず気の利いた答えを出すと、教授はくすくす笑った。"),
    "deportation": ("強制送還", "名詞", "The court ordered his deportation after the visa violation.", "裁判所はビザ違反の後、彼の強制送還を命じた。"),
    "insurrection": ("反乱、暴動", "名詞", "The government declared a state of emergency after the insurrection.", "政府は反乱の後、非常事態を宣言した。"),
    "elocution": ("発音・朗読法", "名詞", "The actor took elocution lessons before the play opened.", "その俳優は初演前に発音・朗読法のレッスンを受けた。"),
    "disposition": ("気質、処分", "名詞", "Her cheerful disposition helped the team through the difficult week.", "彼女の明るい気質が、困難な週を乗り切るチームの助けになった。"),
    "penitent": ("悔い改めた、後悔している", "形容詞", "The penitent official apologized publicly and promised to repair the damage.", "後悔している役人は公に謝罪し、損害を修復すると約束した。"),
    "studious": ("勉強熱心な", "形容詞", "Her studious approach to every assignment impressed the demanding instructor.", "どの課題にも勉強熱心に取り組む彼女の姿勢は、厳しい講師に感銘を与えた。"),
    "soggy": ("びしょ濡れの、ふやけた", "形容詞", "The soggy newspaper fell apart in my hands.", "びしょ濡れの新聞は手の中でばらばらになった。"),
    "irrepressible": ("抑えきれない、非常に前向きな", "形容詞", "His irrepressible optimism kept the volunteers working during the long crisis.", "彼の抑えきれない楽観性が、長い危機の間もボランティアたちを働き続けさせた。"),
    "roguish": ("いたずらっぽい", "形容詞", "The child gave a roguish grin after hiding the birthday gift.", "誕生日プレゼントを隠した後、その子どもはいたずらっぽく笑った。"),
    "cerebral": ("脳の、知的な", "形容詞", "The scan revealed cerebral damage that affected the patient's ability to speak.", "スキャンによって、患者の発話能力に影響する脳損傷が明らかになった。"),
    "intricate": ("複雑な、入り組んだ", "形容詞", "The artist designed an intricate pattern for the tile.", "その芸術家はタイルに複雑な模様をデザインした。"),
    "fraudulent": ("不正な、詐欺的な", "形容詞", "The bank froze the account after detecting a fraudulent transfer overseas.", "銀行は海外への不正な送金を検知した後、その口座を凍結した。"),
    "spillage": ("流出、こぼれ", "名詞", "The crew cleaned up the chemical spillage immediately.", "乗組員は化学物質の流出を直ちに処理した。"),
    "gristle": ("軟骨", "名詞", "The old dog had trouble chewing the tough gristle.", "その老犬は硬い軟骨をかむのに苦労した。"),
    "audacity": ("厚かましい大胆さ", "名詞", "I was surprised by her audacity in challenging the director.", "私は、彼女が監督に意見した大胆さに驚いた。"),
    "rehash": ("焼き直し", "名詞", "The sequel felt like a rehash of the first movie.", "その続編は1作目の焼き直しのように感じられた。"),
    "regurgitates": ("吐き戻す、逆流させる", "動詞", "The parent bird regurgitates food for its chicks.", "親鳥はひなたちのために食べ物を吐き戻す。"),
    "illuminates": ("照らす、明らかにする", "動詞", "The diagram illuminates the structure of the machine.", "その図は機械の構造を明らかにする。"),
    "truncates": ("切り詰める、省略する", "動詞", "The software truncates long filenames when it exports them to the archive.", "そのソフトウェアは長いファイル名をアーカイブに書き出す際に切り詰める。"),
    "fumigates": ("燻蒸消毒する", "動詞", "The company fumigates the warehouse once a year.", "その会社は年に一度、倉庫を燻蒸消毒する。"),
    "exude": ("にじみ出る、発散する", "動詞", "The flowers exude a sweet fragrance at night.", "その花は夜に甘い香りを発散する。"),
    "debilitate": ("弱らせる", "動詞", "A long illness can debilitate even a strong athlete.", "長い病気は強い運動選手でさえ弱らせることがある。"),
    "waive": ("放棄する、免除する", "動詞", "The hotel agreed to waive the cancellation fee.", "ホテルはキャンセル料を免除することに同意した。"),
    "diversify": ("多様化する", "動詞", "The company plans to diversify its product line.", "その会社は製品ラインを多様化する計画だ。"),
    "illustrious": ("著名な、輝かしい", "形容詞", "The museum honors the illustrious scientist every year.", "その博物館は毎年、その著名な科学者をたたえている。"),
    "imperious": ("横柄な、尊大な", "形容詞", "The imperious director dismissed every suggestion without explaining her decision.", "横柄な部長は、自分の決定を説明せずにあらゆる提案を退けた。"),
    "extraneous": ("余分な、無関係な", "形容詞", "Please remove any extraneous information from the summary.", "要約から余分な情報を取り除いてください。"),
    "intravenous": ("静脈内の", "形容詞", "The patient received intravenous fluids after the operation.", "患者は手術後、静脈内輸液を受けた。"),
    "insurmountable": ("克服できない、乗り越えがたい", "形容詞", "The team found a way around what seemed like an insurmountable obstacle.", "チームは克服不可能に見えた障害を乗り越える方法を見つけた。"),
    "insolent": ("生意気な、横柄な", "形容詞", "The insolent student refused to follow the simple instruction.", "その生意気な生徒は簡単な指示に従うことを拒んだ。"),
    "roundabout": ("遠回りの、間接的な", "形容詞", "We took a roundabout route to avoid the traffic.", "私たちは渋滞を避けるため遠回りの道を通った。"),
    "senile": ("老衰した、老年性の", "形容詞", "The novel portrays a senile king losing his grip on power.", "その小説は、権力を失っていく老衰した王を描いている。"),
    "invert": ("逆さにする、反転する", "動詞", "Invert the container carefully before mixing the concentrated solution with water.", "濃縮液を水と混ぜる前に、容器を注意深く逆さにしてください。"),
    "condone": ("大目に見る、容認する", "動詞", "The school will not condone bullying of any kind.", "学校はいかなる種類のいじめも容認しない。"),
    "mortify": ("屈辱を与える、悔しがらせる", "動詞", "The unexpected mistake did not mortify her because the team corrected it quickly.", "予想外の間違いが起きたが、チームがすぐに訂正したため、彼女は屈辱を感じなかった。"),
    "embroil": ("巻き込む", "動詞", "The leaked document could embroil the minister in a dispute over public contracts.", "流出した文書によって、大臣は公共契約をめぐる紛争に巻き込まれる可能性がある。"),
    "carrying over": ("持ち越す", "熟語", "The unused budget is carrying over to the next quarter.", "未使用の予算は次の四半期へ持ち越される。"),
    "cracking down": ("厳しく取り締まる", "熟語", "The city is cracking down on illegal parking.", "市は違法駐車を厳しく取り締まっている。"),
    "hanging out": ("ぶらぶら過ごす、遊ぶ", "熟語", "We spent the afternoon hanging out at the park.", "私たちは午後を公園でぶらぶら過ごした。"),
    "wasting away": ("やせ衰える、衰弱する", "熟語", "Without proper care, the abandoned garden was wasting away.", "適切な世話がなく、その放置された庭は衰えていった。"),
    "Snap out of": ("ぼんやりした状態から立ち直る", "熟語", "You need to snap out of your gloomy mood and face the problem.", "憂鬱な気分から立ち直って、問題に向き合う必要がある。"),
    "Act up to": ("期待に応えて行動する", "熟語", "The young player tried to act up to the high expectations placed on him.", "その若い選手は寄せられた大きな期待に応えようとした。"),
    "Hold out on": ("隠して与えない、出し惜しみする", "熟語", "Please do not hold out on us when you know the answer.", "答えを知っているなら、私たちに隠さないでください。"),
    "Stand up to": ("立ち向かう", "熟語", "She learned to stand up to the bully and report the incident.", "彼女はいじめっ子に立ち向かい、その出来事を報告することを学んだ。"),
    "lay out": ("説明する、明確に示す", "熟語", "The lawyer will lay out the risks before we sign the contract.", "弁護士は私たちが契約に署名する前にリスクを説明する。"),
    "drum up": ("（支持・仕事など）をかき集める", "熟語", "The campaign tried to drum up support from local residents.", "その運動は地元住民から支持を集めようとした。"),
    "settle on": ("～に決める", "熟語", "After comparing several plans, we will settle on the simplest one.", "いくつかの計画を比較した後、私たちは最も簡単なものに決める。"),
    "seal off": ("封鎖する、立ち入り禁止にする", "熟語", "Police will seal off the street after the accident.", "警察は事故の後、その通りを封鎖する。"),
    "bargained on": ("当てにした、予期した", "熟語", "We had not bargained on such a long delay.", "私たちはこれほど長い遅延を予期していなかった。"),
    "bought off": ("買収した、金で黙らせた", "熟語", "The company bought off the witness with a large payment.", "その会社は多額の支払いで証人を買収した。"),
    "eked out": ("かろうじて得た、やりくりした", "熟語", "She eked out a living by repairing old bicycles.", "彼女は古い自転車を修理して、かろうじて生計を立てた。"),
    "soaked up": ("吸収した、十分に味わった", "熟語", "The children soaked up every detail of the science show.", "子どもたちは科学ショーの細部をすべて吸収した。"),
}


ETYMOLOGY = {
    "concussion": "ラテン語 concutere（激しく揺さぶる）に由来。con-（ともに）＋quatere（揺する）。",
    "infraction": "ラテン語 infringere（壊す、破る）に由来。in-（中へ）＋frangere（壊す）。",
    "preclusion": "ラテン語 praecludere（前もって閉じる、締め出す）に由来。",
    "retribution": "ラテン語 retribuere（返し与える）に由来。re-（返して）＋tribuere（割り当てる）。",
    "thrift": "古ノルド語 þrift（繁栄）に由来し、thrive（栄える）と関係する。",
    "affability": "ラテン語 affabilis（話しかけやすい）に由来。affari（話しかける）と関係する。",
    "dud": "英語の俗語 dud（役に立たないもの）に由来。詳しい語源は確定していない。",
    "retrospect": "ラテン語 retro（後ろへ）＋specere（見る）に由来。後ろを振り返って見ること。",
    "darting": "dart（投げ矢、突進する）＋-ing。矢のように素早く進むこと。",
    "slouching": "slouch（前かがみになる）＋-ing。slouchの詳しい語源は不確か。",
    "wedging": "wedge（くさび、押し込む）＋-ing。wedgeは古英語系の語。",
    "defecting": "ラテン語 defectus（欠けたこと、離脱）に由来する defect＋-ing。",
    "exhorts": "ラテン語 exhortari（強く勧める）に由来する exhort＋三人称語尾 -s。",
    "typifies": "ギリシャ語 typos（型、刻印）＋-ify（〜にする）に由来する typify＋-s。",
    "dispirits": "dis-（離れて、奪って）＋spirit（精神）に由来する dispirit＋-s。",
    "omits": "ラテン語 omittere（手放す、省く）に由来する omit＋-s。",
    "clemency": "ラテン語 clementia（穏やかさ、慈悲）に由来。clemens（穏やかな）と関係する。",
    "demise": "古フランス語 demise（手放すこと）を経て、ラテン語 dimittere（送り去る）と関係する。",
    "melancholy": "ギリシャ語 melas（黒い）＋khole（胆汁）に由来。古い四体液説の『黒胆汁』から憂鬱の意へ。",
    "scam": "英語 scam（詐欺）に由来する比較的新しい俗語。詳しい語源は確定していない。",
    "supposition": "ラテン語 supponere（下に置く）に由来。sup-（下に）＋ponere（置く）。",
    "quirk": "英語 quirk（風変わりな点）に由来。詳しい語源は不確か。",
    "misnomer": "mis-（誤って）＋ギリシャ語 onoma（名前）＋-er。誤った名前を付けること。",
    "wrench": "古英語 wrencan（ねじる）に由来。ねじることから、強い苦痛の意へ。",
    "filtered": "filter（ろ過する、選別する）＋-ed。filterは中世ラテン語 filtrum（ろ過布）に由来。",
    "alleged": "ラテン語 allegare（正式に申し立てる）に由来する allege＋-ed。",
    "tethered": "tether（つなぎ綱、つなぐ）＋-ed。tetherは古英語系の『つなぐ』語とされる。",
    "debriefed": "de-（取り去って）＋brief（要約、報告）に由来する debrief＋-ed。",
    "abominable": "ラテン語 abominari（悪い兆しとして忌み嫌う）に由来。ab-（離れて）＋omen（前兆）。",
    "impertinent": "ラテン語 impertinens（関係のない）に由来。im-（否定）＋pertinere（関係する）。",
    "lethal": "ギリシャ語 lethe（忘却）に由来するラテン語 lethalis（死をもたらす）から。",
    "sleek": "古英語 slīc（滑らかな）に由来。",
    "torrid": "ラテン語 torridus（乾いた、焼けつくような）に由来。torre（焼く）と関係する。",
    "irresolute": "in-（〜でない）＋ラテン語 resolvere（ほどく、決める）に由来。",
    "rudimentary": "ラテン語 rudimentum（出発点、初歩）に由来。rudis（未加工の、未熟な）と関係する。",
    "amenable": "古フランス語 amener（導く、連れて行く）に由来し、意見を受け入れられる意へ。",
    "stipulation": "ラテン語 stipulari（要求する、約束する）に由来。契約上の条件の意へ。",
    "provision": "ラテン語 providere（前もって見る、備える）に由来。pro-（前もって）＋videre（見る）。",
    "annotation": "ラテン語 annotare（注を付ける）に由来。ad-（〜へ）＋nota（印、注記）。",
    "indiscretion": "in-（否定）＋discretion（分別、判断）に由来する語。discretionはラテン語 discernere（見分ける）と関係する。",
    "splashed": "擬音的な英語 splash（ばしゃりとはねる）＋-ed。",
    "hastened": "haste（急ぐこと）＋-ened。hasteは古フランス語を経たゲルマン系の語。",
    "capitalized": "ラテン語 caput（頭）に由来する capital（主要な、資本）＋-ize＋-ed。",
    "relented": "ラテン語 relentare（ゆるめる）に由来する relent＋-ed。",
    "fluctuated": "ラテン語 fluctuare（波打つ、揺れ動く）に由来。fluctus（波）と関係する。",
    "bolted": "bolt（矢、急に走る）＋-ed。boltは古英語系の語。",
    "deteriorated": "ラテン語 deterior（より悪い）に由来する deteriorate＋-ed。",
    "chuckled": "反復音を思わせる英語 chuckle（くすくす笑う）＋-ed。",
    "deportation": "ラテン語 deportare（運び去る）に由来。de-（離れて）＋portare（運ぶ）。",
    "insurrection": "ラテン語 insurgere（立ち上がる）に由来。in-（上へ）＋surgere（立ち上がる）。",
    "elocution": "ラテン語 eloqui（外へ話す）に由来。e-（外へ）＋loqui（話す）。",
    "disposition": "ラテン語 disponere（離して置く、配置する）に由来。dis-（離して）＋ponere（置く）。",
    "penitent": "ラテン語 paenitere（後悔する）に由来。",
    "studious": "ラテン語 studere（熱心に取り組む、学ぶ）に由来。",
    "soggy": "sog（浸す、湿らせる）＋-y。sogの詳しい語源は不確か。",
    "irrepressible": "in-（否定）＋ラテン語 reprimere（押し戻す、抑える）＋-ible。",
    "roguish": "rogue（ならず者、いたずら者）＋-ish。rogueの詳しい語源は不確か。",
    "cerebral": "ラテン語 cerebrum（脳）に由来。",
    "intricate": "ラテン語 intricare（絡ませる、もつれさせる）に由来。",
    "fraudulent": "ラテン語 fraudare（だます）に由来。fraus（詐欺）と関係する。",
    "spillage": "spill（こぼす、流出する）＋-age。spillは古英語 spillanに由来。",
    "gristle": "古英語 gristle（軟骨）に由来。",
    "audacity": "ラテン語 audax（大胆な）に由来。audere（あえてする、挑む）と関係する。",
    "rehash": "re-（再び）＋hash（細かく刻む、寄せ集める）に由来する英語の複合語。",
    "regurgitates": "ラテン語 regurgitare（逆流させる）に由来。re-（戻って）＋gurges（渦、のど）。",
    "illuminates": "ラテン語 illuminare（照らす）に由来。in-/il-（中へ）＋lumen（光）。",
    "truncates": "ラテン語 truncare（切り落とす）に由来する truncate＋-s。",
    "fumigates": "ラテン語 fumigare（煙を出す、燻蒸する）に由来。fumus（煙）と関係する。",
    "exude": "ラテン語 exudare（外へ汗を出す）に由来。ex-（外へ）＋sudare（汗をかく）。",
    "debilitate": "ラテン語 debilitare（弱くする）に由来。de-（離して）＋debilis（弱い）。",
    "waive": "古フランス語 weyver（放棄する、脇へ置く）に由来。",
    "diversify": "ラテン語 diversus（別々の、異なる）に由来する diverse＋-ify（〜にする）。",
    "illustrious": "ラテン語 illustris（明るい、輝かしい）に由来。in-/il-（中へ）＋lustrare（照らす）と関係する。",
    "imperious": "ラテン語 imperare（命令する、支配する）に由来。imperium（支配権）と関係する。",
    "extraneous": "ラテン語 extraneus（外部の、よそ者の）に由来。extra（外に）と関係する。",
    "intravenous": "ラテン語 intra（内側に）＋vena（静脈）に由来。",
    "insurmountable": "in-（否定）＋surmount（乗り越える）＋-able。surmountはラテン語 supermontare（山を越える）に由来。",
    "insolent": "ラテン語 insolens（慣れていない、横柄な）に由来。in-（否定）＋solere（慣れている）。",
    "roundabout": "round（丸い、回り道の）＋about（周囲に）からなる英語の複合語。",
    "senile": "ラテン語 senilis（老人の）に由来。senex（老人）と関係する。",
    "invert": "ラテン語 invertere（向きを逆にする）に由来。in-（反対に）＋vertere（回す）。",
    "condone": "ラテン語 condonare（許す、与え渡す）に由来。con-（完全に）＋donare（与える）。",
    "mortify": "ラテン語 mortificare（死なせる、苦しめる）に由来。mors（死）＋facere（する）。",
    "embroil": "古フランス語 embrouiller（混乱させる）に由来。en-（中へ）＋brouiller（混ぜる）。",
    "carrying over": "carry（運ぶ）＋over（越えて）からなる句動詞。境目を越えて運ぶイメージ。",
    "cracking down": "crack（強く打つ）＋down（押さえつけて）からなる句動詞。強く押さえ込むイメージ。",
    "hanging out": "hang（ぶら下がる）＋out（外で）からなる句動詞。外でぶらぶら過ごすこと。",
    "wasting away": "waste（消耗する）＋away（離れて消える）からなる句動詞。少しずつ衰えること。",
    "Snap out of": "snap（ぱっと弾く）＋out of（〜の外へ）からなる口語的な句動詞。停滞した状態から抜け出すこと。",
    "Act up to": "act（行動する）＋up to（基準まで）からなる句動詞。基準や期待に届くよう行動すること。",
    "Hold out on": "hold（保持する）＋out（外へ出したまま）＋on（相手に対して）からなる句動詞。手元に残して出さないこと。",
    "Stand up to": "stand（立つ）＋up to（〜に対して）からなる句動詞。圧力に負けず立つこと。",
    "lay out": "lay（置く、並べる）＋out（外へ広げて）からなる句動詞。要素を広げて示すこと。",
    "drum up": "drum（太鼓を鳴らす）＋up（盛り上げて）からなる句動詞。呼びかけて支持などを集めること。",
    "settle on": "settle（落ち着く）＋on（〜の上に）からなる句動詞。候補の一つに落ち着いて決めること。",
    "seal off": "seal（封をする）＋off（切り離して）からなる句動詞。封をして閉ざすこと。",
    "bargained on": "bargain（取引する、見込む）＋on（〜を前提に）からなる句動詞。起こると見込むこと。",
    "bought off": "buy（買う）＋off（離れさせて）からなる句動詞。金で相手を味方から離すこと。",
    "eked out": "eke（補う、引き延ばす）＋out（最後まで）からなる句動詞。少ないものを引き延ばして使うこと。",
    "soaked up": "soak（吸い込む）＋up（完全に）からなる句動詞。中へ完全に吸収すること。",
}


CORE_IMAGES = {
    "carrying over": {
        "chain": [
            {"term": "carry", "gloss": "運ぶ"},
            {"term": "over", "gloss": "越えて"},
            {"gloss": "境目を越えて運ぶ"},
            {"gloss": "持ち越す"},
        ],
        "particle": "over",
    },
    "cracking down": {
        "chain": [
            {"term": "crack", "gloss": "打ち砕く"},
            {"term": "down", "gloss": "下へ・押さえつけて"},
            {"gloss": "強く押さえ込む"},
            {"gloss": "厳しく取り締まる"},
        ],
        "particle": "down",
        "particleSense": "suppress",
    },
    "hanging out": {
        "chain": [
            {"term": "hang", "gloss": "ぶら下がる"},
            {"term": "out", "gloss": "外へ・こもらずに"},
            {"gloss": "こもらずに人と一緒にぶらぶら過ごす"},
            {"gloss": "ぶらぶら過ごす、遊ぶ"},
        ],
        "particle": "out",
        "particleSense": "social",
    },
    "wasting away": {
        "chain": [
            {"term": "waste", "gloss": "消耗する・衰える"},
            {"term": "away", "gloss": "離れて消える"},
            {"gloss": "少しずつ力を失う"},
            {"gloss": "やせ衰える、衰弱する"},
        ],
        "particle": "away",
    },
    "Snap out of": {
        "chain": [
            {"term": "snap", "gloss": "ぱっと弾く"},
            {"term": "out", "gloss": "外へ"},
            {"term": "of", "gloss": "〜から"},
            {"gloss": "停滞した状態の外へぱっと出る"},
            {"gloss": "ぼんやりした状態から立ち直る"},
        ],
        "particle": "out",
        "particleSense": "escape",
    },
    "Act up to": {
        "chain": [
            {"term": "act", "gloss": "行動する"},
            {"term": "up to", "gloss": "基準まで"},
            {"gloss": "基準に届くよう行動する"},
            {"gloss": "期待に応えて行動する"},
        ],
        "particle": "up to",
        "particleSense": "standard",
    },
    "Hold out on": {
        "chain": [
            {"term": "hold", "gloss": "保持する"},
            {"term": "out", "gloss": "外へ出したまま"},
            {"term": "on", "gloss": "相手に対して"},
            {"gloss": "手元に保持したまま出さない"},
            {"gloss": "隠して与えない、出し惜しみする"},
        ],
        "particle": "out",
        "particleSense": "reserve",
    },
    "Stand up to": {
        "chain": [
            {"term": "stand", "gloss": "立つ"},
            {"term": "up to", "gloss": "〜に対して"},
            {"gloss": "圧力に負けず立つ"},
            {"gloss": "立ち向かう"},
        ],
        "particle": "up to",
        "particleSense": "confront",
    },
    "lay out": {
        "chain": [
            {"term": "lay", "gloss": "置く・並べる"},
            {"term": "out", "gloss": "外へ広げる"},
            {"gloss": "要素を広げて並べる"},
            {"gloss": "説明する、明確に示す"},
        ],
        "particle": "out",
        "particleSense": "spread",
    },
    "drum up": {
        "chain": [
            {"term": "drum", "gloss": "太鼓を鳴らす"},
            {"term": "up", "gloss": "上へ・盛り上げる"},
            {"gloss": "何度も呼びかけて盛り上げる"},
            {"gloss": "支持・仕事などをかき集める"},
        ],
        "particle": "up",
        "particleSense": "raise",
    },
    "settle on": {
        "chain": [
            {"term": "settle", "gloss": "落ち着く"},
            {"term": "on", "gloss": "〜の上に"},
            {"gloss": "候補の一つに落ち着く"},
            {"gloss": "〜に決める"},
        ],
        "particle": "on",
        "particleSense": "contact",
    },
    "seal off": {
        "chain": [
            {"term": "seal", "gloss": "封をする"},
            {"term": "off", "gloss": "切り離して"},
            {"gloss": "封をして切り離す"},
            {"gloss": "封鎖する、立ち入り禁止にする"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "bargained on": {
        "chain": [
            {"term": "bargain", "gloss": "取引する"},
            {"term": "on", "gloss": "〜を前提に"},
            {"gloss": "起こると見込んで賭ける"},
            {"gloss": "当てにした、予期した"},
        ],
        "particle": "on",
        "particleSense": "rely",
    },
    "bought off": {
        "chain": [
            {"term": "buy", "gloss": "買う"},
            {"term": "off", "gloss": "離れさせる"},
            {"gloss": "金で味方から離す"},
            {"gloss": "買収した、金で黙らせた"},
        ],
        "particle": "off",
        "particleSense": "pull-away",
    },
    "eked out": {
        "chain": [
            {"term": "eke", "gloss": "補う・増やす"},
            {"term": "out", "gloss": "外へ・最後まで"},
            {"gloss": "少ないものを引き伸ばして使う"},
            {"gloss": "かろうじて得た、やりくりした"},
        ],
        "particle": "out",
        "particleSense": "exhaust",
    },
    "soaked up": {
        "chain": [
            {"term": "soak", "gloss": "浸す・吸い込む"},
            {"term": "up", "gloss": "完全に"},
            {"gloss": "中へ完全に吸い込む"},
            {"gloss": "吸収した、十分に味わった"},
        ],
        "particle": "up",
        "particleSense": "complete",
    },
}


BLANK_RE = re.compile(r"\(\s*\)|（\s*）")


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 25:
        raise ValueError("模試 第1回は25問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != len(set(choices)):
        raise ValueError("選択肢に重複があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    missing_etymology = sorted(set(choices) - set(ETYMOLOGY))
    if missing_etymology:
        raise ValueError(f"語源情報がありません: {missing_etymology}")
    missing_core_image = sorted({phrase for phrase in choices if " " in phrase} - set(CORE_IMAGES))
    if missing_core_image:
        raise ValueError(f"熟語の核心イメージがありません: {missing_core_image}")

    for index, question in enumerate(QUESTIONS, start=1):
        if len(question["choices"]) != 4 or question["answerIndex"] not in range(4):
            raise ValueError(f"Q{index}の4択または正答位置が不正です")
        if len(BLANK_RE.findall(question["stem"])) != 1:
            raise ValueError(f"Q{index}の空所が1か所ではありません")
        if any(
            re.search(rf"\b{re.escape(choice)}\b", question["stem"], flags=re.IGNORECASE)
            for choice in question["choices"]
        ):
            raise ValueError(f"Q{index}の選択肢が設問文に含まれています")
        if BLANK_RE.search(question["translation"]):
            raise ValueError(f"Q{index}の和訳に空所記号があります")

    meta = {
        "grade": "英検1級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "ユーザー提供の模試原稿（模試 第1回）を学習用JSONへ構造化",
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
                "etymology": ETYMOLOGY[choice],
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
    vocab_data = {"meta": meta, "words": words, "idioms": idioms}
    return vocab_data, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / "vocab_1_mock-1.json", vocab)
    write_json(DATA_DIR / "questions_1_mock-1.json", questions)
    print("mock-1: 25 questions / 100 items (84 words, 16 idioms)")


if __name__ == "__main__":
    main()
