import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
READER = ROOT / "skills/recall/scripts/codex_transcripts.py"


class PackagingTests(unittest.TestCase):
    def test_manifests_share_identity_and_base_version(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        entry = next(p for p in marketplace["plugins"] if p["name"] == claude["name"])
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(codex["version"].split("+", 1)[0], claude["version"])
        self.assertEqual(entry["version"], claude["version"])
        self.assertEqual((ROOT / entry["source"]).resolve(), ROOT)
        self.assertEqual(codex["skills"], "./skills/")
        self.assertTrue((ROOT / codex["skills"]).is_dir())

    def test_codex_hooks_mirror_claude_hooks_without_modules(self):
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        claude_hooks = json.loads((ROOT / "hooks/hooks.json").read_text())
        codex_hooks = json.loads((ROOT / codex["hooks"]).read_text())
        self.assertEqual(codex_hooks, {"hooks": claude_hooks["hooks"]})

    def test_mcp_configs_declare_servers(self):
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        claude_servers = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]
        codex_servers = json.loads((ROOT / codex["mcpServers"]).read_text())["mcpServers"]
        self.assertLessEqual(claude_servers.keys(), codex_servers.keys())

    def test_explicit_invocation_policies_match(self):
        for skill in (ROOT / "skills").glob("*/SKILL.md"):
            with self.subTest(skill=skill.parent.name):
                frontmatter = skill.read_text().split("---", 2)[1]
                explicit = bool(re.search(r"^disable-model-invocation: true$", frontmatter, re.M))
                policy = skill.parent / "agents/openai.yaml"
                codex_explicit = policy.exists() and bool(re.search(
                    r"^  allow_implicit_invocation: false$", policy.read_text(), re.M,
                ))
                self.assertEqual(explicit, codex_explicit)

    def test_shared_hook_commands_work_from_another_directory(self):
        hooks = json.loads((ROOT / "hooks/hooks.json").read_text())["hooks"]
        # Codex canonicalizes exec_command to Bash and aliases apply_patch to Edit/Write.
        cases = [
            ("PreToolUse", "Bash", ["Bash"], {"command": "git stash"}, 2),
            ("PreToolUse", "Bash", ["Bash"], {"command": "git status --short"}, 0),
            ("PostToolUse", "apply_patch", ["apply_patch", "Edit", "Write"], {
                "command": "*** Begin Patch\n*** Add File: a.ts\n+// @ts-ignore\n*** End Patch",
            }, 2),
        ]
        with tempfile.TemporaryDirectory(prefix="caddie hook cwd ") as cwd:
            for event, tool, aliases, fields, expected in cases:
                with self.subTest(event=event, fields=fields):
                    commands = [command for group in hooks[event]
                                if any(re.search(group["matcher"], alias) for alias in aliases)
                                for command in group["hooks"]]
                    self.assertEqual(len(commands), 1)
                    result = subprocess.run(
                        ["bash", "-c", commands[0]["command"]], cwd=cwd,
                        env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(ROOT)},
                        input=json.dumps({"tool_name": tool, "tool_input": fields}),
                        text=True, capture_output=True, check=False,
                    )
                    self.assertEqual(result.returncode, expected, result.stderr)


class HookTests(unittest.TestCase):
    def run_hook(self, name, payload):
        return subprocess.run(
            ["bash", str(ROOT / "hooks" / name)], input=json.dumps(payload),
            text=True, capture_output=True, check=False,
        )

    def suppression(self, payload, expected):
        result = self.run_hook("suppression-guard.sh", payload)
        self.assertEqual(result.returncode, expected, result.stderr)
        if expected == 2:
            self.assertIn("fix the cause", result.stderr)
        return result

    def test_claude_edit_write_and_multiedit(self):
        for tool, fields in [
            ("Edit", {"new_string": "// @ts-ignore\ncall();"}),
            ("Write", {"content": "// eslint-disable-next-line\ncall();"}),
            ("MultiEdit", {"edits": [{"new_string": "// biome-ignore lint\ncall();"}]}),
        ]:
            with self.subTest(tool=tool):
                result = self.suppression({"tool_name": tool, "tool_input": {
                    "file_path": "example.ts", **fields,
                }}, 2)
                self.assertIn("example.ts", result.stderr)

    def test_claude_clean_edits_removals_and_formatter(self):
        for fields in [
            {"new_string": "call();"},
            {"old_string": "// @ts-ignore", "new_string": ""},
            {"content": "// prettier-ignore\ncall();"},
            {},
        ]:
            with self.subTest(fields=fields):
                self.suppression({"tool_name": "Edit", "tool_input": fields}, 0)

    def test_codex_added_suppressions(self):
        for header in ["*** Add File: new.ts", "*** Update File: old.ts"]:
            with self.subTest(header=header):
                patch = f"*** Begin Patch\n{header}\n@@\n+// @ts-ignore\n+call();\n*** End Patch"
                result = self.suppression({"tool_name": "apply_patch", "tool_input": {"command": patch}}, 2)
                self.assertIn(header.split(": ", 1)[1], result.stderr)

    def test_codex_only_added_lines_are_checked(self):
        patches = [
            "*** Update File: a.ts\n@@\n-// @ts-ignore\n+call();",
            "*** Update File: a.ts\n@@\n // @ts-ignore\n+call();",
            "*** Add File: a.ts\n+// prettier-ignore\n+call();",
            "*** Delete File: a.ts",
        ]
        for patch in patches:
            with self.subTest(patch=patch):
                self.suppression({"tool_name": "apply_patch", "tool_input": {
                    "command": f"*** Begin Patch\n{patch}\n*** End Patch",
                }}, 0)

    def test_codex_multiple_files(self):
        patch = "*** Begin Patch\n*** Update File: a.ts\n@@\n-// @ts-ignore\n+call();\n*** Add File: b.ts\n+// @ts-expect-error\n*** End Patch"
        self.suppression({"tool_name": "apply_patch", "tool_input": {"command": patch}}, 2)

    def test_session_start_prints_user_instructions_from_another_directory(self):
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                ["bash", str(ROOT / "hooks/user-instructions.sh")], cwd=cwd,
                input=json.dumps({"hook_event_name": "SessionStart", "source": "startup"}),
                text=True, capture_output=True, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (ROOT / "hooks/user-instructions.md").read_text())

    def test_destructive_command_is_rejected_without_execution(self):
        result = self.run_hook("destructive-git-guard.sh", {
            "tool_name": "Bash", "tool_input": {"command": "git stash"},
        })
        self.assertEqual(result.returncode, 2)
        self.assertIn("Blocked", result.stderr)

    def test_claude_retired_skill_redirects(self):
        for retired, replacement in [
            ("caddie:unslop", "ryan-voice-guide"),
            ("anthropic-skills:humanize-writing", "ryan-voice-guide"),
            ("anthropic-skills:cro-metrics-writing", "ryan-voice-guide"),
        ]:
            with self.subTest(retired=retired):
                result = self.run_hook("retired-skill-redirect.sh", {
                    "tool_input": {"skill": retired},
                })
                self.assertEqual(result.returncode, 0)
                output = json.loads(result.stdout)["hookSpecificOutput"]
                self.assertEqual(output["permissionDecision"], "deny")
                self.assertIn(f"caddie:{replacement}", output["permissionDecisionReason"])


    def test_superpowers_skills_are_not_redirected(self):
        for skill in ["superpowers:systematic-debugging", "superpowers:brainstorming",
                      "superpowers:writing-skills"]:
            with self.subTest(skill=skill):
                result = self.run_hook("retired-skill-redirect.sh", {
                    "tool_input": {"skill": skill},
                })
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")


class TranscriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.project = self.home / "project with spaces"
        self.project.mkdir()

    def rollout(self, name, cwd=None, source="cli", age=0, archived=False):
        path = self.home / ("archived_sessions" if archived else "sessions") / f"{name}.jsonl"
        path.parent.mkdir(exist_ok=True)
        records = [
            {"type": "session_meta", "payload": {"id": name, "cwd": str(cwd or self.project), "source": source}},
            {"type": "response_item", "payload": {"type": "message", "role": "developer", "content": [{"type": "input_text", "text": "PRIVATE_CONTEXT"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "# AGENTS.md instructions for project"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Fix the retry bug"}]}},
            {"type": "event_msg", "payload": {"type": "user_message", "message": "Fix the retry bug"}},
            {"type": "response_item", "payload": {"type": "function_call_output", "output": "PRIVATE_TOOL_OUTPUT"}},
            {"type": "response_item", "payload": {"type": "reasoning", "summary": "PRIVATE_REASONING"}},
            {"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "The retry is fixed."}]}},
        ]
        path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
        os.utime(path, (time.time() - age, time.time() - age))
        return path

    def run_reader(self, *args):
        return subprocess.run([
            "python3", str(READER), "--codex-home", str(self.home),
            "--project", str(self.project), *map(str, args),
        ], text=True, capture_output=True, check=False)

    def test_index_scope_window_exclusion_and_order(self):
        self.rollout("older", age=60)
        self.rollout("newer", archived=True)
        self.rollout("outside", cwd=self.home / "other")
        self.rollout("old", age=9 * 86400)
        self.rollout("child", source={"subagent": {"parent_thread_id": "older"}})
        self.rollout("current")
        result = self.run_reader("index", "--exclude-session", "current")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([row["session_id"] for row in rows], ["newer", "older"])
        self.assertTrue(all(row["prompts"] == 1 for row in rows))
        result = self.run_reader("index", "--days", "0", "--exclude-session", "current")
        self.assertIn('"session_id": "old"', result.stdout)

    def test_digest_filters_private_context_and_paginates(self):
        path = self.rollout("one")
        result = self.run_reader("digest", path, "--limit", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(rows[1]["text"], "Fix the retry bug")
        self.assertEqual(rows[2]["next_start"], 2)
        result = self.run_reader("digest", path, "--start", "2")
        self.assertIn("The retry is fixed.", result.stdout)
        self.assertNotIn("PRIVATE_", result.stdout)
        self.assertNotIn("Fix the retry bug", result.stdout)

    def test_topic_search_excludes_tool_output(self):
        self.rollout("one")
        self.assertEqual(self.run_reader("index", "--topic", "PRIVATE_TOOL_OUTPUT").stdout, "")
        self.assertIn('"session_id": "one"', self.run_reader("index", "--topic", "retry").stdout)

    def test_digest_rejects_other_project(self):
        path = self.rollout("outside", cwd=self.home / "other")
        result = self.run_reader("digest", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside", result.stderr)

    def test_missing_history_is_reported(self):
        result = self.run_reader("index")
        self.assertEqual(result.returncode, 1)
        self.assertIn("No local Codex session directories", result.stderr)


if __name__ == "__main__":
    unittest.main()
