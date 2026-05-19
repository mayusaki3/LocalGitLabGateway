# LocalGitLabGateway

LocalGitLabGateway は、外部公開された Linux サーバーを経由して、ファイアウォール内の Linux サーバー上で稼働する GitLab を Git や ChatGPT から安全に操作するためのゲートウェイツール群です。

## 構成要素

| 名称 | 役割 |
| --- | --- |
| Public Gateway Host | インターネット側から到達可能な Linux サーバー。Git や ChatGPT からの要求を受け付ける公開側ホスト。 |
| Public Gateway Service | Public Gateway Host 上で動作するサービス。認証、要求検証、中継、監査ログ記録を担当する。 |
| Private GitLab Host | ファイアウォール内に配置された Linux サーバー。GitLab と Private Bridge Agent が動作する内部側ホスト。 |
| Private Bridge Agent | Private GitLab Host 上で動作するエージェント。Public Gateway Service から許可された要求を受け取り、GitLab API を代理実行する。 |
| Managed GitLab | Private GitLab Host 上で稼働する操作対象 GitLab。 |
| ChatGPT Operation Profile | ChatGPT に与える接続先、認証、操作範囲、禁止事項、API仕様をまとめた情報セット。 |

## 通信方式

```text
ChatGPT
  ↓ HTTPS
Public Gateway Service
  ↓ WireGuard VPN
Private Bridge Agent
  ↓ GitLab REST API v4
Managed GitLab
```

## ドキュメント

本ドキュメントは、[HLDocS規約](https://github.com/mayusaki3/HLDocS) に準拠しています。

- [目次](docs/ja-JP/目次.md)
- [運用手順目次](docs/ja-JP/03_運用手順/運用手順目次.md)

---
© 2026 LocalGitLabGateway
