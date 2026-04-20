Repo 维护全流程，编排原子命令：/pull → /audit → fix(/promote) → review → /ship。

## 范围

从 $ARGUMENTS 确定目标：
- 无参数 → 所有 non-ignored repos（`~/Dev/configs/repo-map.json`）
- `<name> [name2 ...]` → 指定 repo（repo-map.json 查路径）
- `--check` → 只跑 Phase 1-2（/pull + /audit），不修复
- `--skip-pull` → 跳过 Phase 1
- `--category <cat>` → 按分类过滤（hydro/tools/infra/knowledge/personal/work）

## 数据源

- `~/Dev/configs/repo-map.json` — repo 注册表
- `~/Dev/configs/repo-standards.json` — 完整性标准
- 金标准 README：`~/Dev/stations/dockit/README.md`（EN）、`~/Dev/stations/dockit/README_CN.md`（CN）

跳过 `local` 路径不存在的 repo（warn）或 `"ignored": true`。

---

## Phase 1: Pull

调用 `/pull <targets>`。

---

## Phase 2: Audit

调用 `/audit <targets>`。

如果 `--check`，到这里停止。

---

## Phase 3: Fix

Group all issues by fix type. Generate fixes but do NOT apply yet.

### Auto-fixable（批量确认）

**1. LICENSE**
Add MIT LICENSE file (copyright holder = tianli, year = current year).

**2. .gitignore gaps**
Append missing baseline entries from `repo-standards.json → common.gitignore_baseline`. Do not remove existing entries.

**3. GitHub metadata**
调用 `/promote <name>` 处理每个有 metadata 问题的 repo：
- description: 从 README 提取
- topics: 从 `category.topic_base` + 技术栈推断
- homepage: 有 VPS 部署的设 `https://{name}.tianlizeng.cloud`

### User-review fixes（逐个确认）

**4. CLAUDE.md generation**
Read the repo's code to generate:
- Title + one-line description
- Quick Reference table (key files, URLs, deploy paths)
- Common commands (dev/test/build/deploy)
- Project structure (`tree` output, depth 2)

Style: Chinese (matching existing CLAUDE.md convention).

**5. README.md generation/repair**
- Missing: generate from category's `readme_template`
- Exists but failing checks: fix structural issues only
- Generate in English first

**6. README_CN.md translation**
For repos where `bilingual = true` and README_CN.md is missing/outdated:
- Translate README.md to Chinese
- Mirror structure exactly
- Keep code blocks, URLs, technical terms unchanged

---

## Phase 4: Review Checkpoint

### Batch-approvable
```
LICENSE additions (N repos) → Approve all? [Y/n]
.gitignore fixes (N repos) → Approve all? [Y/n]
GitHub metadata (N repos) → table with changes → Approve all? [Y/n]
```

### Individual review
```
CLAUDE.md (N repos) → each: Approve? [Y/n/edit]
README updates (N repos) → each: Approve? [Y/n/edit]
README_CN.md translations (N repos) → each: Approve? [Y/n/edit]
```

---

## Phase 5: Ship

调用 `/ship <targets>`（只推有 approved changes 的 repo）。

Commit messages: conventional commits（chore/docs/fix）.

Final summary:
```
✓ hydro-rainfall  a7f3b1c  chore: add LICENSE, fix .gitignore
✓ learn           e96c3c4  docs: add CLAUDE.md, generate README
✗ vps             (push failed — behind remote)
— dockit          (no changes needed)
```

---

## 调用的原子命令

- `/pull` — Phase 1: git pull
- `/audit` — Phase 2: 完整性审计
- `/promote` — Phase 3: GitHub metadata 修复
- `/ship` — Phase 5: commit + push

## 规则

- repo-map.json is the sole source of truth for repo list
- repo-standards.json is the sole source of truth for completeness criteria
- Never force-push or rewrite history
- Never commit .env, credentials, secrets, *.pem, *.key
- If pull diverged, audit but don't fix
- CLAUDE.md in Chinese, README.md in English, README_CN.md in Chinese
- /tidy and README changes always need individual review
- LICENSE and .gitignore can be batch-approved
