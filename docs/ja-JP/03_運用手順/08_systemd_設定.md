<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000005Z-LGG-SYSTEMD
lang: ja-JP
canonical_title: systemd 設定
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > systemd 設定

# systemd 設定

## 1. Public Gateway

```bash
sudo cp \
  deploy/systemd/local-gitlab-gateway-public.service.example \
  /etc/systemd/system/local-gitlab-gateway-public.service
```

## 2. Private Bridge

```bash
sudo cp \
  deploy/systemd/local-gitlab-gateway-private.service.example \
  /etc/systemd/system/local-gitlab-gateway-private.service
```

## 3. daemon-reload

```bash
sudo systemctl daemon-reload
```

## 4. enable

```bash
sudo systemctl enable local-gitlab-gateway-public
sudo systemctl enable local-gitlab-gateway-private
```

## 5. start

```bash
sudo systemctl start local-gitlab-gateway-public
sudo systemctl start local-gitlab-gateway-private
```

## 6. 状態確認

```bash
systemctl status local-gitlab-gateway-public --no-pager
systemctl status local-gitlab-gateway-private --no-pager
```

## 7. journalctl

```bash
journalctl -u local-gitlab-gateway-public -n 50 --no-pager
journalctl -u local-gitlab-gateway-private -n 50 --no-pager
```

---

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > systemd 設定
