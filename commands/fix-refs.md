---
description: 修复 DOCX 中的文献引用角标（[数字] → 右上角上标）
---

用户提供了参数: $ARGUMENTS

将 Word 文档中 `[1]` `[3-4]` `[18-19]` 等文献引用标记改为右上角上标格式。

## 工具

```
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/fix_superscript_refs.py <file> [-o <output>] [--dry-run]
```

## 流程

### 1. 确定输入文件

- 如果 `$ARGUMENTS` 为空，问用户要文件路径
- 确认文件存在且为 `.docx`
- 解析 flags：`--dry-run`、`-o <output>`

### 2. 先预览

```bash
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/fix_superscript_refs.py "<文件>" --dry-run
```

报告哪些段落有需要修复的引用。

### 3. 执行修复

如果有需要修复的引用：

```bash
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/fix_superscript_refs.py "<文件>" -o "<输出文件>"
```

- 默认输出覆盖原文件
- 如用户指定了 `-o`，输出到指定路径

### 4. 完成

- 用 `open` 打开修复后的 docx
- 报告：修复了几个段落、几处引用

## 注意事项

- 自动跳过参考文献列表行（以 `[数字]` 开头的行）
- 自动跳过已经是上标的引用
- 支持修订标记（track changes）中的文本
- 支持 `[1]` `[3-4]` `[8,12]` `[18-19]` 等多种引用格式
