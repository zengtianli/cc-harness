"""D6: Orphan files, reference chain, naming."""

import re
from pathlib import Path


def _check_orphan_files(config: dict) -> list:
    """Check for files not referenced by any CLAUDE.md or skill."""
    findings = []
    rules_files = config.get("rules_files", [])
    local_md = config.get("local_claude_md", "")
    global_md = config.get("global_claude_md", "")
    combined = local_md + "\n" + global_md

    for rf in rules_files:
        path = Path(rf["path"])
        fname = path.name
        if fname not in combined:
            findings.append({
                "severity": "info",
                "code": "D6-ORPHAN",
                "title": f"Rules 文件未被引用: {fname}",
                "detail": f"路径: {rf['path']}",
                "fix": "在 CLAUDE.md 中引用此文件，或删除孤立文件",
            })

    return findings


def _check_naming(skills: list) -> list:
    """Check skill naming conventions."""
    findings = []
    for s in skills:
        name = s.get("name", "")
        # Check for inconsistent naming (mix of Chinese and kebab-case, etc.)
        if " " in name:
            findings.append({
                "severity": "info",
                "code": "D6-NAME",
                "title": f"Skill 名称含空格: '{name}'",
                "detail": "建议使用 kebab-case 命名",
                "fix": f"重命名为 '{name.replace(' ', '-').lower()}'",
            })

    return findings


def _check_gitignore(config: dict) -> list:
    """Check if settings.local.json is gitignored."""
    findings = []
    if not config.get("gitignore_has_settings", True):
        settings = config.get("settings_json", {})
        if settings:
            findings.append({
                "severity": "critical",
                "code": "D6-GITIGNORE",
                "title": "settings.local.json 未加入 .gitignore",
                "detail": "可能将 API tokens 和个人路径提交到版本控制",
                "fix": "在 .gitignore 中添加 .claude/settings.local.json",
            })
        else:
            findings.append({
                "severity": "warning",
                "code": "D6-GITIGNORE",
                "title": "settings.local.json 未加入 .gitignore",
                "detail": "虽然当前无 settings 文件，但一旦创建有泄露风险",
                "fix": "在 .gitignore 中添加 .claude/settings.local.json",
            })
    return findings


def _check_reference_chain(config: dict, skills: list) -> list:
    """Check that CLAUDE.md references skills/rules properly."""
    findings = []
    local_md = config.get("local_claude_md", "")

    # Check if skills are mentioned in CLAUDE.md
    if skills and local_md:
        skill_names = [s["name"] for s in skills if s.get("origin") == "local"]
        mentioned = sum(1 for name in skill_names if name in local_md)
        if skill_names and mentioned == 0:
            findings.append({
                "severity": "info",
                "code": "D6-REF",
                "title": "CLAUDE.md 未引用任何本地 skill",
                "detail": f"有 {len(skill_names)} 个本地 skills 但 CLAUDE.md 中未提及",
                "fix": "在 CLAUDE.md 中简要提及关键 skills 的用途",
            })

    return findings


def analyze_structure(config: dict, skills: list, tier: str) -> dict:
    """Analyze D6 file structure."""
    findings = []
    score = 10.0

    # Orphan files
    orphans = _check_orphan_files(config)
    findings.extend(orphans)
    score -= min(1.5, len(orphans) * 0.3)

    # Naming
    naming = _check_naming(skills)
    findings.extend(naming)
    score -= min(1.0, len(naming) * 0.2)

    # Gitignore
    gi_findings = _check_gitignore(config)
    findings.extend(gi_findings)
    for f in gi_findings:
        if f["severity"] == "critical":
            score -= 2.0
        else:
            score -= 0.5

    # Reference chain
    ref_findings = _check_reference_chain(config, skills)
    findings.extend(ref_findings)
    score -= min(1.0, len(ref_findings) * 0.3)

    if not findings:
        findings.append({
            "severity": "info",
            "code": "D6-OK",
            "title": "文件结构正常",
            "detail": "",
            "fix": "",
        })

    score = max(0.0, min(10.0, score))
    return {
        "dimension": "D6 结构",
        "score": round(score, 1),
        "max_score": 10.0,
        "findings": findings,
    }
