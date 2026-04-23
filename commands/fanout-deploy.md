---
description: 并行多站部署编排 — 给每个目标 repo 起独立 subagent，各自 edit+build+deploy+verify，汇总状态表
---

跨站 SSOT 同步或批量变更时使用。比 `/deploy-changed` 更主动：你指定变更规格，编排器为每个站并行执行完整的 edit → build → deploy → verify 流程。

## 用法

```
/fanout-deploy "<变更规格>" --repos <repo1>,<repo2>,...
/fanout-deploy "<变更规格>" --all
/fanout-deploy "<变更规格>" --repos <repo1>,<repo2> --dry-run
```

- `<变更规格>` — 自然语言描述要做什么，例如「把 navbar 版本号从 2.1 改到 2.2」
- `--repos` — 逗号分隔的 repo 路径（相对 ~/Dev/）或绝对路径
- `--all` — 从 `~/Dev/stations/website/lib/services.ts` 读取所有站点
- `--dry-run` — 只打印每站的变更 diff，不执行 deploy

## 适用场景

| 场景 | 示例 |
|---|---|
| navbar/menus SSOT 改完，推送所有消费者 | `--all` |
| 指定几个站同步同一个改动 | `--repos hydro-annual,hydro-capacity,hydro-runoff` |
| 验证跨站改动影响范围（不部署） | `--dry-run` |

## 和现有命令的区别

| 命令 | 适合什么 |
|---|---|
| `/deploy` | 当前目录单站，有 deploy.sh |
| `/deploy-changed` | git diff 自动检测受影响站，批量部署 |
| `/ship-site` | 新站首次上线（含 CF DNS/Access 创建） |
| **`/fanout-deploy`（本命令）** | 已知要改哪些站，并行 edit+deploy+verify |

## 执行流程

### Step 0 — Pre-flight
- 解析 `--repos` 或 `--all`，列出目标站点清单
- 验证每个 repo 路径存在
- 打印将要执行的操作，暂停等用户确认（`--dry-run` 跳过）

### Step 1 — 并行 fanout
为每个目标 repo **同时**起一个 subagent（`run_in_background: true`），每个 subagent 接收：
- repo 绝对路径
- 变更规格
- 该站的验证 URL（从 services.ts 自动推断）

每个 subagent 执行：
1. 应用变更规格到该 repo
2. 如有 `deploy.sh` → `bash deploy.sh`；如为 web-stack app → `pnpm build`
3. `curl -sI <验证URL>` 检查 HTTP 状态
4. 返回结构化结果：`{repo, status, commit_sha, deployed_url, http_status, issues}`

### Step 2 — 汇总
编排层收集所有 subagent 返回，输出状态表：

```
## Fanout Deploy Results

| Repo              | Status  | Commit     | Live URL                      | HTTP |
|-------------------|---------|------------|-------------------------------|------|
| hydro-annual      | ✅ done | abc1234    | hydro-annual.tianlizeng.cloud | 302  |
| hydro-capacity    | ❌ fail | —          | —                             | err  |
| stations/web-stack| ✅ done | def5678    | stack.tianlizeng.cloud        | 302  |
```

失败项列出 `issues` 字段，提示下一步排查路径。

## 规则

- 每个 subagent 独立运行，互不阻塞 — 一个站失败不影响其他站
- `--dry-run` 输出每站的 diff，不执行任何 deploy 或 commit
- 变更规格如有歧义，subagent 先问编排层，再问用户
- 凭证在 `~/.personal_env`，subagent 自动继承，不问用户

## 参考

- services.ts：`~/Dev/stations/website/lib/services.ts`（站点注册表）
- 底层部署：`~/Dev/stations/web-stack/infra/deploy/deploy-batch.sh`
- 单站验证：`/sites-health --filter <name>`
