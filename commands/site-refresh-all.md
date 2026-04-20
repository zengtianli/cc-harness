---
description: 站群 SSOT 改完一键同步所有产物 + 消费者 + audit。不含 deploy（破坏性操作由用户明确指定）。
---

用户提供了参数: $ARGUMENTS

## 定位

**站群任务编排 skill**。改完任何 SSOT（navbar.yaml / sites/*.yaml / menus.py / templates/）后跑这条，让所有产物、消费者本地副本、TS 数据、audit 状态一次性到位。

配套 playbook：`~/Dev/tools/configs/playbooks/stations.md` § 编排图

**刻意不含 `/deploy`**：部署会把改动推上线（破坏性），必须由用户明确指定要部署哪几个站。本 skill 只负责"本地全对齐 + audit 绿"。

## 执行

按顺序跑（任一步失败立即停，报错出来）：

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

# 6. navbar.html 同步到 5 消费者（auto commit + push）
bash ~/Dev/devtools/scripts/tools/navbar_refresh.sh

# 7. React 共享组件 + TS 数据 copy → ops-console
cp ~/Dev/stations/website/components/mega-navbar.tsx     ~/Dev/stations/ops-console/components/mega-navbar.tsx
cp ~/Dev/stations/website/lib/shared-navbar.generated.ts ~/Dev/stations/ops-console/lib/shared-navbar.generated.ts

# 8. 静态站重生成 HTML（stack / cmds / logs）
cd ~/Dev/stations/stack  && python3 generate.py
cd ~/Dev/stations/cmds   && python3 generate.py
cd ~/Dev/stations/logs   && python3 generate.py

# 9. audit 8 类全绿
python3 ~/Dev/devtools/lib/tools/menus.py audit
```

## 完成后的提示

audit 全绿后，**必须**告诉用户：

> ✅ 本地全对齐，audit 8/8 绿。下一步你来指挥：
>
> 要部署哪些站？参考受影响范围：
> - 改了 `NAVBAR_CSS` / `site-navbar.html` → 全 6 站（website + ops-console + stack + cmds + logs + audiobook）
> - 改了 `mega-navbar.tsx` → 只 website + ops-console
> - 改了 `site-content.css` → stack + cmds + logs + ops-console
> - 改了 `sites/<name>.yaml.header` → 只对应一站
>
> 告诉我哪些，我 `/deploy <name>` 跑。

**不自动调 /deploy**。等用户明确。

## 反模式

- ❌ 自动在流程末尾加 `for d in ...; do deploy.sh; done` → 部署是破坏性，必须用户批准
- ❌ 跳过 audit 就宣布 "已同步" → 可能产物不一致
- ❌ 某步失败还继续 → 必须立即停并报错

## 和 /frontend-tweak 的关系

`/frontend-tweak` 的 Step 6 会调用这条 skill：

```
/frontend-tweak
  ├─ 定位 + Edit
  ├─ /menus-audit（改前基线）
  ├─ /site-refresh-all   ← 这里
  └─ 问用户部署清单
```

独立使用 `/site-refresh-all` 的场景：SSOT 手工改完（Plan mode 路径 B），需要批量同步。

## 相关

- playbook: `~/Dev/tools/configs/playbooks/stations.md`
- 姊妹 skill: `/frontend-tweak`（视觉微调） · `/menus-audit`（单独跑 audit） · `/deploy`（单站部署）
