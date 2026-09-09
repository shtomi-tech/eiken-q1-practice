"""英検1級 模試第14回（自作セット）の問題・語彙データを生成する。

語彙は docs/SET_PLAN_1_mock-10-21.md の mock-14 の割り当てに従う。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-14"
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
PARTICLES = {
    "up", "down", "in", "out", "on", "off", "over", "away", "back", "into", "across",
    "through", "together", "along", "behind", "upon", "under", "around", "by", "about",
    "forward", "for", "with", "at", "to", "against", "from",
}


QUESTIONS = [
    {
        "stem": "The constant roadworks outside the shop were a daily (   ) that cost the owner many customers.",
        "choices": ["aggravation", "abstinence", "compunction", "vice"],
        "answerIndex": 0,
        "translation": "店の外での絶え間ない道路工事は日々の悩みの種であり、店主は多くの客を失った。",
    },
    {
        "stem": "A (   ) broke out between two groups of supporters shortly after the final whistle.",
        "choices": ["calibration", "brawl", "redemption", "edifice"],
        "answerIndex": 1,
        "translation": "試合終了の笛の直後、2組のサポーターの間で乱闘が起こった。",
    },
    {
        "stem": "Faced with a genuine (   ), the committee postponed its decision until the following month.",
        "choices": ["hype", "cognition", "quandary", "felony"],
        "answerIndex": 2,
        "translation": "本当の板挟みに直面し、委員会は決定を翌月まで延期した。",
    },
    {
        "stem": "Infant (   ) in the district fell by half once the new water treatment plant opened.",
        "choices": ["referendum", "zest", "reproach", "mortality"],
        "answerIndex": 3,
        "translation": "新しい浄水場が稼働すると、その地区の乳児死亡率は半分に下がった。",
    },
    {
        "stem": "A bitter (   ) divided the congregation into two groups that never worshipped together again.",
        "choices": ["schism", "dispensation", "diatribe", "sanctity"],
        "answerIndex": 0,
        "translation": "激しい分裂がその信徒集団を2つに分け、二度と一緒に礼拝することはなかった。",
    },
    {
        "stem": "A general (   ) settled on the office in the weeks after the merger was announced.",
        "choices": ["escapade", "epiphany", "malaise", "autocrat"],
        "answerIndex": 2,
        "translation": "合併が発表された後の数週間、全体的な沈滞した空気が職場を覆った。",
    },
    {
        "stem": "The proposal finally gained (   ) only after two national newspapers had described it in detail.",
        "choices": ["grimace", "traction", "animosity", "lesion"],
        "answerIndex": 1,
        "translation": "その提案は2つの全国紙が詳しく報じて初めて、ようやく支持を広げた。",
    },
    {
        "stem": "The council (   ) the rats in the market building over a period of three months.",
        "choices": ["recuperated", "immersed", "ingratiated", "exterminated"],
        "answerIndex": 3,
        "translation": "議会は3か月かけて市場の建物のネズミを駆除した。",
    },
    {
        "stem": "Managers (   ) the junior staff into signing the revised contracts before the end of the month.",
        "choices": ["coerced", "wavered", "hobbled", "bombarded"],
        "answerIndex": 0,
        "translation": "管理職は月末までに若手職員を強制して改定契約書に署名させた。",
    },
    {
        "stem": "A single spark from the welding torch (   ) the sawdust on the workshop floor.",
        "choices": ["adorned", "ignited", "astounded", "derailed"],
        "answerIndex": 1,
        "translation": "溶接トーチからの1つの火花が作業場の床のおがくずに引火した。",
    },
    {
        "stem": "The general (   ) the throne in 1503, shortly after the young heir was sent into exile.",
        "choices": ["mutilated", "weaned", "usurped", "lurked"],
        "answerIndex": 2,
        "translation": "その将軍は若い後継者が追放された直後の1503年に王位を簒奪した。",
    },
    {
        "stem": "The storyteller (   ) the children so completely that not one of them moved for an hour.",
        "choices": ["pounced", "babbled", "dribbled", "enthralled"],
        "answerIndex": 3,
        "translation": "その語り手は子どもたちをすっかり魅了し、1時間の間、誰一人動かなかった。",
    },
    {
        "stem": "He (   ) openly about his rival's defeat, which few of his colleagues found attractive.",
        "choices": ["gloated", "apprehended", "nibbled", "oriented"],
        "answerIndex": 0,
        "translation": "彼は競争相手の敗北について公然と勝ち誇り、同僚のほとんどはそれを好ましく思わなかった。",
    },
    {
        "stem": "The union leader (   ) that the figures had come from the company's own accountants.",
        "choices": ["instigated", "retorted", "stuttered", "embossed"],
        "answerIndex": 1,
        "translation": "組合の指導者は、その数字は会社自身の会計士から出たものだと言い返した。",
    },
    {
        "stem": "The floor of the valley was (   ), with ferns and mosses covering every exposed rock.",
        "choices": ["profound", "ample", "luxuriant", "vulgar"],
        "answerIndex": 2,
        "translation": "その谷底は草木が生い茂り、露出した岩という岩をシダとコケが覆っていた。",
    },
    {
        "stem": "The museum's permanent collection is deliberately (   ), ranging from medieval armor to modern textiles.",
        "choices": ["bumbling", "clairvoyant", "crabby", "eclectic"],
        "answerIndex": 3,
        "translation": "その博物館の常設収蔵品は意図的に多彩で、中世の甲冑から現代の織物にまで及んでいる。",
    },
    {
        "stem": "His account of the delay was (   ), but the timestamps on the recordings contradicted it.",
        "choices": ["plausible", "ubiquitous", "frazzled", "philanthropic"],
        "answerIndex": 0,
        "translation": "遅延についての彼の説明はもっともらしかったが、録音の時刻表示がそれと矛盾していた。",
    },
    {
        "stem": "Sales have been (   ) for three years, neither growing nor falling in any month.",
        "choices": ["preemptive", "stagnant", "resplendent", "wanton"],
        "answerIndex": 1,
        "translation": "売上高は3年間停滞しており、どの月も伸びも落ち込みもしていない。",
    },
    {
        "stem": "The meeting was held at a (   ) location outside the city, and no minutes were kept.",
        "choices": ["somber", "adversarial", "clandestine", "barbarous"],
        "answerIndex": 2,
        "translation": "その会合は市外の秘密の場所で開かれ、議事録は一切残されなかった。",
    },
    {
        "stem": "The lock is an (   ) piece of engineering that uses no springs at all.",
        "choices": ["irate", "covert", "candid", "ingenious"],
        "answerIndex": 3,
        "translation": "その錠はばねをまったく使わない巧妙な工学の産物である。",
    },
    {
        "stem": "The old iron bridge is (   ) expensive to maintain, yet it now carries almost no traffic.",
        "choices": ["stupendously", "posthumously", "semantically", "belligerently"],
        "answerIndex": 0,
        "translation": "その古い鉄橋は維持費が途方もなく高いが、今では交通量はほとんどない。",
    },
    {
        "stem": "Two apprentices (   ) so badly during the busiest week of the year that both were dismissed.",
        "choices": ["goofed off", "let on", "wore down", "milled about"],
        "answerIndex": 0,
        "translation": "2人の見習いは年で最も忙しい週にひどくサボったため、両名とも解雇された。",
    },
    {
        "stem": "The director somehow (   ) a ten-minute scene into almost half of the finished film.",
        "choices": ["bunched up", "shelled out", "spun out", "fenced in"],
        "answerIndex": 2,
        "translation": "その監督はどうにか10分の場面を完成した映画のほぼ半分にまで引き延ばした。",
    },
    {
        "stem": "The new mayor was (   ) at a short ceremony attended by only forty people.",
        "choices": ["tore off", "stubbed out", "swore in", "dragged out"],
        "answerIndex": 2,
        "translation": "新市長はわずか40人が出席する短い式典で宣誓就任した。",
    },
    {
        "stem": "The planners (   ) the outline proposal into a fully detailed scheme over the winter months.",
        "choices": ["fleshed out", "bawled out", "ground up", "leafed through"],
        "answerIndex": 0,
        "translation": "計画担当者たちは冬の数か月で概略案を肉付けし、細部まで詰めた計画に仕上げた。",
    },
]


DETAILS = {
    # Q1
    "aggravation": ("いらだち、悩みの種", "名詞", "The broken lift was a constant aggravation for residents on the eighth floor.", "壊れたエレベーターは8階の住人にとって絶えざる悩みの種だった。"),
    "abstinence": ("節制、禁欲", "名詞", "Complete abstinence from alcohol was a condition of his treatment.", "アルコールの完全な断絶が彼の治療の条件だった。"),
    "compunction": ("良心の呵責", "名詞", "He felt no compunction about charging the tourists twice the usual rate.", "彼は観光客に通常の倍の料金を請求することに何の良心の呵責も感じなかった。"),
    "vice": ("悪徳、悪習", "名詞", "Gambling was the only vice the old sailor ever admitted to.", "賭博はその老水夫が認めた唯一の悪習だった。"),
    # Q2
    "calibration": ("較正、目盛り調整", "名詞", "The calibration of the scales is checked before every shift.", "その秤の較正は各勤務の前に点検される。"),
    "brawl": ("乱闘、けんか", "名詞", "A brawl in the car park ended with three arrests.", "駐車場での乱闘は3人の逮捕で終わった。"),
    "redemption": ("償い、救済", "名詞", "The novel follows one man's slow redemption after a long prison sentence.", "その小説は長い服役の後の一人の男の緩やかな救済を追っている。"),
    "edifice": ("大建造物", "名詞", "The bank occupies a stone edifice built in the 1890s.", "その銀行は1890年代に建てられた石造りの大建築物に入っている。"),
    # Q3
    "hype": ("誇大宣伝", "名詞", "The film never lived up to the hype that preceded its release.", "その映画は公開前の誇大宣伝には決して見合わなかった。"),
    "cognition": ("認知、認識力", "名詞", "Sleep loss affects cognition more severely than most drivers realize.", "睡眠不足は、多くの運転者が思っている以上に認知機能を損なう。"),
    "quandary": ("板挟み、窮地", "名詞", "She was in a quandary about whether to report her own supervisor.", "彼女は自分の上司を報告すべきかどうかで板挟みになっていた。"),
    "felony": ("重罪", "名詞", "The charge was reduced from a felony to a lesser offense.", "その罪状は重罪からより軽い罪へ引き下げられた。"),
    # Q4
    "referendum": ("国民投票、住民投票", "名詞", "The referendum on the new constitution drew a record turnout.", "新憲法についての国民投票は記録的な投票率を集めた。"),
    "zest": ("熱意、風味", "名詞", "He attacked every task with a zest that tired his younger colleagues.", "彼はどの仕事にも、若い同僚を疲れさせるほどの熱意で取り組んだ。"),
    "reproach": ("非難、叱責", "名詞", "There was mild reproach in her voice but no real anger.", "彼女の声には穏やかな非難があったが、本当の怒りはなかった。"),
    "mortality": ("死亡率", "名詞", "Improved sanitation reduced mortality in the crowded districts dramatically.", "衛生状態の改善は過密地区の死亡率を劇的に下げた。"),
    # Q5
    "schism": ("分裂、分派", "名詞", "The schism split the party into two rival organizations.", "その分裂は党を2つの対立組織に割った。"),
    "dispensation": ("特別許可、免除", "名詞", "The couple obtained a special dispensation to marry in the chapel.", "その夫婦は礼拝堂で結婚するための特別許可を得た。"),
    "diatribe": ("痛烈な非難、罵倒", "名詞", "His diatribe against modern architecture filled four newspaper columns.", "現代建築への彼の痛烈な非難は新聞の4段を埋めた。"),
    "sanctity": ("神聖さ、尊厳", "名詞", "The trial turned on the sanctity of confidential medical records.", "その裁判は秘密の診療記録の神聖さをめぐって争われた。"),
    # Q6
    "escapade": ("向こう見ずな行動、無分別な冒険", "名詞", "Their midnight escapade on the roof nearly ended in disaster.", "屋根の上での彼らの真夜中の無謀な行動は、危うく大惨事になるところだった。"),
    "epiphany": ("突然のひらめき、悟り", "名詞", "The solution came to her as a sudden epiphany on the train.", "その解決策は電車の中で突然のひらめきとして彼女に訪れた。"),
    "malaise": ("(社会の)沈滞、不快感", "名詞", "Economic malaise gripped the region for most of the decade.", "経済の沈滞がその10年のほとんどの期間、その地域を覆っていた。"),
    "autocrat": ("独裁者", "名詞", "The company was run by an autocrat who consulted nobody.", "その会社は誰にも相談しない独裁者によって経営されていた。"),
    # Q7
    "grimace": ("しかめ面", "名詞", "A brief grimace crossed his face as he lifted the box.", "箱を持ち上げたとき、彼の顔に一瞬しかめ面がよぎった。"),
    "traction": ("支持の広がり、牽引力", "名詞", "The campaign gained traction after the video was shared widely.", "その動画が広く共有された後、運動は支持を広げた。"),
    "animosity": ("敵意、憎悪", "名詞", "Old animosity between the families resurfaced during the land dispute.", "土地争いの間に、両家の間の古い敵意が再び表面化した。"),
    "lesion": ("病変、損傷", "名詞", "The scan revealed a small lesion on the surface of the liver.", "検査画像は肝臓の表面に小さな病変を示した。"),
    # Q8
    "recuperated": ("回復した、療養した", "動詞", "He recuperated at his sister's house for six weeks after surgery.", "彼は手術の後、姉の家で6週間療養した。"),
    "immersed": ("浸した、没頭させた", "動詞", "She immersed the cloth in dye and left it overnight.", "彼女は布を染料に浸し、一晩そのままにした。"),
    "ingratiated": ("取り入った、機嫌を取った", "動詞", "He ingratiated himself with the committee by praising their earlier report.", "彼は委員会の以前の報告書を褒めることで、彼らに取り入った。"),
    "exterminated": ("駆除した、根絶した", "動詞", "The islanders exterminated the introduced goats to save the native plants.", "島の住人たちは在来植物を守るために持ち込まれたヤギを駆除した。"),
    # Q9
    "coerced": ("強制した", "動詞", "Witnesses said they had been coerced into changing their statements.", "証人たちは供述を変えるよう強制されたと述べた。"),
    "wavered": ("ぐらついた、迷った", "動詞", "His resolve wavered when he saw the size of the crowd.", "群衆の規模を見て、彼の決意はぐらついた。"),
    "hobbled": ("足を引きずって歩いた、動きを妨げた", "動詞", "The old dog hobbled to the door and lay down again.", "その老犬は足を引きずってドアまで行き、また横になった。"),
    "bombarded": ("集中的に浴びせた、砲撃した", "動詞", "Listeners bombarded the station with complaints about the change.", "リスナーたちはその変更についての苦情を放送局に浴びせた。"),
    # Q10
    "adorned": ("飾った", "動詞", "Carved panels adorned the walls of the entrance hall.", "彫刻の施された羽目板が玄関ホールの壁を飾っていた。"),
    "ignited": ("点火した、引火させた", "動詞", "The lamp ignited the dry straw stacked against the barn.", "そのランプは納屋に立てかけられた乾いたわらに引火した。"),
    "astounded": ("仰天させた", "動詞", "The auction price astounded even the dealers who had valued it.", "その落札価格は、評価をした業者たちさえ仰天させた。"),
    "derailed": ("脱線させた、頓挫させた", "動詞", "A single objection derailed six months of careful negotiation.", "1件の異議が6か月に及ぶ慎重な交渉を頓挫させた。"),
    # Q11
    "mutilated": ("切断した、ひどく損傷させた", "動詞", "Vandals mutilated the statue in the square last November.", "破壊行為者たちは昨年11月に広場の像をひどく傷つけた。"),
    "weaned": ("離乳させた、脱却させた", "動詞", "The farm weaned the calves at about ten weeks.", "その農場は生後10週ほどで子牛を離乳させた。"),
    "usurped": ("(王位や権力を)簒奪した", "動詞", "A cousin usurped the title while the heir was abroad.", "後継者が国外にいる間に、いとこがその爵位を奪い取った。"),
    "lurked": ("潜んだ、待ち伏せた", "動詞", "A photographer lurked behind the hedge for most of the morning.", "カメラマンが午前中のほとんど、生け垣の陰に潜んでいた。"),
    # Q12
    "pounced": ("飛びかかった", "動詞", "The cat pounced the moment the mouse left the wall.", "ネズミが壁を離れた瞬間、猫は飛びかかった。"),
    "babbled": ("わけもなくしゃべった", "動詞", "The child babbled happily about the trip for the entire journey.", "その子は道中ずっと旅行のことを楽しげにしゃべり続けた。"),
    "dribbled": ("したたらせた、ドリブルした", "動詞", "Paint dribbled down the ladder and onto the tiles below.", "ペンキがはしごを伝って下のタイルへしたたり落ちた。"),
    "enthralled": ("魅了した", "動詞", "The pianist enthralled an audience that had come mainly for the singer.", "そのピアニストは、主に歌手目当てで来た聴衆を魅了した。"),
    # Q13
    "gloated": ("勝ち誇った、いい気になった", "動詞", "She never gloated, even after winning three titles in a row.", "彼女は3つの選手権を続けて取った後でさえ、決して勝ち誇らなかった。"),
    "apprehended": ("逮捕した、理解した", "動詞", "Police apprehended the driver at a checkpoint near the border.", "警察は国境近くの検問所でその運転手を逮捕した。"),
    "nibbled": ("少しずつかじった", "動詞", "Rabbits nibbled the lettuce seedlings during the night.", "ウサギたちは夜の間にレタスの苗を少しずつかじった。"),
    "oriented": ("(方向づけて)適応させた、向けた", "動詞", "The guide oriented the visitors with a short talk and a map.", "案内人は短い説明と地図で来訪者に見当をつけさせた。"),
    # Q14
    "instigated": ("扇動した、引き起こした", "動詞", "Two former officials instigated the protest that closed the plant.", "2人の元職員が、その工場を閉鎖に追い込んだ抗議を扇動した。"),
    "retorted": ("言い返した", "動詞", "When accused of laziness, he retorted that nobody else had volunteered.", "怠惰だと責められると、彼はほかに誰も志願しなかったと言い返した。"),
    "stuttered": ("どもった、口ごもった", "動詞", "He stuttered badly whenever he had to speak on the telephone.", "彼は電話で話さなければならないときはいつもひどくどもった。"),
    "embossed": ("浮き彫りにした、型押しした", "動詞", "The bookbinder embossed the title in gold on the spine.", "製本職人は背表紙に金で題名を型押しした。"),
    # Q15
    "profound": ("深遠な、重大な", "形容詞", "The lecture had a profound effect on how she chose her subject.", "その講義は彼女の専攻の選び方に深い影響を与えた。"),
    "ample": ("十分な、豊富な", "形容詞", "There is ample parking behind the community hall.", "公民館の裏には十分な駐車場がある。"),
    "luxuriant": ("生い茂った、豊かな", "形容詞", "Luxuriant vines covered the entire southern wall of the house.", "生い茂ったつるが家の南側の壁全体を覆っていた。"),
    "vulgar": ("下品な、俗悪な", "形容詞", "The editor removed a vulgar joke from the opening paragraph.", "編集者は冒頭の段落から下品な冗談を削除した。"),
    # Q16
    "bumbling": ("へまばかりする、不器用な", "形容詞", "A bumbling assistant lost the only copy of the contract.", "へまばかりする助手が契約書の唯一の写しをなくした。"),
    "clairvoyant": ("透視力のある、予知能力のある", "形容詞", "The novel features a clairvoyant child who predicts the flood.", "その小説には洪水を予言する透視能力のある子どもが登場する。"),
    "crabby": ("不機嫌な、気難しい", "形容詞", "He gets crabby if lunch is delayed by more than ten minutes.", "彼は昼食が10分以上遅れると不機嫌になる。"),
    "eclectic": ("多様なものを取り入れた、折衷的な", "形容詞", "Her eclectic taste in music surprised everyone at the party.", "彼女の折衷的な音楽の好みは、パーティーの全員を驚かせた。"),
    # Q17
    "plausible": ("もっともらしい", "形容詞", "The witness gave a plausible but ultimately false explanation.", "その証人はもっともらしいが、結局は虚偽の説明をした。"),
    "ubiquitous": ("至る所にある", "形容詞", "Plastic packaging has become ubiquitous in every supermarket.", "プラスチック包装はどのスーパーでも至る所で見られるようになった。"),
    "frazzled": ("疲れ果てた、いらいらした", "形容詞", "The frazzled receptionist had answered ninety calls before noon.", "疲れ果てた受付係は正午までに90件の電話に応対していた。"),
    "philanthropic": ("慈善の、博愛の", "形容詞", "A philanthropic trust paid for the restoration of the organ.", "慈善信託がそのオルガンの修復費用を負担した。"),
    # Q18
    "preemptive": ("先手を打った、予防的な", "形容詞", "The airline issued a preemptive apology before the delays began.", "その航空会社は遅延が始まる前に先回りして謝罪を出した。"),
    "stagnant": ("停滞した、よどんだ", "形容詞", "Mosquitoes breed rapidly in stagnant water behind the wall.", "蚊は壁の裏のよどんだ水の中で急速に繁殖する。"),
    "resplendent": ("光り輝く、華麗な", "形容詞", "The choir appeared resplendent in newly made scarlet robes.", "聖歌隊は新調された緋色の法衣をまとって輝いて見えた。"),
    "wanton": ("理由のない、放埒な", "形容詞", "The court described the damage as wanton and entirely unnecessary.", "裁判所はその損害を理由のない、まったく不必要なものだと述べた。"),
    # Q19
    "somber": ("陰気な、厳粛な", "形容詞", "A somber mood filled the hall before the memorial began.", "追悼式が始まる前、厳粛な雰囲気がホールを満たしていた。"),
    "adversarial": ("敵対的な、対立的な", "形容詞", "The two departments developed an adversarial relationship over the budget.", "2つの部署は予算をめぐって敵対的な関係になった。"),
    "clandestine": ("秘密の、内密の", "形容詞", "A clandestine printing press operated in the cellar for two years.", "秘密の印刷機が2年間、地下室で稼働していた。"),
    "barbarous": ("野蛮な、残虐な", "形容詞", "The treaty outlawed practices that both sides called barbarous.", "その条約は双方が野蛮と呼んだ行為を禁じた。"),
    # Q20
    "irate": ("激怒した", "形容詞", "An irate customer demanded to speak to the branch manager.", "激怒した客が支店長と話させろと要求した。"),
    "covert": ("ひそかな、隠密の", "形容詞", "The agency ran a covert operation for eleven months.", "その機関は11か月にわたり隠密作戦を実施した。"),
    "candid": ("率直な", "形容詞", "In a candid interview, she admitted that the project had failed.", "率直なインタビューの中で、彼女はその計画が失敗したと認めた。"),
    "ingenious": ("巧妙な、独創的な", "形容詞", "An ingenious pulley system lifts the boats over the weir.", "巧妙な滑車の仕組みが堰を越えて船を持ち上げる。"),
    # Q21
    "stupendously": ("途方もなく", "副詞", "The first computers were stupendously large by modern standards.", "初期のコンピューターは現代の基準では途方もなく大きかった。"),
    "posthumously": ("死後に", "副詞", "The medal was awarded posthumously to a pilot who saved the village.", "その勲章は村を救った操縦士に死後授与された。"),
    "semantically": ("意味の上で", "副詞", "The two terms differ semantically, though people use them interchangeably.", "その2つの用語は意味の上では異なるが、人々は互換的に使っている。"),
    "belligerently": ("好戦的に、けんか腰に", "副詞", "He responded belligerently to what had been a routine question.", "彼はごく普通の質問にけんか腰で応じた。"),
    # Q22
    "goofed off": ("サボった、怠けた", "句動詞", "The crew goofed off whenever the supervisor left the site.", "作業員たちは監督が現場を離れるたびにサボっていた。"),
    "let on": ("(秘密を)漏らした、口に出した", "句動詞", "She knew about the transfer but never let on to anyone.", "彼女は異動のことを知っていたが、誰にも漏らさなかった。"),
    "wore down": ("すり減らした、疲弊させた", "句動詞", "Months of appeals wore down the family's resistance to the sale.", "何か月もの説得が売却に対する一家の抵抗をすり減らした。"),
    "milled about": ("うろうろした、群がって動き回った", "句動詞", "Passengers milled about the concourse waiting for the platform number.", "乗客たちはホームの番号を待ちながら中央広場をうろうろしていた。"),
    # Q23
    "bunched up": ("ひとかたまりになった、たくし上げた", "句動詞", "The runners bunched up at the narrow gate near the finish.", "走者たちはゴール近くの狭い門でひとかたまりになった。"),
    "shelled out": ("(大金を)払った", "句動詞", "He shelled out three hundred pounds for a ticket to the semifinal.", "彼は準決勝のチケットに300ポンドを払った。"),
    "spun out": ("引き延ばした、長引かせた", "句動詞", "The lawyers spun out the hearing for another eight days.", "弁護士たちはその審理をさらに8日間引き延ばした。"),
    "fenced in": ("柵で囲った、束縛した", "句動詞", "The farmer fenced in the meadow to keep the deer out.", "その農場主はシカを入れないために牧草地を柵で囲った。"),
    # Q24
    "tore off": ("引きちぎった、勢いよく外した", "句動詞", "She tore off the label before putting the jar in the recycling.", "彼女は瓶を資源ごみに出す前にラベルを引きはがした。"),
    "stubbed out": ("(たばこを)もみ消した", "句動詞", "He stubbed out his cigarette and walked back into the meeting.", "彼はたばこをもみ消し、会議に戻っていった。"),
    "swore in": ("宣誓させて就任させた", "句動詞", "The chief justice swore in the new governor at noon.", "最高裁長官は正午に新知事に就任の宣誓をさせた。"),
    "dragged out": ("長引かせた、引きずり出した", "句動詞", "The dispute was dragged out for three years by repeated appeals.", "その争いは度重なる上訴によって3年間引き延ばされた。"),
    # Q25
    "fleshed out": ("肉付けした、具体化した", "句動詞", "The architect fleshed out the sketch into a full set of drawings.", "建築家はそのスケッチを肉付けして完全な図面一式に仕上げた。"),
    "bawled out": ("どなりつけた、叱りつけた", "句動詞", "The coach bawled out the defender who had ignored his instructions.", "監督は指示を無視した守備の選手をどなりつけた。"),
    "ground up": ("すりつぶした", "句動詞", "The cook ground up the spices with a heavy stone pestle.", "料理人は重い石のすりこぎで香辛料をすりつぶした。"),
    "leafed through": ("(本などを)ぱらぱらめくった", "句動詞", "He leafed through the catalog while waiting for his appointment.", "彼は予約の時間を待つ間、カタログをぱらぱらとめくった。"),
}


CORE_IMAGES = {
    "goofed off": {
        "chain": [
            {"term": "goof", "gloss": "ばかなことをする"},
            {"term": "off", "gloss": "仕事から離れて"},
            {"gloss": "やるべき仕事から離れてふざけて"},
            {"gloss": "サボる"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "let on": {
        "chain": [
            {"term": "let", "gloss": "通す、許す"},
            {"term": "on", "gloss": "相手へ伝わって"},
            {"gloss": "隠していたことを相手側へ通して"},
            {"gloss": "秘密を漏らす"},
        ],
        "particle": "on",
        "particleSense": "transmit",
    },
    "wore down": {
        "chain": [
            {"term": "wear", "gloss": "すり減らす"},
            {"term": "down", "gloss": "力を下げて"},
            {"gloss": "繰り返しこすって抵抗する力を落として"},
            {"gloss": "疲弊させる、根負けさせる"},
        ],
        "particle": "down",
        "particleSense": "reduce",
    },
    "milled about": {
        "chain": [
            {"term": "mill", "gloss": "臼のようにぐるぐる回る"},
            {"term": "about", "gloss": "周辺をあちこちに"},
            {"gloss": "行き先を決めずに周辺を回り続けて"},
            {"gloss": "うろうろする"},
        ],
        "particle": "about",
    },
    "bunched up": {
        "chain": [
            {"term": "bunch", "gloss": "束にする"},
            {"term": "up", "gloss": "一か所へ寄せ集めて"},
            {"gloss": "ばらけていたものを一か所へ寄せ集めて"},
            {"gloss": "ひとかたまりになる"},
        ],
        "particle": "up",
        "particleSense": "contain",
    },
    "shelled out": {
        "chain": [
            {"term": "shell", "gloss": "殻から取り出す"},
            {"term": "out", "gloss": "手元から外へ出して"},
            {"gloss": "財布の中身を殻から出すように外へ出して"},
            {"gloss": "大金を払う"},
        ],
        "particle": "out",
        "particleSense": "delegate",
    },
    "spun out": {
        "chain": [
            {"term": "spin", "gloss": "糸を紡ぐ"},
            {"term": "out", "gloss": "外へ長く伸ばして"},
            {"gloss": "短い材料を糸のように長く伸ばして"},
            {"gloss": "引き延ばす"},
        ],
        "particle": "out",
        "particleSense": "spread",
    },
    "fenced in": {
        "chain": [
            {"term": "fence", "gloss": "柵を巡らす"},
            {"term": "in", "gloss": "内側へ閉じ込めて"},
            {"gloss": "柵で囲って内側へ閉じ込めて"},
            {"gloss": "囲い込む、束縛する"},
        ],
        "particle": "in",
    },
    "tore off": {
        "chain": [
            {"term": "tear", "gloss": "引き裂く"},
            {"term": "off", "gloss": "本体から切り離して"},
            {"gloss": "力任せに引いて本体から切り離して"},
            {"gloss": "引きちぎる"},
        ],
        "particle": "off",
        "particleSense": "separate",
    },
    "stubbed out": {
        "chain": [
            {"term": "stub", "gloss": "先を押しつぶす"},
            {"term": "out", "gloss": "火を消し尽くして"},
            {"gloss": "吸い殻を押しつけて火を消し尽くして"},
            {"gloss": "たばこをもみ消す"},
        ],
        "particle": "out",
        "particleSense": "exhaust",
    },
    "swore in": {
        "chain": [
            {"term": "swear", "gloss": "誓う"},
            {"term": "in", "gloss": "職の中へ入れて"},
            {"gloss": "宣誓させて職務の内側へ入れて"},
            {"gloss": "宣誓就任させる"},
        ],
        "particle": "in",
    },
    "dragged out": {
        "chain": [
            {"term": "drag", "gloss": "引きずる"},
            {"term": "out", "gloss": "長く外へ伸ばして"},
            {"gloss": "終わるはずのものを引きずって長く伸ばして"},
            {"gloss": "長引かせる"},
        ],
        "particle": "out",
        "particleSense": "spread",
    },
    "fleshed out": {
        "chain": [
            {"term": "flesh", "gloss": "肉をつける"},
            {"term": "out", "gloss": "外形ができるまで"},
            {"gloss": "骨組みに肉をつけて形を作り出して"},
            {"gloss": "肉付けして具体化する"},
        ],
        "particle": "out",
        "particleSense": "produce",
    },
    "bawled out": {
        "chain": [
            {"term": "bawl", "gloss": "大声で叫ぶ"},
            {"term": "out", "gloss": "声を外へ出して"},
            {"gloss": "相手に向けて大声を外へ浴びせて"},
            {"gloss": "どなりつける"},
        ],
        "particle": "out",
        "particleSense": "express",
    },
    "ground up": {
        "chain": [
            {"term": "grind", "gloss": "すりつぶす"},
            {"term": "up", "gloss": "細かくなり切るまで"},
            {"gloss": "元の形が残らなくなるまですりつぶして"},
            {"gloss": "細かくすりつぶす"},
        ],
        "particle": "up",
        "particleSense": "complete",
    },
    "leafed through": {
        "chain": [
            {"term": "leaf", "gloss": "ページをめくる"},
            {"term": "through", "gloss": "端から端まで通して"},
            {"gloss": "ページを端から端まで次々めくって"},
            {"gloss": "ぱらぱらめくって見る"},
        ],
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
        raise ValueError("模試第14回は25問である必要があります")

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
        "source": "AI生成（英検過去問の引用なし）・人手校閲。語彙選定は docs/SET_PLAN_1_mock-10-21.md の mock-14 割り当てに従う",
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
