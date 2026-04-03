将一个 hydro-xxx Streamlit 项目的计算逻辑移植到对应的 Tauri 桌面 app。

## 参数

$ARGUMENTS = app 名称 (如 `capacity`, `reservoir`)

## 前置条件

- `apps/$ARGUMENTS/` 目录已存在（由 `new-app.sh` 生成的骨架）
- 对应的 Python Streamlit 项目在 `~/Dev/hydro-$ARGUMENTS/`

## 执行流程

### 1. 读取 Python 源码

读取 `~/Dev/hydro-$ARGUMENTS/` 下所有 Python 计算逻辑文件：
- `src/` 目录下所有 `.py` 文件
- `app.py` 入口（了解 UI 流程和数据流）
- 如有 `plugin.yaml`，读取了解项目描述

完整理解：
- 输入数据格式（Excel sheet 名、列名、数据类型）
- 计算公式和算法
- 输出数据格式
- UI 流程（几个 tab，每个 tab 做什么）

### 2. 编写 Rust 计算模块

在 `apps/$ARGUMENTS/src-tauri/src/` 下创建：

- `calc/types.rs` — 所有 serde 输入/输出结构体
- `calc/` 下的计算模块 — 移植 Python 公式，保持函数名对应
- `calc/mod.rs` — 模块导出
- `commands/io.rs` — Excel 读写（用 hydro-common 的 cell_str/cell_f64）
- `commands/calc.rs` — 计算编排命令
- `commands/mod.rs`
- `sample_data.rs` — 从 Python 的 sample_data 或测试数据移植
- 更新 `lib.rs` — 注册所有模块和 Tauri commands
- 更新 `main.rs` — 正确引用 crate 名

每个计算函数写 `#[cfg(test)]` 单元测试，用 Python 版的示例数据验证数值一致。

### 3. 编写 React 前端

在 `apps/$ARGUMENTS/src/` 下创建：

- `lib/types.ts` — 镜像 Rust 结构体
- `lib/commands.ts` — typed invoke 封装
- `hooks/useCalculation.ts` — 状态管理（参考 efficiency 的模式）
- `pages/` — 按 Python app.py 的 tab 结构创建页面组件
- `App.tsx` — 用 `@hydro/shared` 的 AppShell 组装

组件从 `@hydro/shared` 导入: AppShell, DataTable, GradeBadge, FileUpload, AlphaSlider。
样式从 `@hydro/shared/src/styles/global.css` 导入（在 main.tsx 中）。

### 4. 验证

- `cd apps/$ARGUMENTS/src-tauri && cargo test` — 单元测试通过
- `cd apps/$ARGUMENTS && npx vite build` — 前端构建通过
- 报告移植结果

## 输出

移植完成后输出：
- 移植了哪些计算模块
- 创建了哪些页面
- 测试结果
- 与 Python 版的差异说明（如有）

## 注意事项

- Rust Cargo.toml 已有 hydro-common 依赖，不需要 ndarray/ndarray-stats（efficiency 用了，其他不一定需要）
- 如果需要额外 Rust 依赖（如某个 app 需要 ndarray），在 Cargo.toml 中添加
- 保持中文 UI，列名/sheet 名与 Python 版一致
- Excel 列名按位置索引解析（0-based），不依赖中文列名匹配
