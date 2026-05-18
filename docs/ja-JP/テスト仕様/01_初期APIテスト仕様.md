[目次](../目次.md) > テスト仕様 > 初期APIテスト仕様

# 初期APIテスト仕様

## 1. 目的

本書は、LocalGitLabGateway の初期実装に対するテスト仕様を定義する。

対象は、Public Gateway Service、Private Bridge Agent、ChatGPT Operation Profile に関する初期 API とセキュリティ境界である。

## 2. テスト方針

- すべてのテストケースにテスト番号を付与する
- 実装前に期待動作を固定する
- 単体テストは対象モジュールのカバレッジ 100% を目標とする
- GitLab Personal Access Token が外部へ露出しないことを確認する
- request_id が Public Gateway Service から Private Bridge Agent まで維持されることを確認する
- 禁止操作が拒否されることを確認する

## 3. テスト対象

| 対象 | 内容 |
| --- | --- |
| Public Gateway Service | 公開API、認証、要求検証、監査ログ |
| Private Bridge Agent | 内部API、GitLab API変換、応答正規化 |
| Common | request_id、エラー応答、共通モデル |
| ChatGPT Operation Profile | 情報セット、禁止情報、allowlist |

## 4. Public Gateway Service 単体テスト

## 4.1 認証テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PG-AUTH-001 | API Key あり | 200 または対象APIの正常応答を返す |
| UT-PG-AUTH-002 | API Key なし | 401 を返す |
| UT-PG-AUTH-003 | 不正 API Key | 401 を返す |
| UT-PG-AUTH-004 | Authorization scheme 不正 | 401 を返す |

## 4.2 request_id テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PG-REQ-001 | request_id 自動採番 | レスポンスに request_id を含む |
| UT-PG-REQ-002 | request_id 監査ログ出力 | 監査ログに request_id を含む |
| UT-PG-REQ-003 | Private Bridge Agent 転送 | 内部要求に同一 request_id を含む |

## 4.3 公開APIテスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PG-API-001 | Health API | status=ok を返す |
| UT-PG-API-002 | Project List API | projects 配列を返す |
| UT-PG-API-003 | Branch List API | branches 配列を返す |
| UT-PG-API-004 | File Get API | file_path, branch, content を返す |
| UT-PG-API-005 | File Create API | result=created を返す |
| UT-PG-API-006 | File Update API | result=updated を返す |
| UT-PG-API-007 | Merge Request Create API | merge_request_id と url を返す |
| UT-PG-API-008 | Issue Create API | issue_id と url を返す |

## 4.4 禁止操作テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PG-DENY-001 | branch delete 禁止 | 403 を返す |
| UT-PG-DENY-002 | project delete 禁止 | 403 を返す |
| UT-PG-DENY-003 | force push 相当操作禁止 | 403 を返す |
| UT-PG-DENY-004 | CI/CD variable read 禁止 | 403 を返す |
| UT-PG-DENY-005 | secret read 禁止 | 403 を返す |
| UT-PG-DENY-006 | GitLab admin API 禁止 | 403 を返す |

## 5. Private Bridge Agent 単体テスト

## 5.1 内部認証テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PB-AUTH-001 | 内部 API Key あり | 正常応答を返す |
| UT-PB-AUTH-002 | 内部 API Key なし | 401 を返す |
| UT-PB-AUTH-003 | 不正内部 API Key | 401 を返す |

## 5.2 GitLab API Mapping テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PB-MAP-001 | Project List mapping | `/api/v4/projects` へ変換する |
| UT-PB-MAP-002 | Branch List mapping | `/api/v4/projects/{project_id}/repository/branches` へ変換する |
| UT-PB-MAP-003 | File Get mapping | repository files API へ変換する |
| UT-PB-MAP-004 | File Create mapping | repository files create API へ変換する |
| UT-PB-MAP-005 | File Update mapping | repository files update API へ変換する |
| UT-PB-MAP-006 | Merge Request mapping | merge_requests API へ変換する |
| UT-PB-MAP-007 | Issue Create mapping | issues API へ変換する |

## 5.3 機密情報非露出テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PB-SEC-001 | GitLab Token レスポンス非露出 | レスポンスに GitLab Token を含めない |
| UT-PB-SEC-002 | GitLab Token ログ非露出 | ログに GitLab Token を含めない |
| UT-PB-SEC-003 | ファイル内容ログ非露出 | 更新対象ファイル内容をログに含めない |
| UT-PB-SEC-004 | GitLab 詳細エラー最小化 | 必要最小限のエラーのみ返す |

## 6. Common 単体テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-COM-REQ-001 | request_id 生成 | `req_` prefix の ID を生成する |
| UT-COM-ERR-001 | 共通エラー形式 | error.code と error.message を返す |
| UT-COM-LOG-001 | 構造化ログ | JSON 形式でログ出力する |

## 7. 結合テスト

## 7.1 Public Gateway Service から Private Bridge Agent

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| IT-PG-PB-001 | Health 中継 | Public Gateway Service 経由で Private Bridge Agent の到達性を確認できる |
| IT-PG-PB-002 | Project List 中継 | projects 配列を返す |
| IT-PG-PB-003 | request_id 維持 | Public Gateway Service と Private Bridge Agent で同一 request_id を記録する |
| IT-PG-PB-004 | 内部認証失敗 | Public Gateway Service は 502 または適切なエラーへ正規化する |

## 7.2 Private Bridge Agent から Managed GitLab

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| IT-PB-GL-001 | GitLab 接続確認 | Managed GitLab API へ接続できる |
| IT-PB-GL-002 | Project List 実行 | GitLab project 一覧を取得できる |
| IT-PB-GL-003 | File Get 実行 | 指定ファイルを取得できる |
| IT-PB-GL-004 | GitLab 認証失敗 | 502 または適切な GitLab API エラーへ正規化する |

## 8. ChatGPT Operation Profile テスト

| テスト番号 | テスト名 | 期待結果 |
| --- | --- | --- |
| UT-PROFILE-001 | 必須項目存在 | base_url, api_key, allowed_operations を含む |
| UT-PROFILE-002 | GitLab Token 非含有 | GitLab Personal Access Token を含まない |
| UT-PROFILE-003 | VPN秘密鍵非含有 | WireGuard private key を含まない |
| UT-PROFILE-004 | 禁止操作明示 | forbidden operations を含む |
| UT-PROFILE-005 | allowlist 明示 | allowed_projects, allowed_paths を定義できる |

## 9. カバレッジ基準

単体テストでは、以下の対象についてカバレッジ 100% を目標とする。

- Public Gateway Service の認証処理
- Public Gateway Service の要求検証処理
- Private Bridge Agent の GitLab API mapping 処理
- 共通エラー応答処理
- request_id 生成処理
- 機密情報マスク処理

## 10. 決定事項

- 初期テストでは破壊的操作を実行しない
- 禁止操作はモックまたはルーティング不在により検証する
- GitLab API は単体テストではモック化する
- 実 GitLab 接続は結合テストでのみ実施する
- 実トークンをテストログへ出力しない

---

[目次](../目次.md) > テスト仕様 > 初期APIテスト仕様
