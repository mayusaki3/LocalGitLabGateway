<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260514-000010Z-LGG-APIKEY
lang: ja-JP
canonical_title: APIキー作成手順
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用 > APIキー作成手順

# APIキー作成手順

本書は、LocalGitLabGateway の runtime 設定で使用する API Key および GitLab Personal Access Token の作成手順を定義する。

## 1. 目的

LocalGitLabGateway では、以下の3種類の認証情報を使用する。

| 名称 | 用途 | 配置先 |
| --- | --- | --- |
| Public API Key | 外部クライアントから Public Gateway Service へ接続するためのキー | Public Gateway Host |
| Internal API Key | Public Gateway Service から Private Bridge Agent へ接続するためのキー | Public Gateway Host / Private GitLab Host |
| GitLab Personal Access Token | Private Bridge Agent から Managed GitLab API へ接続するためのトークン | Private GitLab Host |

## 2. 基本方針

- API Key は `openssl rand` で生成する
- GitLab Personal Access Token は GitLab の UI で作成する
- 実キーを Git リポジトリへ commit しない
- 実キーをチャットやログへ貼り付けない
- Public API Key と Internal API Key は別の値にする
- Internal API Key は Public Gateway Host と Private GitLab Host で同じ値を設定する

## 3. Public API Key の作成

Public Gateway Host で実行する。

```bash
openssl rand -hex 32
```

出力例:

```text
0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

この値を、Public Gateway Host の以下へ設定する。

```text
runtime/public_gateway/config.yaml
```

設定箇所:

```yaml
security:
  api_key: <作成したPublic API Key>
```

## 4. Internal API Key の作成

Public Gateway Host または Private GitLab Host のどちらか一方で実行する。

```bash
openssl rand -hex 32
```

出力例:

```text
abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
```

この値は、Public Gateway Host と Private GitLab Host の両方へ同じ値を設定する。

Public Gateway Host 側:

```text
runtime/public_gateway/config.yaml
```

設定箇所:

```yaml
private_bridge:
  internal_api_key: <作成したInternal API Key>
```

Private GitLab Host 側:

```text
runtime/private_bridge/config.yaml
```

設定箇所:

```yaml
security:
  internal_api_key: <作成したInternal API Key>
```

## 5. GitLab Personal Access Token の作成

GitLab の Web UI で作成する。

### 5.1 作成場所

GitLab にログインし、以下へ移動する。

```text
User Settings
→ Access Tokens
```

GitLab のバージョンや表示設定によっては、以下のような名称の場合がある。

```text
Preferences
→ Access Tokens
```

または:

```text
User Settings
→ Access Tokens
→ Add new token
```

### 5.2 推奨設定

| 項目 | 推奨値 |
| --- | --- |
| Token name | local-gitlab-gateway |
| Expiration date | 運用方針に応じた期限 |
| Scope | api |

初期実装では GitLab REST API v4 を使用するため、`api` scope を使用する。

### 5.3 設定先

作成した GitLab Personal Access Token は、Private GitLab Host の以下へ設定する。

```text
runtime/private_bridge/config.yaml
```

設定箇所:

```yaml
gitlab:
  personal_access_token: <作成したGitLab Personal Access Token>
```

## 6. runtime 設定例

## 6.1 Public Gateway Host

```yaml
server:
  host: 0.0.0.0
  port: 8080

security:
  api_key: <Public API Key>

private_bridge:
  base_url: http://10.20.30.2:8081
  timeout_seconds: 30
  internal_api_key: <Internal API Key>
```

## 6.2 Private GitLab Host

```yaml
server:
  host: 0.0.0.0
  port: 8081

security:
  internal_api_key: <Internal API Key>

gitlab:
  base_url: http://127.0.0.1
  personal_access_token: <GitLab Personal Access Token>
```

## 7. 確認コマンド

runtime 設定ファイルの存在と権限を確認する。

Public Gateway Host:

```bash
ls -l runtime/public_gateway/config.yaml
```

Private GitLab Host:

```bash
ls -l runtime/private_bridge/config.yaml
```

期待例:

```text
-rw------- ... config.yaml
```

## 8. 禁止事項

以下を禁止する。

- 実 API Key を GitHub へ commit する
- 実 API Key をチャットへ貼り付ける
- GitLab Personal Access Token を Public Gateway Host に保存する
- Public API Key と Internal API Key に同じ値を使う
- runtime 設定ファイルをログに保存する

## 9. ローテーション方針

API Key または GitLab Personal Access Token が漏洩した可能性がある場合は、以下を行う。

1. 新しいキーまたはトークンを作成する
2. runtime 設定ファイルを更新する
3. 対象サービスを再起動する
4. 古いキーまたはトークンを無効化する

サービス再起動例:

Public Gateway Host:

```bash
sudo systemctl restart local-gitlab-gateway-public
```

Private GitLab Host:

```bash
sudo systemctl restart local-gitlab-gateway-private
```

---

[目次](../目次.md) > 運用 > APIキー作成手順
