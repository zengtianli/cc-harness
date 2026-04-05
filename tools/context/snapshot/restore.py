"""Read and display saved snapshots."""

from pathlib import Path
from typing import Optional


def find_snapshots(snapshot_dir: Optional[Path] = None) -> list[Path]:
    """Find all saved snapshots, newest first."""
    if snapshot_dir is None:
        snapshot_dir = Path.home() / ".claude" / "snapshots"
    if not snapshot_dir.exists():
        return []
    paths = list(snapshot_dir.glob("*.md"))
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)


def read_snapshot(path: Path) -> str:
    """Read a snapshot file and return its contents."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return f"Error: cannot read {path}"


def restore_latest(snapshot_dir: Optional[Path] = None) -> str:
    """Read the most recent snapshot."""
    snapshots = find_snapshots(snapshot_dir)
    if not snapshots:
        return "No snapshots found."
    return read_snapshot(snapshots[0])
