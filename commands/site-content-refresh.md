---
description: 把站内统一 CSS（site-content.css）从 SSOT 模板同步到 4 个消费者站
---

把 `~/Dev/devtools/lib/templates/site-content.css` 同步到各子站 repo，让所有站点的卡片/grid/配色与 `services` 页保持视觉一致。

## 用法

```bash
/site-content-refresh
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/menus.py build-site-content -w
```

## 范围（4 站）

| 站 | repo | 输出 |
|---|---|---|
| cmds | ~/Dev/cmds/site-content.css | 命令文档站 |
| stack | ~/Dev/stack/site-content.css | 项目地图站 |
| logs | ~/Dev/logs/site-content.css | 时间线站 |
| ops-console | ~/Dev/ops-console/site-content.css | 控制台站 |

## 后续

`build-site-content` 不会触发各站重 deploy。要让线上生效：
1. cd 进各 repo `python3 generate.py` 重生成（或对 ops-console `pnpm build`）
2. `bash deploy.sh` 部署

## 漂移检测

`/menus-audit` 报告里的 `site-content-drift` 类别会列出各 repo site-content.css 与 SSOT 模板不一致的项。

## 共享的关键 class

| class | 用途 |
|---|---|
| `.tlz-page` | body 玻璃浅灰背景 (#f5f5f7) |
| `.tlz-container` | 1280px 容器 |
| `.tlz-section` / `.tlz-section-title` | 分组（icon + title + count） |
| `.tlz-grid` | 自适应 1/2 列 grid |
| `.tlz-card` | 玻璃卡片（与 services ServiceCard 视觉等价） |
| `.tlz-card--row` | 横向行式卡片（logs 时间线用） |
| `.tlz-search` / `.tlz-btn` / `.tlz-filters` | 玻璃搜索框、按钮、过滤组 |
| `.tlz-stats-bar` | 顶部统计条 |
| `.tlz-dot--ok/--bad/--unknown` | 状态点 |

## 规则

- 只写本地文件，不动 git（让你统一在 ship 时提交）
- 4 站全部覆盖（之前的 5 站 - journal/cc-evolution 已归档）
- 与 services 视觉等价（不严格 byte-equal，因为 services 用 Tailwind）
