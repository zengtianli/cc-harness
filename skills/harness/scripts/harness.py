#!/usr/bin/env python3
"""Harness: CC skill distribution manager."""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".claude" / "harness.yaml"
GLOBAL_SKILLS_DIR = Path.home() / ".claude" / "skills"


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


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def hash_skill(skill_dir: Path) -> dict[str, str]:
    """Return {relative_path: short_sha256} for all files."""
    result = {}
    if not skill_dir.exists():
        return result
    for f in sorted(skill_dir.rglob("*")):
        if f.is_file():
            result[str(f.relative_to(skill_dir))] = hash_file(f)
    return result


def compare_skill(source: Path, target: Path) -> tuple[str, list[str]]:
    """Return (status, details). Status: 'synced' | 'missing' | 'drifted'."""
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


# ── Commands ──────────────────────────────────────────


def cmd_status(cfg: dict):
    source = cfg["source"]
    synced = drifted = missing = 0

    print("Harness Status")
    print("=" * 52)

    # Global skills
    print(f"\nGlobal Skills (→ ~/.claude/skills/)")
    for name in cfg.get("global_skills", []):
        src = source / name
        tgt = GLOBAL_SKILLS_DIR / name
        status, details = compare_skill(src, tgt)
        sym = {"synced": "✓", "missing": "✗", "drifted": "⚠"}[status]
        suffix = ""
        if details:
            suffix = f"  ({', '.join(details[:3])})"
        print(f"  {sym} {name:<22} {status}{suffix}")
        if status == "synced":
            synced += 1
        elif status == "missing":
            missing += 1
        else:
            drifted += 1

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
            sym = {"synced": "✓", "missing": "✗", "drifted": "⚠"}[status]
            suffix = ""
            if details:
                suffix = f"  ({', '.join(details[:3])})"
            print(f"      {sym} {name:<22} {status}{suffix}")
            if status == "synced":
                synced += 1
            elif status == "missing":
                missing += 1
            else:
                drifted += 1

    # Standalone
    standalone = cfg.get("standalone", [])
    if standalone:
        print(f"\nStandalone (stays in zdwp)")
        for name in standalone:
            src = source / name
            exists = "✓" if src.exists() else "✗"
            print(f"  {exists} {name}")

    print(f"\nSummary: {synced} synced, {drifted} drifted, {missing} missing")


def cmd_sync(cfg: dict, force: bool = False, dry_run: bool = False):
    source = cfg["source"]
    actions = []

    # Global skills
    for name in cfg.get("global_skills", []):
        src = source / name
        tgt = GLOBAL_SKILLS_DIR / name
        if not src.exists():
            print(f"⚠ Source missing: {src}")
            continue
        status, details = compare_skill(src, tgt)
        if status == "synced":
            continue
        if status == "drifted" and not force:
            print(f"⚠ {name} drifted at {tgt}, skipping (use --force)")
            continue
        actions.append((name, src, tgt, status))

    # Project skills
    for proj_name, proj in cfg.get("projects", {}).items():
        proj_path = proj["path"]
        if not proj_path.exists():
            print(f"⚠ Project dir missing: {proj_path}")
            continue
        for name in proj.get("skills", []):
            src = source / name
            tgt = proj_path / ".claude" / "skills" / name
            if not src.exists():
                print(f"⚠ Source missing: {src}")
                continue
            status, details = compare_skill(src, tgt)
            if status == "synced":
                continue
            if status == "drifted" and not force:
                print(f"⚠ {name} drifted at {tgt}, skipping (use --force)")
                continue
            actions.append((name, src, tgt, status))

    if not actions:
        print("All skills in sync.")
        return

    # Execute
    for name, src, tgt, status in actions:
        label = "overwrite" if status == "drifted" else "copy"
        tgt_short = str(tgt).replace(str(Path.home()), "~")
        if dry_run:
            print(f"  [dry-run] {label} {name} → {tgt_short}")
        else:
            copy_skill(src, tgt)
            print(f"  ✓ {label} {name} → {tgt_short}")

    if dry_run:
        print(f"\n{len(actions)} action(s) planned. Run without --dry-run to execute.")
    else:
        print(f"\n{len(actions)} skill(s) synced.")


def cmd_init(cfg: dict, project_path: str):
    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        print(f"✗ Path not found: {path}")
        sys.exit(1)

    skills_dir = path / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ {skills_dir}")

    settings = path / ".claude" / "settings.json"
    if not settings.exists():
        settings.write_text(json.dumps({"hooks": {}}, indent=2) + "\n")
        print(f"✓ {settings}")

    # Find matching project in registry
    source = cfg["source"]
    matched = None
    for proj_name, proj in cfg.get("projects", {}).items():
        if proj["path"].resolve() == path:
            matched = proj
            break

    if matched:
        for name in matched.get("skills", []):
            src = source / name
            tgt = skills_dir / name
            if src.exists():
                copy_skill(src, tgt)
                print(f"✓ {name}")
            else:
                print(f"⚠ Source missing: {src}")
    else:
        print(f"  (no skills registered for this project)")

    print(f"\nDone. Project initialized at {path}")


# ── Main ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Harness: CC skill distribution")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show sync status")

    p_sync = sub.add_parser("sync", help="Sync skills to targets")
    p_sync.add_argument("--force", action="store_true", help="Overwrite drifted skills")
    p_sync.add_argument("--dry-run", action="store_true", help="Preview only")

    p_init = sub.add_parser("init", help="Initialize project .claude/")
    p_init.add_argument("path", help="Project directory path")

    args = parser.parse_args()
    cfg = load_config()

    if args.cmd == "status":
        cmd_status(cfg)
    elif args.cmd == "sync":
        cmd_sync(cfg, force=args.force, dry_run=args.dry_run)
    elif args.cmd == "init":
        cmd_init(cfg, args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
