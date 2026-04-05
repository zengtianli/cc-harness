"""D1: CLAUDE.md quality, duplicates, token budget."""

import re


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _token_estimate(words: int) -> int:
    return int(words * 1.3)


def _find_duplicates(global_md: str, local_md: str) -> list:
    """Find duplicate/conflicting rules between global and local CLAUDE.md."""
    findings = []
    if not global_md or not local_md:
        return findings

    # Extract lines that look like rules (NEVER, ALWAYS, must, should, etc.)
    rule_pattern = re.compile(r"^[-*]\s*.*(NEVER|ALWAYS|must|禁止|必须|不要|不得)", re.IGNORECASE)

    global_rules = [
        line.strip() for line in global_md.split("\n")
        if rule_pattern.match(line.strip())
    ]
    local_rules = [
        line.strip() for line in local_md.split("\n")
        if rule_pattern.match(line.strip())
    ]

    for gr in global_rules:
        for lr in local_rules:
            # Simple similarity: if >60% words overlap
            g_words = set(gr.lower().split())
            l_words = set(lr.lower().split())
            if len(g_words) < 3 or len(l_words) < 3:
                continue
            overlap = len(g_words & l_words) / min(len(g_words), len(l_words))
            if overlap > 0.6:
                findings.append({
                    "severity": "info",
                    "code": "C1-DUP",
                    "title": "全局/本地规则重复",
                    "detail": f"全局: {gr[:80]}... | 本地: {lr[:80]}...",
                    "fix": "删除本地重复规则，减少上下文占用",
                })

    return findings


def _check_credentials(text: str, source: str) -> list:
    """Check for hardcoded credentials."""
    findings = []
    cred_pattern = re.compile(
        r"(api_key|secret_key|api_secret|access_token|auth.token)\s*[:=]\s*['\"]?[A-Za-z0-9+/]{16,}",
        re.IGNORECASE,
    )
    for i, line in enumerate(text.split("\n"), 1):
        if cred_pattern.search(line):
            findings.append({
                "severity": "critical",
                "code": "C1-CRED",
                "title": f"{source} 包含硬编码凭证",
                "detail": f"第 {i} 行疑似包含明文凭证",
                "fix": "移除明文凭证，改为引用环境变量",
            })
    return findings


def analyze_context(config: dict, metrics: dict, tier: str) -> dict:
    """Analyze D1 Context Engineering."""
    findings = []
    score = 10.0

    global_md = config.get("global_claude_md", "")
    local_md = config.get("local_claude_md", "")
    nested = config.get("nested_claude_mds", [])
    memory_md = config.get("memory_md", "") or config.get("project_memory_md", "")
    startup_tokens = metrics.get("startup_tokens", 0)

    # Check CLAUDE.md exists
    if not local_md:
        findings.append({
            "severity": "critical",
            "code": "C1-MISSING",
            "title": "项目缺少 CLAUDE.md",
            "detail": "未找到本地 CLAUDE.md 文件",
            "fix": "创建 CLAUDE.md，至少包含 build/test 命令和基本规则",
        })
        score -= 3.0

    # Token budget check
    if startup_tokens > 30000:
        findings.append({
            "severity": "critical",
            "code": "C1-BUDGET",
            "title": f"启动上下文过大: {startup_tokens} tokens",
            "detail": f"超过 30K 阈值 (200K 的 15%)",
            "fix": "精简 CLAUDE.md，将详细内容迁移到 rules/ 或 skills",
        })
        score -= 2.0
    elif startup_tokens > 20000:
        findings.append({
            "severity": "warning",
            "code": "C1-BUDGET",
            "title": f"启动上下文偏大: {startup_tokens} tokens",
            "detail": "接近 30K 阈值",
            "fix": "考虑精简 CLAUDE.md 内容",
        })
        score -= 1.0

    # CLAUDE.md size check
    local_tokens = _token_estimate(_word_count(local_md))
    if local_tokens > 5000:
        findings.append({
            "severity": "warning",
            "code": "C1-SIZE",
            "title": f"CLAUDE.md 过大: ~{local_tokens} tokens",
            "detail": "超过 5K token 建议阈值",
            "fix": "将业务细节迁移到 rules/ 或 skills，CLAUDE.md 保持精简",
        })
        score -= 1.0

    # Nested CLAUDE.md
    if nested:
        findings.append({
            "severity": "critical",
            "code": "C1-NESTED",
            "title": f"发现 {len(nested)} 个嵌套 CLAUDE.md",
            "detail": "嵌套 CLAUDE.md 导致不可预测的上下文叠加: " + ", ".join(nested[:3]),
            "fix": "迁移到 skills 或重命名为 PROJECT_NOTES.md",
        })
        score -= min(2.0, len(nested) * 0.5)

    # Duplicate rules
    dup_findings = _find_duplicates(global_md, local_md)
    findings.extend(dup_findings)
    if dup_findings:
        score -= min(1.0, len(dup_findings) * 0.3)

    # Hardcoded credentials
    cred_findings = _check_credentials(global_md, "全局 CLAUDE.md")
    cred_findings.extend(_check_credentials(local_md, "本地 CLAUDE.md"))
    findings.extend(cred_findings)
    if cred_findings:
        score -= 2.0

    # MEMORY.md check (STANDARD+)
    if tier != "simple" and not memory_md:
        conv_count = metrics.get("conversation_count", 0)
        if conv_count >= 10:
            sev = "critical"
            score -= 1.5
        elif conv_count >= 3:
            sev = "warning"
            score -= 0.5
        else:
            sev = "info"
        findings.append({
            "severity": sev,
            "code": "C1-MEMORY",
            "title": "缺少 MEMORY.md",
            "detail": f"项目有 {conv_count} 个会话文件，但未找到 MEMORY.md",
            "fix": "创建 MEMORY.md 记录架构决策和关键 tradeoffs",
        })

    score = max(0.0, min(10.0, score))
    return {
        "dimension": "D1 Context",
        "score": round(score, 1),
        "max_score": 10.0,
        "findings": findings,
    }
