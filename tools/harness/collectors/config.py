"""Collect CLAUDE.md (global+local), settings.json, rules/, gitignore info."""

import json
from pathlib import Path


def _read_text(path: Path) -> str:
    """Read file text, return empty string if missing."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, OSError):
        return ""


def _find_nested_claude_mds(project_path: Path) -> list:
    """Find CLAUDE.md files in subdirectories (not root)."""
    root_claude = project_path / "CLAUDE.md"
    results = []
    for p in project_path.rglob("CLAUDE.md"):
        if p == root_claude:
            continue
        # Skip .git and node_modules
        parts = p.parts
        if ".git" in parts or "node_modules" in parts:
            continue
        results.append(str(p))
    return results


def _find_rules_files(project_path: Path) -> list:
    """Find all .md files in .claude/rules/."""
    rules_dir = project_path / ".claude" / "rules"
    if not rules_dir.is_dir():
        return []
    return [
        {"path": str(f), "content": _read_text(f)}
        for f in sorted(rules_dir.glob("*.md"))
    ]


def _check_gitignore(project_path: Path) -> bool:
    """Check if settings.local.json is in .gitignore."""
    for gitignore_path in [
        project_path / ".gitignore",
        project_path / ".claude" / ".gitignore",
    ]:
        content = _read_text(gitignore_path)
        if "settings.local" in content or "settings.local.json" in content:
            return True
    return False


def _load_settings_json(project_path: Path) -> dict:
    """Load .claude/settings.local.json."""
    path = project_path / ".claude" / "settings.local.json"
    content = _read_text(path)
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"_parse_error": True}


def collect_config(project_path: Path, claude_home: Path) -> dict:
    """Collect all configuration data."""
    global_claude_md = _read_text(claude_home / "CLAUDE.md")
    local_claude_md = _read_text(project_path / "CLAUDE.md")
    nested_claude_mds = _find_nested_claude_mds(project_path)
    settings_json = _load_settings_json(project_path)
    rules_files = _find_rules_files(project_path)
    gitignore_has_settings = _check_gitignore(project_path)
    handoff_md = _read_text(project_path / "HANDOFF.md")
    memory_md = _read_text(claude_home / "MEMORY.md")

    # Also check project-scoped memory
    project_memory_md = ""
    projects_dir = claude_home / "projects"
    if projects_dir.is_dir():
        for d in projects_dir.iterdir():
            mem_path = d / "memory" / "MEMORY.md"
            if mem_path.is_file():
                # Heuristic: check if directory name relates to project
                dir_name = d.name.lower().replace("-", "")
                proj_name = project_path.name.lower().replace("-", "")
                if proj_name in dir_name or dir_name in proj_name:
                    project_memory_md = _read_text(mem_path)
                    break

    return {
        "global_claude_md": global_claude_md,
        "local_claude_md": local_claude_md,
        "nested_claude_mds": nested_claude_mds,
        "settings_json": settings_json,
        "rules_files": rules_files,
        "gitignore_has_settings": gitignore_has_settings,
        "handoff_md": handoff_md,
        "memory_md": memory_md,
        "project_memory_md": project_memory_md,
    }
