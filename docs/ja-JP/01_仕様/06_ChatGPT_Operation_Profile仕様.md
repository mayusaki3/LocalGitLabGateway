<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260513-000008Z-LGG-CGPT-PROFILE
lang: ja-JP
canonical_title: ChatGPT Operation Profile仕様
document_type: spec
canonical_document: true
-->

[目次](../目次.md) > 仕様 > ChatGPT Operation Profile仕様

# ChatGPT Operation Profile仕様

本書は、ChatGPT が LocalGitLabGateway を利用して Managed GitLab を安全に操作するために必要な情報セットである ChatGPT Operation Profile を定義する仕様書である。

## 1. 目的

<!-- sec_id: sec_lgg_profile_001 -->

本書は、ChatGPT が LocalGitLabGateway を利用して Managed GitLab を安全に操作するために必要な情報セットである ChatGPT Operation Profile を定義する。

ChatGPT Operation Profile は、Public Gateway Service へ接続するための情報、および利用可能操作の制約を定義する。

## 2. 基本方針

<!-- sec_id: sec_lgg_profile_002 -->

- ChatGPT には必要最小限の情報のみ渡す
- GitLab Personal Access Token を ChatGPT へ渡さない
- Private GitLab Host の詳細内部情報を ChatGPT へ渡さない
- Public Gateway Service のみを公開接続先とする
- ChatGPT が実行可能な操作範囲を明示する
- ChatGPT が禁止操作を判断できる情報を含める

## 3. ChatGPT Operation Profile 構成

<!-- sec_id: sec_lgg_profile_003 -->

```text
ChatGPT
  ↓
ChatGPT Operation Profile
  ↓
Public Gateway Service
```

## 4. 格納場所

<!-- sec_id: sec_lgg_profile_004 -->

```text
profiles/chatgpt/
├── operation_profile.template.md
└── operation_profile.example.md
```

## 5. 含める情報

<!-- sec_id: sec_lgg_profile_005 -->

### 5.1 Public Gateway Service 接続情報

| 項目 | 内容 |
| --- | --- |
| base_url | Public Gateway Service の HTTPS URL |
| api_version | API version |
| timeout | API timeout |

### 5.2 認証情報

| 項目 | 内容 |
| --- | --- |
| api_key | Public Gateway Service 用 API Key |
| auth_scheme | Bearer authentication |

### 5.3 利用可能 API

| API | 用途 |
| --- | --- |
| Project List API | Project 一覧取得 |
| Branch List API | Branch 一覧取得 |
| File Get API | File 取得 |
| File Create API | File 作成 |
| File Update API | File 更新 |
| Merge Request Create API | Merge Request 作成 |
| Issue Create API | Issue 作成 |

### 5.4 許可操作

ChatGPT に許可する操作を定義する。

例:

```text
- README 更新
- docs 更新
- 新規 markdown 追加
- feature branch 作成
- Merge Request 作成
- Issue 作成
```

### 5.5 禁止操作

ChatGPT に禁止する操作を定義する。

例:

```text
- branch delete
- protected branch update
- force push
- secret read
- CI/CD variable read
- runner operation
- project delete
- GitLab admin API
```

### 5.6 プロジェクト制限

操作対象 Project を制限する場合、allowlist を定義する。

例:

```text
allowed_projects:
  - LocalGitLabGateway
  - SansaVRM
```

### 5.7 ブランチ制限

ChatGPT が直接更新可能な branch を制限する。

例:

```text
allowed_write_branches:
  - feature/*
  - develop
```

### 5.8 ファイル制限

更新可能ファイル範囲を制限する。

例:

```text
allowed_paths:
  - docs/**
  - README.md
  - src/**
```

## 6. 含めてはならない情報

<!-- sec_id: sec_lgg_profile_006 -->

### 6.1 GitLab Personal Access Token

GitLab Personal Access Token を含めてはならない。

### 6.2 Private GitLab Host 詳細情報

以下を含めてはならない。

- 内部 IP
- firewall 詳細
- SSH 認証情報
- VPN 秘密鍵

### 6.3 機密情報

以下を含めてはならない。

- CI/CD secrets
- runner token
- database password
- TLS private key
- WireGuard private key

## 7. 形式

<!-- sec_id: sec_lgg_profile_007 -->

### 7.1 テンプレート形式

ChatGPT Operation Profile は Markdown 形式とする。

### 7.2 例

```markdown
# ChatGPT Operation Profile

## Endpoint

https://gateway.example.com

## Authentication

Authorization: Bearer <API_KEY>

## Allowed Operations

- File Get
- File Update
- Merge Request Create

## Forbidden Operations

- branch delete
- project delete
```

## 8. 運用ルール

<!-- sec_id: sec_lgg_profile_008 -->

### 8.1 API Key ローテーション

API Key は定期的に変更する。

### 8.2 権限最小化

ChatGPT に渡す権限は最小限とする。

### 8.3 操作監査

ChatGPT からの全操作は Public Gateway Service の監査ログへ記録する。

### 8.4 revoke

API Key 漏洩時は即時 revoke 可能とする。

## 9. ChatGPT 側利用方針

<!-- sec_id: sec_lgg_profile_009 -->

ChatGPT は以下を守る前提とする。

- request_id を維持する
- 禁止操作を実行しない
- allowlist 外操作を実行しない
- API error を無視しない
- Merge Request を優先し、直接 main 更新を避ける

## 10. 初期テンプレート構成

<!-- sec_id: sec_lgg_profile_010 -->

```text
profiles/chatgpt/
├── operation_profile.template.md
└── operation_profile.example.md
```

## 11. 将来拡張

<!-- sec_id: sec_lgg_profile_011 -->

将来的には以下を追加可能とする。

- operation scope per repository
- operation scope per branch
- approval workflow
- operation rate limit
- read-only mode
- maintenance mode

## 12. 決定事項

<!-- sec_id: sec_lgg_profile_012 -->

- ChatGPT は Public Gateway Service のみへ接続する
- GitLab Personal Access Token を ChatGPT へ渡さない
- ChatGPT へ渡す操作権限は allowlist 方式とする
- ChatGPT に禁止操作一覧を明示する
- ChatGPT Operation Profile は Markdown 形式とする

---

[目次](../目次.md) > 仕様 > ChatGPT Operation Profile仕様
