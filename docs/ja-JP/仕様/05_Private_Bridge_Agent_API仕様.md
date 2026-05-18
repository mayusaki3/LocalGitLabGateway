<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260513-000007Z-LGG-PB-API
lang: ja-JP
canonical_title: Private Bridge Agent API仕様
document_type: spec
canonical_document: true
-->

[目次](../目次.md) > 仕様 > Private Bridge Agent API仕様

# Private Bridge Agent API仕様

本書は、Public Gateway Service から呼び出される Private Bridge Agent の内部 API を定義する仕様書である。

## 1. 目的

<!-- sec_id: sec_lgg_pb_api_001 -->

本書は、Public Gateway Service から呼び出される Private Bridge Agent の内部 API を定義する。

Private Bridge Agent は、Public Gateway Service から受け取った要求を Managed GitLab の REST API v4 へ変換し、実行結果を返却する。

## 2. 基本方針

<!-- sec_id: sec_lgg_pb_api_002 -->

- Private Bridge Agent は Private GitLab Host 上で動作する
- Private Bridge Agent は WireGuard VPN 内からのみ到達可能とする
- Private Bridge Agent は GitLab Personal Access Token を保持する
- GitLab Personal Access Token は Public Gateway Service へ返却しない
- Private Bridge Agent は GitLab REST API v4 を代理実行する
- Public Gateway Service から渡された request_id を維持する
- 内部 API も JSON API とする

## 3. エンドポイント一覧

<!-- sec_id: sec_lgg_pb_api_003 -->

| Method | Path | 役割 |
| --- | --- | --- |
| GET | `/internal/health` | 内部ヘルスチェック |
| GET | `/internal/api/v1/projects` | Project 一覧取得 |
| GET | `/internal/api/v1/projects/{project_id}/branches` | Branch 一覧取得 |
| GET | `/internal/api/v1/projects/{project_id}/files/{file_path}` | File 取得 |
| POST | `/internal/api/v1/projects/{project_id}/files/{file_path}` | File 作成 |
| PUT | `/internal/api/v1/projects/{project_id}/files/{file_path}` | File 更新 |
| POST | `/internal/api/v1/projects/{project_id}/merge-requests` | Merge Request 作成 |
| POST | `/internal/api/v1/projects/{project_id}/issues` | Issue 作成 |

## 4. 共通仕様

<!-- sec_id: sec_lgg_pb_api_004 -->

### 4.1 Content-Type

```text
application/json
```

### 4.2 内部認証

Public Gateway Service から Private Bridge Agent への要求には内部 API Key を使用する。

```text
Authorization: Bearer <INTERNAL_API_KEY>
```

### 4.3 request_id

Public Gateway Service から渡された `request_id` をそのまま使用する。

```json
{
  "request_id": "req_xxxxxxxx"
}
```

### 4.4 共通エラー応答

```json
{
  "request_id": "req_xxxxxxxx",
  "error": {
    "code": "GITLAB_API_ERROR",
    "message": "GitLab API request failed"
  }
}
```

## 5. Health API

<!-- sec_id: sec_lgg_pb_api_005 -->

### 5.1 Request

```http
GET /internal/health
```

### 5.2 Response

```json
{
  "status": "ok",
  "request_id": "req_xxxxxxxx"
}
```

## 6. Project List API

<!-- sec_id: sec_lgg_pb_api_006 -->

### 6.1 Request

```http
GET /internal/api/v1/projects
```

### 6.2 GitLab API Mapping

```http
GET /api/v4/projects
```

### 6.3 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "projects": [
    {
      "id": 1,
      "name": "sample-project",
      "path": "sample-project"
    }
  ]
}
```

## 7. Branch List API

<!-- sec_id: sec_lgg_pb_api_007 -->

### 7.1 Request

```http
GET /internal/api/v1/projects/{project_id}/branches
```

### 7.2 GitLab API Mapping

```http
GET /api/v4/projects/{project_id}/repository/branches
```

### 7.3 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "branches": [
    {
      "name": "main"
    }
  ]
}
```

## 8. File Get API

<!-- sec_id: sec_lgg_pb_api_008 -->

### 8.1 Request

```http
GET /internal/api/v1/projects/{project_id}/files/{file_path}?ref=main
```

### 8.2 GitLab API Mapping

