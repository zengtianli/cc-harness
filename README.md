# cc-configs

**English** | [中文](README_CN.md)

The single source of truth for all Claude Code customizations — slash commands, auto-triggered skills, agent definitions, rules, and CLI tools (audit + context monitoring), managed as code and symlinked into `~/.claude/`.

[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge)](https://python.org)

---

![cc-configs demo](docs/screenshots/demo.png)

---

## What is this?

| Layer | What | Where |
|-------|------|-------|
| **Commands** | 28 slash commands (`/ship`, `/deploy`, `/harness`, ...) | `commands/` |
| **Skills** | 14 auto-triggered context injections | `skills/` |
| **Agents** | 2 specialized agent definitions | `agents/` |
| **Rules** | Command rule files (gen-report, review-deep) | `rules/` |
| **Harness tool** | 6-dimension config quality scanner | `tools/harness/` |
| **Context tool** | Token monitor, snapshot, health check | `tools/context/` |

`install.sh` symlinks `commands/`, `skills/`, and `agents/` into `~/.claude/`, so Claude Code picks them up automatically across all projects.

## Install

```bash
git clone https://github.com/zengtianli/cc-configs.git ~/Dev/cc-configs
cd ~/Dev/cc-configs
bash install.sh
```

This creates symlinks:

```
~/.claude/commands  → ~/Dev/cc-configs/commands
~/.claude/skills    → ~/Dev/cc-configs/skills
~/.claude/agents    → ~/Dev/cc-configs/agents
```

Update by pulling the repo — symlinks keep everything in sync.

---

## Commands Reference

Commands are slash commands invoked as `/command-name [args]` in Claude Code. Each command encodes a repeatable workflow as a prompt.

### Ship & Deploy

| Command | Usage | Description |
|---------|-------|-------------|
| `/ship` | `/ship`, `/ship all`, `/ship dockit hydro-risk` | Commit + push one or more repos. Auto-generates conventional commit messages. `all` mode reads `repo-map.json` to find every dirty repo. |
| `/deploy` | `/deploy`, `/deploy --backend-only` | Deploy current project to VPS. Detects `deploy.sh`, builds frontend if needed, runs deploy, verifies with curl. |
| `/pull` | `/pull`, `/pull all`, `/pull dockit learn` | Batch `git pull --ff-only` for one or more repos. |
| `/dashboard` | `/dashboard`, `/dashboard --scan-only` | Scan Claude Code sessions with LLM analyzer, then deploy the dashboard app. `--scan-only` skips deploy. `--force` ignores cache. |
| `/scan` | `/scan` | Scan Claude Code sessions, analyze task status with LLM, generate `tasks.json`. |

### Repo Management

| Command | Usage | Description |
|---------|-------|-------------|
| `/groom` | `/groom`, `/groom hydro-risk learn`, `/groom --check` | Full repo maintenance pipeline: pull → audit → fix → review → push. Orchestrates atomic commands. |
| `/audit` | `/audit`, `/audit hydro-risk` | Audit repo integrity against `repo-standards.json` — checks files and GitHub metadata. |
| `/promote` | `/promote`, `/promote all --check` | Lightweight GitHub metadata audit: description, topics, homepage, screenshots. Subset of `/groom` focused on public visibility. |
| `/repo-map` | `/repo-map scan`, `/repo-map sync`, `/repo-map show` | Manage the GitHub ↔ local path registry (`repo-map.json`). `scan` discovers repos on disk, `sync` propagates to consumers, `show` prints the table. |
| `/auggie-map` | `/auggie-map hydro-risk` | Generate a binary file map (`_files.md`) for large projects, push to GitHub so Auggie can index files not tracked in git. |

### Infrastructure

| Command | Usage | Description |
|---------|-------|-------------|
| `/vps-status` | `/vps-status`, `/vps-status nginx` | SSH into VPS, show running services, ports, disk, memory, Docker containers. With a service name arg, also shows recent logs. |
| `/cf-dns` | `/cf-dns list`, `/cf-dns add status`, `/cf-dns delete old-sub` | Manage Cloudflare DNS records via API. `add` creates A record + Origin Rule in one step. |
| `/fix-printer` | `/fix-printer` | Diagnose and fix office Canon iR C3322L printer — network detection, VPN bypass, CUPS config, queue cleanup. |

### Document Processing

| Command | Usage | Description |
|---------|-------|-------------|
| `/md2word` | `/md2word path/to/file.md` | Full MD/DOCX → Word pipeline: template styling → text formatting (punctuation, units) → image caption centering. 4-step automated workflow. |
| `/review-docx` | `/review-docx path/to/report.docx` | Review a Word document: extract text, analyze for banned words / wrong punctuation / missing citations, write track-changes comments back into the file. |
| `/review-deep` | `/review-deep path/to/report.docx` | 4-dimension LLM deep review (completeness / structure / tone / data consistency), outputs Word comments. |
| `/gen-report` | `/gen-report county-name` | Generate a new county report chapter-by-chapter from a reference report — extract → data prep → LLM per-chapter → merge. |

### Hydro Project Tools

| Command | Usage | Description |
|---------|-------|-------------|
| `/build-hydro` | `/build-hydro capacity`, `/build-hydro all` | Build Tauri desktop installers for hydro apps. Reports artifact paths and sizes. |
| `/migrate-hydro` | `/migrate-hydro capacity` | Port a hydro Streamlit app's calculation logic to the corresponding Tauri desktop app. Reads Python → writes Rust + React. |
| `/prep-basic-info` | `/prep-basic-info county-name` | Basic info data prep: web search + download + LLM extraction → `01-06.md` files. |
| `/prep-ecoflow-calc` | `/prep-ecoflow-calc county-name` | Ecological flow calculation (Tennant + QP methods, Python replaces CurveFitting). |
| `/prep-engineering` | `/prep-engineering county-name` | Engineering survey data prep: filter → merge → MD extraction → simplify → survey table. |

### Scaffolding

| Command | Usage | Description |
|---------|-------|-------------|
| `/harness` | `/harness`, `/harness ~/Dev/new-project`, `/harness --check` | Detect project type (streamlit/cli/scripts/docs/...) and maturity stage (seed/growing/established/mature), then generate or upgrade Claude Code config: CLAUDE.md, README, .gitignore, hooks, rules. Grows with the project — re-run as the project evolves. |

### Session & Workflow

| Command | Usage | Description |
|---------|-------|-------------|
| `/recap` | `/recap` | End-of-session retrospective: review conversation, extract lessons, update memory/skills/commands/CLAUDE.md, generate `session-retro-{date}.md`. |
| `/context` | `/context monitor`, `/context health` | Monitor Claude Code session health — token usage, tool call distribution, context bloat detection, snapshot save/restore. |
| `/tidy` | `/tidy`, `/tidy ~/Work/project/docs` | Deep-clean a directory: find garbage files, version chains, misplaced files. Presents table per directory, waits for approval before executing. |
| `/health` | `/health`, `/health --llm` | File hygiene + git status check. Discovers issues, can invoke `/tidy` for cleanup. |

---

## Skills Reference

Skills are auto-triggered context injections. Claude Code loads skill knowledge automatically when it detects a matching scenario — no manual invocation needed.

### Global Skills (active in all projects)

| Skill | Trigger | Knowledge provided |
|-------|---------|-------------------|
| **context** | Working in ZDWP hydro company projects | Corporate structure, county lists, data field specs, delivery standards |
| **structure** | Organizing files, creating new projects | Directory naming rules, file classification rules, auto-organization logic |
| **plan-first** | Batch operations, destructive actions | Enforces "plan before execute" discipline — show table, wait for approval |
| **quarto** | Converting DOCX to Quarto projects | Quarto build workflow, template structure, figure handling |
| **frontend** | Building UIs | Information density, compact layout, actionable data, Streamlit conventions |

### Project-specific Skills

| Skill | Bound project | Knowledge provided |
|-------|--------------|-------------------|
| **risk-map** | ~/Work/risk-map | Flood risk map data processing, QGIS spatial workflows, Excel template filling |
| **eco-flow** | ~/Work/eco-flow | Ecological flow calculation (Tennant method), reservoir screening, guarantee plans |
| **zdys** | ~/Work/zdys | Zhedong diversion operational status, dispatch models, irrigation demand calculation |
| **water-src** | ~/Work/water-src | Drinking water source safety assessment methodology |
| **water-quality** | (standalone) | Qiandao Lake diversion classified water supply management |
| **resources** | risk-map, eco-flow, zdys, water-src | Shared resource catalog: reservoir data, GIS basemaps, admin boundaries, water resource yearbooks, industry standards |

### Tool Skills

| Skill | Trigger | Knowledge provided |
|-------|---------|-------------------|
| **harness** | Checking/syncing skill config | Skill distribution registry, cross-project sync logic |
| **repo-manage** | Managing GitHub repos | Audit/screenshot/promotion SOP |
| **restart** | Terminal restart, session recovery | Session recovery instructions |

---

## Agents Reference

Agents are specialized autonomous workers for complex multi-step tasks.

| Agent | Purpose |
|-------|---------|
| **bid-chapter-writer** | Write bid document chapters following company templates and formatting standards |
| **project-content-checker** | Audit project deliverable completeness against requirement checklists |

---

## CLI Tools

### Harness — Config Auditor

```bash
# Full audit
python3 tools/harness/harness.py /path/to/project

# JSON output
python3 tools/harness/harness.py /path/to/project --json

# Security scan only
python3 tools/harness/harness.py /path/to/project --security-only
```

| Dimension | What's checked |
|-----------|---------------|
| **D1 Context** | CLAUDE.md quality, token budget, duplicates, nested files, credentials |
| **D2 Hooks** | PostToolUse coverage, schema validity, output truncation, error surfacing |
| **D3 Agents** | Skill count, overlap, description quality, frontmatter, disable-model-invocation |
| **D4 Verification** | Done-conditions, build/test commands, CI integration |
| **D5 Session** | Compact Instructions, HANDOFF.md, context budget documentation |
| **D6 Structure** | Orphan files, reference chain, naming conventions, gitignore |

### Security Scanner

The scanner checks skills for 6 categories of risk:

1. **Prompt injection** — instruction override, role hijacking
2. **Data exfiltration** — HTTP POST with secrets, base64 encoding
3. **Destructive commands** — rm -rf /, force-push main, chmod 777
4. **Hardcoded credentials** — api_key/secret_key with long strings
5. **Obfuscation** — eval $(), base64 decode piped to shell
6. **Safety override** — bypass/disable safety/rules/hooks

The scanner distinguishes between skills that **discuss** security patterns (benign) vs. those that **use** them (flagged).

### Context — Session Monitor

```bash
# Token usage for latest session
python3 tools/context/context.py monitor

# Health check (anti-pattern detection)
python3 tools/context/context.py health

# Save context snapshot
python3 tools/context/context.py snapshot save
```

## Running Tests

```bash
python3 -m pytest tools/harness/tests/ -v
python3 -m pytest tools/context/tests/ -v
```

## License

MIT
