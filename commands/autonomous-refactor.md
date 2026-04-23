---
description: 自循环重构 — 定义验收脚本，Claude 在 git worktree 里自动 patch→test→fix 循环，通过或超预算才通知用户
---

大型重构变"过夜任务"。你定义目标 + 验收标准，Claude 自循环执行，只在完成或耗尽预算时叫你。

## 用法

```
/autonomous-refactor \
  --goal "<重构目标描述>" \
  --verify <验收脚本路径> \
  --max-iter <最大迭代次数>
```

示例：
```
/autonomous-refactor \
  --goal "把 12 个 station repo 迁到 monorepo，pnpm build 全绿" \
  --verify ~/Dev/scripts/verify-monorepo.sh \
  --max-iter 15
```

## 验收脚本约定

脚本必须输出 JSON 到 stdout，exit 0 表示可继续：

```json
{"passing": false, "failures": ["hydro-annual build failed: missing tsconfig", "navbar missing in stack"]}
```

或通过：
```json
{"passing": true, "failures": []}
```

Claude 解析 `failures` 数组，**每轮只修第一条**，然后重新运行脚本，直到 `passing: true` 或达到 `max-iter`。

## 执行流程

### Step 0 — 初始化
- 创建 git worktree：`git worktree add /tmp/refactor-<timestamp> -b refactor/<goal-slug>`
- 在 worktree 里做所有改动，不污染主分支
- 运行一次验收脚本，建立 baseline（记录初始 failures 数）

### Step 1 — 自循环（最多 max-iter 次）

```
loop:
  1. 读当前 failures[0]
  2. 分析根因，实施最小修复
  3. 运行验收脚本
  4. 如 passing: true → 跳出循环 → 报告成功
  5. 如 failures 没减少（循环卡住）→ 换策略，记录尝试
  6. 迭代计数 +1，未超 max-iter → 继续
```

**Claude 在循环中不向用户提问**，只在以下情况打断：
- 遇到需要删除文件（需确认）
- 遇到需要修改 settings.json / CLAUDE.md（需确认）

### Step 2 — 完成或超预算

**通过时**：
- 提交 worktree 改动：`git commit -m "autonomous-refactor: <goal>"`
- 输出摘要：迭代次数、修复路径、diff 统计
- 询问用户是否 merge 回主分支

**超预算时**：
- 输出已尝试的策略清单和当前 failures
- 标注"卡在哪一步"
- worktree 保留，供用户手工接力

## 验收脚本模板

如果没有现成脚本，用这个骨架：

```bash
#!/bin/bash
# verify.sh — 按需修改检查项
set -e
failures=()

# 检查 1：构建
cd ~/Dev/stations/web-stack
pnpm build 2>/dev/null || failures+=("web-stack pnpm build failed")

# 检查 2：所有子域返回 200/302
for site in hydro-annual hydro-capacity; do
  code=$(curl -sI -o /dev/null -w "%{http_code}" "https://$site.tianlizeng.cloud" 2>/dev/null)
  [[ "$code" == "200" || "$code" == "302" ]] || failures+=("$site HTTP $code")
done

# 输出
if [ ${#failures[@]} -eq 0 ]; then
  echo '{"passing": true, "failures": []}'
else
  python3 -c "import json,sys; print(json.dumps({'passing': False, 'failures': sys.argv[1:]}))" "${failures[@]}"
fi
```

## 和 `/fanout-deploy` 的区别

| 命令 | 适合什么 |
|---|---|
| `/fanout-deploy` | **已知改什么**，让各站并行执行 |
| `/autonomous-refactor` | **知道目标，不确定路径**，让 Claude 自己摸索 |

## 规则

- worktree 在 `/tmp/refactor-<timestamp>/`，不影响主分支
- 每次迭代前 git commit 一次（方便回滚到上一个稳定点）
- 不自动 push/merge，完成后由用户决定
- 如验收脚本本身报错（不是 JSON），视为环境问题，暂停并通知用户
