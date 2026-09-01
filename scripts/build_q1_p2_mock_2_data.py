"""準2級の自作模試第2回をQ1形式のJSONへ出力する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-2"


QUESTIONS = [
    {
        "stem": "The school posted the new (   ) on its website, showing when each club meets and when students must submit their forms.",
        "choices": ["schedule", "budget", "entrance", "shelf"],
        "answerIndex": 0,
        "translation": "学校は新しい予定表をウェブサイトに載せ、各クラブの活動日と生徒が用紙を提出しなければならない日を示した。",
    },
    {
        "stem": "A: Why did you buy so many apples? B: The supermarket offered a ten-percent (   ) on fruit near the checkout, so I decided to buy more than usual.",
        "choices": ["customer", "cashier", "basket", "discount"],
        "answerIndex": 3,
        "translation": "A：どうしてりんごをそんなにたくさん買ったの？ B：スーパーがレジ近くの果物を10パーセント割引にしていたから、いつもより多く買うことにしたんだ。",
    },
    {
        "stem": "We used a (   ) with a needle that pointed north while walking through the forest, because the clouds hid the sun for most of the afternoon.",
        "choices": ["trail", "compass", "cabin", "map"],
        "answerIndex": 1,
        "translation": "午後のほとんどの間、雲で太陽が隠れていたので、森の小道を歩きながら方角を知るためにコンパスを使った。",
    },
    {
        "stem": "The town's summer (   ) lasted three days and included food stalls, concerts, and games for children.",
        "choices": ["parade", "costume", "festival", "fireworks"],
        "answerIndex": 2,
        "translation": "町の夏祭りは3日間続き、食べ物の屋台やコンサート、子ども向けのゲームが行われた。",
    },
    {
        "stem": "A: Can we meet the new art teacher tomorrow? B: Yes, I wrote down the (   ) in my calendar, so I will not forget the time. She is visiting our class at three.",
        "choices": ["folder", "appointment", "message", "visitor"],
        "answerIndex": 1,
        "translation": "A：明日、新しい美術の先生に会える？ B：うん、予定をカレンダーに書き留めたから時間を忘れないよ。3時に私たちのクラスへ来るんだ。",
    },
    {
        "stem": "The supermarket was so (   ) after work that we had to wait outside until several people left.",
        "choices": ["narrow", "local", "private", "crowded"],
        "answerIndex": 3,
        "translation": "仕事の後、スーパーはとても混雑していたので、何人かが出ていくまで外で待たなければならなかった。",
    },
    {
        "stem": "A: Why did you choose Naomi to lead the group? B: She is very (   ) and listens carefully, even when a task takes much longer than expected.",
        "choices": ["honest", "polite", "patient", "curious"],
        "answerIndex": 2,
        "translation": "A：どうしてナオミをグループのリーダーに選んだの？ B：彼女はとても忍耐強く、作業が予想よりずっと長くかかっても注意深く話を聞くからだよ。",
    },
    {
        "stem": "The diagram in this guide is especially (   ) for visitors because it shows every entrance and exit.",
        "choices": ["similar", "useful", "available", "usual"],
        "answerIndex": 1,
        "translation": "この案内書の図はすべての入口と出口を示しているので、来訪者にとって特に役立つ。",
    },
    {
        "stem": "A: This shirt is too small for me. B: The shop can (   ) it if you bring the receipt and explain the problem to the cashier.",
        "choices": ["replace", "reserve", "deliver", "recommend"],
        "answerIndex": 0,
        "translation": "A：このシャツは私には小さすぎる。 B：レシートを持ってきて、レジ係に事情を説明すれば、店は交換してくれるよ。",
    },
    {
        "stem": "Before the safety drill begins, the students must (   ) their presentation materials; the teacher has already printed the schedule.",
        "choices": ["notice", "protect", "return", "prepare"],
        "answerIndex": 3,
        "translation": "避難訓練が始まる前に、生徒たちは発表の資料を準備しなければならない。先生はすでに予定表を印刷している。",
    },
    {
        "stem": "A: What did you do before the test? B: I had to (   ) the meaning of an unfamiliar word in a dictionary before writing my answer.",
        "choices": ["put off", "figure out", "look up", "make up"],
        "answerIndex": 2,
        "translation": "A：テストの前に何をしたの？ B：答えを書く前に、辞書で知らない単語の意味を調べなければならなかった。",
    },
    {
        "stem": "Before mailing the application, Ken had to (   ) the form completely because the office would reject incomplete applications.",
        "choices": ["find out", "fill out", "leave out", "call off"],
        "answerIndex": 1,
        "translation": "申込書を郵送する前に、事務所が不完全な申込書を受け付けないので、ケンは用紙にすべて記入しなければならなかった。",
    },
    {
        "stem": "A: What should I do in an emergency? B: Keep this phone number (   ) an emergency, because the community center can provide blankets and a place to sleep during a storm.",
        "choices": ["in the course of", "on the way to", "instead of", "in case of"],
        "answerIndex": 3,
        "translation": "A：緊急時にはどうすればいいの？ B：緊急事態に備えてこの電話番号を控えておきなさい。嵐のとき、公民館は毛布と寝る場所を提供できる。",
    },
    {
        "stem": "The teacher explained the rules (   ) the school tour, so every student knew where to meet before the bus left.",
        "choices": ["at the beginning of", "in the center of", "for the purpose of", "in honor of"],
        "answerIndex": 0,
        "translation": "先生は校外見学の初めに規則を説明したので、バスが出発する前に全員がどこに集合すればよいか分かった。",
    },
    {
        "stem": "A: What caused the company to change its delivery plan? B: It changed the plan (   ) repeated complaints from customers and promised faster service next month.",
        "choices": ["under the control of", "at the risk of", "in response to", "with the support of"],
        "answerIndex": 2,
        "translation": "A：会社が配送計画を変えた原因は何？ B：顧客から繰り返し苦情が寄せられたため計画を変え、来月はもっと速いサービスを約束したんだ。",
    },
]


DETAILS = {
    "schedule": ("予定、日程", "名詞", "The club schedule changed after the school added two afternoon activities.", "学校が午後の活動を2つ追加した後、クラブの予定が変わった。"),
    "budget": ("予算", "名詞", "Our family budget includes money for food, transport, and school supplies.", "私たちの家計には食費、交通費、学校用品のためのお金が含まれている。"),
    "entrance": ("入口、入場", "名詞", "The museum entrance is beside the ticket office near the main street.", "博物館の入口は大通り近くのチケット売り場の隣にある。"),
    "shelf": ("棚", "名詞", "I placed the travel guide on the highest shelf in the study.", "私は旅行案内書を書斎のいちばん高い棚に置いた。"),
    "customer": ("客、顧客", "名詞", "The customer asked whether the store could deliver the table tomorrow.", "その客は、店が明日テーブルを配達できるか尋ねた。"),
    "cashier": ("レジ係", "名詞", "The cashier counted the coins carefully before giving me the receipt.", "レジ係は私にレシートを渡す前に硬貨を注意深く数えた。"),
    "basket": ("かご", "名詞", "She put apples and bread into a basket at the market.", "彼女は市場でりんごとパンをかごに入れた。"),
    "discount": ("割引", "名詞", "The shop offered a discount to students who showed their student ID cards.", "その店は学生証を見せた生徒に割引を提供した。"),
    "trail": ("小道、登山道", "名詞", "The forest trail becomes narrow after the bridge near the waterfall.", "滝の近くの橋を過ぎると、森の小道は狭くなる。"),
    "compass": ("コンパス、羅針盤", "名詞", "We checked the compass before leaving the campsite on a cloudy morning.", "曇った朝、キャンプ場を出る前に私たちはコンパスを確認した。"),
    "cabin": ("小屋、客室", "名詞", "The hikers slept in a small cabin beside the quiet lake.", "ハイカーたちは静かな湖のそばの小さな小屋で眠った。"),
    "map": ("地図", "名詞", "Please draw a map showing the safest path to the station.", "駅までの最も安全な道を示す地図を描いてください。"),
    "parade": ("パレード、行列", "名詞", "The town parade passed our house while children waved small flags.", "子どもたちが小旗を振る中、町のパレードが私たちの家の前を通った。"),
    "costume": ("衣装、仮装", "名詞", "Her colorful costume was ready before the school festival began.", "学校祭が始まる前に、彼女の色鮮やかな衣装は準備できていた。"),
    "festival": ("祭り、行事", "名詞", "The summer festival attracts families from several villages every year.", "その夏祭りには毎年、いくつもの村から家族連れが集まる。"),
    "fireworks": ("花火", "名詞", "We watched the fireworks from a hill above the harbor.", "私たちは港の上にある丘から花火を見た。"),
    "appointment": ("約束、予約", "名詞", "I made an appointment with the dentist for next Tuesday afternoon.", "私は来週火曜日の午後に歯科医の予約を取った。"),
    "folder": ("フォルダー、書類入れ", "名詞", "I kept the permission form in a blue folder on my desk.", "私は許可書を机の上の青いフォルダーに入れておいた。"),
    "message": ("伝言、メッセージ", "名詞", "He left a short message on my phone before catching the bus.", "彼はバスに乗る前に私の携帯電話に短いメッセージを残した。"),
    "visitor": ("訪問者、来訪者", "名詞", "Every visitor receives a simple map at the museum entrance.", "来訪者は全員、博物館の入口で簡単な地図を受け取る。"),
    "crowded": ("混雑した", "形容詞", "The train station was crowded because several buses arrived at once.", "何台ものバスが一度に到着したので、駅は混雑していた。"),
    "narrow": ("狭い", "形容詞", "This narrow road is difficult for two cars to use together.", "この狭い道は2台の車が同時に通るのが難しい。"),
    "local": ("地元の", "形容詞", "We bought local vegetables from a farmer near the village.", "私たちは村の近くの農家から地元の野菜を買った。"),
    "private": ("私的な、個人用の", "形容詞", "The hotel has a private room where guests can study quietly.", "そのホテルには宿泊客が静かに勉強できる個室がある。"),
    "patient": ("忍耐強い", "形容詞", "A patient teacher gives children time to explain their ideas.", "忍耐強い先生は子どもたちに考えを説明する時間を与える。"),
    "honest": ("正直な", "形容詞", "Our honest guide told us that the path was temporarily closed.", "正直なガイドは、その道が一時的に閉鎖されていると私たちに伝えた。"),
    "polite": ("礼儀正しい", "形容詞", "The polite student thanked the librarian before leaving the room.", "その礼儀正しい生徒は部屋を出る前に司書へお礼を言った。"),
    "curious": ("好奇心の強い", "形容詞", "The curious child asked many questions about the old machine.", "その好奇心の強い子どもは古い機械について多くの質問をした。"),
    "useful": ("役に立つ", "形容詞", "This useful website explains how visitors can reserve museum tickets.", "この役立つウェブサイトは来訪者が博物館のチケットを予約する方法を説明している。"),
    "similar": ("似た、類似した", "形容詞", "The two paintings look similar, but their colors are slightly different.", "その2枚の絵は似ているが、色は少し違う。"),
    "available": ("利用できる、空いている", "形容詞", "Several seats are available on the later train to the coast.", "海岸行きの後発の列車には空いている席がいくつかある。"),
    "usual": ("いつもの、通常の", "形容詞", "The bus was later than usual because road work blocked traffic.", "道路工事で交通が妨げられたため、バスはいつもより遅れた。"),
    "reserve": ("予約する、取っておく", "動詞", "We should reserve a table before the restaurant becomes busy.", "レストランが混む前に、私たちはテーブルを予約すべきだ。"),
    "deliver": ("配達する、届ける", "動詞", "The company will deliver the new desks to our classroom tomorrow.", "会社は明日、新しい机を私たちの教室へ届ける。"),
    "replace": ("取り替える、交換する", "動詞", "The store agreed to replace the broken lamp without charging us.", "店は私たちに料金を請求せず、壊れたランプを交換することに同意した。"),
    "recommend": ("推薦する、勧める", "動詞", "I recommend this quiet café to visitors who enjoy reading.", "読書が好きな来訪者には、この静かなカフェをお勧めします。"),
    "notice": ("気づく", "動詞", "Did you notice the small sign beside the library door?", "図書館のドアの横にある小さな表示に気づきましたか。"),
    "protect": ("守る、保護する", "動詞", "Sunscreen helps protect your skin during a long outdoor event.", "日焼け止めは長い屋外行事の間、肌を守るのに役立つ。"),
    "prepare": ("準備する", "動詞", "The students will prepare their materials before the science lesson.", "生徒たちは理科の授業の前に資料を準備する。"),
    "return": ("返す、戻る", "動詞", "Please return the library books before the holiday begins.", "休暇が始まる前に図書館の本を返してください。"),
    "put off": ("延期する", "句動詞", "The committee decided to put off the meeting until Friday because two members were away.", "委員会は2人のメンバーが不在だったため、会議を金曜日まで延期することにした。"),
    "figure out": ("理解する、解決する", "句動詞", "We need to figure out the safest route before the hikers leave.", "ハイカーたちが出発する前に、私たちは最も安全な道を見つけ出す必要がある。"),
    "look up": ("調べる", "句動詞", "You can look up the unfamiliar word in a dictionary before writing your answer.", "答えを書く前に、辞書で知らない単語を調べることができます。"),
    "make up": ("作り上げる、でっち上げる", "句動詞", "She had to make up a reasonable excuse for missing the rehearsal.", "彼女はリハーサルを休んだもっともらしい言い訳を作らなければならなかった。"),
    "find out": ("知る、突き止める", "句動詞", "The teacher will find out who left the window open after class.", "先生は授業の後、誰が窓を開けたままにしたのか突き止めるだろう。"),
    "fill out": ("記入する", "句動詞", "Please fill out the application form before you mail it.", "郵送する前に申込書に記入してください。"),
    "leave out": ("省く、除外する", "句動詞", "Do not leave out your phone number when you complete the form.", "用紙に記入するとき、電話番号を省かないでください。"),
    "call off": ("中止する", "句動詞", "The organizers had to call off the outdoor concert because of lightning.", "主催者は雷のため屋外コンサートを中止しなければならなかった。"),
    "in case of": ("〜の場合には、〜に備えて", "前置詞句", "In case of heavy rain, the outdoor concert will move indoors.", "大雨の場合、屋外コンサートは屋内へ移される。"),
    "instead of": ("〜の代わりに", "前置詞句", "Instead of a paper form, the office accepted online applications.", "紙の用紙の代わりに、その事務所はオンライン申請を受け付けた。"),
    "in the course of": ("〜の間に、〜の過程で", "前置詞句", "In the course of the afternoon, the clouds slowly disappeared.", "午後の間に、雲はゆっくり消えていった。"),
    "on the way to": ("〜へ行く途中で", "前置詞句", "We bought fresh bread on the way to the picnic.", "私たちはピクニックへ行く途中で焼きたてのパンを買った。"),
    "at the beginning of": ("〜の初めに", "前置詞句", "At the beginning of each lesson, students review yesterday's words.", "毎回の授業の初めに、生徒たちは昨日の単語を復習する。"),
    "in the center of": ("〜の中心に", "前置詞句", "The fountain stands in the center of the busy plaza.", "噴水はにぎやかな広場の中央にある。"),
    "for the purpose of": ("〜する目的で", "前置詞句", "The room was built for the purpose of teaching basic computer skills.", "その部屋は基本的なコンピューター技能を教える目的で建てられた。"),
    "in honor of": ("〜に敬意を表して、〜を記念して", "前置詞句", "The concert was held in honor of the town's founders.", "そのコンサートは町の創設者たちに敬意を表して開かれた。"),
    "in response to": ("〜に応じて、〜への対応として", "前置詞句", "The store offered refunds in response to several customer complaints.", "その店は顧客からのいくつかの苦情に対応して返金を行った。"),
    "under the control of": ("〜の管理下に", "前置詞句", "The old theater is now under the control of the city council.", "その古い劇場は今では市議会の管理下にある。"),
    "at the risk of": ("〜の危険を冒して", "前置詞句", "He crossed the stream at the risk of getting his shoes wet.", "彼は靴を濡らす危険を冒して小川を渡った。"),
    "with the support of": ("〜の支援を受けて", "前置詞句", "With the support of her coach, Rina entered the regional race.", "コーチの支援を受けて、リナは地域のレースに出場した。"),
}


CORE_IMAGES = {
    "put off": {"particle": "off", "particleSense": "pull-away", "chain": [{"term": "put", "gloss": "置く"}, {"term": "off", "gloss": "離して"}, {"gloss": "予定を先へ延ばす"}]},
    "figure out": {"particle": "out", "particleSense": "resolve", "siblings": [{"phrase": "sort out", "gloss": "整理して解決する"}, {"phrase": "iron out", "gloss": "問題を解消する"}, {"phrase": "straighten out", "gloss": "整理する"}], "chain": [{"term": "figure", "gloss": "考える"}, {"term": "out", "gloss": "外へほどいて"}, {"gloss": "理解して解決する"}]},
    "look up": {"particle": "up", "particleSense": "appear", "chain": [{"term": "look", "gloss": "目を向ける"}, {"term": "up", "gloss": "上へ出して"}, {"gloss": "情報を調べて見つける"}]},
    "make up": {"particle": "up", "particleSense": "fabricate", "siblings": [{"phrase": "cook up", "gloss": "でっち上げる"}, {"phrase": "dream up", "gloss": "考え出す"}, {"phrase": "think up", "gloss": "思いつく"}], "chain": [{"term": "make", "gloss": "作る"}, {"term": "up", "gloss": "作り上げて"}, {"gloss": "話や言い訳を作り出す"}]},
    "find out": {"particle": "out", "particleSense": "produce", "chain": [{"term": "find", "gloss": "見つける"}, {"term": "out", "gloss": "表に出して"}, {"gloss": "隠れた情報を表に出して突き止める"}]},
    "fill out": {"particle": "out", "particleSense": "spread", "chain": [{"term": "fill", "gloss": "満たす"}, {"term": "out", "gloss": "すみずみまで広げて"}, {"gloss": "用紙に必要事項を記入する"}]},
    "leave out": {"particle": "out", "particleSense": "remove", "chain": [{"term": "leave", "gloss": "残す"}, {"term": "out", "gloss": "外に残して"}, {"gloss": "一部を省く"}]},
    "call off": {"particle": "off", "particleSense": "pull-away", "siblings": [{"phrase": "pay off", "gloss": "金を渡して黙らせる"}, {"phrase": "warn off", "gloss": "警告して手を引かせる"}, {"phrase": "hold off", "gloss": "延期する"}], "chain": [{"term": "call", "gloss": "呼ぶ"}, {"term": "off", "gloss": "離して"}, {"gloss": "予定を取り消して中止する"}]},
    "in case of": {"chain": [{"term": "case", "gloss": "場合"}, {"term": "of", "gloss": "〜について"}, {"gloss": "〜の場合には、〜に備えて"}]},
    "instead of": {"chain": [{"term": "instead", "gloss": "代わりに"}, {"term": "of", "gloss": "〜について"}, {"gloss": "あるものを別のものに置き換えて"}]},
    "in the course of": {"chain": [{"term": "course", "gloss": "進行する道筋"}, {"term": "of", "gloss": "〜の中で"}, {"gloss": "〜の間に、〜の過程で"}]},
    "on the way to": {"chain": [{"term": "way", "gloss": "道筋"}, {"term": "to", "gloss": "〜へ向かって"}, {"gloss": "〜へ行く途中で"}]},
    "at the beginning of": {"chain": [{"term": "beginning", "gloss": "始まり"}, {"term": "of", "gloss": "〜を基準に"}, {"gloss": "〜の初めに"}]},
    "in the center of": {"chain": [{"term": "center", "gloss": "中心"}, {"term": "of", "gloss": "〜の中で"}, {"gloss": "〜の中心に"}]},
    "for the purpose of": {"chain": [{"term": "purpose", "gloss": "目的"}, {"term": "of", "gloss": "〜に向けて"}, {"gloss": "〜する目的で"}]},
    "in honor of": {"chain": [{"term": "honor", "gloss": "敬意、名誉"}, {"term": "of", "gloss": "〜に向けて"}, {"gloss": "〜に敬意を表して、〜を記念して"}]},
    "in response to": {"chain": [{"term": "response", "gloss": "応答"}, {"term": "to", "gloss": "〜に向けて"}, {"gloss": "〜に応じて、〜への対応として"}]},
    "under the control of": {"chain": [{"term": "control", "gloss": "管理"}, {"term": "of", "gloss": "〜による"}, {"gloss": "〜の管理下に"}]},
    "at the risk of": {"chain": [{"term": "risk", "gloss": "危険"}, {"term": "of", "gloss": "〜を伴って"}, {"gloss": "〜の危険を冒して"}]},
    "with the support of": {"chain": [{"term": "support", "gloss": "支援"}, {"term": "of", "gloss": "〜から受けて"}, {"gloss": "〜の支援を受けて"}]},
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 15:
        raise ValueError("準2級模試第2回は15問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 60 or len(choices) != len(set(choices)):
        raise ValueError("選択肢は重複しない60件である必要があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
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
    write_json(DATA_DIR / "vocab_p2_mock-2.json", vocab)
    write_json(DATA_DIR / "questions_p2_mock-2.json", questions)
    print("p2 mock-2: 15 questions / 60 items (40 words, 20 idioms)")


if __name__ == "__main__":
    main()
