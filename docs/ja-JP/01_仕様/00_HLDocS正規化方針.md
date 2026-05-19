<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260513-000001Z-LGG-HLDOCS-POLICY
lang: ja-JP
canonical_title: HLDocS正規化方針
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 仕様 > HLDocS正規化方針

# HLDocS正規化方針

本書は、LocalGitLabGateway のドキュメントを最新の HLDocS 共通仕様へ準拠させるための正規化方針を定義する。

## 1. 適用するHLDocS仕様

以後、LocalGitLabGateway のドキュメントは以下を正として扱う。

```text
https://github.com/mayusaki3/HLDocS/tree/develop/docs/ja-JP/仕様/00_共通
```

## 2. 正規化対象

以下を正規化対象とする。

- `docs/ja-JP/目次.md`
- `docs/ja-JP/01_仕様/*.md`
- `docs/ja-JP/02_テスト仕様/*.md`
- `docs/ja-JP/03_運用手順/*.md`

## 3. 正規化方針

## 3.1 共通構造

各ドキュメントは、以下の順序を持つ。

1. LLM-MANAGED ブロック
2. 空行
3. 先頭階層リンク
4. 空行
5. タイトル
6. 空行
7. 本文
8. 空行
9. 区切り線
10. 空行
11. フッタ階層リンク

## 3.2 階層リンク

LocalGitLabGateway では、ドキュメント入口を以下とする。

```text
README.md → docs/ja-JP/目次.md → 各ドキュメント
```

各ドキュメントの階層リンクは、原則として以下の形式に統一する。

```text
[目次](../目次.md) > <分類> > <ドキュメント名>
```

`docs/ja-JP/目次.md` 自身は以下の形式とする。

```text
[README](../../README.md) > 目次
```

## 3.3 LLM-MANAGED ブロック

各ドキュメント先頭に、以下のメタデータを持つ LLM-MANAGED ブロックを配置する。

```text
HLDocS:LLM-MANAGED
doc_id: <stable doc id>
lang: ja-JP
canonical_title: <正規タイトル>
document_type: <document type>
canonical_document: true
```

## 3.4 document_type

LocalGitLabGateway では、初期段階で以下の document_type を使用する。

| 配置 | document_type |
| --- | --- |
| `docs/ja-JP/目次.md` | index |
| `docs/ja-JP/仕様/*.md` | spec |
| `docs/ja-JP/テスト仕様/*.md` | testspec |
| `docs/ja-JP/運用/*.md` | note |

## 3.5 doc_id

`doc_id` は再作成時も維持する。

既存ドキュメントを初回正規化する場合は、LocalGitLabGateway 用の安定 ID を付与する。

## 3.6 Traceability

仕様、テスト仕様、実装の対応関係は後続工程で導入する。

初期正規化では、まず共通構造、階層リンク、LLM-MANAGED ブロックを優先する。

## 4. 正規化順序

以下の順で正規化する。

1. `docs/ja-JP/目次.md`
2. `docs/ja-JP/仕様/*.md`
3. `docs/ja-JP/テスト仕様/*.md`
4. `docs/ja-JP/運用/*.md`
5. Traceability 導入
6. testspec と code の対応付け

## 5. 当面の禁止事項

以下を禁止する。

- LLM-MANAGED ブロックなしの新規ドキュメント追加
- 階層リンクなしの新規ドキュメント追加
- `README.md → docs/ja-JP/目次.md → 各ドキュメント` を崩す構成変更
- doc_id の理由なき変更
- Git 管理外の仕様を記憶ベースで反映すること

## 6. 決定事項

- 最新 HLDocS 共通仕様を正として扱う
- LocalGitLabGateway の正式なドキュメント入口は `docs/ja-JP/目次.md` とする
- 既存ドキュメントは順次 HLDocS 共通構造へ正規化する
- 正規化作業中は、実装追加よりドキュメント整合性を優先する

---

[目次](../目次.md) > 仕様 > HLDocS正規化方針
