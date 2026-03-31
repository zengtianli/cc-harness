"""Tests for analyzers."""

import unittest

from analyzers.context import analyze_context, _find_duplicates, _check_credentials
from analyzers.hooks import analyze_hooks
from analyzers.agents import analyze_agents, _find_overlapping_skills
from analyzers.verification import analyze_verification, _has_verification_section
from analyzers.session import analyze_session
from analyzers.structure import analyze_structure


class TestContextAnalyzer(unittest.TestCase):

    def test_missing_claude_md(self):
        config = {"local_claude_md": "", "global_claude_md": "", "nested_claude_mds": []}
        metrics = {"startup_tokens": 0, "conversation_count": 0}
        result = analyze_context(config, metrics, "standard")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("C1-MISSING", codes)
        self.assertLess(result["score"], 10.0)

    def test_high_token_budget(self):
        config = {"local_claude_md": "x", "global_claude_md": "", "nested_claude_mds": []}
        metrics = {"startup_tokens": 35000, "conversation_count": 0}
        result = analyze_context(config, metrics, "standard")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("C1-BUDGET", codes)

    def test_nested_claude_mds(self):
        config = {
            "local_claude_md": "ok",
            "global_claude_md": "",
            "nested_claude_mds": ["/a/CLAUDE.md", "/b/CLAUDE.md"],
        }
        metrics = {"startup_tokens": 100, "conversation_count": 0}
        result = analyze_context(config, metrics, "standard")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("C1-NESTED", codes)

    def test_hardcoded_credentials(self):
        findings = _check_credentials(
            'api_key="skabcdef1234567890abcdef"', "test"
        )
        self.assertTrue(len(findings) > 0)
        self.assertEqual(findings[0]["code"], "C1-CRED")

    def test_no_credentials(self):
        findings = _check_credentials("# Just a comment\nno secrets here", "test")
        self.assertEqual(len(findings), 0)

    def test_find_duplicates(self):
        global_md = "- NEVER commit .env files to git\n- ALWAYS use type hints"
        local_md = "- NEVER commit .env files to the repo\n- Use Python 3.11"
        dups = _find_duplicates(global_md, local_md)
        self.assertGreater(len(dups), 0)

    def test_memory_md_missing_high_conversations(self):
        config = {"local_claude_md": "x", "global_claude_md": "", "nested_claude_mds": []}
        metrics = {"startup_tokens": 100, "conversation_count": 15}
        result = analyze_context(config, metrics, "standard")
        mem_findings = [f for f in result["findings"] if f["code"] == "C1-MEMORY"]
        self.assertTrue(len(mem_findings) > 0)
        self.assertEqual(mem_findings[0]["severity"], "critical")


class TestHooksAnalyzer(unittest.TestCase):

    def test_simple_tier_no_hooks(self):
        hooks_data = {"has_settings": False, "hook_entries": [], "schema_issues": [], "event_types": []}
        config = {}
        result = analyze_hooks(hooks_data, config, "simple")
        self.assertGreaterEqual(result["score"], 7.0)

    def test_standard_no_hooks(self):
        hooks_data = {"has_settings": False, "hook_entries": [], "schema_issues": [], "event_types": []}
        config = {}
        result = analyze_hooks(hooks_data, config, "standard")
        self.assertLess(result["score"], 8.0)
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("H2-MISSING", codes)

    def test_standard_with_hooks(self):
        hooks_data = {
            "has_settings": True,
            "hook_entries": [{"event": "PostToolUse", "matcher": "Edit", "command": "echo ok | head -5 || echo FAILED", "command_issues": []}],
            "schema_issues": [],
            "event_types": ["PostToolUse"],
        }
        config = {}
        result = analyze_hooks(hooks_data, config, "standard")
        self.assertGreaterEqual(result["score"], 9.0)


class TestAgentsAnalyzer(unittest.TestCase):

    def test_simple_no_skills(self):
        result = analyze_agents([], "simple")
        self.assertGreaterEqual(result["score"], 8.0)

    def test_too_many_skills(self):
        skills = [
            {"name": f"skill-{i}", "description": f"Desc {i}", "path": f"/s/{i}",
             "has_frontmatter": True, "disable_model_invocation": False}
            for i in range(25)
        ]
        result = analyze_agents(skills, "standard")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("A3-COUNT", codes)

    def test_missing_frontmatter(self):
        skills = [
            {"name": "no-fm", "description": "test", "path": "/s/no-fm",
             "has_frontmatter": False, "disable_model_invocation": False}
        ]
        result = analyze_agents(skills, "standard")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("A3-FM", codes)

    def test_overlapping_skills(self):
        skills = [
            {"name": "a", "description": "Deploy the application to production server"},
            {"name": "b", "description": "Deploy the application to production environment"},
        ]
        overlaps = _find_overlapping_skills(skills)
        self.assertGreater(len(overlaps), 0)


class TestVerificationAnalyzer(unittest.TestCase):

    def test_has_verification_section(self):
        self.assertTrue(_has_verification_section("## Verification\n- run tests"))
        self.assertTrue(_has_verification_section("## 验证规则\n- pytest"))
        self.assertFalse(_has_verification_section("# No verify here"))

    def test_simple_tier(self):
        config = {"local_claude_md": "# Simple\nJust basics", "global_claude_md": ""}
        metrics = {}
        result = analyze_verification(config, metrics, "simple")
        self.assertGreaterEqual(result["score"], 8.0)

    def test_standard_missing_verification(self):
        config = {"local_claude_md": "# No verify section", "global_claude_md": ""}
        metrics = {}
        result = analyze_verification(config, metrics, "standard")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("V4-SECTION", codes)


class TestSessionAnalyzer(unittest.TestCase):

    def test_simple_tier(self):
        config = {"local_claude_md": "", "global_claude_md": ""}
        result = analyze_session(config, "simple")
        self.assertGreaterEqual(result["score"], 8.0)

    def test_standard_missing_all(self):
        config = {"local_claude_md": "# Basic", "global_claude_md": "# Global", "handoff_md": ""}
        result = analyze_session(config, "standard")
        self.assertLess(result["score"], 8.0)

    def test_standard_with_compact(self):
        config = {
            "local_claude_md": "## Compact Instructions\n- summarize\n",
            "global_claude_md": "",
            "handoff_md": "# Current work\n",
        }
        result = analyze_session(config, "standard")
        self.assertGreaterEqual(result["score"], 7.0)


class TestStructureAnalyzer(unittest.TestCase):

    def test_gitignore_missing(self):
        config = {
            "gitignore_has_settings": False,
            "settings_json": {"hooks": {}},
            "rules_files": [],
            "local_claude_md": "",
            "global_claude_md": "",
        }
        result = analyze_structure(config, [], "standard")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("D6-GITIGNORE", codes)

    def test_clean_structure(self):
        config = {
            "gitignore_has_settings": True,
            "settings_json": {},
            "rules_files": [],
            "local_claude_md": "",
            "global_claude_md": "",
        }
        result = analyze_structure(config, [], "standard")
        self.assertGreaterEqual(result["score"], 9.0)


if __name__ == "__main__":
    unittest.main()
