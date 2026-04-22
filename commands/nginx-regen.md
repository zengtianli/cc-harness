---
description: 从 services.ts 重新生成所有动态子域的 nginx vhost 文件（不推送 VPS）
---

扫 `~/Dev/stations/website/lib/services.ts` 里所有带 `port` 字段的子域（hydro-* / audiobook / cclog / dockit / cc-options / dashboard），渲染 nginx vhost 配置到 `~/Dev/tools/configs/nginx/out/<name>.conf`。

**不推送 VPS** —— 只生成本地文件。用户审阅 diff 后自行 `rsync` 或 `scp` 到 VPS。

## 用法

```bash
/nginx-regen                # 全部子域
/nginx-regen hydro-annual   # 单个
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/services_to_nginx.py
```

单个：

```bash
python3 ~/Dev/devtools/lib/tools/services_to_nginx.py hydro-annual
```

## 端口约定

| 端口类型 | 公式 | 示例（hydro-capacity port 8511） |
|---|---|---|
| legacy (Streamlit) | services.ts 的 `port` | 8511 |
| api (FastAPI) | legacy + 100 | 8611 |
| web (Next.js) | legacy − 5400 | 3111 |
| 例外 | audiobook api = 9200 | — |

## 后续

检查 diff：

```bash
diff -r ~/Dev/tools/configs/nginx/out/ <(ssh root@104.218.100.67 'cat /etc/nginx/sites-enabled/*.conf')
```

推送：

```bash
rsync -avz ~/Dev/tools/configs/nginx/out/ root@104.218.100.67:/etc/nginx/sites-enabled/
ssh root@104.218.100.67 'nginx -t && systemctl reload nginx'
```

## 背景

前身是 `~/Dev/stations/web-stack/infra/nginx/render.py`，但它硬编码了 reorg 前的 `~/Dev/website/lib/services.ts` 路径（已失效）。2026-04-22 提升到 devtools，修正路径，统一输出到 `tools/configs/nginx/out/`。
