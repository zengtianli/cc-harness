---
description: 增删改 ~/.claude/settings.json 的 hooks/permissions/env（薄封装 update-config skill）
---

$ARGUMENTS 形式：

```bash
/update-hooks <action> <target> [value]
```

## 动作

- `/update-hooks disable Stop`      — 删除 Stop hook 整块
- `/update-hooks disable SessionEnd` — 删除 SessionEnd hook 整块
- `/update-hooks enable Stop <cmd>`  — 加 Stop hook 跑 `<cmd>`，timeout=5，async=true
- `/update-hooks list`                — 显示当前所有 hooks
- `/update-hooks allow <tool-pattern>` — 加 permissions.allow 条目（复用 update-config）

## 执行规则

1. **先读** `~/.claude/settings.json` 看当前状态
2. 只做 JSON 结构编辑，保留缩进和其他字段
3. 改动前 diff 给用户看一眼，再确认落盘
4. 失败时不破坏文件（用临时文件写入 + 校验 JSON → mv）

## 典型场景

- 本次关"会话反思"扰民：`/update-hooks disable Stop`
- 本次 cclog 修复后要让 SessionEnd 的 cclog index 报错可见：`/update-hooks list` 看现状
- 升级 hook：先 `disable` 再 `enable`

## 参考

- 后端 skill：`update-config`（CC 内置，专管 settings.json）
- 原则：自动化行为（"whenever/each time"）必须走 hook，不能靠 memory/preferences
- 实战：2026-04-17 删 Stop hook 的手工过程，之后应直接用此命令
