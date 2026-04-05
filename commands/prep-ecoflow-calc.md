---
description: 生态流量计算（Tennant法+QP法，Python替代CurveFitting）
---

用户提供了参数: $ARGUMENTS

请执行生态流量计算流程。

## 工具位置

- 计算脚本：`/Users/tianli/miniforge3/bin/python3 ~/Work/eco-flow/code/脚本/core/eco_flow_calc.py`
- 逐日流量数据：`~/Work/eco-flow/data/小型水库流量_水文to水资源.xlsx`（47个水库，1962-2023）
- 已有计算结果（验证用）：`~/Work/eco-flow/data/生态流量核定.xlsx`

## 流程

### 1. 解析参数

从 `$ARGUMENTS` 解析目标县市名（如 "景宁"）。

读取 `~/Work/eco-flow/sync_config.yaml` 获取县市配置。

确定目录：
- 目标县市目录：`~/Work/eco-flow/{city拼音}-{county}/`
- 合并数据文件：`{县市目录}/data/合并数据/水库基本情况和生态流量状况_*.xlsx`
- 输出目录：`{县市目录}/data/计算结果/`

### 2. 检查前置数据

1. 检查逐日流量数据文件是否存在
2. 检查合并数据表是否存在（用于获取该县市水库列表）
   - 如果不存在，提示先运行 `/prep-engineering`

### 3. 确定水库列表

从合并数据表获取该县市的水库名称列表，与逐日流量数据中的列名匹配。

如果匹配率低，报告未匹配的水库名称，提示用户：
- 可能是水库名称不一致（简称/全称）
- 可能该水库的径流数据确实不在全省数据源中

### 4. 执行计算

```bash
/Users/tianli/miniforge3/bin/python3 ~/Work/eco-flow/code/脚本/core/eco_flow_calc.py \
  --flow-data ~/Work/eco-flow/data/小型水库流量_水文to水资源.xlsx \
  --county <县名> \
  --merge-file "<合并数据文件>" \
  -o "<输出目录>" \
  --verify ~/Work/eco-flow/data/生态流量核定.xlsx
```

可选参数：
- `--reservoirs 坦袋水库,黄坑水库` — 只计算指定水库
- `--level 良好` — 使用更高保护等级（默认"一般"）
- `--period 1962-2023` — 指定计算时段
- `--dry-run` — 只打印结果不写文件
- `--list-reservoirs` — 列出数据源中所有水库

### 5. 检查产出

检查输出文件：
- `{县名}_生态流量计算结果.xlsx` — 汇总表（水库名、平均流量、Tennant、QP、推荐值）
- `{县名}_逐月流量统计.xlsx` — 各水库12个月统计
- `计算说明.md` — 方法说明和结果摘要

### 6. 完成

报告：
- 计算的水库数量和匹配率
- 与已有结果的对比（如有）
- 各水库推荐生态基流汇总
- 提示后续步骤：
  1. 检查推荐值是否合理（与水库规模匹配）
  2. `/gen-report` 生成报告时会自动读取计算结果
