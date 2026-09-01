# 意味だけ復習を「例文の下線部を問う」形式にする計画

対象: `static/src/90-learn-flow.js` / `static/styles.css` / `index.html` / `DESIGN.md` /
例文の正本4スクリプト（`scripts/curate_1_examples.py`・`scripts/build_q1_mock_3_data.py`・`scripts/q1_eiken2_metadata.py`・`scripts/q1_pre1_metadata.py`）/
新規 `scripts/check-meaning-example-ui.cjs`
関連: [RESPONSE_TIME_SRS_PLAN.md](RESPONSE_TIME_SRS_PLAN.md)（応答時間とSRS）/ [CROSS_GRADE_DUE_PLAN.md](CROSS_GRADE_DUE_PLAN.md)（級横断プール）
状態: 実装・公開済み（`a05520e`）。以下は追補
- 実行時の一致判定は単語境界付きにした（境界なしだと "When" の中の "he" を下線にする）
- 音声ボタンは例文の横ではなく設問文の行へ置き、例文の行長を46ch→62chに広げた
スコープ: **意味だけ復習（`mode === "meaning"`）の出題形式のみ**。通常学習(learn)・最終チェック(final)の出題形式、4択の生成ロジック、SRSの判定は対象外

## 0. 目的

いま意味だけ復習は、語句を単独で見せて意味を4択で問う。

```
次の語句の意味は？
   consolidated  🔊
   ① … ② … ③ … ④ …
```

これを、古文単語アプリ（kobun-vocab-learning）と同じ「例文中の下線部の意味を問う」形式にする。

```
下線部の意味として最も適当なものを選べ
   The company c̲o̲n̲s̲o̲l̲i̲d̲a̲t̲e̲d̲ its regional offices into one headquarters.  🔊
   ① … ② … ③ … ④ …
```

語を裸で覚える状態から、**文脈の中で意味を取る**練習へ移す。意味だけ復習はフラッシュカードを挟まず
`stage: "check"` から始まる（[90-learn-flow.js:93](../static/src/90-learn-flow.js)）ため、例文は設問で初めて目に入り、
「直前に見た文の再認」にはならない。

## 1. 前提として確認した事実

| # | 事実 | 根拠 |
| --- | --- | --- |
| A | 意味確認画面 `renderCheck()` は `learn` / `meaning` / `final` の3モード共用 | [90-learn-flow.js:581](../static/src/90-learn-flow.js) |
| B | 意味だけ復習は `stage: "check"` 開始でフラッシュカードを経由しない | [90-learn-flow.js:93](../static/src/90-learn-flow.js) |
| C | 例文ハイライトの前例あり。`flashExampleRow()` が出題形を正規表現で `<em>` 化 | [90-learn-flow.js:541](../static/src/90-learn-flow.js) |
| D | `.flashEx em` は既に `border-bottom: 2px solid var(--ink)`。**見た目はすでに下線** | [styles.css:1236](../static/styles.css) |
| E | `data/vocab_*.json` 全**2124件**に `example` と `exampleTranslation` が存在。欠損ゼロ | 全ファイル走査 |
| F | うち**2119件**は出題形が例文中に完全一致。不一致は分離句動詞**5件のみ** | 同上（§4に一覧） |
| G | `data/vocab_*.json` は生成物。例文の正本は `scripts/` 側 | AGENTS.md / 各 `build_*.py` |
| H | 準1級には既存の例文差し替え機構 `EXAMPLE_OVERRIDES` がある | [q1_pre1_metadata.py:96](../scripts/q1_pre1_metadata.py) |
| I | 誤答の見直し画面は `buildFlashCard()` 再利用で、すでに例文＋下線＋訳を表示 | [90-learn-flow.js:759](../static/src/90-learn-flow.js) |
| J | `static/mode-q1.js` は生成物。編集は `static/src/` → `npm run build` | AGENTS.md |
| K | 公開は `main` への push をトリガーに GitHub Pages ワークフローが実行 | [.github/workflows/pages.yml](../.github/workflows/pages.yml) |

D は重要で、**Q15（見直し画面との統一）は新規スタイルの発明ではなく、既存の下線を共通トークンへ寄せる作業**になる。

## 2. UI変更（`static/src/90-learn-flow.js`）

### 2.1 `renderCheck()` — 出題部の分岐

`mode === "meaning"` かつ例文中に出題形が見つかるときだけ新形式にする。それ以外は現行のまま。

| 要素 | 現行（全モード） | 新（meaning のみ） |
| --- | --- | --- |
| ラベル `.label` | `次の語句の意味は？` | `下線部の意味として最も適当なものを選べ` |
| 語句表示 | `.askWordLine > .askWord`（見出し語） | `.askExampleLine > .askExample`（例文・該当箇所に下線） |
| 音声ボタン | `.quizListenButton`（語単体TTS） | 同じものを例文ブロックの脇に維持 |
| 出典・品詞 | なし | **出さない**（品詞は推測ヒントになるため） |
| 4択 | `meaningDistractors()` | 変更なし |

