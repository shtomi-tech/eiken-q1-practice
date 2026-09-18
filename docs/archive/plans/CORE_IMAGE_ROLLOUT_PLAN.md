# 核心イメージを全セットへ展開する計画

対象: `data/vocab_*.json`（配信中の15セット）/ `data/particle_images.json` / `scripts/`
関連: [CORE_IMAGE_PLAN.md](CORE_IMAGE_PLAN.md)（導入）/ [CORE_IMAGE_SENSE_PLAN.md](CORE_IMAGE_SENSE_PLAN.md)（用法別）/ [CORE_IMAGE_SENSE_FIX_PLAN.md](CORE_IMAGE_SENSE_FIX_PLAN.md)
状態: 未着手（`fa5a795` までで仕組みは完成・公開済み。データが `vocab_1_mock-1.json` の16件しか無い）

## 0. 対象の実数

`data/manifest.json` に載っている19セットのうち、熟語（`idioms[]`）を持つのは**15セット・292件（ユニーク285件）**。準1級と国際医療福祉大学のセットは熟語0件、テーマ別5セット（296件）は**manifestから外れており配信されていない**ため対象外。

| 級 | ユニーク熟語 | 済 | 残 |
| --- | --- | --- | --- |
| 1級（過去問3＋模試5） | 125 | 16（mock-1） | 109 |
| 2級（3セット） | 84 | 0 | 84 |
| 準2級（4セット） | 76 | 0 | 76 |
| **計** | **285** | **16** | **269** |

## 1. 型で3つに切り分ける

全部に同じ形を当てない。**当たらないものには付けない**（`coreImage` は任意フィールド）。

| 型 | 件数 | 方針 |
| --- | --- | --- |
| A: 動詞＋不変化詞 | 220 | 本命。`chain` ＋ `particle` ＋ `particleSense`。例: `buckle down` `branch off` `pony up` |
| B: 前置詞句・定型表現 | 38 | `chain` は組めるが不変化詞パネルは出さない（`particle` を付けない）。例: `in search of`＝in（〜の中）＋search（探す）＋of（〜を）→ 探している最中で |
| C: それ以外 | 27 | 原則付けない。接続表現（`provided that` `rather than` `even though`）や動詞＋名詞（`shake hands` `give way`）は連鎖がこじつけになる。どうしても示したい成り立ちは既存の `etymology` フィールドを使う（単語と同じ枠で表示される） |

Cを無理に埋めないことを**明示的な合格条件**とする。件数の消化を目的にしない。

## 2. 辞書（`particle_images.json`）を先に広げる

Aの220件が使う不変化詞は次のとおり（出現数）。

```
out 36 / up 32 / off 27 / on 18 / in 17 / down 13 / over 8 / away 7 /
back 4 / into 4 / across 2 / together 2 / along 2 /
behind 1 / upon 1 / under 1 / around 1 / forward 1
```

- 現在 `senses` を持つのは `out`(5) `up`(2) `off`(2) `on`(2) `up to`(2) のみ。**`in` `down` `over` `away` `back` `into` は未整備**。
- 1セット内で同じ不変化詞が最大6件（`vocab_1_2025-2.json` の `off`）。用法に割れば1用法あたり2〜3件に収まり、既存の検査（同一 sense を `n` 件が参照するなら仲間例は `min(3+(n-1), 6)` 件以上）を満たせる。
- 出現1〜2件の不変化詞（`behind` `upon` `under` `around` `forward` `across` `along` `together`）は**用法分割せず**、トップレベル `siblings` 3件だけを用意する。分割は「同一セット内で複数回出る」ものに限る。

辞書の拡張は**データ投入より先に、まとめて1コミット**で行う。

## 3. バッチ運用

**1セット＝1バッチ＝1コミット**。1バッチは16〜28件で、`vocab_1_mock-1.json` の16件と同じ粒度に収まる。

順序（学習者数と型の素直さで決める）。**バッチ0（7章のキャッシュ制御）を最初に行う。**

1. 1級 模試 mock-2〜mock-5（各16件・Aが多い）
2. 1級 過去問 2025-2 / 2025-3 / 2026-1（各16件）
3. 2級 3セット（各28件・Bが多め）
4. 準2級 4セット（各20件）

各バッチで辞書に用法追加が必要になったら、そのバッチのコミットに含める（辞書だけ先行して肥大させない）。

## 4. 手順（1バッチあたり）

1. `scripts/build_core_image_stub.py`（新規）を実行し、対象セットの未着手熟語について次を出力する。
   - `phrase` / `meaning` / `example`
   - 型の自動判定（A/B/C の候補。**最終判断は人**）
   - 検出した不変化詞と、辞書にある用法（id・label・仲間例）の一覧
   - `chain` を空にした雛形JSON
   これは**下書き支援であって生成ではない**。語義の判断を機械に委ねない。
