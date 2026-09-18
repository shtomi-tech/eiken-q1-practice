# 不変化詞パネル（sense分割）修正計画

対象: `data/particle_images.json` / `data/vocab_1_mock-1.json` / `scripts/check-core-image-data.cjs` / `static/mode-q1.js`
関連: [CORE_IMAGE_SENSE_PLAN.md](CORE_IMAGE_SENSE_PLAN.md)（実装計画）/ [CORE_IMAGE_PLAN.md](CORE_IMAGE_PLAN.md)
状態: 未着手。sense分割の実装は**作業ツリーに未コミットで存在**（公開はまだ `eb7535a` の状態）

## 0. 現状の判定

sense分割の実装自体は計画どおりで、`npm test` は全項目 OK。16枚すべてが異なる仲間例になり、決定性（同じカードは常に同じ3件）も `loadData` / `loadPooledItems` の両経路で成立している。

**壊れているのは用法の割り当て2件と、検査スクリプトの作りである。**

| # | 症状 | 重大度 |
| --- | --- | --- |
| A | `Snap out of` に `out/social`（こもらずに外へ出る）を割り当て、`stay out / come out / go out` が出る。この熟語は「気分・状態から抜け出す」で、連鎖も「停滞した状態の外へぱっと出る」。物理的な外出の仲間とは別種 | 高（説明が誤り） |
| B | `bought off` に `off/pull-away` を割り当て、`drive off / fend off / ward off` が出る。これらは「自分に迫るものを追い払う」で、buy off の「相手に働きかけて手を引かせる」とは向きが違う | 中 |
| C | `check-core-image-data.cjs` の `expectedSenses` が phrase→sense の対応表を**スクリプト側に複製**している。A・Bを直すと検査も同時に直す必要があり、他の `check-*.cjs`（構造だけを見る）と性格が異なる | 中（保守性） |
| D | `coreImage.siblings`（例外上書き）は `if (particle && …)` の中でしか描画されず、辞書に無い不変化詞では上書きが効かない | 低（現データ未使用） |

公開中の版にはA・Bは含まれていない（sense分割自体が未公開）ため、**配信を止める必要はない**。未コミットの実装を直してから1本にまとめる。

## 1. A: `out` に「状態の外へ出る」用法を足す

`data/particle_images.json` の `out.senses` に追加する。

```json
{
  "id": "escape",
  "label": "状態の外へ出る",
  "siblings": [
    { "phrase": "get out of", "gloss": "抜け出す" },
    { "phrase": "grow out of", "gloss": "成長して卒業する" },
    { "phrase": "talk out of", "gloss": "説得してやめさせる" },
    { "phrase": "break out of", "gloss": "打ち破って抜け出す" }
  ]
}
```

- `Snap out of` の `particleSense` を `social` → `escape` に変更する。
- 仲間例が `out of` 型でそろうのは意図的。`Snap out of` 自身が `out of` 型であり、「何の状態から出るか」を取る形が共通している。
- `social` は `hanging out` の1件だけになる（プール5件・slot 0 で `go out / eat out / ask out`）。表示は変わらない。

## 2. B: `off/pull-away` を「手を引かせる」側に寄せる

現状の4件（`drive off` `fend off` `ward off` `scare off`）は「自分に迫るものを追い払う」で一貫しており、**それ自体は正しい束**である。`bought off` がその束に属していないことが問題。

方針（**要判断**）:

| 案 | 内容 | 備考 |
| --- | --- | --- |
| B-1（推奨） | `pull-away` の label を「働きかけて手を引かせる」に改め、siblings を `pay off=金を渡して黙らせる` / `call off=中止させる` / `warn off=警告して手を引かせる` / `put off=思いとどまらせる` に差し替える | 追い払い系の束は今回のセットでは誰も参照しないため、データを増やさない |
| B-2 | 追い払い系を `repel` として残し、`deter`（手を引かせる）を新設して `bought off` をそちらへ移す | 将来 `drive off` 系の熟語が来たとき使えるが、当面は未参照の sense が残る |

`pay off` は buy off とほぼ同義の口語であり、仲間例として最も近い。ただし「賄賂」の含意が語義の中心かは辞書により振れるため、**gloss は「金を渡して黙らせる」と限定して書き、断定的な語義説明はしない**。

## 3. C: 検査を「割当表の複製」から契約検査へ

`expectedSenses` を**削除**し、代わりに次を検査する。

1. **移行漏れの検出**: `senses` を持つ不変化詞を参照する熟語は `particleSense` が必須。
   （現状 `hanging out` 等はすべて設定済みだが、今後 `out` の熟語を追加したとき無指定だとフォールバック表示になり、気づけない）
2. **変化の担保**: 同一 (`particle`, `particleSense`) を参照する熟語が同一データセット内に `n` 件あるとき、その sense の `siblings` は **`min(3 + (n - 1), 6)` 件以上**必要。
   各カードが少なくとも1件は他と違う仲間例を持てることを構造だけで保証でき、表示アルゴリズム（slot計算）をスクリプト側に複製しなくて済む。
3. 既存の「`particleSense` が辞書に存在する」「仲間例に自分自身を含まない」「sense の構造（id一意・label非空・siblings 3〜6件）」はそのまま残す。

これにより、今後 sense の割り当てを変えても検査スクリプトを触らずに済む。

## 4. D: 例外上書きの描画条件（任意）

`flashCoreImage()` の描画条件を `if (particle && visibleSiblings.length)` から、上書きがあるときも通るよう `if ((particle || overrideSiblings) && visibleSiblings.length)` に変える。見出しと説明文は `particle` が無い場合を考慮した分岐が要る。

現データでは `coreImage.siblings` を使っていないため**後回しでもよい**。今回は「使う予定ができた時点で直す」判断でも構わない。A〜Cと同時に入れるかは要判断。

## 5. 検証

- `npm test`（`check-core-image-data.cjs` の書き換え後も全項目 OK であること）
- 表示シミュレーションで、16枚の仲間例が引き続きすべて異なり、`Snap out of` が `get out of / grow out of / talk out of`、`bought off` が手を引かせる系になること
- 実ブラウザ（公開後）: 第22〜25問を通しで確認、同じカードを2回開いて仲間例が変わらないこと、幅375pxの折り返し、コンソールエラー無し

## 6. まとめ方

A〜C（＋判断次第でD）を**1コミット**にまとめ、未コミットの sense 分割実装と合わせて `熟語の不変化詞パネルを用法別にする` として1本で公開する。`index.html` のキャッシュバスターは `mode-q1.js?v=1.1.9` が既に立っているため、追加の変更が `mode-q1.js` に及ぶ場合もそのままでよい（未公開のため）。

`.gitignore` の `graft/` 追加は今回の変更と無関係なので、**同じコミットに含めない**。
