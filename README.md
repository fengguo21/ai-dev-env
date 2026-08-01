# AI Dev Environment for macOS v1.1

A professional Ghostty + tmux + Git worktree environment for Codex, Claude
Code, FastAPI, Vue, Docker, tests, logs, and Git review.

The folder name remains `ai-dev-env-v1.0` for compatibility, but the contents
and installed configuration are v1.1.

## Visual profile

- Ghostty built-in `TokyoNight Night` theme
- `JetBrainsMono Nerd Font Mono` at 15 pt
- Opaque background for stable contrast during long sessions
- A restrained Tokyo Night tmux status bar and clear active-pane border
- Plain, compact window labels instead of a decorative Powerline layout
- Matching colors across Ghostty, tmux, copy mode, messages, and pane borders
- Native tmux RGB support for `xterm-ghostty`, plus compatibility fallbacks
- Dark native macOS title bar, protected paste, and SSH terminfo propagation
- 50 MB Ghostty scrollback for long Codex, test, and log output

## Safety and workflow defaults

- Ghostty confirms closing surfaces that still contain a running process
- Existing Ghostty/tmux configs and helper commands are backed up before install
- Uninstall restores the latest backup only when managed files were not edited
- tmux window names stay stable: `codex`, `backend`, `frontend`, `services`, etc.
- New tmux windows and panes inherit the active Git worktree directory
- TPM installs `tmux-resurrect`, `tmux-continuum`, and `tmux-yank`
- `dev` creates one reusable tmux session per project instead of one global session
- `newtask` defaults to `HEAD`, so it works with either `main` or `master`

`tmux-resurrect` restores sessions, layouts, pane directories, and supported
programs. It cannot reconstruct every interactive AI process after a reboot;
resume Codex/Claude sessions using the relevant CLI's own history feature.

## Install or upgrade

Run from any directory:

```bash
/Users/renyakun/work26/ai-dev-env-v1.0/install.sh
```

The installer validates both configs, installs missing dependencies/plugins,
and records its backup under:

```text
~/.local/state/ai-dev-env/backups/
```

Open a new Ghostty window after installation, or reload the shell once:

```bash
source ~/.zshrc
ai-dev-doctor
```

## Start a project workspace

Use the current directory or provide an explicit project/worktree path:

```bash
dev
dev /path/to/project
dev /path/to/project --no-codex
```

The default layout contains `codex`, `backend`, `frontend`, `services`, `test`,
and `git`. Backend/frontend subdirectories are detected automatically. If
Codex is installed, it starts in the `codex` window unless `--no-codex` is set.

Create a parallel Git worktree from the current commit or another base ref:

```bash
newtask auth
newtask pipeline origin/main
```

The worktree is created next to the primary repository under
`<repository>_worktrees/<task>`. To use a different parent, set
`AI_WORKTREE_ROOT`.

## tmux quick reference

The prefix is `Ctrl+a`: press it, release it, then press the next key.

| Action | Shortcut |
|---|---|
| New window | `Ctrl+a c` |
| Previous / next window | `Ctrl+a p` / `Ctrl+a n` |
| Horizontal / vertical split | `Ctrl+a \|` / `Ctrl+a -` |
| Move between panes | `Ctrl+a h/j/k/l` |
| Resize panes | `Ctrl+a H/J/K/L` |
| Maximize current pane | `Ctrl+a z` |
| Copy mode | `Ctrl+a [` |
| Reload config | `Ctrl+a r` |
| Detach session | `Ctrl+a d` |
| Save / restore layout | `Ctrl+a Ctrl+s` / `Ctrl+a Ctrl+r` |
| Install TPM plugins | `Ctrl+a I` |

## Verify

Run the bundled doctor after installing:

```bash
ai-dev-doctor
```

It checks Ghostty, tmux, Git, the selected font/theme, config syntax, plugins,
and helper command availability. Equivalent focused checks are:

```bash
ghostty +validate-config --config-file="$HOME/.config/ghostty/config"
ghostty +list-fonts | grep -F "JetBrainsMono Nerd Font Mono"
tmux -V
tmux show-options -gqv default-terminal
tmux show-options -sqv terminal-features
```

Inside tmux, the word below should render in Tokyo Night blue rather than the
nearest basic ANSI color:

```bash
printf '\033[38;2;122;162;247mtruecolor sample\033[0m\n'
```

## Uninstall configuration

```bash
/Users/renyakun/work26/ai-dev-env-v1.0/uninstall.sh
```

The uninstaller does not remove Homebrew packages, fonts, TPM plugins, or
backups. It also preserves any managed file changed after installation.

## Project files

```text
config/ghostty.conf  Ghostty theme, font, readability, and macOS behavior
config/tmux.conf     tmux navigation, Tokyo Night styling, RGB, and plugins
install.sh           dependency install, backups, validation, and activation
uninstall.sh         fingerprint-aware restore of the previous configuration
dev                  project-scoped tmux workspace launcher
newtask              safe Git worktree creator
doctor               installed-environment health check
```
