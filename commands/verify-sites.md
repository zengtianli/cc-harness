---
description: 一条命令端到端体检 28 子域全部活/静态一致性/工具完整性/git 推送状态
---

运行所有子域生态的综合健康检查。给出明确 `✓/⚠/✗` 清单 + 脚本测不出的浏览器项。

## 用法

```bash
/verify-sites [--quiet] [--json]
```

- 默认打印所有项（含 pass）
- `--quiet` — 只显示 warn 和 fail
- `--json` — 机器可读，供其他命令消费（如未来 `/handoff` 里 gate）

## 执行

```bash
source ~/.personal_env
python3 ~/Dev/devtools/lib/tools/verify_sites.py "$@"
```

## 检查分组

1. **commands** — 6 个子域治理命令 + /verify-sites 自己在 cc-configs/commands 下存在
2. **services.ts** — 可解析 + 无重复 subdomain
3. **cf-audit** — CF DNS / Origin / Access / VPS nginx 四源与 services.ts 对齐；`scheduled-archives.json` 里登记的孤儿是预期，不报 FAIL
4. **sites-health** — 所有站 HTTP 健康（audiobook/panel/sub 的 405 是预期 API 行为）
5. **scheduled-archives** — 每个 301 窗口的老域在 origin nginx 还真是 301，未被意外改动
6. **git state** — devtools / cc-configs / website / stack 四个关键 repo 无未提交、无未 push
7. **🧑 browser todos** — 脚本无法探测的 Streamlit SPA navbar + 端到端 301 跳转目测项

## 退出码

- `0` — 零 FAIL（可能有 WARN，通常是预期）
- `1` — 至少一项 FAIL（需处理）

## 何时运行

- 做完 `/site-rename` / `/site-archive` 后立刻跑
- 会话结束前（`/handoff` 前）跑一次
- 每周例行 + 修完 CF/nginx 手工改动后

## 和其他命令的关系

- 底层：复用 `sites_health.py` + `cf_audit.py` + `cf_api.py` 三个模块
- 上层：可在 `/handoff` 里 gate；`/ship-site` 部署成功后可自动跑一次确认
- 浏览器部分：只有人能点的项单独列出

## 说明材料

完整的"怎么用 + 怎么看懂 + 出问题怎么办"见：
**`~/Dev/cc-configs/docs/verify-sites-guide.md`**
