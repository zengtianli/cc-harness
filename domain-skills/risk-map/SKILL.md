---
name: risk-map
description: 洪水风险图项目知识。当处理风险图数据、QGIS空间处理、Excel表格填充时触发。
---

# 风险图项目知识

> 路径：`.claude/skills/zdwp-risk-map/`

## 核心要点

| 属性 | 值 |
|------|-----|
| 项目名称 | 2025风险图 |
| 项目类型 | 水利风险分析 + GIS空间数据处理 |
| 涉及流域 | 华溪(HX)、熟溪(SX)、白溪(BX)、乌溪(WX)、古竹溪(GZX) |
| 坐标系 | CGCS2000（输出时可转 WGS84） |
| 编码规范 | 保护片编码必须大写（HX/SX/BX/WX/GZX） |
| 岸别字段 | zya 只能是 L（左岸）或 R（右岸） |

## 工作流概述

```
Phase 1: QGIS空间处理（10步）  ── 1-2天，半自动化
    |
Phase 2: Excel表格填充（3套）  ── 2-4小时，脚本自动化
    |       套1: 库表结构（4个脚本）
    |       套2: 预报调度（1个脚本）
    |       套3: 风险分析（9个脚本）
    |
Phase 3: 参数文件生成          ── 30分钟，脚本自动化
    |       GRID_ELEVATION.txt / economy.txt / LossRate.txt
    |
Phase 4: 最终成果输出          ── 1小时，整理导出
```

## 脚本位置

| 类型 | 路径 |
|------|------|
| QGIS 脚本（12个） | `~/Dev/labs/hydro-qgis/pipeline/` |
| Excel 脚本（14个） | `~/Dev/stations/web-stack/services/hydro-risk/` |
| 共享库 | `~/Dev/stations/web-stack/services/hydro-risk/lib/` |
| 本地步骤脚本 | `scripts/`（01~07） |

## 项目结构

```
风险图/
├── 县市项目/           # 各流域数据（熟溪/华溪/白溪...）
├── scripts/            # 本地 QGIS 步骤脚本
├── 参考/               # 参考文档
└── docs/               # 项目文档
```

## 详细参考

- 完整 QGIS 工作流：`references/qgis-workflow.md`
- Excel 表格填充指南：`references/excel-filling.md`
- 项目架构与 Agent 调度：`references/project-architect.md`
