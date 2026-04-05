"""Anti-pattern detection in Claude Code sessions."""

from dataclasses import dataclass, field

from monitor.parser import SessionData


@dataclass
class PatternReport:
    """Detected anti-patterns."""

    patterns: list[str] = field(default_factory=list)


def detect_patterns(session: SessionData) -> PatternReport:
    """Detect anti-patterns in a session."""
    report = PatternReport()

    grep_queries: dict[str, int] = {}
    glob_queries: dict[str, int] = {}
    bash_commands: dict[str, int] = {}
    large_reads: list[str] = []
    large_outputs: int = 0

    for entry in session.messages:
        if entry.get("type") != "assistant":
            continue
        msg = entry.get("message", {})

        # Check for very large assistant outputs
        usage = msg.get("usage", {})
        out_tokens = usage.get("output_tokens", 0)
        if out_tokens > 5000:
            large_outputs += 1

        content = msg.get("content", [])
        if not isinstance(content, list):
            continue

        for item in content:
            if not isinstance(item, dict) or item.get("type") != "tool_use":
                continue

            name = item.get("name", "")
            inp = item.get("input", {})
            if not isinstance(inp, dict):
                continue

            if name == "Grep":
                pattern = inp.get("pattern", "")
                if pattern:
                    grep_queries[pattern] = grep_queries.get(pattern, 0) + 1

            elif name == "Glob":
                pattern = inp.get("pattern", "")
                if pattern:
                    glob_queries[pattern] = glob_queries.get(pattern, 0) + 1

            elif name == "Bash":
                cmd = inp.get("command", "")
                if cmd:
                    bash_commands[cmd] = bash_commands.get(cmd, 0) + 1

            elif name == "Read":
                fp = inp.get("file_path", "")
                offset = inp.get("offset")
                limit = inp.get("limit")
                if fp and offset is None and limit is None:
                    large_reads.append(fp)

    # Report repeated grep patterns
    for pattern, count in sorted(grep_queries.items(), key=lambda x: x[1], reverse=True):
        if count > 2:
            report.patterns.append(
                f"Grep pattern repeated {count} times: '{pattern}'"
            )

    # Report repeated glob patterns
    for pattern, count in sorted(glob_queries.items(), key=lambda x: x[1], reverse=True):
        if count > 2:
            report.patterns.append(
                f"Glob pattern repeated {count} times: '{pattern}'"
            )

    # Report repeated bash commands
    for cmd, count in sorted(bash_commands.items(), key=lambda x: x[1], reverse=True):
        if count > 2:
            short_cmd = cmd[:80] + "..." if len(cmd) > 80 else cmd
            report.patterns.append(
                f"Bash command repeated {count} times: '{short_cmd}'"
            )

    # Report large file reads without offset/limit
    if len(large_reads) >= 5:
        report.patterns.append(
            f"{len(large_reads)} file reads without offset/limit — may waste context on large files"
        )

    # Report large outputs
    if large_outputs > 3:
        report.patterns.append(
            f"{large_outputs} assistant responses with >5000 output tokens — consider more targeted requests"
        )

    return report


def format_pattern_report(report: PatternReport) -> str:
    """Format pattern report for display."""
    if not report.patterns:
        return "  No anti-patterns detected."

    lines = ["  [!] Anti-patterns:"]
    for p in report.patterns:
        lines.append(f"      - {p}")
    return "\n".join(lines)
