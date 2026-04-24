---
description: 进项目先跑一句 — 告诉你当前加载的 skills、CLAUDE.md、HANDOFF、git 状态和建议动作
---

进 `~/Dev/*` 或 `~/Dev/Work/*` 任何项目目录下，跑这个命令得到一份"情报简报"：我现在知道些什么、你上次停在哪、下一步有什么路子。

纯只读，没有副作用。

## 用法

```bash
/warmup
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/warmup.py
```

## 输出段

1. **项目** — CWD、git branch、脏/干净、未推 commit、最近一次 commit
2. **CC 配置** — 是否有 `.claude/`、CLAUDE.md（+ H1）、`harness.yaml` 的全局 + 本项目 skills、合计加载数
3. **交接状态** — 本项目 HANDOFF.md（若无则看全局 `~/Dev/HANDOFF.md`）年龄 + H1 + 抽取的"下一轮/待办/遗留"条目
4. **建议动作** — 基于上面情况的 next-step hints（无 CLAUDE.md→/init；无 `.claude/`→/harness；HANDOFF 停太久→先 cat；engineering-mode 已载→破坏性操作走 plan mode）

## 什么时候跑

- 进入一个新/陌生项目目录的第一个命令
- 久未动的项目重新开工前
- 不确定当前 CC 配置加载了啥时
- 想知道 harness.yaml 把哪些 skills 分给这个项目时

## 不做

- 不修改任何文件/配置
- 不自动跑 `/harness` / `/handoff`；只提示是否该跑
- 不展示 HANDOFF 全文（太长）；只给年龄、标题、摘要
