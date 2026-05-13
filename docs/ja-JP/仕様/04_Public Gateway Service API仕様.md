<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260513-000006Z-LGG-PG-API
lang: ja-JP
canonical_title: Public Gateway Service API仕様
document_type: spec
canonical_document: true
-->

[目次](../目次.md) > 仕様 > 04_Public Gateway Service API仕様

# Public Gateway Service API仕様

本書は、ChatGPT から利用される Public Gateway Service の公開 API を定義する仕様書である。

## 1. 目的

<!-- sec_id: sec_lgg_pg_api_001 -->

本書は、ChatGPT から利用される Public Gateway Service の公開 API を定義する。

Public Gateway Service は、ChatGPT からの要求を受け付け、Private Bridge Agent へ安全に転送する。

## 2. 基本方針

<!-- sec_id: sec_lgg_pg_api_002 -->

- ChatGPT は Public Gateway Service のみへ接続する
- ChatGPT は Private Bridge Agent へ直接接続しない
- GitLab Personal Access Token は公開しない
- API は GitLab REST API v4 を抽象化する
- request_id により全操作を追跡可能とする
- JSON API とする

## 3. エンドポイント一覧

<!-- sec_id: sec_lgg_pg_api_003 -->

| Method | Path | 役割 |
| --- | --- | --- |
| GET | `/health` | ヘルスチェック |
| GET | `/v1/projects` | Project 一覧取得 |
| GET | `/v1/projects/{project_id}/branches` | Branch 一覧取得 |
| GET | `/v1/projects/{project_id}/files/{file_path}` | File 取得 |
| POST | `/v1/projects/{project_id}/files/{file_path}` | File 作成 |
| PUT | `/v1/projects/{project_id}/files/{file_path}` | File 更新 |
| POST | `/v1/projects/{project_id}/merge-requests` | Merge Request 作成 |
| POST | `/v1/projects/{project_id}/issues` | Issue 作成 |

## 4. 共通仕様

<!-- sec_id: sec_lgg_pg_api_004 -->

### 4.1 Content-Type

```text
application/json
```

### 4.2 認証

HTTP Header に API Key を指定する。

```text
Authorization: Bearer <API_KEY>
```

### 4.3 request_id

全レスポンスに `request_id` を含める。

```json
{
  "request_id": "req_xxxxxxxx"
}
```

### 4.4 エラー応答

```json
{
  "request_id": "req_xxxxxxxx",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "invalid parameter"
  }
}
```

## 5. Health API

<!-- sec_id: sec_lgg_pg_api_005 -->

### 5.1 Request

```http
GET /health
```

### 5.2 Response

```json
{
  "status": "ok",
  "request_id": "req_xxxxxxxx"
}
```

## 6. Project List API

<!-- sec_id: sec_lgg_pg_api_006 -->

### 6.1 Request

```http
GET /v1/projects
```

### 6.2 Response

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

<!-- sec_id: sec_lgg_pg_api_007 -->

### 7.1 Request

```http
GET /v1/projects/{project_id}/branches
```

### 7.2 Response

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

<!-- sec_id: sec_lgg_pg_api_008 -->

### 8.1 Request

```http
GET /v1/projects/{project_id}/files/{file_path}?ref=main
```

### 8.2 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "file_path": "README.md",
  "branch": "main",
  "content": "file content"
}
```

## 9. File Create API

<!-- sec_id: sec_lgg_pg_api_009 -->

### 9.1 Request

```http
POST /v1/projects/{project_id}/files/{file_path}
```

```json
{
  "branch": "feature/test",
  "content": "new file content",
  "commit_message": "add file"
}
```

### 9.2 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "result": "created"
}
```

## 10. File Update API

<!-- sec_id: sec_lgg_pg_api_010 -->

### 10.1 Request

```http
PUT /v1/projects/{project_id}/files/{file_path}
```

```json
{
  "branch": "feature/test",
  "content": "updated file content",
  "commit_message": "update file"
}
```

### 10.2 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "result": "updated"
}
```

## 11. Merge Request Create API

<!-- sec_id: sec_lgg_pg_api_011 -->

### 11.1 Request

```http
POST /v1/projects/{project_id}/merge-requests
```

```json
{
  "source_branch": "feature/test",
  "target_branch": "develop",
  "title": "Update README"
}
```

### 11.2 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "merge_request_id": 10,
  "url": "https://gitlab.example.com/..."
}
```

## 12. Issue Create API

<!-- sec_id: sec_lgg_pg_api_012 -->

### 12.1 Request

```http
POST /v1/projects/{project_id}/issues
```

```json
{
  "title": "Bug report",
  "description": "issue body"
}
```

### 12.2 Response

```json
{
  "request_id": "req_xxxxxxxx",
  "issue_id": 20,
  "url": "https://gitlab.example.com/..."
}
```

## 13. 監査ログ

<!-- sec_id: sec_lgg_pg_api_013 -->

全 API 呼び出しについて、以下を記録する。

- request_id
- timestamp
- caller_ip
- endpoint
- project_id
- operation_type
- execution_result

## 14. 制限事項

<!-- sec_id: sec_lgg_pg_api_014 -->

### 14.1 初期禁止操作

初期実装では以下を禁止する。

- branch delete
- project delete
- force push
- protected branch update
- CI/CD variable read
- secret read
- runner operation
- GitLab admin API

### 14.2 ファイルサイズ制限

初期実装ではファイルサイズ上限を設定する。

初期値:

```text
1 MiB
```

## 15. HTTP Status Code

<!-- sec_id: sec_lgg_pg_api_015 -->

| Status | 用途 |
| --- | --- |
| 200 | 成功 |
| 400 | リクエスト不正 |
| 401 | 認証失敗 |
| 403 | 禁止操作 |
| 404 | 対象なし |
| 409 | 競合 |
| 500 | 内部エラー |
| 502 | Private Bridge Agent 通信失敗 |

## 16. 決定事項

<!-- sec_id: sec_lgg_pg_api_016 -->

- ChatGPT からは Public Gateway Service のみへアクセスする
- GitLab API は直接公開しない
- Public Gateway Service は GitLab Token を保持しない
- 全操作へ request_id を付与する
- 初期実装では破壊的操作を禁止する

---

[目次](../目次.md) > 仕様 > 04_Public Gateway Service API仕様
