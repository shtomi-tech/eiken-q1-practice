# HOME_LAYOUT_UNIFICATION_PLAN — ホーム画面の並び順統一

> 対象: `kobun-vocab-learning` と `eiken-q1-practice` の2リポジトリ。
> 目的: 両アプリのホーム画面の要素順を、同一の基準で並べ直す。
> 状態: 計画（未着手）。作成日 2026-08-21。

## 1. 並び順の基準

**スコープの広い順 × 決定コストの低い順。** ホームが上から順に次の問いへ答える構成にする。

| 層 | 答える問い | 要素 |
|---|---|---|
| A | これは何のアプリか | 導入（初回訪問時のみ表示） |
| B | 次に何をすればいいか | 主CTA1つ＋途中保存通知＋進捗指標 |
| C | どこまで来たか | 語彙目標カード |
| D | 他に今日できることは | 意味だけ復習（範囲横断） |
| E | 別の範囲をやりたい | 学習セット／問題セットの選択 |
| F | 特定の箇所から始めたい | 範囲内の単位一覧・参照一覧 |
| G | 記録と設定を触りたい | 履歴・進捗リセット・級変更 |

- **E と F は必ず隣接させる。** 「範囲を選ぶ → その中の単位を選ぶ」というズームの順序にする。
- **D は E より上に置く。** 意味だけ復習はセット／級をまたぐプールが対象で、範囲選択より上位のため。eiken では主CTAが `null` になり間隔復習が実質の主導線になる分岐があり、実利もある。
- **進捗の数値（stats）と語彙目標カードの間に他要素を挟まない。** kobun の `.stats` は主カード末尾に据え置き、直後に語彙目標カードを置くことでC層を成立させる（statsのカード移設はしない）。
- **一覧はデータ順・manifest順を維持し、進捗で並べ替えない。**

## 2. 目標の並び

| 層 | kobun-vocab-learning | eiken-q1-practice |
|---|---|---|
| A | hero（初回のみ）※フェーズ4で新設 | hero（初回のみ・現状維持） |
| B | 主カード（label / h2 / recommend / stats） | 今日の学習カード |
| C | 語彙目標カード | 語彙目標カード |
| D | 意味だけ復習 | 意味だけ復習 |
| E | 学習セット選択（独立カード化） | 問題セット選択 |
| F | 学習ブロックマップ → 単語一覧 | 問題一覧 |
| G | 履歴 → その他 | その他（リセット＋級変更） |

## 3. フェーズ1: eiken-q1-practice

1. `static/mode-q1.js` `renderHomeContent()`: `home.appendChild(el("section", { class: "card" }, datasetPicker()))` を `meaningMission(...)` の appendChild の**後ろ**へ移動する。`meaningMission` は `if (grade)` ガード内、`datasetPicker` はガード外。ガード構造は変えず順序だけ入れ替える。
2. 「その他」カード（`if (!sharedMode())`）と「級を変更」カード（`if (!URLSearchParams.has("g"))`）を1枚のカードへ統合する。
   - **条件は保持する。** 進捗リセットは `!sharedMode()` のときのみ、級変更は `?g` 無しのときのみ内容に含める。
   - 両方とも該当しない場合はカード自体を描画しない（現状 sharedMode では「その他」だけ消えて級変更は残るため、統合で級変更を巻き添えに消さない）。
3. `npm test` を実行する。`scripts/check-meaning-mission-ui.cjs` は `home.appendChild(meaningMission(` の存在のみを検査し順序は見ないため、そのまま通る見込み。

## 4. フェーズ2: kobun-vocab-learning

4. `static/mode-vocab.js` `renderHome()`: 主カード生成の引数から `setPicker()` を外す。主カードの `h2` が現在セット名（`state.set.meta.title`）のため、代替hintの追加は不要。
5. `home.appendChild` の順序を **語彙目標 → 意味だけ復習 → セット選択 → ブロックマップ → 単語一覧 → 履歴 → その他** に組み替える。セット選択は eiken と同じく `el("section", { class: "card" }, setPicker())` で包む。
6. `static/styles.css`: `.setPicker { margin-bottom: 20px }` は主カード内前提のため、カード直下では0にする（`.card > .setPicker { margin-bottom: 0 }` を追加）。
7. `showAllSetsHome()` に `picker.scrollIntoView({ block: "start" })` を追加する。完了画面の「全セットの学習状況を見る」から呼ばれるが、ピッカーがページ下方へ移動するため、これを入れないと押しても画面が変わったように見えない。
8. **`scripts/check-vocab-goal-ui.cjs` が落ちる。** 「ブロックマップ < 語彙目標カード」を assert しているので、新規定に合わせて不等号を反転する（語彙目標 < ブロックマップ）。`check-unit-map-ui.cjs` は存在チェックのみで通過する。
9. `node --check static/mode-vocab.js` と `node scripts/check-vocab-goal-ui.cjs` / `check-unit-map-ui.cjs` / `check-set-progress.cjs` / `check-srs.cjs` を実行する。

## 5. フェーズ3: DESIGN.md（正本の更新。コード変更と同じコミットに含める）

10. kobun `DESIGN.md`「学習ブロックマップ」節の「ホームの主カード直下に表示する」と、「語彙目標カード」節の「ホームでの位置は『主カード → 学習ブロックマップ → 語彙目標カード → 意味だけ復習』とし、学習ブロックマップが主カード直下という規定を崩さない」を、本計画の順序へ改訂する。
11. 両 `DESIGN.md` に共通文言で「ホームの層構造」節を追加する（第1章の基準と第2章の表）。あわせて「一覧はデータ順・manifest順を維持し、進捗で並べ替えない」を共通規則として明記する（kobun のセット一覧節に既出、eiken へは新規）。

## 6. フェーズ4: A層の統一

12. kobun に初回訪問時のみの hero カードを追加し、主カードの常設 `lead`（「4語ずつ、覚える → 意味を確かめる、の順に進めてから文中問題を解きます」）をそこへ移す。判定条件は eiken と同じく「まだ何も学習していない」（kobun では `learned === 0`）。
13. 2回目以降は主カードから説明文が消える。B層は label / h2 / recommend / stats のみになる。
14. eiken 側は現状の hero が既にこの条件のため変更しない。

## 7. 検証

- 各リポジトリの既存 check スクリプトと `node --check`（フェーズ1・2・4の各末尾で実行）。
- ブラウザ確認は各アプリ1回ずつ。ホーム表示、コンソールエラー、kobun の「全セットの学習状況を見る」導線（項目7の実挙動）、フェーズ4の hero が初回のみ表示されること。網羅的な操作確認は行わない。
- デプロイは行わない（eiken の netlify 反映は別途指示があれば実施）。

## 8. 想定される破壊的変更・注意点

- kobun の `check-vocab-goal-ui.cjs` は**意図的に**落とし、規定変更に合わせて更新する（項目8）。テストの無効化ではなく、新しい規定への書き換えとして行う。
- eiken の「その他」統合では sharedMode と `?g` の2条件を混同しない（項目2）。
- 保存データ・進捗キー・URLパラメータの仕様は変更しない。本計画はホームの描画順とDESIGN.mdのみを対象とする。
