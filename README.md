# 英検 大問1 単語アプリ

英検5級・1級・2級・準2級・準1級の大問1（語彙）を扱う静的Webアプリです。5級の2026年度第1回、1級・2級・準2級・準1級の各級過去問3回分に加え、1級の模試第1回〜第9回、準2級の自作模試第1回〜第4回、国際医療福祉大学の総合型選抜基礎試験セット2回分を収録しています（合計28セット）。準2級の自作模試と国際医療福祉大学セットは英検過去問を引用していません。

## 学習の流れ

1. 選択肢の意味・補足情報を確認する
2. 意味チェックを行う
3. 本番形式の4択問題を解く
4. 全語句の最終チェックで80%以上を目指す

問題セット・問題別進捗・途中位置はブラウザのローカルストレージに保存されます。
本番形式で間違えた問題も回答結果として保存しますが、専用の誤答復習には回しません。必要な場合は問題一覧からその設問をやり直せます。
意味だけ復習で間違えた英単語・熟語は、その1回分の最後に暗記カードで見直します。「確認した」を押して全件を確認すると、結果へ進めます。

### 間隔復習（全級共通）

各級とも、その級の収録セットの語句をまとめた「意味だけ復習」をホーム画面の独立した「間隔復習」カードとして使えます。通常学習で最後まで解いた設問の語句だけが対象になり、未学習の語句は出題されません。1回の出題は最大30語句で、正解した語句は1日・3日・7日・14日の間隔で復習へ回ります。

間隔が伸びるのは**速く正解できた語句だけ**です。正解でも解答までに時間がかかった語句は、間隔を伸ばさず同じ間隔でもう一度出します（遅いかどうかは、8秒未満なら常に速い・20秒以上なら常に遅い・その間はその回の中央値の1.6倍を境に判定します）。意味だけ復習での誤答が5回以上の語句は間隔の上限を3日に抑えます。出題順は誤答回数・直近の解答の遅さ・復習期限の超過日数から決めます。解答直後には、その語句の前回までの平均秒数も表示します（出題から計測した回のみ）。ホームでは語句を「未実施」「要再確認」「1日後」「3日後」「7日後」「14日後」に分けて表示します。対象語句は通常学習の進行に合わせて、その級の全語句まで増えます。

通常問題・意味練習の履歴は各回の進捗に最大500件まで保存し、古いものから置き換えます（ホーム画面には表示せず、内部記録のみ）。

| 級 | 設問数（3回合計） | 対象語句の上限 |
| --- | --- | --- |
| 5級 | 15 | 60 |
| 2級 | 51 | 204 |
| 準2級 | 105 | 420 |
| 準1級 | 54 | 216 |
| 1級（模試第1回〜第9回を含む） | 291 | 1164 |
| 医療福祉 基礎試験（第1回・第2回） | 30 | 120 |

語句ごとの復習間隔は、その語句が属する回の進捗（`eiken_q1_progress_<datasetId>` の `items`）に保存します。級をまたいで混ざることはありません。

## 日次・週次学習目標（英検5級〜1級）

英検5級・準2級・2級・準1級・1級の通常問題では、ホームの語彙目標カード上段に新規問題の学習計画を表示できます。常時表示は「今日 n / m問」です。新規問題は、本番形式4択へ初めて回答した `(datasetId, q)` の組です。正誤は問わず、同じ問題の解き直し・意味だけ復習は日次・週次・総問題数へ重複加算しません。医療福祉セットは英検の級ではないため対象外です。

- 総問題目標の初期値は、manifest配下のその級の通常問題数です（5級15問／準2級105問／2級51問／準1級54問／1級291問）。既存データとの互換性のため保持しますが、ホームの設定・表示には出しません。
- 1日の問題目標の初期値は8問、週間目標はその7倍です。設定では1日の問題目標と週の開始曜日を変更できます。週次の集計・再配分ロジックは保持しますが、ホームには表示しません。
- 日次・週次の実績は、設問の初回答時刻 `firstAnsweredAt` を利用者のローカル日付へ戻して集計します。既存履歴から補完できる場合は最古の設問回答時刻を使い、日時不明の旧回答は総数だけに含めます。
- 週の残り日数へ再配分する値は、`ceil(週間残数 / 今週の残り日数)` です。未達分を翌週へ自動繰越はしません。

