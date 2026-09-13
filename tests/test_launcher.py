#!/usr/bin/env python3
"""Behavior tests use disposable repositories and a dedicated tmux server."""
import os
import json
from pathlib import Path
import shutil
import shlex
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
TMUX = shutil.which("tmux")


@unittest.skipUnless(TMUX, "tmux is required for isolated integration tests")
class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-dev-launcher-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.project = self.base / "project"
        self.project.mkdir()
        self.socket = "ai-dev-test-" + self.base.name
        self.env = dict(os.environ, AI_DEV_TMUX_SOCKET=self.socket,
                        PATH=str(self.bin) + os.pathsep + os.environ["PATH"])
        for key in ("TMUX", "BASH_ENV", "ENV"):
            self.env.pop(key, None)
        self.stub("lazygit", "exit 0\n")
        self.stub("claude", self.record_cli_args("claude"))
        self.stub("codex", 'if [ "$1" = debug ]; then exit 1; fi\n'
                  + self.record_cli_args("codex"))
        self.tmux("-f", "/dev/null", "new-session", "-d", "-s", "harness", "/bin/sh")
        self.addCleanup(lambda: subprocess.run(
            [TMUX, "-L", self.socket, "kill-server"], capture_output=True))
        self.tmux("set-option", "-g", "default-shell", "/bin/bash")
        self.tmux("set-option", "-g", "default-command", "/bin/bash --noprofile --norc")

    def stub(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/bash\n" + body)
        path.chmod(0o755)

    @staticmethod
    def record_cli_args(name):
        # Per-pane records prove that every launcher receives the right flags.
        return (f'printf "%s\\n" "$@" > "$PWD/.{name}-args-$TMUX_PANE.tmp"\n'
                f'mv "$PWD/.{name}-args-$TMUX_PANE.tmp" "$PWD/{name}-args-$TMUX_PANE"\n'
                f'printf "%s\\n" "$@" > "$PWD/{name}-args"\n')

    def tmux(self, *args, check=True):
        return subprocess.run([TMUX, "-L", self.socket, *args], env=self.env,
                              text=True, capture_output=True, check=check)

    def dev(self, *args, project=None, check=True):
        result = subprocess.run(["bash", str(ROOT / "dev"), str(project or self.project),
                                 *args], env=self.env, text=True, capture_output=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def session(self, project=None):
        output = self.dev("--plan", "--no-ai", project=project).stdout
        return next(line.split(": ", 1)[1] for line in output.splitlines()
                    if line.startswith("Session:"))

    def wait_file(self, path):
        for _ in range(60):
            if path.exists():
                return path.read_text()
            time.sleep(0.05)
        self.fail("command did not write expected file: " + str(path))

    def wait_cli_calls(self, name, expected):
        for _ in range(60):
            records = sorted(self.project.glob(name + "-args-%*"))
            if len(records) >= expected:
                self.assertEqual(len(records), expected)
                return {path.name.rsplit("-", 1)[1]: path.read_text().splitlines()
                        for path in records}
            time.sleep(0.05)
        self.fail(f"expected {expected} {name} launches; found {len(records)}")

    def test_same_basename_and_git_subdirectory_identity(self):
        other = self.base / "other" / "project"
        other.mkdir(parents=True)
        self.assertNotEqual(self.session(), self.session(other))
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        sub = self.project / "backend"
        sub.mkdir()
        self.assertEqual(self.session(), self.session(sub))

    def test_reuse_and_unverified_session_protection(self):
        self.dev("--no-ai", "--detached")
        session = self.session()
        before = self.tmux("list-panes", "-s", "-t", "=" + session).stdout
        self.dev("--no-ai", "--detached")
        self.assertEqual(before, self.tmux("list-panes", "-s", "-t", "=" + session).stdout)
        self.tmux("new-session", "-d", "-s", "unverified")
        result = self.dev("--session", "unverified", "--detached", "--no-ai", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unverified directory", result.stderr)
        self.assertEqual(self.tmux("has-session", "-t", "=unverified").returncode, 0)

    def test_focused_layout_and_context(self):
        self.dev("--no-ai", "--detached", "--layout", "focus")
        session = self.session()
        names = self.tmux("list-windows", "-t", "=" + session, "-F", "#{window_name}").stdout
        self.assertEqual(names.splitlines(), ["ai", "app", "services", "test", "git"])
        self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                  "@ai_project").stdout.strip(), str(self.project.resolve()))
        self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                  "@ai_ready").stdout.strip(), "1")
        ports = self.tmux("show-environment", "-t", "=" + session).stdout
        self.assertIn("BACKEND_PORT=", ports)
        self.assertIn("COMPOSE_PROJECT_NAME=", ports)
        self.assertFalse((self.project / "codex-args").exists())

    def test_default_classic_layout_and_deep_profile_without_ai(self):
        self.dev("--no-ai", "--detached")
        session = self.session()
        windows = self.tmux("list-windows", "-t", "=" + session, "-F",
                            "#{window_name}\t#{window_panes}").stdout.splitlines()
        self.assertEqual(windows, ["codex\t2", "codex-claude\t2",
                                   "backend-frontend\t2", "services\t1",
                                   "test\t1", "git\t1"])
        self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                  "@ai_layout").stdout.strip(), "classic")
        self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                  "@ai_profile").stdout.strip(), "deep")
        panes = self.tmux("list-panes", "-s", "-t", "=" + session,
                          "-F", "#{pane_id}").stdout.splitlines()
        self.assertEqual(len(panes), 9)
        self.assertFalse(list(self.project.glob("codex-args*")))
        self.assertFalse(list(self.project.glob("claude-args*")))

    def test_classic_launches_three_codex_and_normal_claude(self):
        self.dev("--detached")
        codex_calls = self.wait_cli_calls("codex", 3)
        claude_calls = self.wait_cli_calls("claude", 1)
        for args in codex_calls.values():
            self.assertIn("--dangerously-bypass-approvals-and-sandbox", args)
        claude_args = next(iter(claude_calls.values()))
        self.assertNotIn("--permission-mode", claude_args)
        self.assertNotIn("plan", claude_args)
        self.assertNotIn("--dangerously-skip-permissions", claude_args)

    def test_classic_no_codex_keeps_claude(self):
        self.dev("--detached", "--no-codex")
        self.wait_cli_calls("claude", 1)
        self.assertFalse(list(self.project.glob("codex-args*")))

    def test_classic_unsafe_also_enables_claude_permission_bypass(self):
        self.dev("--detached", "--unsafe")
        for args in self.wait_cli_calls("codex", 3).values():
            self.assertIn("--dangerously-bypass-approvals-and-sandbox", args)
        claude_args = next(iter(self.wait_cli_calls("claude", 1).values()))
        self.assertIn("--dangerously-skip-permissions", claude_args)
        self.assertNotIn("--permission-mode", claude_args)

    def test_restore_focus_retains_panes_and_running_ai_and_is_idempotent(self):
        self.stub("codex", 'if [ "$1" = debug ]; then exit 1; fi\n'
                  + self.record_cli_args("codex")
                  + 'printf "%s\\n" "$$" > "$PWD/codex-process-$TMUX_PANE"\n'
                  'exec sleep 120\n')
        self.dev("--detached", "--layout", "focus", "--profile", "standard")
        session = self.session()
        original_calls = self.wait_cli_calls("codex", 1)
        primary_pane = next(iter(original_calls))
        process_file = self.project / ("codex-process-" + primary_pane)
        original_process = int(self.wait_file(process_file))
        os.kill(original_process, 0)
        before = self.tmux("list-panes", "-s", "-t", "=" + session, "-F",
                           "#{pane_id}\t#{pane_pid}").stdout.splitlines()
        self.dev("--detached", "--restore-layout")
        self.assertEqual(self.tmux("list-windows", "-t", "=" + session, "-F",
                                   "#{window_name}\t#{window_panes}").stdout.splitlines(),
                         ["codex\t2", "codex-claude\t2", "backend-frontend\t2",
                          "services\t1", "test\t1", "git\t1"])
        after = self.tmux("list-panes", "-s", "-t", "=" + session, "-F",
                          "#{pane_id}\t#{pane_pid}").stdout.splitlines()
        self.assertEqual(len(after), 9)
        self.assertTrue(set(before).issubset(after))
        self.assertEqual(int(process_file.read_text()), original_process)
        os.kill(original_process, 0)
        self.wait_cli_calls("codex", 3)
        self.wait_cli_calls("claude", 1)
        self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                  "@ai_layout").stdout.strip(), "classic")
        self.dev("--detached", "--restore-layout")
        self.assertEqual(self.tmux("list-panes", "-s", "-t", "=" + session, "-F",
                                   "#{pane_id}\t#{pane_pid}").stdout.splitlines(), after)
        self.assertEqual(int(process_file.read_text()), original_process)
        os.kill(original_process, 0)

    def test_restore_focus_no_ai_starts_no_new_ai(self):
        self.dev("--detached", "--layout", "focus", "--no-ai")
        self.dev("--detached", "--restore-layout", "--no-ai")
        self.assertEqual(len(self.tmux("list-panes", "-s", "-t", "=" + self.session(),
                                       "-F", "#{pane_id}").stdout.splitlines()), 9)
        self.assertFalse(list(self.project.glob("codex-args*")))
        self.assertFalse(list(self.project.glob("claude-args*")))

    def test_restore_modified_focus_refuses_without_changes(self):
        self.dev("--detached", "--layout", "focus", "--no-ai")
        session = self.session()
        self.tmux("split-window", "-h", "-t", "=" + session + ":ai")
        before = self.tmux("list-panes", "-s", "-t", "=" + session, "-F",
                           "#{window_name}\t#{pane_id}\t#{pane_pid}").stdout
        result = self.dev("--detached", "--restore-layout", "--no-ai", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tmux("list-panes", "-s", "-t", "=" + session, "-F",
                                   "#{window_name}\t#{pane_id}\t#{pane_pid}").stdout, before)
        self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                  "@ai_layout").stdout.strip(), "focus")

    def test_restore_failures_roll_back_only_new_panes(self):
        self.dev("--detached", "--layout", "focus", "--no-ai")
        session = self.session()
        snapshot_format = "#{window_index}\t#{window_name}\t#{pane_id}\t#{pane_pid}"
        before = self.tmux("list-panes", "-s", "-t", "=" + session,
                           "-F", snapshot_format).stdout
        for failure in ("split-window", "rename-window*backend-frontend"):
            with self.subTest(failure=failure):
                self.stub("tmux", 'case "$*" in *' + failure + '*) exit 23 ;; esac\n'
                          'exec "' + TMUX + '" "$@"\n')
                result = self.dev("--detached", "--restore-layout", "--no-ai", check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.tmux("list-panes", "-s", "-t", "=" + session,
                                           "-F", snapshot_format).stdout, before)
                self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                          "@ai_layout").stdout.strip(), "focus")

    def test_labels_keep_chinese_and_roles_survive_title_changes(self):
        project = self.base / "中文项目"
        project.mkdir()
        self.dev("--no-ai", "--detached", "--layout", "focus", project=project)
        session = self.session(project)
        self.assertEqual(self.tmux("show-options", "-qv", "-t", "=" + session + ":",
                                  "@ai_label").stdout.strip(), "中文项目")
        target = "=" + session + ":ai"
        self.tmux("select-pane", "-t", target, "-T", "Application changed title")
        self.assertEqual(self.tmux("show-options", "-pqv", "-t", target,
                                  "@ai_role").stdout.strip(), "Implement")

    def test_config_is_data_and_commands_need_start(self):
        marker = self.project / "started"
        (self.project / ".ai-dev.conf").write_text(
            'backend_cmd=printf "%s" "$BACKEND_PORT" > started\nbackend_port=21123\n')
        self.dev("--plan")
        self.assertFalse(marker.exists())
        self.dev("--no-ai", "--detached")
        self.assertFalse(marker.exists())
        self.dev("--no-ai", "--detached", "--start", "--session", "with-start")
        self.assertEqual(self.wait_file(marker), "21123")

    def test_invalid_config_never_executes_substitution(self):
        marker = self.project / "injected"
        (self.project / ".ai-dev.conf").write_text("layout=$(touch " + str(marker) + ")\n")
        result = self.dev("--plan", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(marker.exists())
        (self.project / ".ai-dev.conf").write_text("layout=focus\nlayout=full\n")
        self.assertIn("duplicate key", self.dev("--plan", check=False).stderr)

    def test_relative_commands_and_invalid_ports(self):
        backend = self.project / "backend"
        backend.mkdir()
        runner = backend / "start"
        runner.write_text("#!/bin/sh\nexit 0\n")
        runner.chmod(0o755)
        (self.project / ".ai-dev.conf").write_text("backend_cmd=./start\n")
        self.dev("--check")
        (self.project / ".ai-dev.conf").write_text("backend_cmd=./dev\n")
        self.assertNotEqual(self.dev("--check", check=False).returncode, 0)
        (self.project / ".ai-dev.conf").write_text("backend_port=02000\nfrontend_port=2000\n")
        self.assertNotEqual(self.dev("--check", check=False).returncode, 0)

    def test_resume_uses_picker_and_review_is_plan_mode(self):
        self.dev("--detached", "--resume", "--layout", "pair")
        args = self.wait_file(self.project / "codex-args")
        self.assertIn("resume", args)
        self.assertNotIn("--last", args)
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", args)
        review = self.wait_file(self.project / "claude-args")
        self.assertIn("--permission-mode\nplan", review)
        self.assertIn("--resume", review)
        self.assertNotIn("dangerously", review)

    def test_full_explore_inherits_codex_settings_without_resuming_writer(self):
        (self.project / ".ai-dev.conf").write_text(
            "codex_model=test-model\ncodex_effort=ultra\ncodex_fast=1\n"
            "codex_session=writer-session\n")
        self.dev("--detached", "--resume", "--layout", "full")
        calls = self.wait_cli_calls("codex", 2)
        session = self.session()
        writer_pane = self.tmux("display-message", "-p", "-t", "=" + session + ":ai",
                                "#{pane_id}").stdout.strip()
        explore_pane = self.tmux("display-message", "-p", "-t", "=" + session + ":explore",
                                 "#{pane_id}").stdout.strip()
        writer_args, explore_args = calls[writer_pane], calls[explore_pane]
        self.assertEqual(writer_args[:2], ["resume", "writer-session"])
        self.assertEqual(writer_args[2:], explore_args)
        self.assertNotIn("resume", explore_args)
        self.assertNotIn("writer-session", explore_args)
        self.assertNotIn("--sandbox", explore_args)
        self.assertIn("--model\ntest-model", "\n".join(explore_args))
        self.assertIn("model_reasoning_effort=ultra", explore_args)
        self.assertIn("service_tier=fast", explore_args)
        self.assertIn("fast_mode", explore_args)
        self.assertIn("multi_agent", explore_args)
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", explore_args)
        review = self.wait_file(self.project / "claude-args")
        self.assertIn("--permission-mode\nplan", review)
        self.assertNotIn("dangerously", review)

    def test_catalog_failure_uses_cli_defaults(self):
        self.dev("--detached", "--profile", "deep", "--layout", "focus")
        args = self.wait_file(self.project / "codex-args")
        self.assertNotIn("--model", args)
        self.assertNotIn("model_reasoning_effort", args)

    @unittest.skipUnless(Path("/usr/bin/plutil").exists(), "macOS catalog parser")
    def test_classic_resume_preserves_deep_settings_for_all_codex(self):
        catalog = {"models": [
            {"slug": "hidden-model", "visibility": "hide", "priority": 0},
            {"slug": "test-model", "visibility": "list", "priority": 1,
             "supported_reasoning_levels": [{"effort": "high"}, {"effort": "ultra"}],
             "additional_speed_tiers": ["fast"]},
            {"slug": "other-model", "visibility": "list", "priority": 5}
        ]}
        self.stub("codex", 'if [ "$1" = debug ]; then printf "%s\\n" '
                  + shlex.quote(json.dumps(catalog)) + '; exit 0; fi\n'
                  + self.record_cli_args("codex"))
        (self.project / ".ai-dev.conf").write_text("codex_session=writer-session\n")
        self.dev("--detached", "--resume")
        calls = self.wait_cli_calls("codex", 3)
        resumed = [args for args in calls.values() if args[0] == "resume"]
        fresh = [args for args in calls.values() if args[0] != "resume"]
        self.assertEqual(len(resumed), 1)
        self.assertEqual(len(fresh), 2)
        self.assertEqual(resumed[0][:2], ["resume", "writer-session"])
        self.assertEqual(resumed[0][2:], fresh[0])
        self.assertEqual(fresh[0], fresh[1])
        self.assertNotIn("writer-session", fresh[0])
        for args in calls.values():
            self.assertIn("--model\ntest-model", "\n".join(args))
            self.assertIn("model_reasoning_effort=ultra", args)
            self.assertIn("service_tier=fast", args)
            self.assertIn("fast_mode", args)
            self.assertIn("multi_agent", args)
            self.assertIn("--dangerously-bypass-approvals-and-sandbox", args)

    def test_partial_creation_is_removed_without_touching_other_sessions(self):
        self.stub("tmux", 'for arg in "$@"; do [ "$arg" != new-window ] || exit 23; done\n'
                  'exec "' + TMUX + '" "$@"\n')
        result = self.dev("--detached", "--no-ai", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(self.tmux("has-session", "-t", "=" + self.session(),
                                     check=False).returncode, 0)
        self.tmux("has-session", "-t", "=harness")


if __name__ == "__main__":
    unittest.main()
