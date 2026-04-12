---
name: bid
description: 标书撰写技能。当处理 ~/Work/bids/ 下的标书项目，需要解析招标文件、搭建章节框架、盘点参考资料、走四阶段写作管线时触发。
---

# bid — 标书撰写

标书项目集中在 `~/Work/bids/`，方法论沉淀在 `~/Work/bids/CLAUDE.md`。本 skill 是入口，告诉你**做什么、按什么顺序、用哪个工具**。

## 核心原则

1. **三级优先级**：脚本 > skill > CC 直接。能脚本化的不要 AI，能 skill 的不要裸写。
2. **主会话不写正文**：只做规划、调度、验证。正文一律交 subagent，并带 4 维度约束。
3. **章节-评分硬绑定**：每章顶部必须贴"得满分要求"原文，写作 subagent 必须逐项响应。
4. **不问节奏**：拿到任务直接按"把它做好"全力推进，不要问截止日期/紧不紧。

## 标书撰写的 6 个阶段

### 阶段 1 — 项目初始化
```bash
cp -r ~/Work/bids/_template ~/Work/bids/{slug}
```
把招标文件原件丢进 `招标文件/`，把所有参考资料丢进 `参考/`。
填 `_project.yaml`（项目名、编号、采购人、预算、截止日期）。

### 阶段 2 — 招标文件解析
```bash
python3 ~/Dev/scripts/scripts/document/zbwj_parse.py ~/Work/bids/{slug}/招标文件/
```
脚本输出：
- `招标文件/*.md`（doc/docx → md，pandoc）
- `招标文件/scoring.json`（提取的评分表：序号 / 评分项 / 分值 / 得满分要求）
- `技术标框架.md`（按评分项生成章节骨架，每章贴好"得满分要求"）

人工复核 `scoring.json`，确保没漏分项。

### 阶段 3 — 参考资料盘点
让 Claude 读 `参考/` 下所有文档，生成 `参考/_index.md`：
```
| 文件 | 涵盖章节 | 可复用内容 | 是否最新 |
```
重点：标出"可直接复用 / 需更新数据 / 需新写"三类。
对延续项目，老中标稿是金矿，模板章（业绩、组织、质量、售后）几乎可以整段搬。

### 阶段 4 — 写作（subagent + 4 维度约束）
按 `技术标框架.md` 逐章派 subagent 写作，输出到 `成果/md/`。
每个 subagent prompt 必须包含：
- 该章的"得满分要求"
- D1-D4 维度约束（见 ~/Work/bids/CLAUDE.md）
- 参考资料盘点结果（告诉它哪段抄哪里）
- 当前章节的数据来源约束

### 阶段 5 — 四阶段管线（脚本）
```bash
cd ~/Work/bids/{slug}/成果/

# 5.1 质量修复（禁用词、数据来源标注）
python3 ~/Dev/scripts/scripts/document/report_quality_check.py md/ --bid --fix --output-dir md_clean/

# 5.2 结构标准化（标题/编号/评分引用/加粗/来源 6 项）
python3 ~/Dev/scripts/scripts/document/bid_standardize.py md_clean/ --scoring ../招标文件/scoring.json --fix --output-dir md_fixed/

# 5.3 生成图表 PNG（charts/*_config.json）
for cfg in charts/*_config.json; do
  type=$(echo "$cfg" | grep -o 'gantt\|bar\|flow')
  python3 ~/Dev/scripts/scripts/document/chart_${type}.py "$cfg" -o "charts/$(basename "$cfg" _config.json).png"
done

# 5.4 ASCII art → PNG 引用
python3 ~/Dev/scripts/scripts/document/chart_insert.py md_fixed/ --config charts/insert_config.json --fix --output-dir md_final/

# 5.5 合并 + 转 docx
python3 ~/Dev/scripts/scripts/document/md_merge.py md_final/ -o merged.md
python3 ~/Dev/scripts/scripts/document/md_docx_template.py merged.md -o 技术标.docx
```

### 阶段 6 — 终审
- 跑 `report_quality_check.py --check` 看残留问题
- 自审：每章是否都响应了"得满分要求"每一条
- D3 预判：扮演评审专家，能不能问倒自己

## 4 维度写作约束（subagent 必带）

| 维度 | 检查要点 |
|------|----------|
| D1 溯源链 | 每个结论有推导过程，筛选链条完整不跳步 |
| D2 立场措辞 | 站乙方立场，委婉表达，风险抛给甲方/政策 |
| D3 预判评审 | 写完假装审查专家，能否问倒自己 |
| D4 数据纵深 | 总量→结构→趋势→对比，先全貌后细节 |

## 模板章（跨项目高复用）

下列章节高度模板化，新项目可从老项目搬：
- **质量保证措施**（评分常 3 分）
- **售后服务方案**（注意各地"当天到现场"得满分的要求）
- **进度保障措施**
- **组织架构与人员配置**
- **业绩与资质**

参考：`~/Work/bids/qiantang-monitoring-2026/成果/md_final/11.md` `12.md`

## 不要做的事

- ❌ 不要问用户"截止日期紧不紧 / 项目什么状态 / 今天做到哪一步"
- ❌ 主会话不要直接写正文，一定派 subagent
- ❌ 不要跳过 4 维度约束
- ❌ 不要手画图表，所有图走 chart_*.py + JSON 配置
- ❌ 不要在 md_final 之后再手动改文字（改 md_clean，重跑管线）