`roundInfo`（`4語句の意味確認 n / N`）と選択肢のキーボード操作・`armChoiceGuard()`・解答時間計測
（`session.checkShownAt`）は現行の実装をそのまま使う。**出題部の組み立てだけを差し替える**。

### 2.2 共通ヘルパーの抽出

`flashExampleRow()` の中に埋まっているマッチ処理を、単独の関数として切り出して両方から使う。

```js
// 例文中の出題形の位置を返す。見つからなければ null。
function exampleMatch(item) { ... }   // → { before, hit, after } もしくは null
// 例文ノードを組み立てる。hit を .exUnderline で包む。
function buildExampleText(item, match) { ... }
```

- `flashExampleRow()` はこのヘルパーを使う形に書き換える（表示内容・DOM構造は変えない。`<em>` → `<span class="exUnderline">` のみ）
- `renderCheck()` は `exampleMatch(item)` が `null` を返したときに現行の見出し語表示へフォールバックする（§4.3）

マッチは現行と同じ「出題形の完全一致・大文字小文字無視」を踏襲する。ステミングや語形変化の吸収は**しない**
（`surfaceOf()` が既に出題形＝例文に現れる形を持っているため不要で、入れると誤ハイライトのリスクだけが増える）。

### 2.3 解答後のフィードバック

`appendCheckFeedback()` に例文の日本語訳を1行追加する。例文（下線付き）は上に残したまま。

```
[例文＋下線]              ← 残る
──────────────
正解！
consolidate：統合した、固めた
例文訳：その会社は地域ごとの事務所を一つの本部に統合した。   ← 追加
出題から 4.2 秒で解答（前回までの平均 3.8 秒）
[語源 / 核心イメージ]
```

- 追加は `mode === "meaning"` かつ `item.exampleTranslation` があるときのみ
- 既存の要素（正誤見出し・`語句：意味`・応答時間・語源）の順序と文言は変えない

### 2.4 応答時間の扱い

例文を読む分、1問あたりの解答時間は伸びる。`avgMs` は学習進捗そのもの（SRSの判定にも使われる）なので
**リセットしない**。「前回までの平均」の比較は変更直後の数十問だけ意味が薄れるが、自然に新しい水準へ収束する。
この判断は本計画の既知の副作用として記録しておく。

## 3. スタイル（`static/styles.css` / `DESIGN.md`）

### 3.1 下線トークンの新設

DESIGN.md には現在、下線・傍線の規定がない（強調は反転タイルのみ）。新設する。

```css
:root { --rule-underline: 1.5px solid var(--ink); }

.exUnderline {
  border-bottom: var(--rule-underline);
  padding-bottom: 1px;   /* ベースラインから少し離す */
  font-style: normal;
}
```

- `.flashEx em` の既存指定（`border-bottom: 2px`）を `.exUnderline` に統合する。
  **フラッシュカード側の下線が 2px → 1.5px にわずかに細くなる**のが唯一の見た目の副作用
- 色は `--ink`（本文と同じ）。色だけに頼らず線で示すため WCAG 2.2「色以外の手段」を満たす
- スクリーンリーダー向けの補助テキストは**入れない**（決定事項）

### 3.2 出題部のレイアウト

```css
.askExampleLine { display: flex; align-items: flex-start; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.askExample { font-family: var(--serif); font-size: 20px; line-height: 1.8; max-inline-size: 46ch; margin: 0; }
```

- 現行 `.askWord` は 26px。英検1級の例文は20語前後で、スマホ幅（375px）では2〜3行になる。
  **20px＋行間1.8** で折り返し時も下線が各行に正しく付き、行同士が詰まらないようにする
- `.quizBox` の `padding` とアニメーションは現行のまま

### 3.3 DESIGN.md への追記

「機能色」節の近くに**下線（強調）**の項を追加し、`--rule-underline` の用途を「例文中の対象語句を示す唯一の手段」
として明記する。適用箇所は `.askExample` と `.flashEx` の2つだけ、と範囲も書く。

## 4. データ修正（分離句動詞5件）

### 4.1 対象と正本

`data/vocab_*.json` は生成物なので**直接編集しない**。それぞれの正本を直して再生成する。

