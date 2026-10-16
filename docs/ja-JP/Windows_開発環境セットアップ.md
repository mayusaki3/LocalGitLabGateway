# Windows 開発環境・テスト実行手順

## 1. 対象

開発PC: Windows 11 / PowerShell。配備先: Ubuntu Server（Public GatewayおよびGitLab）。
この手順はGitLabやUbuntu Serverを構築せず、まずWindowsでPythonテストを実行する。

## 2. 必要ソフト

- Git
- Python 3.11以上（`py -3.11 --version` で確認）
- インターネット接続（Python依存の初回取得のみ）

## 3. PowerShellでの初回準備

リポジトリのルートで以下を実行する。

```powershell
git switch develop
git pull --ff-only
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Python 3.11がない場合は `py -0p` で利用可能なPythonを確認し、3.11以上の実際のバージョンに置き換える。

## 4. 単体テスト・静的検査

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

全テストの設定ではカバレッジ100%が要求される。初期実装のため現時点で失敗する可能性があり、失敗したログは省略せず共有する。トンネル関連の個別テストだけを調べる場合:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests/test_tunnel_auth.py tests/test_tunnel_session.py tests/test_tunnel_protocol.py tests/test_tunnel_relay.py tests/test_tunnel_endpoint.py tests/test_tunnel_worker.py tests/test_tunnel_client.py tests/test_tunnel_public_api.py tests/test_private_canonical_projects.py tests/test_request_id_propagation.py
```

## 5. 設定ファイルのWindows対応

アプリ起動時にLinuxの `/opt/...` パスを使わないよう、次の環境変数でローカル設定ファイルを指定できる。

```powershell
$env:LGG_PUBLIC_CONFIG = "D:\\path\\to\\public-config.yaml"
$env:LGG_PRIVATE_CONFIG = "D:\\path\\to\\private-config.yaml"
```

これらのYAMLに入れる認証情報・GitLab PATはGitへコミットしない。テストのみであれば通常は実際のGitLab PATは不要。

## 6. 次段階の検証

1. Windows上でpytestとruffの結果を確認・修正。
2. Windows内でPublic GatewayとPrivate Bridgeの模擬GitLabを使い、WSS往復試験を追加・実行。
3. FW内テスト用GatewayからFW内GitLabへの疎通確認。
4. 外部Ubuntu ServerへPublic Gatewayを配備し、FW内からWSSを手動起動して疎通確認。
5. 前段階が合格してからChatGPT接続を検証。

Windows検証は本番UbuntuのTLS、nginx、systemd、Firewall動作の代替にはならない。

## 7. 現状の制限

旧HTTP API・テストの移行は未完了。公開APIとPrivate Bridge間のWSS統合テストは未実行。設定ファイル形式の全項目やセキュリティ検証も未確定のため、本番公開はしない。


## 8. 2026-10-16 単体検証の確定結果

Windows 11 / Python 3.11.9、develop commit `22493f0` について利用者が実行し、以下を確認した。

- `python -m pytest -q`: **76 passed, 1 warning**。
- 対象モジュールのカバレッジ: **287 statements / 0 missed = 100.00%**。
- `python -m ruff check .`: **All checks passed**。
- 警告: `StarletteDeprecationWarning`（`starlette.testclient` の httpx 互換性）。テスト失敗ではない。

この結果は現行カバレッジ対象の単体テストであり、実際の WSS 往復、GitLab 実機、Ubuntu/nginx/systemd/TLS 設定を検証したものではない。前節の「初期実装のため失敗する可能性がある」はこの日時の結果で更新する。

## 9. 次工程：Windows 上の Reverse WebSocket 結合検証

### 9.1 検証の構成と前提

1. Windows 開発PC上で **Public Gateway（127.0.0.1:8080）** と **Private Bridge（127.0.0.1:8081）** を別プロセスとして起動する。Private Bridge の GitLab 接続先はモック HTTP サーバーとし、実 PAT は使用しない。
2. WSS Worker は別プロセスとして手動起動する。Public Gateway 側の `/internal/tunnel/v1` は WebSocket 受入口であり、Worker が要求する `wss://` との間に **TLS 終端プロキシが必要**。単純な `ws://127.0.0.1:8080` への変更は行わない。
3. ローカル検証用 CA とサーバー証明書を使用する場合、Worker が証明書を検証できるよう `SSL_CERT_FILE` などの信頼設定を行う。自己署名証明書の検証無効化は行わない。
4. 設定ファイルはリポジトリ外に作り、`LGG_PUBLIC_CONFIG` と `LGG_PRIVATE_CONFIG` で指定する。GitLab PAT、公開 API Key、内部 API Key、WSS Token はそれぞれ別のテスト用値とする。

### 9.2 起動前の確認

Public Gateway の設定には少なくとも `security.api_key`、`private_bridge.base_url`、`private_bridge.internal_api_key`、`tunnel.token` が必要。Private Bridge の設定には `security.internal_api_key`、`gitlab.base_url`、`gitlab.personal_access_token` が必要。正確な構造は現行の `main.py` と構成例に照合する。

