---
description: 审阅 DOCX 文档（格式检查 + 可选 LLM 深度审阅），输出 Word 批注
---

用户提供了一个文件路径: $ARGUMENTS

请审阅 Word 文档并以修订标记 + 批注的形式标出问题。

## 模式

根据用户参数选择模式：

- **格式审阅**（默认）：禁用词、英文标点、单位格式、数据无来源、重复表述
- **深度审阅**（`--deep`）：4维度 LLM 审阅（完整性/结构性/立场措辞/数据一致性）
- **全量审阅**（`--all`）：先格式再深度，两轮批注

## 工具位置

- 提取文本：`/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py extract <file>`
- 写入批注：`/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes review <file> -o <output> -r <rules.json>`
- 深度审阅：`/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/review_deep.py <file> --rules <rule-name>`
- 规则目录：`~/Dev/cc-configs/rules/review-deep/`

## 流程

### 1. 确定输入文件

- 如果 `$ARGUMENTS` 为空（去掉 flags 后），问用户要文件路径
- 确认文件存在且为 `.docx`
- 解析 flags：`--deep`、`--all`、`--dim <dims>`、`--model <model>`、`--dry-run`

### 2A. 格式审阅（默认模式 或 --all 第一轮）

#### 提取文档文本

```
/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py extract "<输入文件>"
```

#### 分析问题并生成 rules

阅读提取的文本，检查以下问题类型：

- **禁用词**：确保、我们、我司、贵司 → 建议替换词 + 批注说明原因
- **英文标点**：英文逗号/冒号/分号/括号出现在中文语境中 → 替换为中文标点 + 批注
- **单位格式**：平方米/立方米/公里等中文单位 → 替换为 m²/m³/km 等 + 批注
- **数据无来源**：含具体数字的关键句子缺少来源标注 → 不替换，仅批注提醒
- **重复表述**：相邻段落有高度相似或重复的内容 → 不替换，仅批注提醒
- **其他公文规范问题**：根据文档内容判断

生成 rules JSON 文件（与输入文件同目录，命名为 `_review_rules.json`）：

```json
[
  {"find": "确保", "replace": "确保", "comment": "建议替换为"保障"或"保证"，"确保"在公文中不常用"}
]
```

注意：如果只需要批注不需要替换，find 和 replace 设为相同值。

#### 写入批注

```
/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes review "<输入文件>" -o "<输出文件>" -r "<rules文件>"
```

### 2B. 深度审阅（--deep 模式 或 --all 第二轮）

```bash
/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/review_deep.py \
  "<输入文件>" \
  --rules eco-flow-report \
  --model haiku
```

可选参数：
- `--dim completeness structure tone consistency` — 指定维度
- `--model haiku|sonnet` — 默认 haiku，重要文档建议 sonnet
- `--dry-run` — 只输出问题清单，不写入批注
- `-o <输出路径>` — 指定输出文件路径

如果是 `--all` 模式，深度审阅的输入文件用格式审阅的输出文件。

### 3. 完成

- 用 `open` 打开审阅后的 docx
- 报告：按类型/维度汇总问题数量
- 清理临时 rules JSON 文件
