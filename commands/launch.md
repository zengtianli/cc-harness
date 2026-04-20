---
description: 新项目一条龙上线 — /site-add → /groom → /repo-map → /promote → /ship-site → /deploy
---

新项目从零上线的 meta 编排。把已有的 4 个积木串成一条：GitHub repo → webhook 注册 → 子域名绑定 → 部署验证。

## 用法

```bash
/launch <name> [--kind static|app] [--no-github] [--no-deploy] [--vps-path PATH]
```

- `<name>` — 项目/子域名/目录名
- `--kind static` — 纯静态站点（默认），用 `/ship-site`
- `--kind app` — 有 systemd 服务的 app，用 `/deploy`（需本地 `deploy.sh`）
- `--no-github` — 跳过 GitHub repo 创建和推广
- `--no-deploy` — 仅初始化骨架，不部署
- `--vps-path PATH` — 指定 VPS 路径（默认 `/var/www/<name>`）

## 编排顺序

每步失败立即停止。已完成的步骤幂等（再跑会跳过）。

### Phase 1: 本地骨架（如果 ~/Dev/<name>/ 不存在）
调用 `/site-add <name>`

### Phase 2: Repo 质量 + GitHub（除非 --no-github）
```
/groom <name>   # pull → audit → promote → ship
```
内部已含 `/promote` 的 README/metadata 推广和 `/ship` 的 commit+push。

### Phase 3: Webhook 注册（除非 --no-github）
```
/repo-map add <name> --vps <vps-path>
```
把 `<name> → <vps-path>` 加到 webhook receiver 的 REPO_PATHS，之后 push 自动拉取。

### Phase 4: 部署（除非 --no-deploy）
```
if --kind static:   /ship-site <name>        # rsync + Nginx + CF DNS/Origin/Access
elif --kind app:    cd ~/Dev/<name> && /deploy
```

### Phase 5: 在 stack 登记
提示用户：
> 已上线：https://<name>.tianlizeng.cloud
> 建议把条目加到 ~/Dev/stations/website/lib/services.ts（stack 页下次 generate 会自动识别 CC commands，但项目要手工加到 services.ts）

## 规则

- **不重新发明**：所有真实动作都委托给已有命令，本命令只是 meta 编排
- **幂等**：每阶段先检查是否已完成（目录存在 / repo-map 已有 / Nginx config 已在），跳过已完成步骤
- **可中断恢复**：失败后人工修复，再跑 `/launch <name>` 会从下一未完成步骤继续

## 典型流程

```bash
/launch mynewsite
# ↓ 自动串起：
# /site-add mynewsite     — 建目录 + yaml/py/sh 模板
# 用户编辑 projects.yaml
# /launch mynewsite       — 再跑一次，从 Phase 2 继续
# /groom mynewsite        — repo 质量
# /repo-map add mynewsite
# /ship-site mynewsite    — DNS + Access + 部署
# ↓ 完成
```

## 参考

- 2026-04-17 新建 stack 的流程暴露了缺口：本命令就是把当时的 15 手工步编排成 1 条
- 底层积木：`/site-add` `/groom` `/promote` `/ship` `/repo-map` `/ship-site` `/cf` `/deploy`