```http
GET /api/v4/projects/{project_id}/repository/files/{file_path}?ref=main
```

GitLab API の `file_path` は URL encode して送信する。

### 8.3 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "file_path": "README.md",
  "branch": "main",
  "content": "file content"
}
```

## 9. File Create API

<!-- sec_id: sec_lgg_pb_api_009 -->

### 9.1 Request

```http
POST /internal/api/v1/projects/{project_id}/files/{file_path}
```

```json
{
  "request_id": "req_xxxxxxxx",
  "branch": "feature/test",
  "content": "new file content",
  "commit_message": "add file"
}
```

### 9.2 GitLab API Mapping

```http
POST /api/v4/projects/{project_id}/repository/files/{file_path}
```

### 9.3 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "result": "created"
}
```

## 10. File Update API

<!-- sec_id: sec_lgg_pb_api_010 -->

### 10.1 Request

```http
PUT /internal/api/v1/projects/{project_id}/files/{file_path}
```

```json
{
  "request_id": "req_xxxxxxxx",
  "branch": "feature/test",
  "content": "updated file content",
  "commit_message": "update file"
}
```

### 10.2 GitLab API Mapping

```http
PUT /api/v4/projects/{project_id}/repository/files/{file_path}
```

### 10.3 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "result": "updated"
}
```

## 11. Merge Request Create API

<!-- sec_id: sec_lgg_pb_api_011 -->

### 11.1 Request

```http
POST /internal/api/v1/projects/{project_id}/merge-requests
```

```json
{
  "request_id": "req_xxxxxxxx",
  "source_branch": "feature/test",
  "target_branch": "develop",
  "title": "Update README"
}
```

### 11.2 GitLab API Mapping

```http
POST /api/v4/projects/{project_id}/merge_requests
```

### 11.3 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "merge_request_id": 10,
  "url": "https://gitlab.example.com/..."
}
```

## 12. Issue Create API

<!-- sec_id: sec_lgg_pb_api_012 -->

### 12.1 Request

```http
POST /internal/api/v1/projects/{project_id}/issues
```

```json
{
  "request_id": "req_xxxxxxxx",
  "title": "Bug report",
  "description": "issue body"
}
```

### 12.2 GitLab API Mapping

```http
POST /api/v4/projects/{project_id}/issues
```

### 12.3 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "issue_id": 20,
  "url": "https://gitlab.example.com/..."
}
```

## 13. GitLab 認証情報管理

<!-- sec_id: sec_lgg_pb_api_013 -->

Private Bridge Agent は、GitLab Personal Access Token を設定ファイルまたは環境変数から読み込む。

Git 管理対象の設定例には、実トークンを含めない。

## 14. GitLab API 応答の正規化

<!-- sec_id: sec_lgg_pb_api_014 -->

Private Bridge Agent は、GitLab API の応答を Public Gateway Service 向けに正規化する。

正規化対象:

- 不要な内部情報の除去
- GitLab Token の除去
- GitLab 詳細エラーの必要最小化
- ChatGPT が扱いやすい JSON 形式への変換

## 15. ログ

<!-- sec_id: sec_lgg_pb_api_015 -->

Private Bridge Agent は、以下をログへ記録する。

- request_id
- timestamp
- endpoint
- project_id
- operation_type
- GitLab API endpoint
- execution_result

GitLab Personal Access Token、ファイル内容、秘密情報はログに出力しない。

## 16. HTTP Status Code

<!-- sec_id: sec_lgg_pb_api_016 -->

| Status | 用途 |
| --- | --- |
| 200 | 成功 |
| 400 | リクエスト不正 |
| 401 | 内部認証失敗 |
| 403 | 禁止操作 |
| 404 | 対象なし |
| 409 | GitLab 側競合 |
| 500 | 内部エラー |
| 502 | GitLab API 通信失敗 |

## 17. 決定事項

<!-- sec_id: sec_lgg_pb_api_017 -->

- Private Bridge Agent は内部 API のみ提供する
- Private Bridge Agent は GitLab Personal Access Token を保持する
- Public Gateway Service へ GitLab Personal Access Token を返却しない
- Public Gateway Service から渡された request_id を維持する
- GitLab API の詳細応答は必要最小限へ正規化する

---

[目次](../目次.md) > 仕様 > Private Bridge Agent API仕様
