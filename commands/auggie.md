---
description: Auggie 索引管理（dash=扫描部署 dashboard, fix=补全缺失 _files.md）
---

用户提供了参数: $ARGUMENTS

## 子命令路由

解析 `$ARGUMENTS` 第一个词：
- `dash` — 扫描索引状态并部署 dashboard
- `fix` — 补全缺失 _files.md 并 commit+push
- 为空 → 默认 `dash`

---

## dash — 扫描并部署 Dashboard

1. 运行 scanner 生成 scan.json：
   ```bash
   python3 ~/Dev/auggie-dashboard/lib/scanner.py ~/Dev/auggie-dashboard/data/scan.json
   ```
2. 部署到 VPS：
   ```bash
   bash ~/Dev/auggie-dashboard/deploy.sh
   ```
3. 输出摘要：总 repo 数、cloud complete、needs attention、missing _files.md

---

## fix — 补全缺失 _files.md

扫描 ~/Dev 和 ~/Work 所有 git+GitHub repo，为缺少 _files.md 的补上清单。

支持 `--dry-run` 只列出不写入。

1. 运行：
   ```bash
   python3 ~/Dev/auggie-dashboard/lib/fix_files_md.py [--dry-run]
   ```
2. 对每个新增的 _files.md 执行 `git add _files.md && git commit && git push`
3. 完成后运行 `dash` 子命令刷新 dashboard