同じカードには、1問4語句として、7・30・90・180・365日後の理論上の学習語句数と、その級の語彙目標へ到達する予想日を表示します。いずれも学習ペースの目安であり、長期予測には現在の収録語句数を超える理論値が含まれます。

語彙目標は級ごとに次の値です。5級は前の級を持たないため0語を起点とし、準2級以降は「前級の目標＝当級の起点」という連鎖になっています。

| 級 | 起点 | 目標 |
| --- | ---: | ---: |
| 5級 | 0 | 600 |
| 準2級 | 1,500（3級相当） | 3,000 |
| 2級 | 3,000 | 5,000 |
| 準1級 | 5,000 | 9,000 |
| 1級 | 9,000 | 14,000 |

計画設定は級ごとに独立して保存します。1級は従来どおり `eiken_q1_study_plan_v1`、他の級は `eiken_q1_study_plan_v1_<級プレフィックス>`（例: `eiken_q1_study_plan_v1_eiken5`）です。生徒別利用では同じキーの生徒別localStorageへ保存します。クラウド進捗では、1級を既存の `studyPlanV1`、他の級を `studyPlanByGradeV1` として `_meta` へマージし、既存の進捗・アプリID・1級の目標レコードは変更しません。

## 対象データ

- 5級: `data/questions_5_*.json` / `data/vocab_5_*.json`
- 2級: `data/questions_*.json` / `data/vocab_*.json`
- 準2級: `data/questions_p2_*.json` / `data/vocab_p2_*.json`
- 準2級模試第1回: `data/questions_p2_mock-1.json` / `data/vocab_p2_mock-1.json`
- 準2級模試第2回〜第4回: `data/questions_p2_mock-{2,3,4}.json` / `data/vocab_p2_mock-{2,3,4}.json`
- 準1級: `data/questions_pre1_*.json` / `data/vocab_pre1_*.json`
- 1級: `data/questions_1_*.json` / `data/vocab_1_*.json`
- 1級模試第1回: `data/questions_1_mock-1.json` / `data/vocab_1_mock-1.json`
- 1級模試第2回: `data/questions_1_mock-2.json` / `data/vocab_1_mock-2.json`
- 1級模試第3回: `data/questions_1_mock-3.json` / `data/vocab_1_mock-3.json`
- 1級模試第4回: `data/questions_1_mock-4.json` / `data/vocab_1_mock-4.json`
- 1級模試第5回: `data/questions_1_mock-5.json` / `data/vocab_1_mock-5.json`
- 1級模試第6回: `data/questions_1_mock-6.json` / `data/vocab_1_mock-6.json`
- 1級模試第7回: `data/questions_1_mock-7.json` / `data/vocab_1_mock-7.json`
- 1級模試第8回: `data/questions_1_mock-8.json` / `data/vocab_1_mock-8.json`
- 1級模試第9回: `data/questions_1_mock-9.json` / `data/vocab_1_mock-9.json`
- 国際医療福祉大学 基礎試験 第1回: `data/questions_iuhw_set-1.json` / `data/vocab_iuhw_set-1.json`
- 国際医療福祉大学 基礎試験 第2回: `data/questions_iuhw_set-2.json` / `data/vocab_iuhw_set-2.json`
- 熟語の核心イメージ共有辞書（データ検査・作成補助用。UIには表示しない）: `data/particle_images.json`
- 単語の語根・接辞辞書（表示専用）: `data/word_roots.json`
- 単語の語源分解（表示専用・原形キー）: `data/word_origins.json`
- 単語語源の個別再調査台帳（authoring正本）: `data/word_origin_research.json`
- 個別再調査バッチの記録: `data/word_origin_research_batch_*.json`
- 問題セット一覧: `data/manifest.json` の `q1`

1級の模試第1回〜第9回と公式過去問3回分は、模試25問/100語句・公式22問/88語句の形式差を保ったまま、共通検査で第6回の完成条件を確認できます。第7回〜第9回は表層音声と暗記カード用原形音声の生成済みデータを含むため、専用検査を通常モードで実行できます。

