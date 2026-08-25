# 暗記カード 導線・可読性の修正計画

> 対象: `eiken-q1-practice` の暗記カード画面（STEP 1 flash）。
> 目的: UX摩擦監査・デザイン監査（2026-08-25）の指摘のうち、**学習設計に踏み込まずに直せる範囲**を実装する。
> 関連: [FLASHCARD_MEASUREMENT_PLAN.md](FLASHCARD_MEASUREMENT_PLAN.md)（合格基準の正本）/ [HOME_NEXT_ACTION_FIX_PLAN.md](HOME_NEXT_ACTION_FIX_PLAN.md) / [../DESIGN.md](../DESIGN.md)
> 状態: 計画（未着手）。作成日 2026-08-25。

## 1. 直す摩擦

| # | 摩擦 | 実測（375px・n=20） |
|---|---|---|
| ① | 主操作「次のカード」が常に画面外にあり、位置も一定しない | M1 = **+4 〜 +720px**。中間ブロックなし4〜26px、語源・核心イメージあり239〜720px |
| ①' | 送り後にスクロール位置が持ち越され、**新しい語の見出しを見ないまま進む** | M12 = 語源ありのカードで **false**（見出し語が画面外・語源の途中が表示される） |
| ② | 覚える対象の「意味」が視覚的に弱い | M5 = 19px / 400 / 見出し語比 **0.63**。意味はカードの7〜9%、語源・核心イメージは42〜64% |
| ③ | カード送りに450msの無反応窓があり、何も起きない | M11 = **false**（ガード中に見た目が変わらない） |
| ④ | 1280pxで本文の行幅が長すぎる | M6 = 意味46.9em / 例文59.5em / 例文訳68.6em / パネル本文81.1em、`max-width` 指定なし |
| ⑤ | カード進捗が二重表示・単位違い・操作の後 | 上部「1/4語」（`.sessionStickyFlash`）と下部「カード 1 / 4」（`.cardCounter`）。後者は操作ボタンの下、間隔10px |

## 2. 決定事項

| 項目 | 決定 | 却下した案 |
|---|---|---|
| カードの長さ | **維持する。導線だけ直す** | 語源・核心イメージの既定折りたたみ／意味→例文→語源への順序変更。どちらも学習設計に関わり、監査で「検証後」に分類した範囲 |
| 送りボタンの位置 | **下部の固定バー** | 上部 `.sessionStickyNav` への併設（スマホで親指から遠く、「戻る」と「進む」が同じ帯に並ぶ） |
| 同時に直す範囲 | ②意味のタイポ／③押下フィードバック／④行幅上限／⑤カウンタ一本化 | — |

**M1とM12は別問題**である。ボタンを固定しても見出し語を見ないまま進める状態は消えず、先頭スクロールだけでは押すためのスクロールが残る。**両方を実装しないと①は解決しない。**

## 3. 変更①: 送り導線（固定バー＋先頭スクロール）

### 3-1. 固定バー `static/mode-q1.js`

[renderFlash()](../static/mode-q1.js) の `.actions.flashNav` を、画面下部に固定する `.sessionActionBar` で包む。

- 構成は左から「← 前のカード」「カード n / 4」「次のカード →」。**カウンタをバーの中央へ入れる**ことで⑤も同時に解消する（現在地と操作が同じ帯に収まる）。
- バーは `.wrap` と同じ幅（最大960px）で中央寄せにし、全幅ベタ塗りにしない。
- 面は Parchment、上辺のみ hairline。影は使わない（DESIGN.mdの深度規範に従う）。
- **flashステージのみ**に出す。check / practice / wrongReview / done は現状のまま。混在する見た目になるため、5章に整合の注記を置く。

### 3-2. 本文がバーに隠れないようにする `static/styles.css`

- `#sessionPanel` に flash ステージ用のクラス（例 `.hasActionBar`）を付け、`padding-bottom: calc(76px + env(safe-area-inset-bottom))` を与える。
- バー自体も `padding-bottom: max(12px, env(safe-area-inset-bottom))`（iOSのホームインジケータ回避）。
- `z-index` は上部 `.sessionStickyNav` と同じ 6。

### 3-3. 1行に収める

現在の `.flashNav .cta { min-width: min(100%, 220px) }` は375pxで折り返し、ナビが115px高になる（実測）。固定バーでこの高さは重い。

