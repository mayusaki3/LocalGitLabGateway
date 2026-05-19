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

nginx reverse proxy を使用し、LocalGitLabGateway API および GitLab reverse proxy を外部公開する。

## 2. 設定ファイル配置

```bash
sudo cp \
  deploy/nginx/local-gitlab-gateway.conf.example \
  /etc/nginx/sites-available/local-gitlab-gateway.conf
```

## 3. nginx 設定有効化

```bash
sudo ln -s \
  /etc/nginx/sites-available/local-gitlab-gateway.conf \
  /etc/nginx/sites-enabled/local-gitlab-gateway.conf
```

## 4. GitLab Reverse Proxy

```nginx
location /gitlab/ {
    proxy_pass https://10.20.30.2/gitlab/;

    proxy_ssl_verify off;

    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Ssl on;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Prefix /gitlab;

    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
}
```

## 5. 構文確認

```bash
sudo nginx -t
```

## 6. reload

```bash
sudo systemctl reload nginx
```

## 7. 動作確認

```bash
curl -i http://127.0.0.1/api/health
curl -i http://127.0.0.1/gitlab/users/sign_in
```

## 8. ログ確認

```bash
sudo tail -n 50 /var/log/nginx/local-gitlab-gateway.access.log
sudo tail -n 50 /var/log/nginx/local-gitlab-gateway.error.log
```

---

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > nginx 設定
