#!/usr/bin/env python3
"""Scan CC session transcripts and report slash command usage frequency."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude" / "projects"


def scan_sessions(days: int = 0) -> Counter:
    """Scan all session JSONL files and count slash command invocations.

    Counts both:
    - User messages starting with /command
    - Skill tool_use calls
    """
    counter: Counter = Counter()
    cutoff = 0.0
    if days > 0:
        import time
        cutoff = time.time() - days * 86400

    for jsonl in CLAUDE_DIR.rglob("*.jsonl"):
        if "subagents" in str(jsonl) or "cache" in str(jsonl):
            continue
        if cutoff and jsonl.stat().st_mtime < cutoff:
            continue
        try:
            with open(jsonl) as f:
                for line in f:
                    try:
                        obj = json.loads(line.strip())
                        msg = obj.get("message", {})
                        role = msg.get("role", "")
                        content = msg.get("content", "")

                        # User typed /command
                        if role == "user" and isinstance(content, str):
                            for m in re.finditer(r"(?:^|\s)(\/[a-z][\w-]*)", content):
                                counter[m.group(1)] += 1

                        # Skill tool call
                        if isinstance(content, list):
                            for c in content:
                                if (isinstance(c, dict)
                                        and c.get("type") == "tool_use"
                                        and c.get("name") == "Skill"):
                                    skill = c.get("input", {}).get("skill", "")
                                    if skill:
                                        counter[f"/{skill}"] += 1
                    except (json.JSONDecodeError, KeyError):
                        pass
        except (OSError, PermissionError):
            pass

    return counter


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CC command usage stats")
    parser.add_argument("--days", type=int, default=0,
                        help="Only count sessions modified in last N days (0=all)")
    parser.add_argument("--top", type=int, default=30,
                        help="Show top N commands")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--registered", action="store_true",
                        help="Only show commands that have a .md file in commands/")
    args = parser.parse_args()

    counter = scan_sessions(args.days)

    if not counter:
        print("No command usage found.")
        sys.exit(0)

    # Optionally filter to registered commands
    if args.registered:
        cmd_dir = Path(__file__).resolve().parent.parent / "commands"
        registered = set()
        for md in cmd_dir.glob("*.md"):
            registered.add(f"/{md.stem}")
        for md in (cmd_dir / "archive").glob("*.md"):
            registered.add(f"/{md.stem}")
        counter = Counter({k: v for k, v in counter.items() if k in registered})

    if args.json:
        print(json.dumps(dict(counter.most_common(args.top)), indent=2))
    else:
        period = f"last {args.days} days" if args.days else "all time"
        print(f"Command usage ({period}):\n")
        print(f"{'Count':>5}  {'Command':<25}  Bar")
        print(f"{'─'*5}  {'─'*25}  {'─'*30}")
        top = counter.most_common(args.top)
        max_count = top[0][1] if top else 1
        for cmd, count in top:
            bar_len = int(count / max_count * 25)
            print(f"{count:>5}  {cmd:<25}  {'█' * bar_len}")
        print(f"\nTotal: {sum(counter.values())} invocations, {len(counter)} unique commands")


if __name__ == "__main__":
    main()