- `.flashNav .cta` の `min-width` を `min(100%, 160px)` に下げ、375pxで **prev 132px＋gap＋next** が1行に収まるようにする。
- `.flashNav` の `gap` を 24px → 12px（DESIGN.md「ボタン・選択肢の gap は 12px に統一」に寄せる）。
- 両ボタンとも最小高さ44pxを維持する。

### 3-4. 送り後に先頭へスクロール

```
scrollFlashCardIntoView():
  target = .flash の絶対上端 − .sessionStickyNav の高さ − 8px
  window.scrollTo({ top: max(0, target), behavior: "auto" })
```

- 呼び出しは [renderFlash()](../static/mode-q1.js) の「前のカード」「次のカード」の `onclick` の中、`renderSession()` の**後**。`renderSession()` 自体には入れない（check / practice / done まで巻き込むため）。
- `behavior: "auto"`（即時）にする。smoothだと測定のサンプリング時刻と実際の位置がずれ、M12の判定が不安定になる。
- 上部の sticky バーの高さを引くのは、`.flash` の上端をぴったり合わせるとカード上部がバーの下に隠れるため。

## 4. 変更②〜⑤

### ② 意味の強調 `static/styles.css`

```
.flashMeaning { font-size: 22px; font-weight: 600; }   /* 現在: 19px / 400 */
```

見出し語比は 22 ÷ 30 = **0.73**（基準0.70以上）。データ・順序・行構成は変えない。

**リスク**: 日本語はCormorant Garamondではなく明朝系へフォールバックするため、600が合成ボールドになる環境がある。実機で不自然なら **24px / 500** へ切り替える（この場合も比は0.80で基準を満たす）。

### ③ ガード中の押下フィードバック `static/mode-q1.js` / `static/styles.css`

- [renderFlash()](../static/mode-q1.js) でボタンを組み立てるとき `flashNavLocked()` を見て、真なら `class` に `isGuarded` を足し `aria-disabled="true"` を付ける。残り時間後に `setTimeout` で両方を外す。
- **`disabled` 属性は使わない**。フォーカスが外れ、キーボード操作が途切れるため。
- CSS: `.flashNav .isGuarded { opacity: .6; cursor: default; }`。450msの間だけ「受付済み」に見せる。
- ガード自体（`FLASH_NAV_GUARD_MS = 450`、誤ダブルタップ防止）は残す。

### ④ 本文の行幅上限 `static/styles.css`

| 対象 | 上限 | 根拠 |
|---|---|---|
| `.flashMeaning` / `.flashExampleTranslation` / `.particlePanel p` | `max-inline-size: 34em` | 日本語本文の目安30〜40em |
| `.flashEx` | `max-inline-size: 70ch` | ラテン本文の目安45〜75ch |

375pxでは現状すべて上限内（意味16.2em / 例文20.5em・41ch / 訳23.6em / パネル27.9em）なので、**モバイルの見た目は変わらない**。

### ⑤ カウンタの一本化 `static/mode-q1.js`

- 表記を「カード n / 4」に統一する（「語」と「カード」の混在をやめる）。
- 置き場所は 3-1 の固定バー中央。
- [sessionStickyNav()](../static/mode-q1.js) の `flashLabel`（`.sessionStickyFlash`）と、`renderFlash()` 末尾の `.cardCounter` を**削除する**。固定バーが常に見えるため、上部の重複は不要になる。
- `.sessionStickyFlash` はflashステージ専用なので、他ステージへの影響はない。CSSの当該セレクタも整理する。

## 5. DESIGN.md への追記

- **セッション操作バー（`.sessionActionBar`）**: 暗記カードの送り操作を画面下部に固定する。Parchment地＋上辺hairline、影なし、`.wrap` と同じ最大幅で中央寄せ。左に副操作、中央に現在地、右に主操作を置き、1行に収める。flashステージ専用であり、他ステージはカード末尾の `.actions` を使う。
- **暗記カードの意味（`.flashMeaning`）**: 覚える対象として、見出し語に次ぐ2番目の強さを持たせる。見出し語に対する文字サイズ比は0.70以上を保つ。
- 本文の行幅上限（日本語34em／ラテン70ch）をタイポグラフィ節へ追記する。

## 6. 検証

### 6-1. 実測（正本: [FLASHCARD_MEASUREMENT_PLAN.md](FLASHCARD_MEASUREMENT_PLAN.md)）

**実装前にベースラインを取る。** 順序は Before測定 → 実装 → After測定。

