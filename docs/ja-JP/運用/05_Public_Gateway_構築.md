<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000010Z-LGG-PUBLIC
lang: ja-JP
canonical_title: Public Gateway 構築
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用 > Public Gateway 構築

# Public Gateway 構築

## 対象ホスト

- AIChaBoServ
- <PUBLIC_SERVER_IP>

## 稼働サービス

- nginx
- local-gitlab-gateway-public
- WireGuard

## 起動確認

```bash
curl -i http://127.0.0.1:8080/health
```

## API入口

```text
/api/v1/gitlab/
```

## 関連ドキュメント

- [nginx 設定](07_nginx_設定.md)
- [systemd 設定](08_systemd_設定.md)

---

[目次](../目次.md) > 運用 > Public Gateway 構築
