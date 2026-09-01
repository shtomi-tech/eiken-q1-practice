"""準2級の自作模試第1回をQ1形式のJSONへ出力する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-1"


QUESTIONS = [
    {
        "stem": "The teacher gave us extra time to finish the science (   ). The class will present its results to the principal tomorrow.",
        "choices": ["assignment", "deadline", "lecture", "attitude"],
        "answerIndex": 0,
        "translation": "先生は、科学の課題を終えるために、私たちに余分な時間をくれた。クラスは明日、結果を校長に発表する。",
    },
    {
        "stem": "A: Did you buy that jacket at the department store? B: Yes, it was on sale, so the price was really (   ). I had expected to pay much more.",
        "choices": ["expensive", "affordable", "colorful", "formal"],
        "answerIndex": 1,
        "translation": "A：あのジャケットをデパートで買ったの？ B：うん、セール中だったから値段が本当に手頃だったよ。もっと高い金額を払うと思っていた。",
    },
    {
        "stem": "Because the train was canceled, we had to find another (   ) with enough seats for all six travelers. Fortunately, a bus was leaving in ten minutes.",
        "choices": ["route", "border", "vehicle", "luggage"],
        "answerIndex": 2,
        "translation": "電車が運休になったので、6人の旅行者全員に十分な座席がある別の乗り物を見つけなければならなかった。幸い、10分後にバスが出るところだった。",
    },
    {
        "stem": "A: Did Mia finish the report? B: Yes, she (   ) it before lunch and sent it to the manager. She even checked the numbers twice.",
        "choices": ["borrowed", "escaped", "painted", "completed"],
        "answerIndex": 3,
        "translation": "A：ミアはレポートを終えた？ B：うん、昼食前に完成させて、マネージャーに送ったよ。数字も2回確認していた。",
    },
    {
        "stem": "My younger brother was proud when he won a (   ) at the local art contest. He brought it home and showed it to everyone.",
        "choices": ["neighbor", "prize", "wallet", "pillow"],
        "answerIndex": 1,
        "translation": "弟は、地域の美術コンテストで賞を取ったとき誇らしそうだった。賞を家に持ち帰り、みんなに見せた。",
    },
    {
        "stem": "The town held a clean-up (   ) near the river on Saturday. Many families joined and collected plastic bottles.",
        "choices": ["engine", "habit", "event", "temperature"],
        "answerIndex": 2,
        "translation": "町は土曜日に川の近くで清掃行事を開いた。多くの家族が参加し、ペットボトルを集めた。",
    },
    {
        "stem": "A: How did everyone react to the principal's announcement? B: The students looked really (   ) when they heard that Friday's test was canceled. They had worried all week.",
        "choices": ["nervous", "silent", "famous", "relieved"],
        "answerIndex": 3,
        "translation": "A：校長先生の発表にみんなはどう反応したの？ B：金曜日のテストが中止だと聞いて、生徒たちは本当に安心した様子だったよ。一週間ずっと心配していたからね。",
    },
    {
        "stem": "Please check the (   ) on the box before you buy the toy. It lists the age range and safety information.",
        "choices": ["label", "surface", "garage", "valley"],
        "answerIndex": 0,
        "translation": "そのおもちゃを買う前に、箱の表示を確認してください。対象年齢と安全情報が載っています。",
    },
    {
        "stem": "The guide asked visitors not to (   ) the old paintings in the museum. Even clean hands can damage their surface.",
        "choices": ["greet", "repair", "touch", "measure"],
        "answerIndex": 2,
        "translation": "ガイドは来館者に、博物館の古い絵に触れないよう頼んだ。きれいな手でも表面を傷めることがある。",
    },
    {
        "stem": "The manager asked Lena to (   ) the meeting until next week because two important clients were unavailable.",
        "choices": ["decorate", "postpone", "whisper", "cancel"],
        "answerIndex": 1,
        "translation": "2人の重要な顧客の都合がつかなかったため、マネージャーはレナに会議を来週まで延期するよう頼んだ。",
    },
    {
        "stem": "A: Why is Ken still in the classroom? B: He stayed behind to (   ) his notes before the exam. He wants to remember the key points clearly.",
        "choices": ["look after", "run into", "turn down", "go over"],
        "answerIndex": 3,
        "translation": "A：ケンはどうしてまだ教室にいるの？ B：試験の前にノートを復習するために残っているんだよ。重要な点をはっきり覚えておきたいんだ。",
    },
    {
        "stem": "A: The store sent me the wrong size. B: You should (   ) and ask for an exchange. Keep the receipt in case they need it.",
        "choices": ["take it back", "fill it out", "put it off", "give it away"],
        "answerIndex": 0,
        "translation": "A：店が違うサイズを送ってきた。 B：それを返品して交換を頼むべきだよ。店が必要とするかもしれないから、レシートは取っておいて。",
    },
    {
        "stem": "We will (   ) the mountain village early so that we can arrive before dark. The road is expected to become busy after noon.",
        "choices": ["look forward to", "get rid of", "set off for", "run out of"],
        "answerIndex": 2,
        "translation": "私たちは暗くなる前に到着できるよう、早く山村へ出発する。正午を過ぎると道が混むと予想されている。",
    },
    {
        "stem": "Each morning the workers must (   ) a short safety check before they start the machines. The supervisor records the result in a notebook.",
        "choices": ["break into", "carry out", "pick up", "look for"],
        "answerIndex": 1,
        "translation": "毎朝、作業員は機械を動かす前に短い安全点検を実施しなければならない。監督者はその結果をノートに記録する。",
    },
    {
        "stem": "A: What are those boxes at the community center? B: The neighbors decided to (   ) a small food drive for families in need.",
        "choices": ["take after", "come across", "turn into", "set up"],
        "answerIndex": 3,
        "translation": "A：公民館にあるあの箱は何？ B：近所の人たちが、困っている家庭のために小さな食料寄付活動を始めることにしたんだよ。",
    },
]


DETAILS = {
    "assignment": ("課題、宿題", "名詞", "I finished my science assignment before dinner and checked every answer.", "夕食前に科学の課題を終え、すべての答えを確認した。"),
    "deadline": ("締め切り", "名詞", "The project deadline is next Friday, so we must work carefully.", "プロジェクトの締め切りは次の金曜日なので、慎重に作業しなければならない。"),
    "lecture": ("講義", "名詞", "The professor gave a short lecture about animals living in the ocean.", "教授は海に住む動物について短い講義をした。"),
    "attitude": ("態度", "名詞", "Her positive attitude helped the team solve a difficult problem.", "彼女の前向きな態度は、チームが難しい問題を解決する助けになった。"),
    "affordable": ("手頃な、買いやすい", "形容詞", "This small apartment is affordable for a student with a part-time job.", "この小さなアパートは、アルバイトをする学生にも手頃だ。"),
    "expensive": ("高価な", "形容詞", "That restaurant is expensive, so we usually cook at home instead.", "そのレストランは高価なので、私たちはたいてい代わりに家で料理する。"),
    "colorful": ("色鮮やかな", "形容詞", "The children made a colorful poster for the school festival.", "子どもたちは学校祭のために色鮮やかなポスターを作った。"),
    "formal": ("正式な、きちんとした", "形容詞", "He wore a formal shirt when he visited the company office.", "彼は会社の事務所を訪れたとき、きちんとしたシャツを着ていた。"),
    "vehicle": ("乗り物、車両", "名詞", "The family used a large vehicle to carry camping equipment.", "その家族はキャンプ用品を運ぶために大きな車両を使った。"),
    "route": ("道順、経路", "名詞", "We chose a safer route through the village after the storm.", "嵐の後、私たちは村を通るより安全な経路を選んだ。"),
    "border": ("国境", "名詞", "The travelers showed their passports when they reached the border.", "旅行者たちは国境に着いたとき、パスポートを見せた。"),
    "luggage": ("荷物", "名詞", "Please keep your luggage beside you while you wait for the train.", "電車を待つ間、荷物をそばに置いておいてください。"),
    "completed": ("完了した、完成させた", "動詞", "She completed the online form and sent it before the evening deadline.", "彼女はオンラインの用紙に記入し、夕方の締め切り前に送った。"),
    "borrowed": ("借りた", "動詞", "I borrowed a camera from my neighbor for the school trip.", "私は校外学習のために近所の人からカメラを借りた。"),
    "escaped": ("逃げた、脱出した", "動詞", "The small dog escaped from the garden during the afternoon.", "その小さな犬は午後に庭から逃げた。"),
    "painted": ("描いた、塗った", "動詞", "They painted the classroom walls during the summer vacation.", "彼らは夏休み中に教室の壁を塗った。"),
    "prize": ("賞", "名詞", "The student received a prize for her careful drawing at school.", "その生徒は学校で丁寧な絵を描いたことで賞を受け取った。"),
    "neighbor": ("近所の人", "名詞", "Our neighbor brought fresh vegetables from her garden yesterday.", "昨日、近所の人が庭で採れた新鮮な野菜を持ってきてくれた。"),
    "wallet": ("財布", "名詞", "He found his wallet under the sofa after searching everywhere.", "彼はあちこち探した後、ソファの下で財布を見つけた。"),
    "pillow": ("枕", "名詞", "I put a soft pillow on the chair before our guests arrived.", "客が到着する前に、柔らかい枕を椅子の上に置いた。"),
    "event": ("行事、イベント", "名詞", "The school event brought parents and children together on Saturday.", "その学校行事は土曜日に保護者と子どもたちを一つにした。"),
    "engine": ("エンジン", "名詞", "The mechanic checked the car engine before the long journey.", "整備士は長旅の前に車のエンジンを点検した。"),
    "habit": ("習慣", "名詞", "Reading before bed became a relaxing habit for my sister.", "寝る前の読書は妹にとってリラックスできる習慣になった。"),
    "temperature": ("温度", "名詞", "The temperature fell quickly after the sun disappeared behind clouds.", "太陽が雲の後ろに隠れると、温度は急に下がった。"),
    "relieved": ("安心した", "形容詞", "We felt relieved when the doctor said the test was normal.", "医師が検査は正常だと言ったとき、私たちは安心した。"),
    "nervous": ("緊張した", "形容詞", "She felt nervous before speaking in front of the whole class.", "彼女はクラス全員の前で話す前に緊張した。"),
    "silent": ("静かな、無言の", "形容詞", "The library became silent when the students started their reading.", "生徒たちが読書を始めると、図書館は静かになった。"),
    "famous": ("有名な", "形容詞", "The town is famous for its beautiful spring festival.", "その町は美しい春祭りで有名だ。"),
    "label": ("ラベル、表示", "名詞", "Read the label carefully before you use this cleaning product.", "この掃除用品を使う前に、表示を注意深く読んでください。"),
    "surface": ("表面", "名詞", "The table surface became wet after someone spilled a glass.", "誰かがグラスをこぼした後、テーブルの表面が濡れた。"),
    "garage": ("車庫、ガレージ", "名詞", "My father keeps his bicycle in the garage during winter.", "父は冬の間、自転車を車庫に置いている。"),
    "valley": ("谷", "名詞", "The hikers looked down at the green valley from the hill.", "ハイカーたちは丘から緑の谷を見下ろした。"),
    "touch": ("触る", "動詞", "Please do not touch the wet paint near the entrance.", "入口の近くにある濡れたペンキに触れないでください。"),
    "greet": ("挨拶する", "動詞", "Visitors should greet the host politely when they arrive.", "訪問者は到着したら、礼儀正しく主催者に挨拶すべきだ。"),
    "repair": ("修理する", "動詞", "The workers will repair the broken bridge before the rainy season.", "作業員たちは雨季の前に壊れた橋を修理する。"),
    "measure": ("測る", "動詞", "The nurse used a ruler to measure the child's height.", "看護師は定規を使って子どもの身長を測った。"),
    "postpone": ("延期する", "動詞", "The airline had to postpone the flight because of heavy snow.", "航空会社は大雪のため、フライトを延期しなければならなかった。"),
    "decorate": ("飾る", "動詞", "The volunteers will decorate the hall with flowers and paper stars.", "ボランティアは花と紙の星でホールを飾る。"),
    "whisper": ("ささやく", "動詞", "Please whisper in the museum so other visitors can concentrate.", "他の来館者が集中できるよう、博物館ではささやき声で話してください。"),
    "cancel": ("中止する、取り消す", "動詞", "The organizer may cancel the picnic if the weather becomes dangerous.", "天候が危険になれば、主催者はピクニックを中止するかもしれない。"),
    "go over": ("復習する、見直す", "句動詞", "Let's go over the instructions once more before we begin the experiment.", "実験を始める前に、指示をもう一度確認しよう。"),
    "look after": ("世話をする", "句動詞", "My sister will look after our dog while we visit the museum.", "私たちが博物館を訪れている間、妹が犬の世話をする。"),
    "run into": ("偶然出会う", "句動詞", "I often run into my old teacher near the station.", "私は駅の近くで昔の先生に偶然会うことがよくある。"),
    "turn down": ("断る、下げる", "句動詞", "She decided to turn down the job because the hours were too long.", "勤務時間が長すぎたので、彼女はその仕事を断ることにした。"),
    "take it back": ("返品する、撤回する", "句動詞", "The customer had to take it back because the zipper broke after one day.", "ファスナーが一日で壊れたため、客はそれを返品しなければならなかった。"),
    "fill it out": ("記入する", "句動詞", "Please fill it out carefully before you submit the application online.", "オンラインで申請書を提出する前に、注意深く記入してください。"),
    "put it off": ("延期する、先延ばしにする", "句動詞", "We should not put it off because the deadline is tomorrow.", "締め切りは明日なので、それを先延ばしにすべきではない。"),
    "give it away": ("それを譲る、ただであげる", "句動詞", "They decided to give it away after buying a newer computer.", "彼らは新しいコンピューターを買った後、それを人に譲ることにした。"),
    "set off for": ("〜へ出発する", "句動詞", "The hikers will set off for the lake before sunrise tomorrow.", "ハイカーたちは明日、日の出前に湖へ出発する。"),
    "look forward to": ("〜を楽しみに待つ", "句動詞", "I look forward to meeting your family during the summer holiday.", "夏休みにあなたの家族に会うのを楽しみにしています。"),
    "get rid of": ("〜を取り除く、処分する", "句動詞", "We need to get rid of these broken chairs before the event.", "行事の前に、これらの壊れた椅子を処分する必要がある。"),
    "run out of": ("〜を使い果たす", "句動詞", "The bakery may run out of bread before the afternoon rush.", "そのパン屋は午後の混雑前にパンを切らすかもしれない。"),
    "carry out": ("実行する", "句動詞", "The workers must carry out the safety check before opening the factory.", "作業員は工場を開ける前に安全点検を実施しなければならない。"),
    "break into": ("〜に侵入する", "句動詞", "Someone tried to break into the empty shop late at night.", "誰かが夜遅くに空き店舗へ侵入しようとした。"),
    "pick up": ("拾う、受け取る", "句動詞", "Can you pick up the package from the post office today?", "今日、郵便局から荷物を受け取ってくれますか。"),
    "look for": ("〜を探す", "句動詞", "We need to look for a larger room for the meeting.", "私たちは会議のためにもっと広い部屋を探す必要がある。"),
    "set up": ("設置する、準備する", "句動詞", "The volunteers will set up tables before the community lunch begins.", "ボランティアは地域の昼食会が始まる前にテーブルを準備する。"),
    "take after": ("〜に似ている", "句動詞", "Many people say I take after my mother in personality.", "多くの人は、私の性格は母に似ていると言う。"),
    "come across": ("偶然見つける、出会う", "句動詞", "You may come across useful information while reading the local newspaper.", "地域の新聞を読んでいると、役立つ情報に偶然出会うかもしれない。"),
    "turn into": ("〜に変わる、〜に変える", "句動詞", "The empty lot will turn into a public garden next year.", "その空き地は来年、公共の庭に変わる予定だ。"),
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 15:
        raise ValueError("準2級模試第1回は15問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 60 or len(choices) != len(set(choices)):
        raise ValueError("選択肢は重複しない60件である必要があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")

    meta = {
        "grade": "英検準2級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "AI生成（英検過去問の引用なし）・人手校閲",
        "counts": {"questions": 15, "words": 40, "idioms": 20, "total": 60},
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
                item["type"] = "idiom"
                item["phrase"] = choice
                idioms.append(item)
            else:
                item["word"] = choice
                words.append(item)
    if (len(words), len(idioms)) != (40, 20):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idioms)}")
    return {"meta": meta, "words": words, "idioms": idioms}, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / "vocab_p2_mock-1.json", vocab)
    write_json(DATA_DIR / "questions_p2_mock-1.json", questions)
    print("p2 mock-1: 15 questions / 60 items (40 words, 20 idioms)")


if __name__ == "__main__":
    main()
