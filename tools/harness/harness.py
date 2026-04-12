#!/usr/bin/env python3
"""cc-configs harness: Claude Code configuration auditor + skill distribution manager.

Subcommands:
  audit   <path>       Six-dimension quality audit of a project's CC setup
  status               Show skill sync status across all registered projects
  sync   [--force]     Sync skills from repo to targets
  init   <path>        Bootstrap .claude/ for a project
"""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml

REPO_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_DIR / "harness.yaml"
GLOBAL_SKILLS_DIR = Path.home() / ".claude" / "skills"


# ── Config ────────────────────────────────────────────


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"✗ Config not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    cfg["source"] = Path(cfg["source"]).expanduser()
    for proj in cfg.get("projects", {}).values():
        proj["path"] = Path(proj["path"]).expanduser()
    return cfg


# ── Hash / Compare ────────────────────────────────────


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def hash_skill(skill_dir: Path) -> dict[str, str]:
    result = {}
    if not skill_dir.exists():
        return result
    for f in sorted(skill_dir.rglob("*")):
        if f.is_file():
            result[str(f.relative_to(skill_dir))] = hash_file(f)
    return result


def compare_skill(source: Path, target: Path) -> tuple[str, list[str]]:
    if not target.exists():
        return "missing", []
    src_hashes = hash_skill(source)
    tgt_hashes = hash_skill(target)
    drifted = []
    for rel, src_h in src_hashes.items():
        tgt_h = tgt_hashes.get(rel)
        if tgt_h is None:
            drifted.append(f"+{rel}")
        elif tgt_h != src_h:
            drifted.append(rel)
    if drifted:
        return "drifted", drifted
    return "synced", []


def copy_skill(source: Path, target: Path):
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)


# ── Subcommand: status ────────────────────────────────


def cmd_status(cfg: dict):
    source = cfg["source"]
    synced = drifted = missing = 0
    SYM = {"synced": "✓", "missing": "✗", "drifted": "⚠"}

    print("Harness Status")
    print("=" * 52)

    # Global skills — if ~/.claude/skills is a symlink to repo, they're always synced
    global_dir = GLOBAL_SKILLS_DIR
    is_symlinked = global_dir.is_symlink()
    print(f"\nGlobal Skills (→ ~/.claude/skills/){' [symlinked]' if is_symlinked else ''}")
    for name in cfg.get("global_skills", []):
        src = source / name
        tgt = global_dir / name
        if is_symlinked:
            exists = "✓" if tgt.exists() else "✗"
            print(f"  {exists} {name:<22} {'present' if tgt.exists() else 'missing'}")
            if tgt.exists():
                synced += 1
            else:
                missing += 1
        else:
            status, details = compare_skill(src, tgt)
            suffix = f"  ({', '.join(details[:3])})" if details else ""
            print(f"  {SYM[status]} {name:<22} {status}{suffix}")
            if status == "synced": synced += 1
            elif status == "missing": missing += 1
            else: drifted += 1

    # Project skills
    print(f"\nProject Skills")
    for proj_name, proj in cfg.get("projects", {}).items():
        proj_path = proj["path"]
        exists = "✓" if proj_path.exists() else "✗"
        print(f"  {exists} {proj_name:<14} {proj_path}")
        for name in proj.get("skills", []):
            src = source / name
            tgt = proj_path / ".claude" / "skills" / name
            status, details = compare_skill(src, tgt)
            suffix = f"  ({', '.join(details[:3])})" if details else ""
            print(f"      {SYM[status]} {name:<22} {status}{suffix}")
            if status == "synced": synced += 1
            elif status == "missing": missing += 1
            else: drifted += 1

    # Standalone
    standalone = cfg.get("standalone", [])
    if standalone:
        print(f"\nStandalone (in source only)")
        for name in standalone:
            exists = "✓" if (source / name).exists() else "✗"
            print(f"  {exists} {name}")

    print(f"\nSummary: {synced} synced, {drifted} drifted, {missing} missing")


# ── Subcommand: sync ──────────────────────────────────


def cmd_sync(cfg: dict, force: bool = False, dry_run: bool = False):
    source = cfg["source"]
    actions = []

    # If global skills dir is symlinked, skip global sync
    if GLOBAL_SKILLS_DIR.is_symlink():
        print("Global skills: symlinked, skipping.")
    else:
        for name in cfg.get("global_skills", []):
            src = source / name
            tgt = GLOBAL_SKILLS_DIR / name
            if not src.exists():
                print(f"⚠ Source missing: {src}")
                continue
            status, _ = compare_skill(src, tgt)
            if status == "synced":
                continue
            if status == "drifted" and not force:
                print(f"⚠ {name} drifted, skipping (use --force)")
                continue
            actions.append((name, src, tgt, status))

    # Project skills
    for proj_name, proj in cfg.get("projects", {}).items():
        proj_path = proj["path"]
        if not proj_path.exists():
            print(f"⚠ Project missing: {proj_path}")
            continue
        for name in proj.get("skills", []):
            src = source / name
            tgt = proj_path / ".claude" / "skills" / name
            if not src.exists():
                print(f"⚠ Source missing: {src}")
                continue
            status, _ = compare_skill(src, tgt)
            if status == "synced":
                continue
            if status == "drifted" and not force:
                print(f"⚠ {name} drifted at {proj_name}, skipping (use --force)")
                continue
            actions.append((name, src, tgt, status))

    if not actions:
        print("All skills in sync.")
        return

    for name, src, tgt, status in actions:
        label = "overwrite" if status == "drifted" else "copy"
        tgt_short = str(tgt).replace(str(Path.home()), "~")
        if dry_run:
            print(f"  [dry-run] {label} {name} → {tgt_short}")
        else:
            copy_skill(src, tgt)
            print(f"  ✓ {label} {name} → {tgt_short}")

    if dry_run:
        print(f"\n{len(actions)} action(s) planned.")
    else:
        print(f"\n{len(actions)} skill(s) synced.")


