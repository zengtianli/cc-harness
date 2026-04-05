"""Tests for health module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from monitor.parser import parse_session
from health.session_check import check_session_health, format_health_report
from health.patterns import detect_patterns, format_pattern_report

FIXTURE = Path(__file__).parent / "fixtures" / "sample_session.jsonl"


class TestSessionCheck(unittest.TestCase):
    def setUp(self):
        self.session = parse_session(FIXTURE)
        self.report = check_session_health(self.session)

    def test_report_has_score(self):
        self.assertGreaterEqual(self.report.score, 0)
        self.assertLessEqual(self.report.score, 100)

    def test_detects_repeated_reads(self):
        # The fixture has main.py read 5 times (>3 threshold)
        read_warnings = [w for w in self.report.warnings if "read" in w.lower() and "times" in w.lower()]
        self.assertGreater(len(read_warnings), 0, "Should detect repeated file reads")

    def test_format_report(self):
        text = format_health_report(self.report, self.session)
        self.assertIn("test-session-001", text)
        self.assertIn("Health", text)

    def test_info_has_totals(self):
        info_text = " ".join(self.report.info)
        self.assertIn("tokens", info_text.lower())


class TestPatterns(unittest.TestCase):
    def setUp(self):
        self.session = parse_session(FIXTURE)
        self.report = detect_patterns(self.session)

    def test_detects_repeated_grep(self):
        # The fixture has "TODO" grep 3 times
        grep_patterns = [p for p in self.report.patterns if "Grep" in p]
        self.assertGreater(len(grep_patterns), 0, "Should detect repeated grep patterns")

    def test_detects_large_reads(self):
        # The fixture has many reads without offset/limit
        read_patterns = [p for p in self.report.patterns if "offset/limit" in p]
        self.assertGreater(len(read_patterns), 0, "Should detect reads without offset/limit")

    def test_format_report(self):
        text = format_pattern_report(self.report)
        self.assertIn("Anti-pattern", text)

    def test_empty_report(self):
        from health.patterns import PatternReport
        empty = PatternReport()
        text = format_pattern_report(empty)
        self.assertIn("No anti-patterns", text)


if __name__ == "__main__":
    unittest.main()
