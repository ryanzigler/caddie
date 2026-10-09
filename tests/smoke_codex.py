"""Install and discover Caddie with a temporary CODEX_HOME; requires Codex CLI."""

import json
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix="caddie-codex-") as temporary:
        env = {**os.environ, "CODEX_HOME": temporary}
        for args in [
            ["marketplace", "add", str(ROOT), "--json"],
            ["add", "caddie@caddie", "--json"],
        ]:
            subprocess.run(
                ["codex", "plugin", *args], env=env, cwd=temporary,
                check=True, capture_output=True, text=True, timeout=30,
            )

        with tempfile.TemporaryFile(mode="w+") as stderr:
            process = subprocess.Popen(
                ["codex", "app-server"], env=env, cwd=temporary,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                text=True,
            )
            try:
                def send(message):
                    process.stdin.write(json.dumps(message) + "\n")
                    process.stdin.flush()

                def receive(request_id):
                    deadline = time.monotonic() + 20
                    with selectors.DefaultSelector() as selector:
                        selector.register(process.stdout, selectors.EVENT_READ)
                        while time.monotonic() < deadline:
                            if not selector.select(timeout=1):
                                continue
                            line = process.stdout.readline()
                            if not line:
                                raise RuntimeError("Codex app-server closed stdout")
                            message = json.loads(line)
                            if message.get("id") == request_id:
                                if "error" in message:
                                    raise RuntimeError(message["error"])
                                return message["result"]
                    raise TimeoutError("Codex app-server did not answer")

                send({"id": 1, "method": "initialize", "params": {
                    "clientInfo": {"name": "caddie-smoke", "version": "1.0"},
                }})
                receive(1)
                send({"method": "initialized"})
                send({"id": 2, "method": "skills/list", "params": {
                    "cwds": [temporary], "forceReload": True,
                }})
                result = receive(2)
                skills = [skill for row in result["data"] for skill in row["skills"]
                          if skill.get("pluginId") == "caddie@caddie"]
                errors = [error for row in result["data"] for error in row["errors"]]
                assert not errors, errors
                expected = {f"caddie:{path.parent.name}"
                            for path in (ROOT / "skills").glob("*/SKILL.md")}
                actual = {skill["name"] for skill in skills}
                assert actual == expected, {"missing": expected - actual, "extra": actual - expected}
                for skill in skills:
                    assert skill["enabled"], skill["name"]
                    assert Path(skill["path"]).resolve().is_relative_to(Path(temporary).resolve())
                    assert Path(skill["path"]).is_file(), skill["path"]
                print(f"Installed and discovered all {len(skills)} Caddie skills with no loader errors.")

                send({"id": 3, "method": "hooks/list", "params": {"cwds": [temporary]}})
                result = receive(3)
                hooks = [hook for row in result["data"] for hook in row["hooks"]
                         if hook.get("pluginId") == "caddie@caddie"]
                problems = [problem for row in result["data"]
                            for problem in row["errors"] + row["warnings"]]
                assert not problems, problems
                manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
                declared = json.loads((ROOT / manifest["hooks"]).read_text())["hooks"]
                expected = sum(len(group["hooks"]) for groups in declared.values() for group in groups)
                assert len(hooks) == expected, hooks
                print(f"Loaded all {len(hooks)} Caddie hooks with no parse errors.")
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                process.stdin.close()
                process.stdout.close()


if __name__ == "__main__":
    main()
