---
description: 把共享 navbar 模板同步到 4 个消费者 repo，有变更就 commit+push
---

在 `~/Dev/devtools/lib/templates/site-navbar.html` 改完后跑这个命令：对 **stack / cmds / cc-evolution / audiobook** 各自的 `site-navbar.html` 做 cp → git diff → commit + push。GHA 各自接力重新部署。

## 用法

```bash
/navbar-refresh [--dry-run]
```

## 执行

```bash
bash ~/Dev/devtools/scripts/tools/navbar_refresh.sh "$@"
```

## 覆盖范围

- `~/Dev/stack/site-navbar.html`  — GHA 部署到 `stack.tianlizeng.cloud`
- `~/Dev/cmds/site-navbar.html`   — GHA 部署到 `cmds.tianlizeng.cloud`
- `~/Dev/cc-evolution/site-navbar.html` — GHA 部署到 `changelog.tianlizeng.cloud`
- `~/Dev/audiobook/site-navbar.html`    — `deploy.sh` 部署到 `audiobook.tianlizeng.cloud`

## 不处理

**Streamlit 三站**（repo-dashboard / hs-dashboard / auggie-dashboard）**不在列**——它们运行时从 VPS 上的 `~/Dev/devtools/lib/templates/site-navbar.html` 读取（devtools 已部署到 VPS），不 vendor 本地副本。

如果要让 Streamlit 三站拿到新模板，需要把 devtools 同步到 VPS（当前假设 devtools 与各 Streamlit repo 共存于 VPS）。

## 规则

- 只对 `site-navbar.html` 做 diff，不碰其他文件
- 无变更 repo 直接跳过，不产生空 commit
- `--dry-run` 只显示变更预览，不写 git
