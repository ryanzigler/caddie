import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
READER = ROOT / "skills/recall/scripts/opencode_transcripts.py"


class OpenCodePackagingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("npm"), "npm required for package artifact checks")
    def test_native_package_contains_shared_resources_and_entrypoint(self):
        with tempfile.TemporaryDirectory(prefix="caddie package spaces ") as temporary:
            result = subprocess.run(["npm", "pack", "--json", "--pack-destination", temporary],
                                    cwd=ROOT, check=True, capture_output=True, text=True)
            artifact = json.loads(result.stdout)[0]
            paths = {item["path"] for item in artifact["files"]}
            for path in ["opencode/plugin.js", "opencode/runtime.mjs", "agents/code-reviewer.md",
                         "references/opencode.md", "skills/how/SKILL.md", "skills/how/LICENSE",
                         "hooks/destructive-git-guard.sh", "skills/recall/scripts/opencode_transcripts.py"]:
                self.assertIn(path, paths)
            self.assertNotIn("scripts/install_opencode.py", paths)
            self.assertEqual(json.loads((ROOT / "package.json").read_text())["version"],
                             json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"])

    @unittest.skipUnless(shutil.which("node") and shutil.which("jq"), "Node and jq required")
    def test_runtime_against_shared_guards(self):
        result = subprocess.run(["node", "--test", str(ROOT / "tests/opencode.test.mjs")],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class OpenCodeHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.exports = self.root / "exports"
        self.exports.mkdir()

    def export(self, session_id, directory=None, parent=None, messages=None):
        info = {"id": session_id, "location": {"directory": str(directory or self.project)},
                "time": {"updated": time.time() * 1000}, "title": "Fixture"}
        if parent:
            info["parentID"] = parent
        path = self.exports / f"{session_id}.json"
        path.write_text(json.dumps({"info": info, "messages": messages or []}))
        return path

    def run_reader(self, *arguments):
        return subprocess.run([sys.executable, str(READER), "--project", str(self.project),
                               "--exports-dir", str(self.exports), "--exclude-session", "ses_current",
                               *arguments], capture_output=True, text=True)

    def test_index_filters_project_current_and_children_and_topics_only_search_prose(self):
        self.export("ses_good", messages=[{"type": "user", "text": "Fix the upload", "id": "msg_user"}])
        self.export("ses_current")
        self.export("ses_child", parent="ses_good")
        self.export("ses_other", directory=self.root / "other")
        self.export("ses_tool", messages=[{"type": "assistant", "content": [
            {"type": "tool", "text": "upload"}, {"type": "reasoning", "text": "upload"}]}])
        result = self.run_reader("index", "--offline", "--days", "0", "--topic", "upload")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([row["session_id"] for row in rows], ["ses_good"])
        self.assertEqual(rows[0]["prompts"], 1)

    def test_digest_omits_synthetic_skills_reasoning_and_tools_and_paginates(self):
        path = self.export("ses_good", messages=[
            {"type": "system", "text": "Injected"},
            {"type": "synthetic", "text": "Notification"},
            {"type": "skill", "text": "Instructions"},
            {"type": "user", "text": "User goal", "id": "msg_user"},
            {"type": "assistant", "id": "msg_assistant", "content": [
                {"type": "reasoning", "text": "Private reasoning"},
                {"type": "tool", "state": {"output": "Tool output"}},
                {"type": "text", "text": "Result"}]}])
        result = self.run_reader("digest", str(path), "--limit", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(rows[1]["text"], "User goal")
        self.assertEqual(rows[2], {"next_start": 2})
        next_result = self.run_reader("digest", str(path), "--start", "2")
        self.assertIn('"text": "Result"', next_result.stdout)
        self.assertNotIn("Private reasoning", next_result.stdout)
        self.assertNotIn("Tool output", next_result.stdout)

    def test_digest_rejects_cross_project_current_and_child_exports(self):
        for path in [self.export("ses_current"), self.export("ses_child", parent="ses_parent"),
                     self.export("ses_other", directory=self.root / "other")]:
            with self.subTest(path=path):
                result = self.run_reader("digest", str(path))
                self.assertEqual(result.returncode, 1)
                self.assertIn("outside the project", result.stderr)

    def test_unsupported_format_is_an_access_gap(self):
        (self.exports / "invalid.json").write_text('{"messages":[]}')
        result = self.run_reader("index", "--offline")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Unsupported OpenCode", result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node is needed for the CLI export regression")
    def test_live_index_captures_large_cli_exports_before_immediate_exit(self):
        path = self.export("ses_large", messages=[{"type": "user", "text": "x" * 300000}])
        cli = self.root / "opencode-fixture"
        rows = [{"id": "ses_large", "directory": str(self.project), "updated": time.time() * 1000}]
        cli.write_text("#!/usr/bin/env node\n"
                       "const fs = require('node:fs');\n"
                       f"const rows = {json.dumps(rows)};\n"
                       f"const source = {json.dumps(str(path))};\n"
                       "console.log(process.argv.includes('list') ? JSON.stringify(rows) : fs.readFileSync(source, 'utf8'));\n"
                       "process.exit(0);\n")
        cli.chmod(0o700)
        result = self.run_reader("--opencode", str(cli), "index", "--days", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["session_id"], "ses_large")
        self.assertEqual(len(json.loads(path.read_text())["messages"][0]["text"]), 300000)

    def test_location_changes_exclude_previous_project_messages(self):
        path = self.export("ses_moved", messages=[
            {"type": "user", "text": "Other project private goal"},
            {"type": "location-switched", "previous": {"location": {"directory": str(self.root / "other")}},
             "location": {"directory": str(self.project)}},
            {"type": "user", "text": "Current project goal"}])
        result = self.run_reader("digest", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Current project goal", result.stdout)
        self.assertNotIn("Other project private goal", result.stdout)


if __name__ == "__main__":
    unittest.main()
