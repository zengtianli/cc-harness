---
description: 根据审稿意见修改论文，以修订标记+批注形式插入修改内容到 DOCX
---

用户提供了参数: $ARGUMENTS

请根据审稿意见修改论文，将修改内容以 Word 修订标记 + 批注的形式写入文档。

## 参数解析

- 第一个参数：论文 DOCX 文件路径
- `--comments <file>`：审稿意见文件路径（如不提供，从论文文档中提取）
- `--rules <file>`：已有规则 JSON 文件（跳过生成步骤，直接写入）
- `--dry-run`：只生成规则 JSON，不写入文档
- `--author <name>`：修订作者名（默认"审稿修改"）

## 工具位置

- 提取文本：`/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py extract <file>`
- 写入修订：`/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes review <file> -o <output> -r <rules.json> -a <author>`
- 读取修订：`/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes read <file>`

## 流程

### 1. 确定输入

- 确认论文文件存在且为 `.docx`
- 如有 `--comments` 参数，读取审稿意见文件
- 如无，从论文文档中提取文本，查找审稿意见部分（通常在文档开头或单独文件）

### 2. 分析审稿意见

逐条分析审稿意见，分为三类：

- **可直接修改**：文字改写、补充数据/论证、可视化图件等（需要先用代码计算或生成的，先完成计算）
- **需要计算支撑**：如灵敏度分析、中间结果提取等 — 先写脚本并运行，再用结果撰写修改内容
- **无法修改**：需要用户提供原始素材的条目 — 在批注中说明所需素材

### 3. 生成修改规则

构建 rules JSON 文件（与输入文件同目录，命名为 `_revise_rules.json`），格式：

```json
[
  {
    "find": "原文中需要修改的段落或句子",
    "replace": "修改后的内容",
    "comment": "【回应审稿意见第N条】修改说明"
  }
]
```

规则编写要点：
- `find` 必须是论文中能**唯一匹配**的原文片段
- 如只需插入内容不需替换，在 `replace` 中保留原文并追加新内容
- 如只需批注不修改正文，`find` 和 `replace` 设为相同值
- 每条 `comment` 以 `【回应审稿意见第N条】` 开头，标明对应的审稿意见编号
- 需要计算支撑的修改，先运行计算脚本，用实际结果填入 `replace`

### 4. 写入文档

```bash
/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes review \
  "<输入文件>" \
  -o "<输出文件>" \
  -r "<rules文件>" \
  -a "<作者名>"
```

输出文件命名规则：`（修改稿）原文件名.docx`

### 5. 验证与报告

- 用 `track-changes read` 读取输出文件，确认修订和批注正确写入
- 用 `open` 打开输出文件
- 汇总报告：
  - 已修改条目（列出对应审稿意见编号 + 修改摘要）
  - 未修改条目（列出原因 + 所需素材）
  - 生成的辅助文件（计算结果、图件等）
- 清理临时文件（可选保留 rules JSON 供后续调整）
