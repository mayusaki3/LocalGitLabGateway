<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000007Z-LGG-API-CHECK
lang: ja-JP
canonical_title: API確認
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用 > [運用目次](./運用目次.md) > API確認

# API確認

## health

```powershell
Invoke-WebRequest `
  -Uri "http://<PUBLIC_SERVER_IP>/api/health" `
  -Headers @{ "X-API-Key" = $PublicApiKey }
```

## projects

```powershell
Invoke-RestMethod `
  -Uri "http://<PUBLIC_SERVER_IP>/api/v1/gitlab/projects?page=1&per_page=3" `
  -Headers @{ "X-API-Key" = $PublicApiKey }
```

## repository tree

```powershell
Invoke-RestMethod `
  -Uri "http://<PUBLIC_SERVER_IP>/api/v1/gitlab/projects/21/repository/tree?page=1&per_page=20" `
  -Headers @{ "X-API-Key" = $PublicApiKey }
```

## repository file

```powershell
Invoke-RestMethod `
  -Uri "http://<PUBLIC_SERVER_IP>/api/v1/gitlab/projects/21/repository/files/README.md" `
  -Headers @{ "X-API-Key" = $PublicApiKey }
```

---

[目次](../目次.md) > 運用 > [運用目次](./運用目次.md) > API確認
