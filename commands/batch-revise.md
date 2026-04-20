---
description: 批量将改动草稿 MD 转为 track-changes 写入 DOCX（修订标记+批注，用户可在 Word 中逐条接受/拒绝）
---

用户提供了参数: $ARGUMENTS

将一批改动草稿 MD 文件转为 Word 修订标记，批量写入标书大纲 DOCX。

## 参数

- 无参数：扫描 `成果/md/*-改动草稿.md`，全部处理
- 指定文件：`成果/md/3.5-xxx-改动草稿.md`
- `--dry-run`：只生成 rules JSON，不写入
- `--author <name>`：修订作者名（默认"审阅"）

## 工具

- 写入修订：`python3 ~/Dev/tools/doctools/scripts/document/docx_tools.py track-changes review <file> -o <output> -r <rules.json> -a <author>`
- 读取修订：`python3 ~/Dev/tools/doctools/scripts/document/docx_tools.py track-changes read <file>`

## 流程

### 1. 确定输入

- 基准 DOCX：在 `招标文件/` 下找主文档（排除 `~$`、`copy`、`修改稿`），优先找最新的合并稿或原始稿
- 改动草稿 MD：按参数确定，无参数则 glob `成果/md/*-改动草稿.md`
- 列出待处理的 MD 文件清单，向用户确认

### 2. 逐个 MD 生成 rules JSON

对每个改动草稿 MD：

1. **读取 MD**，解析出所有改动条目（找"原文"/"改为"配对，以及"删除"/"新增"指令）
2. **读取 DOCX 对应段落**，用 python-docx 提取原文，确保 `find` 能唯一匹配
3. **用 Python `json.dump` 生成 rules JSON**（绝对不用 Write 工具写 JSON，避免中文引号解析失败）
   - 文件命名：`招标文件/_revise_rules_{章节号}.json`
   - 格式：`[{"find": "...", "replace": "...", "comment": "【改动N】..."}]`
4. 验证 JSON 可解析

### 3. 批量写入

对每个 rules JSON，调用 docx_tools.py track-changes review 写入。
每个 MD 生成独立的修改稿 DOCX（不累加到一个文件），方便用户分批审阅。

### 4. 验证与报告

- 用 `track-changes read` 验证每个输出文件
- 汇总报告表格：

| MD 文件 | 改动数 | 输出 DOCX | 状态 |
|---------|--------|-----------|------|

- 用 `open` 打开所有输出文件

### 关键约束

1. **JSON 必须用 Python 生成**（`json.dump(rules, f, ensure_ascii=False, indent=2)`），不用 Write 工具
2. **find 必须唯一匹配**，如果原文被多处引用，加更多上下文使其唯一
3. **删除操作**：`replace` 设为空字符串 `""`
4. **新增操作**：找到插入点前的段落作为 `find`，`replace` = 原文 + "\n" + 新内容
5. **文件名含中文引号**：用 Python glob 获取路径，不要在 shell 中直接拼
6. **每个草稿 MD 独立输出**，不累加修改
7. **大段替换（>10段）改用直接重建**：delete old paras + insert new（参考 rebuild 脚本模式），不走 track-changes
