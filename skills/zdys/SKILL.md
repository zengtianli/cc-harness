---
name: zdys
description: 浙东引水项目知识。当处理浙东引水运行态势、调度模型、灌溉需水计算时触发。
---

# 浙东引水项目知识

> 路径：`.claude/skills/zdwp-zdys/`

## 核心要点

- **项目名称**：浙东水资源配置工程运行态势研究
- **区域**：浙江省浙东地区，覆盖 15 个平原灌区，总面积 4600+ km²
- **核心任务**：水资源调度与配置、河区水量平衡计算、灌溉需水模型、干旱/洪涝/生态等多场景调度
- **项目状态**：进行中

### 项目结构

```
浙东引水/
├── 主文档/               # 核心文档（五场景调度、基础数据、FASE模型体系）
├── 代码/                 # 模型代码（概湖降雨模型、灌溉需水模型）
├── 学术成果/             # 论文、专利
└── 报告/                 # 输出报告
```

## 技术要点

### 灌溉需水模型

- **原理**：基于水量平衡的农业灌溉需水计算
- **核心公式**：水位变化 = 降雨 + 灌溉 - 蒸发蒸腾 - 渗漏 - 排水
- **计算模式**：旱地作物（dryland）、水稻灌溉（paddy）、综合模式（both）
- **数据格式**：支持 TXT 模式和 B3 NC 数据模式
- **单位约定**：水位/水深 mm，面积 km²，水量 万m³
- **灌区参数**：实灌面积 2,540,000 亩，灌溉水利用系数 0.5328

### B3 比赛适配

- **评测指标**：灌溉期总量相对误差、单旬相对误差最大值（误差 <=25% 合格）
- **当前精度**：约 21%，基本达标
- **待完成**：逐日转逐旬聚合、参数率定（Kc）、多年验证、Linux .so 封装

### 运行方式

```bash
# TXT 模式
cd ngxs && python main.py [数据目录]

# B3 NC 模式
python main.py --b3 <NC数据目录>
python main.py --b3 --year 2020 <NC数据目录>
```

## 工具与脚本

### 文档读取

```bash
# Word 文档
/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py <file.docx>

# Excel 文件
/opt/homebrew/bin/python3 ~/Dev/hydro-risk/read_xlsx.py <file.xlsx> --list

# NC 文件
# [已废弃] read_nc.py
```

### 格式修复

```bash
# Word 一键格式化
/opt/homebrew/bin/python3 ~/Dev/doctools/scripts/document/docx_text_formatter.py <file.docx>

# Word 表格样式
# [已废弃] apply_table_style.py

# Markdown 格式修复
# [已废弃] formatter.py
```

### 格式转换

```bash
# Word -> Markdown
# [已废弃] docx_to_md.sh

# Excel -> CSV
# [已废弃] to_csv.py

# PDF -> Markdown
# [已废弃] pdf_to_md.sh
```

### 比较与分析

```bash
# 比较文件/文件夹
# [已废弃] compare_files_folders.py

# 比较 Excel 数据
# [已废弃] compare_excel_data.py

# 字数统计
# [已废弃] count_chars.py
```

## 工作约定

1. **先查后写** - 新脚本前先搜索脚本库
2. **备份优先** - 修改文件前自动备份
3. **通用入库** - 可复用脚本放脚本库
4. **数据文件编码** - UTF-8
5. **输出格式** - 保持与原有 txt 格式一致

## 详细参考

- 项目上下文：`references/project-context.md`
- 工具命令：`references/project-tools.md`
- 灌溉需水模型：`references/irrigation-model.md`
