"""D4: Done-conditions coverage."""

import re


def _has_verification_section(text: str) -> bool:
    """Check if text has a verification/done-conditions section."""
    patterns = [
        r"##\s*(验证|Verification|Done.?conditions|完成条件)",
        r"##\s*验证规则",
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _has_build_test_commands(text: str) -> bool:
    """Check if CLAUDE.md has build/test commands."""
    patterns = [
        r"(cargo|npm|python|pytest|go|make|gradle)\s+(build|test|check|run)",
        r"```(bash|sh|shell)",
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def analyze_verification(config: dict, metrics: dict, tier: str) -> dict:
    """Analyze D4 verification layer."""
    findings = []
    score = 10.0

    local_md = config.get("local_claude_md", "")
    global_md = config.get("global_claude_md", "")

    # Simple tier: minimal verification needed
    if tier == "simple":
        if not _has_build_test_commands(local_md) and not _has_build_test_commands(global_md):
            findings.append({
                "severity": "info",
                "code": "V4-CMD",
                "title": "CLAUDE.md 未包含 build/test 命令",
                "detail": "即使 Simple 项目也建议有基本的验证命令",
                "fix": "在 CLAUDE.md 中添加项目的 build/test 命令",
            })
            score -= 1.0
        return {
            "dimension": "D4 验证",
            "score": round(max(0.0, min(10.0, score)), 1),
            "max_score": 10.0,
            "findings": findings,
        }

    # Standard+: expect verification section
    has_verify = _has_verification_section(local_md) or _has_verification_section(global_md)
    if not has_verify:
        findings.append({
            "severity": "warning",
            "code": "V4-SECTION",
            "title": "CLAUDE.md 缺少验证章节",
            "detail": "Standard+ 项目应有 Verification/验证规则 章节",
            "fix": "添加 ## 验证规则 章节，定义任务完成条件",
        })
        score -= 2.5

    has_commands = _has_build_test_commands(local_md)
    if not has_commands:
        findings.append({
            "severity": "warning",
            "code": "V4-CMD",
            "title": "CLAUDE.md 未包含 build/test 命令",
            "detail": "无法自动验证任务完成状态",
            "fix": "添加项目的 build/test/lint 命令",
        })
        score -= 1.5

    # Check for CI integration on complex
    if tier == "complex" and metrics.get("ci_workflows", 0) == 0:
        findings.append({
            "severity": "info",
            "code": "V4-CI",
            "title": "Complex 项目无 CI 工作流",
            "detail": "建议配置 CI 自动验证",
            "fix": "添加 .github/workflows/ CI 配置",
        })
        score -= 1.0

    score = max(0.0, min(10.0, score))
    return {
        "dimension": "D4 验证",
        "score": round(score, 1),
        "max_score": 10.0,
        "findings": findings,
    }
