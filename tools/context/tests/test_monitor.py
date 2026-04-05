"""Tests for monitor module."""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitor.parser import parse_session, SKIP_TYPES
from monitor.token_stats import compute_token_stats, format_token_stats
from monitor.cost_tracker import estimate_cost, PRICING

FIXTURE = Path(__file__).parent / "fixtures" / "sample_session.jsonl"


class TestParser(unittest.TestCase):
    def test_parse_session_basic(self):
        session = parse_session(FIXTURE)
        self.assertEqual(session.session_id, "test-session-001")
        self.assertEqual(session.model, "claude-sonnet-4-6")
        self.assertEqual(session.project_path, "/Users/test/project")
        self.assertEqual(session.git_branch, "main")
        self.assertEqual(session.slug, "test-slug")

    def test_skips_types(self):
        session = parse_session(FIXTURE)
        for msg in session.messages:
            self.assertNotIn(msg.get("type"), SKIP_TYPES)

    def test_timestamps(self):
        session = parse_session(FIXTURE)
        self.assertIsNotNone(session.start_time)
        self.assertIsNotNone(session.end_time)
        self.assertLessEqual(session.start_time, session.end_time)

    def test_nonexistent_file(self):
        session = parse_session(Path("/nonexistent/file.jsonl"))
        self.assertEqual(session.messages, [])

    def test_messages_not_empty(self):
        session = parse_session(FIXTURE)
        self.assertGreater(len(session.messages), 0)


class TestTokenStats(unittest.TestCase):
    def setUp(self):
        self.session = parse_session(FIXTURE)
        self.summary = compute_token_stats(self.session)

    def test_tokens_accumulated(self):
        self.assertGreater(self.summary.input_tokens, 0)
        self.assertGreater(self.summary.output_tokens, 0)
        self.assertGreater(self.summary.cache_read_tokens, 0)

    def test_tool_calls_counted(self):
        self.assertIn("Read", self.summary.tool_calls)
        self.assertIn("Edit", self.summary.tool_calls)
        self.assertIn("Bash", self.summary.tool_calls)
        self.assertIn("Grep", self.summary.tool_calls)
        self.assertIn("Write", self.summary.tool_calls)

    def test_cache_hit_rate(self):
        rate = self.summary.cache_hit_rate
        self.assertGreaterEqual(rate, 0.0)
        self.assertLessEqual(rate, 1.0)

    def test_total_tokens(self):
        self.assertEqual(
            self.summary.total_tokens,
            self.summary.input_tokens + self.summary.output_tokens,
        )

    def test_format_output(self):
        text = format_token_stats(self.summary, self.session)
        self.assertIn("Token", text)
        self.assertIn("Tool", text)
        self.assertIn("Read", text)

    def test_user_turns(self):
        # Should only count non-tool-result user messages
        self.assertGreater(self.summary.user_turns, 0)


class TestCostTracker(unittest.TestCase):
    def test_estimate_cost_known_model(self):
        from monitor.token_stats import TokenSummary
        summary = TokenSummary(
            input_tokens=1_000_000,
            output_tokens=100_000,
            cache_read_tokens=500_000,
            cache_creation_tokens=200_000,
        )
        cost = estimate_cost(summary, "claude-sonnet-4-6")
        self.assertAlmostEqual(cost["input"], 3.0)
        self.assertAlmostEqual(cost["output"], 1.5)
        self.assertAlmostEqual(cost["cache_read"], 0.15)
        self.assertGreater(cost["total"], 0)

    def test_estimate_cost_unknown_model(self):
        from monitor.token_stats import TokenSummary
        summary = TokenSummary(input_tokens=1000)
        cost = estimate_cost(summary, "unknown-model")
        self.assertGreater(cost["total"], 0)

    def test_pricing_has_required_models(self):
        self.assertIn("claude-opus-4-6", PRICING)
        self.assertIn("claude-sonnet-4-6", PRICING)
        self.assertIn("claude-haiku-4-5", PRICING)


if __name__ == "__main__":
    unittest.main()
