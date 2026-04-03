# Excel 表格填充与成果输出（Phase 2-4）

## Phase 2: Excel 表格填充

### 脚本位置

```
~/Dev/hydro-risk/
```

### 三套表格

| 套 | 表格类型 | 脚本前缀 | 数量 |
|----|---------|---------|------|
| 1 | 库表结构（下发） | 1.x | 4个 |
| 2 | 预报调度 | 2.x | 1个 |
| 3 | 风险分析 | 3.x | 9个 |

### 套1: 库表结构填充

| 序号 | 脚本 | 填充内容 |
|-----|------|---------|
| 1.1 | `1.1_database_protection_area.py` | 保护片信息 |
| 1.2 | `1.2_database_dike_section.py` | 堤段对应信息 |
| 1.3 | `1.3_database_dike.py` | 堤防信息 |
| 1.4 | `1.4_database_river_centerline.py` | 河道中心线信息 |

**运行**：
```bash
python ~/Dev/hydro-risk/1.1_database_protection_area.py
python ~/Dev/hydro-risk/1.2_database_dike_section.py
python ~/Dev/hydro-risk/1.3_database_dike.py
python ~/Dev/hydro-risk/1.4_database_river_centerline.py
```

### 套2: 预报调度填充

| 序号 | 脚本 | 填充内容 |
|-----|------|---------|
| 2.1 | `2.1_forecast_cross_section.py` | 断面数据 |

### 套3: 风险分析填充

| 序号 | 脚本 | 填充内容 |
|-----|------|---------|
| 3.01 | `3.01_risk_protection_info.py` | 保护区基本信息 |
| 3.02 | `3.02_risk_protection_region.py` | 保护区范围 |
| 3.03 | `3.03_risk_protection_dike_relation.py` | 保护区-堤段关系 |
| 3.04 | `3.04_risk_dike_section_info.py` | 堤段信息 |
| 3.05 | `3.05_risk_elevation_relation.py` | 高程关系 |
| 3.06 | `3.06_risk_section_mileage.py` | 断面里程 |
| 3.07 | `3.07_risk_dike_info.py` | 堤防信息 |
| 3.08 | `3.08_risk_dike_profile.py` | 堤防剖面 |
| 3.09 | `3.09_risk_facilities.py` | 设施信息 |

**批量运行**：
```bash
for i in 01 02 03 04 05 06 07 08 09; do
    python ~/Dev/hydro-risk/3.${i}_*.py
done
```

### Excel 输出位置

```
脚本/xlsx/output/
└── 风险分析-熟溪.xlsx   ← 已有（可覆盖更新）
```

## Phase 3: 参数文件生成

### 需要生成的文件

| 文件 | 格式 | 说明 |
|-----|------|------|
| `GRID_ELEVATION.txt` | code\televation\tpolderId | 网格高程 |
| `economy.txt` | polderId\tpop\tgdp | 经济参数 |
| `LossRate.txt` | water_depth\tloss | 损失率（固定） |
| `DOT_LC.txt` | - | 里程点 |
| `POLDER_DS_DDGC_CONTACT.txt` | - | 保护片-堤段高程关系 |

### GRID_ELEVATION.txt

**脚本**：`05_生成GRID_ELEVATION.py`（全省参考/scripts/）

**手动方式**：
```
1. 导出grid属性表为CSV
2. 保留列：grid_id, elevation, polder_id
3. 重命名：grid_id→code, polder_id→polderId
4. 保存为制表符分隔的txt
```

**格式**：
```
code	elevation	polderId
1	94.6068	SX0001
2	90.7119	SX0001
```

### economy.txt

**脚本**：`06_计算economy参数.py`（全省参考/scripts/）

**计算公式**：
- `pop` = 保护人口(万人) / 房屋面积(km2)
- `gdp` = 保护区GDP(万元) / 房屋面积(km2)

**格式**：
```
polderId	pop	gdp
SX0001	2.926678	335332.2997
SX0002	0.785125	19617.7022
```

### LossRate.txt

**直接创建（固定值）**：
```
water_depth	loss
0.5	0.02
1	0.17
2	0.5
3	0.61
100000	0.72
```

## Phase 4: 最终成果输出

### 成果目录结构

```
{流域名}/
├── 风险统计数据/
│   ├── GRID_ELEVATION.txt
│   └── {流域代码}/
│       ├── params/
│       │   ├── economy.txt
│       │   └── LossRate.txt
│       └── shp/
│           ├── grid.shp
│           ├── house.shp
│           ├── road.shp
│           └── vegetation.shp
│
├── GeoJSON/
│   ├── {代码}_baohu.geojson     # 保护片
│   └── {代码}_duan.geojson      # 堤段
│
├── Excel/
│   ├── 库表结构-{流域名}.xlsx
│   ├── 预报调度-{流域名}.xlsx
│   └── 风险分析-{流域名}.xlsx
│
└── 文档/
    └── 处理说明.md
```

### 质量检查清单

- [ ] grid.shp 所有网格都有 polderId
- [ ] house/road/vegetation 都关联了 grid_id
- [ ] GRID_ELEVATION.txt 行数 = grid要素数
- [ ] economy.txt 保护片数量正确
- [ ] Excel表格所有必填字段完整
- [ ] GeoJSON 坐标系正确（WGS84）

## 常用命令速查

### Excel 脚本

```bash
# 进入脚本目录
cd ~/Dev/hydro-risk/

# 查看可用脚本
ls *.py

# 执行单个脚本
python 3.03_risk_protection_dike_relation.py

# 查看Excel结构
python quick_check.py 风险分析-熟溪.xlsx
```

### 数据检查

```bash
# 查看shp信息
ogrinfo -so grid.shp grid

# 查看GeoJSON要素数
ogrinfo -so sx_baohu.geojson sx_baohu

# 行数统计
wc -l GRID_ELEVATION.txt
```
