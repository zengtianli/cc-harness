---
description: 修复 DOCX 文档问题（refs=引用角标, heading=标题编号, numbering=表图编号, all=全部）
---

用户提供了参数: $ARGUMENTS

统一入口修复 DOCX 文档的常见格式问题。根据第一个参数分派到对应的子命令。

## 子命令路由

解析 `$ARGUMENTS`：
- 第一个词为子命令：`refs` | `heading` | `numbering` | `all`
- 剩余部分为文件路径和 flags

如果 `$ARGUMENTS` 为空或第一个词不是子命令，问用户选择：
- `refs` — 文献引用 `[1]` `[3-4]` → 右上角上标
- `heading` — 标题编号体系修复（7级阿拉伯数字）
- `numbering` — 表/图编号及引用一致性
- `all` — 按 heading → numbering → refs 顺序全部执行

---

## refs — 引用角标修复

将 `[1]` `[3-4]` `[18-19]` 等文献引用改为右上角上标格式。

**工具**: `/opt/homebrew/bin/python3 ~/Dev/tools/doctools/scripts/document/fix_superscript_refs.py`

1. 先 `--dry-run` 预览
2. 执行修复（默认覆盖原文件，`-o` 指定输出路径）
3. `open` 打开结果

自动跳过参考文献列表行和已上标引用。

---

## heading — 标题编号体系

7级体系：1 → 1.1 → 1.1.1 → 1.1.1.1 → （1） → 1） → ①

**DOCX 三步修复**：
1. **numbering.xml** — 确保 H5/H6 绑定 numPr
2. **标题级别** — 两遍扫描法修复层级跳跃（第一遍只读分析，第二遍批量写入）
3. **去硬编码前缀** — 跨 run 逐字符消耗，去掉手动编号

⚠️ 关键：不能边修边检测，必须用两遍扫描法。

确认方案后执行，验证无层级跳跃，`open` 打开。

---

## numbering — 表/图编号一致性

检查表格和图片编号是否连续，正文引用是否匹配。

1. 扫描标题段落（"表"/"图"开头，<80字符）和正文引用
2. 诊断：编号不连续、顺序不一致、引用不匹配
3. 替换时处理 w:t 跨节点（"表"和数字可能分属不同 w:t）
4. 避免编号冲突用 `_tmp` 临时后缀

---

## all — 全部修复

按顺序执行 heading → numbering → refs，中间不需要用户确认。
