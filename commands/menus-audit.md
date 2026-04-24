---
description: 检测站群菜单/导航 yaml SSOT (~/Dev/tools/configs/menus/) 与各消费者源码的漂移（14 类，含路径域）
---

跨 11 个源做只读对账，配套 `~/Dev/tools/configs/menus/` 图模型（entities/ + relations/ + consumers.yaml + sites/*.yaml + navbar.yaml），并融合路径注册表（`~/Dev/paths.yaml`）漂移检查。

## 用法

```bash
/menus-audit
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/menus.py audit          # 默认：paths-drift 只警告
python3 ~/Dev/devtools/lib/tools/menus.py audit --strict # paths-drift 失败也 exit 1
```

## 报告分类（14 类）

**图层不变量（2026-04-22 新增）**：

- `graph-invariants` — 所有 `_id` 引用解析 / 每子域 1 个 group / 无空 group / navbar group_id 合法 / services.ts 未被手改
- `consumer-registry` — `consumers.yaml` 每条 path 存在 / subdomain_id 可解析 / navbar_html auto-discovery 对账
- `react-mega-navbar-drift` — `devtools/lib/react/mega-navbar.tsx` ≠ 两站 `components/mega-navbar.tsx`

**8 类消费者漂移**：

- `navbar-drift` — `navbar.yaml` 渲染 ≠ `devtools/lib/templates/site-navbar.html`
- `website-nav-drift` — `sites/website.yaml` ≠ `website/lib/profile-config.ts` 的 `navigationConfig`
- `website-shared-nav-drift` — `navbar.yaml` 渲染 ≠ `website/lib/shared-navbar.generated.ts`
- `ops-console-drift` — `sites/ops-console.yaml` ≠ `ops-console/components/section-nav.tsx` 的 `ITEMS`
- `cmds-drift` — `sites/cmds.yaml` ≠ `cmds/generate.py` 的 `CATEGORY_MAP/ORDER/COLOR`
- `stack-drift` — `sites/stack.yaml` ≠ `stack/projects.yaml` 的 `groups[].name`
- `site-header-drift` — `sites/*.yaml.header` ≠ 各站 `site-header.html`
- `site-content-drift` — `templates/site-content.css` ≠ 各站 `site-content.css`

**服务契约（2026-04-22 新增）**：

- `services-consistency` — `web-stack/services/*/` pyproject.toml 有 version、api.py 有 `/api/metadata` 路由（static audit，不 probe live 端口）
- `static-sites-filter-drift` — cmds/stack generate.py 引用共享 `devtools/lib/templates/site-filter.js` + `markdown_utils.parse_frontmatter`（logs 保留独立 radio-filter 不抽）

**路径域（2026-04-24 新增）**：

- `paths-drift` — 内部 subprocess 调 `paths.py audit --strict`（路径注册表 SSOT 4 项：路径存在性 / 硬编码候选 / 派生产物新鲜度 / env_vars 存在性）。默认 soft（只警告，不 gate），`--strict` 才 gate 整体 exit code

## 退出码

- `0` — 14/14 绿（或 13 绿 + paths-drift 警告 且无 `--strict`）
- `1` — 13 类任一漂移 / `--strict` 模式下 paths-drift 也失败（可用作 CI gate）

## 相关命令

- `python3 menus.py validate` — 校验 yaml 结构
- `python3 menus.py build-services-ts -w` — entities/* → services.ts
- `python3 menus.py build-react-mega-navbar -w` — devtools canonical → 两站 copy
- `python3 menus.py render-navbar -w` — navbar.yaml → site-navbar.html
- `python3 menus.py build-website-navbar -w` — navbar.yaml → shared-navbar.generated.ts
- `python3 menus.py build-catalog -w` — 重建 catalog.yaml
- `/navbar-refresh` — site-navbar.html → 6 个 vendor
- `/site-refresh-all` — 11 步全同步骨架

## 路径域（已融入第 14 类）

2026-04-24 起，`~/Dev/paths.yaml` 域（路径 SSOT、死链、migrations、env_vars）作为第 14 类 `paths-drift` 纳入本 audit —— 内部 subprocess 调 `paths.py audit --strict`。

- 默认模式：paths-drift 失败只打印警告（`⚠`），**不影响** exit code
- `--strict` 模式：paths-drift 失败也 exit 1，可用作 CI gate

单独跑路径检查（不跑 13 类菜单）：

```bash
python3 ~/Dev/devtools/lib/tools/paths.py audit --strict
```

## 规则

- 只读，无副作用
- 自 2026-04-22 重构后 13 类全绿基线；2026-04-24 起加入第 14 类 paths-drift。任一红项对应一个具体修复命令，按 MD 内提示跑
- Pre-commit hook 装在 7 个 repo（audit 失败阻断 commit，逃生门 `--no-verify`）
