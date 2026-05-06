---
name: zdwp-project
description: ZDWP 水利公司项目上下文与架构。集团架构、涉及县市、数据字段、常用命令、开发部调用、交付规范。当在水利公司项目中工作时触发。
---

# ZDWP 项目上下文

## 集团架构

```
一人集团
├── 开发部: ~/Dev/
│   ├── hydro-qgis/       # QGIS 空间处理
│   ├── hydro-risk/       # 风险图 Excel 处理
│   ├── hydro-geocode/    # 地理编码工具
│   └── doctools/         # 文档工具
│
└── 水利公司: ~/Dev/Work/zdwp/
    ├── resources/        # GIS、参考资料、基础数据
    ├── projects/         # 11个业务领域
    └── archives/         # 历史归档
```

## 业务部项目

生态流量、风险图、水源地评估、供水管网、可用水量、浙东引水、岸线规划、分质供水、农业水价、再生水利用、用水权改革

## 涉及县市

| 地市 | 县区 |
|------|------|
| 丽水市 | 景宁、缙云、青田、龙泉、庆元、云和、松阳、遂昌 |
| 金华市 | 婺城、金东、兰溪、东阳、义乌、永康、武义、浦江、磐安 |
| 其他 | 温岭（台州）、仙居（台州）、长兴（湖州） |

## 数据字段

### 水库数据

| 字段 | 含义 |
|------|------|
| NAME | 水库名称 |
| CODE | 编码 |
| COUNTY | 所在县 |
| TCR | 总库容 (万m³) |
| UCR | 兴利库容 |
| RCAREA | 集雨面积 (km²) |
| NPL | 正常蓄水位 (m) |

### GIS 数据

- 坐标系（三轨并存）：
  - **EPSG:4549** — CGCS2000 3度带 CM 120E（投影 / Gauss-Kruger）— 大中型水库.shp、全省水库.geojson
  - **EPSG:4490** — CGCS2000 地理坐标（lng/lat）— 行政境界（乡镇）.shp、河流手册.shp
  - **EPSG:4326** — WGS84（小水电.geojson）+ 输出给 QGIS/底图统一用
- 格式: GDB, SHP, GeoJSON
- SSOT: `~/Dev/labs/hydro-qgis/lib/hydraulic/qgis_config.py` 的 `TARGET_CRS / GEO_CRS / COUNTY_SLICE_SOURCES`
- 工具：`bash ~/Dev/labs/hydro-qgis/scripts/cut_county.sh <县名> <输出目录>`（按县切 5 类要素）

## 常用命令

```bash
# 读取 Word
python ~/Dev/tools/doctools/scripts/document/docx_tools.py <file>

# 读取 Excel
python ~/Dev/stations/web-stack/services/hydro-risk/read_xlsx.py <file>

# 一键格式化 Word
python ~/Dev/tools/doctools/scripts/document/docx_text_formatter.py <file>

# 地理编码
python ~/Dev/stations/web-stack/services/hydro-geocode/src/geocode_by_address.py
```

## Symlink 桥接

业务数据在 zdwp，自动化脚本在 `~/Dev/hydro-*`，通过 symlink 桥接：

| zdwp 路径 | 指向 |
|-----------|------|
| `projects/risk-map/code` | `~/Dev/stations/web-stack/services/hydro-risk` |
| `projects/risk-map/qgis` | `~/Dev/labs/hydro-qgis` |
| `projects/zhedong-diversion/irrigation` | `~/Dev/stations/web-stack/services/hydro-irrigation` |

在 zdwp 下开 CC，可同时看到数据和代码。Git 管理在 `~/Dev/` 侧进行。

## 交付规范

| 交付物 | 必须 |
|--------|------|
| 成果文件 | 是 |
| 成果说明.md | 是 |
| 数据来源注明 | 是 |

文件命名：`[日期]_[业务]_[内容]_[版本].[后缀]`

## 禁止事项

- 不开发通用脚本（交给开发部）
- 不配置系统环境（交给配置部）
- 不配置定时任务（交给总控）

## 关键路径

| 内容 | 路径 |
|-----|------|
| 水利公司 | `/Users/tianli/Dev/Work/zdwp/` |
| 资源部 | `resources/` |
| 业务部 | `projects/` |
| 水利专用工具 | `~/Dev/hydro-*/` |