| 語句 | 意味 | 正本 | ファイル |
| --- | --- | --- | --- |
| `cast down` | 落胆させる、意気消沈させる | 例文キュレーション | [scripts/curate_1_examples.py](../scripts/curate_1_examples.py) |
| `let down` | 失望させる | 模試3の生成 | [scripts/build_q1_mock_3_data.py](../scripts/build_q1_mock_3_data.py) |
| `feed on` | 〜を食べて生きる | 2級メタデータ | [scripts/q1_eiken2_metadata.py](../scripts/q1_eiken2_metadata.py) |
| `pull off` | うまくやり遂げる | 準1級 `EXAMPLE_OVERRIDES` | [scripts/q1_pre1_metadata.py](../scripts/q1_pre1_metadata.py) |
| `read into` | 〜を深読みする | 準1級 `EXAMPLE_OVERRIDES` | [scripts/q1_pre1_metadata.py](../scripts/q1_pre1_metadata.py) |

### 4.2 変更内容

| 語句 | 変更前 | 変更後 |
| --- | --- | --- |
| `cast down` | The rejection **cast her down**, but she soon tried again.<br>不合格の知らせで彼女は落胆したが、すぐにもう一度挑戦した。 | The rejection **cast down** her spirits, but she soon tried again.<br>不合格の知らせは彼女の気持ちを落ち込ませたが、すぐにもう一度挑戦した。 |
| `let down` | I promised that I would not **let my team down** during the crisis.<br>私は危機の間、チームを失望させないと約束した。 | I promised that I would never **let down** my team during the crisis.<br>私は危機の間、チームを決して失望させないと約束した。 |
| `feed on` | Giant pandas **feed mainly on** bamboo in their natural mountain habitat.<br>ジャイアントパンダは自然の山岳環境で主に竹を食べます。 | Giant pandas **feed on** bamboo in their natural mountain habitat.<br>ジャイアントパンダは自然の山岳環境で竹を食べます。 |
| `pull off` | It was a difficult project, but the team managed to **pull it off**.<br>難しいプロジェクトでしたが、チームはなんとかやり遂げました。 | It was a difficult project, but the team managed to **pull off** the launch.<br>難しいプロジェクトでしたが、チームはなんとか立ち上げをやり遂げました。 |
| `read into` | Don't **read too much into** his silence; he's probably just tired.<br>彼の沈黙を深読みしないでください。彼はおそらくただ疲れているだけだろう。 | Don't **read into** his silence; he's probably just tired.<br>彼の沈黙を深読みしないでください。彼はおそらくただ疲れているだけだろう。 |

`cast down her spirits` と `pull off the launch` は、承認いただいた案（`her hopes` / `a success`）から
英語としての自然さを優先して調整している。§9で最終確認する。

副作用として `let down` / `pull off` の**分離用法に触れる機会は失われる**が、目的語が代名詞でない場合は
非分離が普通なので、例文として不自然にはならない。

### 4.3 実行時の安全網

今後の問題セット追加で分離形が再び混入し得る。二重に備える。

1. **実行時フォールバック**: `exampleMatch()` が `null` のとき、その設問だけ現行の見出し語表示
   （`.askWordLine` ＋「次の語句の意味は？」）に戻す。例文枠は出さない。表示が壊れない
2. **機械検査**: §5 のスクリプトで `npm test` 時に不一致を検出して落とす

## 5. 検査（新規 `scripts/check-meaning-example-ui.cjs`）

`scripts/lib/app-source.cjs` の読み込みと `extractFunctionBody` を使う（AGENTS.md の規約）。
既存の `check-meaning-mission-ui.cjs` と同じ書き方に合わせる。

**データ側**

- `data/vocab_*.json` の全 `words` / `idioms` に `example` と `exampleTranslation` があること
- 出題形（`word` / `phrase`）が `example` 中に大文字小文字を無視して完全一致で現れること
- 不一致があればファイル名・語句・例文を挙げて失敗する

**UI側**（ソースのテキスト検査）

- `renderCheck` 本体に `下線部の意味として最も適当なものを選べ` が存在する
- `renderCheck` 本体が `mode === "meaning"` で分岐している（他モードに波及していないこと）
- `renderCheck` 本体に見出し語表示へのフォールバック経路が残っている
- `flashExampleRow` 本体が共通ヘルパー経由になっていて、`<em>` 直書きが残っていない
- CSS に `--rule-underline` と `.exUnderline` が存在し、`.flashEx em` の旧指定が残っていない

`package.json` の `test` スクリプト末尾に `node scripts/check-meaning-example-ui.cjs` を追加する。

## 6. 作業手順

