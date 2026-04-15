# Restart / Resume Session

The user wants to resume this Claude Code session after restarting Ghostty or the terminal.

Output the following (replace SESSION_ID with the actual current session ID from context):

1. **Continue most recent session** (simplest):
```
claude -c
```

2. **Resume this specific session by ID**:
```
claude -r SESSION_ID
```

To find the current session ID, look at the task output file paths in this conversation — they follow the pattern `/tmp/.../SESSION_ID/...`. The session ID is the UUID segment.

Always output both commands so the user can choose. Keep the response short and direct — just the two commands with brief labels.
