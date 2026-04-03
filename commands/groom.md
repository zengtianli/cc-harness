Orchestrate repo maintenance: pull → audit → fix → review → push.

## Scope

Determine targets from $ARGUMENTS:
- No args → all non-ignored repos in `~/Dev/configs/repo-map.json`
- `<name> [name2 ...]` → specific repos by name (lookup in repo-map.json)
- `--check` → audit only, no fixes
- `--skip-pull` → skip pull phase
- `--category <cat>` → filter by category (hydro/tools/infra/knowledge/personal/work)

## References

- Repo registry: `~/Dev/configs/repo-map.json`
- Completeness standards: `~/Dev/configs/repo-standards.json`
- Gold standard README: `~/Dev/dockit/README.md` (EN), `~/Dev/dockit/README_CN.md` (CN)
- Audit tool: `python3 ~/Dev/devtools/repo_manager.py audit`

Skip repos where local path doesn't exist (warn) or `"ignored": true`.

---

## Phase 1: Pull

For each target repo (resolve `local` path from repo-map.json):
1. `git pull --ff-only`
2. If fails: log ⚠ and continue (don't force)

Output summary:
```
✓ dockit          pulled (2 commits)
✓ hydro-rainfall  already up to date
⚠ vps             diverged — skipping fixes
— oauth-proxy     no remote tracking branch
```

---

## Phase 2: Audit

Load `~/Dev/configs/repo-standards.json`. For each repo, check against `common` + its category requirements:

### File checks
- LICENSE exists (MIT, copyright holder = tianli)
- .gitignore exists and contains all `gitignore_baseline` entries
- README.md exists
- README_CN.md exists (if `category.bilingual = true`)
- CLAUDE.md exists

### README quality (if exists)
Check against the repo's `readme_template` sections list:
- **app** template: language selector, for-the-badge badges, separator, screenshot/demo ref, feature table, install, quick start
- **infra** template: title, badges, what-it-does, setup, usage
- **content** template: title, badges, contents overview
- **minimal** template: title, overview

### GitHub metadata
```bash
gh repo view zengtianli/<name> --json description,repositoryTopics,homepageUrl
```
- Description non-empty
- Topics count >= `min_topics` (3)
- Homepage set if repo has `vps` path or Streamlit deploy

### Output

```
✅ dockit           — all clear
🔧 hydro-rainfall  — missing LICENSE, missing README_CN.md
🔧 learn           — missing CLAUDE.md, missing LICENSE, 0 topics
⚠️  essays          — missing LICENSE, no description
```

If `--check`, stop here.

---

## Phase 3: Fix

Group all issues by fix type. Generate fixes but do NOT apply yet.

### Auto-fixable (批量确认)

**1. LICENSE**
Add MIT LICENSE file:
```
MIT License

Copyright (c) 2025 tianli

Permission is hereby granted, free of charge...
[standard MIT text]
```

**2. .gitignore gaps**
Append missing baseline entries from `repo-standards.json → common.gitignore_baseline`. Do not remove existing entries.

**3. GitHub metadata**
For each repo with gaps:
- **description**: Extract from README first non-empty line after title/language selector. If no README, use repo-map category + name.
- **topics**: Start with `category.topic_base`, add stack-specific (streamlit/tauri/cli). Use `gh repo edit` to set.
- **homepage**: If repo has `vps` in repo-map and category is hydro, set `https://{name}.tianlizeng.cloud`.

### User-review fixes (逐个确认)

**4. CLAUDE.md generation**
Read the repo's code to generate:
- Title + one-line description
- Quick Reference table (key files, URLs, deploy paths)
- Common commands (dev/test/build/deploy)
- Project structure (`tree` output, depth 2)
- Development notes

Style: Chinese (matching existing CLAUDE.md convention across repos).

**5. README.md generation/repair**
- If missing: generate from scratch using the category's `readme_template`
- If exists but failing checks: fix structural issues only, preserve existing content
- Follow gold standard structure for `app` template repos
- Generate in English first

**6. README_CN.md translation**
For repos where `bilingual = true` and README_CN.md is missing or outdated:
- Translate README.md to Chinese
- Mirror structure exactly (same sections, same badges with Chinese labels)
- Keep code blocks, URLs, and technical terms unchanged

**7. /tidy cleanup**
Only for `work` category repos that have deliverables/ or docs/ directories:
- Apply `/tidy` scanning logic (garbage files, version chains, scattered files)
- Present per-directory tables
- **Always requires explicit user approval per repo**

---

## Phase 4: Review Checkpoint

Present changes **grouped by fix type** for efficient batch review:

### Batch-approvable
```markdown
### LICENSE additions (N repos)
hydro-rainfall, hydro-risk, learn, essays, ...
→ All identical MIT template. Approve all? [Y/n]

### .gitignore fixes (N repos)
[table: repo | entries added]
→ Approve all? [Y/n]

### GitHub metadata (N repos)
| Repo | Change | Old → New |
|------|--------|-----------|
| learn | +topics | (none) → knowledge, ai-learning, python |
| hydro-rainfall | +description | (empty) → "Rainfall-runoff calculator..." |
→ Approve all? [Y/n]
```

### Individual review
```markdown
### CLAUDE.md (N repos)
**learn:**
[full generated content]
→ Approve? [Y/n/edit]

### README updates (N repos)
**hydro-rainfall:**
[diff or full content]
→ Approve? [Y/n/edit]

### README_CN.md translations (N repos)
**hydro-rainfall:**
[full translated content]
→ Approve? [Y/n/edit]

### /tidy cleanup (work repos)
**zdwp:**
[/tidy output tables]
→ Approve? [Y/n/edit]
```

User can approve, reject, or request edits for each item.

---

## Phase 5: Ship

For each repo with approved changes:
1. `git add` specific changed files (not `-A`)
2. Commit with conventional message:
   - `chore: add LICENSE` / `chore: add LICENSE, fix .gitignore`
   - `docs: add CLAUDE.md` / `docs: generate README`
   - `docs: add Chinese README`
3. Append `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`
4. `git push`

Final summary:
```
✓ hydro-rainfall  a7f3b1c  chore: add LICENSE, fix .gitignore
✓ learn           e96c3c4  docs: add CLAUDE.md, generate README
✓ essays          b2d4e8f  chore: add LICENSE
✗ vps             (push failed — behind remote)
— dockit          (no changes needed)
```

---

## Rules

- repo-map.json is the sole source of truth for repo list
- repo-standards.json is the sole source of truth for completeness criteria
- Never force-push or rewrite history
- Never commit .env, credentials, secrets, *.pem, *.key
- If pull diverged, audit but don't fix (user must resolve manually)
- CLAUDE.md content in Chinese (existing convention)
- README.md in English, README_CN.md in Chinese
- Commit messages: conventional commits (chore/docs/fix)
- /tidy and README changes always need individual review
- LICENSE and .gitignore can be batch-approved
