"""Session health metrics and checks."""

from dataclasses import dataclass, field

from monitor.parser import SessionData
from monitor.token_stats import TokenSummary, compute_token_stats


@dataclass
class HealthReport:
    """Health check results."""

    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    score: int = 100  # 0-100, deducted per issue


def check_session_health(session: SessionData) -> HealthReport:
    """Run health checks on a session."""
    report = HealthReport()
    summary = compute_token_stats(session)

    # Count user turns (non-tool-result)
    user_turns = summary.user_turns

    # Check turn count
    if user_turns > 100:
        report.warnings.append(
            f"Session has {user_turns} user turns — consider splitting into smaller tasks"
        )
        report.score -= 15
    elif user_turns > 50:
        report.info.append(f"Session has {user_turns} user turns — getting long")
        report.score -= 5

    # Check duration
    if session.start_time and session.end_time:
        duration_hours = (session.end_time - session.start_time).total_seconds() / 3600
        if duration_hours > 3:
            report.warnings.append(
                f"Session lasted {duration_hours:.1f} hours — long session, context may degrade"
            )
            report.score -= 10
        elif duration_hours > 1.5:
            report.info.append(f"Session lasted {duration_hours:.1f} hours")

    # Check cache hit rate
    if summary.input_tokens + summary.cache_read_tokens > 0:
        if summary.cache_hit_rate < 0.5:
            report.warnings.append(
                f"Cache hit rate is {summary.cache_hit_rate:.0%} — very poor caching"
            )
            report.score -= 20
        elif summary.cache_hit_rate < 0.8:
            report.warnings.append(
                f"Cache hit rate is {summary.cache_hit_rate:.0%} — below 80%, consider restructuring prompts"
            )
            report.score -= 10

    # Check for files read multiple times
    file_read_counts: dict[str, int] = {}
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
            if item.get("type") == "tool_use" and item.get("name") == "Read":
                inp = item.get("input", {})
                if isinstance(inp, dict):
                    fp = inp.get("file_path", "")
                    if fp:
                        file_read_counts[fp] = file_read_counts.get(fp, 0) + 1

    repeated = {fp: c for fp, c in file_read_counts.items() if c > 3}
    if repeated:
        for fp, count in sorted(repeated.items(), key=lambda x: x[1], reverse=True)[:5]:
            report.warnings.append(
                f"File read {count} times: {fp} — use CLAUDE.md memory instead"
            )
        report.score -= min(len(repeated) * 5, 20)

    # Clamp score
    report.score = max(0, report.score)

    # Add summary info
    report.info.append(f"Total tokens: {summary.total_tokens:,}")
    report.info.append(f"Tool calls: {summary.total_tool_calls}")

    return report


def format_health_report(report: HealthReport, session: SessionData) -> str:
    """Format health report for display."""
    lines: list[str] = []

    # Score
    if report.score >= 80:
        grade = "Good"
    elif report.score >= 60:
        grade = "Fair"
    else:
        grade = "Poor"

    lines.append(f"  Session: {session.session_id}")
    lines.append(f"  Health:  {report.score}/100 ({grade})")
    lines.append("")

    if report.warnings:
        lines.append("  [!] Warnings:")
        for w in report.warnings:
            lines.append(f"      - {w}")
        lines.append("")

    if report.info:
        lines.append("  [i] Info:")
        for i in report.info:
            lines.append(f"      - {i}")

    return "\n".join(lines)
