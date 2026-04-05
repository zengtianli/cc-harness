"""Tests for snapshot module."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from monitor.parser import parse_session
from monitor.token_stats import compute_token_stats
from snapshot.auto_save import extract_modified_files, build_snapshot_markdown, save_snapshot
from snapshot.restore import find_snapshots, restore_latest

FIXTURE = Path(__file__).parent / "fixtures" / "sample_session.jsonl"


class TestAutoSave(unittest.TestCase):
    def setUp(self):
        self.session = parse_session(FIXTURE)
        self.summary = compute_token_stats(self.session)

    def test_extract_modified_files(self):
        files = extract_modified_files(self.session)
        self.assertIn("/Users/test/project/main.py", files)
        self.assertIn("/Users/test/project/TODOS.md", files)

    def test_no_duplicate_files(self):
        files = extract_modified_files(self.session)
        self.assertEqual(len(files), len(set(files)))

    def test_build_snapshot_markdown(self):
        files = extract_modified_files(self.session)
        md = build_snapshot_markdown(self.session, self.summary, files)
        self.assertIn("test-session-001", md)
        self.assertIn("Token", md)
        self.assertIn("Tool", md)
        self.assertIn("Modified Files", md)
        self.assertIn("main.py", md)

    def test_save_snapshot_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = save_snapshot(self.session, Path(tmpdir))
            self.assertTrue(out.exists())
            content = out.read_text()
            self.assertIn("test-session-001", content)


class TestRestore(unittest.TestCase):
    def test_find_snapshots_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshots = find_snapshots(Path(tmpdir))
            self.assertEqual(snapshots, [])

    def test_restore_latest_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = restore_latest(Path(tmpdir))
            self.assertIn("No snapshots", result)

    def test_save_and_restore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = parse_session(FIXTURE)
            save_snapshot(session, Path(tmpdir))
            snapshots = find_snapshots(Path(tmpdir))
            self.assertEqual(len(snapshots), 1)


if __name__ == "__main__":
    unittest.main()
