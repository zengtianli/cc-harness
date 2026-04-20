---
description: 检测站群菜单/导航 yaml SSOT (~/Dev/tools/configs/menus/) 与各消费者源码的漂移
---

跨 5 个菜单/导航源做只读对账，配套 `~/Dev/tools/configs/menus/` 物理目录使用。

## 用法

```bash
/menus-audit
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/menus.py audit
```

## 报告分类

- `navbar-drift` — `navbar.yaml` 渲染结果 ≠ `devtools/lib/templates/site-navbar.html`
- `website-nav-drift` — `sites/website.yaml` ≠ `website/lib/profile-config.ts` 的 `navigationConfig`
- `ops-console-drift` — `sites/ops-console.yaml` ≠ `ops-console/components/section-nav.tsx` 的 `ITEMS`
- `cmds-drift` — `sites/cmds.yaml` ≠ `cmds/generate.py` 的 `CATEGORY_MAP/ORDER/COLOR`
- `stack-drift` — `sites/stack.yaml` 的分组列表 ≠ `stack/projects.yaml` 的 `groups[].name`

## 退出码

- `0` — 零漂移
- `1` — 有任一漂移（可用作 CI gate）

## 相关命令

- `python3 ~/Dev/devtools/lib/tools/menus.py validate` — 校验 yaml 结构
- `python3 ~/Dev/devtools/lib/tools/menus.py render-navbar -w` — 从 yaml 重渲染 site-navbar.html
- `python3 ~/Dev/devtools/lib/tools/menus.py build-catalog -w` — 重建 catalog.yaml
- `/navbar-refresh` — 把 site-navbar.html 同步到 4 个消费者 repo

## 规则

- 只读，无副作用
- 阶段 1 完工时所有项应全绿（yaml 是从原始位置原样翻译来的）
- 阶段 2 改造各站消费者后仍应全绿（消费者改成读 yaml）
