"""D2: Hooks coverage, schema validity."""


def analyze_hooks(hooks_data: dict, config: dict, tier: str) -> dict:
    """Analyze D2 Hooks system."""
    findings = []
    score = 10.0

    has_settings = hooks_data.get("has_settings", False)
    hook_entries = hooks_data.get("hook_entries", [])
    schema_issues = hooks_data.get("schema_issues", [])
    event_types = hooks_data.get("event_types", [])

    # Simple tier: hooks optional
    if tier == "simple":
        if not has_settings:
            return {
                "dimension": "D2 Hooks",
                "score": 8.0,
                "max_score": 10.0,
                "findings": [{
                    "severity": "info",
                    "code": "H2-SKIP",
                    "title": "Simple 项目，Hooks 为可选项",
                    "detail": "无 settings.local.json，Simple 级别不要求 hooks",
                    "fix": "",
                }],
            }

    # Standard+: expect hooks
    if not has_settings or not hook_entries:
        findings.append({
            "severity": "warning",
            "code": "H2-MISSING",
            "title": "无 Hooks 配置",
            "detail": "Standard+ 级别项目应有 PostToolUse hooks",
            "fix": "创建 settings.local.json 并配置 PostToolUse hooks",
        })
        score -= 3.0

    # PostToolUse check
    if "PostToolUse" not in event_types and hook_entries:
        findings.append({
            "severity": "warning",
            "code": "H2-POST",
            "title": "缺少 PostToolUse hooks",
            "detail": "无编辑后自动检查",
            "fix": "添加 PostToolUse hook 用于主要语言的语法检查",
        })
        score -= 1.5

    # Schema issues
    for issue in schema_issues:
        findings.append({
            "severity": "warning",
            "code": "H2-SCHEMA",
            "title": f"Hook 架构问题 ({issue['event']})",
            "detail": issue["issue"],
            "fix": "修复 hook 配置的 schema",
        })
        score -= 0.5

    # Command issues
    for entry in hook_entries:
        for cmd_issue in entry.get("command_issues", []):
            findings.append({
                "severity": "warning",
                "code": "H2-CMD",
                "title": f"Hook 命令问题 ({entry['matcher']})",
                "detail": cmd_issue,
                "fix": "修复 hook 命令",
            })
            score -= 0.3

    # Notification hook (complex only)
    if tier == "complex" and "Notification" not in event_types:
        findings.append({
            "severity": "info",
            "code": "H2-NOTIFY",
            "title": "缺少 Notification hook",
            "detail": "Complex 项目建议配置通知 hook",
            "fix": "添加 Notification hook",
        })
        score -= 0.5

    score = max(0.0, min(10.0, score))
    return {
        "dimension": "D2 Hooks",
        "score": round(score, 1),
        "max_score": 10.0,
        "findings": findings,
    }
