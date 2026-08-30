"""英検2級Q1の共通メタデータと暗記カード用例文を適用する。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_IDS = ("2026-1", "2025-3", "2025-2")

sys.path.insert(0, str(ROOT / "scripts"))
from check_q1_data import surface_variants  # noqa: E402

SOURCE_URLS = {
    "2026-1": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2026-1-1ji-2kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202601F2kyu.pdf",
    },
    "2025-3": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2025-3-1ji-2kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202503F2kyu.pdf",
    },
    "2025-2": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2025-2-1ji-2kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202502F2kyu.pdf",
    },
}


# 公式問題の設問・選択肢・正答・安定IDは変更せず、暗記カードの例文だけを補正する。
# 1級・準1級と同じく、8語以上で見出し語句を1回含む例文に統一する。
EXAMPLE_OVERRIDES = {
    "2025-2": {
        "forgive": (
            "I forgive my brother when he sincerely apologizes for breaking my phone.",
            "弟が携帯電話を壊したことを心から謝れば、私は弟を許します。",
        ),
        "arrest": (
            "The police will arrest the suspect near the station after collecting evidence.",
            "証拠を集めた後、警察は駅の近くで容疑者を逮捕します。",
        ),
        "suffer": (
            "Many farmers suffer from drought when the rainy season arrives late.",
            "雨季の到来が遅れると、多くの農家が干ばつに苦しみます。",
        ),
        "reflect": (
            "A calm lake can reflect the mountains clearly on a sunny morning.",
            "穏やかな晴れた朝、静かな湖は山々をはっきり映します。",
        ),
        "expand": (
            "The city plans to expand its subway system over the next decade.",
            "その市は今後10年間で地下鉄網を拡張する計画です。",
        ),
        "influence": (
            "Her teacher continues to influence her decision to become a scientist.",
            "彼女の先生は、科学者になるという彼女の決断に影響を与え続けています。",
        ),
        "rob": (
            "Thieves may rob the bank if the alarm system stops working.",
            "警報システムが止まれば、泥棒たちは銀行を襲うかもしれません。",
        ),
        "qualify": (
            "She hopes to qualify for the Olympics after years of training.",
            "彼女は何年も訓練を続けた後、オリンピック出場資格を得たいと考えています。",
        ),
        "weigh": (
            "The nurse will weigh the baby immediately after he is born.",
            "看護師は、赤ちゃんが生まれた直後に体重を測ります。",
        ),
        "disappear": (
            "The sun will disappear behind the clouds within a few minutes.",
            "太陽は数分以内に雲の後ろへ消えるでしょう。",
        ),
        "complaint": (
            "The hotel received a serious complaint about noise from a guest.",
            "そのホテルは宿泊客から騒音について深刻な苦情を受けました。",
        ),
        "accept": (
            "She decided to accept the job offer after discussing it with her family.",
            "彼女は家族と相談した後、その仕事の申し出を受け入れることにしました。",
        ),
        "flatten": (
            "The strong storm could flatten several trees in the city park.",
            "その激しい嵐は市立公園の木を何本もなぎ倒す可能性があります。",
        ),
        "grip": (
            "The suspenseful novel can grip readers from its very first page.",
            "そのサスペンス小説は最初のページから読者を引き込むことがあります。",
        ),
        "promise": (
            "He will promise to call her as soon as he arrives.",
            "彼は到着したらすぐに彼女へ電話すると約束するでしょう。",
        ),
        "came down": (
            "Heavy rain came down on the town throughout the long afternoon.",
            "長い午後の間、激しい雨が町に降り続きました。",
        ),
        "jealous of": (
            "He felt jealous of his brother's success after the award ceremony.",
            "彼は表彰式の後、兄の成功をうらやましく思いました。",
        ),
        "confident of": (
            "She is confident of winning the national competition this year.",
            "彼女は今年、全国大会で優勝できると自信を持っています。",
        ),
        "turn in": (
            "Please turn in your homework by Friday morning before the class begins.",
            "授業が始まる前の金曜朝までに宿題を提出してください。",
        ),
        "feed on": (
            "Giant pandas feed mainly on bamboo in their natural mountain habitat.",
            "ジャイアントパンダは自然の山岳環境で主に竹を食べます。",
        ),
    },
    "2025-3": {
        "elastic": (
            "This elastic material stretches easily without losing its original shape.",
            "この伸縮性のある素材は、元の形を失わずに簡単に伸びます。",
        ),
        "troop": (
            "A troop of soldiers entered the town before sunrise to protect residents.",
            "兵士の一隊が住民を守るため、日の出前に町へ入りました。",
        ),
        "proverb": (
            "My grandmother often used an old proverb to teach patience and kindness.",
            "祖母は忍耐と親切を教えるため、古いことわざをよく使いました。",
        ),
        "exist": (
            "Many different opinions exist in the class about the new rule.",
            "そのクラスには新しい規則についてさまざまな意見があります。",
        ),
        "seize": (
            "The police will seize the stolen goods if the court approves the warrant.",
            "裁判所が令状を承認すれば、警察は盗品を押収します。",
        ),
        "disappear": (
            "The bright stars disappear when morning sunlight reaches the quiet valley.",
            "朝の日差しが静かな谷に届くと、明るい星々は消えます。",
        ),
        "spectator": (
            "Each spectator watched the final game from a crowded seat near the field.",
            "それぞれの観客は、競技場近くの混雑した席から決勝戦を見ました。",
        ),
        "fly": (
            "They will fly to Canada next week for a family holiday.",
            "彼らは来週、家族旅行のためカナダへ飛びます。",
        ),
        "swim": (
            "The children swim in the lake every summer during their school vacation.",
            "子どもたちは学校の休暇中、毎年夏に湖で泳ぎます。",
        ),
        "recover": (
            "Most patients recover quickly from this illness with proper medical treatment.",
            "適切な治療を受ければ、ほとんどの患者はこの病気からすぐ回復します。",
        ),
        "tie": (
            "Neil stopped to tie his shoelaces before entering the crowded classroom.",
            "ニールは混雑した教室に入る前に、靴ひもを結ぶため立ち止まりました。",
        ),
        "earn": (
            "She hopes to earn enough money by teaching piano to local children.",
            "彼女は地元の子どもたちにピアノを教えて、十分なお金を稼ぎたいと考えています。",
        ),
        "pour": (
            "Please pour some hot tea into this cup for our guest.",
            "このカップに熱いお茶を少し注いで、お客さまに出してください。",
        ),
        "fortune": (
            "She made a small fortune by selling handmade furniture online.",
            "彼女は手作り家具をオンラインで販売して、小さな財産を築きました。",
        ),
        "suspicion": (
            "The strange noise filled her with suspicion about the empty house.",
            "その奇妙な物音は、空き家についての疑いを彼女に抱かせました。",
        ),
        "wealth": (
            "The country gained great wealth from trade over several centuries.",
            "その国は数世紀にわたる貿易で大きな富を得ました。",
        ),
        "poverty": (
            "The charity helps children living in poverty in several rural communities.",
            "その慈善団体は、いくつかの地方社会で貧困の中に暮らす子どもたちを支援します。",
        ),
        "innocently": (
            "The child innocently denied taking the cookie from the kitchen.",
            "その子は台所からクッキーを取ったことを無邪気に否定しました。",
        ),
        "traditionally": (
            "This festival is traditionally held in spring by local families.",
            "この祭りは地元の家族によって、伝統的に春に開催されます。",
        ),
        "resentfully": (
            "He resentfully accepted the decision after hearing the manager's explanation.",
            "彼は支配人の説明を聞いた後、不満そうにその決定を受け入れました。",
        ),
        "shake hands": (
            "The two leaders shake hands after signing the agreement in public.",
            "二人の指導者は、公の場で合意書に署名した後、握手をします。",
        ),
        "give way": (
            "Drivers must give way to pedestrians at the busy crossing.",
            "運転手はその混雑した横断歩道で歩行者に道を譲らなければなりません。",
        ),
        "take pains": (
            "I take pains to review all new vocabulary every night before bed.",
            "私は毎晩寝る前に、新しい語彙をすべて復習するよう心がけています。",
        ),
        "make sense": (
            "Your explanation will make sense after we review the diagram together.",
            "一緒に図を見直せば、あなたの説明は理解できるようになります。",
        ),
        "put away": (
            "Please put away your toys before the guests arrive this evening.",
            "今晩、来客が到着する前に、おもちゃを片付けてください。",
        ),
        "consist of": (
            "The committee will consist of ten members from different schools.",
            "その委員会は異なる学校から来た10人のメンバーで構成されます。",
        ),
        "all or nothing": (
            "The risky investment forced the committee to choose an all or nothing strategy.",
            "その危険な投資によって、委員会は全か無かの方針を選ばざるを得ませんでした。",
        ),
        "safe and sound": (
            "The cat came home safe and sound before the storm began.",
            "その猫は嵐が始まる前に、無事に帰宅しました。",
        ),
        "as fast as": (
            "The athlete ran as fast as she could during the final race.",
            "その選手は決勝レースで、できる限り速く走りました。",
        ),
        "as well as": (
            "She speaks Spanish as well as English at work and at home.",
            "彼女は職場でも家庭でも、英語だけでなくスペイン語も話します。",
        ),
    },
    "2026-1": {
        "surgeon": (
            "The surgeon performed the operation carefully in the city hospital yesterday.",
            "外科医は昨日、市立病院で慎重に手術を行いました。",
        ),
        "priority": (
            "During the emergency, protecting children became our top priority.",
            "緊急事態の間、子どもたちを守ることが私たちの最優先事項になりました。",
        ),
        "discrimination": (
            "Strong laws should protect every worker from discrimination at work.",
            "強い法律は、職場であらゆる労働者を差別から守るべきです。",
        ),
        "shelter": (
            "The hikers found shelter from the heavy rain inside an old cabin.",
            "ハイカーたちは激しい雨から逃れるため、古い小屋の中に避難場所を見つけました。",
        ),
        "hate": (
            "I hate getting up early on cold winter mornings.",
            "私は寒い冬の朝に早起きするのが嫌いです。",
        ),
        "divide": (
            "Please divide the cake into eight equal pieces for the children.",
            "子どもたちのために、そのケーキを8つの同じ大きさに分けてください。",
        ),
        "pronounce": (
            "Can you pronounce this difficult word clearly for the class?",
            "この難しい単語をクラスのみんなにはっきり発音できますか。",
        ),
        "chemical": (
            "The factory stores each dangerous chemical in a locked cabinet.",
            "その工場は危険な化学物質を一つずつ鍵のかかった戸棚に保管しています。",
        ),
        "occur": (
            "Serious accidents can occur when drivers ignore warning signs.",
            "運転手が警告標識を無視すると、重大な事故が起こることがあります。",
        ),
        "tap": (
            "Please tap the screen twice to open the application.",
            "アプリケーションを開くには、画面を2回タップしてください。",
        ),
        "illustrate": (
            "The diagram will illustrate how cells work inside the human body.",
            "その図は細胞が人体の中でどのように働くかを説明します。",
        ),
        "occupy": (
            "These large boxes occupy the whole shelf in our storage room.",
            "これらの大きな箱は、倉庫の棚全体を占めています。",
        ),
        "polish": (
            "She will polish the silver dishes before the formal dinner.",
            "彼女は正式な夕食会の前に銀の食器を磨くでしょう。",
        ),
        "congratulate": (
            "We will congratulate her on passing the exam after the ceremony.",
            "式典の後、私たちは試験に合格した彼女を祝福します。",
        ),
        "secretly": (
            "She secretly planned a surprise party for her father's birthday.",
            "彼女は父親の誕生日のために、秘密裏にサプライズパーティーを計画しました。",
        ),
        "repeatedly": (
            "She repeatedly checked her phone for messages during the long meeting.",
            "彼女は長い会議中、メッセージがないか携帯電話を何度も確認しました。",
        ),
        "frown": (
            "The students frown whenever teachers announce an unexpected test.",
            "教師が予想外のテストを発表すると、学生たちはいつも顔をしかめます。",
        ),
        "slip": (
            "Drivers may slip on the icy road during winter storms.",
            "冬の嵐の間、運転手は凍った道路で滑ることがあります。",
        ),
        "crawl": (
            "The baby began to crawl across the floor toward his mother.",
            "赤ちゃんは母親に向かって床をはい始めました。",
        ),
        "on one's own": (
            "The expression on one's own means doing something without help from others.",
            "「on one's own」という表現は、他人の助けなしに何かをすることを意味します。",
        ),
        "at a distance": (
            "At a distance, the mountain looked purple beneath the evening sky.",
            "遠くから見ると、その山は夕空の下で紫色に見えました。",
        ),
        "to one's surprise": (
            "To one's surprise, the quiet village becomes lively after sunset.",
            "驚いたことに、静かな村は日没後に活気づきます。",
        ),
        "take away from": (
            "Loud noise can take away from the enjoyment of a concert.",
            "大きな音はコンサートを楽しむことの妨げになる場合があります。",
        ),
        "bring out in": (
            "The teacher knows how to bring out in students a love of science.",
            "その教師は、生徒たちの中に科学への愛情を引き出す方法を知っています。",
        ),
        "back and forth": (
            "The discussion moved back and forth before the committee reached a decision.",
            "委員会が決定に達するまで、議論は行ったり来たりしました。",
        ),
        "composed of": (
            "The machine is composed of several parts that work together.",
            "その機械は、一緒に動くいくつかの部品で構成されています。",
        ),
        "flip over": (
            "Please flip over the card to read the information on the back.",
            "裏の情報を読むために、そのカードを裏返してください。",
        ),
        "bring about": (
            "The new policy may bring about positive changes in our community.",
            "その新しい方針は、地域社会に前向きな変化をもたらすかもしれません。",
        ),
    },
}


WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
BLANK_RE = re.compile(r"(?:\(\s*\)|（\s*）)")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    newline = "\r\n" if b"\r\n" in path.read_bytes() else "\n"
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if newline == "\r\n":
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def normalize_surface(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def item_surface(item: dict) -> str:
    return str(item.get("phrase") or item.get("word") or "").strip()


def surface_matches(example: str, surface: str) -> list[re.Match[str]]:
    parts = surface.split()
    exact = re.compile(
        rf"(?<![A-Za-z]){re.escape(surface)}(?![A-Za-z])",
        flags=re.IGNORECASE,
    )
    matches = list(exact.finditer(example))
    if matches or len(parts) != 2:
        return matches
    separated = re.compile(
        rf"(?<![A-Za-z]){re.escape(parts[0])}(?:\s+[A-Za-z]+){{1,5}}\s+{re.escape(parts[1])}(?![A-Za-z])",
        flags=re.IGNORECASE,
    )
    return list(separated.finditer(example))


def surfaces_match(left: str, right: str) -> bool:
    return bool(surface_variants(left) & surface_variants(right))


def metadata(round_id: str, existing: dict) -> dict:
    urls = SOURCE_URLS[round_id]
    result = dict(existing or {})
    result.update(
        {
            "grade": "英検2級",
            "round": round_id,
            "section": "Reading 大問1（語句空所補充）",
            "source": "英検公式の公開過去問PDFを、学習用JSONへ大問1だけ構造化",
            "source_problem_url": urls["problem"],
            "source_answer_url": urls["answer"],
            "counts": {"words": 40, "idioms": 28, "total": 68},
        }
    )
    return result


def apply_round(round_id: str) -> None:
    if round_id not in ROUND_IDS:
        raise ValueError(f"未登録の2級回です: {round_id}")

    questions_path = DATA_DIR / f"questions_{round_id}.json"
    vocab_path = DATA_DIR / f"vocab_{round_id}.json"
    questions_data = load_json(questions_path)
    vocab_data = load_json(vocab_path)
    questions = questions_data.get("questions", [])
    words = vocab_data.get("words", [])
    idioms = vocab_data.get("idioms", [])
    all_items = [*words, *idioms]
    if len(questions) != 17:
        raise ValueError(f"{round_id}: 2級は17問である必要があります")
    if len(words) != 40 or len(idioms) != 28:
        raise ValueError(f"{round_id}: 語句構成が40語・28熟語から変わっています")

    overrides = EXAMPLE_OVERRIDES[round_id]
    items_by_surface = {normalize_surface(item_surface(item)): item for item in all_items}
    missing = sorted(set(overrides) - set(items_by_surface))
    if missing:
        raise ValueError(f"{round_id}: 例文補正の対象語句が語彙データにありません: {', '.join(missing)}")
    for surface, (example, translation) in overrides.items():
        item = items_by_surface[normalize_surface(surface)]
        item["example"] = example
        item["exampleTranslation"] = translation

    questions_by_q = {int(question["q"]): question for question in questions}
    items_by_q: dict[int, list[dict]] = {}
    for item in all_items:
        items_by_q.setdefault(int(item["q"]), []).append(item)
    if sorted(questions_by_q) != list(range(1, 18)):
        raise ValueError(f"{round_id}: 設問番号が1〜17で連続していません")

    for q in range(1, 18):
        question = questions_by_q[q]
        choices = question.get("choices", [])
        answer_index = question.get("answerIndex")
        items = items_by_q.get(q, [])
        if len(choices) != 4 or len(items) != 4 or answer_index not in range(4):
            raise ValueError(f"{round_id}: Q{q}の4択・語句・正答位置が不正です")
        if not str(question.get("translation", "")).strip() or BLANK_RE.search(
            str(question.get("translation", ""))
        ):
            raise ValueError(f"{round_id}: Q{q}の設問文訳が空または空所記号を含みます")
        answer_surface = str(choices[answer_index])
        matched = [item for item in items if surfaces_match(answer_surface, item_surface(item))]
        if len(matched) != 1:
            raise ValueError(f"{round_id}: Q{q}の正答語句が語彙データと一致しません")
        for item in items:
            item["is_answer"] = item is matched[0]

    for item in all_items:
        surface = item_surface(item)
        example = str(item.get("example", ""))
        if not all(str(item.get(field, "")).strip() for field in ("meaning", "pos", "exampleTranslation")):
            raise ValueError(f"{round_id}: {surface}の学習項目が不足しています")
        if len(WORD_RE.findall(example)) < 8 or len(surface_matches(example, surface)) != 1:
            raise ValueError(f"{round_id}: {surface}の例文が整合基準を満たしません")

    questions_data["meta"] = metadata(round_id, questions_data.get("meta", {}))
    vocab_data["meta"] = metadata(round_id, vocab_data.get("meta", {}))
    write_json(questions_path, questions_data)
    write_json(vocab_path, vocab_data)


__all__ = ["EXAMPLE_OVERRIDES", "ROUND_IDS", "apply_round"]
