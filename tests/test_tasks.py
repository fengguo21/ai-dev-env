"""Task lifecycle regressions using disposable repositories and fake tmux/dev."""
import os
from pathlib import Path
import pty
import select
import shutil
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ai-dev-task-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.tools = self.root / "tools"
        (self.tools / "lib").mkdir(parents=True)
        for name in ("task", "newtask", "lib/common.sh"):
            shutil.copy2(SOURCE / name, self.tools / name)
        self.mock = self.root / "mock"
        self.mock.mkdir()
        self.write_executable(self.mock / "tmux", """#!/usr/bin/env bash
case "$1" in
  has-session) [ -n "${TEST_SESSION:-}" ] && [ "$3" = "=$TEST_SESSION" ] ;;
  list-sessions) [ -z "${TEST_SESSION_PROJECT:-}" ] || printf 'custom-session\\t%s\\n' "$TEST_SESSION_PROJECT" ;;
  list-panes) [ -z "${TEST_PANE_PATH:-}" ] || printf 'legacy-session\\t%s\\n' "$TEST_PANE_PATH" ;;
  *) exit 90 ;;
esac
""")
        self.write_executable(self.tools / "dev", "#!/usr/bin/env bash\nprintf 'DEV_ARG=%s\\n' \"$@\"\n")
        self.env = dict(os.environ)
        for name in ("AI_WORKTREE_ROOT", "AI_DEV_TMUX_SOCKET", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            self.env.pop(name, None)
        self.env.update({
            "PATH": str(self.mock) + os.pathsep + self.env["PATH"],
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Task tests",
            "GIT_AUTHOR_EMAIL": "tests@example.invalid",
            "GIT_COMMITTER_NAME": "Task tests",
            "GIT_COMMITTER_EMAIL": "tests@example.invalid",
        })
        self.repo = self.make_repo("project")

    @staticmethod
    def write_executable(path, content):
        path.write_text(content)
        path.chmod(0o755)

    def run_cmd(self, *args, cwd=None, env=None, check=True):
        result = subprocess.run(
            args, cwd=cwd or self.repo, env=env or self.env,
            text=True, capture_output=True, timeout=20,
        )
        if check and result.returncode:
            self.fail(f"{args!r} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
        return result

    def make_repo(self, name):
        path = self.root / name
        self.run_cmd("git", "init", "-q", "-b", "main", str(path), cwd=self.root)
        self.run_cmd("git", "commit", "--allow-empty", "-qm", "initial", cwd=path)
        return path

    def new(self, name="auth", cwd=None, env=None):
        result = self.run_cmd(str(self.tools / "newtask"), "--print-path", name, cwd=cwd, env=env)
        return Path(result.stdout.strip())

    def task(self, *args, **kwargs):
        return self.run_cmd(str(self.tools / "task"), *args, **kwargs)

    def task_pty(self, *args):
        master, slave = pty.openpty()
        try:
            process = subprocess.Popen(
                [str(self.tools / "task"), *args], cwd=self.repo, env=self.env,
                stdin=slave, stdout=slave, stderr=subprocess.PIPE,
            )
            _, errors = process.communicate(timeout=20)
            chunks = []
            # Keep our slave descriptor open until output is drained: macOS
            # can discard buffered PTY output when the last slave closes.
            while select.select([master], [], [], 0.2)[0]:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
            self.assertEqual(process.returncode, 0, errors.decode())
            return b"".join(chunks).decode()
        finally:
            if slave is not None:
                os.close(slave)
            os.close(master)

    def branch_exists(self, name="auth"):
        return self.run_cmd("git", "show-ref", "--verify", "--quiet", "refs/heads/feature/" + name, check=False).returncode == 0

    def mark_remote(self, ref="HEAD"):
        commit = self.run_cmd("git", "rev-parse", ref).stdout.strip()
        self.run_cmd("git", "update-ref", "refs/remotes/origin/main", commit)

    def test_shared_root_namespaces_same_named_repositories(self):
        other = self.make_repo("other/project")
        env = dict(self.env, AI_WORKTREE_ROOT=str(self.root / "shared"))
        first = self.new(env=env)
        second = self.new(cwd=other, env=env)
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_dir())
        self.assertTrue(second.is_dir())

    def test_relative_root_is_relative_to_caller_and_prints_real_absolute_path(self):
        nested = self.repo / "src"
        nested.mkdir()
        path = self.new(cwd=nested, env=dict(self.env, AI_WORKTREE_ROOT=".worktrees"))
        self.assertTrue(path.is_absolute())
        self.assertTrue(path.is_dir())
        self.assertEqual(path.parent.parent, nested / ".worktrees")

    def test_preexisting_target_does_not_create_branch(self):
        occupied = self.root / "project_worktrees" / "auth"
        occupied.mkdir(parents=True)
        (occupied / "mine").write_text("preserve")
        result = self.run_cmd(str(self.tools / "newtask"), "auth", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.branch_exists())
        self.assertEqual((occupied / "mine").read_text(), "preserve")

    def test_failed_checkout_rolls_back_new_branch(self):
        real_git = shutil.which("git")
        self.write_executable(self.mock / "git", """#!/usr/bin/env bash
for arg in "$@"; do
  if [ "${previous:-}" = worktree ] && [ "$arg" = add ]; then exit 72; fi
  previous="$arg"
done
exec "$TEST_REAL_GIT" "$@"
""")
        self.env["TEST_REAL_GIT"] = real_git
        result = self.run_cmd(str(self.tools / "newtask"), "auth", check=False)
        self.assertEqual(result.returncode, 72)
        self.assertFalse(self.branch_exists())

    def test_failed_checkout_preserves_existing_branch(self):
        self.run_cmd("git", "branch", "feature/auth")
        real_git = shutil.which("git")
        self.write_executable(self.mock / "git", """#!/usr/bin/env bash
for arg in "$@"; do
  if [ "${previous:-}" = worktree ] && [ "$arg" = add ]; then exit 72; fi
  previous="$arg"
done
exec "$TEST_REAL_GIT" "$@"
""")
        self.env["TEST_REAL_GIT"] = real_git
        self.assertEqual(self.run_cmd(str(self.tools / "newtask"), "auth", check=False).returncode, 72)
        self.assertTrue(self.branch_exists())

    def test_existing_branch_rejects_explicit_base_instead_of_ignoring_it(self):
        self.run_cmd("git", "branch", "feature/auth")
        result = self.run_cmd(str(self.tools / "newtask"), "auth", "HEAD", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("omit BASE_REF", result.stderr)
        self.assertTrue(self.branch_exists())

    def test_repeated_task_reports_open_and_keeps_worktree(self):
        path = self.new()
        result = self.run_cmd(str(self.tools / "newtask"), "auth", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("task open auth", result.stderr)
        self.assertTrue(path.is_dir())

    def test_open_locates_legacy_registered_path_and_forwards_options(self):
        path = self.root / "old tasks" / "auth"
        self.run_cmd("git", "worktree", "add", "-b", "feature/auth", str(path))
        result = self.task("open", "auth", "--resume", "--profile", "deep")
        self.assertIn("DEV_ARG=" + str(path), result.stdout)
        self.assertIn("DEV_ARG=--resume", result.stdout)
        self.assertIn("DEV_ARG=deep", result.stdout)

    def test_new_can_open_or_only_create(self):
        result = self.task("new", "auth", "--no-open")
        self.assertNotIn("DEV_ARG=", result.stdout)
        result = self.task("new", "billing", "--no-ai", "--detached")
        self.assertIn("DEV_ARG=--no-ai", result.stdout)
        self.assertIn("DEV_ARG=--detached", result.stdout)

    def test_list_shows_dirty_and_custom_session(self):
        path = self.new()
        (path / "scratch").write_text("work")
        result = self.task("list", env=dict(self.env, TEST_SESSION_PROJECT=str(path)))
        self.assertIn("auth\tfeature/auth\tdirty\tcustom-session\t", result.stdout)

    def test_pick_opens_selected_task_in_interactive_terminal(self):
        path = self.new()
        self.new("billing")
        self.write_executable(self.mock / "fzf", "#!/usr/bin/env bash\nsed -n '2p'\n")
        output = self.task_pty("pick", "--resume")
        self.assertIn("DEV_ARG=" + str(path), output)
        self.assertIn("DEV_ARG=--resume", output)

    def test_pick_without_terminal_lists_tasks_even_if_fzf_is_installed(self):
        self.new()
        self.write_executable(self.mock / "fzf", "#!/usr/bin/env bash\nexit 90\n")
        result = self.task("pick")
        self.assertIn("auth\tfeature/auth", result.stdout)
        self.assertIn("task open NAME", result.stdout)
        self.assertNotIn("DEV_ARG=", result.stdout)

    def test_done_default_is_preview_and_clean_merged_remote_task_is_removable(self):
        path = self.new()
        self.mark_remote()
        result = self.task("done", "auth")
        self.assertIn("Ready.", result.stdout)
        self.assertTrue(path.is_dir())
        self.task("done", "auth", "--apply")
        self.assertFalse(path.exists())
        self.assertFalse(self.branch_exists())

    def test_done_blocks_dirty_even_with_allow_flags(self):
        path = self.new()
        (path / "scratch").write_text("keep this")
        result = self.task("done", "auth", "--apply", "--allow-unpushed", "--allow-ignored", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("uncommitted or untracked", result.stdout)
        self.assertEqual((path / "scratch").read_text(), "keep this")

    def test_done_blocks_unmerged_even_with_allow_unpushed(self):
        path = self.new()
        self.run_cmd("git", "commit", "--allow-empty", "-qm", "not merged", cwd=path)
        result = self.task("done", "auth", "--apply", "--allow-unpushed", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not merged", result.stdout)
        self.assertTrue(path.exists())

    def test_done_requires_remote_or_explicit_allow_and_supports_keep_branch(self):
        path = self.new()
        result = self.task("done", "auth", "--apply", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no remote-tracking ref", result.stdout)
        self.task("done", "auth", "--apply", "--allow-unpushed", "--keep-branch")
        self.assertFalse(path.exists())
        self.assertTrue(self.branch_exists())

    def test_done_blocks_custom_tmux_session_even_after_panes_move(self):
        path = self.new()
        result = self.task("done", "auth", "--apply", "--allow-unpushed", env=dict(self.env, TEST_SESSION_PROJECT=str(path)), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("custom-session", result.stdout)
        self.assertTrue(path.exists())

    def test_done_blocks_legacy_session_by_pane_directory(self):
        path = self.new()
        result = self.task("done", "auth", "--apply", "--allow-unpushed", env=dict(self.env, TEST_PANE_PATH=str(path / "src")), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("legacy-session", result.stdout)
        self.assertTrue(path.exists())

    def test_done_ignored_env_requires_explicit_permission(self):
        (self.repo / ".gitignore").write_text(".env\n")
        self.run_cmd("git", "add", ".gitignore")
        self.run_cmd("git", "commit", "-qm", "ignore local environment")
        path = self.new()
        (path / ".env").write_text("LOCAL_ONLY=example\n")
        result = self.task("done", "auth", "--apply", "--allow-unpushed", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ignored files", result.stdout)
        self.assertTrue((path / ".env").exists())
        self.task("done", "auth", "--apply", "--allow-unpushed", "--allow-ignored")
        self.assertFalse(path.exists())

    def test_primary_worktree_cannot_be_removed(self):
        self.run_cmd("git", "branch", "-m", "feature/auth")
        result = self.task("done", "auth", "--apply", "--allow-unpushed", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("primary worktree", result.stderr)
        self.assertTrue(self.repo.exists())

    def test_locked_worktree_is_never_force_removed(self):
        path = self.new()
        self.run_cmd("git", "worktree", "lock", "--reason", "keep it", str(path))
        result = self.task("done", "auth", "--apply", "--allow-unpushed", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(path.exists())
        self.assertTrue(self.branch_exists())

    def test_cleanup_refuses_path_replaced_by_another_repository(self):
        path = self.new()
        shutil.move(path, self.root / "saved-original-worktree")
        self.run_cmd("git", "init", "-q", "-b", "main", str(path))
        self.run_cmd("git", "commit", "--allow-empty", "-qm", "different repository", cwd=path)
        result = self.task("done", "auth", "--apply", "--allow-unpushed", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another repository", result.stderr)
        self.assertTrue(path.exists())
        self.assertTrue(self.branch_exists())

    def test_invalid_task_does_not_create_branch(self):
        for name in ("..", ".", "../escape", "bad name"):
            with self.subTest(name=name):
                result = self.run_cmd(str(self.tools / "newtask"), name, check=False)
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
