"""D5: Compact Instructions, Handoff, templates."""

import re


def _has_compact_instructions(text: str) -> bool:
    """Check for Compact Instructions section."""
    return bool(re.search(r"(Compact\s+Instructions|紧凑指令|压缩指令)", text, re.IGNORECASE))


def _has_handoff(config: dict) -> bool:
    """Check if handoff mechanism exists."""
    if config.get("handoff_md"):
        return True
    # Check if CLAUDE.md mentions handoff
    for md in [config.get("local_claude_md", ""), config.get("global_claude_md", "")]:
        if re.search(r"(handoff|交接|HANDOFF)", md, re.IGNORECASE):
            return True
    return False


def _has_context_budget(text: str) -> bool:
    """Check if context budget is documented."""
    return bool(re.search(r"(context\s*budget|上下文\s*预算|token\s*(budget|限制|预算))", text, re.IGNORECASE))


def analyze_session(config: dict, tier: str) -> dict:
    """Analyze D5 session management."""
    findings = []
    score = 10.0

    local_md = config.get("local_claude_md", "")
    global_md = config.get("global_claude_md", "")
    combined_md = global_md + "\n" + local_md

    # Simple: minimal requirements
    if tier == "simple":
        return {
            "dimension": "D5 会话",
            "score": 8.5,
            "max_score": 10.0,
            "findings": [{
                "severity": "info",
                "code": "S5-SKIP",
                "title": "Simple 项目，会话管理为可选项",
                "detail": "",
                "fix": "",
            }],
        }

    # Compact Instructions
    if not _has_compact_instructions(combined_md):
        findings.append({
            "severity": "warning",
            "code": "S5-COMPACT",
            "title": "缺少 Compact Instructions",
            "detail": "未找到 Compact Instructions 章节",
            "fix": "添加结构化的 Compact Instructions 指导长会话压缩",
        })
        score -= 2.0

    # Handoff
    if not _has_handoff(config):
        findings.append({
            "severity": "warning",
            "code": "S5-HANDOFF",
            "title": "缺少跨会话交接机制",
            "detail": "无 HANDOFF.md 且 CLAUDE.md 未提及交接",
            "fix": "创建 HANDOFF.md 或在 CLAUDE.md 中定义交接格式",
        })
        score -= 1.5

    # Context budget
    if not _has_context_budget(combined_md):
        findings.append({
            "severity": "info",
            "code": "S5-BUDGET",
            "title": "未记录上下文预算规范",
            "detail": "建议明确上下文使用策略",
            "fix": "在 CLAUDE.md 中添加 Context Budget 规范",
        })
        score -= 0.5

    score = max(0.0, min(10.0, score))
    return {
        "dimension": "D5 会话",
        "score": round(score, 1),
        "max_score": 10.0,
        "findings": findings,
    }
