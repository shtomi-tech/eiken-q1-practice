# DESIGN.md — eiken-q1-practice

> このアプリのUIデザイン正本。エージェントは `dev/CLAUDE.md` の共通指針ではなく**このファイルに準拠**すること。
> ベース: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) の Claude DESIGN.md（Anthropic公式サイト風の暖色エディトリアルデザイン）を本アプリ（英検1級・2級・準2級・準1級の大問1語彙演習、Windows/モバイル環境）向けに適応。

## デザインの核

暖色クリームの紙面に、セリフ見出し・モノスペースラベル・単一の焦茶アクセント（Clay）を組み合わせたエディトリアルな学習アプリの言語。罫線で区切る活版印刷調から、背景色の階調（canvas／card／soft／strong の4段）と角丸カードで深度を表す構成に転換。影はほぼ使わない。正誤・状態は色だけに頼らず、文言・記号・アイコンを必ず併記する（既存の学習UI設計を継続）。

## カラーパレット

### アクセント（インタラクティブ）
- **Clay** `#a9583e` — 間隔復習・最終チェック等の「要注意・行動喚起」アクション、おすすめ導線の見出し文字、間隔復習カードの左太罫。Claude原典のcoral `#cc785c` はクリーム地でコントラスト比が約3.1:1しかなくAA未達のため、`primary-active` 相当の値を採用（実測 約4.8:1）
- **Clay Hover** `#8a4732` — Clay要素の押下色。明るい背景上の小さいアクセント文字にも使用する（実測5.7:1以上）
- 第2のアクセント色を追加しない。通常の学習フロー（開始・意味チェック等）は Ink（下記）を主色として使う

### サーフェス
- **Canvas** `#faf9f5` — ページ地色
- **Card** `#efe9de` — カード面（`.card` 等、canvasより一段深いクリーム）
- **Surface Soft** `#f5f0e8` — ホバー時の淡い着色
- **Surface Strong** `#e8e0d2` — 選択状態の着色
- **Dark Tile** `#141413`（Ink と同値）— ヒーロー・完了バナー等の反転タイル。Claude原典の `surface-dark #181715` とはRGB差が数単位で視覚的に無差別なため、別トークンを起こさず Ink に統合

### テキスト
- **Ink** `#141413` — 見出し・本文・主要ボタン背景（開始・意味チェック等の標準フロー）
- **Muted** `#615c54` — 補助テキスト・キャプション・モノスペースラベル。Claude原典の `muted #6c6a64` は本アプリのCard地(`#efe9de`)上で実測4.48:1とAA基準4.5:1をわずかに下回るため、5.5:1前後を確保できる値に微調整
- **On Dark** `var(--parchment)` / 補助は `rgba(250,249,246,.72)` 前後

### ボーダー
- **Hairline** `#e6dfd8` — カード・入力欄・選択肢の枠線（罫線は最小限、太い区切りは章単位の見出し前のみ2pxで残す）

### 機能色（正誤フィードバック用）
- **OK** `#16803a`（正解）／ **OK Text** `#126b30`（Card・Surface上の小さい状態文字）／ **NG** `#b42318`（不正解）／ **Warn** `#a16207`（部分一致）
- Claude原典の `success #5db872`（対クリーム地コントラスト約2.3:1）・`warning #d4a017`（約2.3:1）・`error #c64545`（約4.6:1）はいずれもAA未達または現状値より弱いため採用せず、実測でAAを満たす値を維持する（AGENTS.md「理論とアクセシビリティが衝突する場合はアクセシビリティを優先」）

## タイポグラフィ

- 見出し（display）: `"Cormorant Garamond", Georgia, "Hiragino Mincho ProN", "Yu Mincho", serif`。Claude原典のCopernicus（非公開ライセンス書体）代替としてGoogle Fontsから読み込む。ウェイト500〜600、字間は詰めない（日本語混植のため原典のnegative trackingは採用しない）
- 本文: `"Inter", "Segoe UI", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif`。StyreneB代替。ラテン文字はInter、CJK文字は既存システムフォントに自動フォールバック
- ラベル・カウンタ: `"JetBrains Mono", "SFMono-Regular", Consolas, monospace`。大文字化＋字間拡大（既存踏襲）
- 暗記カード本文の行幅上限: 日本語（`.flashMeaning` `.flashExampleTranslation`）は34em、ラテン文字の例文（`.flashEx`）は58ch。カードの情報量は変えず、長文だけを読み幅で制約する
- フォント読み込みは `display=swap` 必須。取得中・失敗時も日本語システムフォントでレイアウトが崩れない

## 角丸スケール

