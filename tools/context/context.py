#!/usr/bin/env python3
"""cc-configs context: Claude Code context engineering toolkit.

Usage:
    python3 context.py monitor                          # Latest session tokens
    python3 context.py monitor --session SESSION_ID     # Specific session
    python3 context.py monitor --all --json             # All sessions JSON
    python3 context.py snapshot save                    # Save snapshot
    python3 context.py snapshot restore                 # Restore snapshot
    python3 context.py health                           # Health check latest
    python3 context.py health --all                     # All sessions
    python3 context.py hooks install                    # Install compact hook
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from monitor.parser import parse_session, find_sessions
from monitor.token_stats import compute_token_stats, format_token_stats
from monitor.cost_tracker import estimate_cost, format_cost
from snapshot.auto_save import save_snapshot
from snapshot.restore import restore_latest
from health.session_check import check_session_health, format_health_report
from health.patterns import detect_patterns, format_pattern_report
from hooks.install import install_hook


def find_session_by_id(session_id: str) -> Path | None:
    """Find a session file by its ID."""
    for path in find_sessions():
        if path.stem == session_id or session_id in path.stem:
            return path
    return None


def cmd_monitor(args: argparse.Namespace) -> None:
    """Monitor token usage."""
    if args.session:
        path = find_session_by_id(args.session)
        if not path:
            print(f"Session not found: {args.session}", file=sys.stderr)
            sys.exit(1)
        paths = [path]
    elif args.all:
        paths = find_sessions()
        if not paths:
            print("No sessions found.", file=sys.stderr)
            sys.exit(1)
    else:
        paths = find_sessions()
        if not paths:
            print("No sessions found.", file=sys.stderr)
            sys.exit(1)
        paths = [paths[0]]

    results = []
    for p in paths:
        session = parse_session(p)
        summary = compute_token_stats(session)
        cost = estimate_cost(summary, session.model)

        if args.json:
            results.append({
                "session_id": session.session_id,
                "model": session.model,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "tokens": {
                    "input": summary.input_tokens,
                    "output": summary.output_tokens,
                    "cache_read": summary.cache_read_tokens,
                    "cache_creation": summary.cache_creation_tokens,
                    "total": summary.total_tokens,
                    "cache_hit_rate": round(summary.cache_hit_rate, 4),
                },
                "tool_calls": summary.tool_calls,
                "turns": {"assistant": summary.turn_count, "user": summary.user_turns},
                "cost": {k: round(v, 6) for k, v in cost.items()},
            })
        else:
            print(format_token_stats(summary, session))
            print(format_cost(cost, session.model))
            print()

    if args.json:
        output = results if args.all else results[0]
        print(json.dumps(output, indent=2, ensure_ascii=False))


def cmd_snapshot(args: argparse.Namespace) -> None:
    """Snapshot save/restore."""
    if args.action == "save":
        session_id = getattr(args, "session", None)
        if session_id:
            path = find_session_by_id(session_id)
        else:
            paths = find_sessions()
            path = paths[0] if paths else None

        if not path:
            print("No session found.", file=sys.stderr)
            sys.exit(1)

        session = parse_session(path)
        out = save_snapshot(session)
        if not getattr(args, "quiet", False):
            print(f"Snapshot saved: {out}")

    elif args.action == "restore":
        content = restore_latest()
        print(content)


def cmd_health(args: argparse.Namespace) -> None:
    """Health check."""
    if args.all:
        paths = find_sessions()
    else:
        paths = find_sessions()
        if paths:
            paths = [paths[0]]

    if not paths:
        print("No sessions found.", file=sys.stderr)
        sys.exit(1)

    for p in paths:
        session = parse_session(p)
        report = check_session_health(session)
        print(format_health_report(report, session))
        print()

        pattern_report = detect_patterns(session)
        print(format_pattern_report(pattern_report))
        print()
        print("  " + "-" * 40)
        print()


def cmd_hooks(args: argparse.Namespace) -> None:
    """Hook management."""
    if args.action == "install":
        result = install_hook()
        print(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cc-configs-context",
        description="Claude Code context engineering toolkit",
    )
    subparsers = parser.add_subparsers(dest="command")

    # monitor
    p_monitor = subparsers.add_parser("monitor", help="Token monitoring")
    p_monitor.add_argument("--session", "-s", help="Session ID")
    p_monitor.add_argument("--all", "-a", action="store_true", help="All sessions")
    p_monitor.add_argument("--json", "-j", action="store_true", help="JSON output")

    # snapshot
    p_snapshot = subparsers.add_parser("snapshot", help="Context snapshots")
    p_snapshot.add_argument("action", choices=["save", "restore"], help="save or restore")
    p_snapshot.add_argument("--session", "-s", help="Session ID")
    p_snapshot.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")

    # health
    p_health = subparsers.add_parser("health", help="Session health check")
    p_health.add_argument("--all", "-a", action="store_true", help="All sessions")

    # hooks
    p_hooks = subparsers.add_parser("hooks", help="Hook management")
    p_hooks.add_argument("action", choices=["install"], help="install")

    args = parser.parse_args()

    if args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "snapshot":
        cmd_snapshot(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "hooks":
        cmd_hooks(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
