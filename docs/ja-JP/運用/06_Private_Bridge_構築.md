<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000011Z-LGG-PRIVATE
lang: ja-JP
canonical_title: Private Bridge 構築
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用 > Private Bridge 構築

# Private Bridge 構築

## 対象ホスト

- <PRIVATE_GITLAB_HOST>
- WireGuard: 10.20.30.2

## 稼働サービス

- GitLab
- local-gitlab-gateway-private
- WireGuard

## internal health確認

```bash
curl -i http://127.0.0.1:8081/internal/health
```

## GitLab Version API

```text
/internal/gitlab/version
```

## 関連ドキュメント

- [WireGuard 構築](04_WireGuard_構築.md)
- [systemd 設定](08_systemd_設定.md)

---

[目次](../目次.md) > 運用 > Private Bridge 構築
