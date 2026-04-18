---
name: bid-diff-and-revise
description: 两份标书 docx 的雷同破除工作流。典型场景：投标前查副标 vs 旧版 / 副标 vs 主标，防止内容雷同导致废标。产出改动草稿 MD → rules JSON → track-changes 写入 docx。
---

# bid-diff-and-revise · v0.1

> **成熟度**：v0.1 — 基于 `panan-rigid-2026` 单次实战抽取。下一次标书项目验证流程稳定后升 v1.0。
> **逃生通道**：原脚本保留在 `~/Work/bids/panan-rigid-2026/scripts/`，可参考对照。

## 何时触发

当用户需要对比**两份 docx** 并破除内容雷同时触发，典型场景：
- 标书副标 vs 同业旧版标书（防被判雷同废标）
- 技术商务文件 vs 主标（防副标抄主标）
- 两个版本 docx 全文差异检查

不适用于：正向生成（用 `/draft-revisions`）、单文件修订（用 `/batch-revise`）。

## 7 步流程

### 1. 章节级 diff（热身）

```bash
/diff-docx <源.docx> <目标.docx> --md-only
```

输出：章节"未改动/已修改/新增"汇总。主要用于快速判断量级，决定是否深入。

### 2. 全文逐段 sequence diff（主量尺）

```bash
python3 ~/.claude/skills/bid-diff-and-revise/scripts/seqdiff.py \
  --src <旧版.docx> --dst <新版.docx> \
  --out <目标目录>/逐段对照.md
```

输出：新版每一段与旧版的匹配状态（原样照搬 / 小改 / 改写 / 新增）+ ratio + 跨章节迁移标记。过滤短表格字段噪声。

### 3. 图片 hash 查重

```bash
python3 ~/.claude/skills/bid-diff-and-revise/scripts/image_dedup.py \
  --src <旧版.docx> --dst <新版.docx> \
  --out <目标目录>/图片重复清单.md
```

SHA256 对比 `word/media/`，定位重复图片的章节位置。

### 4. （可选）副标 vs 主标交叉检查

```bash
python3 ~/.claude/skills/bid-diff-and-revise/scripts/compare_vs_ref.py \
  --drafts-dir <成果/md 目录> \
  --ref <主标.docx> \
  --out <目标>/vs-主标-雷同检查.md
```

从改动 MD 中抽 "改为"段，与主标全文比相似度，防"副标改完又撞主标"。

### 5. 按 L1 章节写改动草稿 MD（subagent 并行）

把逐段对照里"实质雷同段 ≥ 1"的 L1 章节挑出来，每个 L1 起一个 subagent 写 1 份 `fb-<L1名>-改动草稿.md`（或去掉 fb 前缀按项目约定）。每份 MD 按模板写：

- 顶部 frontmatter：目标 docx / L1 章节 / 雷同段号
- **原文 #xxxx** / **改为 #xxxx** 成对块
- 末尾汇总表

模板见 `~/.claude/skills/bid-diff-and-revise/templates/改动草稿-模板.md`。

### 6. 合并 rules JSON + 写 track-changes

```bash
# 6a. 合并 MD → rules JSON（含 3 道守卫）
python3 ~/.claude/skills/bid-diff-and-revise/scripts/gen_rules.py \
  --drafts-dir <成果/md 目录> \
  --docx <目标.docx> \
  --out <目标目录>/_revise_rules.json

# 6b. 调用 docx_tools.py 写 track-changes
python3 ~/Dev/doctools/scripts/document/docx_tools.py track-changes review \
  <目标.docx> \
  -o <目标目录>/（修改稿）<名字>.docx \
  -r <目标目录>/_revise_rules.json \
  -a <作者名>
```

**gen_rules.py 3 道守卫（必保留）**：
1. **引号自动 swap**：MD 里直引号自动尝试弯引号 variant 再验 find 是否在 docx
2. **title-only rule 跳过**：find 和 replace 都是短标题时跳过（用户常反馈"标题别动"）
3. **说明性括号剥**：replace 中"（面向...）""（含...）"等注释性括号自动删

### 7. 特殊处理 + 验收

```bash
# 7a. 表格行删除（track-changes 做不了）
python3 ~/.claude/skills/bid-diff-and-revise/scripts/delete_table_rows.py \
  --docx <修改稿.docx> \
  --table-index <N> \
  --rows <FROM>:<TO> \
  --expected-first-col <期望首列值> \
  --expected-residue <要删的行里应出现的关键词>

# 7b. 模拟接受所有修订后扫残留术语
python3 ~/.claude/skills/bid-diff-and-revise/scripts/verify_after_accept.py \
  --docx <修改稿.docx> \
  --terms "自然资源集约利用考核,林长制,水土保持目标责任制"
```

## 踩坑预警（来自 panan 实战）

1. **正则匹配带括号说明的 `**改为 #185（第 1 步...）**`**：用 `[^*]*` 吃到 `**`
2. **引号直/弯**：MD 直引号 vs docx 弯引号 → 靠 gen_rules.py 守卫 1 自动 swap
3. **subagent 会 paraphrase 原文**：find-not-in-docx 校验 + 手工修正
4. **MD `> 原文` 后接 `> **2024 原文 #xxx**：注释`**：解析跳过 `**` 开头的辅助行
5. **标题+引言拼 replace 丑**：find=title, replace=title+\n+intro 在 Word 里 track-changes 显示重复标题，需另法插引言段
6. **表行删除不能 track-changes**：单独脚本直删
7. **残留扫描 track-changes docx 不准**：paragraph.text 含 ins+del 混文本，必须先剔 w:del + 解包 w:ins 再扫

## 外部依赖

- `~/Dev/doctools/scripts/document/docx_tools.py track-changes review` — 主要写入工具
- `python-docx`（pip 包）

## 产出位置约定

```
<项目>/
├── <fb或对应子目录>/
│   ├── 逐段对照.md              # step 2 产出
│   ├── 图片重复清单.md          # step 3 产出
│   ├── _revise_rules.json       # step 6a 产出
│   └── （修改稿）<名字>.docx     # step 6b 产出（终稿）
└── 成果/md/
    ├── <前缀>-<L1名>-改动草稿.md   # step 5 产出（多份）
    └── vs-主标-雷同检查.md        # step 4 产出
```

## v0.1 → v1.0 升级条件

- [ ] 下一个标书项目完整跑一遍，验证硬编码都已参数化
- [ ] `gen_rules.py` 3 道守卫在新数据上经受住考验
- [ ] 通用化模板（`改动草稿-模板.md`）能被 subagent 直接套用
- [ ] 如果发现新的坑（如跨项目特异性），补进踩坑预警

## 相关 playbook

完整时间轴 + 决策过程：`~/Work/_playbooks/bids/panan-雷同破除-2026-04-17.md`
