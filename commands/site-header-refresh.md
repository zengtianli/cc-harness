---
description: 把站内开场样式（site-header.html）从 yaml SSOT 同步到所有消费者
---

把 `~/Dev/tools/configs/menus/sites/<name>.yaml` 的 `header` 字段渲染成统一格式的 site-header.html，写入各子站 repo。

## 用法

```bash
/site-header-refresh
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/menus.py render-site-header --all -w
```

## 范围（5 个站）

| 站 | repo | site-header.html 输出 |
|---|---|---|
| cmds | ~/Dev/stations/cmds | 📚 CC Docs · Claude Code 命令 & 技能说明书 |
| stack | ~/Dev/stations/stack | 🗂 Stack · ~/Dev 项目架构地图 |
| journal | ~/Dev/journal | 📔 Journal · HANDOFF / 方案 / 复盘时间线 |
| cc-evolution | ~/Dev/_archive/cc-evolution-20260419 | 🔄 Changelog · CC 自我进化变更日志 |
| ops-console | ~/Dev/stations/ops-console | 📊 Dashboard · VPS 服务 · 任务 · Git 提交总览 |

## 渲染产物

每个 site-header.html 含：
1. `<style>` — `.tlz-site-header` 类完整 CSS（统一字体、间距、颜色）
2. `<header>` — 含面包屑（tianlizeng.cloud / Services / <site>）+ icon + title + tagline

各站 generate.py 用 `_load_site_header()` 注入到 navbar 之后、内容之前。

## 后续动作

`/site-header-refresh` 不会触发各站重 deploy。你要：

1. cd 进各 repo `python3 generate.py` 重新生成 site/
2. `bash deploy.sh` 部署到 VPS

或者用 `/deploy` 跑统一部署（针对单个 repo）。

## 漂移检测

`/menus-audit` 报告里的 `site-header-drift` 类别会列出 yaml 与本地 site-header.html 不一致的站点。

## 规则

- 只写本地文件，不动 git（让你统一在 ship 时提交）
- 渲染失败立即报错（不静默）
- 5 站缺其中任何一个 site-header.html 时 audit 会报 missing
