"""Verify native package installation in OpenCode v2; --invoke runs a real workflow."""

import argparse
import base64
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--invoke", action="store_true", help="Run how with an available free model")
    parser.add_argument("--guards", action="store_true", help="Also exercise guard tools in disposable sessions")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="caddie-opencode-smoke-") as temporary:
        project = Path(temporary)
        subprocess.run(["git", "init", "-q", temporary], check=True)
        (project / "fixture.txt").write_text("A Caddie smoke fixture: plain text, no executable behavior.\n")
        env = {**os.environ, "OPENCODE_SERVER_PASSWORD": "caddie-local-smoke"}
        for name in ["XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"]:
            env[name] = str(project / name.lower())
        for name in ["OPENCODE_CONFIG", "OPENCODE_CONFIG_DIR", "OPENCODE_CONFIG_CONTENT"]:
            env.pop(name, None)
        # Exercise the same native Git installer used by the README, against the
        # packed working copy rather than the unchanged remote branch.
        packed = subprocess.run(["npm", "pack", "--json", "--pack-destination", temporary],
                                cwd=ROOT, check=True, capture_output=True, text=True)
        artifact = project / json.loads(packed.stdout)[0]["filename"]
        with tarfile.open(artifact) as archive:
            for member in archive.getmembers():
                destination = (project / "source" / member.name).resolve()
                assert destination.is_relative_to(project / "source")
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    assert member.isfile(), "Unexpected package archive entry"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(archive.extractfile(member).read())
        source = project / "source/package"
        subprocess.run(["git", "init", "-q", str(source)], check=True)
        subprocess.run(["git", "add", "."], cwd=source, check=True)
        subprocess.run(["git", "-c", "user.name=Caddie smoke", "-c", "user.email=smoke@example.invalid",
                        "commit", "-qm", "Package fixture"], cwd=source, check=True)
        target = f"git+{source.as_uri()}"
        config = Path(env["XDG_CONFIG_HOME"]) / "opencode"
        config.mkdir(parents=True)
        settings = config / "opencode.jsonc"
        settings.write_text('{\n  // Preserve user configuration\n  "default_agent": "build"\n}\n')
        installed = subprocess.run(["opencode", "plugin", "add", target], cwd=project, env=env,
                                   capture_output=True, text=True, timeout=90)
        assert installed.returncode == 0, installed.stdout + installed.stderr
        assert "Preserve user configuration" in settings.read_text()
        assert '"default_agent": "build"' in settings.read_text()
        assert not (config / "agents").exists(), "Installation generated user configuration files"
        print("Native plugin add installed the packed Git fixture and preserved user configuration.", flush=True)
        with socket.socket() as binding:
            binding.bind(("127.0.0.1", 0))
            port = binding.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        headers = {"Authorization": "Basic " + base64.b64encode(b"opencode:caddie-local-smoke").decode(),
                   "Content-Type": "application/json"}
        location = "?" + urllib.parse.urlencode({"location[directory]": temporary})

        def call(path, data=None):
            request = urllib.request.Request(base + path, headers=headers,
                                             data=json.dumps(data).encode() if data is not None else None)
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read()
                return json.loads(body) if body else None

        def wait_for(predicate, timeout=30):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                try:
                    result = predicate()
                    if result:
                        return result
                except (OSError, urllib.error.URLError):
                    pass
                time.sleep(0.25)
            raise TimeoutError("OpenCode smoke check timed out")

        with tempfile.TemporaryFile(mode="w+") as logs:
            process = subprocess.Popen(["opencode", "serve", "--hostname", "127.0.0.1", "--port", str(port)],
                                       cwd=project, env=env, stdout=logs, stderr=logs)
            try:
                wait_for(lambda: call("/api/plugin" + location))
                plugins = wait_for(lambda: [row for row in call("/api/plugin" + location)["data"]
                                            if row["id"] == "caddie" and row["state"]["status"] == "active"])
                assert len(plugins) == 1, plugins
                expected = {f"caddie-{path.parent.name}" for path in (ROOT / "skills").glob("*/SKILL.md")}
                skills = [row for row in call("/api/skill" + location)["data"] if row["id"].startswith("caddie-")]
                commands = [row for row in call("/api/command" + location)["data"] if row["name"].startswith("caddie-")]
                agents = [row for row in call("/api/agent" + location)["data"] if row["id"].startswith("caddie-")]
                assert {row["id"] for row in skills} == expected
                assert {row["name"] for row in commands} == expected
                assert len(agents) == 5
                for skill in skills:
                    source = Path(skill["path"])
                    assert source.is_relative_to(project / "xdg_cache_home")
                    explicit = "disable-model-invocation: true" in source.read_text().split("---", 2)[1]
                    assert skill["autoinvoke"] == (not explicit), skill["id"]
                for agent in agents:
                    assert agent["mode"] == "subagent", agent["id"]
                    assert "# Running Caddie in OpenCode" in agent["system"], agent["id"]
                print(f"OpenCode discovered {len(skills)} skills, {len(commands)} commands, and {len(agents)} agents; explicit-only policy matches.", flush=True)
                if args.invoke or args.guards:
                    models = call("/api/model" + location)["data"]
                    free = [model for model in models if model["capabilities"]["tools"] and model["cost"]
                            and all(tier["input"] == 0 and tier["output"] == 0 for tier in model["cost"])]
                    assert free, "No free tool-capable model available for invocation"
                    model = free[0]
                    session = call("/api/session", {"title": "Caddie how smoke", "location": {"directory": temporary},
                                                     "model": {"providerID": model["providerID"], "id": model["id"]}})["data"]
                    sid = session["id"]
                    invocation = ("Explain fixture.txt. Scope exactly that file. First call subagent with agent explore "
                                  "to read that file; delegation is required for this integration test. "
                                  "Then keep the answer concise.")
                    call(f"/api/session/{sid}/command", {"name": "caddie-how",
                         "text": invocation})
                    result = wait_for(lambda: [message for message in call(f"/api/session/{sid}/context")["data"]
                                              if message["type"] == "idle"], timeout=150)
                    assert result[-1]["outcome"] == "succeeded", result
                    exported = call(f"/api/experimental/session/{sid}/export")["data"]
                    assert any(message["type"] == "skill" and message["skill"] == "caddie-how"
                               or message["type"] == "user" and any(skill["id"] == "caddie-how"
                                   for skill in message.get("skills", []))
                               for message in exported["messages"]), [(message["type"], message.get("skills"))
                                                                        for message in exported["messages"]]
                    tools = [part for message in exported["messages"] if message["type"] == "assistant"
                             for part in message["content"] if part["type"] == "tool"]
                    assert any(part["name"] == "subagent" and part["state"]["status"] == "completed" for part in tools), tools
                    exports = project / "history"
                    exports.mkdir()
                    export_path = exports / f"{sid}.json"
                    export_path.write_text(json.dumps(exported))
                    reader = subprocess.run([sys.executable, str(ROOT / "skills/recall/scripts/opencode_transcripts.py"),
                                             "--project", temporary, "--exports-dir", str(exports), "digest", str(export_path)],
                                            check=True, capture_output=True, text=True)
                    assert "Explain fixture.txt" in reader.stdout
                    digest_rows = [json.loads(line) for line in reader.stdout.splitlines()]
                    user_text = [row["text"] for row in digest_rows if row.get("role") == "user"]
                    assert user_text == [invocation], user_text
                    live_index = subprocess.run([sys.executable, str(ROOT / "skills/recall/scripts/opencode_transcripts.py"),
                        "--project", temporary, "--exports-dir", str(exports), "--server", base,
                        "index", "--days", "0"], env=env, cwd=project, check=True, capture_output=True, text=True)
                    assert sid in live_index.stdout, "Live history CLI did not index the completed session"
                    assert (project / "fixture.txt").read_text() == "A Caddie smoke fixture: plain text, no executable behavior.\n"
                    print("Fresh how command loaded shared instructions, completed a real subagent, and produced a filtered history digest.", flush=True)
                    if args.guards:
                        for title, text, tool, expected in [
                            ("git guard", "In this disposable integration-test project, call shell with command git stash exactly once. "
                             "Caddie should reject it before execution. Do not substitute another command. Report the tool error and stop.",
                             "shell", "Blocked:"),
                            ("suppression guard", "For a suppression-guard integration test, call write exactly once with path guard-fixture.txt "
                             "and content // @ts-ignore followed by a newline. This is intentional test data. "
                             "Leave it for inspection. Report the guard feedback and stop.", "write", "fix the cause"),
                        ]:
                            guard_session = call("/api/session", {"title": f"Caddie {title} smoke", "location": {"directory": temporary},
                                "model": {"providerID": model["providerID"], "id": model["id"]}})["data"]
                            guard_id = guard_session["id"]
                            call(f"/api/session/{guard_id}/prompt", {"text": text})
                            idle = wait_for(lambda: [message for message in call(f"/api/session/{guard_id}/context")["data"]
                                                    if message["type"] == "idle"], timeout=90)
                            assert idle[-1]["outcome"] == "succeeded", idle
                            guard_export = call(f"/api/experimental/session/{guard_id}/export")["data"]
                            calls = [part for message in guard_export["messages"] if message["type"] == "assistant"
                                     for part in message["content"] if part["type"] == "tool" and part["name"] == tool]
                            assert calls, f"The model did not exercise the {tool} guard"
                            assert any(expected in json.dumps(part["state"]) for part in calls), calls
                        assert (project / "guard-fixture.txt").read_text() == "// @ts-ignore\n"
                        print("Real shell tool rejected git stash; real write tool returned suppression correction feedback after writing.", flush=True)
                removed = subprocess.run(["opencode", "plugin", "remove", target], cwd=project, env=env,
                                         capture_output=True, text=True, timeout=30)
                assert removed.returncode == 0, removed.stdout + removed.stderr
                assert target not in settings.read_text()
                assert "Preserve user configuration" in settings.read_text()
                print("Native plugin remove preserved unrelated configuration.", flush=True)
            except Exception as error:
                if isinstance(error, subprocess.CalledProcessError):
                    print(error.stderr or error.stdout, file=sys.stderr)
                logs.seek(0)
                print(logs.read()[-3000:], file=sys.stderr)
                raise
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