- `pill` 9999px — バッジ・チップ・丸番号バッジ（`.key`）
- `lg` 12px — カード全般（`.card` `.flash` `.passageCard` `.textPanel` 等）
- `md` 8px — ボタン・入力欄・タブ・グリッドタイル
- `sm` 6px — リスニングの問題一覧タイルなど小型要素
- 全面ブリードのタイル（`.hero` `.doneBanner` `.completionCard` の内部要素）は文脈に応じてlg

## 影・深度

- **影はほぼ使わない**。深度は (1) サーフェス色の切替（canvas ⇔ card ⇔ soft/strong ⇔ dark tile）(2) hairline ボーダー（入力欄・選択肢・小区切りのみ）で表現
- 例外: フローティングパネル（`.dictSettingsBody` 等、背景から浮くポップオーバー）のみ軽いdrop-shadowを許容
- 罫線結合グリッド（親にborder-top/left、子にborder-right/bottomを持たせて格子を作る手法）は廃止。`gap` + 個々のセルへの背景色・角丸に置き換える

## スペーシング

既存のグリッド不使用（4/8/12/16/24/32px前後の実測値を踏襲）。新規・変更箇所は 4/8/12/16/24/32 のスケールに寄せる。ボタン・選択肢の gap は 12px に統一。

## 印刷用翻訳ワークシート

- 翻訳用HTMLは A4縦・1枚を標準とし、`@page { size: A4 portrait; margin: 8mm; }` と本文幅 `194mm` を基準にする。
- 印刷時は画面用の操作リンク・フッターを非表示にし、英文の各行と訳欄がページ途中で分割されないよう `break-inside: avoid` を指定する。
- 1枚に収まるかをPDFまたは印刷プレビューで確認する。収まらない場合は任意の高さ固定やページラッパーの `overflow: hidden` で下端を切らず、余白を先に調整する。それでも読めない場合は英文を分割する。
- 訳欄は右列を空欄にし、max(1, 表示された英文の行数−1)本の横罫線で記入欄を分ける。1行の英文でも罫線は1本置く。罫線はセル幅いっぱいの明示的な層として描き、画面幅・印刷幅の変更後も英文の折り返し行数を測って再計算する。中央の縦罫線はグリッド親要素で連続させ、行ごとの罫線の継ぎ目を作らない。
- 英文は画面24px・印刷18pxを基準とし、行間は画面では `2.1` 前後、印刷では `1.7` 前後にして、読みやすさとA4 1枚への収まりを両立する。

## コンポーネント規範

