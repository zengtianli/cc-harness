"""Output markdown report (Critical/Structural/Incremental)."""

from datetime import date

from reporters.scorecard import render_scorecard


def _render_metrics(results: dict) -> str:
    """Render project metrics section."""
    metrics = results.get("metrics", {})
    tier = results.get("tier", "unknown")
    project_path = results.get("project_path", "")

    lines = [
        "# Claude Code 配置审计报告",
        "",
        f"**项目**: {project_path}",
        f"**日期**: {date.today().isoformat()}",
        f"**工具**: cc-harness v0.1.0",
        "",
        "## 项目分级判定",
        "",
        "| 指标 | 实际值 |",
        "|------|--------|",
        f"| 源代码文件数 | {metrics.get('source_files', 0)} |",
        f"| 贡献者数 | {metrics.get('contributors', 0)} |",
        f"| CI 工作流 | {metrics.get('ci_workflows', 0)} |",
        f"| 启动 Token 预算 | {metrics.get('startup_tokens', 0)} |",
        f"| 会话文件数 | {metrics.get('conversation_count', 0)} |",
        "",
        f"**判定结果: {tier.upper()} 级别**",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def _severity_icon(severity: str) -> str:
    icons = {
        "critical": "\U0001f534",
        "warning": "\U0001f7e1",
        "info": "\U0001f7e2",
    }
    return icons.get(severity, "")


def _render_findings_section(title: str, findings: list) -> str:
    """Render a findings section."""
    if not findings:
        return ""
    lines = [title, ""]
    for f in findings:
        icon = _severity_icon(f.get("severity", "info"))
        code = f.get("code", "")
        lines.append(f"#### {icon} {code} {f['title']}")
        if f.get("detail"):
            lines.append(f"\n{f['detail']}\n")
        if f.get("fix"):
            lines.append(f"**修复**: {f['fix']}\n")
    return "\n".join(lines)


def _render_security(security: list) -> str:
    """Render security findings."""
    if not security:
        return "\n## 安全扫描\n\n未发现安全问题。\n"

    lines = ["\n## 安全扫描\n"]
    for f in security:
        icon = _severity_icon(f.get("severity", "info"))
        lines.append(f"- {icon} **[{f['category']}]** {f['title']}: {f.get('detail', '')}")
    lines.append("")
    return "\n".join(lines)


def render_markdown_report(results: dict) -> str:
    """Render full markdown audit report."""
    parts = []

    # Metrics
    parts.append(_render_metrics(results))

    # Collect all findings by severity
    critical = []
    structural = []
    incremental = []

    for dim in results.get("dimensions", []):
        for f in dim.get("findings", []):
            f_copy = dict(f)
            f_copy["dimension"] = dim["dimension"]
            if f["severity"] == "critical":
                critical.append(f_copy)
            elif f["severity"] == "warning":
                structural.append(f_copy)
            else:
                incremental.append(f_copy)

    # Security findings are always critical
    for sf in results.get("security", []):
        critical.append(sf)

    # Render sections
    parts.append(_render_findings_section(
        "## \U0001f534 Critical -- 立即修复", critical
    ))
    parts.append(_render_findings_section(
        "## \U0001f7e1 Structural -- 尽快修复", structural
    ))
    parts.append(_render_findings_section(
        "## \U0001f7e2 Incremental -- 可选改进", incremental
    ))

    # Security summary
    parts.append(_render_security(results.get("security", [])))

    # Score card
    parts.append("---\n")
    parts.append(render_scorecard(results))

    # Roadmap
    parts.append(_render_roadmap(critical, structural, incremental))

    return "\n".join(p for p in parts if p)


def _render_roadmap(critical: list, structural: list, incremental: list) -> str:
    """Render fix roadmap."""
    lines = ["## 修复优先级路线图\n"]

    if critical:
        lines.append("### Phase 1: 立即")
        for i, f in enumerate(critical, 1):
            lines.append(f"{i}. **{f.get('code', '')}** {f['title']}")
        lines.append("")

    if structural:
        lines.append("### Phase 2: 本周")
        for i, f in enumerate(structural, 1):
            lines.append(f"{i}. **{f.get('code', '')}** {f['title']}")
        lines.append("")

    if incremental:
        lines.append("### Phase 3: 本月")
        for i, f in enumerate(incremental, 1):
            lines.append(f"{i}. **{f.get('code', '')}** {f['title']}")
        lines.append("")

    return "\n".join(lines)
