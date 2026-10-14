<!--
HLDocS:LLM-MANAGED
doc_id: doc-20261014-090000Z-LGG-RWSS-DESIGN
lang: ja-JP
canonical_title: Reverse WebSocket 詳細設計
document_type: design
canonical_document: true
-->

[目次](../目次.md) > 仕様 > Reverse WebSocket 詳細設計

# Reverse WebSocket 詳細設計

## 1. 目的と適用範囲

本書は、FW内から外部Ubuntu Serverへ接続するオンデマンド Reverse WebSocket（WSS）の最小構成と検証順序を定める。通信方式の正本は [通信方式設計](02_通信方式設計.md)、API契約の正本は Public Gateway / Private Bridge の各API仕様とする。

## 2. 配置

- 外部Ubuntu: nginx（HTTPS/WSS終端）、Public Gateway API、認証付きトンネル受入口、監査ログ。
- FW内: Private Bridge API、Managed GitLab、トンネルクライアントと手動起動・停止機構。
- 検証段階1: FW内にPublic Gatewayとトンネル受入口を配置し、ローカル接続で機能・障害試験を行う。
- 検証段階2: 外部Ubuntuの本番Public GatewayをFW内からHTTPSで呼び出し、FW内から張ったWSSを介した応答を確認する。
- 検証段階3: 段階2の合格後、ChatGPTから同じHTTPS公開APIを呼び出す。
- FW内のPrivate Bridge/GitLabは外部から直接到達できない。外部Ubuntuのトンネル受入口と公開APIは別ルートにする。

## 3. ライフサイクル

状態は `DISABLED`、`CONNECTING`、`CONNECTED`、`RECONNECT_WAIT`、`STOPPING` とする。

- 初期状態は `DISABLED`。明示的な管理操作でのみ `CONNECTING` に移る。
- WSS接続と相互認証が成功した場合に `CONNECTED` となる。
- 利用中の予期せぬ切断は `RECONNECT_WAIT` とし、有効フラグが真の間だけ再接続する。
- 無効化操作は再接続待機を取り消し、接続と未完了要求を終了して `DISABLED` へ移る。
- Public GatewayへのAPI要求によってトンネルを自動起動しない。
- サービス再起動後の有効状態は既定で無効とする。自動起動設定を用意する場合も明示的な運用変更を要する。

## 4. 要求・応答中継

- Public GatewayはBearer認証、入力検証、allowlist判定後に `request_id` を付けてトンネルへ要求を送る。
- トンネルの要求メッセージは `type`、`request_id`、`method`、`path`、`query`、`body` を持つ。HTTPヘッダー全体を無条件転送しない。
- FW内クライアントは受信した操作を内部APIの許可済みパスに限定し、内部Bearer認証でPrivate Bridgeを呼び出す。
- 応答メッセージは `type`、`request_id`、`status_code`、`body` を持つ。Public Gatewayは公開API仕様の正規化応答を返す。
- 同時要求は `request_id` で対応付ける。重複ID、未知ID、遅延応答は拒否・破棄し監査記録する。
- トンネル切断、タイムアウト、内部障害時は、Public Gatewayが同一 `request_id` を含む安全なエラー応答を返す。
- 書き込み操作の再送は自動実行しない。タイムアウト後の成否不明ケースは照会・人手確認を優先する。

## 5. セキュリティ境界

- 公開API認証: `Authorization: Bearer <API_KEY>`。
- Private Bridge認証: `Authorization: Bearer <INTERNAL_API_KEY>`。
- WSSトンネル接続は上記とは独立した専用資格情報で認証する。秘密値はソースコード・ログ・API応答に含めない。
- WSSはサーバー証明書検証を必須とする。無効化設定を本番で認めない。
- 外部UbuntuにはGitLab Personal Access Tokenを置かない。内部APIの資格情報はFW内に保持する。
- トンネルは許可済みのGitLab操作のみを中継する。汎用TCPプロキシや任意URLアクセスを提供しない。
- Public Gatewayからの正常・異常応答と双方の監査ログで同一 `request_id` を保持する。

## 6. 接続不能時

- トンネル未接続でも `GET /health` はPublic Gatewayプロセスの稼働を示せる。ただしGitLab操作可能状態とは区別する。
- GitLab操作要求は未接続・タイムアウト・認証不成立のいずれでも実行せず、内部情報を含まないエラーを返す。
- 再接続中は新規要求を無期限にキューしない。キュー上限と要求タイムアウトを設ける。

## 7. テスト対応

[初期APIテスト仕様](../02_テスト仕様/01_初期APIテスト仕様.md) の `UT-TUN-001`〜`009`、`IT-TUN-001`〜`005` を実施する。段階1→2→3の順に検証し、前段階未合格で次へ進まない。

## 8. 詳細実装時の決定事項

- トンネル専用認証方式と資格情報のローテーション方法。
- WSSの具体的なURL、接続数制限、再接続間隔、タイムアウト値。
- 操作許可リストの表現とトンネルメッセージの厳密なスキーマ。
- systemd管理操作と有効化状態の永続化方針。
- 旧WireGuard配備資料の廃止・移行範囲。


## 9. 初期プロトコル確定値

- WSSパス: `/internal/tunnel/v1`。公開GitLab APIとルートを分離する。
- トンネル接続認証: 専用 `Authorization: Bearer <TUNNEL_TOKEN>`。Public API Key、Internal API Keyと別の秘密値とし、固定時間比較で照合する。資格情報をURLクエリに含めない。
- WebSocketサブプロトコル: `lgg-tunnel.v1`。未対応のバージョンは接続を拒否する。
- JSONメッセージ形式: UTF-8、1フレーム1メッセージ、厳格なスキーマ検証、未知のtypeを拒否する。
- `request`: `{"type":"request","request_id":"req_...","method":"GET","path":"/internal/api/v1/projects","query":{},"body":null}`。
- `response`: `{"type":"response","request_id":"req_...","status_code":200,"body":{"request_id":"req_...","projects":[]}}`。
- `request_id` は `req_` で始まる識別子であり、同時実行中の要求で重複してはならない。応答body内のIDも外側と一致させる。
- `path` は相対パスのみ許可し、スキーム・ホスト・フラグメント・パス走査を拒否する。HTTPメソッドと内部APIのパスは個別に許可リストで制限する。
- トンネル未接続時は公開APIで `503` と `error.code=tunnel_unavailable` を返す。接続中の応答期限超過は `504` と `error.code=tunnel_timeout` を返す。いずれも `request_id` を含める。
- 要求期限は初期値30秒。同時WSS接続は初期値1本。異常切断時の再接続は有効化中に限り指数バックオフ（初回1秒、最大30秒）とする。
- WSS接続を閉じた際は保留中の要求をすべて終了する。特に書き込み要求は自動再送しない。
- systemdサービスは初期状態で無効（自動起動禁止）とし、利用開始・終了時にFW内管理者が手動で開始・停止する。サービス起動中のみ再接続を許可する。

## 10. 初期実装の分割

1. メッセージスキーマ・認証・許可リストの単体テストと実装。
2. FW内ローカル構成でWSS受入口・クライアントを実装し、要求対応付けと切断処理を結合テスト。
3. Public Gatewayの既存HTTP中継をWSS中継へ切り替え、公開API契約の整合性をテスト。
4. nginx・systemdの設定を追加し、内部環境、本番Ubuntu、ChatGPTの順で検証する。


本書は設計文書であり、実装・テスト合格を示すものではない。

---

[目次](../目次.md) > 仕様 > Reverse WebSocket 詳細設計
