<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000003Z-LGG-GITLAB-PROXY
lang: ja-JP
canonical_title: GitLab Reverse Proxy
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > GitLab Reverse Proxy

# GitLab Reverse Proxy

## 1. 目的

GitLab を：

```text
/gitlab
```

subpath 配下で reverse proxy 運用する。

対象：

- GitLab UI
- GitLab API
- login
- Cookie
- CSRF
- redirect

---

# 2. 前提条件

## 2.1 システム構成

```text
Internet
  ↓
Public Gateway (nginx)
  ↓ WireGuard
Private Bridge
  ↓
GitLab
```

---

## 2.2 GitLab external_url

GitLab は以下を前提とする。

```ruby
external_url "https://GITLAB_INTERNAL_HOST_EXAMPLE/gitlab"
```

---

## 2.3 relative_url_root

上記設定により GitLab は：

```text
/gitlab
```

prefix 配下で動作する。

そのため reverse proxy 側も：

```text
prefix aware
```

である必要がある。

---

# 3. reverse proxy 成立条件

# 3.1 trailing slash

## 必須

以下は trailing slash を一致させる。

```nginx
location /gitlab/
proxy_pass https://GITLAB_INTERNAL_ADDR_EXAMPLE/gitlab/;
```

---

## 禁止

以下は禁止。

```nginx
location /gitlab/
proxy_pass https://GITLAB_INTERNAL_ADDR_EXAMPLE;
```

---

## 理由

不整合により：

- redirect mismatch
- Cookie Path mismatch
- form action mismatch
- CSRF token mismatch

が発生する。

---

# 3.2 Host header

## 必須

```nginx
proxy_set_header Host GITLAB_INTERNAL_HOST_EXAMPLE;
```

---

## 理由

GitLab は：

- Host
- Origin
- CSRF token

を厳密に判定する。

---

# 3.3 X-Forwarded-Proto

## 必須

```nginx
proxy_set_header X-Forwarded-Proto https;
```

---

# 3.4 X-Forwarded-Ssl

## 必須

```nginx
proxy_set_header X-Forwarded-Ssl on;
```

---

# 3.5 X-Forwarded-Host

## 必須

```nginx
proxy_set_header X-Forwarded-Host $host;
```

---

# 3.6 X-Forwarded-Prefix

## 必須

```nginx
proxy_set_header X-Forwarded-Prefix /gitlab;
```

---

## 理由

GitLab に：

```text
/gitlab
```

prefix 配下で動作していることを通知する。

---

# 3.7 websocket

## 推奨

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

## 理由

GitLab UI 将来互換性。

---

# 4. self-signed certificate

## 現状

PoC 段階では：

```nginx
proxy_ssl_verify off;
```

を許可する。

---

## 将来方針

最終的には：

- internal CA
- verify_tls true

へ移行する。

---

# 5. nginx 設定

参照：

- [nginx 設定](07_nginx_設定.md)

---

# 6. 動作確認

## login URL

```text
http://PUBLIC_GATEWAY_HOST_EXAMPLE/gitlab/users/sign_in
```

---

## 推奨

- シークレットウィンドウ
- Cookie削除

---

# 7. 確認項目

# 7.1 login

以下成立。

- login 成功
- 422 不発
- redirect loop 無し

---

# 7.2 URL

以下を維持する。

```text
/gitlab/users/sign_in
```

---

## 禁止状態

以下は禁止。

```text
/users/sign_in
```

---

# 7.3 CSS / JS

以下成立。

- CSS 崩れ無し
- JS エラー無し

---

# 7.4 Cookie

Cookie の：

- Path
- Secure
- Domain

を確認。

---

# 8. 問題発生時

# 8.1 422 The change you requested was rejected

## 確認

- X-Forwarded-Prefix
- Host header
- external_url
- Cookie Path
- trailing slash

---

# 8.2 redirect loop

## 確認

- proxy_pass
- relative_url_root
- HTTPS 判定

---

# 8.3 CSS 崩れ

## 確認

- static asset path
- /gitlab prefix

---

# 9. ログ確認

# nginx

```bash
sudo tail -100 /var/log/nginx/local-gitlab-gateway.error.log
```

---

# GitLab

```bash
sudo gitlab-ctl tail
```

---

# 10. 運用方針

## docs 正本

本システムでは：

```text
docs を正本
```

とする。

---

## 実機 workaround 禁止

以下は禁止。

- 実機のみ修正
- docs 未更新
- example 未更新

---

## OSS 検証

本環境は：

```text
第三者が同一手順で構築可能
```

であることを検証対象とする。

---

# 11. 関連ドキュメント

- [nginx 設定](07_nginx_設定.md)
- [動作確認](10_動作確認.md)
- [トラブルシュート](12_トラブルシュート.md)

---

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > GitLab Reverse Proxy
