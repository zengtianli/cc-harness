---
description: 统计 slash command 使用频率，基于会话 transcript 数据
---

统计所有 CC 会话中 slash command 的调用频率。

## 用法

运行统计脚本：

```bash
/Users/tianli/miniforge3/bin/python3 ~/Dev/cc-configs/tools/cmd_stats.py
```

## 参数

根据 $ARGUMENTS 解析：
- 无参数 → 全量统计，显示 top 30
- `--days N` → 只统计最近 N 天
- `--top N` → 显示 top N
- `--json` → JSON 格式输出
- `--registered` → 只显示有对应 .md 文件的命令（过滤掉内置命令如 /cost /status）

## 示例

```bash
# 全量统计
/Users/tianli/miniforge3/bin/python3 ~/Dev/cc-configs/tools/cmd_stats.py

# 最近 7 天
/Users/tianli/miniforge3/bin/python3 ~/Dev/cc-configs/tools/cmd_stats.py --days 7

# 只看注册的命令，JSON 输出
/Users/tianli/miniforge3/bin/python3 ~/Dev/cc-configs/tools/cmd_stats.py --registered --json
```

## 输出

展示结果表格给用户，包含：调用次数、命令名、频率条形图。
