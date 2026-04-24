---
description: 基于参考报告逐章生成新县市报告（提取→数据准备→LLM逐章→合并）
---

用户提供了参数: $ARGUMENTS

请执行报告生成工作流。

## 工具位置

- 报告生成：`/opt/homebrew/bin/python3 ~/Dev/tools/doctools/scripts/document/gen_report.py`
- MD 合并：`/opt/homebrew/bin/python3 ~/Dev/tools/doctools/scripts/document/md_tools.py`
- 章节策略：`~/Dev/tools/cc-configs/rules/gen-report/`
- 参考章节：`~/Dev/Work/eco-flow/模板/ref_chapters/`（景宁成品已拆分）

## 流程

### 1. 解析参数

从 `$ARGUMENTS` 解析目标县市名（如 "天台"）。

读取 `~/Dev/Work/eco-flow/sync_config.yaml` 获取县市配置（project_dir、stat_name、city）。

确定目录：
- 目标县市目录：`~/Dev/Work/eco-flow/{city拼音}-{county}/`
- data 目录：`~/Dev/Work/eco-flow/{city拼音}-{county}/data/`
- 工作目录：`~/Dev/Work/eco-flow/{city拼音}-{county}/docs/gen-report/`

### 2. 检查数据就绪

检查目标县市 data 目录下是否存在：
- `01_基本信息.md` ~ `06_水资源概况.md`（县市基础数据）
- `表2-1*.xlsx` 或 `合并数据/`（水库工程数据）

如果缺失，提示用户先准备数据：
```
天台县数据尚未准备完整。建议先运行：
  python3 code/脚本/core/generate_table_2_1.py --county 天台 --city 台州
或手动将数据放入 taizhou-天台/data/
```

### 3. 逐章生成

```bash
/opt/homebrew/bin/python3 ~/Dev/tools/doctools/scripts/document/gen_report.py \
  --ref-dir ~/Dev/Work/eco-flow/模板/ref_chapters \
  --data-dir "<data目录>" \
  --config eco-flow-report \
  --output "<工作目录>/generated" \
  --county "<县名>" --city "<市名>"
```

可选参数：
- `--chapters 01,02` — 只生成指定章节
- `--dry-run` — 只打印 prompt，不调 LLM
- `--force` — 覆盖已有章节
- `--model sonnet` — 覆盖所有章节使用的模型

### 4. 合并

```bash
/opt/homebrew/bin/python3 ~/Dev/tools/doctools/scripts/document/md_tools.py merge \
  <工作目录>/generated/0[1-6]_*.md \
  -o "<工作目录>/<县名>小型水库工程生态流量核定与保障实施方案.md"
```

### 5. 完成

- 报告每个章节的生成策略和字数
- 检查 `grep 景宁` 确认无县名残留
- 提示后续步骤：
  1. `/md2word` 将合并后的 MD 转为 Word
  2. `/review-deep` 审阅生成的报告
