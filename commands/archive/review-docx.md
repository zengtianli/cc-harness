---
description: 审阅 DOCX 文档，自动批注问题（禁用词、标点、格式等）
---

用户提供了一个文件路径: $ARGUMENTS

请审阅 Word 文档并以修订标记 + 批注的形式标出问题。

## 工具位置

- 提取文本：`/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py extract <file>`
- 写入批注：`/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes review <file> -o <output> -r <rules.json>`

## 流程

### 1. 确定输入文件

- 如果 `$ARGUMENTS` 为空，问用户要文件路径
- 确认文件存在且为 `.docx`

### 2. 提取文档文本

运行 extract 提取文档内容为 Markdown：

```
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py extract "<输入文件>"
```

### 3. 分析问题并生成 rules

阅读提取的文本，检查以下问题类型：

- **禁用词**：确保、我们、我司、贵司 → 建议替换词 + 批注说明原因
- **英文标点**：英文逗号/冒号/分号/括号出现在中文语境中 → 替换为中文标点 + 批注
- **单位格式**：平方米/立方米/公里等中文单位 → 替换为 m²/m³/km 等 + 批注
- **数据无来源**：含具体数字的关键句子缺少来源标注 → 不替换，仅批注提醒
- **重复表述**：相邻段落有高度相似或重复的内容 → 不替换，仅批注提醒
- **其他公文规范问题**：根据文档内容判断

生成 rules JSON 文件，格式为：

```json
[
  {"find": "确保", "replace": "确保", "comment": "建议替换为"保障"或"保证"，"确保"在公文中不常用"},
  {"find": "我们", "replace": "我们", "comment": "公文中避免使用"我们"，建议改为具体单位名称"}
]
```

注意：
- 如果只需要批注不需要替换，find 和 replace 设为相同值（只留批注）
- 每条 rule 的 comment 要简洁说明问题和建议
- 将 rules 写入临时文件（与输入文件同目录，命名为 `_review_rules.json`）

### 4. 写入批注

```
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes review "<输入文件>" -o "<输入文件目录>/<原名>_reviewed.docx" -r "<rules文件>"
```

### 5. 完成

- 用 `open` 打开审阅后的 docx
- 报告：发现了多少处问题，按类型分类汇总
- 清理临时 rules JSON 文件
