"""英検2級 Chapter 3 模擬テスト第1回をQ1形式のJSONへ出力する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ROUND_ID = "mock-1"


QUESTIONS = [
    {
        "stem": "After the new airport opened, many nearby residents were upset. They said that they could no longer (   ) the noise of the airplanes.",
        "choices": ["flee", "require", "tolerate", "delay"],
        "answerIndex": 2,
        "translation": "新しい空港が開港すると、近隣の住民の多くは怒った。飛行機の騒音にもう耐えられないと言った。",
    },
    {
        "stem": "When she started art school, Maria's (   ) was to become a graphic designer. However, she ended up becoming a make-up artist.",
        "choices": ["intention", "introduction", "allowance", "investment"],
        "answerIndex": 0,
        "translation": "美術学校に入ったとき、マリアの意図はグラフィックデザイナーになることだった。しかし、結局はメイクアップアーティストになった。",
    },
    {
        "stem": "David entered the house and went up the stairs (   ) because he did not want to wake his sleeping family.",
        "choices": ["simply", "silently", "safely", "surely"],
        "answerIndex": 1,
        "translation": "デイビッドは眠っている家族を起こしたくなかったので、静かに階段を上って家に入った。",
    },
    {
        "stem": "To make a necklace, first (   ) the wire into a circle. Next, place the beads onto the wire. Finally, tie the two ends together.",
        "choices": ["heal", "bend", "cure", "elect"],
        "answerIndex": 1,
        "translation": "ネックレスを作るには、まず針金を曲げて輪にする。次にビーズを針金に通し、最後に両端を結ぶ。",
    },
    {
        "stem": "A: The data in this report doesn't look right. B: Are you (   ) that I didn't check it properly?",
        "choices": ["committing", "adjusting", "betting", "implying"],
        "answerIndex": 3,
        "translation": "A：この報告書のデータは正しく見えない。B：私がきちんと確認しなかったとほのめかしているの？",
    },
    {
        "stem": "Many teenagers experience a period when they question their (   ), but most people become more comfortable with themselves.",
        "choices": ["identity", "magnificence", "variety", "scenery"],
        "answerIndex": 0,
        "translation": "多くの10代の若者は自分のアイデンティティーに疑問を抱く時期を経験するが、ほとんどの人はやがて自分自身により安心できるようになる。",
    },
    {
        "stem": "The thief tried to (   ) his actions. However, the judge said that there was no excuse for what he had done.",
        "choices": ["justify", "restrict", "estimate", "reveal"],
        "answerIndex": 0,
        "translation": "その泥棒は自分の行動を正当化しようとした。しかし、裁判官は彼のしたことに弁解の余地はないと言った。",
    },
    {
        "stem": "It was quite an (   ) for Jessie to win the chess tournament because she just started learning how to play a month ago.",
        "choices": ["instrument", "achievement", "admission", "omission"],
        "answerIndex": 1,
        "translation": "ジェシーはチェスを習い始めてまだ1か月なので、チェス大会で優勝したことはかなりの偉業だった。",
    },
    {
        "stem": "A: Where's Alan? He's already 10 minutes late. I hope he's OK. B: Don't worry, he'll be here. He's almost never (   ).",
        "choices": ["absolute", "intelligent", "various", "punctual"],
        "answerIndex": 3,
        "translation": "A：アランはどこ？もう10分も遅れている。大丈夫だといいけど。B：心配しないで、すぐ来るよ。彼はほとんど時間を守らないことがないから。",
    },
    {
        "stem": "One of the actors became ill and was unable to work for a few months, so the producers of the film began looking for a (   ) for him.",
        "choices": ["replacement", "critic", "criminal", "detective"],
        "answerIndex": 0,
        "translation": "俳優の1人が病気になり数か月働けなくなったので、映画の製作者たちは彼の代役を探し始めた。",
    },
    {
        "stem": "Jill wants to be a nurse, but she knows it is impossible. She gets sick at the (   ) of blood.",
        "choices": ["feel", "sense", "sight", "area"],
        "answerIndex": 2,
        "translation": "ジルは看護師になりたいが、それは無理だと分かっている。血を見ると気分が悪くなるからだ。",
    },
    {
        "stem": "When Mike was shopping, he met his best friend from high school (   ). They decided to have coffee together and talk about the old days.",
        "choices": ["at large", "out of place", "by accident", "in question"],
        "answerIndex": 2,
        "translation": "マイクが買い物をしていると、高校時代の親友に偶然会った。2人は一緒にコーヒーを飲み、昔の日々について話すことにした。",
    },
    {
        "stem": "(   ) the damage caused by the storm, the school will be closed for two days.",
        "choices": ["in accordance with", "owing to", "made by", "compared with"],
        "answerIndex": 1,
        "translation": "嵐による被害のため、学校は2日間休校になる。",
    },
    {
        "stem": "Sandi was given a new position. She is now in (   ) of advertising and promotion.",
        "choices": ["schedule", "board", "payment", "charge"],
        "answerIndex": 3,
        "translation": "サンディは新しい役職を与えられた。現在は広告と販売促進を担当している。",
    },
    {
        "stem": "A: There's a lot I can tell you about the life of an artist, but (   ), it's difficult to make a living from art. B: I understand that. That's why I want to keep my job for now.",
        "choices": ["in fact", "in short", "at last", "on target"],
        "answerIndex": 1,
        "translation": "A：芸術家の生活について話せることはたくさんあるけれど、要するに、芸術で生計を立てるのは難しい。B：分かっているよ。だから今は仕事を続けたいんだ。",
    },
    {
        "stem": "Peggy's son reached to get the last piece of cake, so Peggy told him to be (   ) the other children.",
        "choices": ["careful of", "sufficient for", "considerate of", "pleased about"],
        "answerIndex": 2,
        "translation": "ペギーの息子が最後のケーキに手を伸ばしたので、ペギーは他の子どもたちに配慮するよう言った。",
    },
    {
        "stem": "Oliver checked the advertisements and (   ) several of the companies that were looking for engineers.",
        "choices": ["answered for", "applied to", "led to", "kept up"],
        "answerIndex": 1,
        "translation": "オリバーは広告を調べ、技術者を探していた会社のいくつかに応募した。",
    },
    {
        "stem": "A: I (   ) invited you to spend Christmas with my family if I'd known that you'd be alone. B: Thanks, but I prefer to spend Christmas alone.",
        "choices": ["have", "had", "will have", "would have"],
        "answerIndex": 3,
        "translation": "A：あなたが一人で過ごすと知っていたら、家族とクリスマスを過ごすよう誘ったのに。B：ありがとう。でもクリスマスは一人で過ごしたい。",
    },
    {
        "stem": "Students are not allowed to swim in the school pool (   ) they have a teacher with them.",
        "choices": ["whether", "without", "moreover", "unless"],
        "answerIndex": 3,
        "translation": "生徒は、教師が一緒でない限り、学校のプールで泳ぐことを許されていない。",
    },
    {
        "stem": "The woman at the garage sale said that she would sell the bedframe for $200, but Linda told her that she would pay (   ) $150 for it.",
        "choices": ["no more than", "nothing left for", "a little of", "not up to"],
        "answerIndex": 0,
        "translation": "ガレージセールの女性はベッドフレームを200ドルで売ると言ったが、リンダは150ドルしか払わないと言った。",
    },
]


DETAILS = {
    "flee": ("逃げる", "動詞", "The frightened dog tried to flee when the gate suddenly opened.", "おびえた犬は門が突然開くと逃げようとした。"),
    "require": ("必要とする、要求する", "動詞", "Some jobs require applicants to work late during busy seasons.", "忙しい時期には応募者に遅くまで働くことを求める仕事もある。"),
    "tolerate": ("我慢する、許容する", "動詞", "The hotel does not tolerate smoking anywhere inside the building.", "そのホテルは建物内のどこでも喫煙を許容していない。"),
    "delay": ("遅らせる、延期する", "動詞", "Heavy snow may delay the morning train by several hours.", "大雪によって朝の列車が数時間遅れるかもしれない。"),
    "intention": ("意図、意向", "名詞", "My original intention was to study medicine at university.", "私の当初の意図は大学で医学を学ぶことだった。"),
    "introduction": ("紹介、導入", "名詞", "The speaker gave a brief introduction before explaining the new plan.", "講演者は新しい計画を説明する前に簡単な紹介をした。"),
    "allowance": ("小遣い、手当", "名詞", "Mika saves part of her monthly allowance for books and music.", "ミカは毎月の小遣いの一部を本と音楽のために貯めている。"),
    "investment": ("投資", "名詞", "The company made a large investment in solar energy last year.", "その会社は昨年、太陽エネルギーに大きな投資をした。"),
    "simply": ("単純に、ただ", "副詞", "The answer is not simply a matter of choosing the cheapest option.", "その答えは単に最も安い選択肢を選ぶだけの問題ではない。"),
    "silently": ("静かに、黙って", "副詞", "The audience listened silently while the musician played the final song.", "音楽家が最後の曲を演奏する間、聴衆は静かに聞いた。"),
    "safely": ("安全に", "副詞", "Please place the glass safely on the shelf above the sink.", "流しの上の棚にグラスを安全に置いてください。"),
    "surely": ("確かに、きっと", "副詞", "If you keep practicing, you will surely improve before the contest.", "練習を続ければ、コンテスト前にきっと上達する。"),
    "heal": ("治る、治す", "動詞", "The nurse said that the small cut would heal within a week.", "看護師はその小さな切り傷は1週間以内に治ると言った。"),
    "bend": ("曲げる", "動詞", "Bend the paper carefully before placing it inside the envelope.", "封筒の中に入れる前に、その紙を注意深く折り曲げてください。"),
    "cure": ("治療する、治す", "動詞", "Scientists are searching for a medicine that can cure the disease.", "科学者たちはその病気を治せる薬を探している。"),
    "elect": ("選出する", "動詞", "The club members will elect a new leader at the next meeting.", "クラブのメンバーは次の会合で新しいリーダーを選出する。"),
    "committing": ("犯す、委ねる", "動詞", "The witness denied committing the crime described in the newspaper.", "その証人は新聞に書かれた犯罪を犯したことを否定した。"),
    "adjusting": ("調整する", "動詞", "The technician is adjusting the lights before the evening performance begins.", "技術者は夜の公演が始まる前に照明を調整している。"),
    "betting": ("賭ける", "動詞", "Betting large amounts of money can cause serious problems for families.", "大金を賭けることは家族に深刻な問題を引き起こすことがある。"),
    "implying": ("ほのめかす、暗示する", "動詞", "Are you implying that the manager knew about the mistake earlier?", "あなたはマネージャーがもっと早くそのミスを知っていたとほのめかしているのですか。"),
    "identity": ("アイデンティティー、身元", "名詞", "The police asked the passenger to show proof of her identity.", "警察はその乗客に身元を証明するものを見せるよう求めた。"),
    "magnificence": ("壮大さ、華麗さ", "名詞", "Visitors were impressed by the magnificence of the ancient palace.", "訪問者たちは古代の宮殿の壮大さに感銘を受けた。"),
    "variety": ("多様性、種類", "名詞", "The market offers a wide variety of fresh vegetables every morning.", "その市場では毎朝、さまざまな新鮮な野菜を販売している。"),
    "scenery": ("景色、風景", "名詞", "The mountain scenery became more beautiful as the train climbed higher.", "列車が高く登るにつれて山の景色はさらに美しくなった。"),
    "justify": ("正当化する", "動詞", "The manager could not justify spending so much money on decorations.", "マネージャーは装飾にそれほど多くのお金を使うことを正当化できなかった。"),
    "restrict": ("制限する", "動詞", "The new rules restrict visitors from entering the laboratory alone.", "新しい規則は訪問者が一人で研究室に入ることを制限している。"),
    "estimate": ("見積もる、推定する", "動詞", "Experts estimate that the repairs will take nearly three months.", "専門家は修理にほぼ3か月かかると見積もっている。"),
    "reveal": ("明らかにする、暴露する", "動詞", "The investigation may reveal why the machine stopped without warning.", "調査によって、なぜ機械が予告なく止まったのかが明らかになるかもしれない。"),
    "instrument": ("器具、楽器", "名詞", "The museum displays a musical instrument from the nineteenth century.", "その博物館は19世紀の楽器を展示している。"),
    "achievement": ("業績、達成", "名詞", "Winning the national prize was a major achievement for the young scientist.", "全国賞を受賞したことは、その若い科学者にとって大きな業績だった。"),
    "admission": ("入場、入学許可、認めること", "名詞", "Admission to the science museum is free for children under twelve.", "科学博物館への入場は12歳未満の子どもは無料だ。"),
    "omission": ("省略、脱落", "名詞", "The omission of one important detail changed the meaning of the report.", "重要な詳細を1つ省略したことで報告書の意味が変わった。"),
    "absolute": ("絶対的な、完全な", "形容詞", "The judge said that the evidence did not provide absolute proof.", "裁判官はその証拠が絶対的な証明にはならないと言った。"),
    "intelligent": ("知的な、賢い", "形容詞", "The intelligent student found a practical solution to the difficult problem.", "その知的な生徒は難しい問題への実用的な解決策を見つけた。"),
    "various": ("さまざまな", "形容詞", "The library provides various materials for students conducting research.", "その図書館は研究を行う生徒にさまざまな資料を提供している。"),
    "punctual": ("時間を守る", "形容詞", "Our new assistant is always punctual and arrives before the office opens.", "新しいアシスタントはいつも時間を守り、事務所が開く前に到着する。"),
    "replacement": ("交換品、代わりの人", "名詞", "The store sent a replacement after the original product arrived damaged.", "元の商品が壊れた状態で届いた後、店は交換品を送った。"),
    "critic": ("批評家、批判する人", "名詞", "The film received praise from one critic but complaints from another.", "その映画は1人の批評家から称賛されたが、別の批評家からは苦情を受けた。"),
    "criminal": ("犯罪者、犯罪の", "名詞", "The police arrested the criminal near the station late at night.", "警察は深夜に駅の近くでその犯罪者を逮捕した。"),
    "detective": ("刑事、探偵", "名詞", "The detective interviewed every witness before writing the final report.", "その刑事は最終報告書を書く前にすべての目撃者に聞き取りをした。"),
    "feel": ("感覚、感じること", "名詞", "The soft fabric has a pleasant feel against the skin.", "その柔らかな布地は肌に心地よい感触がある。"),
    "sense": ("感覚、意味", "名詞", "She had a strong sense that someone was waiting outside.", "彼女は誰かが外で待っているという強い感覚があった。"),
    "sight": ("見ること、光景", "名詞", "The sight of the empty classroom made the teacher feel lonely.", "空っぽの教室を見て、教師は寂しい気持ちになった。"),
    "area": ("地域、範囲", "名詞", "This area becomes crowded whenever the summer festival takes place.", "この地域は夏祭りが開かれるたびに混雑する。"),
    "at large": ("逃走中で、自由に", "副詞句", "The suspect is still at large despite the police search yesterday.", "警察が昨日捜索したにもかかわらず、容疑者はまだ逃走中だ。"),
    "out of place": ("場違いな、所定の場所から外れて", "形容詞句", "The bright red chair looked out of place in the quiet reading room.", "その鮮やかな赤い椅子は静かな閲覧室では場違いに見えた。"),
    "by accident": ("偶然に、誤って", "副詞句", "I found the old photograph by accident while cleaning the attic.", "屋根裏を掃除しているとき、偶然その古い写真を見つけた。"),
    "in question": ("問題になっている、当該の", "形容詞句", "The document in question was signed by the director last Friday.", "問題の文書には先週の金曜日に部長が署名した。"),
    "in accordance with": ("〜に従って、〜に一致して", "前置詞句", "The staff acted in accordance with the safety rules during the experiment.", "実験中、職員は安全規則に従って行動した。"),
    "owing to": ("〜が原因で、〜のために", "前置詞句", "The flight was canceled owing to strong winds near the airport.", "空港付近の強風が原因で、その便は欠航になった。"),
    "made by": ("〜によって作られた", "受動表現", "This traditional cake was made by local cooks for the festival.", "この伝統的なケーキは祭りのために地元の料理人が作った。"),
    "compared with": ("〜と比べて", "前置詞句", "Compared with last year, this winter has been unusually warm.", "昨年と比べると、今年の冬は異例に暖かい。"),
    "schedule": ("予定、スケジュール", "名詞", "The manager changed the schedule because several meetings were canceled.", "いくつかの会議が中止になったので、マネージャーは予定を変更した。"),
    "board": ("板、掲示板、委員会", "名詞", "The school board discussed the budget for the new sports center.", "教育委員会は新しいスポーツセンターの予算について話し合った。"),
    "payment": ("支払い", "名詞", "The online store confirmed my payment before sending the package.", "オンラインストアは荷物を送る前に私の支払いを確認した。"),
    "charge": ("担当、料金、責任", "名詞", "The nurse is in charge of organizing the emergency supplies.", "その看護師は救急用品の整理を担当している。"),
    "in fact": ("実際には、実は", "副詞句", "The task looked easy, but in fact it required careful planning.", "その作業は簡単に見えたが、実際には慎重な計画が必要だった。"),
    "in short": ("要するに、簡潔に言えば", "副詞句", "In short, the committee needs more time before making a decision.", "要するに、委員会は決定を下す前にもっと時間が必要だ。"),
    "at last": ("ついに、とうとう", "副詞句", "At last, the repair team found the source of the leak.", "ついに、修理チームは水漏れの原因を見つけた。"),
    "on target": ("目標どおりで、的確な", "形容詞句", "The campaign is on target to reach its fundraising goal this month.", "そのキャンペーンは今月、募金目標を達成する見込みだ。"),
    "careful of": ("〜に注意して、〜を大切にして", "形容詞句", "Please be careful of the wet steps near the entrance.", "入口近くの濡れた階段に注意してください。"),
    "sufficient for": ("〜に十分な", "形容詞句", "The amount of water should be sufficient for the entire hike.", "その水の量はハイキング全体に十分なはずだ。"),
    "considerate of": ("〜に配慮した", "形容詞句", "The student was considerate of others and offered his seat to an elderly passenger.", "その生徒は他人に配慮し、高齢の乗客に席を譲った。"),
    "pleased about": ("〜を喜んで、〜に満足して", "形容詞句", "The coach was pleased about the team's progress during the season.", "監督はシーズン中のチームの進歩を喜んでいた。"),
    "answered for": ("〜の責任を負った、〜を保証した", "動詞句", "The manager answered for the mistake when the customer requested an explanation.", "客が説明を求めたとき、マネージャーはそのミスの責任を負った。"),
    "applied to": ("〜に応募した、〜に適用された", "動詞句", "Oliver applied to several companies after completing his engineering course.", "オリバーは工学課程を修了した後、いくつかの会社に応募した。"),
    "led to": ("〜につながった、〜を引き起こした", "動詞句", "The careful experiment led to an important discovery in the laboratory.", "その慎重な実験は研究室での重要な発見につながった。"),
    "kept up": ("〜についていった、〜を維持した", "動詞句", "The runner kept up with the leader until the final turn.", "その走者は最後の曲がり角まで先頭の走者についていった。"),
    "have": ("持っている、〜する", "助動詞", "I have enough time to finish the assignment before dinner tonight.", "私は今夜の夕食前に課題を終える時間が十分にある。"),
    "had": ("持っていた、〜した", "助動詞", "She had already left the station when I called her phone.", "私が彼女の携帯に電話したとき、彼女はすでに駅を出ていた。"),
    "will have": ("〜するだろう、〜を持つことになる", "助動詞句", "By next spring, the town will have a new public library.", "来年の春までに、その町には新しい公共図書館ができるだろう。"),
    "would have": ("〜しただろう、〜だっただろう", "助動詞句", "Without your advice, I would have made the same serious mistake.", "あなたの助言がなければ、私は同じ重大なミスをしただろう。"),
    "whether": ("〜かどうか", "接続詞", "We must decide whether the event should be moved indoors.", "私たちはその行事を屋内へ移すべきかどうか決めなければならない。"),
    "without": ("〜なしに、〜を持たずに", "前置詞", "The hikers left without checking the latest weather report.", "ハイカーたちは最新の天気予報を確認せずに出発した。"),
    "moreover": ("そのうえ、さらに", "副詞", "The apartment is affordable; moreover, it is close to the station.", "そのアパートは手頃なうえ、駅にも近い。"),
    "unless": ("〜でない限り", "接続詞", "You cannot enter the laboratory unless a staff member accompanies you.", "職員が同行しない限り、研究室に入ることはできない。"),
    "no more than": ("たった〜、〜しか", "数量表現", "The repair will cost no more than one hundred dollars.", "その修理には100ドルしかかからないだろう。"),
    "nothing left for": ("〜に残されたものが何もない", "表現", "After the guests ate, there was nothing left for the children.", "客が食べた後、子どもたちのために残されたものは何もなかった。"),
    "a little of": ("少しの〜", "数量表現", "Add a little of the sauce before tasting the noodles again.", "麺をもう一度味見する前に、ソースを少し加えてください。"),
    "not up to": ("〜に達しない、〜の水準ではない", "形容詞句", "The first draft was not up to the standard required by the editor.", "最初の草稿は編集者が求める水準に達していなかった。"),
}


CORE_IMAGES = {
    "at large": {"chain": [{"term": "at", "gloss": "ある状態にあって"}, {"term": "large", "gloss": "広い範囲に及んで"}, {"gloss": "拘束されず自由に、または逃走中で"}]},
    "out of place": {"chain": [{"term": "out", "gloss": "外へ出て"}, {"term": "of", "gloss": "〜から"}, {"term": "place", "gloss": "所定の場所"}, {"gloss": "場違いな、所定の場所から外れて"}]},
    "by accident": {"chain": [{"term": "by", "gloss": "〜によって"}, {"term": "accident", "gloss": "偶然の出来事"}, {"gloss": "偶然に、意図せず"}]},
    "in question": {"chain": [{"term": "in", "gloss": "範囲の中で"}, {"term": "question", "gloss": "問題、疑問"}, {"gloss": "問題になっている、当該の"}]},
    "in accordance with": {"chain": [{"term": "accordance", "gloss": "一致、調和"}, {"term": "with", "gloss": "〜とともに"}, {"gloss": "〜に従って、〜に一致して"}]},
    "owing to": {"chain": [{"term": "owing", "gloss": "負っている"}, {"term": "to", "gloss": "〜に対して"}, {"gloss": "〜が原因で"}]},
    "made by": {"chain": [{"term": "made", "gloss": "作られた"}, {"term": "by", "gloss": "行為者によって"}, {"gloss": "〜によって作られた"}]},
    "compared with": {"chain": [{"term": "compared", "gloss": "比べて"}, {"term": "with", "gloss": "〜と並べて"}, {"gloss": "〜と比べて"}]},
    "in fact": {"chain": [{"term": "in", "gloss": "範囲の中で"}, {"term": "fact", "gloss": "事実"}, {"gloss": "実際には、実は"}]},
    "in short": {"chain": [{"term": "in", "gloss": "範囲を絞って"}, {"term": "short", "gloss": "短く"}, {"gloss": "要するに、簡潔に言えば"}]},
    "at last": {"chain": [{"term": "at", "gloss": "ある時点に達して"}, {"term": "last", "gloss": "最後"}, {"gloss": "ついに、とうとう"}]},
    "on target": {"chain": [{"term": "on", "gloss": "対象に重なって"}, {"term": "target", "gloss": "目標"}, {"gloss": "目標どおりで、的確な"}]},
    "careful of": {"chain": [{"term": "careful", "gloss": "注意深い"}, {"term": "of", "gloss": "対象について"}, {"gloss": "〜に注意して"}]},
    "sufficient for": {"chain": [{"term": "sufficient", "gloss": "十分な"}, {"term": "for", "gloss": "対象に対して"}, {"gloss": "〜に十分な"}]},
    "considerate of": {"chain": [{"term": "considerate", "gloss": "思いやりのある"}, {"term": "of", "gloss": "対象について"}, {"gloss": "〜に配慮した"}]},
    "pleased about": {"chain": [{"term": "pleased", "gloss": "喜んだ、満足した"}, {"term": "about", "gloss": "対象について"}, {"gloss": "〜を喜んで、〜に満足して"}]},
    "answered for": {"chain": [{"term": "answered", "gloss": "答えた"}, {"term": "for", "gloss": "対象を引き受けて"}, {"gloss": "〜の責任を負った"}]},
    "applied to": {"chain": [{"term": "applied", "gloss": "申し込んだ、当てはめた"}, {"term": "to", "gloss": "対象へ向けて"}, {"gloss": "〜に応募した"}]},
    "led to": {"chain": [{"term": "led", "gloss": "導いた"}, {"term": "to", "gloss": "〜へ向かって"}, {"gloss": "〜につながった"}]},
    "kept up": {"particle": "up", "particleSense": "raise", "chain": [{"term": "keep", "gloss": "保つ"}, {"term": "up", "gloss": "高い水準へ"}, {"gloss": "同じ水準を保ってついていく"}]},
    "will have": {"chain": [{"term": "will", "gloss": "未来を示して"}, {"term": "have", "gloss": "持つ、経験する"}, {"gloss": "将来〜するだろう"}]},
    "would have": {"chain": [{"term": "would", "gloss": "仮定の結果を示して"}, {"term": "have", "gloss": "持つ、経験する"}, {"gloss": "実際には起きなかったことを仮に述べる"}]},
    "no more than": {"chain": [{"term": "no", "gloss": "ない"}, {"term": "more", "gloss": "それ以上"}, {"term": "than", "gloss": "比較して"}, {"gloss": "〜を超えない、たった〜"}]},
    "nothing left for": {"chain": [{"term": "nothing", "gloss": "何もない"}, {"term": "left", "gloss": "残された"}, {"term": "for", "gloss": "対象のために"}, {"gloss": "〜のために残されたものが何もない"}]},
    "a little of": {"chain": [{"term": "little", "gloss": "少量"}, {"term": "of", "gloss": "全体の中から"}, {"gloss": "少しの〜"}]},
    "not up to": {"chain": [{"term": "not", "gloss": "〜でない"}, {"term": "up", "gloss": "基準まで上がって"}, {"term": "to", "gloss": "対象の水準へ"}, {"gloss": "〜に達しない、〜の水準ではない"}]},
}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[dict, dict]:
    if len(QUESTIONS) != 20:
        raise ValueError("2級模試第1回は20問である必要があります")
    choices = [choice for question in QUESTIONS for choice in question["choices"]]
    if len(choices) != 80 or len(choices) != len(set(choices)):
        raise ValueError("選択肢は重複しない80件である必要があります")
    missing = sorted(set(choices) - set(DETAILS))
    if missing:
        raise ValueError(f"語句情報がありません: {missing}")
    idioms = {choice for choice in choices if " " in choice}
    if idioms != set(CORE_IMAGES):
        raise ValueError(f"核心イメージの定義が一致しません: {sorted(idioms ^ set(CORE_IMAGES))}")

    meta = {
        "grade": "英検2級",
        "round": ROUND_ID,
        "section": "Reading 大問1（語句空所補充）",
        "source": "ユーザー提供のChapter 3 模擬テスト第1回原稿を基に構造化。訳・例文・語句情報は学習用に作成",
        "counts": {"questions": 20, "words": 54, "idioms": 26, "total": 80},
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
    if (len(words), len(idiom_items)) != (54, 26):
        raise ValueError(f"語句数が想定と違います: words={len(words)}, idioms={len(idiom_items)}")
    return {"meta": meta, "words": words, "idioms": idiom_items}, question_data


def main() -> None:
    vocab, questions = build()
    write_json(DATA_DIR / "vocab_2_mock-1.json", vocab)
    write_json(DATA_DIR / "questions_2_mock-1.json", questions)
    print("eiken2 mock-1: 20 questions / 80 items (54 words, 26 idioms)")


if __name__ == "__main__":
    main()
