"""Skill security scan (6 categories)."""

import re


SECURITY_PATTERNS = {
    "prompt_injection": {
        "category": "Prompt Injection",
        "patterns": [
            (r"ignore\s+(previous|above|all)\s+(instructions|prompts|rules)", "指令覆盖尝试"),
            (r"you\s+are\s+now|pretend\s+you\s+are|act\s+as\s+if|new\s+persona", "角色劫持"),
        ],
    },
    "data_exfiltration": {
        "category": "Data Exfiltration",
        "patterns": [
            (r"(curl|wget).+(-X\s*POST|--data|-d\s).+https?://", "网络 POST 外发"),
            (r"base64.*encode.*(secret|key|token)", "Base64 编码凭证"),
        ],
    },
    "destructive": {
        "category": "Destructive Commands",
        "patterns": [
            (r"rm\s+-rf\s+[/~]", "递归删除根/家目录"),
            (r"git\s+push\s+--force\s+origin\s+main", "强制推送 main"),
            (r"chmod\s+777", "全局可写权限"),
        ],
    },
    "hardcoded_credentials": {
        "category": "Hardcoded Credentials",
        "patterns": [
            (
                r"(api_key|secret_key|api_secret|access_token)\s*[:=]\s*[\"'][A-Za-z0-9+/]{16,}",
                "硬编码凭证",
            ),
        ],
    },
    "obfuscation": {
        "category": "Obfuscation",
        "patterns": [
            (r"eval\s*\$\(", "eval 子 shell 执行"),
            (r"base64\s+-d", "Base64 解码执行"),
            (r"\\x[0-9a-fA-F]{2}", "Hex 转义序列"),
        ],
    },
    "safety_override": {
        "category": "Safety Override",
        "patterns": [
            (
                r"(override|bypass|disable)\s*(the\s+)?(safety|rules?|hooks?|guard|verification)",
                "安全机制覆盖",
            ),
        ],
    },
}


def _scan_text(text: str, source: str) -> list:
    """Scan text for security patterns."""
    findings = []
    lines = text.split("\n")

    for cat_key, cat_info in SECURITY_PATTERNS.items():
        for pattern, desc in cat_info["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's in a code block that DISCUSSES the pattern
                    # vs one that USES it
                    context_start = max(0, i - 3)
                    context_end = min(len(lines), i + 2)
                    context = "\n".join(lines[context_start:context_end])

                    # Heuristic: if surrounding context contains "check", "scan",
                    # "detect", "flag", "grep" - it's discussing, not using
                    discussing_indicators = [
                        "check", "scan", "detect", "flag", "grep", "search",
                        "pattern", "example", "warning", "dangerous",
                    ]
                    is_discussion = any(
                        ind in context.lower() for ind in discussing_indicators
                    )

                    if is_discussion:
                        continue

                    findings.append({
                        "severity": "critical",
                        "category": cat_info["category"],
                        "title": desc,
                        "detail": f"{source} 第 {i} 行: {line.strip()[:100]}",
                        "source": source,
                        "line": i,
                    })

    return findings


def scan_security(skills: list, config: dict) -> list:
    """Run security scan on all skills and config."""
    findings = []

    # Scan skills
    for skill in skills:
        content = skill.get("content", "")
        if content:
            skill_findings = _scan_text(content, f"skill:{skill['name']} ({skill['path']})")
            findings.extend(skill_findings)

    # Scan CLAUDE.md for credentials
    for label, key in [
        ("全局 CLAUDE.md", "global_claude_md"),
        ("本地 CLAUDE.md", "local_claude_md"),
    ]:
        text = config.get(key, "")
        if text:
            cred_findings = _scan_text(text, label)
            findings.extend(cred_findings)

    return findings
