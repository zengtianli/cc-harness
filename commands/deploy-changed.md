---
name: deploy-changed
description: Scan recent git diffs across web-stack + hydro-* + audiobook + devtools/lib, figure out which sites were affected, and batch-deploy only those.
---

薄皮 skill — 调 `~/Dev/devtools/scripts/deploy-changed.sh`。一键「我刚改的几站上线」，不用手工列站名。

## 用法

```bash
/deploy-changed                     # 默认 HEAD~1..HEAD
/deploy-changed --since origin/main # 相对 remote main
/deploy-changed --fast              # 过 pass-through 给 deploy-batch.sh
/deploy-changed --dry               # 只打印会部署哪些站，不实际跑
```

## 执行

```bash
bash ~/Dev/devtools/scripts/deploy-changed.sh $ARGUMENTS
```

## 脚本行为

扫三个来源的 `git diff --name-only <since> HEAD`：

- `~/Dev/devtools/lib/` — 共享 Python 模块，变了 → **所有** 已迁站点
- `~/Dev/stations/web-stack/` — `apps/<name>-web/*` 变了 → 对应站；`packages/*` 变了 → 所有站
- `~/Dev/hydro-*`、`~/Dev/stations/audiobook` — 该 repo 任意变动 → 对应站

去重后合并调 `~/Dev/stations/web-stack/infra/deploy/deploy-batch.sh <sites...>`。

若零变更 → 打印「nothing changed」退 0（不算错）。

## 什么时候跑

- 改完一两站准备上线，记不清到底动了哪些 repo
- CI / hook 里自动选站部署
- 迭代中连续改数次，只想 push 最后一版的合集

## 不做

- 不自动 commit / push（你自己先 commit，脚本读本地 diff）
- 不跨 branch 对比（默认 HEAD~1；跨分支用 `--since origin/main`）
- 不部署 Streamlit legacy 站（只看 web-stack/apps/*-web 存在的站）

## 相关

- `~/Dev/stations/web-stack/infra/deploy/deploy.sh` — 单站底层
- `~/Dev/stations/web-stack/infra/deploy/deploy-batch.sh` — 多站并行
- `~/Dev/stations/web-stack/infra/deploy/sync-global.sh` — 共享 devtools/lib 同步
- `/api-smoke` — 部署前本地 smoke test
