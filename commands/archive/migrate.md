---
description: 将 Python/Streamlit 项目移植到 Tauri 桌面 app（Rust 后端 + React 前端）
---

将一个 Python/Streamlit 项目的计算逻辑移植到对应的 Tauri 桌面 app。

## 参数

$ARGUMENTS = 源项目路径或 app 名称

解析规则：
- 如果是路径（含 `/`）→ 直接使用
- 如果是名称（如 `capacity`）→ 查找 `~/Dev/hydro-$ARGUMENTS/`
- 如果是 `hydro-xxx` 格式 → 查找 `~/Dev/$ARGUMENTS/`

## 前置条件

- 源 Python 项目存在
- Tauri 目标目录已存在（骨架已生成）
- 如果目标不存在，提示用户先创建骨架

## 执行流程

### 1. 分析 Python 源码

读取源项目下所有 Python 计算逻辑文件：
- `src/` 目录下所有 `.py` 文件
- `app.py` 入口（了解 UI 流程和数据流）
- 如有 `plugin.yaml`，读取了解项目描述

完整理解：
- 输入数据格式（Excel sheet 名、列名、数据类型）
- 计算公式和算法
- 输出数据格式
- UI 流程（几个 tab，每个 tab 做什么）

### 2. 编写 Rust 计算模块

在目标 `src-tauri/src/` 下创建：

- `calc/types.rs` — 所有 serde 输入/输出结构体
- `calc/` 下的计算模块 — 移植 Python 公式，保持函数名对应
- `calc/mod.rs` — 模块导出
- `commands/io.rs` — Excel 读写（如有 hydro-common 则用其 cell_str/cell_f64）
- `commands/calc.rs` — 计算编排命令
- `commands/mod.rs`
- `sample_data.rs` — 从 Python 的 sample_data 或测试数据移植
- 更新 `lib.rs` — 注册所有模块和 Tauri commands
- 更新 `main.rs` — 正确引用 crate 名

每个计算函数写 `#[cfg(test)]` 单元测试，用 Python 版的示例数据验证数值一致。

### 3. 编写 React 前端

在目标 `src/` 下创建：

- `lib/types.ts` — 镜像 Rust 结构体
- `lib/commands.ts` — typed invoke 封装
- `hooks/useCalculation.ts` — 状态管理
- `pages/` — 按 Python app.py 的 tab 结构创建页面组件
- `App.tsx` — 组装页面

如果是 hydro-apps monorepo，组件从 `@hydro/shared` 导入。
样式从共享 `global.css` 导入（在 main.tsx 中）。

### 4. 验证

- `cargo test` — Rust 单元测试通过
- `npx vite build` — 前端构建通过
- 报告移植结果

## 输出

移植完成后输出：
- 移植了哪些计算模块
- 创建了哪些页面
- 测试结果
- 与 Python 版的差异说明（如有）

## 注意事项

- 保持中文 UI，列名/sheet 名与 Python 版一致
- Excel 列名按位置索引解析（0-based），不依赖中文列名匹配
- 如果需要额外 Rust 依赖，在 Cargo.toml 中添加
