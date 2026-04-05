"""Parse Claude Code session .jsonl files."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SKIP_TYPES = {"file-history-snapshot", "progress", "queue-operation", "last-prompt"}


@dataclass
class SessionData:
    """Parsed session data from a .jsonl file."""

    messages: list[dict] = field(default_factory=list)
    path: Path = field(default_factory=lambda: Path())
    session_id: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    model: Optional[str] = None
    project_path: str = ""
    git_branch: Optional[str] = None
    slug: Optional[str] = None


def parse_timestamp(ts_str) -> Optional[datetime]:
    """Parse ISO 8601 timestamp string or unix millis."""
    if isinstance(ts_str, (int, float)):
        return datetime.fromtimestamp(ts_str / 1000, tz=timezone.utc)
    if not isinstance(ts_str, str):
        return None
    try:
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return None


def parse_session(jsonl_path: Path) -> SessionData:
    """Parse a session .jsonl file into SessionData."""
    messages: list[dict] = []
    session_id = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    model: Optional[str] = None
    project_path = ""
    git_branch: Optional[str] = None
    slug: Optional[str] = None

    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = entry.get("type")
                if entry_type in SKIP_TYPES:
                    continue

                messages.append(entry)

                # Track timestamps
                ts_str = entry.get("timestamp")
                if ts_str:
                    ts = parse_timestamp(ts_str)
                    if ts:
                        if start_time is None or ts < start_time:
                            start_time = ts
                        if end_time is None or ts > end_time:
                            end_time = ts

                # Extract metadata from first user message
                if entry_type == "user" and not session_id:
                    session_id = entry.get("sessionId", "")
                    project_path = entry.get("cwd", "")
                    git_branch = entry.get("gitBranch")

                if entry_type == "assistant":
                    if slug is None:
                        slug = entry.get("slug")
                    msg = entry.get("message", {})
                    if model is None:
                        model = msg.get("model")
    except OSError:
        pass

    if not session_id:
        session_id = jsonl_path.stem

    return SessionData(
        messages=messages,
        path=jsonl_path,
        session_id=session_id,
        start_time=start_time,
        end_time=end_time,
        model=model,
        project_path=project_path,
        git_branch=git_branch,
        slug=slug,
    )


def find_sessions(claude_home: Optional[Path] = None) -> list[Path]:
    """Find all session .jsonl files, sorted by modification time (newest first)."""
    if claude_home is None:
        claude_home = Path.home() / ".claude"
    if not claude_home.exists():
        return []
    paths = list(claude_home.glob("projects/*/*.jsonl"))
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)
