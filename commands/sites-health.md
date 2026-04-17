---
description: 扫描 services.ts 所有子域 HTTP/Access/Navbar 状态，输出诊断矩阵
---

一键健康探针 — 验证 `~/Dev/website/lib/services.ts` 里所有子域的可达性、CF Access 一致性、navbar 部署情况。

## 用法

```bash
/sites-health [--filter PREFIX1,PREFIX2] [--no-traffic] [--json]
```

- `--filter` — 逗号分隔子域前缀（如 `dashboard,cc,auggie`）
- `--no-traffic` — 跳过 7 天流量聚合
- `--json` — 机器可读输出（供 `/site-rename` 等命令消费）

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/sites_health.py "$@"
```

## 输出解读

| 符号 | 含义 |
|---|---|
| ✅ 200 | 站点公开可达 |
| 🔒 302 | CF Access 在守门（正常） |
| ❌ {code} | 返回 4xx/5xx 或 timeout |
| 🌐 | 从 edge 看是公开访问 |
| 🔒 | CF Access 302 到 `cloudflareaccess.com` |
| ⚠ | `services.ts` 声明的 accessType 与实际不符 |
| ✓ | edge curl 抓到 `class="tlz-nav"` |
| ✓(local) | edge 探测不到（Access 阻挡），SSH→origin 抓到 navbar |
| ✗ | 抓了 HTML 但无 navbar — 真缺失 |
| ? | SPA（Streamlit）或无 port 的 Access 站，HTTP 探测不出，需人肉浏览器验 |

## 限制

1. **Streamlit 全 SPA**：初始 HTML 不含 navbar（JS mount 后才注入），本工具永远给 `?`
2. **7d Hits 暂不可用**：VPS nginx 默认 combined log_format 不含 `$host`；开启需改 `/etc/nginx/nginx.conf` 的 log_format 加 `$host` 字段
3. `auggie` / `panel` / `sub` 等 API 站返回 405/400 属正常（GET `/` 不被支持），不代表服务死

## 规则

- 凭证无需（curl + ssh，ssh key 默认加载）
- 并发 8 路 curl + 并发 6 路 SSH，跑完 27 站约 15–30 秒
- 支持只查子集：例如 `/sites-health --filter hydro` 只扫 hydro-\*
