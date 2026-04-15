---
description: 检查并修复 DOCX 文档中表/图的编号及正文引用一致性
---

用户提供了文件路径: $ARGUMENTS

检查 Word 文档中所有表格和图片的编号是否按出现顺序连续，正文中的交叉引用是否与标题编号一致。发现问题后自动修复。

## 工具

- 提取文本：`/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py extract <file>`
- python-docx 直接操作 XML（处理 w:t 跨节点的编号替换）

## 流程

### 1. 确定输入文件

- 如果 `$ARGUMENTS` 为空，问用户要文件路径
- 确认文件存在且为 `.docx`
- 用 `ls` 获取精确路径（中文文件名用 glob 或 tab 补全）

### 2. 扫描当前状态

用 python-docx 遍历 `doc.element.body` 的所有直接子元素，收集：

**表/图标题**（按出现顺序）：
- 段落文本以"表"或"图"开头、长度 < 80 字符的认定为标题
- 记录：`(body_index, 当前编号, 标题文本, 类型=表/图)`

**正文引用**：
- 在所有长段落中用正则 `[表图]\d+` 提取引用
- 记录：`(body_index, 引用列表)`

**注意 w:t 跨节点问题**：
- Word 经常把"表2 CRITIC"拆成 `[表] [2] [ CRITIC] [法...]` 多个 w:t 节点
- 获取段落完整文本时必须遍历所有 `w:t` 节点拼接
- 替换时不能只在单个 w:t 中搜索，需要处理"表"和数字分属不同 w:t 的情况

### 3. 诊断问题

对比标题编号和出现顺序，检查：

1. **编号不连续**：表/图应分别从 1 开始连续编号
2. **编号与出现顺序不一致**：如先出现表8再出现表6
3. **引用与标题不匹配**：正文"见表6"但实际该内容在表10

输出诊断报告给用户（Markdown 表格），包括：
- 当前标题编号 vs 应有编号
- 每处需要修改的引用

### 4. 用户确认后执行修复

**替换策略**（处理 w:t 跨节点）：

```python
def replace_table_num(para_elem, old_num, new_num):
    wt = [n for n in para_elem.iter() if n.tag == qn('w:t')]
    # 策略1: "表{num}" 在同一个 w:t 中
    for n in wt:
        if n.text and f"表{old_num}" in n.text:
            n.text = n.text.replace(f"表{old_num}", f"表{new_num}", 1)
            return True
    # 策略2: "表" 在一个 w:t，数字在下一个 w:t
    for i in range(len(wt) - 1):
        if wt[i].text and wt[i].text.endswith("表"):
            if wt[i+1].text and wt[i+1].text.startswith(old_num):
                wt[i+1].text = new_num + wt[i+1].text[len(old_num):]
                return True
    return False
```

**避免编号冲突**：如果需要互换编号（如表6↔表8），先全部改为临时编号（加 `_tmp` 后缀），再去掉后缀。

**修复顺序**：
1. 先改标题编号
2. 再改正文引用（按 body_index 精确定位）
3. 同时处理"~"范围引用（如"表2~5"）和"、"并列引用（如"表10、表11"）

### 5. 验证

修复后重新扫描，确认：
- 标题编号从 1 开始连续
- 所有正文引用都指向存在的标题
- 输出最终对照表给用户

### 6. 保存

- 默认覆盖原文件
- 如果用户指定 `-o <path>` 则输出到指定路径
- 用 `open` 打开修复后的文件
