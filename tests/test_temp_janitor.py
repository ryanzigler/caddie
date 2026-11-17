import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
JANITOR = ROOT / "hooks/temp-janitor.sh"
AGE_SECONDS = 2
UID = os.getuid()


def clean_env():
    return {k: v for k, v in os.environ.items()
            if not k.startswith(("CADDIE_TEMP_JANITOR", "RAILWAY_"))}


def janitor_pids(marker):
    if Path("/proc/self").is_dir():
        pids = []
        for proc in Path("/proc").glob("[0-9]*"):
            try:
                cmd = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            except OSError:
                continue
            if "temp-janitor.sh --daemon" in cmd and marker in cmd:
                pids.append(int(proc.name))
        return pids
    out = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True).stdout
    return [int(line.split(None, 1)[0]) for line in out.splitlines()
            if "temp-janitor.sh --daemon" in line and marker in line]


def wait_for(predicate, timeout=10.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.1)
    return predicate()


class TempJanitorTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="caddie-janitor-")).resolve()
        self.root = self.base / "root"
        self.state = self.base / "state"
        self.outside = self.base / "outside"
        for path in (self.root, self.outside):
            path.mkdir()
        self.children = []
        self.handles = []

    def tearDown(self):
        for pid in janitor_pids(str(self.state)):
            os.kill(pid, signal.SIGTERM)
        wait_for(lambda: not janitor_pids(str(self.state)), timeout=5)
        for child in self.children:
            child.kill()
            child.wait()
        for handle in self.handles:
            handle.close()
        shutil.rmtree(self.base, ignore_errors=True)

    def env(self, **extra):
        return {
            **clean_env(),
            "CADDIE_TEMP_JANITOR_TEST_ROOT": str(self.root),
            "CADDIE_TEMP_JANITOR_STATE_DIR": str(self.state),
            "CADDIE_TEMP_JANITOR_MAX_AGE": f"{AGE_SECONDS}s",
            **extra,
        }

    def run_janitor(self, *args, env):
        return subprocess.run(["bash", str(JANITOR), *args], env=env, cwd=self.base,
                              capture_output=True, text=True, timeout=60)

    def log(self):
        path = self.state / "janitor.log"
        return path.read_text() if path.exists() else ""

    def settled_janitor(self):
        """The one running janitor once it holds the lock, or None."""
        def settled():
            pids = janitor_pids(str(self.state))
            lock = self.state / "lock"
            return (len(pids) == 1 and lock.exists()
                    and lock.read_text().strip() == str(pids[0]))
        return janitor_pids(str(self.state))[0] if wait_for(settled) else None

    def make_dir(self, name, files=("file",)):
        path = self.root / name
        path.mkdir()
        for file in files:
            (path / file).write_text("x")
        return path

    def build_fixtures(self):
        """Old entries first, then age past the threshold, then new ones."""
        self.make_dir("old-plain", ["a", "b"])
        (self.root / "old-file").write_text("x")
        old_link_holder = self.make_dir("old-with-link")
        target = self.outside / "target"
        target.mkdir()
        (target / "precious").write_text("keep me")
        (old_link_holder / "to-outside").symlink_to(target)
        (self.root / "link").symlink_to(target)
        for name in (f"claude-{UID}", "cc-socks", f"tsx-{UID}", "custom-keep"):
            self.make_dir(name)
        sockets = self.make_dir("old-with-socket", [])
        for path in (self.root / "s", sockets / "s"):
            server = socket.socket(socket.AF_UNIX)
            server.bind(str(path))
            self.handles.append(server)
        cwd = self.make_dir("old-cwd")
        self.children.append(subprocess.Popen(["sleep", "300"], cwd=cwd))
        self.handles.append(open(self.make_dir("old-open") / "file"))
        fresh_inside = self.make_dir("old-fresh-inside", [])
        (fresh_inside / "deep").mkdir()
        time.sleep(AGE_SECONDS + 1.5)
        (fresh_inside / "deep" / "new").write_text("x")
        self.make_dir("new")
        extracted = self.make_dir("new-extracted")
        os.utime(extracted, (500_000_000, 500_000_000))
        os.utime(extracted / "file", (500_000_000, 500_000_000))

    def names(self):
        return {path.name for path in self.root.iterdir()}

    def test_pass_deletes_only_stale_idle_entries(self):
        self.build_fixtures()
        result = self.run_janitor("--once", env=self.env(
            CADDIE_TEMP_JANITOR="1", CADDIE_TEMP_JANITOR_KEEP="custom-*, other"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.names(), {
            "link", f"claude-{UID}", "cc-socks", f"tsx-{UID}", "custom-keep", "s",
            "old-with-socket", "old-cwd", "old-open", "old-fresh-inside", "new", "new-extracted",
        })
        self.assertTrue((self.root / "link").is_symlink())
        self.assertEqual((self.outside / "target/precious").read_text(), "keep me")
        self.assertRegex(self.log(), r"pass dry_run=0 root=\S+ removed=3 kept=12 in_use=\d+ busy_inside=\d+ failed=0")

    def test_dry_run_only_logs(self):
        self.build_fixtures()
        before = self.names()
        self.state.mkdir()
        (self.state / "janitor.log").write_text("old line\n" * 40_000)
        result = self.run_janitor("--once", env=self.env(
            CADDIE_TEMP_JANITOR="1", CADDIE_TEMP_JANITOR_DRY_RUN="1"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.names(), before)
        log = self.log()
        for name in ("old-plain", "old-file", "old-with-link", "custom-keep"):
            self.assertIn(f"dry-run would remove {self.root}/{name}\n", log)
        self.assertNotIn("old-cwd\n", log)
        self.assertIn("would_remove=4", log)
        self.assertNotIn("old line", log)
        self.assertTrue((self.state / "janitor.log.1").exists())
        self.assertEqual(result.stderr, "")

    def test_names_with_trailing_whitespace_resolve_to_themselves(self):
        self.make_dir("twin ")
        (self.root / "file\t").write_text("x")
        (self.root / f"claude-{UID} ").mkdir()
        time.sleep(AGE_SECONDS + 1.5)
        (self.root / "twin").mkdir()
        (self.root / "file").write_text("x")
        (self.root / f"claude-{UID}").mkdir()
        self.run_janitor("--once", env=self.env(CADDIE_TEMP_JANITOR="1"))
        self.assertEqual(self.names(), {"twin", "file", f"claude-{UID}"})

    @unittest.skipUnless(Path("/proc/self/maps").exists(), "memory maps are read from /proc")
    def test_memory_mapped_files_are_kept(self):
        mapped = self.make_dir("old-mapped")
        (mapped / "lib.so").write_bytes(b"x" * 4096)
        script = ("import mmap,sys,time\n"
                  "f = open(sys.argv[1], 'rb'); m = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)\n"
                  "f.close(); print('ready', flush=True); time.sleep(300)")
        child = subprocess.Popen(["python3", "-c", script, str(mapped / "lib.so")],
                                 stdout=subprocess.PIPE, text=True)
        self.children.append(child)
        self.assertEqual(child.stdout.readline().strip(), "ready")
        time.sleep(AGE_SECONDS + 1.5)
        self.run_janitor("--once", env=self.env(CADDIE_TEMP_JANITOR="1"))
        self.assertEqual(self.names(), {"old-mapped"})

    def test_once_refuses_while_a_janitor_holds_the_lock(self):
        env = self.env(CADDIE_TEMP_JANITOR="1", CADDIE_TEMP_JANITOR_INTERVAL="1h")
        self.run_janitor(env=env)
        self.assertIsNotNone(self.settled_janitor())
        result = self.run_janitor("--once", env=env)
        self.assertEqual(result.returncode, 1)
        self.assertIn("another janitor", result.stderr)
        dry = self.run_janitor("--once", env={**env, "CADDIE_TEMP_JANITOR_DRY_RUN": "1"})
        self.assertEqual(dry.returncode, 0, dry.stderr)

    @unittest.skipUnless(os.geteuid() == 0, "chown to another user needs root")
    def test_other_users_files_are_kept(self):
        foreign = self.make_dir("foreign")
        os.chown(foreign, 65534, 65534)
        nested = self.make_dir("nested-foreign")
        os.chown(nested / "file", 65534, 65534)
        time.sleep(AGE_SECONDS + 1.5)
        self.run_janitor("--once", env=self.env(CADDIE_TEMP_JANITOR="1"))
        self.assertEqual(self.names(), {"foreign", "nested-foreign"})

    def test_refuses_unexpected_roots(self):
        cases = {
            "/": {},
            str(ROOT): {},
            str(Path.home()): {},
            str(self.root): {"RAILWAY_VOLUME_MOUNT_PATH": str(self.base)},
        }
        self.make_dir("old")
        time.sleep(AGE_SECONDS + 1.5)
        for root, extra in cases.items():
            with self.subTest(root=root):
                result = self.run_janitor("--once", env=self.env(
                    CADDIE_TEMP_JANITOR="1", CADDIE_TEMP_JANITOR_TEST_ROOT=root, **extra))
                self.assertEqual(result.returncode, 1)
                self.assertIn("refusing to run", self.log())
        self.assertEqual(self.names(), {"old"})

    def test_off_without_an_enabling_variable(self):
        self.make_dir("old")
        time.sleep(AGE_SECONDS + 1.5)
        for extra in ({}, {"CADDIE_TEMP_JANITOR": "0", "RAILWAY_SERVICE_ID": "svc"}):
            with self.subTest(env=extra):
                hook = self.run_janitor(env=self.env(**extra))
                self.assertEqual((hook.returncode, hook.stdout, hook.stderr), (0, "", ""))
                self.assertEqual(self.run_janitor("--once", env=self.env(**extra)).returncode, 1)
        time.sleep(1)
        self.assertFalse(self.state.exists())
        self.assertEqual(janitor_pids(str(self.state)), [])
        self.assertEqual(self.names(), {"old"})

    def test_railway_hook_starts_a_silent_janitor(self):
        self.make_dir("old")
        time.sleep(AGE_SECONDS + 1.5)
        started = time.monotonic()
        hook = subprocess.run(["bash", str(JANITOR)], env=self.env(RAILWAY_SERVICE_ID="svc"),
                              input=json.dumps({"hook_event_name": "SessionStart"}),
                              capture_output=True, text=True, timeout=10)
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual((hook.returncode, hook.stdout, hook.stderr), (0, "", ""))
        self.assertTrue(wait_for(lambda: "removed=1" in self.log()), self.log())
        self.assertEqual(self.names(), set())
        self.assertEqual(len(janitor_pids(str(self.state))), 1)

    def test_concurrent_hooks_leave_one_janitor(self):
        env = self.env(CADDIE_TEMP_JANITOR="1", CADDIE_TEMP_JANITOR_INTERVAL="1h")
        hooks = [subprocess.Popen(["bash", str(JANITOR)], env=env, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) for _ in range(12)]
        for hook in hooks:
            stdout, stderr = hook.communicate(timeout=10)
            self.assertEqual((hook.returncode, stdout, stderr), (0, b"", b""))
        self.assertIsNotNone(self.settled_janitor())
        time.sleep(1)
        pids = janitor_pids(str(self.state))
        self.assertEqual(len(pids), 1)
        self.assertEqual((self.state / "lock").read_text().strip(), str(pids[0]))
        self.assertEqual(self.log().count(" started "), 1, self.log())

        self.run_janitor(env=env)
        time.sleep(1)
        self.assertEqual(janitor_pids(str(self.state)), pids)

        os.kill(pids[0], signal.SIGTERM)
        self.assertTrue(wait_for(lambda: not janitor_pids(str(self.state)), timeout=5))
        self.assertFalse((self.state / "lock").exists())
        self.assertIn(" stopped", self.log())

    def test_stale_lock_is_taken_over(self):
        dead = subprocess.Popen(["true"])
        dead.wait()
        impostor = subprocess.Popen(["sleep", "300"])
        self.children.append(impostor)
        env = self.env(CADDIE_TEMP_JANITOR="1", CADDIE_TEMP_JANITOR_INTERVAL="1h")
        for holder in (dead.pid, impostor.pid):
            with self.subTest(holder=holder):
                self.state.mkdir(exist_ok=True)
                (self.state / "lock").write_text(f"{holder}\n")
                self.assertEqual(self.run_janitor(env=env).stdout, "")
                pid = self.settled_janitor()
                self.assertIsNotNone(pid, self.log())
                self.assertNotEqual(pid, holder)
                os.kill(pid, signal.SIGTERM)
                self.assertTrue(wait_for(lambda: not janitor_pids(str(self.state)), timeout=5))

    def test_hook_is_wired_for_session_start(self):
        hooks = json.loads((ROOT / "hooks/hooks.json").read_text())["hooks"]["SessionStart"]
        commands = [hook["command"] for group in hooks for hook in group["hooks"]]
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/hooks/temp-janitor.sh"', commands)


if __name__ == "__main__":
    unittest.main()
