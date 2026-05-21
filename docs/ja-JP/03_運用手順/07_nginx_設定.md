<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000002Z-LGG-NGINX
lang: ja-JP
canonical_title: nginx 設定
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > nginx 設定

# nginx 設定

## 1. 目的

nginx reverse proxy を使用し、
以下を外部公開する。

- LocalGitLabGateway API
- GitLab Reverse Proxy

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

## 2.2 repository 配置

LocalGitLabGateway repository が
Public Host 上へ配置済みであること。

---

# 3. 開発版を使用する場合

Public Host 上で：

```bash
cd /opt/local-gitlab-gateway

git checkout develop
git pull
```

develop ブランチを利用する場合のみ実施する。

---

# 4. nginx 設定ファイル配置

## 4.1 設定ファイルコピー

Public Host 上で：

```bash
sudo cp \
  deploy/nginx/local-gitlab-gateway.conf.example \
  /etc/nginx/sites-available/local-gitlab-gateway.conf
```

---

## 4.2 プレースホルダー置換

以下を実環境値へ置換。

```text
<PUBLIC_GATEWAY_HOST>
<GITLAB_INTERNAL_ADDR>
<GITLAB_INTERNAL_HOST>
```

---

## 4.3 確認

以下を確認。

- GitLab internal address
- GitLab internal host
- proxy_pass trailing slash
- /gitlab prefix

---

# 5. nginx 設定有効化

## 5.1 symbolic link 作成

```bash
sudo ln -s \
  /etc/nginx/sites-available/local-gitlab-gateway.conf \
  /etc/nginx/sites-enabled/local-gitlab-gateway.conf
```

---

## 5.2 既存 link 存在時

既存 link が存在する場合：

```bash
sudo rm \
  /etc/nginx/sites-enabled/local-gitlab-gateway.conf
```

後に再作成する。

---

# 6. nginx verify

## 6.1 構文確認

```bash
sudo nginx -t
```

---

## 6.2 成功条件

以下表示。

```text
syntax is ok
test is successful
```

---

## 6.3 失敗時確認

以下を確認。

- semicolon
- duplicate directive
- proxy_pass
- trailing slash
- symbolic link

---

# 7. nginx reload

## 7.1 reload

```bash
sudo systemctl reload nginx
```

---

## 7.2 注意

原則：

```text
reload
```

を使用する。

restart は最終手段。

---

# 8. 動作確認

## 8.1 API

```bash
curl -i http://127.0.0.1/api/health
```

---

## 8.2 GitLab login

ブラウザで以下へアクセス。

```text
http://<PUBLIC_GATEWAY_HOST>/gitlab/users/sign_in
```

---

## 8.3 推奨

- シークレットウィンドウ
- Cookie削除

---

# 9. 確認項目

## 9.1 login

以下成立。

- login page 表示
- login 成功
- 422 不発

---

## 9.2 redirect

以下成立。

- redirect loop 無し
- /gitlab prefix 維持

---

## 9.3 CSS / JS

以下成立。

- CSS 崩れ無し
- JS エラー無し

---

# 10. ログ確認

# nginx access log

```bash
sudo tail -50 \
  /var/log/nginx/local-gitlab-gateway.access.log
```

---

# nginx error log

```bash
sudo tail -50 \
  /var/log/nginx/local-gitlab-gateway.error.log
```

---

# GitLab log

```bash
sudo gitlab-ctl tail
```

---

# 11. 問題発生時

## 11.1 422 発生

以下確認。

- X-Forwarded-Prefix
- Host header
- external_url
- Cookie Path
- trailing slash

---

## 11.2 redirect loop

以下確認。

- proxy_pass
- relative_url_root
- HTTPS 判定

---

## 11.3 CSS 崩れ

以下確認。

- static asset path
- /gitlab prefix

---

# 12. 運用方針

## docs 正本

本システムでは：

```text
docs を正本
```

とする。

---

## OSS 検証

本環境は：

```text
第三者が同一手順で構築可能
```

であることを検証対象とする。

---

# 関連ドキュメント

- [GitLab Reverse Proxy](09_GitLab_ReverseProxy.md)

---

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > nginx 設定
