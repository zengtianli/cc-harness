"""Token analysis by tool type."""

from dataclasses import dataclass, field
from typing import Optional

from monitor.parser import SessionData


@dataclass
class TokenSummary:
    """Aggregated token usage for a session."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    tool_calls: dict[str, int] = field(default_factory=dict)  # tool_name -> count
    turn_count: int = 0
    user_turns: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate = cache_read / (cache_read + input_tokens)."""
        denom = self.cache_read_tokens + self.input_tokens
        if denom == 0:
            return 0.0
        return self.cache_read_tokens / denom

    @property
    def total_tool_calls(self) -> int:
        return sum(self.tool_calls.values())


def compute_token_stats(session: SessionData) -> TokenSummary:
    """Compute token statistics from a parsed session."""
    summary = TokenSummary()

    for entry in session.messages:
        entry_type = entry.get("type")

        if entry_type == "user":
            # Only count user turns that have actual user content (not tool results)
            msg = entry.get("message", {})
            content = msg.get("content", "")
            is_tool_result = False
            if isinstance(content, list):
                is_tool_result = all(
                    isinstance(item, dict) and item.get("type") == "tool_result"
                    for item in content
                    if isinstance(item, dict)
                )
            if not is_tool_result:
                summary.user_turns += 1

        elif entry_type == "assistant":
            summary.turn_count += 1
            msg = entry.get("message", {})

            # Accumulate token usage
            usage = msg.get("usage", {})
            summary.input_tokens += usage.get("input_tokens", 0)
            summary.output_tokens += usage.get("output_tokens", 0)
            summary.cache_read_tokens += usage.get("cache_read_input_tokens", 0)
            summary.cache_creation_tokens += usage.get("cache_creation_input_tokens", 0)

            # Count tool calls
            content = msg.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_use":
                        tool_name = item.get("name", "unknown")
                        summary.tool_calls[tool_name] = summary.tool_calls.get(tool_name, 0) + 1

    return summary


def format_token_stats(summary: TokenSummary, session: Optional[SessionData] = None) -> str:
    """Format token stats for display."""
    lines: list[str] = []

    if session:
        lines.append(f"  Session: {session.session_id}")
        if session.model:
            lines.append(f"  Model: {session.model}")
        if session.start_time:
            lines.append(f"  Start: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if session.end_time:
            lines.append(f"  End:   {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if session.start_time and session.end_time:
            duration = session.end_time - session.start_time
            minutes = int(duration.total_seconds() / 60)
            lines.append(f"  Duration: {minutes} min")
        lines.append("")

    lines.append("  --- Token ---")
    lines.append(f"  Input:         {summary.input_tokens:>12,}")
    lines.append(f"  Output:        {summary.output_tokens:>12,}")
    lines.append(f"  Cache Read:    {summary.cache_read_tokens:>12,}")
    lines.append(f"  Cache Write:   {summary.cache_creation_tokens:>12,}")
    lines.append(f"  Total:         {summary.total_tokens:>12,}")
    lines.append(f"  Cache Hit:     {summary.cache_hit_rate:>11.1%}")
    lines.append("")

    lines.append(f"  --- Tool ({summary.total_tool_calls} calls) ---")
    if summary.tool_calls:
        sorted_tools = sorted(summary.tool_calls.items(), key=lambda x: x[1], reverse=True)
        total = summary.total_tool_calls
        for name, count in sorted_tools:
            pct = count / total * 100 if total > 0 else 0
            lines.append(f"  {name:<20s} {count:>4d}  ({pct:5.1f}%)")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append(f"  Turns: {summary.turn_count} assistant / {summary.user_turns} user")

    return "\n".join(lines)
