---
description: 并行多 repo 重构编排 — 每个 repo 一个 subagent 独立 worktree，audit 绿才 commit，supervisor 汇总后分批 deploy。比 /fanout-deploy 多一层 audit gate 和 worktree 隔离。
---

跨 repo 批量重构时使用。和 `/fanout-deploy` 的区别：本命令专为**重构改动**设计，必须每个 repo 在独立 worktree 里跑完整 audit 后才允许 commit，绝不绕开质量闸。

## 用法

```
/fanout-refactor "<重构规格>" --repos <repo1>,<repo2>,... [--deploy]
/fanout-refactor "<重构规格>" --all [--deploy]
/fanout-refactor "<重构规格>" --repos <repo1>,<repo2> --dry-run
```

- `<重构规格>` — 自然语言描述，例如「把所有 api.py 的 df_to_json_safe 调用换成 df_to_json_v2」「统一把 legacy useEffect 迁移到 useLayoutEffect」
- `--repos` — 逗号分隔的 repo 路径（相对 `~/Dev/`）或绝对路径
- `--all` — 从 `~/Dev/stations/website/lib/services.ts` 读全部站
- `--deploy` — audit 绿的 repo 自动触发 `/deploy`（默认只 commit + push，部署留给人类决定）
- `--dry-run` — 每 repo 只 patch + audit，不 commit

## 和现有命令的区别

| 命令 | 适合 | audit gate | worktree |
|---|---|---|---|
| `/deploy` | 当前目录单站 | ✗ | ✗ |
| `/deploy-changed` | git diff 扇出批量部 | ✗ | ✗ |
| `/ship-site` | 新站首次上线 | ✗ | ✗ |
| `/fanout-deploy` | 已知要改哪些站，并行 edit+deploy | ✗ | ✗ |
| **`/fanout-refactor`**（本命令） | **重构类改动，严格 audit 闸 + worktree 隔离** | ✓ | ✓ |

## 适用场景

- 共享库 API 升级，需要改 N 个调用方
- 依赖版本批量升级 + 测试回归
- Lint 规则收紧，批量修正所有 repo
- 统一代码风格 / 引入新 helper 替换旧模式
- 架构级 rename / 移文件路径

## 执行流程

### Step 0 — Pre-flight

- 解析 `--repos` 或 `--all` → 目标 repo 清单
- 对每个 repo 检查：
  - 存在 `.git`
  - 工作区干净（`git status --porcelain` 空）
  - 有 `origin` 远端
  - 有可执行的 audit 入口（`/audit` `/menus-audit` `/api-smoke` 视 repo 类型）
- 任一 repo 失败 → 报告清单，不继续（不做破坏性操作）

### Step 1 — Fan-out（一个 message 里起 N 个 Agent）

对每个目标 repo，并行启动一个 **Task Agent**（`general-purpose` 或专用 subagent），每个 Agent 拿到：

- repo 路径（作为独立 git worktree 挂到 `~/Dev/.worktrees/fanout-<timestamp>/<repo>`）
- 完整 `<重构规格>`（逐字传递，不复述）
- Audit 入口命令（Plan 模式决定具体跑哪个 audit：/audit / /menus-audit / /api-smoke / typecheck / build / 单元测试）
- 明确硬规则：**audit 不绿禁止 commit**；失败时把诊断写到 `<worktree>/FANOUT_FAIL.md`

单 Agent 内部流程：

```
1. cd worktree
2. 按规格 Edit 代码
3. 跑 audit 入口：
   - hydro-*-web → pnpm typecheck && build
   - web-stack services → /api-smoke <name> --compute
   - 静态站 → /menus-audit 对应维度
   - 任何 repo → /audit
4. 绿 → git add -A && git commit -m "<规格>"
   不绿 → 写 FANOUT_FAIL.md，不 commit
5. 返回状态：{ repo, passed, diff_summary, audit_output, fail_reason? }
```

并行性硬规则：
- 同一个 message 内必须 fan-out 所有 Agent（不允许串行发起）
- Agent 独立 worktree，不相互写同一工作目录

