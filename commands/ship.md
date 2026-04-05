Commit and push changes in one or more projects under ~/Dev.

## Behavior

1. **Determine scope** from $ARGUMENTS:
   - No args → current working directory (must be a git repo)
   - `.` → current working directory
   - `all` → read `~/Dev/configs/repo-map.json`, ship ALL repos that have uncommitted changes
   - `<name> [name2 ...]` → look up name in `repo-map.json` to resolve local path, then ship

2. **For each project with changes:**
   - Run `git status --short` to see what changed
   - Run `git diff --stat` for a summary
   - Stage all modified/untracked files with `git add -A`
   - Generate a concise commit message from the diff (1-2 sentences, conventional commits style)
   - Commit and push in one step
   - Report result: ✓ project → commit hash, or ✗ project → error

3. **Output a summary table** at the end:
   ```
   ✓ dockit        a7ff7b1  docs: fix Python version badge
   ✓ cc-configs    e96c3c4  docs: unify README format
   ✗ hydro-annual  (nothing to commit)
   ```

## Rules

- Always append `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` to commit messages
- Never commit files matching: `.env`, `credentials*`, `*secret*`, `*.pem`, `*.key`
- If `all` mode finds 5+ projects with changes, list them first and ask for confirmation before proceeding
- Use `git push` (never force push)
- If push fails (e.g. behind remote), report the error — don't force push or auto-rebase
