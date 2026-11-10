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

    def test_claude_only_skills_stay_out_of_other_hosts(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(claude["skills"], ["./claude-skills/"])
        claude_only = {p.parent.name for p in (ROOT / "claude-skills").glob("*/SKILL.md")}
        shared = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertIn("generate-image", claude_only)
        self.assertEqual(claude_only & shared, set())
        package = json.loads((ROOT / "package.json").read_text())
        self.assertNotIn("claude-skills", package["files"])

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
        edit_aliases = ["apply_patch", "Edit", "Write"]
        cases = [
            ("PreToolUse", "Bash", ["Bash"], {"command": "git stash"}, [2]),
            ("PreToolUse", "Bash", ["Bash"], {"command": "git status --short"}, [0]),
            ("PostToolUse", "apply_patch", edit_aliases, {
                "command": "*** Begin Patch\n*** Add File: a.ts\n+// @ts-ignore\n*** End Patch",
            }, [2, 0]),
            ("PostToolUse", "apply_patch", edit_aliases, {
                "command": "*** Begin Patch\n*** Add File: a.ts\n+var x = 1;\n*** End Patch",
            }, [0, 2]),
        ]
        with tempfile.TemporaryDirectory(prefix="caddie hook cwd ") as cwd:
            for event, tool, aliases, fields, expected in cases:
                with self.subTest(event=event, fields=fields):
                    commands = [command for group in hooks[event]
                                if any(re.search(group["matcher"], alias) for alias in aliases)
                                for command in group["hooks"]]
                    codes = [subprocess.run(
                        ["bash", "-c", command["command"]], cwd=cwd,
                        env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(ROOT)},
                        input=json.dumps({"tool_name": tool, "tool_input": fields}),
                        text=True, capture_output=True, check=False,
                    ).returncode for command in commands]
                    self.assertEqual(codes, expected)


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

    def style(self, payload, expected):
        result = self.run_hook("js-style-guard.sh", payload)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def test_style_violations_in_claude_edits(self):
        for code, rule in [
            ("var count = 0;", "var:"),
            ("items.forEach((item) => use(item));", ".forEach:"),
            ("for (let i = 0; i < items.length; i++) {}", "index for-loop:"),
            ("const fs = require('node:fs');", "CommonJS:"),
            ("module.exports = run;", "CommonJS:"),
            ("if (left == right) {}", "loose equality:"),
            ("if (left != right) {}", "loose equality:"),
            ("const value = input as any;", "any:"),
            ("const parse = (raw: any) => raw;", "any:"),
        ]:
            with self.subTest(code=code):
                result = self.style({"tool_name": "Edit", "tool_input": {
                    "file_path": "src/example.ts", "new_string": code,
                }}, 2)
                self.assertIn(f"src/example.ts: {rule}", result.stderr)

    def test_style_clean_code_strings_and_comments(self):
        clean = "\n".join([
            "const total = items.length;",
            "if (value == null || null != other) {}",
            "if (left === right && left !== other && left <= right) {}",
            "for (const [index, item] of items.entries()) {}",
            "const variable = 'var x == y as any; items.forEach(';",
            'const message = "require(\\"fs\\") != that";',
            "const note = `module.exports == ${name}`;",
            "// var legacy = 1; items.forEach(run);",
            " * if (a == b) {}",
            "const url = 'https://example.com'; // left == right",
            "const parse = (raw: unknown) => raw;",
            "const company = anyValue;",
        ])
        self.style({"tool_name": "Write", "tool_input": {"file_path": "a.ts", "content": clean}}, 0)

    def test_style_file_types(self):
        for path, code, expected in [
            ("README.md", "var x = 1;", 0),
            ("notes.txt", "items.forEach(run);", 0),
            ("config.cjs", "const fs = require('node:fs');\nmodule.exports = fs;", 0),
            ("script.js", "const value = input as any;", 0),
            ("component.tsx", "list.forEach(render);", 2),
            ("module.mjs", "module.exports = run;", 2),
            ("types.mts", "const value = input as any;", 2),
            ("", "var x = 1;", 0),
        ]:
            with self.subTest(path=path):
                self.style({"tool_name": "Write", "tool_input": {"file_path": path, "content": code}}, expected)

    def test_style_braces_and_return_spacing(self):
        for code, expected in [
            ("if (!user) return;", 0),
            ("if (done) {\n  return;\n}", 0),
            ("if (route === undefined)\n  throw new Error('missing');", 2),
            ("} else if (ready)\n  go();", 2),
            ("} else\n  stop();", 2),
            ("for (const [k, v] of body) url.set(k, v);", 0),
            ("for (const item of items)\n  use(item);", 2),
            ("while (queue.length > 0)\n  queue.pop();", 2),
            ("const total = sum();\nreturn total;", 2),
            ("if (ready) {\n  go();\n}\nreturn next;", 2),
            ("const total = sum();\n\nreturn total;", 0),
            ("const run = () => {\n  return 1;\n};", 0),
            ("switch (kind) {\n  case 'a':\n    return 1;\n}", 0),
            ("// explain why\nreturn value;", 0),
            ("const ok = check(\n  value,\n);\n\nreturn ok;", 0),
        ]:
            with self.subTest(code=code):
                self.style({"tool_name": "Write", "tool_input": {"file_path": "a.ts", "content": code}}, expected)

    def test_style_return_spacing_uses_patch_context(self):
        for context, expected in [(" const total = sum();", 2), (" ", 0), (" if (ready) {", 0)]:
            with self.subTest(context=context):
                patch = f"*** Begin Patch\n*** Update File: a.ts\n@@\n{context}\n+return total;\n*** End Patch"
                self.style({"tool_name": "apply_patch", "tool_input": {"command": patch}}, expected)
        patch = "*** Begin Patch\n*** Update File: a.ts\n@@\n const total = sum();\n@@\n+return total;\n*** End Patch"
        self.style({"tool_name": "apply_patch", "tool_input": {"command": patch}}, 0)
        self.style({"tool_name": "MultiEdit", "tool_input": {"file_path": "a.ts", "edits": [
            {"new_string": "const total = sum();"}, {"new_string": "return total;"},
        ]}}, 0)

    def test_style_ryans_fake_graph_examples(self):
        correct = (ROOT / "tests/fixtures/fake-graph.ts.txt").read_text()
        self.style({"tool_name": "Write", "tool_input": {"file_path": "fake-graph.ts", "content": correct}}, 0)
        unbraced = (correct
                    .replace("URLSearchParams) {\n      for (const [k, v] of init.body) {\n        url.searchParams.set(k, v);\n      }\n    }",
                             "URLSearchParams)\n      for (const [k, v] of init.body) url.searchParams.set(k, v);")
                    .replace("undefined) {\n      throw new Error(`fake graph: no route for ${method} ${path}`);\n    }",
                             "undefined)\n      throw new Error(`fake graph: no route for ${method} ${path}`);"))
        self.assertNotEqual(unbraced, correct)
        result = self.style({"tool_name": "Write", "tool_input": {"file_path": "fake-graph.ts", "content": unbraced}}, 2)
        self.assertEqual(result.stderr.count("unbraced body"), 2)
        cramped = re.sub(r"\n\n(?=\s*(return|const route|const body|calls|if|const path|const fetchImpl))", "\n", correct)
        result = self.style({"tool_name": "Write", "tool_input": {"file_path": "fake-graph.ts", "content": cramped}}, 2)
        self.assertEqual(result.stderr.count("return right after a statement"), 2)

    def test_style_multiedit_and_removed_code(self):
        self.style({"tool_name": "MultiEdit", "tool_input": {
            "file_path": "a.ts", "edits": [{"old_string": "x", "new_string": "var x = 1;"}],
        }}, 2)
        self.style({"tool_name": "Edit", "tool_input": {
            "file_path": "a.ts", "old_string": "var x = 1;", "new_string": "const x = 1;",
        }}, 0)

    def test_style_codex_patches_check_added_lines_per_file(self):
        patch = "\n".join([
            "*** Begin Patch",
            "*** Update File: a.ts",
            "@@",
            "-var removed = 1;",
            " var context = 2;",
            "+const added = 1;",
            "*** Add File: notes.md",
            "+var prose = 1;",
            "*** Add File: b.mjs",
            "+module.exports = run;",
            "*** Update File: c.txt",
            "*** Move to: c.js",
            "@@",
            "+var moved = 1;",
            "*** Delete File: d.ts",
            "*** End Patch",
        ])
        result = self.style({"tool_name": "apply_patch", "tool_input": {"command": patch}}, 2)
        self.assertIn("b.mjs: CommonJS:", result.stderr)
        self.assertIn("c.js: var:", result.stderr)
        self.assertNotIn("a.ts", result.stderr)
        self.assertNotIn("notes.md", result.stderr)

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
