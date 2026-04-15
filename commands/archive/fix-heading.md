---
description: 修复 MD/DOCX 文件的标题编号体系（中文序号→阿拉伯数字7级体系）
---

用户提供了一个文件路径: $ARGUMENTS

## 标题编号体系（7级）

| 层级 | Word 样式 | 自动编号格式 | 示例 |
|------|-----------|-------------|------|
| 1级 | Heading 1 | `%1` | 1 总论 |
| 2级 | Heading 2 | `%1.%2` | 1.1 项目背景 |
| 3级 | Heading 3 | `%1.%2.%3` | 1.1.1 自然概况 |
| 4级 | Heading 4 | `%1.%2.%3.%4` | 1.1.1.1 地形地貌 |
| 5级 | Heading 5 | `（%5）` | （1）政策解读与任务分解 |
| 6级 | Heading 6 | `%6）` | 1）灌区管理单位 |
| 7级 | — | `①` | ①核对灌溉面积 |

## 流程

### 1. 确定输入

- 如果 `$ARGUMENTS` 为空，问用户要文件路径
- 支持 `.md` 和 `.docx` 文件
- 读取文件内容，识别当前的标题结构

### 2. 分析问题

#### MD 文件

扫描文件，找出所有不符合7级体系的标题，列出问题清单：

常见错误模式：
- `一、二、三、` → 应为对应层级的阿拉伯数字编号
- `（一）（二）（三）` → 应为对应层级的阿拉伯数字编号
- `第一章/第二章` → 应为 `1` `2`
- 无编号的游离标题 → 分配正确编号
- markdown `#` `##` `###` 层级与编号不匹配
- 编号跳号或重复

#### DOCX 文件

DOCX 修复分三步，按顺序执行：

**Step 1 — 修复 numbering.xml（自动编号定义）**

检查 Heading 样式是否绑定了 numPr。通常 H1-H4 已有自动编号（通过 abstractNum 的 pStyle 关联），H5/H6 可能缺失。

```python
# 定位标题用的 abstractNum（通过 pStyle='1','2','3','4' 识别）
for absNum in numbering_el.findall(f'.//{qn("abstractNum")}'):
    for lvl in absNum.findall(qn('lvl')):
        pStyle = lvl.find(qn('pStyle'))
        if pStyle is not None and pStyle.get(qn('val')) in ('1','2','3','4'):
            target_absNum = absNum  # 这就是标题编号用的 abstractNum
```

修复内容：
- ilvl=4：设 fmt=decimal, lvlText=`（%5）`, pStyle=5, start=1
- ilvl=5：设 fmt=decimal, lvlText=`%6）`, pStyle=6, start=1
- 给 Heading 5 样式添加 numPr（numId=同H1-H4, ilvl=4）
- 给 Heading 6 样式添加 numPr（numId=同H1-H4, ilvl=5）

**Step 2 — 修复标题级别（Heading style）**

核心问题：标题级别跳跃（如 H3 下直接出现 H5，跳过了 H4）。

⚠️ **关键经验：不能边修边检测。** 修了第一个 H5→H4 后，后续兄弟 H5 会被误判为"H4 的子级"而不再报错。

**正确做法——两遍扫描法：**

1. **第一遍（只读）**：用原始级别建 parent 追踪，记录每个标题的 `(段落索引, 原始级别, 正确级别)`
2. **第二遍（写入）**：批量修改 style

```python
# 第一遍：静态分析原始级别
parent_at_level = {}
corrections = []  # (para_idx, old_level, new_level)

for idx, (para_i, orig_level, p) in enumerate(headings):
    parent_level = max((lv for lv in parent_at_level if lv < orig_level), default=0)
    expected = parent_level + 1 if parent_level > 0 else orig_level
    if orig_level > expected:
        corrections.append((para_i, orig_level, expected, p))
    # 用 ORIGINAL level 更新追踪（不用 corrected）
    parent_at_level[orig_level] = idx
    for lv in list(parent_at_level):
        if lv > orig_level:
            del parent_at_level[lv]

# 第二遍：批量改 style
for para_i, old, new, p in corrections:
    p.style = style_map[f'Heading {new}']
```

**如果有未修改的原始文件**（同目录下不带日期后缀的版本），优先用段落顺序一一匹配来确定正确级别，避免文本匹配因重复标题名冲突：

```python
# 原始文件和目标文件标题数量相同时，按顺序匹配
if len(orig_headings) == len(cur_headings):
    for (correct_level, _), (para_i, cur_level, p) in zip(orig_headings, cur_headings):
        if cur_level != correct_level:
            p.style = style_map[f'Heading {correct_level}']
```

**Step 3 — 去除文本中的硬编码编号前缀**

H4+ 的标题如果已有自动编号，文本里的手动编号（`1）`、`（1）`）会重复显示，需要去掉。

⚠️ 注意 runs 可能拆分为多段：`('1',)('）',)('文字',)` — 必须跨 run 逐字符消耗：

```python
for p in doc.paragraphs:
    style = p.style.name if p.style else ''
    if style not in ('Heading 4', 'Heading 5', 'Heading 6'):
        continue
    if not p.runs:
        continue
    m = re.match(r'^[（(]?\d+[）)]\s*', p.text)
    if not m:
        continue
    chars_to_strip = m.end()
    for run in p.runs:
        if chars_to_strip <= 0:
            break
        if len(run.text) <= chars_to_strip:
            chars_to_strip -= len(run.text)
            run.text = ''
        else:
            run.text = run.text[chars_to_strip:]
            chars_to_strip = 0
```

### 3. 确认修复方案

向用户展示：
- 发现 N 处标题编号问题
- 列出每处的 **原文 → 修正后** 对照
- 等用户确认后再执行修改

### 4. 执行修复

- MD 文件：用 Edit 工具或 sed 批量处理
- DOCX 文件：**一个 Python 脚本按 Step 1→2→3 顺序执行**，用 `/opt/homebrew/bin/python3`
- 文件名含中文引号时 python-docx 的 `Document()` 会报错，用 `glob.glob()` 拿到实际路径再传入

### 5. 验证与完成

```python
# 验证：扫描一遍确认无层级跳跃
parent_at = {}
skip_count = 0
for p in doc.paragraphs:
    if not p.text.strip() or not p.style.name.startswith('Heading'):
        continue
    level = int(p.style.name.split()[-1])
    parent = max((lv for lv in parent_at if lv < level), default=0)
    if parent > 0 and level > parent + 1:
        skip_count += 1
    parent_at[level] = True
    for lv in list(parent_at):
        if lv > level:
            del parent_at[lv]
# skip_count == 0 即通过
```

- 报告：级别修复 N 处 + 编号前缀清理 N 处 + numbering.xml 修改
- DOCX 用 `open "$(glob路径)"` 打开让用户检查大纲视图
- 统计：`H1=N, H2=N, H3=N, H4=N, H5=N` 各级标题数量

## 注意事项

- 只改标题编号格式和样式级别，不改正文内容
- 保留原有标题文字，只替换/去除编号部分
- 如果无法确定某个标题应该在哪个层级，问用户
- Word 自动编号通过样式绑定 numPr 实现，不要在文本中硬编码编号
- Python 运行路径：`/opt/homebrew/bin/python3`
- XML 命名空间：`W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'`
