---
description: 刷新 auggie dashboard — GitHub repo 列表 / workspace 注册表 / health 健康
---

# /auggie — 刷新 auggie dashboard

`$ARGUMENTS` 子命令：
- `dash`（默认）— 拉 GitHub repo 列表，刷新 ops-console 的 auggie scan 卡片
- `sync` — 重 build workspace 注册表 + retry-failed warmup + scp health.json，刷新 `/auggie/workspaces` 表
- `all` — 串跑 `dash` + `sync`

未传子命令 → 跑 `dash`。

---

## dash — GitHub repo 列表（3 步）

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

### 验证 dash
```bash
curl -s --noproxy '*' https://dashboard.tianlizeng.cloud/api/auggie \
  | python3 -c "import json, sys; d=json.load(sys.stdin); print(len(d['repos']))"
```

---

## sync — workspace 注册表 + health 数据（4 步）

刷新 `dashboard.tianlizeng.cloud/auggie/workspaces` 表（41 行 + 健康徽章）。

1. **rebuild auggie-workspaces.json**
   ```bash
   python3 ~/Dev/devtools/lib/tools/auggie_workspaces.py build
   python3 ~/Dev/devtools/lib/tools/auggie_workspaces.py audit  # 必须 0 退出
   ```

2. **retry-failed warmup**（仅重跑 status != 'ok' 的，保留已 ok）
   ```bash
   python3 ~/Dev/devtools/lib/tools/auggie_warmup.py run --retry-failed
   ```
   产出 `~/Dev/tools/configs/auggie-health.json`。预计耗时几分钟（视失败数量）。

3. **scp 到 VPS**
   ```bash
   scp ~/Dev/tools/configs/auggie-workspaces.json \
       ~/Dev/tools/configs/auggie-health.json \
       root@104.218.100.67:/opt/ops-console/data/
   ```

4. **验证 live**
   ```bash
   curl -fsSL "https://dashboard.tianlizeng.cloud/auggie/workspaces" \
     -o /dev/null -w "HTTP %{http_code}\n"
   # 预期 200
   ```

### sync 何时跑
- 改 `auggie-workspaces.yaml`（增删 workspace / 改 indexable）后必须跑
- warmup 失败重试（如 augment 后端节流恢复后）
- 周期性维护（建议每周 1 次）

---

## all — dash + sync 串跑

```bash
# 等价
/auggie dash
/auggie sync
```

完整一次刷新 dashboard 两个 auggie 页面。

---

## 数据 schema 快查

### scan.json（dash 数据）— 7 字段
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

### auggie-workspaces.json（sync 数据）
SSOT 源 `~/Dev/tools/configs/auggie-workspaces.yaml`，41 entries · 22 indexable。字段见 yaml 顶部 banner。

### auggie-health.json（sync 数据）
warmup 产出。每个 indexable workspace 1 record：`status / duration_s / avg_relevance / warmup_at / error`。

---

## 页面位置
- `dashboard.tianlizeng.cloud/auggie` — GitHub repo 列表（dash）
- `dashboard.tianlizeng.cloud/auggie/workspaces` — workspace 注册表 + 健康（sync）
