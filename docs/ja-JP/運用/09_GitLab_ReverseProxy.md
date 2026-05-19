<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000003Z-LGG-GITLAB-PROXY
lang: ja-JP
canonical_title: GitLab Reverse Proxy
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用 > [運用目次](./運用目次.md) > GitLab Reverse Proxy

# GitLab Reverse Proxy

## external_url

GitLab の subpath 構成を使用する。

```ruby
external_url "https://<PRIVATE_GITLAB_HOST>/gitlab"
```

## login URL

```text
http://<PUBLIC_SERVER_IP>/gitlab/users/sign_in
```

## 現在の問題

```text
422 The change you requested was rejected
```

## 原因候補

- X-Forwarded header
- subpath prefix
- proxy_pass path
- Host header
- CSRF
- Cookie

## 確認コマンド

```bash
sudo gitlab-ctl tail nginx
sudo gitlab-ctl tail gitlab-rails
```

## 関連ドキュメント

- [nginx 設定](07_nginx_設定.md)

## 動作確認

```bash
curl -i http://127.0.0.1/gitlab/users/sign_in
```

推奨:

- シークレットウィンドウ
- Cookie削除

---

[目次](../目次.md) > 運用 > [運用目次](./運用目次.md) > GitLab Reverse Proxy
