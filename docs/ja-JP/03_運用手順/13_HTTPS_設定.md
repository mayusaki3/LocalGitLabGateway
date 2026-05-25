<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260521-000001Z-LGG-HTTPS
lang: ja-JP
canonical_title: HTTPS 設定
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > HTTPS 設定

# HTTPS 設定

## 1. 目的

Public Gateway の外部公開 endpoint を HTTPS 必須にする。

LocalGitLabGateway は、社外からローカル GitLab へ安全にアクセスすることを目的とするため、HTTP での利用は禁止し、HTTP は HTTPS への redirect 専用とする。

---

# 2. 方針

## 2.1 HTTPS 必須

ブラウザおよび Git tool から Public Gateway へ接続する場合は、HTTPS を使用する。

```text
https://<PUBLIC_GATEWAY_HOST>/
```

---

## 2.2 HTTP 禁止

HTTP はサービス提供には使用しない。

Port 80 は以下の用途に限定する。

```text
HTTPS redirect
```

---

## 2.3 GitLab Reverse Proxy との関係

GitLab は HTTPS 前提で動作する。

そのため、nginx の GitLab reverse proxy では以下を維持する。

```nginx
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-Ssl on;
```

HTTP で Public Gateway へ接続すると、GitLab の Cookie / CSRF / redirect の整合が崩れ、ログイン後に 422 が発生する可能性がある。

---

# 3. 前提条件

## 3.1 repository 配置

LocalGitLabGateway repository が Public Host 上へ配置済みであること。

---

## 3.2 nginx 設定

以下が実施済みであること。

- [nginx 設定](07_nginx_設定.md)
- [GitLab Reverse Proxy](09_GitLab_ReverseProxy.md)

---

## 3.3 443/tcp

Public Host で 443/tcp が使用可能であること。

確認：

```bash
sudo ss -tlnp | grep :443
```

何も表示されない場合は、443/tcp は未使用である。

---

# 4. TLS 証明書作成

## 4.1 証明書配置ディレクトリ作成

Public Host 上で：

```bash
sudo mkdir -p /etc/nginx/ssl
```

---

## 4.2 self-signed certificate 作成

PoC では self-signed certificate を使用する。

```bash
sudo openssl req -x509 -nodes -days 365 \
  -newkey rsa:4096 \
  -keyout /etc/nginx/ssl/local-gitlab-gateway.key \
  -out /etc/nginx/ssl/local-gitlab-gateway.crt
```

---

## 4.3 Common Name

Common Name には `<PUBLIC_GATEWAY_HOST>` に設定する値を指定する。

公開ホスト名を使用する場合は公開ホスト名を指定する。

公開 IP アドレスで検証する場合は公開 IP アドレスを指定する。

---

# 5. nginx 設定反映

## 5.1 設定ファイルコピー

Public Host 上で：

```bash
cd /opt/local-gitlab-gateway

sudo cp \
  deploy/nginx/local-gitlab-gateway.conf.example \
  /etc/nginx/sites-available/local-gitlab-gateway.conf
```

---

## 5.2 設定ファイル編集

```bash
sudo nano /etc/nginx/sites-available/local-gitlab-gateway.conf
```

---

## 5.3 プレースホルダー置換

以下を実環境値へ置換する。

```text
<PUBLIC_GATEWAY_HOST>
<GITLAB_INTERNAL_HOST>
```

標準 WireGuard 構成では、Private GitLab Host の WireGuard IP は `10.20.30.2` である。

WireGuard 構成を変更した場合のみ、`proxy_pass` の `10.20.30.2` を変更する。

---

# 6. nginx verify

## 6.1 構文確認

```bash
sudo nginx -t
```

---

## 6.2 成功条件

以下が表示されること。

```text
syntax is ok
test is successful
```

---

# 7. nginx reload

```bash
sudo systemctl reload nginx
```

---

# 8. 動作確認

## 8.1 HTTP redirect

以下へアクセスする。

```text
http://<PUBLIC_GATEWAY_HOST>/gitlab/users/sign_in
```

期待結果：

```text
https://<PUBLIC_GATEWAY_HOST>/gitlab/users/sign_in
```

へ redirect されること。

---

## 8.2 HTTPS login

シークレットウィンドウで以下へアクセスする。

```text
https://<PUBLIC_GATEWAY_HOST>/gitlab/users/sign_in
```

---

## 8.3 確認項目

以下が成立すること。

- login page 表示
- login 成功
- 422 不発
- redirect loop 無し
- /gitlab prefix 維持
- CSS 崩れ無し

---

# 9. 問題発生時

## 9.1 422 発生

以下を確認する。

- ブラウザ接続が HTTPS であること
- `X-Forwarded-Proto https` が設定されていること
- `X-Forwarded-Ssl on` が設定されていること
- GitLab `external_url` と `proxy_set_header Host` が一致していること
- Cookie Path が `/gitlab` であること

---

## 9.2 証明書警告

self-signed certificate を使用する場合、ブラウザに証明書警告が表示される。

PoC では許容する。

正式運用では、公的証明書または組織内 CA の証明書を使用する。

---

# 10. 将来方針

正式運用では以下へ移行する。

- 公的証明書または組織内 CA
- 証明書更新手順
- HSTS 設定
- `verify_tls: true`

---

# 関連ドキュメント

- [nginx 設定](07_nginx_設定.md)
- [GitLab Reverse Proxy](09_GitLab_ReverseProxy.md)
- [動作確認](10_動作確認.md)
- [トラブルシュート](12_トラブルシュート.md)

---

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > HTTPS 設定
