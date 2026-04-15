# Repo Management SOP

When the user wants to manage, audit, screenshot, or promote GitHub repositories under ~/Dev.

## Available Tools

### 1. repo_audit.py — 项目合规性审计
Checks README structure, badges, screenshots, gitignore, dependency pinning against DocKit gold standard template.

```bash
# Audit all projects
python3 ~/Dev/scripts/repo_audit.py

# Audit specific projects
python3 ~/Dev/scripts/repo_audit.py cc-configs dockit

# Audit + auto-fix gitignore gaps
python3 ~/Dev/scripts/repo_audit.py --fix-gitignore
```

**Checks performed:**
- README.md / README_CN.md: language selector, for-the-badge badges, separator lines, screenshot reference, feature table, install/quick start sections
- .gitignore: baseline entries (__pycache__, .env, venv, IDE, build artifacts, lint cache)
- requirements.txt: all dependencies must be version-pinned (>=X.Y.Z)

### 2. repo_screenshot.py — 统一截图工具
Supports both Streamlit apps (Playwright URL screenshots) and CLI tools (terminal output rendering).

```bash
# Screenshot a Streamlit app
python3 ~/Dev/scripts/repo_screenshot.py streamlit hydro-rainfall https://hydro-rainfall.tianlizeng.cloud

# Screenshot a CLI tool
python3 ~/Dev/scripts/repo_screenshot.py cli cc-configs "python3 tools/harness/harness.py ~/Dev/dockit"

# Batch all Streamlit apps
python3 ~/Dev/scripts/repo_screenshot.py batch

# Batch all (including CLI)
python3 ~/Dev/scripts/repo_screenshot.py batch --include-cli
```

**Output:** `docs/screenshots/demo.png` (1280x800) in each project directory.

### 3. promote_repos.py — 批量推广
Generates bilingual READMEs, SVG demo previews, badges, and pushes to GitHub.

```bash
# Promote all registered repos
python3 ~/Dev/scripts/promote_repos.py

# Promote specific repos
python3 ~/Dev/scripts/promote_repos.py hydro-rainfall dockit
```

**Note:** This tool generates from templates, overwriting existing READMEs. Use for initial setup only.

### 4. screenshot_repos.py — 旧版 Streamlit 截图（已被 repo_screenshot.py 替代）
Legacy tool, only supports Streamlit apps. Use repo_screenshot.py instead.

---

## SOP: New Project Setup

When creating a new project under ~/Dev:

1. **README** — Follow DocKit template:
   - Language selector: `**English** | [中文](README_CN.md)` 
   - Badges: License + Python version, `for-the-badge` style, colors: License=green, Python=yellow, Demo=blue
   - Separator `---` after badges and after screenshot
   - Feature table, Install, Quick Start sections
   - README_CN.md as full Chinese mirror

2. **Screenshot** — Generate with repo_screenshot.py:
   - Streamlit: `repo_screenshot.py streamlit <name> <url>`
   - CLI: `repo_screenshot.py cli <name> "<command>"`

3. **.gitignore** — Run `repo_audit.py --fix-gitignore <name>` to ensure baseline coverage

4. **Dependencies** — Pin all versions: `package>=X.Y.Z`

5. **Verify** — Run `repo_audit.py <name>` to confirm compliance

## SOP: Periodic Audit

```bash
python3 ~/Dev/scripts/repo_audit.py
```

Fix any issues found, then re-run to confirm clean.

## Gold Standard Template Reference

The definitive example is **dockit** (`~/Dev/dockit/README.md`).

Badge colors:
- Live Demo: `blue`
- License: `green`  
- Python version: `yellow`

All badges use `style=for-the-badge`.