```powershell
$env:LGG_PUBLIC_CONFIG = "C:\\LGG-test\\public.yaml"
$env:LGG_PRIVATE_CONFIG = "C:\\LGG-test\\private.yaml"
.\\.venv\\Scripts\\python.exe -m uvicorn local_gitlab_gateway.public_gateway.main:app --host 127.0.0.1 --port 8080
```

別の PowerShell で:

```powershell
$env:LGG_PRIVATE_CONFIG = "C:\\LGG-test\\private.yaml"
.\\.venv\\Scripts\\python.exe -m uvicorn local_gitlab_gateway.private_bridge.main:app --host 127.0.0.1 --port 8081
```

これらは **起動例であり、結合検証合格の記録ではない**。パス、設定値、モックサーバー、TLS プロキシを準備してから実行する。

### 9.3 検証項目と合格条件

| 検証 | 条件 |
|---|---|
| トンネル停止 | 認証済み `GET /api/v1/projects` が 503 と `request_id` を返す |
| WSS 認証 | トンネル専用 Bearer Token が不正なら接続拒否 |
| WSS 接続 | 正しい Token / `lgg-tunnel.v1` で接続できる |
| 正常往復 | Public API → WSS → Private Bridge → モック GitLab → WSS → Public API の結果が正規化形式 |
| ID 伝播 | 全経路で同一 `request_id` |
| 禁止操作 | 許可リスト外の要求が GitLab に到達しない |
| 切断 | 待機中の要求は 503、接続切断後は 503 |
| 再接続 | Worker が稼働中のみバックオフで再接続 |
| 手動停止 | Worker 停止後は再接続しない |
| 機密情報 | PAT、内部 API Key、WSS Token が公開応答・通常ログに出ない |

### 9.4 現時点の実装上の注意

- `public_gateway/main.py` と `private_bridge/main.py` には **旧 HTTP API ルートが残存**する。結合検証では正規ルート `/api/v1/projects` と `/internal/api/v1/projects` を使用し、旧経路の公開可否は別途整理する。
- Worker は受信要求を逐次処理している。複数同時要求や遅延時の挙動は結合テストで追加確認する。
- 実 WSS 通信を伴う検証は未実施。Windows でのモック結合合格後に FW 内環境、外部 Ubuntu、ChatGPT の順に進める。


## 10. 実WSSスモークテスト（ローカルホスト）

`validation/wss_smoke/mock_gitlab.py` は、ループバックで起動する検証専用のGitLab模擬API。 `validation/wss_smoke/setup_windows.ps1` は、mkcertを使ってローカルTLS証明書と検証用YAMLを一時ディレクトリに作り、各プロセスの起動コマンドを表示する。**自動起動や自動配備は行わない。**

事前に `mkcert` をインストールし、開発PC上で `mkcert -install` によりローカルCAを信頼させる。検証用CAは本番環境に配布しない。

```powershell
git pull --ff-only
.\\validation\\wss_smoke\\setup_windows.ps1
```

表示されたコマンドを別々のPowerShellで順に実行する。

1. モックGitLab: `127.0.0.1:8090`
2. Private Bridge: `127.0.0.1:8081`
3. TLS Public Gateway: `https://localhost:8443`
4. Tunnel Worker: `wss://localhost:8443/internal/tunnel/v1`

Workerを起動する前に、公開APIが503を返すことを確認する。Worker起動後は同じAPIが200を返し、`projects[0].id=42`、`page=2`、`per_page=5`、`request_id` が返ることを確認する。WorkerをCtrl+Cで停止し、再度503になることを確認する。

**注意:** この手順はUvicornの直接TLS終端を使うため、nginxのTLS終端・リバースプロキシ設定はまだ検証しない。localhost証明書、ポート、認証情報は検証専用とする。実行結果は未確認。


## 11. 2026-10-16 Windows 実WSSスモークテスト結果

ユーザー実測。mkcert v1.4.4 でローカルCAを登録し、`validation/wss_smoke/setup_windows.ps1` によりlocalhost証明書と一時設定を生成した。モックGitLab（8090）、Private Bridge（8081）、Public Gateway（8443, Uvicorn直接TLS）を別プロセスで起動した。

| 手順 | 実測結果 | 判定 |
|---|---|---|
| Worker未起動 | GET `/api/v1/projects?page=2&per_page=5` → HTTP 503 | PASS |
| Worker起動 | 同API → HTTP 200、`projects[0].id=42`、`page=2`、`per_page=5`、`request_id` あり | PASS |
| Worker停止 | 同API → HTTP 503 | PASS |
| Worker再起動 | 同API → 正常プロジェクト応答 | PASS |
| Worker再停止 | 同API → HTTP 503 | PASS |

追加結合テスト `tests/test_tunnel_roundtrip_integration.py` は単独1件成功。全体は77件成功、警告1件、計測対象287行100%カバレッジ、Ruff成功（ユーザー実測）。

**未検証:** 不正Bearer/API認証、処理中切断、ネットワーク障害中のWorker自動再接続、複数同時要求、Ubuntu/nginx/systemd、外部ネットワーク、実GitLab、ChatGPT。検証用のUvicorn直接TLSは本番TLS終端の代替ではない。

既存の第7節・第9節にある「実WSS未実施」は記述当時の状態であり、本節の実測結果を最新とする。
