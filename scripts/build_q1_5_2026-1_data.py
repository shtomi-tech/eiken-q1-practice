"""英検5級 2026年度第1回の大問1を共通Q1形式へ構造化する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "2026-1"
SOURCE_PROBLEM_URL = "https://www.eiken.or.jp/eiken/exam/kakomon/2026-1-1ji-5kyu.pdf"
SOURCE_ANSWER_URL = "https://www.eiken.or.jp/eiken/result/pdf/202601F5kyu.pdf"
BLANK_RE = re.compile(r"\(\s+\)")
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


QUESTIONS = [
    {
        "stem": "A : What do you do in your free time, John?\nB : I read a (   ) every day.",
        "choices": ["music", "paint", "newspaper", "lunch"],
        "answerIndex": 2,
        "translation": "A：ジョン、暇な時間には何をしますか。\nB：毎日、新聞を1紙読みます。",
    },
    {
        "stem": "Many (   ) are waiting for the new pink train. It’s very popular.",
        "choices": ["books", "teeth", "fruits", "people"],
        "answerIndex": 3,
        "translation": "多くの人々が新しいピンク色の電車を待っています。とても人気があります。",
    },
    {
        "stem": "A : Where is your tennis (   ), Hiroki?\nB : It’s in my bag, Mom.",
        "choices": ["fork", "dictionary", "kite", "racket"],
        "answerIndex": 3,
        "translation": "A：ヒロキ、テニスのラケットはどこですか。\nB：かばんの中だよ、母さん。",
    },
    {
        "stem": "A : Mike, please (   ) your coffee before you go to school.\nB : OK, Mom.",
        "choices": ["sleep", "drink", "arrive", "talk"],
        "answerIndex": 1,
        "translation": "A：マイク、学校へ行く前にコーヒーを飲みなさい。\nB：分かった、母さん。",
    },
    {
        "stem": "Taro likes skiing. He goes to the (   ) near his house every winter.",
        "choices": ["pool", "station", "library", "mountain"],
        "answerIndex": 3,
        "translation": "太郎はスキーが好きです。毎冬、家の近くの山へ行きます。",
    },
    {
        "stem": "A : Mike, how (   ) is that building?\nB : It’s 200 meters.",
        "choices": ["fast", "cold", "young", "tall"],
        "answerIndex": 3,
        "translation": "A：マイク、あの建物はどのくらいの高さですか。\nB：200メートルです。",
    },
    {
        "stem": "A : Excuse me, Ms. Brown. Can I go home now?\nB : Yes, John. You can (   ) now.",
        "choices": ["know", "leave", "take", "eat"],
        "answerIndex": 1,
        "translation": "A：すみません、ブラウン先生。もう帰ってもいいですか。\nB：はい、ジョン。もう帰っていいですよ。",
    },
    {
        "stem": "A : Sorry, Mike. I can’t go to the movie with you today.\nB : Oh, I (   ).",
        "choices": ["look", "see", "play", "stand"],
        "answerIndex": 1,
        "translation": "A：ごめん、マイク。今日はあなたと映画に行けません。\nB：ああ、残念です。",
    },
    {
        "stem": "A : Do you often eat fruit (   ) home?\nB : No.",
        "choices": ["under", "with", "about", "at"],
        "answerIndex": 3,
        "translation": "A：家でよく果物を食べますか。\nB：いいえ。",
    },
    {
        "stem": "A : Dad, can we (   ) hiking tomorrow?\nB : Sure.",
        "choices": ["go", "want", "close", "play"],
        "answerIndex": 0,
        "translation": "A：お父さん、明日ハイキングに行ってもいいですか。\nB：もちろん。",
    },
    {
        "stem": "Taro goes to the swimming pool (   ) school.",
        "choices": ["after", "about", "down", "on"],
        "answerIndex": 0,
        "translation": "太郎は放課後に水泳プールへ行きます。",
    },
    {
        "stem": "I (   ) up at seven every morning. Then, I have breakfast with my mother.",
        "choices": ["sing", "talk", "close", "wake"],
        "answerIndex": 3,
        "translation": "私は毎朝7時に起きます。それから母と朝食を食べます。",
    },
    {
        "stem": "Mr. Ford teaches English. We like (   ) class very much.",
        "choices": ["his", "he", "him", "us"],
        "answerIndex": 0,
        "translation": "フォード先生は英語を教えています。私たちは彼の授業が大好きです。",
    },
    {
        "stem": "A : Nancy, I can’t find my eraser. Can I use yours?\nB : Yes. You can use (   ).",
        "choices": ["I", "my", "me", "mine"],
        "answerIndex": 3,
        "translation": "A：ナンシー、消しゴムが見つかりません。あなたのを使ってもいいですか。\nB：はい。私のを使っていいですよ。",
    },
    {
        "stem": "A : Is Kent in the library?\nB : Yes, he (   ) there.",
        "choices": ["is studying", "are studying", "am studying", "studying"],
        "answerIndex": 0,
        "translation": "A：ケントは図書館にいますか。\nB：はい、そこで勉強しています。",
    },
]


DETAILS: dict[tuple[int, str], dict[str, str]] = {}
ETYMOLOGY: dict[str, str] = {}


def add_detail(
    q: int,
    surface: str,
    meaning: str,
    pos: str,
    example: str,
    example_translation: str,
    etymology: str,
) -> None:
    DETAILS[(q, surface)] = {
        "meaning": meaning,
        "pos": pos,
        "example": example,
        "exampleTranslation": example_translation,
    }
    ETYMOLOGY.setdefault(surface, etymology)


# Q1
add_detail(1, "music", "音楽", "名詞", "Mika listens to music after dinner every evening at home.", "ミカは毎晩、家で夕食後に音楽を聴きます。", "music comes from Greek mousikē, the art of the Muses.")
add_detail(1, "paint", "絵の具、塗料", "名詞", "The children used bright paint to decorate their classroom wall.", "子どもたちは明るい色の絵の具を使って教室の壁を飾りました。", "paint comes through Old French from Latin pingere, to mark or color.")
add_detail(1, "newspaper", "新聞", "名詞", "My grandfather reads the newspaper with breakfast every morning.", "私の祖父は毎朝、朝食を食べながら新聞を読みます。", "newspaper combines new with paper, a sheet used for writing.")
add_detail(1, "lunch", "昼食", "名詞", "I usually bring my lunch from home on Fridays.", "私はたいてい金曜日には昼食を家から持ってきます。", "lunch is a shortened form of luncheon, a midday meal.")

# Q2
add_detail(2, "books", "本、書籍", "名詞", "The students put their books on the desk before class.", "生徒たちは授業の前に本を机の上へ置きました。", "book comes from Old English bōc, a written work.")
add_detail(2, "teeth", "歯", "名詞", "Brush your teeth carefully after breakfast and before bed.", "朝食後と寝る前に、歯をていねいに磨きなさい。", "tooth and teeth trace back to Old English tōth and its plural.")
add_detail(2, "fruits", "果物", "名詞", "These fresh fruits are popular at the summer market.", "これらの新鮮な果物は夏の市場で人気があります。", "fruit comes from Latin fructus through Old French, meaning produce or harvest.")
add_detail(2, "people", "人々", "名詞", "Many people are waiting outside the station this morning.", "今朝、多くの人々が駅の外で待っています。", "people comes from Latin populus through French, meaning persons.")

# Q3
add_detail(3, "fork", "フォーク", "名詞", "Please use a fork when you eat the salad at lunch.", "昼食でサラダを食べるときはフォークを使ってください。", "fork comes from Latin furca through Old French, meaning a pronged tool.")
add_detail(3, "dictionary", "辞書", "名詞", "She checked the new word in her English dictionary yesterday.", "彼女は昨日、英語の辞書でその新しい単語を調べました。", "dictionary comes from Latin dictionarium, a collection of words.")
add_detail(3, "kite", "たこ", "名詞", "My brother flies his colorful kite in the park on Sundays.", "弟は日曜日に公園で色鮮やかなたこを揚げます。", "kite comes from Old English cyta, named after the bird.")
add_detail(3, "racket", "ラケット", "名詞", "Hiroki keeps his tennis racket safely inside his school bag.", "ヒロキはテニスのラケットを学校のかばんの中に安全にしまっています。", "racket for a sports bat comes through French raquette from Arabic.")

# Q4
add_detail(4, "sleep", "眠る", "動詞", "Young children sleep for ten hours on school nights.", "幼い子どもたちは学校のある夜には10時間眠ります。", "sleep comes from Old English slǣpan, meaning to rest.")
add_detail(4, "drink", "飲む", "動詞", "Please drink your coffee slowly before you leave home.", "家を出る前にコーヒーをゆっくり飲んでください。", "drink comes from Old English drincan, to swallow liquid.")
add_detail(4, "arrive", "到着する", "動詞", "We will arrive at the museum before the morning tour begins.", "私たちは朝の見学が始まる前に博物館へ到着します。", "arrive comes from Old French arriver, to reach a shore or place.")
add_detail(4, "talk", "話す", "動詞", "Please talk with your partner before you answer the question.", "その質問に答える前に、相手と話してください。", "talk comes from Middle English talken, meaning to speak.")

# Q5
add_detail(5, "pool", "プール", "名詞", "The hotel has a small pool where guests can swim.", "そのホテルには宿泊客が泳げる小さなプールがあります。", "pool comes from Old English pōl, a small body of water.")
add_detail(5, "station", "駅", "名詞", "Our family met at the station before taking the train.", "私たち家族は電車に乗る前に駅で会いました。", "station comes from Latin statio through French, a stopping place.")
add_detail(5, "library", "図書館", "名詞", "I borrowed two storybooks from the library last Saturday.", "私は先週の土曜日に図書館から物語の本を2冊借りました。", "library comes from Latin librarium, a place for books.")
add_detail(5, "mountain", "山", "名詞", "Taro sees the snowy mountain from his bedroom window.", "太郎は寝室の窓から雪の積もった山を見ます。", "mountain comes from Latin montanus through French, relating to a mountain.")

# Q6
add_detail(6, "fast", "速い", "形容詞", "The new train is very fast and comfortable for travelers.", "その新しい電車はとても速く、旅行者にとって快適です。", "fast comes from Old English fæst, meaning firmly or quickly.")
add_detail(6, "cold", "寒い、冷たい", "形容詞", "The water was too cold for swimming this early morning.", "その水は今朝早く泳ぐには冷たすぎました。", "cold comes from Old English cald, meaning low in temperature.")
add_detail(6, "young", "若い", "形容詞", "That young player practices soccer with great energy every day.", "あの若い選手は毎日、元気いっぱいにサッカーを練習します。", "young comes from Old English geong, meaning in an early age.")
add_detail(6, "tall", "背が高い、高い", "形容詞", "The tall building can be seen from the nearby school.", "その高い建物は近くの学校から見ることができます。", "tall comes from Old English getæl, related to being well-formed.")

# Q7
add_detail(7, "know", "知っている、分かる", "動詞", "I know the answer because I studied the lesson carefully.", "私はその答えを知っています。授業をていねいに勉強したからです。", "know comes from Old English cnāwan, meaning to recognize or understand.")
add_detail(7, "leave", "去る、出発する", "動詞", "You may leave the classroom after the teacher checks your work.", "先生があなたの課題を確認したら、教室を出てもかまいません。", "leave comes from Old English lǣfan, meaning to depart or let remain.")
add_detail(7, "take", "取る、持っていく", "動詞", "Please take your umbrella when you go outside today.", "今日は外へ行くときに傘を持っていってください。", "take comes from Old Norse taka, meaning to grasp or receive.")
add_detail(7, "eat", "食べる", "動詞", "We eat dinner together around seven o'clock every night.", "私たちは毎晩7時ごろ一緒に夕食を食べます。", "eat comes from Old English etan, meaning to consume food.")

# Q8
add_detail(8, "look", "見る", "動詞", "Please look at this picture before you choose an answer.", "答えを選ぶ前に、この絵を見てください。", "look comes from Old English lōcian, meaning to direct the eyes.")
add_detail(8, "see", "見る、分かる", "動詞", "I see your point, but I cannot join the movie today.", "あなたの言いたいことは分かりますが、今日は映画に参加できません。", "see comes from Old English sēon, meaning to perceive with the eyes.")
add_detail(8, "play", "遊ぶ、する", "動詞", "The children play soccer together after school every afternoon.", "子どもたちは毎日午後、放課後に一緒にサッカーをします。", "play comes from Old English plegian, meaning to exercise or have fun.")
add_detail(8, "stand", "立つ", "動詞", "Please stand near the door until your name is called.", "名前を呼ばれるまでドアの近くに立っていてください。", "stand comes from Old English standan, meaning to remain upright.")

# Q9
add_detail(9, "under", "〜の下に", "前置詞", "The cat is sleeping under the table in our kitchen.", "その猫は私たちの台所のテーブルの下で眠っています。", "under comes from Old English under, meaning below or beneath.")
add_detail(9, "with", "〜と一緒に", "前置詞", "I went to the park with my cousin yesterday afternoon.", "私は昨日の午後、いとこと一緒に公園へ行きました。", "with comes from Old English mid, a word for together or against.")
add_detail(9, "about", "〜について", "前置詞", "We talked about the school festival during our lunch break.", "私たちは昼休みに学校祭について話しました。", "about comes from Old English abūtan, meaning around or concerning.")
add_detail(9, "at", "〜で、〜に", "前置詞", "The students arrived at school before the first bell.", "生徒たちは始業のベルの前に学校へ到着しました。", "at comes from Old English æt, marking a place or time.")

# Q10
add_detail(10, "go", "行く", "動詞", "Dad and I go hiking in the hills every autumn.", "父と私は毎年秋に丘へハイキングに行きます。", "go comes from Old English gān, meaning to move or travel.")
add_detail(10, "want", "欲しい、望む", "動詞", "I want a warm drink after walking in the rain.", "私は雨の中を歩いた後、温かい飲み物が欲しいです。", "want comes from Old Norse vanta, meaning to lack or desire.")
add_detail(10, "close", "閉じる", "動詞", "Please close the window before you leave the room.", "部屋を出る前に窓を閉めてください。", "close comes from Old French clos, meaning shut or near.")
add_detail(10, "play", "遊ぶ、する", "動詞", "Can we play outside after we finish our homework today?", "今日は宿題を終えたら外で遊んでもいいですか。", "play comes from Old English plegian, meaning to exercise or have fun.")

# Q11
add_detail(11, "after", "〜の後に", "前置詞", "Taro visits the swimming pool after school on Tuesdays.", "太郎は火曜日に放課後、水泳プールへ行きます。", "after comes from Old English æfter, meaning later than.")
add_detail(11, "about", "〜について", "前置詞", "The teacher asked about our plans for the school trip.", "先生は私たちの修学旅行の計画について尋ねました。", "about comes from Old English abūtan, meaning around or concerning.")
add_detail(11, "down", "〜を下って、下へ", "前置詞", "The children walked down the road with their coach.", "子どもたちはコーチと一緒に道を下って歩きました。", "down comes from Old English dūne, meaning toward a lower place.")
add_detail(11, "on", "〜の上に、〜に接して", "前置詞", "There is a colorful picture on the classroom wall.", "教室の壁に色鮮やかな絵があります。", "on comes from Old English on, meaning in contact with or during.")

# Q12
add_detail(12, "sing", "歌う", "動詞", "My sister likes to sing songs while she cleans her room.", "姉は部屋を掃除しながら歌を歌うのが好きです。", "sing comes from Old English singan, meaning to make musical sounds.")
add_detail(12, "talk", "話す", "動詞", "Please talk quietly while the baby is sleeping upstairs.", "赤ちゃんが2階で寝ている間は静かに話してください。", "talk comes from Middle English talken, meaning to speak.")
add_detail(12, "close", "閉じる", "動詞", "The shop will close its doors at eight tonight.", "その店は今夜8時に店を閉めます。", "close comes from Old French clos, meaning shut or near.")
add_detail(12, "wake", "起きる、目を覚ます", "動詞", "I wake up early because my bus leaves at seven.", "私はバスが7時に出るので早く起きます。", "wake comes from Old English wacan, meaning to stop sleeping.")

# Q13
add_detail(13, "his", "彼の", "代名詞（所有格を含む）", "Mr. Ford brings his English books to every class.", "フォード先生は毎回の授業に彼の英語の本を持ってきます。", "his comes from Old English his, the possessive form of he.")
add_detail(13, "he", "彼は", "代名詞（所有格を含む）", "When he finishes practice, Ken walks home with friends.", "ケンは練習を終えると、友達と歩いて家へ帰ります。", "he comes from Old English hē, a masculine pronoun.")
add_detail(13, "him", "彼を、彼に", "代名詞（所有格を含む）", "We invited him to our school event last Saturday.", "私たちは先週の土曜日、彼を学校行事に招待しました。", "him comes from Old English him, the object form of he.")
add_detail(13, "us", "私たちを、私たちに", "代名詞（所有格を含む）", "Our teacher helps us with difficult homework after class.", "先生は授業の後、難しい宿題を私たちに手伝ってくれます。", "us comes from Old English ūs, the first-person plural object pronoun.")

# Q14
add_detail(14, "I", "私は、私が", "代名詞（所有格を含む）", "Only I can answer this question about the missing eraser.", "なくなった消しゴムについて、この質問に答えられるのは私だけです。", "I comes from Old English ic, the first-person singular pronoun.")
add_detail(14, "my", "私の", "代名詞（所有格を含む）", "My sister keeps spare pencils in a small box.", "姉は予備の鉛筆を小さな箱に入れています。", "my developed from Old English mīn, meaning belonging to me.")
add_detail(14, "me", "私を、私に", "代名詞（所有格を含む）", "Please call me when you find the blue eraser.", "青い消しゴムを見つけたら私に電話してください。", "me comes from Old English mē, the object form of I.")
add_detail(14, "mine", "私のもの", "代名詞（所有格を含む）", "That red notebook is mine, so please leave it here.", "あの赤いノートは私のものなので、ここに置いておいてください。", "mine comes from Old English mīn, meaning belonging to me.")

# Q15
add_detail(15, "is studying", "勉強している（主語が単数）", "動詞", "Kent is studying English in the library after school today.", "ケントは今日、放課後に図書館で英語を勉強しています。", "is combines be with studying to show an action continuing now.")
add_detail(15, "are studying", "勉強している（主語が複数・you）", "動詞", "The two students are studying together for tomorrow's test.", "その2人の生徒は明日のテストに向けて一緒に勉強しています。", "are combines be with studying to show an action continuing now.")
add_detail(15, "am studying", "勉強している（主語がI）", "動詞", "I am studying math now because the quiz starts soon.", "私は小テストがすぐ始まるので、今数学を勉強しています。", "am combines be with studying to show an action continuing now.")
add_detail(15, "studying", "勉強している（現在分詞）", "動詞", "She is studying quietly while her brother watches television.", "彼女は弟がテレビを見ている間、静かに勉強しています。", "studying is the -ing form of study, used for an action in progress.")


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def surface_occurrences(text: str, surface: str) -> int:
    pattern = rf"(?<![A-Za-z]){re.escape(surface)}(?![A-Za-z])"
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 15:
        raise ValueError("英検5級大問1は15問である必要があります")

    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 60:
        raise ValueError("英検5級大問1は60選択肢である必要があります")
    missing = []
    for question_index, question in enumerate(QUESTIONS, start=1):
        missing.extend(
            choice
            for choice in question["choices"]
            if (question_index, choice) not in DETAILS
        )
    missing = sorted(set(missing))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    missing_etymology = sorted(set(choices) - set(ETYMOLOGY))
    if missing_etymology:
        raise ValueError(f"語源情報がありません: {missing_etymology}")

    for q, question in enumerate(QUESTIONS, start=1):
        if len(question["choices"]) != 4 or question["answerIndex"] not in range(4):
            raise ValueError(f"Q{q}の4択または正答位置が不正です")
        if len(BLANK_RE.findall(question["stem"])) != 1:
            raise ValueError(f"Q{q}の空所が1か所ではありません")
        if re.search(r"\(\s*\)|（\s*）", question["translation"]):
            raise ValueError(f"Q{q}の和訳に空所記号があります")
        meanings = []
        positions = []
        for choice in question["choices"]:
            detail = DETAILS[(q, choice)]
            if surface_occurrences(detail["example"], choice) != 1:
                raise ValueError(f"Q{q}/{choice}の例文に見出し語句が1回ありません")
            if len(WORD_RE.findall(detail["example"])) < 8:
                raise ValueError(f"Q{q}/{choice}の例文が8語未満です")
            meanings.append(detail["meaning"])
            positions.append(detail["pos"])
        if len(set(meanings)) != 4:
            raise ValueError(f"Q{q}の意味が重複しています")
        if len(set(positions)) != 1:
            raise ValueError(f"Q{q}の品詞ラベルが揃っていません")

    meta = {
        "grade": "英検5級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "英検公式の過去問PDFを大問1だけ学習用JSONへ構造化",
        "source_problem_url": SOURCE_PROBLEM_URL,
        "source_answer_url": SOURCE_ANSWER_URL,
        "counts": {"words": 60, "idioms": 0, "total": 60},
    }
    question_data = {
        "meta": meta,
        "questions": [
            {"q": index, **question}
            for index, question in enumerate(QUESTIONS, start=1)
        ],
    }

    words = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, choice in enumerate(question["choices"]):
            detail = DETAILS[(q, choice)]
            words.append({
                "q": q,
                "is_answer": index == question["answerIndex"],
                "word": choice,
                "itemKey": f"q{q}-choice{index + 1}",
                **detail,
                "etymology": ETYMOLOGY[choice],
            })

    if len(words) != 60:
        raise ValueError(f"語句数が想定と違います: words={len(words)}")
    return {"meta": meta, "words": words, "idioms": []}, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / "vocab_5_2026-1.json", vocab)
    write_json(DATA_DIR / "questions_5_2026-1.json", questions)
    print("5級 2026-1 大問1: 15 questions / 60 words")


if __name__ == "__main__":
    main()
