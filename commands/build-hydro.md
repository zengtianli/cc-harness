构建 hydro app 的 Tauri 安装包。

## 参数

$ARGUMENTS = app 名称或 `all`

- 单个 app: `build capacity`
- 全部: `build all`

## 流程

1. 确定要构建的 app 列表
2. 对每个 app:
   - `cd apps/$APP && pnpm tauri build`
   - 报告产物路径和大小
3. 输出汇总表

## 输出示例

| App | 产物 | 大小 |
|-----|------|------|
| efficiency | 水效评估工具_1.0.0_aarch64.dmg | 4.2 MB |
| capacity | 纳污能力计算_1.0.0_aarch64.dmg | 3.8 MB |
