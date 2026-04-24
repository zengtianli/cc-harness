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

## Rules

- `repo-map.json` is ALWAYS the source of truth
- The `web` repo: GitHub name `web`, local dir `website`
- `git_smart_push.py` reads JSON at runtime — no need to sync it, it's already dynamic
- `webhook_receiver.py` is static (runs on VPS) — must be synced and pushed
- Never remove entries without asking
