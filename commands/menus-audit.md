---
description: 检测站群菜单/导航 yaml SSOT (~/Dev/tools/configs/menus/) 与各消费者源码的漂移（11 类）
---

跨 11 个源做只读对账，配套 `~/Dev/tools/configs/menus/` 图模型（entities/ + relations/ + consumers.yaml + sites/*.yaml + navbar.yaml）。

## 用法

```bash
/menus-audit
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/menus.py audit
```

## 报告分类（11 类）

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

## 退出码

- `0` — 11/11 绿
- `1` — 任一漂移（可用作 CI gate）

## 相关命令

- `python3 menus.py validate` — 校验 yaml 结构
- `python3 menus.py build-services-ts -w` — entities/* → services.ts
- `python3 menus.py build-react-mega-navbar -w` — devtools canonical → 两站 copy
- `python3 menus.py render-navbar -w` — navbar.yaml → site-navbar.html
- `python3 menus.py build-website-navbar -w` — navbar.yaml → shared-navbar.generated.ts
- `python3 menus.py build-catalog -w` — 重建 catalog.yaml
- `/navbar-refresh` — site-navbar.html → 6 个 vendor
- `/site-refresh-all` — 11 步全同步骨架

## 规则

- 只读，无副作用
- 自 2026-04-22 重构后全绿基线；任一红项对应一个具体修复命令，按 MD 内提示跑
- Pre-commit hook 装在 7 个 repo（audit 失败阻断 commit，逃生门 `--no-verify`）
