"""Extract and save context snapshot from a session."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from monitor.parser import SessionData
from monitor.token_stats import TokenSummary, compute_token_stats
from monitor.cost_tracker import estimate_cost


def extract_modified_files(session: SessionData) -> list[str]:
    """Extract file paths modified by Write/Edit tools."""
    files: list[str] = []
    seen: set[str] = set()

    for entry in session.messages:
        if entry.get("type") != "assistant":
            continue
        msg = entry.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "tool_use":
                continue
            name = item.get("name", "")
            if name not in ("Write", "Edit"):
                continue
            inp = item.get("input", {})
            if isinstance(inp, dict):
                fp = inp.get("file_path", "")
                if fp and fp not in seen:
                    seen.add(fp)
                    files.append(fp)

    return files


def build_snapshot_markdown(
    session: SessionData,
    summary: TokenSummary,
    modified_files: list[str],
) -> str:
    """Build a markdown snapshot of the session."""
    lines: list[str] = []
    lines.append(f"# Session Snapshot: {session.session_id}")
    lines.append("")

    if session.start_time:
        lines.append(f"- **Start**: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if session.end_time:
        lines.append(f"- **End**: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if session.start_time and session.end_time:
        dur = int((session.end_time - session.start_time).total_seconds() / 60)
        lines.append(f"- **Duration**: {dur} min")
    if session.model:
        lines.append(f"- **Model**: {session.model}")
    if session.project_path:
        lines.append(f"- **Project**: {session.project_path}")
    lines.append(f"- **Turns**: {summary.turn_count} assistant / {summary.user_turns} user")
    lines.append("")

    # Token summary
    lines.append("## Token")
    lines.append("")
    lines.append(f"| Type | Count |")
    lines.append(f"|------|-------|")
    lines.append(f"| Input | {summary.input_tokens:,} |")
    lines.append(f"| Output | {summary.output_tokens:,} |")
    lines.append(f"| Cache Read | {summary.cache_read_tokens:,} |")
    lines.append(f"| Cache Write | {summary.cache_creation_tokens:,} |")
    lines.append(f"| Cache Hit | {summary.cache_hit_rate:.1%} |")
    lines.append("")

    # Cost
    cost = estimate_cost(summary, session.model)
    lines.append(f"**Cost**: ${cost['total']:.4f}")
    lines.append("")

    # Tool usage
    lines.append("## Tool")
    lines.append("")
    if summary.tool_calls:
        lines.append(f"| Tool | Calls |")
        lines.append(f"|------|-------|")
        for name, count in sorted(summary.tool_calls.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {name} | {count} |")
    else:
        lines.append("(none)")
    lines.append("")

    # Modified files
    lines.append("## Modified Files")
    lines.append("")
    if modified_files:
        for fp in modified_files:
            lines.append(f"- `{fp}`")
    else:
        lines.append("(none)")
    lines.append("")

    return "\n".join(lines)


def save_snapshot(session: SessionData, output_dir: Optional[Path] = None) -> Path:
    """Save a context snapshot to a markdown file.

    Returns the path to the saved snapshot.
    """
    if output_dir is None:
        output_dir = Path.home() / ".claude" / "snapshots"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = compute_token_stats(session)
    modified_files = extract_modified_files(session)
    md = build_snapshot_markdown(session, summary, modified_files)

    now = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"{session.session_id}-{now}.md"
    out_path = output_dir / filename
    out_path.write_text(md, encoding="utf-8")

    return out_path
