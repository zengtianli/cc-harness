---
description: 扫本地 ~/Dev 重新生成 repo-map.json（消除手工维护漂移）
---

扫 `~/Dev/{stations,tools,labs,content,migrated}/*` 和根下工具基建，产出准确的 `~/Dev/tools/configs/repo-map.json`。

## 用法

```bash
/repo-map-refresh           # 写入
/repo-map-refresh --dry-run # 预览（stdout）
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/repo_map_gen.py
```

`--dry-run` 模式：

```bash
python3 ~/Dev/devtools/lib/tools/repo_map_gen.py --stdout
```

## 背景

repo-map.json 是 `/ship all` 等命令的 name → path lookup 源。手工维护易漂移（2026-04-22 调查发现 22 条陈旧 + 8 条缺失）。此命令通过扫描 .git 目录自动对齐。

## 规则

- 只登记含 `.git` 的本地 repo
- 路径格式统一 `~/Dev/...`
- remote URL 从 `git config --get remote.origin.url` 读取；无远程则 null
- 分层目录：stations / tools / labs / content / migrated
- 根下：devtools / doctools / mactools / clashx / dotfiles / ... (ROOT_REPOS 白名单)
