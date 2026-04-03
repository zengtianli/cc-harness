扫描 Claude Code 会话，LLM 分析任务状态，生成 tasks.json。

## 流程

1. 运行任务分析器：`python3 ~/Dev/repo-dashboard/lib/task_analyzer.py`
2. 输出：任务数量、状态分布（active/completed/stale）、新增/变更任务列表
3. 结果写入 `~/Dev/configs/tasks.json`

## 参数

$ARGUMENTS 可选：
- `--force`：忽略缓存，重新分析所有会话
- `--dry-run`：只分析不写入文件，输出到终端

## 依赖

- `~/Dev/devtools/scripts/tools/cc_sessions.py` — 会话读取
- `~/Dev/devtools/lib/tools/llm_client.py` — LLM 分析
- 环境变量在 `~/.personal_env`，不问用户要

## 输出示例

```
✅ 扫描完成
  总任务: 12
  active: 3 | completed: 7 | stale: 2
  新增: 1 | 变更: 2
  → ~/Dev/configs/tasks.json
```
