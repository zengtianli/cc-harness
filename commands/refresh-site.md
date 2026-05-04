---
description: 站群 SSOT 改完一键同步所有产物 + 消费者 + audit。接 --kind 参数选范围（all / navbar / header / content）。不含 deploy。
---

用户提供了参数: $ARGUMENTS

## 定位

**站群任务编排 skill**。改完任何 SSOT 后跑这条，让所有产物、消费者本地副本、TS 数据、audit 状态一次性到位。

配套 playbook：`~/Dev/tools/configs/playbooks/stations.md` § 编排图

**刻意不含 `/deploy`**：部署是破坏性，必须由用户明确指定要部署哪几个站。本 skill 只负责"本地全对齐 + audit 绿"。

## 用法

```bash
/refresh-site                  # 默认全套（等价旧 /site-refresh-all）
/refresh-site --kind all       # 同上，11 步全跑
/refresh-site --kind navbar    # 只跑 navbar.html → 6 consumers（等价旧 /navbar-refresh）
/refresh-site --kind header    # 只跑 site-header.html → 5 stations（等价旧 /site-header-refresh）
/refresh-site --kind content   # 只跑 site-content.css → 4 stations（等价旧 /site-content-refresh）
```

> 旧 alias 已废：`/site-refresh-all` `/navbar-refresh` `/site-header-refresh` `/site-content-refresh` —— 全合并到本命令。

---

## --kind all（默认）

11 步全跑，任一步失败立即停：

```bash
# 1. navbar SSOT → devtools/lib/templates/site-navbar.html
python3 ~/Dev/devtools/lib/tools/menus.py render-navbar -w

# 2. navbar SSOT → website/lib/shared-navbar.generated.ts
python3 ~/Dev/devtools/lib/tools/menus.py build-website-navbar -w

# 3. catalog 重建（交叉索引）
python3 ~/Dev/devtools/lib/tools/menus.py build-catalog -w

# 4. site-header 渲染到所有 site
python3 ~/Dev/devtools/lib/tools/menus.py render-site-header --all -w

# 5. site-content.css 同步到消费者
python3 ~/Dev/devtools/lib/tools/menus.py build-site-content -w

# 6. navbar.html 同步到 6 消费者（auto commit + push）
bash ~/Dev/devtools/scripts/tools/navbar_refresh.sh

# 7. React mega-navbar → website + ops-console
python3 ~/Dev/devtools/lib/tools/menus.py build-react-mega-navbar -w

# 8. shared-navbar.generated.ts → ops-console copy
cp ~/Dev/stations/website/lib/shared-navbar.generated.ts \
   ~/Dev/stations/ops-console/lib/shared-navbar.generated.ts

# 9. services.ts AUTO-GEN
python3 ~/Dev/devtools/lib/tools/menus.py build-services-ts -w

# 10. 静态站重生成 HTML（stack/cmds/logs/assets）
cd ~/Dev/stations/stack  && python3 generate.py
cd ~/Dev/stations/cmds   && python3 generate.py
cd ~/Dev/stations/logs   && python3 generate.py
cd ~/Dev/stations/assets && python3 generate.py

# 11. audit 17 类全绿
python3 ~/Dev/devtools/lib/tools/menus.py audit
```

---

## --kind navbar（替代旧 /navbar-refresh）

```bash
bash ~/Dev/devtools/scripts/tools/navbar_refresh.sh "$@"
```

支持 `--dry-run`。

**消费者清单**（auto-discovery，不硬编码）：扫 `~/Dev/stations/*/site-navbar.html`（maxdepth 3，排除 _archive / devtools / configs / .next / node_modules）。

**当前 6 站**：stack / cmds / audiobook / assets / logs / ops-console（域名映射见 `services.ts`）

**不处理**：Streamlit 三站（运行时从 VPS 上的 devtools 读模板，不 vendor 本地副本）

---

## --kind header（替代旧 /site-header-refresh）

```bash
python3 ~/Dev/devtools/lib/tools/menus.py render-site-header --all -w
```

**5 站**：cmds / stack / journal / cc-evolution / ops-console（journal & cc-evolution 已归档）

把 `~/Dev/tools/configs/menus/sites/<name>.yaml` 的 `header` 字段渲染成 site-header.html，写入各 repo。

**渲染产物**：
1. `<style>` `.tlz-site-header` 完整 CSS
2. `<header>` 含面包屑 + icon + title + tagline

各站 generate.py 用 `_load_site_header()` 注入。

**漂移检测**：`menus-audit` 的 `site-header-drift` 类。

---

## --kind content（替代旧 /site-content-refresh）

```bash
python3 ~/Dev/devtools/lib/tools/menus.py build-site-content -w
```

**4 站**：cmds / stack / logs / ops-console

把 `~/Dev/devtools/lib/templates/site-content.css` 同步到各子站，让卡片/grid/配色与 services 页一致。

**关键 class**：`.tlz-page` / `.tlz-container` / `.tlz-section` / `.tlz-grid` / `.tlz-card` / `.tlz-search` / `.tlz-stats-bar` / `.tlz-dot--{ok,bad,unknown}`

**漂移检测**：`menus-audit` 的 `site-content-drift` 类。

---

## 完成后的提示（all 模式）

audit 全绿后**必须**告诉用户：

> ✅ 本地全对齐，audit 14/14 绿。下一步你来指挥：
>
> 要部署哪些站？参考受影响范围：
> - 改了 `NAVBAR_CSS` / `site-navbar.html` → 全 6 站（website + ops-console + stack + cmds + logs + audiobook）
> - 改了 `mega-navbar.tsx` → 只 website + ops-console
> - 改了 `site-content.css` → stack + cmds + logs + ops-console
> - 改了 `sites/<name>.yaml.header` → 只对应一站
>
> 告诉我哪些，我 `/deploy <name>` 跑（或 `/deploy fanout` 多站并行 / `/deploy changed` 按 git diff 自动选）。

**不自动调 /deploy**。等用户明确。

---

## 反模式

- ❌ 自动在流程末尾加 `for d in ...; do deploy.sh; done` → 部署是破坏性，必须用户批准
- ❌ 跳过 audit 就宣布 "已同步"
- ❌ 某步失败还继续 → 必须立即停并报错

## 和 /frontend-tweak 的关系

`/frontend-tweak` Step 6 调用本 skill：

```
/frontend-tweak
  ├─ 定位 + Edit
  ├─ /menus-audit（改前基线）
  ├─ /refresh-site --kind all   ← 这里
  └─ 问用户部署清单
```

独立用 `/refresh-site` 的场景：SSOT 手工改完（Plan mode 路径 B），需要批量同步。

## 相关

- playbook: `~/Dev/tools/configs/playbooks/stations.md`
- 姊妹 skill: `/frontend-tweak`（视觉微调） · `/menus-audit`（单独跑 audit） · `/deploy`（单站部署）
