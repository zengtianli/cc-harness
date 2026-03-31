"""Collect hooks config and validate schema."""

import json
from pathlib import Path


def _load_settings(project_path: Path) -> dict:
    """Load settings.local.json."""
    path = project_path / ".claude" / "settings.local.json"
    try:
        content = path.read_text(encoding="utf-8")
        return json.loads(content)
    except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError):
        return {}


def _validate_hook_schema(hook_entry: dict) -> list:
    """Validate a single hook entry's schema. Returns list of issues."""
    issues = []
    if "matcher" not in hook_entry:
        issues.append("missing 'matcher' field - hook would fire on ALL tool calls")
    if "hooks" not in hook_entry:
        issues.append("missing 'hooks' array")
    elif isinstance(hook_entry["hooks"], list):
        for i, h in enumerate(hook_entry["hooks"]):
            if "type" not in h:
                issues.append(f"hook[{i}] missing 'type' field")
            if "command" not in h:
                issues.append(f"hook[{i}] missing 'command' field")
    return issues


def _check_hook_command(command: str) -> list:
    """Check a hook command for common issues."""
    issues = []
    # Check for full test suites
    test_commands = [
        "cargo test", "npm test", "pytest", "go test", "jest",
        "python -m pytest", "python3 -m pytest",
    ]
    for tc in test_commands:
        if tc in command and "check" not in command.lower():
            issues.append(f"runs full test suite '{tc}' on every edit - use fast checker instead")

    # Check for output truncation
    if "| head" not in command and "| tail" not in command and len(command) > 20:
        issues.append("no output truncation (missing '| head -N' or '| tail -N')")

    # Check for error surfacing
    if "|| echo" not in command and "exit" not in command and "FAILED" not in command:
        issues.append("no error surfacing (missing '|| echo FAILED' or exit handling)")

    return issues


def collect_hooks(project_path: Path) -> dict:
    """Collect and validate hooks configuration."""
    settings = _load_settings(project_path)
    hooks_config = settings.get("hooks", {})
    has_settings = bool(settings)

    hook_entries = []
    schema_issues = []

    for event_type, entries in hooks_config.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            schema_errs = _validate_hook_schema(entry)
            if schema_errs:
                schema_issues.extend(
                    {"event": event_type, "issue": e} for e in schema_errs
                )

            hooks_list = entry.get("hooks", [])
            if isinstance(hooks_list, list):
                for h in hooks_list:
                    cmd = h.get("command", "")
                    cmd_issues = _check_hook_command(cmd)
                    hook_entries.append({
                        "event": event_type,
                        "matcher": entry.get("matcher", "(none)"),
                        "command": cmd,
                        "command_issues": cmd_issues,
                    })

    return {
        "has_settings": has_settings,
        "hooks_config": hooks_config,
        "hook_entries": hook_entries,
        "schema_issues": schema_issues,
        "event_types": list(hooks_config.keys()),
    }
