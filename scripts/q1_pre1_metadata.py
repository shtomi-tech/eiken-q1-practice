"""準1級Q1の共通メタデータと設問文訳を適用する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_IDS = ("2026-1", "2025-3", "2025-2")

SOURCE_URLS = {
    "2026-1": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2026-1-1ji-p1kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202601Fp1kyu.pdf",
    },
    "2025-3": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2025-3-1ji-p1kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202503Fp1kyu.pdf",
    },
    "2025-2": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2025-2-1ji-p1kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202502Fp1kyu.pdf",
    },
}


# 公式問題の設問文は変更せず、学習画面で表示する自然な和訳だけを管理する。
QUESTION_TRANSLATIONS = {
    "2025-2": (
        "その夫婦は、田舎の家があまりにも辺鄙だったので、買わないことにした。最寄りの町までは車で2時間以上かかった。",
        "犬は人間と比べて聴覚に優れている。人には聞こえないが、犬には聞き取れる音がたくさんある。",
        "新しい高速道路は、郊外から車で通勤する人々にとって有益なはずだ。市内へ車で入るのに必要な時間は10パーセント短くなると予想されている。",
        "ロジャーは販売1件ごとに20パーセントの手数料を得ていたため、できるだけ多くの車を売ろうと躍起だった。彼はその余分なお金で世界中を旅行するつもりだった。",
        "医師はエマに、働きすぎで疲労に苦しんでいると告げた。しかし、休みを取り、十分に休養すれば、すぐに回復するだろうと言った。",
        "ケビンは、前のトラックが突然停止したとき、危うくトラックに突っ込むところだった。彼は急ブレーキを踏み、どうにか衝突を避けた。",
        "教授はクラスに、遅刻を容認しないと告げた。時間どおりに提出されなかったレポートには不合格の評価を付けると言った。",
        "太陽は地球から見ると小さく見えるかもしれないが、実際には巨大だ。事実、太陽は太陽系のどの惑星よりも何倍も大きい。",
        "A: マジード、会議室Bには何人収容できるか、もう一度教えて。B: 15人だから、今日の会議には大丈夫なはずだ。",
        "会社の社長は、人員削減の理由について率直ではなかった。尋ねられても、曖昧な答えしかせず、直接的な発言を避けた。",
        "その政治家は誰にも借りがないと主張したが、実際には選挙運動を支援するために多くの企業から寄付を受け取っていた。",
        "保護者は、子どもたちを学校のダンスパーティーへ送り迎えするよう求められた。夕方に開催されるため、学校当局は子どもたちが一人で行くことを望まなかった。",
        "そのクッキー工場は、砂糖の代わりに塩を使ったクッキーを1バッチ作ってしまった。工場はその全ロットを廃棄しなければならなかった。",
        "戦争についてのそのドキュメンタリーは非常に力強く、視聴者の中に強い悲しみと怒りの感情を呼び起こした。",
        "旅行代理店は、その格安航空会社の便が時間どおりに運航すると当てにしないよう夫婦に警告した。便はしばしば遅延または欠航になっていた。",
        "その国の軍は、敵の偵察用ドローンが国防に関する情報を集める前に、それを撃墜することができた。",
        "市は古い劇場を取り壊し、同じ場所に新しい劇場を建てる計画だが、多くの住民はその計画に不満を抱いている。",
        "A: ジェーン、山頂から下りるのにどのくらいかかるの？ B: 約3時間だけど、ゆっくり歩けばもっとかかるよ。",
    ),
    "2025-3": (
        "刑務所から脱走した男たちは3週間にわたり警察から逃れていたが、ついに捕まり、連れ戻された。",
        "その小説が魅力的だったのは、同じ物語をいくつかの異なる観点から描いていたからだ。登場人物はそれぞれ、出来事を大きく異なる見方で捉えていた。",
        "そのアパートの寝室はかなり広々としていたが、台所とダイニングルームは狭かったので、夫婦は借りないことにした。",
        "大学は来月、次の学期にそこへ入学することを考えている高校卒業予定者向けのイベントを開く。",
        "実際の戦闘はほぼ1週間続いたが、作家は小説をより劇的にするため、すべての出来事を1日に圧縮することにした。",
        "隣り合う2つのチームの競争意識は非常に強い。時には選手同士が試合中にけんかまでした。",
        "A: ジョージ、春休みはどこかへ行くの？ B: スペインを訪れる仮の計画はあるけど、まだ何も予約していないよ。",
        "医学生は人間の解剖学を学ぶのに多くの時間を費やす。体の最も小さな部分についても用語を暗記しなければならない。",
        "山を登るのに2日かかった一方で、登山者たちは12時間未満で下山できた。",
        "2機の戦闘機は非常に近くを飛んでいたため、片方の操縦士は衝突するのではないかと心配した。",
        "技術者はねじを慎重に外した後、コンピューターから電源装置を切り離し、新しいものに交換することができた。",
        "会社は営業担当者に日々の仕事について自主性を与えた。今では、経営陣の承認を得なくても自分で決定できる。",
        "ニュー・クロワ市は国際的な文化で知られている。世界中から人々が移り住み、多様なレストランや地区で有名だ。",
        "その少女は母親からもらった新しい子犬について祖母に話すとき、目をきらりと輝かせていた。とても幸せなのは明らかだった。",
        "子どもたちは空腹だったので、その夫婦は最寄りの町へ向かうことにした。そこならレストランが見つかると思ったのだ。",
        "ジュリアは息子のロブが家でもっと責任を引き受けられる年齢になったと考え、週末にする仕事を2つ追加で与えることにした。",
        "会社はまず他の選択肢をすべて試したいと考えているが、売上不振が続けば人員削減の可能性を排除することはできない。",
        "映画スターはインタビュー後もその場に残るよう記者に頼んだ。残ってくれれば、独占記事を提供すると約束した。",
    ),
    "2026-1": (
        "細胞がどのように機能するかを説明するため、生物の教師はその細胞のすべての部分を示す詳細な図を黒板に描いた。",
        "A: あなたの作文のこの文は余分じゃないかな。 B: ああ、そうだね。前の段落で私が言ったこととほとんど同じだ。",
        "一部の国では、政府が批判を公表されないようにするため、メディアを検閲している。",
        "奨学金は条件を満たす学生だけが利用できる。受取人は優秀な成績を収め、低所得の家庭の出身でなければならない。",
        "科学者は、専門家たちが実験を再現しようとしたものの同じ結果を出せなかった後、データを捏造したとして非難された。",
        "先週、警察官はハビエルを止め、制限速度を超えて運転したとして交通違反切符を渡した。",
        "乱気流が予想されたため、機長はシートベルト着用サインを点灯し、乗客全員に席へ戻るよう求めた。",
        "数年間ほとんど雨が降らなかった後、その地域は木や他の植物が生き残れない不毛の荒れ地になった。",
        "サイモンがロープを引っ張ると、ロープは突然たるんだ。反対側で結び目がほどけたに違いないと彼は気づいた。",
        "患者はビタミン不足と診断された。医師は、ビタミンの濃度が再び正常になるまでサプリメントを摂る必要があると述べた。",
        "ターニャは新しい学校に入ったときは内気で緊張しているようだったが、今では社交面でうまくいっており、たくさんの友人ができた。",
        "美術を学ぶ学生は自分の作品集を画廊の経営者に見せた。それには絵画、デッサン、写真の作例が含まれていた。",
        "教師は生徒に作文を短くするよう頼んだ。元の長さの半分ほどにすべきだと言った。",
        "患者はあまりにも痛がっていたので、歯科医はその患者の損傷した歯を抜くしかなかった。",
        "その会社は金融危機に大きな打撃を受け、ほとんど倒産したが、現在は回復して再び利益を上げている。",
        "警察官は、その男の話がつじつまの合わないことから、男を怪しいと思った。男は後に警察にうそをついていたことが分かった。",
        "患者は誰にも気づかれずに病院からこっそり立ち去ろうとしたが、看護師に見つかり、止められた。",
        "A: 会議の準備が予想以上に長くかかった。 B: ああ、予算の確認に午後の大半を取られたね。",
    ),
}


# 1級の整合基準（8語以上・見出し語句を1回）に満たない既存例文だけを補正する。
# 設問文・選択肢・正答とは独立した暗記カード用の例文である。
EXAMPLE_OVERRIDES = {
    "2025-2": {
        "cheery": (
            "The children gave the tired nurse a cheery welcome at the hospital.",
            "子どもたちは病院で、疲れた看護師を明るく迎えた。",
        ),
        "elevate": (
            "Regular exercise can elevate your mood after a stressful day at work.",
            "定期的な運動は、仕事で大変な一日を過ごした後の気分を高めることがある。",
        ),
        "humiliate": (
            "The coach refused to humiliate the player after the public mistake.",
            "その監督は、公の場でミスをした選手に恥をかかせることを拒んだ。",
        ),
        "plead": (
            "The defendant continued to plead for mercy during the long hearing.",
            "被告は長い審理の間、情けをかけてくれるよう懇願し続けた。",
        ),
        "import": (
            "The country must import more wheat when domestic harvests are poor.",
            "国内の収穫が不作のとき、その国はより多くの小麦を輸入しなければならない。",
        ),
        "escort": (
            "Trained volunteers will escort elderly visitors through the crowded museum.",
            "訓練を受けたボランティアが、混雑した博物館で高齢の来館者に付き添う。",
        ),
        "shoot down": (
            "The air force may shoot down the drone if it enters restricted airspace.",
            "そのドローンが立入制限空域に入れば、空軍は撃墜する可能性がある。",
        ),
        "snap up": (
            "Customers quickly snap up discounted tickets when the popular show opens.",
            "人気の公演の販売が始まると、客は割引チケットをすぐに買い取る。",
        ),
        "tune up": (
            "The mechanic will tune up the engine before the family starts its journey.",
            "整備士は、その家族が旅を始める前にエンジンを調整する。",
        ),
        "touch on": (
            "The final lecture will touch on several causes of urban migration.",
            "最後の講義では、都市への人口移動のいくつかの原因に軽く触れる。",
        ),
        "tear down": (
            "The city plans to tear down the unsafe bridge next summer.",
            "市は来年の夏に、その危険な橋を取り壊す計画だ。",
        ),
        "free up": (
            "The revised schedule should free up time for teachers to prepare lessons.",
            "改訂された予定表により、教師が授業を準備する時間を空けられるはずだ。",
        ),
        "die away": (
            "The sound of the festival drums began to die away after midnight.",
            "祭りの太鼓の音は、真夜中を過ぎると次第に消え始めた。",
        ),
        "lay out": (
            "The architect will lay out the new plan before the committee meets.",
            "建築家は委員会が開かれる前に、新しい計画を説明する。",
        ),
    },
    "2025-3": {
        "radiating": (
            "The radiating heat from the pavement made the afternoon walk uncomfortable.",
            "舗装道路から放たれる熱で、午後の散歩は不快なものになった。",
        ),
        "solidifying": (
            "The solidifying mixture must be stirred carefully before it becomes too hard.",
            "固まりつつある混合物は、硬くなりすぎる前に注意深くかき混ぜなければならない。",
        ),
        "haunt": (
            "Memories of the accident can haunt survivors for many years afterward.",
            "事故の記憶は、その後何年も生存者を苦しめることがある。",
        ),
        "obstruct": (
            "A fallen tree may obstruct the mountain road after a severe storm.",
            "激しい嵐の後には、倒木が山道をふさぐことがある。",
        ),
        "collide": (
            "The two cyclists might collide if they ignore the warning signs.",
            "警告標識を無視すると、その2人の自転車乗りは衝突するかもしれない。",
        ),
        "unfold": (
            "The historian watched the evidence unfold as new documents were discovered.",
            "新しい文書が発見されるにつれ、歴史学者は証拠が明らかになっていく様子を見守った。",
        ),
        "bundle": (
            "Workers bundle the newspapers before loading them onto the delivery truck.",
            "作業員は配達トラックに積み込む前に、新聞を束ねる。",
        ),
        "gloomy": (
            "The gloomy forecast discouraged tourists from visiting the coastal town.",
            "暗い予報を聞いて、観光客は海辺の町を訪れる気をなくした。",
        ),
        "perch": (
            "The bird can perch on the narrow branch above the quiet stream.",
            "その鳥は、静かな小川の上にある細い枝に止まることができる。",
        ),
        "breeze": (
            "A cool breeze entered through the open window during the lecture.",
            "講義中、開いた窓から涼しいそよ風が入ってきた。",
        ),
        "gleam": (
            "A faint gleam appeared on the horizon just before sunrise.",
            "日の出の直前、水平線にかすかな光が現れた。",
        ),
        "sizzle": (
            "The vegetables began to sizzle when the chef added them to the pan.",
            "料理人が野菜をフライパンに入れると、野菜はジュウジュウと音を立て始めた。",
        ),
        "live off": (
            "Some artists live off irregular income while building their careers.",
            "芸術家の中には、仕事を築きながら不定期の収入に頼って暮らす人もいる。",
        ),
        "make for": (
            "These quiet surroundings make for a pleasant place to study.",
            "この静かな環境は、勉強するのに快適な場所を作り出す。",
        ),
        "wipe out": (
            "A single disease could wipe out the entire crop without treatment.",
            "治療をしなければ、1つの病気で作物全体が全滅する可能性がある。",
        ),
        "size up": (
            "The detective took time to size up the suspect before asking questions.",
            "その刑事は質問する前に、容疑者を見極めるため時間をかけた。",
        ),
        "sound off": (
            "Some commentators sound off about policy without checking the available evidence.",
            "一部の評論家は、入手できる証拠を確認せずに政策について大声で不満を言う。",
        ),
        "draw back": (
            "The frightened horse may draw back when the gate suddenly opens.",
            "門が突然開くと、おびえた馬は後ずさりするかもしれない。",
        ),
        "turn up": (
            "The missing documents may turn up after the archive is searched.",
            "その行方不明の文書は、書庫を探せば見つかるかもしれない。",
        ),
        "rule out": (
            "Doctors cannot rule out infection until the laboratory results arrive.",
            "検査室の結果が出るまで、医師は感染の可能性を排除できない。",
        ),
        "chip in": (
            "All the neighbors agreed to chip in for the community garden.",
            "近所の人たちは皆、地域の庭のためにお金を出し合うことに同意した。",
        ),
        "bear up": (
            "She managed to bear up despite the pressure of the public investigation.",
            "彼女は公の調査によるプレッシャーにもかかわらず、何とか耐えた。",
        ),
    },
    "2026-1": {
        "haul": (
            "The fishermen will haul the heavy nets onto the deck before sunset.",
            "漁師たちは日没前に、重い網を甲板へ引き上げる。",
        ),
        "subtract": (
            "Students should subtract the smaller number from the larger number carefully.",
            "生徒は小さい数を大きい数から注意深く引くべきだ。",
        ),
        "censor": (
            "Some governments censor online reports that criticize their official policies.",
            "政府の公式政策を批判するオンライン報道を検閲する政府もある。",
        ),
        "successor": (
            "The board will introduce the CEO's successor at the annual meeting.",
            "取締役会は年次会議で、最高経営責任者の後任を紹介する。",
        ),
        "triggering": (
            "Triggering a panic attack is a serious risk for vulnerable patients.",
            "パニック発作を引き起こすことは、影響を受けやすい患者にとって重大なリスクだ。",
        ),
        "renouncing": (
            "Renouncing the inheritance allowed him to avoid a complicated legal dispute.",
            "相続を放棄することで、彼は複雑な法的争いを避けることができた。",
        ),
        "vital": (
            "Reliable electricity is vital for hospitals that provide emergency care.",
            "信頼できる電力は、救急医療を提供する病院に不可欠だ。",
        ),
        "emission": (
            "The factory reduced its carbon emission after installing new filters.",
            "その工場は新しいフィルターを設置した後、炭素排出量を減らした。",
        ),
        "pledging": (
            "Pledging support for the project required a formal statement from the union.",
            "その計画への支持を約束するには、組合による正式な声明が必要だった。",
        ),
        "abbreviate": (
            "Editors often abbreviate long technical terms in newspaper headlines.",
            "編集者は新聞の見出しで、長い専門用語を略すことが多い。",
        ),
        "attest": (
            "Several colleagues can attest to her honesty during the difficult investigation.",
            "困難な調査の間、何人かの同僚が彼女の誠実さを証明できる。",
        ),
        "carve": (
            "The artist will carve a detailed pattern into the wooden panel.",
            "その芸術家は木製パネルに細かな模様を彫る。",
        ),
        "yield": (
            "The fertile field may yield a larger harvest after careful irrigation.",
            "その肥沃な畑は、注意深く灌漑すればより多くの収穫をもたらすかもしれない。",
        ),
        "radiate": (
            "The stove can radiate enough heat to warm the small cabin.",
            "そのストーブは、小さな小屋を暖めるのに十分な熱を放射できる。",
        ),
        "sank in": (
            "The seriousness of the announcement slowly sank in during the meeting.",
            "会議中、その発表の重大さが徐々に理解されていった。",
        ),
        "take off": (
            "The new product could take off after a successful television campaign.",
            "その新製品は、テレビキャンペーンが成功すれば急速に売れるかもしれない。",
        ),
        "fall out": (
            "The two partners might fall out over the terms of the contract.",
            "その2人の共同経営者は、契約条件をめぐって仲たがいするかもしれない。",
        ),
        "slip away": (
            "The suspect tried to slip away before the security guard noticed him.",
            "容疑者は警備員に気づかれる前に、こっそり立ち去ろうとした。",
        ),
        "tear up": (
            "She decided to tear up the outdated agreement after consulting her lawyer.",
            "彼女は弁護士に相談した後、古い契約書を破棄することに決めた。",
        ),
        "drop out": (
            "Some students drop out when financial problems make university unaffordable.",
            "経済的な問題で大学に通えなくなると、中退する学生もいる。",
        ),
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    newline = "\r\n" if b"\r\n" in path.read_bytes() else "\n"
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if newline == "\r\n":
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def metadata(round_id: str) -> dict:
    urls = SOURCE_URLS[round_id]
    return {
        "grade": "英検準1級",
        "round": round_id,
        "section": "Reading 大問1（語句空所補充）",
        "source": "英検公式の公開過去問PDFを、学習用JSONへ大問1だけ構造化",
        "source_problem_url": urls["problem"],
        "source_answer_url": urls["answer"],
        "counts": {"words": 72, "idioms": 0, "total": 72},
    }


def apply_round(round_id: str) -> None:
    if round_id not in ROUND_IDS:
        raise ValueError(f"未登録の準1級回です: {round_id}")
    translations = QUESTION_TRANSLATIONS[round_id]
    questions_path = DATA_DIR / f"questions_pre1_{round_id}.json"
    vocab_path = DATA_DIR / f"vocab_pre1_{round_id}.json"
    questions_data = load_json(questions_path)
    vocab_data = load_json(vocab_path)
    questions = questions_data.get("questions", [])
    words = vocab_data.get("words", [])
    if len(questions) != 18 or len(translations) != 18:
        raise ValueError(f"{round_id}: 準1級は18問・18訳である必要があります")
    if len(words) != 72 or vocab_data.get("idioms", []):
        raise ValueError(f"{round_id}: 準1級の語句構成が18問・72語から変わっています")

    overrides = EXAMPLE_OVERRIDES.get(round_id, {})
    word_surfaces = {str(item.get("word", "")) for item in words}
    if set(overrides) - word_surfaces:
        raise ValueError(f"{round_id}: 例文補正の対象語が語彙データにありません")
    for item in words:
        override = overrides.get(str(item.get("word", "")))
        if override:
            item["example"], item["exampleTranslation"] = override

    items_by_q = {}
    for item in words:
        items_by_q.setdefault(int(item["q"]), []).append(item)
    for index, question in enumerate(questions):
        q = int(question["q"])
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        items = items_by_q.get(q, [])
        if len(choices) != 4 or len(items) != 4 or answer_index not in range(4):
            raise ValueError(f"{round_id}: Q{q}の4択・語句・正答位置が不正です")
        answer_surface = choices[answer_index]
        matched = [item for item in items if item.get("word") == answer_surface]
        if len(matched) != 1:
            raise ValueError(f"{round_id}: Q{q}の正答語句が語彙データと一致しません")
        question["translation"] = translations[index]
        for item in items:
            item["is_answer"] = item.get("word") == answer_surface

    meta = metadata(round_id)
    questions_data["meta"] = dict(meta)
    vocab_data["meta"] = dict(meta)
    write_json(questions_path, questions_data)
    write_json(vocab_path, vocab_data)


__all__ = ["ROUND_IDS", "apply_round"]
