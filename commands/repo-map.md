Manage the GitHub ↔ local path bidirectional mapping.

## Registry

Single source of truth: `~/Dev/tools/configs/repo-map.json`

Fields per repo:
- `local` — local path (~/Dev/xxx or ~/Dev/Work/xxx)
- `github` — GitHub owner/repo
- `vps` — VPS deploy path (null if not deployed)
- `category` — hydro/tools/infra/knowledge/personal/work
- `auto_push` — whether `git_smart_push.py` includes it in scheduled pushes

## Consumers (files that embed parts of this mapping)

1. `~/Dev/devtools/scripts/tools/git_smart_push.py` — reads `repo-map.json` at runtime, filters by `auto_push: true`
2. `~/Dev/tools/vps/github_webhook_receiver.py` — `REPO_PATHS` dict (repos with non-null `vps`). Updated by `sync`.
3. `~/Dev/CLAUDE.md` — repo map table section. Updated by `sync`.
4. `~/.claude/commands/ship.md` — `/ship all` reads `repo-map.json` to resolve paths.

## Behavior

Based on $ARGUMENTS:

### `scan` (default if no args)
1. Scan `~/Dev/*/`, `~/Dev/Work/*/`, `~/Documents/sync` for `.git` folders
2. For each, read `git remote get-url origin` to get the GitHub repo
3. Compare against `repo-map.json`:
   - ✓ Matched
   - ⚠️ New (on disk, not in registry) — prompt to add with category/vps/auto_push
   - ✗ Missing (in registry, not on disk) — warn
4. Update `repo-map.json` with changes

### `sync`
1. Read `repo-map.json`
2. Regenerate the embedded mappings in consumers #2 and #3:
   - `webhook_receiver.py` REPO_PATHS — only repos with non-null `vps`
   - `CLAUDE.md` repo map section — all repos grouped by category
3. Show diff, apply, report

### `show`
Display formatted table grouped by category:
```
hydro (12)  ★=auto_push
  hydro-rainfall    ~/Dev/stations/web-stack/services/hydro-rainfall    zengtianli/hydro-rainfall    /opt/hydro/hydro-rainfall
  ...
work (2)
★ zdwp              ~/Dev/Work/zdwp             zengtianli/zdwp              /var/www/zdwp
★ reports           ~/Dev/Work/reports          zengtianli/reports           /var/www/reports
```

### `check`
Verify consistency:
- `repo-map.json` vs actual `git remote` in each local dir
- `repo-map.json` vs `webhook_receiver.py` REPO_PATHS
- `repo-map.json` vs `CLAUDE.md` repo map section
Report mismatches with file:line references.

### `add <name>`
1. Check if directory exists and has a git remote
2. Prompt for: category, vps path, auto_push
3. Add to `repo-map.json`
4. Suggest `sync` to propagate

### `regen`（替代旧 /repo-map-refresh）

完全重新扫 `~/Dev/{stations,tools,labs,content,migrated}/*` 和根下工具基建，**消除手工维护漂移**，写入 `~/Dev/tools/configs/repo-map.json`。

```bash
/repo-map regen           # 写入
/repo-map regen --dry-run # 预览（stdout）
```

实际执行：
```bash
python3 ~/Dev/devtools/lib/tools/repo_map_gen.py            # 写入
python3 ~/Dev/devtools/lib/tools/repo_map_gen.py --stdout   # 预览
```

**和 `scan` 的区别**：
- `scan` 是增量对账（找新增 / 缺失），交互式确认每条改动
- `regen` 是全量重建（直接覆盖 JSON），用于"手工漂移已严重，统一对齐"场景。2026-04-22 调查发现 22 条陈旧 + 8 条缺失 → `regen` 一次清干净

**何时用 `regen`**：
- 大规模目录重构后（如 station-promote 批量迁移）
- 怀疑手工编辑造成漂移
- 跑 `check` 报告大量不一致

**规则**：
- 只登记含 `.git` 的本地 repo
- 路径格式统一 `~/Dev/...`
- remote URL 从 `git config --get remote.origin.url` 读，无远程则 null
- 分层目录：stations / tools / labs / content / migrated
- 根下：devtools / doctools / mactools / clashx / dotfiles / ...（ROOT_REPOS 白名单）

## Rules

- `repo-map.json` is ALWAYS the source of truth
- The `web` repo: GitHub name `web`, local dir `website`
- `git_smart_push.py` reads JSON at runtime — no need to sync it, it's already dynamic
- `webhook_receiver.py` is static (runs on VPS) — must be synced and pushed
- Never remove entries without asking