```
主標本: 1級2026-1 の全22設問×4枚 = 88枚 / 375px と 1280px
補助:   320px・768px は代表6枚
```

| 指摘 | 指標 | 合格基準 |
|---|---|---|
| ① | M1 | 375pxの全88枚で `≤ 0` |
| ① | M2 | `≤ 8px` |
| ①' | M12 | 送り後の全カードで `true` |
| ① | 追加確認 | `.flashExampleTranslation` の下端が固定バー上端より上 |
| ② | M5 | `font-size ≥ 22px` かつ `font-weight ≥ 600` かつ `vsWord ≥ 0.70` |
| ③ | M11 | 全カードで `true` |
| ④ | M6 | 日本語本文 `em ≤ 40`、ラテン本文 `chApprox ≤ 75`（1280px） |
| ⑤ | 追加確認 | 画面内の「カード n / 4」が1箇所のみ。`.sessionStickyFlash` と `.cardCounter` が存在しない |
| 回帰 | M8 / M9 / M10 | `1` / `0件` / `false` |
| 回帰 | M3 / M4 | **変化しない**（カードの長さと構成には触れないため） |

M3・M4が動いた場合は、意図せずカードの構成を変えたということなので原因を特定する。

### 6-2. 自動検証 `scripts/check-flashcard-nav-ui.cjs`（新規）

既存の `.cjs` と同じソース契約テスト。`package.json` の `test` 連鎖へ追加する。

1. `renderFlash` が `scrollFlashCardIntoView` を「前のカード」「次のカード」の両方で呼ぶこと。
2. `renderSession` は `scrollFlashCardIntoView` を呼ばないこと（他ステージへの巻き込み防止）。
3. `renderFlash` が `flashNavLocked()` を見て `isGuarded` と `aria-disabled` を付けること。
4. ガード表現に `disabled` 属性を使っていないこと。
5. `sessionStickyNav` に `sessionStickyFlash` が無いこと、`renderFlash` に `cardCounter` が無いこと（⑤の回帰）。
6. `styles.css` に `.sessionActionBar` / `.flashNav .isGuarded` / `max-inline-size` の規則があること。
7. `.flashMeaning` の `font-size` が22px以上であること。

### 6-3. 手動確認

- 320 / 375 / 768 / 1280px で、固定バーが例文訳を隠さないこと、横スクロールがないこと。
- キーボードでprev→カウンタを飛ばしてnextへタブ移動できること。ガード中もフォーカスが外れないこと。
- 途中再開（`resume` の `flashIdx`）が従来どおり復元されること。
- コンソールエラーなし。

## 7. 完了条件

1. `npm test`（新規 `check-flashcard-nav-ui.cjs` を含む）と `py -3 scripts/check_q1_data.py` が通る。
2. 6-1の合格基準を、After測定のJSONで全項目満たす。満たさない項目は値のまま報告する。
3. `DESIGN.md` に5章の3点が追記されている。
4. Before / After のJSONが `docs/measurements/` に残っている。

## 8. やらないこと

- 語源・核心イメージの折りたたみ、順序変更、削除。カードの長さ（M3）と構成比（M4）は**変えない**。
- check / practice / wrongReview / done ステージの操作配置。今回はflashのみ。
- `FLASH_NAV_GUARD_MS` の値そのものの変更。
- 保存データ形式の変更。`resume` の `flashIdx` の意味は変えない。
- 4枚のカード間を直接移動する導線（監査の「検証後8」）。

## 9. リスク・未確認事項

- **固定バーがflashステージだけに出る**ため、STEP2以降と操作の位置が変わる。反復原則の観点では一貫性が下がる。今回はflash（1設問あたり4枚＝最も反復回数が多い画面）の改善を優先するが、**他ステージへ広げるかは実測後に判断する**。
- 意味の600ウェイトが日本語で合成ボールドになる環境がある（4章②のリスク）。実機確認が要る。
- `env(safe-area-inset-bottom)` の効きは実機のiOS Safariでしか確認できない。ブラウザの端末エミュレーションでは0として扱われる。
- 固定バー導入で画面下部の実効表示領域が約76px減る。カード本文の可読行数が減る影響は未測定。
- Before測定は88枚×2幅で約4分かかる。測定は `resume` を書き換えるため、[FLASHCARD_MEASUREMENT_PLAN.md](FLASHCARD_MEASUREMENT_PLAN.md) 4-1の退避・復元を必ず実行する。
