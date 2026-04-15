---
description: 合并文档内容（md=MD写入DOCX指定章节, revisions=合并多个修改稿）
---

用户提供了参数: $ARGUMENTS

## 子命令路由

解析 `$ARGUMENTS` 第一个词：
- `md` — 将 MD 内容合并写入 DOCX 的指定章节
- `revisions` — 合并多个修改稿 DOCX 到基准文档
- 为空 → 问用户选择

---

## md — MD 内容写入 DOCX

将 MD 文件的内容合并到 DOCX 的指定章节位置（安全替换，保留表格）。

1. 解析 MD 结构（标题层级、段落、表格）
2. 在 DOCX 中定位目标章节（匹配第一个标题）
3. 替换范围：从目标标题到下一个同级标题之前
4. 保留原 DOCX 中的表格和图片
5. 正确映射 MD 标题层级到 Word Heading 样式
6. 输出 `-merged.docx` 后缀

---

## revisions — 合并修改稿

将多个修改稿 DOCX 的修订内容合并到基准文档。

1. 读取修订规则 JSON（`_revise_rules_{section}.json`）
2. 按规则将所有修改作为直接替换（非 track changes）
3. **倒序应用**规则避免索引漂移
4. 输出 `标书大纲-合并稿-{MMDD}.docx`
