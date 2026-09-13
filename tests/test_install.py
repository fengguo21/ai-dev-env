#!/usr/bin/env python3
"""Installer/doctor regressions using disposable destinations, never the real HOME."""

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest
import uuid


REPOSITORY = Path(__file__).resolve().parents[1]
REAL_TMUX = shutil.which("tmux")
REAL_MV = shutil.which("mv")
REAL_GHOSTTY = shutil.which("ghostty") or (
    "/Applications/Ghostty.app/Contents/MacOS/ghostty"
    if Path("/Applications/Ghostty.app/Contents/MacOS/ghostty").is_file() else None
)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ai-dev-install-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.target = self.root / "destination"
        self.bin = self.root / "bin"
        self.source.mkdir()
        self.target.mkdir()
        self.bin.mkdir()
        for script in ("install.sh", "uninstall.sh", "doctor"):
            shutil.copy2(REPOSITORY / script, self.source / script)
        self.write(self.source / "config/tmux.conf", "set -g prefix C-a\nsource-file -q ~/.tmux.local.conf\nrun-shell 'echo tpm/tpm should-never-run'\n")
        self.write(self.source / "config/ghostty.conf", "font-size = 15\nconfig-file = ?config.local\n")
        self.write(self.source / "lib/common.sh", "# shared helpers\n")
        for helper in ("dev", "newtask", "task"):
            self.write(self.source / helper, '#!/bin/bash\nif [ -n "${AI_DEV_CHECK_LOG:-}" ]; then printf "%s\\n" "$@" > "$AI_DEV_CHECK_LOG"; fi\nexit 0\n', executable=True)
        self.write(self.bin / "ghostty", """#!/bin/bash
case "$1" in
  +version) echo 'Ghostty test' ;;
  +list-fonts) echo 'JetBrainsMono Nerd Font Mono' ;;
  +list-themes) echo 'TokyoNight Night' ;;
  +validate-config)
    file="${2#--config-file=}"
    if grep 'invalid-ghostty' "$file" >/dev/null; then exit 1; fi ;;
  *) exit 1 ;;
esac
""", executable=True)
        self.write(self.bin / "tmux", """#!/bin/bash
printf '%s\\n' "$*" >> "$AI_DEV_TEST_LOG"
if [ "$1" = -V ]; then echo 'tmux test'; exit 0; fi
if [ "$1" != -L ]; then echo 'Unexpected default socket access' >&2; exit 99; fi
shift 2
if [ "$1" = source-file ] && grep 'definitely-invalid-option' "$2" >/dev/null; then
  echo 'invalid option: definitely-invalid-option' >&2
  exit 1
fi
# Like real tmux, startup returns 0 even with a bad startup configuration.
exit 0
""", executable=True)
        self.env = os.environ.copy()
        self.env.update(
            AI_DEV_HOME=str(self.target),
            AI_DEV_TEST_LOG=str(self.root / "tmux.log"),
            PATH=str(self.bin) + ":/usr/bin:/bin:/usr/sbin:/sbin",
        )

    @staticmethod
    def write(path, content, executable=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        if executable:
            path.chmod(0o755)

    @property
    def state(self):
        return self.target / ".local/state/ai-dev-env"

    def run_script(self, name, *arguments, success=True):
        result = subprocess.run(
            ["/bin/bash", str(self.source / name), *arguments],
            env=self.env, text=True, capture_output=True, timeout=30,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def install(self, **options):
        return self.run_script("install.sh", "--skip-deps", "--no-reload", **options)

    def test_invalid_candidate_does_not_replace_existing_files(self):
        self.write(self.target / ".tmux.conf", "original tmux\n")
        self.write(self.target / ".config/ghostty/config", "original ghostty\n")
        self.write(self.source / "config/tmux.conf", "set -g definitely-invalid-option on\n")
        self.install(success=False)
        self.assertEqual((self.target / ".tmux.conf").read_text(), "original tmux\n")
        self.assertEqual((self.target / ".config/ghostty/config").read_text(), "original ghostty\n")
        self.assertFalse((self.target / ".local/bin/dev").exists())
        self.assertFalse((self.state / "last-backup").exists())
        commands = (self.root / "tmux.log").read_text()
        self.assertIn("-f /dev/null new-session", commands)
        self.assertIn("source-file", commands)
        self.assertIn("kill-server", commands)

    def test_bad_local_override_also_blocks_replacement(self):
        self.write(self.target / ".tmux.conf", "original tmux\n")
        self.write(self.target / ".tmux.local.conf", "set -g definitely-invalid-option on\n")
        self.install(success=False)
        self.assertEqual((self.target / ".tmux.conf").read_text(), "original tmux\n")

    def test_failure_halfway_through_apply_restores_files_and_manifests(self):
        originals = {
            ".tmux.conf": "original tmux\n",
            ".config/ghostty/config": "original ghostty\n",
            ".local/bin/dev": "original dev\n",
            ".local/bin/task": "original task\n",
            ".zshrc": "export USER_SETTING=kept\n",
            ".local/state/ai-dev-env/last-backup": "original manifest\n",
            ".local/state/ai-dev-env/installed-dev.sha256": "original fingerprint\n",
        }
        for relative, content in originals.items():
            self.write(self.target / relative, content)
        self.write(self.bin / "mv", """#!/bin/bash
for argument in "$@"; do destination="$argument"; done
if [ "$destination" = "$AI_DEV_HOME/.local/bin/task" ]; then
  echo 'Simulated write failure' >&2
  exit 73
fi
exec """ + shlex.quote(REAL_MV) + ' "$@"\n', executable=True)
        result = self.run_script("install.sh", "--skip-deps", "--no-reload", "--replace-modified", success=False)
        self.assertIn("restoring the previous managed files", result.stdout)
        for relative, content in originals.items():
            self.assertEqual((self.target / relative).read_text(), content, relative)
        self.assertFalse((self.target / ".local/bin/newtask").exists())
        self.assertFalse((self.target / ".local/share/ai-dev-env/common.sh").exists())
        self.assertFalse((self.state / "install.lock").exists())

    def test_reinstall_keeps_overrides_and_one_path_block(self):
        self.write(self.target / ".tmux.local.conf", "set -g mouse off\n")
        self.write(self.target / ".config/ghostty/config.local", "font-size = 18\n")
        self.install()
        first_backup = (self.state / "last-backup").read_text()
        self.install()
        self.assertNotEqual((self.state / "last-backup").read_text(), first_backup)
        self.assertEqual((self.target / ".tmux.local.conf").read_text(), "set -g mouse off\n")
        self.assertEqual((self.target / ".config/ghostty/config.local").read_text(), "font-size = 18\n")
        self.assertEqual((self.target / ".zshrc").read_text().count("# >>> ai-dev-env path >>>"), 1)
        for helper in ("dev", "newtask", "task", "ai-dev-doctor"):
            self.assertTrue(os.access(self.target / ".local/bin" / helper, os.X_OK))
        self.assertTrue((self.target / ".local/share/ai-dev-env/common.sh").is_file())

    def test_upgrade_requires_explicit_replacement_of_modified_files(self):
        self.install()
        original_backup = (self.state / "last-backup").read_text()
        edited = "set -g mouse off\n"
        self.write(self.target / ".tmux.conf", edited)
        rejected = self.install(success=False)
        self.assertIn("--replace-modified", rejected.stderr)
        self.assertEqual((self.target / ".tmux.conf").read_text(), edited)
        self.assertEqual((self.state / "last-backup").read_text(), original_backup)
        self.run_script("install.sh", "--skip-deps", "--no-reload", "--replace-modified")
        backup = Path((self.state / "last-backup").read_text().strip())
        self.assertEqual((backup / "tmux.conf").read_text(), edited)
        self.run_script("uninstall.sh")
        self.assertEqual((self.target / ".tmux.conf").read_text(), edited)

    def test_uninstall_preserves_incomplete_shell_block_and_local_overrides(self):
        self.install()
        edited = '# >>> ai-dev-env path >>>\nexport PATH="$HOME/.local/bin:$PATH"\nexport KEEP_ME=yes\n'
        self.write(self.target / ".zshrc", edited)
        self.write(self.target / ".tmux.local.conf", "set -g mouse off\n")
        self.run_script("uninstall.sh")
        self.assertEqual((self.target / ".zshrc").read_text(), edited)
        self.assertEqual((self.target / ".tmux.local.conf").read_text(), "set -g mouse off\n")
        self.assertFalse((self.target / ".local/bin/task").exists())

    def test_uninstall_keeps_library_needed_by_an_edited_helper(self):
        self.install()
        self.write(self.target / ".local/bin/dev", "# personally edited helper\n", executable=True)
        self.run_script("uninstall.sh")
        self.assertEqual((self.target / ".local/bin/dev").read_text(), "# personally edited helper\n")
        self.assertTrue((self.target / ".local/share/ai-dev-env/common.sh").is_file())

    def test_doctor_warns_for_optional_tools_and_checks_requested_project(self):
        self.install()
        self.env["AI_DEV_CHECK_LOG"] = str(self.root / "project-check.log")
        project = self.root / "project with spaces"
        project.mkdir()
        result = self.run_script("doctor", "--project", str(project))
        self.assertIn("WARN", result.stdout)
        self.assertIn("0 failed", result.stdout)
        self.assertEqual((self.root / "project-check.log").read_text(), "--check\n" + str(project) + "\n")

    @unittest.skipUnless(REAL_TMUX, "tmux is not installed")
    def test_real_tmux_startup_false_positive_is_rejected_by_doctor(self):
        self.install()
        invalid_config = self.target / ".tmux.conf"
        invalid_config.write_text("set -g definitely-invalid-option on\n")
        socket = "ai-dev-regression-" + uuid.uuid4().hex
        try:
            startup = subprocess.run(
                [REAL_TMUX, "-L", socket, "-f", str(invalid_config), "new-session", "-d", "-s", "validate", "exec /bin/sleep 30"],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(startup.returncode, 0, startup.stderr)
        finally:
            subprocess.run([REAL_TMUX, "-L", socket, "kill-server"], capture_output=True, timeout=10)
        (self.bin / "tmux").unlink()
        (self.bin / "tmux").symlink_to(REAL_TMUX)
        result = self.run_script("doctor", success=False)
        self.assertIn("tmux configuration is missing or invalid", result.stdout)
        self.assertIn("invalid option", result.stderr)

    @unittest.skipUnless(REAL_TMUX and REAL_GHOSTTY, "real tmux and Ghostty are required")
    def test_checkout_installs_with_real_config_validation_and_shared_helpers(self):
        for relative in ("dev", "newtask", "task", "lib/common.sh", "config/ghostty.conf", "config/tmux.conf"):
            shutil.copy2(REPOSITORY / relative, self.source / relative)
        for name, executable in (("tmux", REAL_TMUX), ("ghostty", REAL_GHOSTTY)):
            (self.bin / name).unlink()
            (self.bin / name).symlink_to(executable)
        self.write(self.target / ".tmux.local.conf", "set -g mouse off\n")
        self.write(self.target / ".config/ghostty/config.local", "font-size = 19\n")
        self.install()
        for helper in ("dev", "newtask", "task"):
            result = subprocess.run(
                [str(self.target / ".local/bin" / helper), "--help"],
                env=self.env, text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