1. `static/src/90-learn-flow.js` を編集（§2）
2. `static/styles.css` を編集（§3.1・3.2）
3. 例文の正本4スクリプトを修正（§4.2）し、該当する `build_*.py` を実行して `data/vocab_*.json` を再生成
4. 再生成後の差分が**5件の `example` / `exampleTranslation` だけ**であることを `git diff --stat` と目視で確認
5. `scripts/check-meaning-example-ui.cjs` を新規作成し、`package.json` に追加（§5）
6. `npm run build`（`static/mode-q1.js` を再生成）
7. `npm test`（生成物の鮮度検査＋全 `check-*.cjs`）
8. `index.html` の `static/mode-q1.js?v=` と `static/styles.css?v=` を上げる
9. `DESIGN.md` に下線トークンを追記（§3.3）
10. 実ブラウザ検証（§7）
11. コミット → `main` へ push → GitHub Pages のデプロイ完了を確認 → 公開URLで再検証（§7.3）

## 7. 検証

### 7.1 機械検査

`npm test`（生成物の鮮度・`node --check`・既存24本の `check-*.cjs`・新規1本）

### 7.2 実ブラウザ（ローカル）

意味だけ復習を実際に開始して確認する。

| # | 確認項目 |
| --- | --- |
| 1 | 例文が表示され、対象語句にだけ下線が引かれている |
| 2 | ラベルが「下線部の意味として最も適当なものを選べ」になっている |
| 3 | 見出し語の単独表示が消えている |
| 4 | 音声ボタンが機能する |
| 5 | 正答・誤答の両方で、フィードバックに例文訳が出る |
| 6 | 例文が解答後も下線付きで残っている |
| 7 | 誤答後の見直しカードの下線が設問と同じ見た目 |
| 8 | 通常学習・最終チェックの意味確認が**現行のまま**（見出し語表示） |
| 9 | 375px 幅で例文が2〜3行に折り返しても、各行に下線が正しく付く |
| 10 | キーボード（数字キー・Tab・Enter）で選択肢を操作できる |
| 11 | コンソールエラーがゼロ |

### 7.3 公開後

GitHub Pages のデプロイ完了後、公開URLで配信中の `mode-q1.js` / `styles.css` が新しい `?v=` を返すこと、
および §7.2 の #1・#2・#5 を再確認する。push 前に `gh api` で Pages の配信ブランチ設定を確認しておく。

## 8. 決定事項（ヒアリング結果）

| # | 論点 | 決定 |
| --- | --- | --- |
| 1 | 見出し語を残すか | 残さない。例文＋下線部のみ |
| 2 | 適用範囲 | **意味だけ復習(`meaning`)のみ**。learn / final は現行維持 |
| 3 | 例文訳の表示 | 解答前は出さず、フィードバックで表示 |
| 4 | 不一致5件の扱い | 例文を書き換えて全件一致させる（正本スクリプト側） |
| 5 | 設問文 | 「下線部の意味として最も適当なものを選べ」 |
| 6 | 音声ボタン | 例文ブロックの脇に維持 |
| 7 | 出典表示 | 出さない（品詞も出さない） |
| 8 | 下線の見た目 | `border-bottom` 1.5px 実線 `--ink`。補助テキストなし |
| 9 | 見直し画面 | 同じ下線スタイルに統一（フラッシュカード全体に波及） |
| 10 | 解答後の例文 | 下線付きのまま残す |
| 11 | 4択のダミー | 変更しない |
| 12 | 応答時間の平均 | リセットしない |
| 13 | 作業範囲 | 実装・検証・実ブラウザ確認・コミット・push・デプロイまで |

## 9. 実装前の最終確認（2件）

§4.2 の例文2件を、承認済みの案から英語としての自然さを優先して調整している。

| 語句 | 承認済みの案 | 本計画での案 | 理由 |
| --- | --- | --- | --- |
| `cast down` | cast down **her hopes** | cast down **her spirits** | `cast down` は「人・気持ちを落ち込ませる」。`hopes` を目的語に取る組み合わせは英語として不自然 |
| `pull off` | pull off **a success** | pull off **the launch** | `pull off` は「困難なことをやり遂げる」で、`a success` は同語反復に近い。具体物を目的語に置く方が自然 |

この2件を承認済みの案に戻す場合はその旨をご指示ください。指示がなければ本計画の案で実装する。

## 10. 想定される副作用

| 副作用 | 影響 | 対応 |
| --- | --- | --- |
| フラッシュカードの下線が 2px → 1.5px | 全級・全モードの暗記カードと見直しカード | 意図した統一。DESIGN.md に記録 |
| 5語の例文と訳が変わる | 該当5語の学習体験 | §4.2 で承認済み |
| 例文音声（TTS）を持つ場合、5語分が古い例文のまま | 例文読み上げがあれば不整合 | 手順3の前に `generate_tts_1.py` 系が例文音声を生成しているか確認。生成していれば該当分を再生成 |
| 1問あたりの解答時間が伸び、`avgMs` の水準が変わる | 「前回までの平均」の比較が数十問ぶん鈍る | リセットせず自然収束を待つ（§2.4） |
