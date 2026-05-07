# QGIS 空间处理工作流（Phase 1）

## 数据准备清单

### 输入数据（需要准备）

| 数据 | 格式 | 说明 |
|-----|------|------|
| 堤防线 | .shp | 含堤防名称、左右岸 |
| 保护片 | .shp | 含保护片编码(SX0001等) |
| 河道中心线 | .shp | 或手动绘制 |
| 高程点/DEM | .shp/.tif | 堤顶高程 |
| 断面数据 | .shp | 含断面高程 |
| 行政区划 | .shp | 乡镇级 |
| 影响分析网格 | .shp | 1km网格，含人口/GDP |
| Element/Node | .shp | SMS网格数据 |
| 耕地/房屋/道路 | .shp | 底板数据 |

### 参考数据（已有）

| 文件 | 位置 |
|-----|------|
| city_county_town.csv | `脚本/xlsx/input/` |
| region_name_code.csv | `脚本/xlsx/input/` |
| GDP人口数据.csv | `脚本/xlsx/input/` |

## 脚本位置

```
~/Dev/tools/hydro-qgis/pipeline/
```

## 10步工作流

```
Step 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 99
  |       |     |     |     |     |     |     |     |     |     |
  |       |     |     |     |     |     |     |     |     |     └─ 批量导出
  |       |     |     |     |     |     |     |     |     └─ 保护片图层
  |       |     |     |     |     |     |     |     └─ 对齐输出字段
  |       |     |     |     |     |     |     └─ Vegetation层
  |       |     |     |     |     |     └─ Road层
  |       |     |     |     |     └─ House层
  |       |     |     |     └─ 增强Grid层
  |       |     |     └─ 对齐堤防字段
  |       |     └─ 赋值高程
  |       └─ 切割堤段
  └─ 生成河道中心点（含里程）
```

## Step 01: 生成河道中心点

**目标**：从河道中心线生成等距点，赋值里程

**脚本**：`01_generate_river_points.py`

**手动步骤**：
```
1. 绘制/加载河道中心线（从上游向下游）
2. 处理工具箱 → 矢量几何 → 沿着线生成点
   - 距离：100米
3. 运行脚本赋值里程LC
```

**输出**：`河道中心点.shp`（含 LC 字段）

## Step 01.5: 断面里程赋值（可选）

**目标**：将里程赋值给断面

**脚本**：`01.5_assign_lc_to_cross_sections.py`

**说明**：如果有断面数据，需要关联里程

## Step 02: 切割堤段

**目标**：用河道中心点切割堤防线，生成堤段

**脚本**：`02_cut_dike_sections.py`

**手动步骤**：
```
1. 近邻分析：河道中心点 → 堤防
2. 生成切割点
3. 处理工具箱 → 矢量叠加 → 用点分割线
4. 传递里程属性
```

**输出**：`堤段.shp`

## Step 03: 赋值高程到堤防

**目标**：从高程点赋值堤顶高程

**脚本**：`03_assign_elevation_to_dike.py`

**手动步骤**：
```
处理工具箱 → 矢量通用 → 按位置连接属性（最近）
- 目标图层：堤段
- 连接图层：高程点
- 最大距离：50米
```

**输出**：堤段含 `ddgc`（堤顶高程）字段

## Step 04: 对齐堤防字段

**目标**：标准化堤防/堤段字段名称

**脚本**：`04_align_dike_fields.py`

**标准字段**：
```
ds_code     - 堤段编码
df_code     - 堤防编码
zya         - 左右岸
river_name  - 河道名称
LC          - 里程
ddgc        - 堤顶高程
```

## Step 04.5: 修正河道名称（可选）

**脚本**：`04.5_fix_river_name.py`

**说明**：统一河道名称格式

## Step 05: 增强 Grid 图层

**目标**：为Grid添加 town、polderId 字段

**脚本**：`05_enrich_grid_layer.py`

**手动步骤**：
```
1. 按位置连接属性 → 关联乡镇
2. 按位置连接属性 → 关联保护片
3. 计算 grid_id、area
```

**输出**：`grid.shp`（含 grid_id, town, polderId, area, elevation）

## Step 06: 生成 House 图层

**目标**：房屋面与Grid相交

**脚本**：`06_generate_house_layer.py`

**手动步骤**：
```
处理工具箱 → 矢量叠加 → 相交
- 输入：房屋面
- 叠加：grid
```

**输出**：`house.shp`（含 grid_id, town, polderId, area）

## Step 07: 生成 Road 图层

**目标**：道路线与Grid相交

**脚本**：`07_generate_road_layer.py`

**输出**：`road.shp`（含 grid_id, town, polderId, length）

## Step 08: 生成 Vegetation 图层

**目标**：耕地面与Grid相交

**脚本**：`08_generate_vegetation_layer.py`

**输出**：`vegetation.shp`（含 grid_id, town, polderId, area）

## Step 09: 对齐输出字段

**目标**：标准化所有输出图层字段

**脚本**：`09_align_output_fields.py`

## Step 10: 生成保护片图层

**目标**：整理保护片属性

**脚本**：`10_generate_baohu_layer.py`

**输出**：`保护片.shp`（含标准字段）

## Step 99: 批量导出

**目标**：导出所有图层为 GeoJSON/Shapefile

**脚本**：`99_batch_export_layers.py`

**输出目录**：
```
output/
├── sx_baohu.geojson      # 保护片
├── sx_duan.geojson       # 堤段
├── shp/
│   ├── grid.shp
│   ├── house.shp
│   ├── road.shp
│   └── vegetation.shp
└── params/
    ├── GRID_ELEVATION.txt
    ├── economy.txt
    └── LossRate.txt
```

## QGIS 脚本运行方法

**方法1：QGIS Python控制台**
```python
exec(open('/Users/tianli/Dev/tools/hydro-qgis/pipeline/01_generate_river_points.py').read())
```

**方法2：批量执行**
```bash
cd ~/Dev/tools/hydro-qgis/pipeline/
./run_pipeline.sh 1-5    # 执行步骤1-5
./run_pipeline.sh 6-10   # 执行步骤6-10
```
