---
description: 对比两个 DOCX 文件，生成变更清单 MD + 可选批注 DOCX（章节级内容对比）
---

对比源 DOCX 与目标 DOCX，输出：
1. **变更清单 MD**：章节树形展示，标记未改动/已修改/新增
2. **批注 DOCX**（可选）：在改动章节标题上加 Word 批注

## 参数

$ARGUMENTS 格式：`<源文件> <目标文件> [--md-only|--docx-only]`

示例：
- `/diff-docx 旧版报告.docx 新版报告.docx`
- `/diff-docx v1.docx v2.docx --md-only`

## 执行流程

### 1. 解析章节

两个文件各自按标题拆分章节：`(标题原文, 层级, 标题归一化, [内容段落])`

标题归一化规则：
```python
import re

def normalize_heading(text):
    t = text.strip()
    t = re.sub(r'^[0-9]+[）)]\s*', '', t)       # 去序号前缀
    t = re.sub(r'（[^）]*标注[^）]*）', '', t)   # 去内部标注
    return t.strip()
```

### 2. 对比内容

对目标文件每个章节，用归一化标题匹配源文件章节：
- **匹配到 + 内容相同** → 未改动
- **匹配到 + 内容不同** → 已修改（计算差异描述：删/改/增几段）
- **未匹配** → 新增

### 3. 生成变更清单 MD

按文档结构树形缩进输出，顶部汇总统计：

```markdown
# 变更清单

| 统计 | 数量 |
|------|------|
| 未改动 | X |
| 已修改 | Y |
| 新增   | Z |

## 章节明细

- 第一章 标题... — 未改动
  - 1.1 ... — **已修改**（删2段，改3段）
  - 1.2 ... — 未改动
- 第二章 ... — **新增**
```

### 4. 生成批注 DOCX（可选）

对已修改章节的标题段落加 Word 批注：

**批注写入方法**（避免 Word "无法读取内容" 错误）：
1. python-docx 插入 commentRangeStart/End + commentReference
2. 构建 comments XML
3. `doc.save(temp_path)` 先保存
4. zipfile 打开 temp，补写 word/comments.xml + Content_Types + Relationships
5. 保存为最终文件

输出到源文件同目录：`{源文件名}-变更清单.md` 和 `{目标文件名}-批注.docx`

## 关键约束

1. **只读对比**——不修改源文件和目标文件
2. **批注人**：从 `git config user.name` 获取，找不到用 "Review"
3. **判断标题用 Heading style**，不靠文本格式猜
4. **批注 DOCX 必须 zip 补丁法**：python-docx 的 Part API 注册 comments 会导致 Content_Types 缺失
5. **内容对比粒度**：段落级，忽略纯空白差异