# ── Subcommand: init ──────────────────────────────────


def cmd_init(cfg: dict, project_path: str):
    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        print(f"✗ Path not found: {path}")
        sys.exit(1)

    skills_dir = path / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ .claude/skills/")

    settings = path / ".claude" / "settings.json"
    if not settings.exists():
        settings.write_text(json.dumps({"hooks": {}}, indent=2) + "\n")
        print(f"✓ .claude/settings.json")

    # Find matching project
    source = cfg["source"]
    matched = None
    matched_name = None
    for proj_name, proj in cfg.get("projects", {}).items():
        if proj["path"].resolve() == path:
            matched = proj
            matched_name = proj_name
            break

    if matched:
        for name in matched.get("skills", []):
            src = source / name
            tgt = skills_dir / name
            if src.exists():
                copy_skill(src, tgt)
                print(f"✓ skill: {name}")
            else:
                print(f"⚠ Source missing: {src}")
        print(f"\nDone. {matched_name} initialized with {len(matched.get('skills', []))} skill(s).")
    else:
        print(f"\n  (no skills registered for {path})")
        print(f"  Add it to harness.yaml to assign skills.")


# ── Subcommand: audit ─────────────────────────────────


def cmd_audit(project_path: str, claude_home: str = None, json_output: bool = False, security_only: bool = False):
    """Delegate to the existing audit pipeline."""
    # Import audit modules (relative to repo root)
    sys.path.insert(0, str(REPO_DIR))
    try:
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
        from reporters.markdown import render_markdown_report
    except ImportError as e:
        print(f"✗ Audit modules not found: {e}")
        print("  Run from repo root or check analyzers/collectors dirs.")
        sys.exit(1)

    path = Path(project_path).expanduser().resolve()
    if not path.is_dir():
        print(f"✗ Not a valid directory: {path}", file=sys.stderr)
        sys.exit(1)

    ch = Path(claude_home).expanduser().resolve() if claude_home else Path.home() / ".claude"

    if security_only:
        skills_data = collect_skills(path, ch)
        config_data = collect_config(path, ch)
        findings = scan_security(skills_data, config_data)
        if json_output:
            print(json.dumps(findings, indent=2, ensure_ascii=False))
        else:
            for f in findings:
                sev = f.get("severity", "info")
                icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(sev, "")
                print(f"{icon} [{f['category']}] {f['title']}")
                if f.get("detail"):
                    print(f"   {f['detail']}")
        return

    config_data = collect_config(path, ch)
    skills_data = collect_skills(path, ch)
    hooks_data = collect_hooks(path)
    metrics_data = collect_metrics(path, ch)

    sf = metrics_data.get("source_files", 0)
    ct = metrics_data.get("contributors", 0)
    ci = metrics_data.get("ci_workflows", 0)
    tier = "simple" if sf < 500 and ct <= 1 and ci == 0 else "complex" if sf > 5000 and ct > 3 and ci > 0 else "standard"

    results = {
        "project_path": str(path), "tier": tier, "metrics": metrics_data,
        "dimensions": [
            analyze_context(config_data, metrics_data, tier),
            analyze_hooks(hooks_data, config_data, tier),
            analyze_agents(skills_data, tier),
            analyze_verification(config_data, metrics_data, tier),
            analyze_session(config_data, tier),
            analyze_structure(config_data, skills_data, tier),
        ],
        "security": scan_security(skills_data, config_data),
        "config": config_data, "skills": skills_data, "hooks": hooks_data,
    }

    if json_output:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_markdown_report(results))


# ── Main ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="cc-configs harness: CC config auditor + skill distribution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    # status
    sub.add_parser("status", help="Show skill sync status")

    # sync
    p_sync = sub.add_parser("sync", help="Sync skills to targets")
    p_sync.add_argument("--force", action="store_true")
    p_sync.add_argument("--dry-run", action="store_true")

    # init
    p_init = sub.add_parser("init", help="Initialize project .claude/")
    p_init.add_argument("path", help="Project directory path")

    # audit
    p_audit = sub.add_parser("audit", help="Audit project CC setup")
    p_audit.add_argument("path", help="Project to audit")
    p_audit.add_argument("--json", action="store_true", dest="json_output")
    p_audit.add_argument("--security-only", action="store_true")
    p_audit.add_argument("--claude-home", type=str, default=None)

    args = parser.parse_args()

    if args.cmd == "status":
        cmd_status(load_config())
    elif args.cmd == "sync":
        cmd_sync(load_config(), force=args.force, dry_run=args.dry_run)
    elif args.cmd == "init":
        cmd_init(load_config(), args.path)
    elif args.cmd == "audit":
        cmd_audit(args.path, claude_home=args.claude_home, json_output=args.json_output, security_only=args.security_only)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
