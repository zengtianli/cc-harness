---
description: 工程排查数据准备（筛选→合并→MD提取→简化→排查表）
---

用户提供了参数: $ARGUMENTS

请执行工程排查数据准备流程。

## 工具位置

- 工程数据脚本：`/Users/tianli/Work/resources/data/全省水资源基础数据/工程数据/脚本/`
  - `full_pipeline.py` — 一键完整流水线
  - `build_reservoir_summary.py` — 步骤1：生成基础表
  - `enrich_from_md.py` — 步骤2：从MD补充详情
  - `build_eco_survey_table.py` — 步骤3：生成排查表
  - `config.py` — 路径和县市映射配置
- 数据同步：`sync_project.py`（在 `~/Work/eco-flow/`）

## 流程

### 1. 解析参数

从 `$ARGUMENTS` 解析目标县市名（如 "天台"）。

读取 `~/Work/eco-flow/sync_config.yaml` 获取县市配置（city、stat_name、project_dir）。

### 2. 检查前置数据

检查全省数据源目录是否存在：
- `/Users/tianli/Work/resources/data/全省水资源基础数据/工程数据/原始/` 下应有：
  - `表2-1工程基本情况调查表.xlsx`
  - `表2-2河湖断面生态流量排查.xlsx`
  - `表2-3水库工程生态流量排查.xlsx`
  - `浙江省已建水库名录信息.xlsx`
  - `浙江省已建水利水电工程基本情况调查表.xlsx`
  - `河湖控制断面生态流量批复成果分析表_*.xlsx`

如果缺失，提示用户先准备全省源数据。

### 3. 检查县市配置

检查 `config.py` 中的 `COUNTY_MAP` 是否包含目标县市。如果不包含，提示需要先在 config.py 中添加映射。

检查是否有工程资料 MD 目录（`MD_DIR_MAP`）。如果没有，流水线会跳过 MD 补充步骤（`--skip-md`）。

### 4. 运行流水线

```bash
cd /Users/tianli/Work/resources/data/全省水资源基础数据/工程数据/脚本
/opt/homebrew/bin/python3 full_pipeline.py -c <县名> --type 小型
```

如果没有 MD 目录，加 `--skip-md`：
```bash
/opt/homebrew/bin/python3 full_pipeline.py -c <县名> --type 小型 --skip-md
```

### 5. 检查产出

检查输出文件：
- `工程数据/合并/水库基本情况和生态流量状况_<县名>_小型.xlsx`
- `工程数据/合并/小型水库生态流量状况排查表_<县名>.xlsx`

用 Python 读取 Excel 报告：
- 水库总数
- 各字段填充率（非空比例）
- 有生态流量目标的水库数

### 6. 同步到项目目录

将产出文件复制到 eco-flow 项目对应县市的 data 目录：
```
~/Work/eco-flow/{city拼音}-{county}/data/合并数据/
```

### 7. 完成

报告：
- 处理的水库数量
- 数据完整度（各关键字段填充率）
- 缺失的数据项（如 MD 资料未提取的字段）
- 提示后续步骤：
  1. 如有工程资料 MD，可补充运行 `enrich_from_md.py`
  2. `/prep-ecoflow-calc` 计算生态流量
  3. `/gen-report` 生成报告