- **主ボタン（既定button）**: Ink地＋Parchment文字、角丸md、min-height 44px。通常の学習フロー（開始・意味チェック・次へ等）に使用
- **要注意アクション（`.reviewCta` `.finalCta`）**: Clay地。`.reviewCta` は間隔復習（意味だけ復習）、`.finalCta` は最終チェックに使用し、通常フローと視覚的に区別する
- **副ボタン（`.ghost`）**: 透明地＋Ink文字＋hairline枠、角丸md。ホバーでInk地に反転
- **二次アクション（`.secondaryCta`）**: 透明地＋hairline枠、角丸md。reviewCta/finalCta系統は枠・文字をClayに
- **カード（`.card` 等）**: Card地・角丸lg・枠なし・影なし
- **語彙目標カード（`.vocabGoalCard`）**: 級単位の語彙目標を、前級目標→当級目標の1本のバーで示す。前級までの区間は「習得済み前提」の中立色（Muted）、このアプリでの実績だけをClayで重ねる。実績は差分区間でクランプし、0でないときは最小3pxで可視化する。現在位置には横向きドット絵のハリネズミ（`.vgHedgehog`／box-shadowのみ。外部画像を持たない、`aria-hidden`）が立ち、実績が1語句以上のときだけ歩く。1級では同じカード内に14,000語到達予想・固定期間の理論語句予測・現在の収録語句数を追加する。語彙数は英検公式の公表値ではないため、「前級までは習得済みとして計算」「目安です」の注記を必ず併記する
- **1級学習計画パネル（`.studyPlanPanel`）**: 「今日の学習」カードを日次・週次の新規問題目標の正本とする。主CTAは増やさず、総目標・今日・今週の進捗と調整目安をカード末尾へ置く。設定フォームは同カード内で開閉し、number input 2つと週開始曜日select、保存・キャンセルを持つ。進捗は文字と `role="progressbar"` の値を併記し、320px幅でも折り返す
- **間隔復習カード（`.spacedReviewCard`）**: 通常学習カードの兄弟として置き、Clayの左4px罫だけで復習導線を示す。カード内のCTAは意味復習セッションだけを開始する。意味復習で誤答した語句は、セッション末尾に暗記カードで見直し、「確認した」を押してから結果へ進む
- **セッション操作バー（`.sessionActionBar`）**: 暗記カード（flashステージ）だけ、送り操作を画面下部へ固定する。Parchment地＋上辺hairline、影なし、`.wrap` と同じ最大幅で中央寄せ。左に前カード、中央に「カード n / 4」、右に次カードを1行で置く。check／practice／doneは従来のカード末尾の`.actions`を使う
- **暗記カードの意味（`.flashMeaning`）**: 覚える対象として見出し語に次ぐ2番目の強さを持たせ、22px・600ウェイトを基準とする。見出し語に対する文字サイズ比は0.70以上を保つ
- **問題セットUnitカード（`.datasetUnitCard`）**: Parchment地＋hairline枠、角丸md。状態は未着手／途中保存あり／学習中／CLEARの4値で扱い、現在選択中はInkの左4px罫＋Surface Strong地（`aria-current="true"`）、CLEAR済みはOKの左4px罫＋「✓ CLEAR」文言、途中保存ありはMutedの「途中保存：第n問・…」文言を進捗と併記する。通常学習の誤答は専用の復習状態にせず、設問の回答結果として表示する。意味だけ復習の誤答見直しはセッション内だけで完結する。色だけに頼らず必ず文言を併記する。番号バッジは表示順であり永続IDではない
- **熟語の核心イメージ（`.coreChain`）**: すべての配信対象の熟語暗記カードを、意味・核心イメージ・例文の3ブロックで構成し、意味の直下に構成語から中心義へ進む2〜5段の連鎖を置く。連鎖はParchment地＋hairline枠のステップで示し、最終ステップが中心義になるため結論行は置かない。不変化詞の共有イメージと仲間例のパネルは表示しない。矢印はCSS疑似要素の装飾とし、読み上げ順に不要な記号を混ぜない。480px以下では縦積みに切り替える
- **単語の語源表示（`.originChain` `.originChip` `.originDerivation`）**: 単語の暗記カードでは、意味の直下・例文の前に置く。語源チェーン（`.originChain`）がある語は、熟語の核心イメージと同じ`.coreChain`のステップカードで、歴史的な構成要素から現在の中心義までを示す。チェーンの最終ステップは中心義だけにし、導出文は独立表示しない。従来のA型はチップ（`.originChip`）と導出文（`.originDerivation`）を同じ語源ブロック内に置き、B型の未チェーン語は一行の由来として表示する。単語カードでは情報量を抑えるため、語根そのものの解説パネル（語根名・イメージ注記・仲間語リスト）は表示しない。480px以下では共通のチェーンを縦積みにし、旧チップも縦積みにする
- **強調タイル（`.hero` `.doneBanner` `.completionCard`）**: Ink地＋Parchment文字の反転表示、角丸lg。「学習フローの始まり」と「締めくくり」を示す
- **選択肢（`.choiceBtn` `.dictChoice`）**: Paper地＋Ink文字＋hairline枠、角丸md。ホバー/選択でInk反転。正解＝OK色の2px枠、不正解＝NG色の2px枠（coral化しない。主要CTAとの混同を避けるため中立表現を維持）
- **番号バッジ（`.key`）**: 24×24pxの円形（角丸pill）、currentColor枠
- **タブ／グリッドタイル（`.appTab` `.qCard` `.dictQuestionList .qBtn`）**: 罫線結合ではなくgapベースのグリッド。各セルはPaper/Parchment地＋角丸md/sm。アプリ移動は「進み方」と「技能」の2グループに分け、主目的の異なるタブを同じ段に混在させない
- **バッジ・チップ（`.tag` `.dictBadge` `.chip`）**: 角丸pill、hairline枠
- **フィードバックカード（`.feedback` `.resultBox`）**: 左4px太罫（Ink既定、OK/NGで色変化）＋Paper地、角丸md、外枠なし
- **入力欄（select/input）**: Paper地＋hairline枠、角丸md、min-height 44px

## モーション

