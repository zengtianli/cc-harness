"""Collect source file count, contributors, CI, startup token budget."""

import subprocess
from pathlib import Path

SOURCE_EXTENSIONS = {
    ".rs", ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".lua",
    ".swift", ".rb", ".java", ".kt", ".cs", ".cpp", ".c", ".h",
}

SKIP_DIRS = {".git", "node_modules", "vendor", "target", "build", "dist", "__pycache__"}


def _count_source_files(project_path: Path) -> int:
    """Count source files, skipping common non-source directories."""
    count = 0
    for f in project_path.rglob("*"):
        if any(skip in f.parts for skip in SKIP_DIRS):
            continue
        if f.is_file() and f.suffix in SOURCE_EXTENSIONS:
            count += 1
    return count


def _count_contributors(project_path: Path) -> int:
    """Count unique git contributors."""
    try:
        result = subprocess.run(
            ["git", "-C", str(project_path), "log", "--format=%ae"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return 0
        emails = set(line.strip() for line in result.stdout.strip().split("\n") if line.strip())
        return len(emails)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return 0


def _count_ci_workflows(project_path: Path) -> int:
    """Count CI workflow files."""
    workflows_dir = project_path / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return 0
    count = 0
    for ext in ("*.yml", "*.yaml"):
        count += len(list(workflows_dir.glob(ext)))
    return count


def _estimate_startup_tokens(project_path: Path, claude_home: Path) -> int:
    """Estimate startup context token budget."""

    def word_count(path: Path) -> int:
        try:
            return len(path.read_text(encoding="utf-8").split())
        except (FileNotFoundError, PermissionError, OSError):
            return 0

    global_words = word_count(claude_home / "CLAUDE.md")
    local_words = word_count(project_path / "CLAUDE.md")

    rules_words = 0
    rules_dir = project_path / ".claude" / "rules"
    if rules_dir.is_dir():
        for f in rules_dir.glob("*.md"):
            rules_words += word_count(f)

    skill_desc_words = 0
    for skills_dir in [project_path / ".claude" / "skills", claude_home / "skills"]:
        if skills_dir.is_dir():
            for skill_dir in skills_dir.iterdir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.is_file():
                    try:
                        content = skill_file.read_text(encoding="utf-8")
                        # Count only description line words
                        for line in content.split("\n"):
                            if line.startswith("description:"):
                                skill_desc_words += len(line.split())
                    except (PermissionError, OSError):
                        pass

    # Token estimate: words * 1.3
    base_tokens = int((global_words + local_words + rules_words + skill_desc_words) * 1.3)
    return base_tokens


def _count_conversations(project_path: Path, claude_home: Path) -> int:
    """Count conversation files for this project."""
    projects_dir = claude_home / "projects"
    if not projects_dir.is_dir():
        return 0

    count = 0
    for d in projects_dir.iterdir():
        if not d.is_dir():
            continue
        # Heuristic match
        dir_name = d.name.lower().replace("-", "")
        proj_name = project_path.name.lower().replace("-", "")
        if proj_name in dir_name or dir_name in proj_name:
            count += len(list(d.glob("*.jsonl")))
    return count


def collect_metrics(project_path: Path, claude_home: Path) -> dict:
    """Collect all project metrics."""
    return {
        "source_files": _count_source_files(project_path),
        "contributors": _count_contributors(project_path),
        "ci_workflows": _count_ci_workflows(project_path),
        "startup_tokens": _estimate_startup_tokens(project_path, claude_home),
        "conversation_count": _count_conversations(project_path, claude_home),
    }
