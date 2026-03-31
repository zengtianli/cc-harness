"""Tests for collectors."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from collectors.config import collect_config, _read_text, _check_gitignore
from collectors.skills import collect_skills, _parse_frontmatter
from collectors.hooks import collect_hooks, _validate_hook_schema, _check_hook_command
from collectors.metrics import _count_source_files, _count_ci_workflows


FIXTURES = Path(__file__).parent / "fixtures"


class TestConfigCollector(unittest.TestCase):

    def test_read_text_existing_file(self):
        content = _read_text(FIXTURES / "sample_claude_md.md")
        self.assertIn("Build & Test", content)

    def test_read_text_missing_file(self):
        content = _read_text(FIXTURES / "nonexistent.md")
        self.assertEqual(content, "")

    def test_collect_config_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            claude_home = Path(tmpdir) / ".claude_home"
            claude_home.mkdir()

            # Create a CLAUDE.md
            (project / "CLAUDE.md").write_text("# Test\n- NEVER do bad things\n")

            result = collect_config(project, claude_home)
            self.assertIn("global_claude_md", result)
            self.assertIn("local_claude_md", result)
            self.assertIn("nested_claude_mds", result)
            self.assertIn("settings_json", result)
            self.assertIn("rules_files", result)
            self.assertIn("gitignore_has_settings", result)
            self.assertEqual(result["local_claude_md"], "# Test\n- NEVER do bad things\n")

    def test_check_gitignore_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".gitignore").write_text("settings.local.json\n")
            self.assertTrue(_check_gitignore(project))

    def test_check_gitignore_absent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            self.assertFalse(_check_gitignore(project))

    def test_nested_claude_mds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            claude_home = Path(tmpdir) / ".claude_home"
            claude_home.mkdir()
            (project / "CLAUDE.md").write_text("root")
            sub = project / "sub" / "dir"
            sub.mkdir(parents=True)
            (sub / "CLAUDE.md").write_text("nested")

            result = collect_config(project, claude_home)
            self.assertEqual(len(result["nested_claude_mds"]), 1)
            self.assertIn("sub", result["nested_claude_mds"][0])


class TestSkillsCollector(unittest.TestCase):

    def test_parse_frontmatter(self):
        content = (FIXTURES / "sample_skill.md").read_text()
        fm = _parse_frontmatter(content)
        self.assertEqual(fm["name"], "sample-skill")
        self.assertEqual(fm["version"], "1.0.0")
        self.assertIn("description", fm)

    def test_parse_frontmatter_missing(self):
        fm = _parse_frontmatter("# No frontmatter\nJust content")
        self.assertEqual(fm, {})

    def test_collect_skills(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            claude_home = Path(tmpdir) / ".claude_home"

            # Create local skill
            skill_dir = project / ".claude" / "skills" / "test-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: test-skill\ndescription: A test skill.\nversion: \"1.0.0\"\n---\n# Test\n"
            )

            # Create global skill dir (empty)
            (claude_home / "skills").mkdir(parents=True)

            result = collect_skills(project, claude_home)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["name"], "test-skill")
            self.assertEqual(result[0]["origin"], "local")
            self.assertTrue(result[0]["has_frontmatter"])


class TestHooksCollector(unittest.TestCase):

    def test_validate_hook_schema_valid(self):
        entry = {
            "matcher": "Edit|Write",
            "hooks": [{"type": "command", "command": "echo ok"}],
        }
        issues = _validate_hook_schema(entry)
        self.assertEqual(issues, [])

    def test_validate_hook_schema_missing_matcher(self):
        entry = {"hooks": [{"type": "command", "command": "echo ok"}]}
        issues = _validate_hook_schema(entry)
        self.assertTrue(any("matcher" in i for i in issues))

    def test_check_hook_command_test_suite(self):
        issues = _check_hook_command("pytest tests/")
        self.assertTrue(any("test suite" in i for i in issues))

    def test_check_hook_command_with_truncation(self):
        issues = _check_hook_command("python3 -m py_compile $f 2>&1 | head -5 || echo 'FAILED'")
        # Should have no truncation issue (has | head) and no error surfacing issue (has || echo)
        self.assertFalse(any("truncation" in i for i in issues))
        self.assertFalse(any("error surfacing" in i for i in issues))

    def test_collect_hooks_with_settings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            settings_dir = project / ".claude"
            settings_dir.mkdir()

            settings = json.loads((FIXTURES / "sample_settings.json").read_text())
            (settings_dir / "settings.local.json").write_text(
                json.dumps(settings, indent=2)
            )

            result = collect_hooks(project)
            self.assertTrue(result["has_settings"])
            self.assertIn("PostToolUse", result["event_types"])
            self.assertGreater(len(result["hook_entries"]), 0)

    def test_collect_hooks_no_settings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = collect_hooks(Path(tmpdir))
            self.assertFalse(result["has_settings"])
            self.assertEqual(result["hook_entries"], [])


class TestMetricsCollector(unittest.TestCase):

    def test_count_source_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "main.py").write_text("print('hello')")
            (project / "lib.js").write_text("console.log('hi')")
            (project / "readme.txt").write_text("not source")

            count = _count_source_files(project)
            self.assertEqual(count, 2)

    def test_count_source_files_skips_gitdir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            git_dir = project / ".git"
            git_dir.mkdir()
            (git_dir / "config.py").write_text("# git internal")
            (project / "app.py").write_text("# real code")

            count = _count_source_files(project)
            self.assertEqual(count, 1)

    def test_count_ci_workflows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            wf = project / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "ci.yml").write_text("name: CI")
            (wf / "deploy.yaml").write_text("name: Deploy")

            count = _count_ci_workflows(project)
            self.assertEqual(count, 2)

    def test_count_ci_workflows_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            count = _count_ci_workflows(Path(tmpdir))
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