### Step 2 — Supervisor 汇总

所有 Agent 返回后，主会话（supervisor）做：

- **状态矩阵**：渲染表格 `| repo | passed | files changed | loc +/- | audit summary | next step |`
- **diff 汇总**：每 repo 列 3-5 行关键改动摘要（来自 Agent 的 diff_summary）
- **分组**：
  - A · audit 绿 → 候选 push
  - B · audit 红 → 保留 worktree，列 fail_reason，需人工介入
  - C · 零改动 → 规格在本 repo 不适用，自动跳过
- **用户决策点**：输出矩阵后 **AskUserQuestion**：「A 组 N 个 repo 已 audit 绿，是否 push？是否 `--deploy`？」

### Step 3 — Push + 可选 Deploy

用户批准后：

- A 组每 repo：`cd <worktree> && git push`，然后把 worktree merge 回主 repo 分支（或保留为 PR 供 review）
- 若 `--deploy` 且 repo 有 deploy 入口 → 在主工作区（不是 worktree）触发 `/deploy <name>`
- B 组 worktree 保留，在报告末尾给 `cd <path>` 提示让人工跟进
- C 组 worktree 自动清理

### Step 4 — 验收

- 对 A 组里实际 deploy 了的 repo 跑 `/sites-health` 或对应 verify
- 输出最终报告：`N 个成功 push / M 个已 deploy / K 个 audit 红待人工 / X 个零改动`
- 更新任务列表 / HANDOFF（若是大改动）

## 硬规则

- **audit 不绿禁 commit**，绝不 `--no-verify`
- **worktree 隔离**，不在主工作区改（防污染未决工作）
- **全局 fan-out**，不允许串行起 Agent
- **破坏性确认门**：Step 2 后必 AskUserQuestion 让用户拍板 push / deploy
- **失败留痕**：失败 repo 的 worktree + FANOUT_FAIL.md 必须保留到用户确认后才清

## 常见失败与处理

| 失败 | 现象 | 处理 |
|---|---|---|
| worktree 创建失败 | `fatal: '<name>' is already checked out` | 先 `git worktree prune` 或换 `--worktree-dir` |
| audit 命令找不到 | repo 无 /audit 入口 | Step 0 时跳过，不纳入扇出 |
| 规格模糊导致 Agent 各改各的 | diff_summary 差异大 | Plan mode 重审规格；可先 `--dry-run` 在 2 repo 验证 |
| push 被 protected branch 拒绝 | 本地绿但远端阻止 | 报告里标出，让人工开 PR |
| deploy 阶段某站失败 | curl 非 200 | 留 A 组已 push 不回滚；单独修失败站 |

## 和 playbook 的关联

- `mass-migration.md` § pilot + 批量刷的"批量刷"阶段可直接调本命令
- `stations.md` § 扩展机制里的大规模结构改动用本命令替代手工循环
- `hydro.md` § 跨站共享改动里如果需要"先 audit 再 commit 再 deploy"可用本命令（默认 /fanout-deploy 更轻量）

## 下次会话示例

```
> 把 ~/Dev/stations/web-stack/services/hydro-*/api.py 里所有 df_to_json_safe 换成 v2 版本
> /fanout-refactor "api.py 里 df_to_json_safe → df_to_json_v2，import 改 from hydro_api_helpers import df_to_json_v2" --repos $(ls -d ~/Dev/stations/web-stack/services/hydro-* | tr '\n' ',')

# CC 行为：
# 1. Pre-flight：10 个 hydro-* repo 检查 git clean + 有 api-smoke 入口
# 2. Fan-out：10 个 Agent 并行，各自 worktree，改 api.py，跑 /api-smoke --compute
# 3. Supervisor：8 个绿 / 1 个红（参数签名变了）/ 1 个零改动（已是 v2）
# 4. 输出矩阵 + AskUserQuestion 让用户决定 push + deploy
# 5. 批准 → 8 个 push + deploy，1 个 worktree 保留待人工
```