MOTION_INTENSITY: 3（既定UIに一貫した押下感・状態変化を与えるが、装飾演出は最小限）。参考: [Kinetics](https://kinetics.colorion.co/) の Push Button / Success Check / Error Shake / Elastic Progress / Submit States / Equalizer Bars / Status Pill / Tab Pill Glide。実装はVanilla JS/CSSのみで、本番依存を増やさない。

### Duration・原則
- **press** 80ms／**release** 180ms／**feedback**（正誤表示）200ms／**progress**（進捗・残数）280ms／**async-state**（音声・送信・保存の状態遷移）220ms／**completion**（初回CLEAR等）420ms
- アニメーション対象は `transform`・`opacity`・色・progress fillに限定する。`width`/`height`/`margin`等レイアウトを揺らすプロパティはアニメーションしない
- 正誤・結果の値は動きの完了を待たずに同フレームで確定表示する（アニメは装飾であり、情報を遅延させない）

### 状態マトリクス
| 対象 | 状態 | 表現 |
| --- | --- | --- |
| 語彙音声 | idle / loading / playing / error | ラベル文言＋`data-audio-state`。playing中は装飾Equalizer Bars（`aria-hidden`） |
| 自作例文チェック | idle / submitting / ok / revise / error | `data-submit-state`。submitting中はボタンdisabled＋小さいloader。okはSuccess Check、reviseは既存の焦茶静的状態、errorは赤い左罫線＋再試行案内 |
| 語彙目標のハリネズミ（`.vgHedgehog`） | 停止 / 歩行 | `data-walking`。実績が1語句以上で520ms・steps(2)の上下2フレーム歩行（transformのみ）。reduced-motionでは静止した状態を表示する |
| 保存状態（`#shareStatus`） | local（非表示）/ syncing / saved / error | harnessの`tone`(`ok`/`syncing`/`ng`)をそのまま利用。syncingはloader、savedは一度だけcheck、errorは静的`!` |

### reduced motion
- `prefers-reduced-motion: reduce` では上記すべての追加アニメーションのdurationを0にする
- 同期中を示すspinner系のみ、状態が分かるよう最小限の非アニメーション表現（静的ドット等）に置き換えてよい。処理中・失敗などの**文言自体は動作の有無に関わらず必ず表示する**

## Do / Don't

✓ CSS変数名は旧デザインとの互換のため維持し、値だけ差し替える（JSがvar参照するため）／ 正誤・状態は色だけでなく文言・記号を併記する／ 44px以上のタップターゲットを死守する（Claude原典のheight:40pxより優先）／ WCAG 2.2 AA を満たす／ 罫線は入力欄・選択肢・章区切りなど機能的な意味がある箇所にのみ残す

✗ `--ok`/`--ng`/`--warn` にClaude原典の生トークンを使わない（実測でAAコントラスト未達）／ 選択肢ボタン（`.choiceBtn`等）の背景をClay/coralにしない（主要CTAとの意味的な混同を避ける）／ 罫線結合グリッド（border-top+left / border-right+bottomの組み合わせ）を新規に作らない／ 装飾のためだけの影を追加しない

## ホームの層構造

ホームは、スコープの広い順 × 決定コストの低い順に、上から次の問いへ答える。

| 層 | 答える問い | 要素 |
|---|---|---|
| A | これは何のアプリか | 導入（初回訪問時のみ表示） |
| B | 次に何をすればいいか | 主CTA1つ＋途中保存通知＋進捗指標＋1級の日次・週次学習計画 |
| C | どこまで来たか | 語彙目標カード＋1級の長期語彙予測 |
| D | 他に今日できることは | 意味だけ復習（範囲横断） |
| E | 別の範囲をやりたい | 学習セット／問題セットの選択 |
| F | 特定の箇所から始めたい | 範囲内の単位一覧・参照一覧 |
| G | 記録と設定を触りたい | 履歴・進捗リセット・級変更 |

| 層 | kobun-vocab-learning | eiken-q1-practice |
|---|---|---|
| A | hero（初回のみ） | hero（初回のみ） |
| B | 主カード（label / h2 / recommend / stats） | 今日の学習カード（主CTA＋日次・週次計画） |
| C | 語彙目標カード | 語彙目標カード（14,000語到達予想・期間別予測を含む） |
| D | 意味だけ復習 | 意味だけ復習 |
| E | 学習セット選択 | 問題セット選択 |
| F | 学習ブロックマップ → 単語一覧 | 問題一覧 |
| G | 履歴 → その他 | その他（リセット＋級変更） |

- EとFは隣接させ、「範囲を選ぶ → その中の単位を選ぶ」の順にする。
- DはEより上に置く。意味だけ復習は範囲横断のプールを対象にする。
- 進捗の数値（stats）と語彙目標カードの間に他要素を挟まない。
- 1級では日次・週次計画を「今日の学習」カード内へ置き、語彙予測は既存の語彙目標カード内へ置く。主CTA、ホーム層B/Cの順序、意味だけ復習の位置は変えない。
- 一覧はデータ順・manifest順を維持し、進捗で並べ替えない。
- A層のhero（`.hero`）は初回訪問時のみ表示し、地色`--ink`・文字`--parchment`の反転カードにする。kobun-vocab-learningの`.card.hero`と同じ表現に揃える。
