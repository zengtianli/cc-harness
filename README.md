# cc-harness

**English** | [中文](README_CN.md)

A personal Claude Code harness — audit tool + slash commands + auto-triggered skills + agent definitions, all managed as code in one repo and symlinked into `~/.claude/`.

[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge)](https://python.org)

---

![cc-harness demo](docs/screenshots/demo.png)

---

## What is this?

This repo is the **single source of truth** for everything that customizes Claude Code behavior:

| Layer | What | Where |
|-------|------|-------|
| **Audit tool** | 6-dimension config quality scanner | `harness.py` + `analyzers/` |
| **Commands** | 17 slash commands (`/ship`, `/deploy`, `/groom`, ...) | `commands/` |
| **Skills** | 13 auto-triggered context injections | `skills/` |
| **Agents** | 2 specialized agent definitions | `agents/` |
| **Registry** | Skill-to-project mapping | `harness.yaml` |

`install.sh` symlinks `commands/`, `skills/`, `agents/`, and `harness.yaml` into `~/.claude/`, so Claude Code picks them up automatically across all projects.

## Install

```bash
git clone https://github.com/zengtianli/cc-harness.git ~/Dev/cc-harness
cd ~/Dev/cc-harness
bash install.sh
```

This creates symlinks:

```
~/.claude/commands  → ~/Dev/cc-harness/commands
~/.claude/skills    → ~/Dev/cc-harness/skills
~/.claude/agents    → ~/Dev/cc-harness/agents
~/.claude/harness.yaml → ~/Dev/cc-harness/harness.yaml
```

Update by pulling the repo — symlinks keep everything in sync.

---

## Commands Reference

Commands are slash commands invoked as `/command-name [args]` in Claude Code. They encode repeatable workflows as prompts.

### Ship & Deploy

| Command | Usage | Description |
|---------|-------|-------------|
| `/ship` | `/ship`, `/ship all`, `/ship dockit hydro-risk` | Commit + push one or more repos. Auto-generates conventional commit messages. `all` mode reads `repo-map.json` to find every dirty repo. |
| `/deploy` | `/deploy`, `/deploy --backend-only` | Deploy current project to VPS. Detects `deploy.sh`, builds frontend if needed, runs deploy, verifies with curl. |
| `/dashboard` | `/dashboard`, `/dashboard --scan-only` | Scan Claude Code sessions with LLM analyzer, then deploy the dashboard app. `--scan-only` skips deploy. `--force` ignores cache. |

### Repo Management

| Command | Usage | Description |
|---------|-------|-------------|
| `/groom` | `/groom`, `/groom hydro-risk learn`, `/groom --check` | Full repo maintenance pipeline: pull → audit (LICENSE, .gitignore, README, CLAUDE.md, GitHub metadata) → fix → review → push. Batches fixes by type for efficient approval. |
| `/promote` | `/promote`, `/promote all --check` | Lightweight GitHub metadata audit: description, topics, homepage, screenshots. Subset of `/groom` focused on public visibility. |
| `/repo-map` | `/repo-map scan`, `/repo-map sync`, `/repo-map show` | Manage the GitHub ↔ local path registry (`repo-map.json`). `scan` discovers repos on disk, `sync` propagates to consumers, `show` prints the table. |

### Infrastructure

| Command | Usage | Description |
|---------|-------|-------------|
| `/vps-status` | `/vps-status`, `/vps-status nginx` | SSH into VPS, show running services, ports, disk, memory, Docker containers. With a service name arg, also shows recent logs. |
| `/cf-dns` | `/cf-dns list`, `/cf-dns add status`, `/cf-dns delete old-sub` | Manage Cloudflare DNS records via API. `add` creates A record + Origin Rule in one step. |

### Document Processing

| Command | Usage | Description |
|---------|-------|-------------|
| `/md2word` | `/md2word path/to/file.md` | Full MD/DOCX → Word pipeline: template styling → text formatting (punctuation, units) → image caption centering. 4-step automated workflow. |
| `/review-docx` | `/review-docx path/to/report.docx` | Review a Word document: extract text, analyze for banned words / wrong punctuation / missing citations, write track-changes comments back into the file. |

### Hydro Project Tools

| Command | Usage | Description |
|---------|-------|-------------|
| `/build-hydro` | `/build-hydro capacity`, `/build-hydro all` | Build Tauri desktop installers for hydro apps. Reports artifact paths and sizes. |
| `/migrate-hydro` | `/migrate-hydro capacity` | Port a hydro Streamlit app's calculation logic to the corresponding Tauri desktop app. Reads Python → writes Rust + React. |

### Session & Workflow

| Command | Usage | Description |
|---------|-------|-------------|
| `/recap` | `/recap` | End-of-session retrospective: review conversation, extract lessons, update memory/skills/commands/CLAUDE.md, generate `session-retro-{date}.md`. |
| `/context` | `/context monitor`, `/context health` | Monitor Claude Code session health — token usage, tool call distribution, context bloat detection, snapshot save/restore. |
| `/tidy` | `/tidy`, `/tidy ~/Work/project/docs` | Deep-clean a directory: find garbage files, version chains, misplaced files. Presents table per directory, waits for approval before executing. |
| `/health` | `/health`, `/health --llm` | Run ZDWP workspace health check. Reports git leaks, version redundancy, scattered files with fix suggestions. |

### Standards

| Command | Usage | Description |
|---------|-------|-------------|
| `/frontend` | (auto-referenced) | Frontend development standards: information density, compact layout, actionable data, Streamlit conventions. Not typically invoked directly — used as reference during UI work. |

---

## Skills Reference

Skills are auto-triggered context injections. When Claude Code detects a matching scenario, it loads the skill's knowledge into context automatically. No manual invocation needed.

### Global Skills (active in all projects)

| Skill | Trigger | What it provides |
|-------|---------|-----------------|
| **context** | Working in ZDWP water company projects | Company org structure, county/city list, data field specs, delivery standards |
| **structure** | Organizing files, creating new projects | Directory naming rules, file classification rules, auto-organize logic |
| **plan-first** | Batch operations, destructive actions | Forces "write plan before executing" discipline — present table, wait for approval |
| **quarto** | Converting DOCX to Quarto projects | Quarto compilation workflow, template structure, figure/table handling |

### Project-Specific Skills

| Skill | Projects | What it provides |
|-------|----------|-----------------|
| **risk-map** | ~/Work/risk-map | Flood risk map data processing, QGIS spatial workflows, Excel template filling |
| **eco-flow** | ~/Work/eco-flow | Ecological flow calculation (Tennant method), reservoir screening, guarantee plans |
| **zdys** | ~/Work/zdys | Zhedong Diversion operations, dispatch models, irrigation demand calculation |
| **water-src** | ~/Work/water-src | Drinking water source safety assessment, evaluation methodology |
| **water-quality** | (standalone) | Qiandao Lake water quality classification supply management |
| **resources** | risk-map, eco-flow, zdys, water-src | Shared resource directory: reservoir data, GIS basemaps, admin boundaries, annual reports, industry standards |

### Utility Skills

| Skill | Trigger | What it provides |
|-------|---------|-----------------|
| **harness** | Checking/syncing skill configurations | Skill distribution registry, cross-project sync logic |
| **repo-manage** | Managing GitHub repos | Audit/screenshot/promote SOPs |
| **restart** | Resuming after terminal restart | Session recovery instructions |

---

## Agents Reference

Agents are specialized autonomous workers for complex multi-step tasks.

| Agent | Purpose |
|-------|---------|
| **bid-chapter-writer** | Writes bid document chapters following company templates and formatting standards |
| **project-content-checker** | Audits project deliverables for completeness against requirements checklists |

---

## Audit Tool

The audit tool (`harness.py`) scans any project's Claude Code configuration and produces a scored report across 6 dimensions:

| Dimension | What's checked |
|-----------|---------------|
| **D1 Context** | CLAUDE.md quality, token budget, duplicates, nested files, credentials |
| **D2 Hooks** | PostToolUse coverage, schema validity, output truncation, error surfacing |
| **D3 Agents** | Skill count, overlap, description quality, frontmatter, disable-model-invocation |
| **D4 Verification** | Done-conditions, build/test commands, CI integration |
| **D5 Session** | Compact Instructions, HANDOFF.md, context budget documentation |
| **D6 Structure** | Orphan files, reference chain, naming conventions, gitignore |

### Tier Detection

Projects are auto-classified to calibrate expectations:

| Tier | Signal | Expectation |
|------|--------|-------------|
| Simple | <500 source files, 1 contributor, no CI | CLAUDE.md only |
| Standard | 500-5K files, small team or CI | CLAUDE.md + rules + skills + hooks |
| Complex | >5K files, multi-contributor, active CI | Full six-layer setup |

### Usage

```bash
# Full audit
python3 harness.py /path/to/project

# JSON output
python3 harness.py /path/to/project --json

# Security scan only
python3 harness.py /path/to/project --security-only

# Custom Claude home directory
python3 harness.py /path/to/project --claude-home ~/.claude
```

### Security Scanner

Built-in scanner checks skills for 6 categories of risk:

1. **Prompt injection** — instruction override, role hijacking
2. **Data exfiltration** — HTTP POST with secrets, base64 encoding
3. **Destructive commands** — rm -rf /, force-push main, chmod 777
4. **Hardcoded credentials** — api_key/secret_key with long strings
5. **Obfuscation** — eval $(), base64 decode piped to shell
6. **Safety override** — bypass/disable safety/rules/hooks

---

## Skill Distribution (harness.yaml)

`harness.yaml` is the registry that maps skills to projects:

```yaml
global_skills:        # Active everywhere
  - context
  - structure
  - plan-first
  - quarto

projects:             # Project-specific bundles
  risk-map:
    path: ~/Work/risk-map
    skills: [risk-map, resources, plan-first]
  eco-flow:
    path: ~/Work/eco-flow
    skills: [eco-flow, resources, plan-first]
  # ...

standalone:           # Single-project skills
  - water-quality
```

The `/harness` skill handles syncing this registry to actual project configurations.

---

## Project Structure

```
cc-harness/
├── harness.py          # CLI entry — tier detection + audit orchestration
├── harness.yaml        # Skill-to-project distribution registry
├── install.sh          # Symlink installer
├── analyzers/          # 6-dimension audit logic
├── collectors/         # Data collectors (metrics/hooks/config/skills)
├── security/           # Security scanner (6 risk categories)
├── reporters/          # Output formatters (scorecard + markdown)
├── commands/           # 17 slash commands → ~/.claude/commands
├── skills/             # 13 auto-triggered skills → ~/.claude/skills
├── agents/             # 2 agent definitions → ~/.claude/agents
├── tests/              # pytest test suite
└── docs/               # Screenshots, documentation
```

## Tests

```bash
python3 -m pytest tests/ -v
```

## License

MIT
