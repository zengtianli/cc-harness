---
description: 刷新 auggie dashboard — 拉最新 GitHub repo 清单 → scan.json → 同步到 VPS
---

# /auggie — 刷新 auggie dashboard

$ARGUMENTS 忽略。默认跑 `dash`（之前的 `fix` 子命令已废，`_files.md` 机制已删）。

## dash — 3 步刷新链路

1. **拉 GitHub 最新清单**
   ```bash
   python3 ~/Dev/labs/auggie-dashboard/lib/scanner.py \
       ~/Dev/labs/auggie-dashboard/data/scan.json
   ```
   产出当前所有 repo（公开 + 私有）的 7 字段 JSON。

2. **同步到 ops-console 消费者**
   ```bash
   cp ~/Dev/labs/auggie-dashboard/data/scan.json \
      ~/Dev/stations/ops-console/data/auggie-scan.json
   ```

3. **scp 到 VPS**
   ```bash
   scp ~/Dev/stations/ops-console/data/auggie-scan.json \
       root@104.218.100.67:/opt/ops-console/data/auggie-scan.json
   ```
   不 rebuild Next.js，页面 `revalidate: 60` 60s 内自动拿到新数据。

## 验证

```bash
curl -s --noproxy '*' https://dashboard.tianlizeng.cloud/api/auggie \
  | python3 -c "import json, sys; d=json.load(sys.stdin); print(len(d['repos']))"
```

## 数据 schema（7 字段）

```json
{
  "name": "dotfiles",
  "visibility": "private",
  "language": "Shell",
  "pushed_at": "2026-04-20T12:31:39Z",
  "description": "dotfiles for macOS",
  "html_url": "https://github.com/zengtianli/dotfiles",
  "archived": false
}
```

页面在 `dashboard.tianlizeng.cloud/auggie`。
