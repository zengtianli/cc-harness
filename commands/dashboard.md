Dashboard 数据维护 + 部署。按页面刷新数据或全量更新。

## 参数

$ARGUMENTS 指定页面：

### `repos` — 刷新 Repos 页面数据
1. 调用 `/repo-map scan`（发现新 repo、检查路径一致性）
2. 调用 `/pull repo-dashboard`（拉最新代码）
3. 输出 repo-map.json 变更摘要

### `tasks` — 刷新 Tasks 页面数据
1. 调用 `/scan`（扫描 CC 会话 → tasks.json）
2. 输出任务状态分布（active/completed/stale）

### `vps` — 检查 VPS 页面数据
1. 调用 `/vps-status`（服务/端口/磁盘/内存/Docker）
2. 输出异常项（如果都正常就一行 ✅）

### `app` — 部署 dashboard 本身
1. `cd ~/Dev/repo-dashboard`
2. 调用 `/deploy`
3. 验证 https://dashboard.tianlizeng.cloud

### 无参数 — 全量维护
按顺序执行：repos → tasks → vps → app
每步输出一行状态，最终汇总表：

```
✅ repos    repo-map.json up to date (29 repos)
✅ tasks    12 tasks scanned (3 active, 7 completed, 2 stale)
⚠️  vps      disk usage 82%
✅ app      deployed → https://dashboard.tianlizeng.cloud
```

## 调用的原子命令

- `/repo-map` — repo 注册表管理
- `/pull` — git pull
- `/scan` — CC 会话扫描
- `/vps-status` — VPS 巡检
- `/deploy` — 通用部署