```powershell
py -3 scripts/check_eiken1_alignment.py --dataset-id eiken1-mock-6
py -3 scripts/check_mock_7_data.py
py -3 scripts/check_mock_8_data.py
py -3 scripts/check_mock_9_data.py
py -3 scripts/check_eiken1_alignment.py --dataset-id eiken1-2026-1
py -3 scripts/check_eiken1_alignment.py --dataset-id eiken2-2026-1
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp2-2026-1
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp1-2026-1
py -3 scripts/check_eiken1_alignment.py --dataset-id iuhw-set-2
py -3 scripts/check_eiken1_alignment.py --all
```

1級・2級・準2級・準1級・5級と国際医療福祉大学の各セットは、公式形式の件数を保ったまま、問題文訳・語句メタデータ・例文・IPA・正答フラグの共通整合検査を実行できます。`--all` はmanifest上の全28セットを対象にします。全1級セットの独立レビュー結果は `docs/EIKEN1_ALIGNMENT_REVIEW.md`、2級と準2級・準1級の整合記録は `docs/EIKEN2_ALIGNMENT.md`、`docs/EIKENP2_ALIGNMENT.md`、`docs/EIKENP1_ALIGNMENT.md`、医療福祉セットの整合記録は `docs/IUHW_ALIGNMENT.md` に記録しています。

準1級のQ1データは、全体過去問データから次で抽出します。

```powershell
py -3 scripts/build_q1_pre1_data.py
# 既存の生成JSONだけへ整合情報を再適用する場合
py -3 scripts/curate_pre1_data.py
# 2級の既存生成JSONへ整合情報を再適用する場合
py -3 scripts/curate_eiken2_data.py
# 準2級公式過去問の既存生成JSONへ整合情報を再適用する場合
py -3 scripts/curate_eikenp2_data.py
py -3 scripts/build_q1_1_data.py
py -3 scripts/enrich_flashcard_fields.py
py -3 scripts/curate_1_examples.py
py -3 scripts/check_q1_data.py
py -3 scripts/build_q1_official_data.py
```

1級公式過去問の入力PDFは `data/eiken_1/<round>/problem.pdf` と
`answer.pdf` に置きます。このフォルダは `.gitignore` 対象で、PDFを公開物へ含めません。

## 起動

```powershell
cd C:\Users\shtom\dev\eiken-q1-practice
py -3 -m http.server 8061 --bind 127.0.0.1
```

ブラウザで `http://127.0.0.1:8061/` を開きます。JSONを相対パスで読むため、`index.html` を直接開かないでください。

## 英検の単語・熟語音声

Azure Speechのキーを保存せず、環境変数から読み込んで単語・熟語MP3を生成します。

```powershell
$env:AZURE_SPEECH_KEY = "AzureポータルのKEY 1"
$env:AZURE_SPEECH_REGION = "japaneast"
py -3 scripts/generate_tts_1.py --grade 1 --round all
py -3 scripts/generate_tts_1.py --grade 2 --round all
py -3 scripts/generate_tts_1.py --grade 5 --round all
py -3 scripts/generate_tts_1.py --grade pre1 --round all
py -3 scripts/generate_tts_1.py --grade pre2 --round all
py -3 scripts/generate_tts_1.py --grade iuhw --round all
```

生成先は単語が `assets/audio/vocab/<級>/<回>/`、熟語が `assets/audio/vocab/<級>/<回>/idiom/` です。生成済みの単語・熟語は暗記カードと意味チェックで「音声」ボタンから再生できます。
準1級はMP3がない場合も、暗記カードの「音声」ボタンからブラウザ標準の英語音声を再生します。

暗記カードで表示する原形MP3は、`py -3 scripts/generate_lemma_tts.py --flashcard-only` で `assets/audio/lemma/` に生成します。

## 暗記カードの共通構成

全級で、見出し語・発音記号・品詞・意味・例文・例文の日本語訳を同じ順序で表示します。熟語の暗記カードは、意味・核心イメージの連鎖・例文の3ブロックで表示し、不変化詞の共有イメージや仲間例のパネルは表示しません。単語の語源は収録されている場合に表示し、語源チェーンがある語は熟語と同じ連鎖カード、A型の未チェーン語は構成チップと導出文、B型の未チェーン語は導出文を同じブロックで表示します（語根そのものの解説パネルは表示しません）。
1級の例文は公式の設問文を流用せず、語句ごとに作成したオリジナル英文と日本語訳を表示します。

