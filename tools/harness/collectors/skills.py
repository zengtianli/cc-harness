"""Collect skill inventory, frontmatter, content."""

import re
from pathlib import Path


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from skill content."""
    if not content.startswith("---"):
        return {}
    lines = content.split("\n")
    fm_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)
    else:
        return {}

    result = {}
    for line in fm_lines:
        match = re.match(r"^(\w[\w-]*):\s*(.+)$", line.strip())
        if match:
            key = match.group(1)
            val = match.group(2).strip().strip('"').strip("'")
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            result[key] = val
    return result


def _collect_skills_from_dir(skills_dir: Path) -> list:
    """Collect all SKILL.md files from a directory."""
    if not skills_dir.is_dir():
        return []

    results = []
    # Check direct subdirectories and symlinked directories
    for entry in sorted(skills_dir.iterdir()):
        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue

        try:
            content = skill_file.read_text(encoding="utf-8")
        except (PermissionError, OSError):
            content = ""

        frontmatter = _parse_frontmatter(content)
        word_count = len(content.split())

        results.append({
            "path": str(skill_file),
            "dir_path": str(entry),
            "name": frontmatter.get("name", entry.name),
            "description": frontmatter.get("description", ""),
            "version": frontmatter.get("version", ""),
            "word_count": word_count,
            "has_frontmatter": bool(frontmatter),
            "frontmatter": frontmatter,
            "is_symlink": entry.is_symlink(),
            "content": content,
            "disable_model_invocation": frontmatter.get("disable-model-invocation", False),
        })

    return results


def collect_skills(project_path: Path, claude_home: Path) -> list:
    """Collect skills from both local and global directories."""
    local_skills = _collect_skills_from_dir(project_path / ".claude" / "skills")
    global_skills = _collect_skills_from_dir(claude_home / "skills")

    # Tag origin
    for s in local_skills:
        s["origin"] = "local"
    for s in global_skills:
        s["origin"] = "global"

    return local_skills + global_skills
