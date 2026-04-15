---
description: 读取 DOCX 指定章节内容（按标题定位），或 --list 列出全部标题结构
---

读取 DOCX 文件中指定章节的全部内容。

## 参数

$ARGUMENTS 格式：`<docx路径> <章节关键词|--list>`

示例：
- `/read-docx path/to/report.docx 水效评估指标体系`
- `/read-docx path/to/report.docx --list`
- `/read-docx path/to/report.docx 3.1`（按编号定位）

## 执行流程

### 1. 定位文件

如果 $ARGUMENTS 只给了关键词没给路径，在当前项目目录下找最新的 `.docx`（排除 `~$` 临时文件）。

### 2. 解析标题结构

用 python-docx 遍历所有段落，识别 Heading 样式：

```python
from docx import Document
import re, sys

doc = Document(docx_path)

def heading_level(style_name):
    m = re.search(r'Heading\s*(\d)', style_name or '')
    return int(m.group(1)) if m else 99

# --list 模式：打印所有标题
for i, p in enumerate(doc.paragraphs):
    lvl = heading_level(p.style.name)
    if lvl < 99 and p.text.strip():
        indent = "  " * (lvl - 1)
        print(f"[{i:>4}] {indent}{p.text.strip()[:120]}")
```

### 3. 提取章节内容

找到匹配标题后，提取从该标题到下一个同级或更高级标题之间的所有段落：

```python
def read_section(doc, query):
    start_idx, start_level = None, None
    for i, p in enumerate(doc.paragraphs):
        lvl = heading_level(p.style.name)
        if lvl < 99 and query in p.text:
            start_idx, start_level = i, lvl
            break
    if start_idx is None:
        return "未找到匹配章节"
    
    lines = [doc.paragraphs[start_idx].text]
    for j in range(start_idx + 1, len(doc.paragraphs)):
        p = doc.paragraphs[j]
        lvl = heading_level(p.style.name)
        if lvl <= start_level:
            break
        lines.append(p.text)
    return "\n".join(lines)
```

### 4. 输出

将章节内容展示给用户，包含段落索引标记以便后续编辑定位。

## 关键约束

- **只读操作**，不修改源文件
- 标题匹配优先精确匹配，找不到时模糊匹配（关键词全部出现）
- 表格内容也要提取（遍历 `doc.tables`）
