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
