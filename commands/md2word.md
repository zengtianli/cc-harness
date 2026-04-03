---
description: MD/DOCX 转 Word 标准工作流（套模板 → 文本修复 → 图名居中）
---

用户提供了一个文件路径: $ARGUMENTS

请执行以下 Word 文档处理工作流。所有脚本位于 `~/Dev/doctools/scripts/document/`，Python 路径为 `/Users/tianli/miniforge3/bin/python3`。

## 流程

### 1. 确定输入文件

- 如果 `$ARGUMENTS` 为空，问用户要文件路径
- 确认文件存在且为 `.md` 或 `.docx`

### 2. 根据文件类型执行转换

**如果输入是 `.md` 文件：**

运行 `md_docx_template.py` 将 MD 转为 docx（自动套模板样式）：

```
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/md_docx_template.py "<输入文件>"
```

输出文件为同目录下同名 `.docx`。后续步骤使用这个 docx 文件。

**如果输入是 `.docx` 文件：**

运行 `docx_apply_template.py` 给 docx 套模板样式：

```
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_apply_template.py "<输入文件>"
```

输出文件为 `<原名>_styled.docx`。后续步骤使用这个输出文件。

### 3. 文本格式修复

运行 `docx_text_formatter.py` 修复标点/引号/单位：

```
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_text_formatter.py "<上一步的docx文件>"
```

输出文件为 `<原名>_fixed.docx`。后续步骤使用这个输出文件。

### 4. 图名样式

运行 `docx_apply_image_caption.py` 应用图片+图名居中样式：

```
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_apply_image_caption.py "<上一步的docx文件>"
```

此脚本会就地修改文件。

### 5. 完成

- 用 `open` 打开最终的 docx 文件
- 报告每一步的处理结果摘要（替换了多少标点、处理了多少图片等）
- 列出产生的所有中间文件路径，方便用户清理
