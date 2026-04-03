Promote GitHub repositories — audit README, update metadata (description/topics/homepage), ensure screenshots exist.

## Scope

Determine target projects from $ARGUMENTS:
- No args → current working directory
- `<name> [name2 ...]` → specific project(s) by directory name under ~/Dev
- `all` → all git repos under ~/Dev (no exclusions — user controls visibility via public/private)
- `--check` flag → dry run, only report status without making changes

## Per-project flow

### 1. README audit

Run: `python3 ~/Dev/devtools/repo_manager.py audit <name>`

If issues found, list them. Don't auto-fix README — just report. README changes should be done in a separate step.

### 2. GitHub metadata

Fetch current state:
```bash
gh repo view zengtianli/<name> --json description,repositoryTopics,homepageUrl
```

**Description** — if empty, extract from README.md line after the language selector (the one-line description), then:
```bash
gh repo edit zengtianli/<name> --description "<extracted description>"
```

**Topics** — if empty or fewer than 3, recommend and add topics using these rules:

| Pattern | Recommended topics |
|---------|-------------------|
| `hydro-apps` | `tauri`, `desktop-app`, `hydrology`, `water-resources`, `rust`, `typescript`, `monorepo` |
| `hydro-*` | `hydrology`, `water-resources`, `python`, `streamlit` (if has demo URL) |
| `cc-*` | `claude-code`, `cli`, `developer-tools`, `python` |
| `dockit*` | `document-processing`, `python`, `streamlit` |
| `edict` | `ai-agents`, `multi-agent`, `python`, `openclaw` |
| `cclog` | `claude-code`, `cli`, `developer-tools`, `python`, `session-management` |
| `downloads-*` | `file-management`, `automation`, `python`, `cli` |
| `vps-*` | `vps`, `nginx`, `cloudflare`, `proxy` |

Additionally scan README for keywords to suggest extra topics. Always confirm with user before adding topics (list the suggestions).

```bash
gh repo edit zengtianli/<name> --add-topic topic1 --add-topic topic2
```

**Homepage URL** — if empty and project has a live demo:
- Streamlit apps: `https://<name>.tianlizeng.cloud`
- Check if URL actually resolves before setting

```bash
gh repo edit zengtianli/<name> --homepage "https://<name>.tianlizeng.cloud"
```

### 3. Screenshot check

Check if `~/Dev/<name>/docs/screenshots/demo.png` exists.

If missing, use `repo_manager.py screenshot` with the appropriate mode:
- **Streamlit** app with demo URL → `python3 ~/Dev/devtools/repo_manager.py screenshot streamlit <name> <url>`
- **CLI** tool → `python3 ~/Dev/devtools/repo_manager.py screenshot cli <name> "<command>"`
- **Tauri desktop** app (hydro-apps monorepo) → `python3 ~/Dev/devtools/repo_manager.py screenshot tauri hydro-apps`
  - Opens each app via `open -a`, gets window bounds via `osascript`, captures via `screencapture -R`
  - Auto-installs from DMG if not in /Applications
  - Produces per-app screenshots + demo.png
- If repo_screenshot.py doesn't support the project, flag it for manual screenshot

### 4. Summary report

Output a table at the end:
```
✅ dockit          — all good
🔧 cc-harness     — added 5 topics, set homepage
🔧 cc-context     — added 4 topics  
⚠️  oauth-proxy    — skipped (internal)
```

## Rules

- Never overwrite existing README content — only audit and report
- Always confirm before adding topics (show the list first)
- Never force-push or rewrite git history
- No project exclusions — user controls visibility via GitHub public/private settings
- Use `gh` CLI for all GitHub API operations
- After making changes, commit + push affected files using `/ship`