語源データは語根597個、A型826語、B型707語を収録しています。単語の語源表示は `data/word_origins.json` だけを参照します（語句データに語源テキストは持ちません）。英検1級模試第6回では、84語すべてにEtymonline・Merriam-Webster・Collins等を照合した語源チェーンを付け、参照URLを語ごとに記録しています。その他の1級セットも、語源説明またはC型の除外理由を各語に付けています。

1,255語のB型は、`word_origin_research.json`で原形ごとに再調査状況・出典・語源経路・語根候補を管理します。確認済みデータを追加するときは、バッチJSONを作成して次を実行します。

```powershell
node scripts/apply-word-origin-research-batch.cjs data/word_origin_research_batch_001.json
node scripts/rebuild-word-origin-dictionaries.cjs --write
node scripts/check-word-origin-research.cjs
```

再調査対象1,255語はすべて確認済みです。`npm test`では台帳と表示用辞書の投影一致も検査します。

## 暗記カードの例文訳

1級・2級・準2級・準1級の例文には `exampleTranslation` として日本語訳を収録しています。訳のない例文を補う
場合は、次のスクリプトを実行します。取得した機械翻訳は、教材として使う前に必要に応じて確認してください。

```powershell
py -3 scripts/add_example_translations.py --dry-run
py -3 scripts/add_example_translations.py
```

暗記カードでは、例文の下に日本語訳を表示し、従来の「使い方・コロケーション」欄は表示しません。

## モーション・状態表示

正誤判定、進捗・残数、語彙音声、保存状態には短い状態変化を付けています（詳細は `DESIGN.md` のモーション節）。

- 語彙音声ボタンは `data-audio-state="idle|loading|playing|error"` で状態を持ち、ラベル文言でも状態を示します。
- 保存状態（画面右上）はローカル保存中は非表示、クラウド同期時のみ「保存中／保存済み／失敗」をアイコンと文言で表示します。
- OS・ブラウザの「アニメーションを減らす」設定（`prefers-reduced-motion: reduce`）が有効な場合、装飾アニメーションはすべて停止し、状態を示す文言・記号はそのまま表示されます。

## 公開版・生徒別進捗

公開URL: https://shtomi-tech.github.io/eiken-q1-practice/

元の総合アプリと既存の公開URLは変更していません。

生徒別URLの `?s=<id>&t=<token>` では、共通Supabaseスキーマの `app_students` / `app_progress` に `app=eiken2-q1` として進捗を同期します。総合アプリ側のQ1進捗と同じ行を共有するため、スマホとPCの学習内容が端末をまたいで復元されます。匿名利用では従来どおりローカル保存だけで動作します。

`app=eiken-q1-practice` は2026-08-09〜2026-08-12に独立版だけが使っていた旧分岐IDです。既存の `eiken-q1-practice` 行はロールバック用バックアップとして残していますが、現在は読み書きしません。

旧準1級アプリの `eiken-pre1` 進捗は、初回起動時にQ1形式へ読み取り移行します。旧キーは移行確認のため残します。

### 使用者ごとの級固定

共有URLに `?g=5` / `?g=pre2` / `?g=2` / `?g=pre1` / `?g=1` を付けると、その使用者の学習範囲を指定した級に固定します。URL指定は生徒別localStorageにも保存され、URLを外しても維持されます。指定がない場合は初回に級を選びます。

固定中は他級の問題セットと復習期限を表示しません。他級の進捗は削除せずに残ります。URLに `g` がない場合だけ、ホーム最下部の「級を変更」から選び直せます。

## 保存キー

- `eiken_q1_dataset`
- `eiken_q1_progress_<datasetId>`
- `eiken_q1_study_plan_v1`
- 旧Q1互換: `eiken2_q1_v1`

## 構成

