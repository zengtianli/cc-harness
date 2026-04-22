---
description: 站群前端微调守门 — 只允许改视觉参数（颜色/间距/字号/断点/动画等），禁止动 yaml 数据结构。改完强制 /menus-audit 13/13 全绿证明未破坏结构。
---

用户提供了参数: $ARGUMENTS

## 定位

**站群任务 · 路径 A（90% 场景）入口**。用户说"改下颜色 / 字号 / 间距 / hover / 断点 / 列数 / 布局微调"等非破坏性视觉调整时走这个。

配套 playbook：`~/Dev/tools/configs/playbooks/stations.md` § 改动边界矩阵

## 硬约束

### ❌ 禁止编辑

- `~/Dev/tools/configs/menus/navbar.yaml`
- `~/Dev/tools/configs/menus/sites/*.yaml`
- `~/Dev/tools/configs/menus/schema/*.json`
- `~/Dev/stations/website/lib/services.ts`（子域清单）
- `~/Dev/tools/configs/menus/catalog.yaml`（自动生成，不手改）
- `~/Dev/stations/website/lib/shared-navbar.generated.ts`（自动生成）

**理由**：这些是 SSOT 数据结构。改它们 = 影响消费者契约 = 破坏性。需走 Plan mode + AskUserQuestion。

### ✅ 允许编辑

- `~/Dev/devtools/lib/tools/menus.py` 里的 `NAVBAR_CSS` 字符串（CSS 值）
- `~/Dev/devtools/lib/templates/site-content.css`（站内 `.tlz-*` 统一样式）
- `~/Dev/stations/website/components/mega-navbar.tsx`（React 视觉 props / Tailwind 类 / 内联样式参数）
- `~/Dev/stations/ops-console/components/mega-navbar.tsx`（同 website copy）
- `~/Dev/stations/website/app/globals.css`（全局 CSS）
- `~/Dev/stations/ops-console/app/globals.css`（同上）
- `~/Dev/stations/website/components/navbar.tsx`（外层包装，Track 色线参数）

**判断标准**：改动是否**只影响视觉渲染**，不改任何消费者读取的**数据字段**、**结构类型**、**导出名**。

## 流程

### Step 1 — 按 stations playbook § 改动边界矩阵自查

读 `~/Dev/tools/configs/playbooks/stations.md` 的矩阵节。如果要改的东西在"破坏性"列 → **立即停止，建议用户走 Plan mode**，不要继续。

### Step 2 — 用户需求复述

按 META.md §4 "对齐" 原则，先用一句话复述用户意图，问"这样对吗？" 再动手。例：

> 用户：改下 mega hover 色
> CC：我理解是把 mega menu 链接 hover 时的文字颜色从 `#D40000` 换成你指定的新色，其他不动。对吗？要换成什么色？

### Step 3 — 定位

用 `Grep` 找要改的 CSS 变量 / Tailwind 类 / 颜色值的所有出现点：

```bash
# 例：找 hover 色
grep -rn "#D40000\|text-\[#D40000\]\|--tlz-accent" \
  ~/Dev/devtools/lib/tools/menus.py \
  ~/Dev/devtools/lib/templates/site-content.css \
  ~/Dev/stations/website/components/ \
  ~/Dev/stations/ops-console/components/
```

**原则**：找到所有出现点**一次改齐**，不漏一处。SSOT 统一的要改 SSOT 一处；未 SSOT 的要多处同步改。

### Step 4 — Edit 最小差集

只改颜色值 / 数字参数，不动结构。**不**顺手"重构"或"顺便改"其他地方。

### Step 5 — 强制 /menus-audit 验证

```bash
python3 ~/Dev/devtools/lib/tools/menus.py audit
```

**必须 8/8 全绿**。任一 drift 红说明你动了数据结构 → **回滚**。

### Step 6 — /site-refresh-all 同步

```
/site-refresh-all
```

（或手动：render-navbar -w + build-website-navbar -w + navbar_refresh.sh + cp mega-navbar.tsx & generated.ts → ops-console + menus-audit）

### Step 7 — 用户手工指定部署哪些站

**不自动 deploy 全部**。问用户：

> 视觉已改完，audit 全绿。要部署哪些站？（默认：website + ops-console；如果改的是 site-navbar/header/content 共享模板，还要 stack/cmds/logs/audiobook）

按用户明确列表跑 `/deploy <name>` × N。

### Step 8 — /ship 收尾

```
/ship configs devtools website ops-console
```

按实际改了哪些 repo 缩减清单。

## 触发词（匹配用户意图）

- "改颜色 / 配色 / 主题色"
- "调字号 / 字重 / 字体"
- "改间距 / padding / margin / gap"
- "hover 效果 / transition / 动画时长"
- "响应式断点 / 移动端 / 桌面"
- "列数调一下 / 布局微调 / 重排"
- "阴影 / 圆角 / 边框"
- "cards / buttons / badges 的样式"

## 拒绝词（这些不走本 skill）

- "加菜单项 / 加分类" → Plan mode
- "删子域 / 退役站" → Plan mode + `/site-archive`
- "换 URL / 改分组逻辑" → Plan mode
- "加新站 / 搭新页" → Plan mode + `/site-add` + `/ship-site`
- "改 yaml / 结构" → Plan mode

遇到拒绝词直接说：

> 这是**数据结构改动**（破坏性），不在 `/frontend-tweak` 范围。需要走 Plan mode + AskUserQuestion 拍板。参考 `~/Dev/tools/configs/playbooks/stations.md` § 改动边界矩阵 路径 B。

## 反模式

- ❌ 跳过 Step 2 复述 → 容易跑偏
- ❌ 跳过 Step 5 audit → 不知道有没有破坏结构
- ❌ 未经允许自动 /deploy 全 6 站 → 用户要控制哪些站受影响
- ❌ 顺手修"看起来不对"的其他 CSS → 越界，改什么就改什么

## 相关

- playbook: `~/Dev/tools/configs/playbooks/stations.md`
- 姊妹 skill: `/site-refresh-all`（同步） · `/menus-audit`（验证） · `/deploy`（部署）
