---
description: 检查 navbar.yaml 每个链接的存活状态 + 每个子域的 favicon / og:image / apple-touch-icon。输出 markdown 报告 + 非 0 退出码在有死链时触发。
---

每次改了 navbar.yaml / subdomains.yaml 后跑一次；会话收尾前跑一次。只读，没副作用。

## 用法

```bash
/nav-health                 # 全报告（leaf URLs + per-host assets）
/nav-health --links-only    # 只查 navbar leaf URLs
/nav-health --assets-only   # 只查 favicon / og:image
/nav-health --fail-on-warn  # warn 也算失败（CI 严格模式）
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/nav_health.py $ARGUMENTS
```

## 检查维度

### Leaf URLs（navbar.yaml 全部展开）

- `OK`  HTTP 200 + body > 500B + `<title>` 非 "loading"
- `AUTH` HTTP 302 + 条目标了 `access: cf-access`（预期，不算错）
- `WARN` 重定向但没标 access / 页面 title 是 loading / body 太薄
- `DEAD` 连不上 / 4xx / 5xx

### Per-host assets（每个 subdomain）

- `og:image` — 从根页面 HTML 抓 `<meta property="og:image">`，再 probe 目标 URL
- `favicon.ico` — 直接 probe
- `apple-touch-icon.png` — 直接 probe

## 什么时候跑

- 改 `entities/subdomains.yaml` / `navbar.yaml` / `relations/*.yaml` 后
- `/site-archive` / `/site-rename` / `/site-add` 之后
- 会话收尾前（`/handoff` 之前）
- 定期（可挂 cron / launchd）

## 不做

- 不修任何文件 / 配置
- 不尝试登录 CF Access（302 视为 auth-gated，健康）
- 不做深度 UI 检查（只看 HTML body + 基本 sanity）
- 修复由你自己决定（改 navbar.yaml 删死链 / 补 favicon / 加 og:image metadata）

## 当前已知常见问题类别

| 症状 | 可能原因 | 修复 |
|---|---|---|
| GitHub URL 404 | repo private 或不存在 | catalog.yaml 去掉 URL 或换 private 标记 |
| og:image 缺失（Next.js） | `app/layout.tsx` 没设 `metadata.openGraph.images` | 加 `openGraph: { images: [{ url: "..." }] }` |
| favicon.ico 404（Next.js） | `app/icon.png` / `public/favicon.ico` 没放 | 放一个 512×512 PNG 到 `app/icon.png` |
| `302 missing` on CF-Access 站 | 资产也被 Access 拦 | 允许匿名访问 `/favicon.ico`、`/_next/static/*` 路径规则
