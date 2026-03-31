"""D3: Skill count, overlap, descriptor quality."""


def _find_overlapping_skills(skills: list) -> list:
    """Find skills with overlapping descriptions."""
    overlaps = []
    for i, s1 in enumerate(skills):
        for s2 in skills[i + 1:]:
            d1 = s1.get("description", "").lower()
            d2 = s2.get("description", "").lower()
            if not d1 or not d2:
                continue
            words1 = set(d1.split())
            words2 = set(d2.split())
            if len(words1) < 3 or len(words2) < 3:
                continue
            overlap = len(words1 & words2) / min(len(words1), len(words2))
            if overlap > 0.6:
                overlaps.append((s1["name"], s2["name"], d1, d2))
    return overlaps


def analyze_agents(skills: list, tier: str) -> dict:
    """Analyze D3 Sub-agent patterns."""
    findings = []
    score = 10.0

    skill_count = len(skills)

    # Simple tier: 0-1 skills is fine
    if tier == "simple":
        if skill_count <= 1:
            return {
                "dimension": "D3 Agents",
                "score": 9.0,
                "max_score": 10.0,
                "findings": [{
                    "severity": "info",
                    "code": "A3-SKIP",
                    "title": f"Simple 项目，{skill_count} 个 skill，正常",
                    "detail": "",
                    "fix": "",
                }],
            }

    # Too many skills
    if skill_count > 20:
        findings.append({
            "severity": "warning",
            "code": "A3-COUNT",
            "title": f"Skills 数量过多: {skill_count} (建议 <20)",
            "detail": "过多 skills 增加上下文开销和匹配混淆",
            "fix": "合并重叠 skills，禁用低频 skills",
        })
        score -= 1.5

    # Description quality
    for s in skills:
        desc = s.get("description", "")
        if not desc:
            findings.append({
                "severity": "warning",
                "code": "A3-DESC",
                "title": f"Skill '{s['name']}' 缺少描述",
                "detail": f"路径: {s['path']}",
                "fix": "添加 <12 词的描述，说明何时触发",
            })
            score -= 0.3
        elif len(desc.split()) > 12:
            findings.append({
                "severity": "info",
                "code": "A3-DESC-LONG",
                "title": f"Skill '{s['name']}' 描述过长 ({len(desc.split())} 词)",
                "detail": f"描述: {desc[:80]}...",
                "fix": "精简到 <12 词，详细信息放在 SKILL.md 正文",
            })
            score -= 0.2

    # Frontmatter check
    missing_fm = [s for s in skills if not s.get("has_frontmatter")]
    if missing_fm:
        findings.append({
            "severity": "warning",
            "code": "A3-FM",
            "title": f"{len(missing_fm)} 个 skill 缺少 YAML frontmatter",
            "detail": ", ".join(s["name"] for s in missing_fm[:5]),
            "fix": "为每个 skill 添加 name/description/version frontmatter",
        })
        score -= min(2.0, len(missing_fm) * 0.3)

    # Overlap check
    overlaps = _find_overlapping_skills(skills)
    for name1, name2, _, _ in overlaps:
        findings.append({
            "severity": "warning",
            "code": "A3-OVERLAP",
            "title": f"Skills '{name1}' 和 '{name2}' 描述重叠",
            "detail": "职责重叠可能导致匹配混淆",
            "fix": "合并或明确区分两个 skill 的职责",
        })
        score -= 0.5

    # disable-model-invocation check (standard+)
    if tier != "simple":
        no_disable = [
            s for s in skills
            if not s.get("disable_model_invocation") and s.get("has_frontmatter")
        ]
        if len(no_disable) > 10:
            findings.append({
                "severity": "info",
                "code": "A3-DISABLE",
                "title": f"{len(no_disable)} 个 skill 未设置 disable-model-invocation",
                "detail": "低频 skills 建议设置 disable-model-invocation: true",
                "fix": "为低频 skills 添加 disable-model-invocation: true",
            })
            score -= 0.5

    score = max(0.0, min(10.0, score))
    return {
        "dimension": "D3 Agents",
        "score": round(score, 1),
        "max_score": 10.0,
        "findings": findings,
    }