- `static/src/*.js`: 全級共通の大問1ロジックの正本（領域ごとに分割）
- `static/mode-q1.js`: `static/src/*.js` の結合結果。**生成物なので直接編集しない**
- `scripts/build-mode-q1.cjs`: 上記の結合ビルド（`npm run build`）
- `static/app.js`: Q1アプリの起動だけを担当する薄いシェル
- `static/vendor/harness/cloud.js`: 生徒別クラウド同期の生成物。直接編集しない
- `scripts/build_q1_pre1_data.py`: 準1級Q1データの抽出
- `scripts/build_q1_1_data.py`: 1級公式PDFから大問1を抽出
- `scripts/build_q1_official_data.py`: 2級・準2級・準1級の非公開公式PDFと設問・4択・正答位置を照合・再適用
- `scripts/build_pre1_data.py`: 1級公式PDFのページ・設問・解答キー抽出ヘルパー
- `scripts/build_q1_5_2026-1_data.py`: 5級2026年度第1回の大問1データ生成
- `scripts/enrich_flashcard_fields.py`: 対象データの発音・品詞の補完
- `scripts/curate_1_examples.py`: 1級のオリジナル例文・日本語訳の適用
- `scripts/rebuild-word-origin-dictionaries.cjs`: 語源再調査台帳から表示用辞書を再生成
- `scripts/apply-word-origin-research-batch.cjs`: 個別再調査バッチを台帳へ適用
- `scripts/check-word-origin-research.cjs`: 1,255語の調査状況・出典・原形対応を検査
- `scripts/check_eiken1_alignment.py`: 5級・準2級・2級・準1級・1級と医療福祉の全28セットの語句・例文・語源・音声の整合検査
- `scripts/review_official_questions.py`: 正答を伏せて2級・準2級・準1級公式問題をローカル別モデルでレビュー
- `scripts/check-pre1-core-image-compat.cjs`: 準1級48句動詞の`word:`進捗互換と核心イメージを検査
- `scripts/q1_eiken2_metadata.py`: 2級の例文補正・正答フラグ・出典メタデータの正本
- `scripts/curate_eiken2_data.py`: 2級の既存生成JSONへの整合情報の再適用
- `scripts/q1_eikenp2_metadata.py`: 準2級公式過去問の例文補正・正答フラグ・出典メタデータの正本
- `scripts/curate_eikenp2_data.py`: 準2級公式過去問の既存生成JSONへの整合情報の再適用
- `scripts/q1_pre1_metadata.py`: 準1級の設問文訳・例文補正・出典メタデータの正本
- `scripts/curate_pre1_data.py`: 準1級の既存生成JSONへの整合情報の再適用
- `scripts/build_q1_mock_1_data.py`: 1級模試第1回の問題・語彙データ生成
- `scripts/build_q1_mock_2_data.py`: 1級模試第2回の問題・語彙データ生成
- `scripts/build_q1_mock_3_data.py`: 1級模試第3回の問題・語彙データ生成
- `scripts/build_q1_mock_4_data.py`: 1級模試第4回の問題・語彙データ生成
- `scripts/build_q1_mock_5_data.py`: 1級模試第5回の問題・語彙データ生成
- `scripts/build_q1_mock_6_data.py`: 1級模試第6回の問題・語彙データ生成
- `scripts/build_q1_mock_7_data.py`: 1級模試第7回の問題・語彙データ生成
- `scripts/build_q1_mock_8_data.py`: 1級模試第8回の問題・語彙データ生成
- `scripts/build_q1_mock_9_data.py`: 1級模試第9回の問題・語彙データ生成
- `scripts/build_q1_p2_mock_1_data.py`: 準2級自作模試第1回の問題・語彙データ生成
- `scripts/build_q1_p2_mock_{2,3,4}_data.py`: 準2級自作模試第2回〜第4回の問題・語彙データ生成
- `scripts/build_q1_iuhw_set_1_data.py`: 国際医療福祉大学セット第1回の問題・語彙データ生成
- `scripts/build_q1_iuhw_set_2_data.py`: 国際医療福祉大学セット第2回の問題・語彙データ生成（完全自作・熟語12件）
- `scripts/check_mock_6_data.py`: 1級模試第6回の内容・重複チェック
- `scripts/check_mock_7_data.py`: 1級模試第7回の内容・重複・音声チェック
- `scripts/check_mock_8_data.py`: 1級模試第8回の内容・重複・音声チェック
- `scripts/check_mock_9_data.py`: 1級模試第9回の内容・重複・音声チェック
- `scripts/check_5_data.py`: 5級2026年度第1回大問1の内容・公式解答チェック
- `scripts/check_q1_data.py`: 28セットのデータ契約チェック
- `scripts/check_p2_mock_data.py`: 準2級自作模試（全回）の内容チェック

このリポジトリは大問1専用です。大問2・3、リスニング、ライティング、言い換えのコード・教材・音声・生成スクリプトには依存しません。
