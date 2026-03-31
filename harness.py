#!/usr/bin/env python3
"""cc-harness: Claude Code configuration quality auditor.

Audits a project's Claude Code setup (CLAUDE.md, skills, hooks, rules, etc.)
and outputs a six-dimension score card + findings report.
"""

import argparse
import json
import sys
from pathlib import Path

from collectors.config import collect_config
from collectors.skills import collect_skills
from collectors.hooks import collect_hooks
from collectors.metrics import collect_metrics
from analyzers.context import analyze_context
from analyzers.hooks import analyze_hooks
from analyzers.agents import analyze_agents
from analyzers.verification import analyze_verification
from analyzers.session import analyze_session
from analyzers.structure import analyze_structure
from security.scanner import scan_security
from reporters.scorecard import render_scorecard
from reporters.markdown import render_markdown_report


def detect_tier(metrics: dict) -> str:
    """Detect project tier based on metrics."""
    sf = metrics.get("source_files", 0)
    ct = metrics.get("contributors", 0)
    ci = metrics.get("ci_workflows", 0)
    if sf < 500 and ct <= 1 and ci == 0:
        return "simple"
    elif sf > 5000 and ct > 3 and ci > 0:
        return "complex"
    else:
        return "standard"


def run_audit(project_path: Path, claude_home: Path) -> dict:
    """Run the full audit pipeline and return results."""
    # Step 1: Collect data
    config_data = collect_config(project_path, claude_home)
    skills_data = collect_skills(project_path, claude_home)
    hooks_data = collect_hooks(project_path)
    metrics_data = collect_metrics(project_path, claude_home)

    # Step 2: Detect tier
    tier = detect_tier(metrics_data)

    # Step 3: Analyze each dimension
    d1 = analyze_context(config_data, metrics_data, tier)
    d2 = analyze_hooks(hooks_data, config_data, tier)
    d3 = analyze_agents(skills_data, tier)
    d4 = analyze_verification(config_data, metrics_data, tier)
    d5 = analyze_session(config_data, tier)
    d6 = analyze_structure(config_data, skills_data, tier)

    # Step 4: Security scan
    security_findings = scan_security(skills_data, config_data)

    return {
        "project_path": str(project_path),
        "tier": tier,
        "metrics": metrics_data,
        "dimensions": [d1, d2, d3, d4, d5, d6],
        "security": security_findings,
        "config": config_data,
        "skills": skills_data,
        "hooks": hooks_data,
    }


def main():
    parser = argparse.ArgumentParser(
        description="cc-harness: Claude Code configuration quality auditor"
    )
    parser.add_argument(
        "project_path",
        type=str,
        help="Path to the project to audit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--security-only",
        action="store_true",
        help="Run security scan only",
    )
    parser.add_argument(
        "--claude-home",
        type=str,
        default=None,
        help="Custom Claude home directory (default: ~/.claude)",
    )

    args = parser.parse_args()

    project_path = Path(args.project_path).expanduser().resolve()
    if not project_path.is_dir():
        print(f"Error: {project_path} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    claude_home = Path(args.claude_home).expanduser().resolve() if args.claude_home else Path.home() / ".claude"

    if args.security_only:
        skills_data = collect_skills(project_path, claude_home)
        config_data = collect_config(project_path, claude_home)
        security_findings = scan_security(skills_data, config_data)
        if args.json_output:
            print(json.dumps(security_findings, indent=2, ensure_ascii=False))
        else:
            for f in security_findings:
                severity = f.get("severity", "info")
                icon = {"critical": "\U0001f534", "warning": "\U0001f7e1", "info": "\U0001f7e2"}.get(severity, "")
                print(f"{icon} [{f['category']}] {f['title']}")
                if f.get("detail"):
                    print(f"   {f['detail']}")
        sys.exit(0)

    results = run_audit(project_path, claude_home)

    if args.json_output:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    else:
        report = render_markdown_report(results)
        print(report)


if __name__ == "__main__":
    main()
