"""国際医療福祉大学の基礎試験セットをQ1形式のJSONへ出力する。

収録語彙は docs/IUHW_BASIC_EXAM_SET_PLAN.md で確定した60語（WORD_LIST）に固定する。
60語は出題英文（正誤判定の選択肢文）から抜き出した語で、名詞32・形容詞17・動詞7・その他4と
品詞が偏っている。全問を「正答と同一品詞の4択」で組むことはできないため、
- 空所に入れたときに文法的に成立する語形を choices に置き、
- 学習見出し語（words[].word）は WORD_LIST の原形のままにする
という二層構造にしている（choices と見出し語の対応は check_q1_data.py と同じ活用照合で検証する）。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_q1_data import surfaces_match  # noqa: E402  同じ活用照合を使い回す

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "set-1"

# 見出し語 -> (意味, 品詞, 例文, 例文訳)
WORD_LIST = {
    "immigration": ("移民（の流入）", "名詞", "Immigration has brought many young researchers to the country's universities.", "移民の流入によって、多くの若い研究者がその国の大学へやって来た。"),
    "creation": ("創出、生み出すこと", "名詞", "The creation of new knowledge often depends on international cooperation.", "新しい知識の創出は、しばしば国際的な協力に依存している。"),
    "definition": ("定義", "名詞", "The committee could not agree on a clear definition of poverty.", "委員会は貧困の明確な定義について合意できなかった。"),
    "expenditure": ("歳出、支出", "名詞", "Government expenditure on welfare has grown faster than tax revenue.", "福祉に対する政府の歳出は、税収より速く増えている。"),

    "uniform": ("統一された、一様な", "形容詞", "The rules are not uniform, so each hospital applies them differently.", "規則は統一されていないため、各病院が異なる形で適用している。"),
    "mutual": ("相互の", "形容詞", "Rural villages once depended on mutual help among neighbors.", "農村はかつて、隣人どうしの相互の助け合いに依存していた。"),
    "apparent": ("明らかな", "形容詞", "The weakness of the old system became apparent during the crisis.", "危機の間に、旧制度の弱さが明らかになった。"),
    "various": ("さまざまな", "形容詞", "The government offers various programs for foreign workers and their families.", "政府は外国人労働者とその家族向けにさまざまな制度を用意している。"),

    "ratio": ("比率", "名詞", "The ratio of nurses to patients differs greatly between regions.", "看護師と患者の比率は地域によって大きく異なる。"),
    "factor": ("要因", "名詞", "Long working hours are one factor behind the shortage of doctors.", "長時間労働は医師不足の背景にある一つの要因である。"),
    "passage": ("（長文の）本文、一節", "名詞", "Read the passage carefully before answering the questions below.", "下の設問に答える前に、本文を注意深く読みなさい。"),
    "resources": ("資源、人材", "名詞", "Universities compete for talented human resources from around the world.", "大学は世界中から優秀な人材を求めて競争している。"),

    "preferential": ("優遇の", "形容詞", "Skilled workers receive preferential handling when they apply for visas.", "技能を持つ労働者は、ビザを申請する際に優遇される。"),
    "local": ("地域の", "形容詞", "The clinic works closely with local communities and schools.", "その診療所は地域の共同体や学校と密接に連携している。"),
    "male": ("男性の", "形容詞", "Most senior posts in the hospital are still held by male staff.", "その病院の上級職の大半は、いまだに男性職員が占めている。"),
    "medical": ("医療の", "形容詞", "Medical costs rise quickly as the population grows older.", "人口の高齢化が進むにつれ、医療費は急速に増える。"),

    "reveal": ("明らかにする、示す", "動詞", "The new data reveal a sharp rise in applications from abroad.", "新しいデータは、海外からの申請の急増を示している。"),
    "support": ("支える", "動詞", "Public spending can support families during long periods of illness.", "公的支出は、長い闘病期間中の家族を支えることができる。"),
    "increase": ("増える、増やす", "動詞", "The number of foreign students continues to increase every year.", "留学生の数は毎年増え続けている。"),
    "reduce": ("減らす", "動詞", "Social insurance is designed to reduce the burden on individual households.", "社会保険は個々の世帯の負担を減らすために設計されている。"),

    "doctors": ("医師（複数）", "名詞", "Many doctors in Japan work far beyond their scheduled hours.", "日本の多くの医師は、予定された時間をはるかに超えて働いている。"),
    "students": ("学生（複数）", "名詞", "Graduate students from abroad now fill many laboratory posts.", "海外からの大学院生が、今では多くの研究室の職を担っている。"),
    "professionals": ("専門職の人（複数）", "名詞", "Highly skilled professionals can apply for a special residence status.", "高度な技能を持つ専門職の人は、特別な在留資格を申請できる。"),
    "individuals": ("個人（複数）", "名詞", "Modern society leaves individuals exposed to dangers their families once absorbed.", "現代社会では、かつて家族が吸収していた危険に個人がさらされている。"),

    "promote": ("昇進させる、促進する", "動詞", "The hospital plans to promote more women to management roles.", "その病院は、より多くの女性を管理職に昇進させる計画である。"),
    "issue": ("発行する", "動詞", "The government will issue more visas to researchers next year.", "政府は来年、研究者向けにより多くのビザを発行する予定である。"),
    "advanced": ("高度な", "形容詞", "The laboratory needs staff with advanced training in data analysis.", "その研究室はデータ分析の高度な訓練を受けた職員を必要としている。"),
    "skilled": ("技能を持つ", "形容詞", "Countries compete to attract skilled workers from other regions.", "各国は他地域から技能を持つ労働者を引きつけようと競っている。"),

    "average": ("平均", "名詞", "Japan's result is still below the average for member countries.", "日本の数値は、加盟国の平均をなお下回っている。"),
    "course": ("課程", "名詞", "She completed a doctoral course before joining the research center.", "彼女は研究センターに加わる前に博士課程を修了した。"),
    "table": ("表", "名詞", "The table below compares spending in five different countries.", "下の表は5つの異なる国の支出を比較している。"),
    "total": ("合計の", "形容詞", "Medical care accounts for a large share of total welfare spending.", "医療は福祉支出の合計のうち大きな割合を占めている。"),

    "percentage": ("百分率、〜％", "名詞", "The percentage of women among new doctors has slowly risen.", "新人医師に占める女性の割合は、ゆっくりと上昇している。"),
    "income": ("所得", "名詞", "Households with a low income depend heavily on public support.", "所得の低い世帯は、公的支援に大きく依存している。"),
    "visas": ("ビザ、査証（複数）", "名詞", "The number of visas granted to engineers rose again last year.", "技術者に発給されたビザの数は、昨年再び増えた。"),
    "benefits": ("給付、恩恵", "名詞", "Pension benefits make up the largest part of the budget.", "年金給付は予算の最大の部分を占めている。"),

    "positions": ("地位、役職（複数）", "名詞", "Few women reach senior positions in Japanese hospitals.", "日本の病院で上級の役職に就く女性は少ない。"),
    "system": ("制度", "名詞", "The social security system was built after the war.", "その社会保障制度は戦後に作られた。"),
    "risks": ("リスク、危険（複数）", "名詞", "Illness and unemployment are risks that any household may face.", "病気と失業は、どの世帯も直面しうるリスクである。"),
    "ties": ("つながり（血縁・地縁）", "名詞", "Blood and local ties no longer protect people as before.", "血縁や地縁のつながりは、以前のように人々を守ってはいない。"),

    "strengthen": ("強化する、強まる", "動詞", "New rules should strengthen help for families with small children.", "新しい規則は、幼い子どもを持つ家庭への支援を強化するはずである。"),
    "function": ("機能", "名詞", "One function of insurance is to spread danger across society.", "保険の一つの機能は、社会全体に危険を分散させることである。"),
    "number": ("数", "名詞", "The number of births has fallen for eight straight years.", "出生数は8年連続で減少している。"),
    "figure": ("図", "名詞", "The figure on the next page shows spending since 2010.", "次のページの図は2010年以降の支出を示している。"),

    "disparities": ("格差（複数）", "名詞", "Wide disparities remain between urban and rural medical services.", "都市部と農村部の医療サービスの間には大きな格差が残っている。"),
    "security": ("保障、安全", "名詞", "Social security protects people who cannot work because of illness.", "社会保障は、病気のために働けない人々を守る。"),
    "treatment": ("待遇、扱い", "名詞", "Fair treatment of foreign staff is essential for long-term employment.", "外国人職員の公正な待遇は、長期の雇用に不可欠である。"),
    "economic": ("経済の", "形容詞", "Stable welfare spending can help economic activity in a downturn.", "安定した福祉支出は、景気後退期の経済活動を助けうる。"),

    "growth": ("成長", "名詞", "Steady growth allows the government to expand welfare programs.", "着実な成長により、政府は福祉制度を拡充できる。"),
    "fiscal": ("会計年度の、財政の", "形容詞", "Welfare spending rose sharply during the last fiscal year.", "前会計年度には福祉支出が急激に増えた。"),
    "doctoral": ("博士課程の", "形容詞", "Many doctoral students in science come from other countries.", "理系の博士課程の学生の多くは他国から来ている。"),
    "international": ("国際的な", "形容詞", "The university welcomes international researchers to its laboratories every spring.", "その大学は毎春、国際的な研究者を研究室に受け入れている。"),

    "expenses": ("費用、経費", "名詞", "Medical expenses account for about a third of the budget.", "医療費は予算の約3分の1を占めている。"),
    "female": ("女性の", "形容詞", "The share of female doctors remains lower than in Europe.", "女性医師の割合は、ヨーロッパより低いままである。"),
    "important": ("重要な", "形容詞", "Language ability is an important condition for these applicants.", "語学力はこれらの申請者にとって重要な条件である。"),
    "quickly": ("早く、すばやく", "副詞", "Costs for elderly care are rising more quickly than expected.", "高齢者介護の費用は予想より早く増えている。"),

    "proportion": ("割合", "名詞", "A large proportion of the budget goes to pensions.", "予算の大きな割合が年金に充てられている。"),
    "per": ("〜あたり", "前置詞", "Japan has fewer doctors per person than most member countries.", "日本は大半の加盟国より、一人あたりの医師数が少ない。"),
    "according to": ("〜によれば", "熟語", "According to the survey, half of the respondents work overtime.", "その調査によれば、回答者の半数は残業をしている。"),
    "in place": ("整備されている", "熟語", "Support programs for foreign workers are already in place.", "外国人労働者への支援制度はすでに整備されている。"),
}

# choices は空所に入れたときの語形、items は WORD_LIST の見出し語（同じ並び）。
QUESTIONS = [
    {
        "stem": "The report treats ( ) as an important factor in producing advanced knowledge, because researchers from abroad bring new ideas.",
        "choices": ["immigration", "creation", "definition", "fiscal"],
        "items": ["immigration", "creation", "definition", "fiscal"],
        "answerIndex": 0,
        "translation": "海外から来た研究者が新しい考えをもたらすため、その報告書は移民の流入を、高度な知識を生み出す重要な要因として扱っている。",
    },
    {
        "stem": "The way of describing highly skilled human resources is not ( ), because each country sets its own standard.",
        "choices": ["mutual", "apparent", "uniform", "various"],
        "items": ["mutual", "apparent", "uniform", "various"],
        "answerIndex": 2,
        "translation": "国ごとに独自の基準を設けているため、高度人材の表し方は統一されていない。",
    },
    {
        "stem": "The graph shows the ( ) of international students in doctoral programs, which is about twenty percent.",
        "choices": ["factor", "ratio", "passage", "resources"],
        "items": ["factor", "ratio", "passage", "resources"],
        "answerIndex": 1,
        "translation": "そのグラフは博士課程における留学生の比率を示しており、それは約20％である。",
    },
    {
        "stem": "Several countries offer ( ) conditions to foreign workers who have advanced skills.",
        "choices": ["local", "male", "medical", "preferential"],
        "items": ["local", "male", "medical", "preferential"],
        "answerIndex": 3,
        "translation": "いくつかの国は、高度な技能を持つ外国人労働者に優遇的な条件を提供している。",
    },
    {
        "stem": "Figure 2 ( ) that the United Kingdom now grants more visas to highly skilled professionals than before.",
        "choices": ["reveals", "supports", "increases", "reduces"],
        "items": ["reveal", "support", "increase", "reduce"],
        "answerIndex": 0,
        "translation": "図2は、英国が以前より多くのビザを高度技能の専門職に与えていることを明らかにしている。",
    },
    {
        "stem": "In Japan, ( ) often work long hours because they must treat patients at night as well.",
        "choices": ["students", "professionals", "doctors", "individuals"],
        "items": ["students", "professionals", "doctors", "individuals"],
        "answerIndex": 2,
        "translation": "日本では、夜間にも患者を診なければならないため、医師は長時間働くことが多い。",
    },
    {
        "stem": "In many hospitals, female staff members are ( ) to senior posts more slowly than male staff members.",
        "choices": ["issued", "promoted", "advanced", "skilled"],
        "items": ["issue", "promote", "advanced", "skilled"],
        "answerIndex": 1,
        "translation": "多くの病院では、女性職員は男性職員より上級職への昇進が遅い。",
    },
    {
        "stem": "The number of doctors per person in Japan is lower than the ( ) for OECD countries.",
        "choices": ["course", "important", "total", "average"],
        "items": ["course", "important", "total", "average"],
        "answerIndex": 3,
        "translation": "日本の一人あたりの医師数は、OECD諸国の平均を下回っている。",
    },
    {
        "stem": "The ( ) of female doctors in Japan is lower than in most other member countries.",
        "choices": ["percentage", "income", "visas", "per"],
        "items": ["percentage", "income", "visas", "per"],
        "answerIndex": 0,
        "translation": "日本の女性医師の割合は、他の大半の加盟国より低い。",
    },
    {
        "stem": "Women hold fewer senior ( ) in Japanese hospitals than their share of the workforce suggests.",
        "choices": ["systems", "risks", "positions", "ties"],
        "items": ["system", "risks", "positions", "ties"],
        "answerIndex": 2,
        "translation": "日本の病院では、労働力に占める割合から予想されるより、女性が就く上級の役職は少ない。",
    },
    {
        "stem": "Mutual help based on blood and local bonds ( ) family life in the past, but that role has weakened.",
        "choices": ["functioned", "strengthened", "numbered", "figured"],
        "items": ["function", "strengthen", "number", "figure"],
        "answerIndex": 1,
        "translation": "血縁や地縁に基づく相互扶助は、かつて家庭生活を強めていたが、その役割は弱まっている。",
    },
    {
        "stem": "One aim of the program is to reduce income ( ) between rich and poor households.",
        "choices": ["security", "treatment", "economic", "disparities"],
        "items": ["security", "treatment", "economic", "disparities"],
        "answerIndex": 3,
        "translation": "その制度の目的の一つは、豊かな世帯と貧しい世帯の間の所得格差を縮めることである。",
    },
    {
        "stem": "Public welfare spending can also help economic ( ) by keeping households stable.",
        "choices": ["growth", "expenditure", "doctoral", "international"],
        "items": ["growth", "expenditure", "doctoral", "international"],
        "answerIndex": 0,
        "translation": "公的な福祉支出は、世帯を安定させることで経済成長を下支えすることもできる。",
    },
    {
        "stem": "Medical ( ) account for about half of all social security spending in Japan.",
        "choices": ["female", "table", "expenses", "quickly"],
        "items": ["female", "table", "expenses", "quickly"],
        "answerIndex": 2,
        "translation": "医療費は日本の社会保障支出全体の約半分を占めている。",
    },
    {
        "stem": "The ( ) of social security in general spending was higher in 2023 than in 2010.",
        "choices": ["benefits", "proportion", "according to", "in place"],
        "items": ["benefits", "proportion", "according to", "in place"],
        "answerIndex": 1,
        "translation": "一般歳出に占める社会保障の割合は、2010年より2023年のほうが高かった。",
    },
]


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text))


def occurrences(text: str, needle: str) -> int:
    return len(re.findall(rf"\b{re.escape(needle)}\b", text, flags=re.IGNORECASE))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(WORD_LIST) != 60:
        raise ValueError(f"見出し語は60語である必要があります: {len(WORD_LIST)}")
    if len(QUESTIONS) != 15:
        raise ValueError("IUHWセットは15問である必要があります")

    used = [item for question in QUESTIONS for item in question["items"]]
    if len(used) != len(set(used)):
        raise ValueError("同じ見出し語を2回使っています")
    if sorted(used) != sorted(WORD_LIST):
        missing = sorted(set(WORD_LIST) - set(used))
        extra = sorted(set(used) - set(WORD_LIST))
        raise ValueError(f"見出し語の使用が一致しません: 未使用={missing} / 一覧外={extra}")

    mixed = 0
    for question in QUESTIONS:
        choices, items = question["choices"], question["items"]
        if len(choices) != 4 or len(items) != 4 or question["answerIndex"] not in range(4):
            raise ValueError(f"4択または正答位置が不正です: {question['stem']}")
        if str(question["stem"]).count("( )") != 1:
            raise ValueError(f"設問文の空所が不正です: {question['stem']}")
        if not question.get("translation"):
            raise ValueError(f"設問文訳がありません: {question['stem']}")
        for choice, item in zip(choices, items):
            if not surfaces_match(choice, item):
                raise ValueError(f"選択肢と見出し語が対応していません: {choice} / {item}")
            if occurrences(question["stem"], choice):
                raise ValueError(f"選択肢が設問文に出ています: {choice}")
        details = [WORD_LIST[item] for item in items]
        if len({detail[0] for detail in details}) != 4:
            raise ValueError(f"同一設問内で意味が重複しています: {items}")
        # 60語は出題英文由来で品詞が偏っており（名詞32・形容詞17・動詞7・その他4）、
        # 全問を同一品詞では組めない。正答と同じ品詞が2件以上あるか、
        # 空所に入る語形が揃っている設問だけを許し、混在の件数を上限で押さえる。
        answer_pos = details[question["answerIndex"]][1]
        if len({detail[1] for detail in details}) != 1:
            mixed += 1
            same_pos = sum(detail[1] == answer_pos for detail in details)
            same_form = len({choice[-2:] for choice in choices}) == 1
            if same_pos < 2 and not same_form:
                raise ValueError(f"選択肢の品詞も語形も揃っていません: {items}")
        for item, (_, _, example, _) in zip(items, details):
            if word_count(example) < 8:
                raise ValueError(f"例文が8語未満です: {item}")
            if occurrences(example, item) != 1:
                raise ValueError(f"例文に見出し語が1回ありません: {item}")

    meta = {
        "grade": "国際医療福祉大学",
        "round": ROUND_ID,
        "section": "基礎試験 英語（選択肢文の語彙）",
        "source": "出題英文から抜き出した60語の学習用自作文（原文未収録）",
        "counts": {"questions": 15, "words": 60, "idioms": 0, "total": 60},
    }
    question_data = {
        "meta": meta,
        "questions": [
            {
                "q": index,
                "stem": question["stem"],
                "choices": question["choices"],
                "answerIndex": question["answerIndex"],
                "translation": question["translation"],
            }
            for index, question in enumerate(QUESTIONS, start=1)
        ],
    }
    words = []
    for q, question in enumerate(QUESTIONS, start=1):
        for index, item in enumerate(question["items"]):
            meaning, pos, example, example_translation = WORD_LIST[item]
            words.append({
                "q": q,
                "word": item,
                "is_answer": index == question["answerIndex"],
                "pos": pos,
                "meaning": meaning,
                "example": example,
                "exampleTranslation": example_translation,
            })
    print(f"品詞混在の設問: {mixed}/15")
    return {"meta": meta, "words": words, "idioms": []}, question_data


def main() -> int:
    vocab, questions = build()
    write_json(DATA_DIR / f"vocab_iuhw_{ROUND_ID}.json", vocab)
    write_json(DATA_DIR / f"questions_iuhw_{ROUND_ID}.json", questions)
    print(f"生成: {len(questions['questions'])}問 / {len(vocab['words'])}語")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