2. 雛形を埋める。`chain` は2〜5段、構成語は**原形・小文字**（`scraped together` → `scrape` / `together`）。最終段は `meaning` の中心義とそろえる。
3. `particleSense` は、**連鎖中のその不変化詞の `gloss` と一致する用法**を選ぶ。一致する用法が無ければ辞書に用法を足す（仲間例4〜5件）。
4. `npm test` を通す。
5. 表示シミュレーションで、そのセット内の仲間例が全カードで異なることを確認する。
6. コミット→push→公開URLで配信データを確認。

## 5. 品質の線引き

- 語義の根拠は既存の `meaning` と `example` を第一とする。辞書の記述に合わせて `meaning` を書き換えない。
- **迷ったら付けない**。連鎖が比喩の飛躍でしか成立しないもの、構成語の語義が熟語の意味そのままになる循環（`eke out` で一度起きた）は不可。
- 仲間例は英検1級レベルに寄せず、**用法のイメージが立つ平易な熟語**を選ぶ。仲間例に対象熟語自身を入れない（検査で落ちる）。
- 未着手のまま残した熟語は、バッチごとに件数と理由を報告する。

## 6. 検査の拡張

`scripts/check-core-image-data.cjs` に追加する。

- **進捗の可視化**: 配信対象セットごとに「熟語数 / `coreImage` 付与数」を出力する（現在は総数のみ）。展開が進んでいるか、どのセットが未着手かがテスト出力で分かる。
- **移行漏れの検出強化**: 同一セット内に同じ `phrase` の熟語が複数ある場合、`coreImage` の有無が食い違わないこと。
- 既存の契約検査（`particleSense` 必須・プール件数下限・自己参照禁止・連鎖の構造）はそのまま適用される。**新規セットの投入時に自動で効く**ため、バッチごとの追加検査は不要。

## 7. 先行作業: 語彙データのキャッシュ制御をそろえる（バッチ0）

`static/mode-q1.js:1146` の `fetch(current.vocabUrl)` には**キャッシュ制御もバージョンクエリも無い**。`manifest.json` と `lemmas.json` は `cache: "no-store"` だが、`vocab_*.json` / `questions_*.json` は素の fetch であり、ブラウザのHTTPキャッシュから古いデータが返る可能性がある。今回の展開は**データだけを15回更新する**ため、反映されない端末が出ても検知できない。

**バッチ1に入る前に、単独のコミットとして次を入れる。**

```js
const [vocab, qs] = await Promise.all([
  fetch(current.vocabUrl, { cache: "no-store" }).then((r) => r.json()),
  fetch(current.questionsUrl, { cache: "no-store" }).then((r) => r.json()),
]);
```

- `loadPooledItems()` の `fetch(DATASETS[id].vocabUrl)`（`static/mode-q1.js:712`）も同じ扱いにする。間隔復習は級内の全セットを読むため、ここが古いと通常学習と表示がズレる。
- 対象JSONは1セットあたり数十KB。毎回取得になるが、既に `manifest.json`・`lemmas.json`・`particle_images.json` が `no-store` で動いている実績があり、体感差は無いと見込む。
- `index.html` のキャッシュバスターを `mode-q1.js?v=1.2.0` に上げる（`static/mode-q1.js` を変更するため）。
- 検証: 公開後に `vocab_1_mock-1.json` を1文字だけ変えて配信し、リロードのみで反映されることを確認してから元に戻す。あるいはDevToolsのNetworkで当該JSONが `200`（`from disk cache` でない）ことを確認する。

この1コミットが済むまで、データバッチの「公開URLで確認」は信用しない。

## 8. 非対象・完了条件

**非対象**: テーマ別5セット（manifest外）、準1級・国際医療福祉大学（熟語0件）、単語（`words[]`）への展開、`coreImage` の自動生成、UIの追加変更。

**完了条件**:
- バッチ0（`vocab_*.json` / `questions_*.json` の `cache: "no-store"` 統一）が公開済みで、データ更新がリロードだけで反映されることを確認済み
- 配信中15セットのA型220件に `coreImage` と `particleSense` が入っている
- B型38件は連鎖のみ、C型27件は未付与（＋理由を記録）
- `npm test` が通り、各セットで仲間例の重複が無い
- 各バッチが公開URLで確認済み

全体でバッチ0＋15バッチ。1バッチあたり16〜28件の語義判断が中心で、**機械化できるのは雛形出力と検査だけ**である点を前提に見積もる。
