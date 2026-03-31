# cc-harness

A standalone CLI tool that audits your Claude Code configuration quality across six dimensions and outputs a scored report with actionable fix recommendations.

## What it does

cc-harness scans your project's Claude Code setup -- CLAUDE.md, skills, hooks, rules, settings -- and produces a six-dimension score card plus a prioritized findings report (Critical / Structural / Incremental). It also runs a security scan on all skills.

**No Claude Code or API key required.** Pure Python, stdlib only.

## Six Dimensions

| Dimension | What's checked |
|-----------|---------------|
| **D1 Context** | CLAUDE.md quality, token budget, duplicates, nested files, credentials |
| **D2 Hooks** | PostToolUse coverage, schema validity, output truncation, error surfacing |
| **D3 Agents** | Skill count, overlap, description quality, frontmatter, disable-model-invocation |
| **D4 Verification** | Done-conditions, build/test commands, CI integration |
| **D5 Session** | Compact Instructions, HANDOFF.md, context budget documentation |
| **D6 Structure** | Orphan files, reference chain, naming conventions, gitignore |

## Tier Detection

Projects are automatically classified to avoid over-checking simple setups:

| Tier | Signal | Expectation |
|------|--------|-------------|
| Simple | <500 source files, 1 contributor, no CI | CLAUDE.md only |
| Standard | 500-5K files, small team or CI | CLAUDE.md + rules + skills + hooks |
| Complex | >5K files, multi-contributor, active CI | Full six-layer setup |

## Usage

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

## Installation

No installation needed. Clone and run:

```bash
git clone https://github.com/zengtianli/cc-harness.git
cd cc-harness
python3 harness.py /path/to/your/project
```

Requirements: Python 3.8+ (stdlib only, no pip dependencies).

## Running Tests

```bash
cd cc-harness
python3 -m pytest tests/ -v
```

## Security Scanner

The built-in security scanner checks skills for 6 categories of risk:

1. **Prompt injection** -- instruction override, role hijacking
2. **Data exfiltration** -- HTTP POST with secrets, base64 encoding
3. **Destructive commands** -- rm -rf /, force-push main, chmod 777
4. **Hardcoded credentials** -- api_key/secret_key with long strings
5. **Obfuscation** -- eval $(), base64 decode piped to shell
6. **Safety override** -- bypass/disable safety/rules/hooks

The scanner distinguishes between skills that **discuss** security patterns (benign) vs. those that **use** them (flagged).

## License

MIT
