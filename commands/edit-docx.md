---
description: 批量修改 docx 标题（改名/插入/删除），直接在 CC 里操作 Word 文件
---

用户要修改 docx 文件的标题。参数: $ARGUMENTS

## 工具

脚本路径: `~/Dev/scripts/scripts/document/docx_heading_edit.py`

```
用法:
  python3 ~/Dev/scripts/scripts/document/docx_heading_edit.py <docx> --list
  python3 ~/Dev/scripts/scripts/document/docx_heading_edit.py <docx> '<json_ops>' [--dry-run] [-o output]
```

支持的操作:
- `rename`: 改标题文本 `{"action":"rename", "index":185, "new_text":"新标题"}`
- `insert_after`: 插入新标题 `{"action":"insert_after", "index":185, "heading_level":4, "new_text":"新标题"}`
- `delete`: 删除标题及其下属内容 `{"action":"delete", "index":208}`
- `delete_heading_only`: 仅删标题段落 `{"action":"delete_heading_only", "index":208}`

⚠️ 文件名含中文引号时用 `glob` 或 `ls` 拿路径，不要手敲。

## 流程

### 1. 确定目标文件

- 如果 `$ARGUMENTS` 有路径，用它
- 否则在当前项目的 `招标文件/` 下找 docx
- 用 `ls` 获取精确路径（避免中文引号问题）

### 2. 列出当前标题

```bash
DOCX="$(ls 招标文件/*大纲*.docx 2>/dev/null | grep -v '~\$' | head -1)"
python3 ~/Dev/scripts/scripts/document/docx_heading_edit.py "$DOCX" --list
```

向用户展示标题树，确认要改哪些。

### 3. 构建操作列表

根据用户需求，构建 JSON 操作数组。注意：
- **index 是段落索引**（从 `--list` 输出获取）
- 多个操作按从上到下写即可，脚本内部会按 delete→rename→insert 顺序、从下往上处理以保持索引稳定

### 4. Dry-run 确认

```bash
python3 ~/Dev/scripts/scripts/document/docx_heading_edit.py "$DOCX" '$OPS_JSON' --dry-run
```

展示修改预览和结果标题树，等用户确认。

### 5. 执行

用户确认后去掉 `--dry-run` 执行。可用 `-o` 指定输出路径（默认覆盖原文件）。

### 6. 验证

```bash
python3 ~/Dev/scripts/scripts/document/docx_heading_edit.py "$DOCX" --list
```

展示修改后的标题树，确认结果正确。
