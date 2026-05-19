<!--
HLDocS:LLM-MANAGED
doc_id: doc-20260519-000004Z-LGG-WIREGUARD
lang: ja-JP
canonical_title: WireGuard 構築
document_type: note
canonical_document: true
-->

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > WireGuard 構築

# WireGuard 構築

## 1. 使用アドレス

| 名称 | WireGuard IP |
| --- | --- |
| Public Gateway Host | 10.20.30.1/24 |
| Private GitLab Host | 10.20.30.2/24 |

## 2. インストール

```bash
sudo apt install -y wireguard
```

## 3. 鍵生成

### Public Gateway Host

```bash
wg genkey | sudo tee /etc/wireguard/public-gateway-private.key | wg pubkey | sudo tee /etc/wireguard/public-gateway-public.key
```

### Private GitLab Host

```bash
wg genkey | sudo tee /etc/wireguard/private-gitlab-private.key | wg pubkey | sudo tee /etc/wireguard/private-gitlab-public.key
```

## 4. 設定ファイル

### Public Gateway Host

```bash
sudo cp \
  deploy/wireguard/public-gateway-wg0.conf.example \
  /etc/wireguard/wg0.conf
```

### Private GitLab Host

```bash
sudo cp \
  deploy/wireguard/private-gitlab-wg0.conf.example \
  /etc/wireguard/wg0.conf
```

## 5. 起動

```bash
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```

## 6. 疎通確認

```bash
ping -c 3 10.20.30.2
curl -i http://10.20.30.2:8081/internal/health
```

## 7. 状態確認

```bash
sudo wg show
ip addr show wg0
systemctl status wg-quick@wg0 --no-pager
```

---

[目次](../目次.md) > 運用手順 > [運用手順目次](./運用手順目次.md) > WireGuard 構築
