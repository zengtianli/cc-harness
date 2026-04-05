"""Install compact hook into Claude Code settings.json."""

import json
from pathlib import Path
from typing import Optional


HOOK_CONFIG = {
    "type": "command",
    "event": "notification",
    "command": "python3 ~/Dev/cc-configs/tools/context/context.py snapshot save --quiet",
    "timeout": 10000,
}


def get_settings_path(claude_home: Optional[Path] = None) -> Path:
    """Get the path to Claude Code settings.json."""
    if claude_home is None:
        claude_home = Path.home() / ".claude"
    return claude_home / "settings.json"


def install_hook(claude_home: Optional[Path] = None) -> str:
    """Install the compact auto-save hook into settings.json.

    Returns a status message.
    """
    settings_path = get_settings_path(claude_home)

    # Load existing settings
    settings: dict = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Ensure hooks list exists
    hooks = settings.get("hooks", [])
    if not isinstance(hooks, list):
        hooks = []

    # Check if already installed
    for hook in hooks:
        if isinstance(hook, dict) and "context.py" in hook.get("command", ""):
            return "Hook already installed."

    # Add our hook
    hook_entry = {**HOOK_CONFIG, "name": "cc-context-autosave"}
    hooks.append(hook_entry)
    settings["hooks"] = hooks

    # Write back
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return f"Hook installed to {settings_path}"
