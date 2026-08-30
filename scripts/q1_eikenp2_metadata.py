"""英検準2級Q1の共通メタデータと暗記カード用例文を適用する。"""

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
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2026-1-1ji-p2kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202601Fp2kyu.pdf",
    },
    "2025-3": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2025-3-1ji-p2kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202503Fp2kyu.pdf",
    },
    "2025-2": {
        "problem": "https://www.eiken.or.jp/eiken/exam/kakomon/2025-2-1ji-p2kyu.pdf",
        "answer": "https://www.eiken.or.jp/eiken/result/pdf/202502Fp2kyu.pdf",
    },
}


# 公式問題の設問・選択肢・正答・安定IDは変更せず、暗記カードの例文だけを補正する。
# 1級・2級と同じく、8語以上で見出し語句を1回含む例文に統一する。
EXAMPLE_OVERRIDES = {
    "2025-2": {
        "editor": (
            "After years of reporting, Angela became the editor of her local newspaper.",
            "数年間記者を務めた後、アンジェラは地元新聞の編集者になりました。",
        ),
        "astronaut": (
            "The young astronaut trained for months before beginning the difficult space mission.",
            "その若い宇宙飛行士は、困難な宇宙任務を始める前に何か月も訓練しました。",
        ),
        "figures": (
            "The financial report includes important figures from the company's sales last year.",
            "その財務報告書には、昨年の会社の売上に関する重要な数字が含まれています。",
        ),
        "characters": (
            "The author created several memorable characters for her new children's novel.",
            "その作家は新しい児童小説のために、印象に残る登場人物を何人も作りました。",
        ),
        "puzzles": (
            "My grandfather enjoys solving difficult puzzles with his grandchildren on weekends.",
            "私の祖父は週末に、孫たちと難しいパズルを解くのを楽しみます。",
        ),
        "explosions": (
            "The firefighters heard several loud explosions near the factory during the night.",
            "消防士たちは夜間、工場の近くで大きな爆発音をいくつも聞きました。",
        ),
        "participants": (
            "All participants received a certificate after completing the weekend training program.",
            "参加者全員が週末の研修プログラムを終えた後、修了証を受け取りました。",
        ),
        "forecasts": (
            "The latest weather forecasts predict heavy rain across the region tomorrow.",
            "最新の天気予報では、明日その地域全体で大雨になると予測されています。",
        ),
        "unfortunately": (
            "Unfortunately, the train was delayed because a tree blocked the railway.",
            "残念ながら、木が線路をふさいだため、列車は遅れました。",
        ),
        "awfully": (
            "The children were awfully quiet while their parents prepared dinner downstairs.",
            "両親が階下で夕食を準備している間、子どもたちはひどく静かでした。",
        ),
        "bravely": (
            "The captain bravely entered the burning building to rescue the trapped child.",
            "船長は閉じ込められた子どもを救うため、勇敢に燃えている建物へ入りました。",
        ),
        "hardly": (
            "I could hardly hear the announcement because the station was extremely crowded.",
            "駅がとても混雑していたため、私はそのアナウンスをほとんど聞き取れませんでした。",
        ),
        "bowls": (
            "Please place the clean bowls on the table before the guests arrive.",
            "お客さまが到着する前に、きれいなボウルをテーブルに置いてください。",
        ),
        "ropes": (
            "The climbers checked their ropes carefully before starting up the steep mountain.",
            "登山者たちは険しい山を登り始める前に、ロープを注意深く確認しました。",
        ),
        "logs": (
            "We carried several heavy logs into the cabin before the winter storm arrived.",
            "私たちは冬の嵐が来る前に、重い丸太を何本も小屋へ運びました。",
        ),
        "rays": (
            "The warm rays of the morning sun entered through the bedroom window.",
            "朝の太陽の暖かな光線が寝室の窓から差し込みました。",
        ),
        "curly": (
            "The little girl has curly hair that reaches her shoulders when it is dry.",
            "その小さな女の子は、乾くと肩まで届く巻き毛をしています。",
        ),
        "steady": (
            "He found a steady job after searching for work throughout the summer.",
            "彼は夏の間ずっと仕事を探した後、安定した仕事を見つけました。",
        ),
        "careful": (
            "Please be careful when you carry this glass across the crowded kitchen.",
            "混雑した台所を横切ってこのグラスを運ぶときは、注意してください。",
        ),
        "blush": (
            "Some people blush when they receive unexpected praise in front of others.",
            "人前で思いがけず褒められると、顔を赤らめる人もいます。",
        ),
        "bend": (
            "You should bend your knees slightly before lifting the heavy box.",
            "重い箱を持ち上げる前に、膝を少し曲げるべきです。",
        ),
        "broadcast": (
            "The local station will broadcast the championship game live on Saturday evening.",
            "地元の放送局は土曜の夜に、決勝戦を生中継する予定です。",
        ),
        "collected": (
            "The museum collected valuable paintings from private owners across the country.",
            "その博物館は全国の個人所有者から貴重な絵画を集めました。",
        ),
        "hurt": (
            "His rude comment hurt my feelings even though he apologized later.",
            "彼は後で謝りましたが、その失礼な発言は私の気持ちを傷つけました。",
        ),
        "waved": (
            "The children waved goodbye as their grandparents drove away from the station.",
            "祖父母が駅から車で去るとき、子どもたちは手を振って別れを告げました。",
        ),
        "stand": (
            "We had to stand outside the theater while the staff checked our tickets.",
            "係員がチケットを確認している間、私たちは劇場の外に立っていなければなりませんでした。",
        ),
        "steam": (
            "You can steam the vegetables gently while the rice cooks in the next pot.",
            "隣の鍋でご飯を炊いている間に、野菜を弱火で蒸すことができます。",
        ),
        "mail": (
            "I will mail the signed documents to the office before Friday afternoon.",
            "私は署名した書類を金曜の午後までに事務所へ郵送します。",
        ),
        "float": (
            "Small pieces of ice can float on the surface of the cold mountain lake.",
            "小さな氷のかけらは、冷たい山の湖の水面に浮かぶことがあります。",
        ),
        "feed": (
            "The zookeepers feed the hungry animals early every morning before visitors arrive.",
            "飼育員たちは来園者が来る前、毎朝早く空腹の動物に餌を与えます。",
        ),
        "share": (
            "Good friends share their worries and support each other during difficult times.",
            "よい友人たちは悩みを分かち合い、困難なときに互いを支えます。",
        ),
        "chew": (
            "Dogs often chew their favorite toys when they feel bored at home.",
            "犬は家で退屈すると、お気に入りのおもちゃをよくかみます。",
        ),
        "learn by heart": (
            "Students sometimes learn by heart short poems before the literature exam.",
            "生徒たちは文学の試験の前に、短い詩を暗記することがあります。",
        ),
        "come of age": (
            "Many young people come of age while attending university away from home.",
            "多くの若者は、家を離れて大学に通う間に成人します。",
        ),
        "by all means": (
            "By all means, call me if you need help with the difficult assignment.",
            "もちろん、その難しい課題で助けが必要なら、私に電話してください。",
        ),
        "in no time": (
            "With everyone's help, we finished cleaning the classroom in no time.",
            "皆が手伝ってくれたので、私たちはあっという間に教室の掃除を終えました。",
        ),
        "out of date": (
            "This computer program is out of date and cannot open the newest files.",
            "このコンピュータープログラムは古く、最新のファイルを開けません。",
        ),
        "for good": (
            "After moving to Canada, she left her hometown for good.",
            "カナダへ引っ越した後、彼女は故郷を永遠に離れました。",
        ),
        "from day to day": (
            "The weather changes from day to day during the spring season here.",
            "この地域では春の間、天気が日ごとに変わります。",
        ),
        "in a word": (
            "In a word, the new restaurant was excellent and worth visiting again.",
            "一言で言えば、その新しいレストランはすばらしく、また訪れる価値がありました。",
        ),
        "on your side": (
            "You can relax because an experienced lawyer is on your side.",
            "経験豊富な弁護士があなたの味方なので、安心してよいですよ。",
        ),
        "with any luck": (
            "With any luck, the package will arrive before the birthday celebration begins.",
            "運がよければ、誕生日のお祝いが始まる前に荷物が届くでしょう。",
        ),
    },
    "2025-3": {
        "skill": (
            "Learning a new skill can give students confidence in many situations.",
            "新しい技能を学ぶことは、さまざまな場面で生徒に自信を与えます。",
        ),
        "audio": (
            "The teacher played the audio twice so everyone could hear the pronunciation clearly.",
            "先生は皆が発音をはっきり聞けるように、その音声を2回流しました。",
        ),
        "joy": (
            "The children shouted with joy when their team won the final game.",
            "チームが決勝戦に勝ったとき、子どもたちは喜びの声を上げました。",
        ),
        "shadow": (
            "We sat in the shadow of the large tree during the hot afternoon.",
            "暑い午後、私たちは大きな木の陰に座りました。",
        ),
        "talent": (
            "Her musical talent became obvious when she performed the difficult song.",
            "彼女が難しい曲を演奏したとき、音楽の才能は明らかになりました。",
        ),
        "pattern": (
            "The designer chose a colorful pattern for the new summer dress.",
            "そのデザイナーは新しい夏のドレスに、色鮮やかな柄を選びました。",
        ),
        "value": (
            "The teacher explained the value of practicing English every day.",
            "先生は毎日英語を練習することの価値を説明しました。",
        ),
        "impression": (
            "The friendly guide made a positive impression on all the visitors.",
            "その親切な案内人は、来場者全員に好印象を与えました。",
        ),
        "survey": (
            "The city conducted a survey to learn what residents wanted.",
            "その市は住民が何を望んでいるか知るため、調査を行いました。",
        ),
        "requirement": (
            "A passport is an important requirement for traveling to many countries.",
            "パスポートは多くの国へ旅行するための重要な要件です。",
        ),
        "purse": (
            "She found her missing purse under the seat of the crowded bus.",
            "彼女はなくした財布を、混雑したバスの座席の下で見つけました。",
        ),
        "statement": (
            "The manager issued a clear statement after the accident at the factory.",
            "工場で事故が起きた後、責任者は明確な声明を出しました。",
        ),
        "product": (
            "The company tested the new product carefully before selling it overseas.",
            "その会社は新製品を海外で販売する前に、注意深くテストしました。",
        ),
        "failure": (
            "The experiment was a failure, but the students learned something important.",
            "その実験は失敗でしたが、生徒たちは大切なことを学びました。",
        ),
        "journey": (
            "The long journey became enjoyable when we saw beautiful mountain scenery.",
            "美しい山の景色を見てから、長い旅は楽しくなりました。",
        ),
        "wondered": (
            "She wondered whether the small shop would remain open during winter.",
            "彼女はその小さな店が冬の間も営業するのかと思いました。",
        ),
        "disappeared": (
            "The footprints disappeared after heavy snow covered the path overnight.",
            "一晩で大雪が道を覆った後、足跡は消えました。",
        ),
        "supposed": (
            "I was supposed to call my uncle before leaving for the airport.",
            "私は空港へ出発する前に、叔父へ電話することになっていました。",
        ),
        "entered": (
            "The students entered the classroom quietly after the bell rang.",
            "ベルが鳴った後、生徒たちは静かに教室へ入りました。",
        ),
        "forward": (
            "Please move forward slowly so the people behind you can pass.",
            "後ろの人が通れるように、ゆっくり前へ進んでください。",
        ),
        "loudly": (
            "The audience laughed loudly when the actor told a funny story.",
            "俳優が面白い話をすると、観客は大声で笑いました。",
        ),
        "worldwide": (
            "The event attracted worldwide attention because of its unusual scientific discovery.",
            "その出来事は珍しい科学的発見のため、世界中の注目を集めました。",
        ),
        "altogether": (
            "There were twenty students altogether in the afternoon cooking class.",
            "午後の料理教室には、全部で20人の生徒がいました。",
        ),
        "cold": (
            "The water was extremely cold, so nobody wanted to swim there.",
            "水がとても冷たかったので、そこでは誰も泳ぎたがりませんでした。",
        ),
        "guilty": (
            "The court found the driver guilty after reviewing the camera evidence.",
            "裁判所はカメラ映像を確認した後、その運転手を有罪としました。",
        ),
        "rest": (
            "You should get enough rest before the long examination tomorrow morning.",
            "明日の朝の長い試験の前に、十分な休息を取るべきです。",
        ),
        "attend": (
            "Many parents attend the school meeting to discuss their children's progress.",
            "多くの保護者が子どもたちの進歩について話し合うため、学校の集会に出席します。",
        ),
        "hire": (
            "The restaurant plans to hire two additional cooks before the busy season.",
            "そのレストランは繁忙期の前に、料理人を2人追加で雇う予定です。",
        ),
        "order": (
            "We need to order new chairs before the office opens next month.",
            "私たちは来月事務所が開く前に、新しい椅子を注文する必要があります。",
        ),
        "catch": (
            "Run quickly if you want to catch the last train home tonight.",
            "今夜、家へ帰る最終列車に乗りたいなら、急いで走ってください。",
        ),
        "hide": (
            "The child tried to hide behind the curtain during the game.",
            "その子どもはゲーム中、カーテンの後ろに隠れようとしました。",
        ),
        "heal": (
            "The nurse said the wound would heal faster with proper care.",
            "看護師は、適切に手当てをすれば傷はより早く治ると言いました。",
        ),
        "chase": (
            "The police officer had to chase the thief through the crowded market.",
            "警察官は混雑した市場を通って、泥棒を追いかけなければなりませんでした。",
        ),
        "accept": (
            "She decided to accept the invitation after checking her busy schedule.",
            "彼女は忙しい予定を確認した後、その招待を受けることにしました。",
        ),
        "take over": (
            "My older sister will take over the shop while our parents travel.",
            "両親が旅行している間、姉が店を引き継ぎます。",
        ),
        "come to": (
            "The two sides finally come to an agreement after several long meetings.",
            "両者は何度も長い会議をした後、ついに合意に至ります。",
        ),
        "point out": (
            "The guide will point out the oldest buildings during the walking tour.",
            "案内人は徒歩ツアー中に、最も古い建物を指摘して教えてくれます。",
        ),
        "laugh at": (
            "It is unkind to laugh at someone who makes an honest mistake.",
            "正直な間違いをした人を笑うのは親切ではありません。",
        ),
        "all over": (
            "Bright posters were placed all over the city before the festival.",
            "祭りの前に、明るいポスターが街中に貼られました。",
        ),
        "just like": (
            "This small village looks just like the town in my childhood memories.",
            "この小さな村は、子どもの頃の記憶にある町とそっくりです。",
        ),
        "up to": (
            "The final decision is up to the director after the committee meeting.",
            "委員会の会議の後、最終決定は責任者に委ねられます。",
        ),
        "ahead of": (
            "We arrived ahead of schedule and waited outside the quiet theater.",
            "私たちは予定より早く到着し、静かな劇場の外で待ちました。",
        ),
        "have a word": (
            "I need to have a word with the manager about this problem.",
            "私はこの問題について責任者と少し話をする必要があります。",
        ),
        "as soon as": (
            "Please call me as soon as you reach the station safely.",
            "駅に無事着いたら、すぐに私へ電話してください。",
        ),
        "even if": (
            "I will support your decision even if the plan becomes difficult.",
            "その計画が難しくなっても、私はあなたの決定を支持します。",
        ),
        "succeeded in": (
            "She succeeded in solving the puzzle after several careful attempts.",
            "彼女は何度か慎重に試した後、そのパズルを解くことに成功しました。",
        ),
        "lived on": (
            "For many years, the family lived on rice and vegetables from their farm.",
            "その家族は長年、自分たちの農場の米と野菜で暮らしました。",
        ),
        "suffered from": (
            "He suffered from a serious fever during the long winter holiday.",
            "彼は長い冬休みの間、ひどい熱に苦しみました。",
        ),
        "felt like": (
            "I felt like taking a short walk after finishing my homework.",
            "宿題を終えた後、私は少し散歩したい気分でした。",
        ),
    },
    "2026-1": {
        "nervously": (
            "The student waited nervously outside the principal's office before the interview.",
            "その生徒は面接の前、校長室の外で緊張しながら待ちました。",
        ),
        "absolutely": (
            "The restaurant is absolutely packed with customers during the lunch hour.",
            "昼食時、そのレストランは客でいっぱいです。",
        ),
        "rarely": (
            "We rarely eat at that restaurant because it is far from our home.",
            "私たちは家から遠いので、そのレストランではめったに食事をしません。",
        ),
        "separately": (
            "Please pack the fragile glasses separately from the heavy kitchen dishes.",
            "割れやすいグラスは重い台所用品とは別に包んでください。",
        ),
        "reduced": (
            "The store reduced the price of winter coats before the weekend sale.",
            "その店は週末のセールの前に、冬のコートの価格を下げました。",
        ),
        "proposed": (
            "The scientist proposed a new explanation after studying the unusual results.",
            "その科学者は珍しい結果を調べた後、新しい説明を提案しました。",
        ),
        "apologized": (
            "The driver apologized to the passengers after taking the wrong road.",
            "その運転手は道を間違えた後、乗客に謝りました。",
        ),
        "dangers": (
            "The guide explained the dangers of walking alone in the mountains.",
            "案内人は山を一人で歩く危険について説明しました。",
        ),
        "palaces": (
            "Tourists visited several beautiful palaces during their trip across Europe.",
            "観光客はヨーロッパを旅する間、いくつかの美しい宮殿を訪れました。",
        ),
        "markets": (
            "Local markets sell fresh vegetables and handmade goods every morning.",
            "地元の市場では毎朝、新鮮な野菜と手作り品を売っています。",
        ),
        "galleries": (
            "The city has several art galleries that display paintings by young artists.",
            "その市には若い芸術家の絵を展示する画廊がいくつかあります。",
        ),
        "wooden": (
            "The carpenter built a wooden table that could seat eight people.",
            "その大工は8人が座れる木製のテーブルを作りました。",
        ),
        "boring": (
            "The lecture seemed boring at first, but the final discussion was interesting.",
            "その講義は最初は退屈に思えましたが、最後の議論は興味深いものでした。",
        ),
        "cute": (
            "The children thought the small puppy was cute and very friendly.",
            "子どもたちはその小さな子犬を、かわいくてとても人なつこいと思いました。",
        ),
        "reasonable": (
            "The hotel offered a reasonable price for a clean room near the station.",
            "そのホテルは駅近くの清潔な部屋を手頃な価格で提供しました。",
        ),
        "award": (
            "The school gave her an award for helping younger students after class.",
            "学校は放課後に年下の生徒を助けたことで、彼女に賞を贈りました。",
        ),
        "aisle": (
            "The narrow aisle became crowded when shoppers entered the store together.",
            "買い物客が一斉に店へ入ると、狭い通路は混雑しました。",
        ),
        "attempt": (
            "Her first attempt to repair the bicycle failed, but she tried again.",
            "彼女の自転車修理の最初の試みは失敗しましたが、再び挑戦しました。",
        ),
        "announcement": (
            "The principal made an announcement about the school festival during lunch.",
            "校長は昼食中に、学校祭について発表しました。",
        ),
        "policies": (
            "The company changed its policies to give employees more flexible hours.",
            "その会社は従業員により柔軟な勤務時間を与えるため、方針を変更しました。",
        ),
        "blankets": (
            "The shelter gave warm blankets to families waiting outside in the cold.",
            "その避難所は、寒い中で外で待っている家族に暖かい毛布を渡しました。",
        ),
        "statues": (
            "The museum displays ancient statues from several different parts of Asia.",
            "その博物館はアジアのさまざまな地域から来た古代の像を展示しています。",
        ),
        "insects": (
            "Many insects disappear when the temperature falls below freezing at night.",
            "夜に気温が氷点下まで下がると、多くの昆虫は姿を消します。",
        ),
        "battery": (
            "The phone's battery ran out after I used the camera all afternoon.",
            "午後ずっとカメラを使った後、携帯電話のバッテリーが切れました。",
        ),
        "website": (
            "You can find the application form on the university's official website.",
            "大学の公式ウェブサイトで、申込書を見つけることができます。",
        ),
        "frame": (
            "The artist placed the finished photograph in a simple wooden frame.",
            "その芸術家は完成した写真を、シンプルな木製の額に入れました。",
        ),
        "paste": (
            "Use a little glue to paste the colorful paper onto the cardboard.",
            "少量ののりを使って、色紙を厚紙に貼り付けてください。",
        ),
        "blame": (
            "It is unfair to blame the new employee for that small mistake.",
            "その小さなミスを新人のせいにするのは不公平です。",
        ),
        "trust": (
            "Children need time to trust adults they meet in a new place.",
            "子どもたちが新しい場所で出会った大人を信頼するには時間が必要です。",
        ),
        "scratch": (
            "Be careful not to scratch the table when you move the heavy box.",
            "重い箱を動かすとき、テーブルを傷つけないように注意してください。",
        ),
        "enter": (
            "Visitors must enter the building through the main gate after noon.",
            "来訪者は正午以降、正門から建物へ入らなければなりません。",
        ),
        "engage": (
            "The museum uses games to engage children during the history exhibition.",
            "その博物館は歴史展示の間、ゲームで子どもたちを夢中にさせます。",
        ),
        "claim": (
            "The customer came back to claim the umbrella she had left there.",
            "その客は、そこに置き忘れた傘を受け取るため戻ってきました。",
        ),
        "score": (
            "Our team managed to score three goals during the second half.",
            "私たちのチームは後半に3得点を挙げることができました。",
        ),
        "ache": (
            "My legs began to ache after I walked around the city all day.",
            "一日中街を歩き回った後、私の脚が痛み始めました。",
        ),
        "soothe": (
            "A warm drink can soothe your throat when you have a bad cough.",
            "ひどいせきが出るとき、温かい飲み物は喉を和らげることがあります。",
        ),
        "push": (
            "Please push the button firmly until the green light appears.",
            "緑のランプがつくまで、そのボタンをしっかり押してください。",
        ),
        "gather": (
            "The volunteers gather donations for families affected by the earthquake.",
            "ボランティアは地震の被害を受けた家族のために寄付を集めます。",
        ),
        "next to": (
            "The small bookstore is next to a busy cafe near the station.",
            "その小さな書店は駅近くのにぎやかなカフェの隣にあります。",
        ),
        "except for": (
            "The museum is open every day except for Monday during winter.",
            "その博物館は冬の間、月曜日を除いて毎日開いています。",
        ),
        "across from": (
            "Our hotel is located across from the park and the public library.",
            "私たちのホテルは公園と公立図書館の向かいにあります。",
        ),
        "up to": (
            "The final choice is up to you after you hear both suggestions.",
            "2つの提案を聞いた後の最終的な選択は、あなた次第です。",
        ),
        "get on": (
            "We need to get on the bus before the doors close.",
            "ドアが閉まる前に、私たちはバスに乗らなければなりません。",
        ),
        "take off": (
            "The airplane will take off after the passengers fasten their seat belts.",
            "乗客がシートベルトを締めた後、その飛行機は離陸します。",
        ),
        "give up": (
            "Please do not give up even when the exercise seems difficult.",
            "その練習問題が難しく思えても、どうかあきらめないでください。",
        ),
        "look out": (
            "Look out for bicycles when you cross this narrow street.",
            "この狭い通りを渡るときは、自転車に気をつけてください。",
        ),
        "in a good temper": (
            "He was in a good temper after receiving the good news.",
            "よい知らせを受けた後、彼は機嫌がよかったです。",
        ),
        "none of your business": (
            "What I do after work is none of your business, thank you.",
            "仕事の後に私が何をするかは、あなたには関係ありません。",
        ),
        "make up my mind": (
            "I cannot make up my mind until I compare the two plans.",
            "2つの計画を比べるまで、私は決心できません。",
        ),
        "get off my back": (
            "Please get off my back and let me finish this work alone.",
            "どうかうるさく言わず、私にこの仕事を一人で終えさせてください。",
        ),
        "go on a voyage": (
            "They plan to go on a voyage around the islands next summer.",
            "彼らは来年の夏、島々を巡る航海に出る予定です。",
        ),
        "put out the light": (
            "Please put out the light before you leave the empty room.",
            "誰もいない部屋を出る前に、明かりを消してください。",
        ),
        "take a look at": (
            "Let's take a look at the map before choosing a route.",
            "道順を選ぶ前に、地図を見てみましょう。",
        ),
        "do a favor for": (
            "Could you do a favor for me and carry this box upstairs?",
            "私のために、この箱を2階へ運んでもらえますか。",
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
            "grade": "英検準2級",
            "round": round_id,
            "section": "Reading 大問1（語句空所補充）",
            "source": "英検公式の公開過去問PDFを、学習用JSONへ大問1だけ構造化",
            "source_problem_url": urls["problem"],
            "source_answer_url": urls["answer"],
            "counts": {"words": 40, "idioms": 20, "total": 60},
        }
    )
    return result


def apply_round(round_id: str) -> None:
    if round_id not in ROUND_IDS:
        raise ValueError(f"未登録の準2級回です: {round_id}")

    questions_path = DATA_DIR / f"questions_p2_{round_id}.json"
    vocab_path = DATA_DIR / f"vocab_p2_{round_id}.json"
    questions_data = load_json(questions_path)
    vocab_data = load_json(vocab_path)
    questions = questions_data.get("questions", [])
    words = vocab_data.get("words", [])
    idioms = vocab_data.get("idioms", [])
    all_items = [*words, *idioms]
    if len(questions) != 15:
        raise ValueError(f"{round_id}: 準2級は15問である必要があります")
    if len(words) != 40 or len(idioms) != 20:
        raise ValueError(f"{round_id}: 語句構成が40語・20熟語から変わっています")

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
    if sorted(questions_by_q) != list(range(1, 16)):
        raise ValueError(f"{round_id}: 設問番号が1〜15で連続していません")

    for q in range(1, 16):
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
        if not all(
            str(item.get(field, "")).strip()
            for field in ("meaning", "pos", "exampleTranslation", "etymology")
        ):
            raise ValueError(f"{round_id}: {surface}の学習項目が不足しています")
        if "word" in item and not re.fullmatch(r"/.+/", str(item.get("ipa", ""))):
            raise ValueError(f"{round_id}: {surface}のIPAがありません")
        if "phrase" in item and not isinstance(item.get("coreImage"), dict):
            raise ValueError(f"{round_id}: {surface}の核心イメージがありません")
        if len(WORD_RE.findall(example)) < 8 or len(surface_matches(example, surface)) != 1:
            raise ValueError(f"{round_id}: {surface}の例文が整合基準を満たしません")

    questions_data["meta"] = metadata(round_id, questions_data.get("meta", {}))
    vocab_data["meta"] = metadata(round_id, vocab_data.get("meta", {}))
    write_json(questions_path, questions_data)
    write_json(vocab_path, vocab_data)


__all__ = ["EXAMPLE_OVERRIDES", "ROUND_IDS", "apply_round"]
