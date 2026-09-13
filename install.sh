#!/usr/bin/env bash
set -Eeuo pipefail

AI_DEV_VERSION="1.2.0"
SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DEV_HOME="${AI_DEV_HOME:-$HOME}"
SKIP_DEPS=0
RELOAD_TMUX=1
REPLACE_MODIFIED=0

log() { printf '[ai-dev-env] %s\n' "$*"; }
fail() { printf '[ai-dev-env] ERROR: %s\n' "$*" >&2; exit 1; }
usage() {
  printf '%s\n' 'Usage: install.sh [--skip-deps] [--no-reload] [--replace-modified]' \
    '  --skip-deps  Install configuration/helpers using existing dependencies; skip plugins.' \
    '  --no-reload  Leave running tmux sessions untouched.' \
    '  --replace-modified  Back up and replace files edited since their last installation.' \
    '  AI_DEV_HOME  Override the destination for isolated tests (requires --skip-deps).'
}
for argument in "$@"; do
  case "$argument" in
    --skip-deps) SKIP_DEPS=1 ;;
    --no-reload) RELOAD_TMUX=0 ;;
    --replace-modified) REPLACE_MODIFIED=1 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown option: $argument" ;;
  esac
done
case "$AI_DEV_HOME" in /*) ;; *) fail 'AI_DEV_HOME must be an absolute path.' ;; esac
AI_DEV_HOME="${AI_DEV_HOME%/}"
[ -n "$AI_DEV_HOME" ] || fail 'The filesystem root cannot be an installation destination.'
if [ "$AI_DEV_HOME" != "$HOME" ]; then
  [ "$SKIP_DEPS" -eq 1 ] || fail 'A custom AI_DEV_HOME requires --skip-deps.'
  RELOAD_TMUX=0
fi
if [ "$SKIP_DEPS" -eq 0 ] && [ "$(uname -s)" != Darwin ]; then
  fail 'Dependency installation is designed for macOS.'
fi

GHOSTTY_CONFIG_DIR="$AI_DEV_HOME/.config/ghostty"
LOCAL_BIN_DIR="$AI_DEV_HOME/.local/bin"
SHARE_DIR="$AI_DEV_HOME/.local/share/ai-dev-env"
STATE_DIR="$AI_DEV_HOME/.local/state/ai-dev-env"
ZSH_CONFIG_FILE="$AI_DEV_HOME/.zshrc"
NAMES=(ghostty tmux dev newtask task doctor common)
BACKUP_NAMES=(ghostty-config tmux.conf dev newtask task ai-dev-doctor common.sh)
TARGETS=("$GHOSTTY_CONFIG_DIR/config" "$AI_DEV_HOME/.tmux.conf" \
  "$LOCAL_BIN_DIR/dev" "$LOCAL_BIN_DIR/newtask" "$LOCAL_BIN_DIR/task" \
  "$LOCAL_BIN_DIR/ai-dev-doctor" "$SHARE_DIR/common.sh")
SOURCES=(config/ghostty.conf config/tmux.conf dev newtask task doctor lib/common.sh)
STATE_FILES=(last-backup zsh-path-block-added)
for name in "${NAMES[@]}"; do STATE_FILES+=("installed-$name.sha256"); done
STAGE_DIR=""
BACKUP_DIR=""
VERIFY_SOCKET="ai-dev-env-install-$$"
VERIFY_STARTED=0
TRANSACTION_ACTIVE=0
LOCK_HELD=0

file_hash() { shasum -a 256 "$1" | awk '{print $1}'; }
backup_file() {
  local target="$1" record="$2"
  if [ -e "$target" ] || [ -L "$target" ]; then
    [ -f "$target" ] || [ -L "$target" ] || fail "Not a regular file: $target"
    cp -Pp "$target" "$BACKUP_DIR/$record"
  else
    : > "$BACKUP_DIR/$record.absent"
  fi
}
restore_file() {
  local target="$1" record="$2"
  if [ -e "$BACKUP_DIR/$record" ] || [ -L "$BACKUP_DIR/$record" ]; then
    rm -f "$target"
    cp -Pp "$BACKUP_DIR/$record" "$target"
  elif [ -f "$BACKUP_DIR/$record.absent" ]; then
    rm -f "$target"
  fi
}
cleanup() {
  local status=$? index name
  trap - EXIT INT TERM
  if [ "$TRANSACTION_ACTIVE" -eq 1 ]; then
    log 'Installation failed; restoring the previous managed files and state.'
    for ((index=0; index<${#NAMES[@]}; index++)); do
      restore_file "${TARGETS[$index]}" "${BACKUP_NAMES[$index]}" || \
        log "WARNING: restore failed for ${TARGETS[$index]}; backup: $BACKUP_DIR"
    done
    restore_file "$ZSH_CONFIG_FILE" zshrc || log "WARNING: restore zshrc from $BACKUP_DIR"
    for name in "${STATE_FILES[@]}"; do
      restore_file "$STATE_DIR/$name" "state-$name" || log "WARNING: restore failed for $name"
    done
  fi
  if [ "$VERIFY_STARTED" -eq 1 ]; then
    tmux -L "$VERIFY_SOCKET" kill-server >/dev/null 2>&1 || true
  fi
  if [ -n "$STAGE_DIR" ]; then
    for name in "${NAMES[@]}" zshrc config.local tmux-core fonts; do rm -f "$STAGE_DIR/$name"; done
    for name in "${STATE_FILES[@]}"; do rm -f "$STAGE_DIR/state-$name"; done
    rmdir "$STAGE_DIR" 2>/dev/null || true
  fi
  if [ "$LOCK_HELD" -eq 1 ]; then rmdir "$STATE_DIR/install.lock" 2>/dev/null || true; fi
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

find_ghostty() {
  if command -v ghostty >/dev/null 2>&1; then command -v ghostty
  elif [ -x /Applications/Ghostty.app/Contents/MacOS/ghostty ]; then
    printf '%s\n' /Applications/Ghostty.app/Contents/MacOS/ghostty
  elif [ -x "$AI_DEV_HOME/Applications/Ghostty.app/Contents/MacOS/ghostty" ]; then
    printf '%s\n' "$AI_DEV_HOME/Applications/Ghostty.app/Contents/MacOS/ghostty"
  else return 1; fi
}
resolve_brew() {
  if command -v brew >/dev/null 2>&1; then command -v brew
  elif [ -x /opt/homebrew/bin/brew ]; then printf '%s\n' /opt/homebrew/bin/brew
  elif [ -x /usr/local/bin/brew ]; then printf '%s\n' /usr/local/bin/brew
  else return 1; fi
}

for source in "${SOURCES[@]}"; do [ -f "$SCRIPT_ROOT/$source" ] || fail "Missing source: $source"; done
log "Installing AI Dev Environment v$AI_DEV_VERSION"
if [ "$SKIP_DEPS" -eq 0 ]; then
  BREW_EXECUTABLE="$(resolve_brew || true)"
  if [ -z "$BREW_EXECUTABLE" ]; then
    log 'Homebrew not found; starting the official installer.'
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    BREW_EXECUTABLE="$(resolve_brew || true)"
  fi
  [ -n "$BREW_EXECUTABLE" ] || fail 'Homebrew is unavailable.'
  eval "$("$BREW_EXECUTABLE" shellenv)"
  if ! find_ghostty >/dev/null; then "$BREW_EXECUTABLE" install --cask ghostty; fi
  for formula in tmux git lazygit git-delta gh fzf; do
    executable="$formula"
    [ "$formula" != git-delta ] || executable=delta
    if ! command -v "$executable" >/dev/null 2>&1; then
      if ! "$BREW_EXECUTABLE" install "$formula"; then
        case "$formula" in
          tmux|git) fail "Could not install required dependency: $formula" ;;
          *) log "WARNING: optional $formula was not installed; rerun brew install $formula later." ;;
        esac
      fi
    fi
  done
fi
command -v tmux >/dev/null 2>&1 || fail 'tmux is required; install it before using --skip-deps.'
GHOSTTY_EXECUTABLE="$(find_ghostty || true)"
[ -n "$GHOSTTY_EXECUTABLE" ] || fail 'Ghostty is required for configuration validation.'

mkdir -p "$STATE_DIR/backups"
mkdir "$STATE_DIR/install.lock" 2>/dev/null || fail "Another install/uninstall is running (lock: $STATE_DIR/install.lock)."
LOCK_HELD=1
for ((index=0; index<${#NAMES[@]}; index++)); do
  manifest="$STATE_DIR/installed-${NAMES[$index]}.sha256"
  target="${TARGETS[$index]}"
  if [ -f "$manifest" ] && { [ -e "$target" ] || [ -L "$target" ]; }; then
    if [ ! -f "$target" ] || [ "$(file_hash "$target")" != "$(sed -n '1p' "$manifest")" ]; then
      if [ "$REPLACE_MODIFIED" -eq 0 ]; then
        fail "Edited since installation: $target. Move personal settings into ~/.tmux.local.conf or ~/.config/ghostty/config.local, or review the changes and rerun with --replace-modified to back up and replace them."
      fi
      log "Will back up and replace modified file: $target"
    fi
  fi
done
STAGE_DIR="$(mktemp -d "$STATE_DIR/.stage.XXXXXX")"
for ((index=0; index<${#NAMES[@]}; index++)); do
  mode=0755
  case "${NAMES[$index]}" in ghostty|tmux|common) mode=0644 ;; esac
  install -m "$mode" "$SCRIPT_ROOT/${SOURCES[$index]}" "$STAGE_DIR/${NAMES[$index]}"
done
for name in dev newtask task doctor common; do bash -n "$STAGE_DIR/$name"; done
if [ -f "$GHOSTTY_CONFIG_DIR/config.local" ]; then
  cp -p "$GHOSTTY_CONFIG_DIR/config.local" "$STAGE_DIR/config.local"
fi
"$GHOSTTY_EXECUTABLE" +list-fonts > "$STAGE_DIR/fonts"
if ! grep -Fx 'JetBrainsMono Nerd Font Mono' "$STAGE_DIR/fonts" >/dev/null; then
  if [ "$SKIP_DEPS" -eq 0 ]; then
    "$BREW_EXECUTABLE" install --cask font-jetbrains-mono-nerd-font
    "$GHOSTTY_EXECUTABLE" +list-fonts > "$STAGE_DIR/fonts"
    grep -Fx 'JetBrainsMono Nerd Font Mono' "$STAGE_DIR/fonts" >/dev/null || fail 'Ghostty cannot see the installed Nerd Font; restart Ghostty and retry.'
  else log 'WARNING: JetBrainsMono Nerd Font Mono is unavailable; Ghostty will use a fallback font.'; fi
fi
log 'Validating the candidate Ghostty and tmux configuration before changing managed files.'
"$GHOSTTY_EXECUTABLE" +validate-config --config-file="$STAGE_DIR/ghostty"
# Load personal overrides explicitly from the destination, never a different HOME.
# TPM restore must not run on a verification server.
sed -e '/^[[:space:]]*run-shell.*tpm\/tpm/d' \
  -e '/^[[:space:]]*source\(-file\)\{0,1\}.*\.tmux\.local\.conf/d' \
  "$STAGE_DIR/tmux" > "$STAGE_DIR/tmux-core"
VERIFY_STARTED=1
tmux -L "$VERIFY_SOCKET" -f /dev/null new-session -d -s verify -c "$STAGE_DIR" 'exec /bin/sleep 300'
tmux -L "$VERIFY_SOCKET" source-file "$STAGE_DIR/tmux-core"
if [ -f "$AI_DEV_HOME/.tmux.local.conf" ]; then
  tmux -L "$VERIFY_SOCKET" source-file "$AI_DEV_HOME/.tmux.local.conf"
fi

if [ -e "$ZSH_CONFIG_FILE" ]; then cp -Lp "$ZSH_CONFIG_FILE" "$STAGE_DIR/zshrc"
else : > "$STAGE_DIR/zshrc"; chmod 0644 "$STAGE_DIR/zshrc"; fi
PATH_BLOCK_START='# >>> ai-dev-env path >>>'
PATH_BLOCK_END='# <<< ai-dev-env path <<<'
start_count="$(grep -Fxc "$PATH_BLOCK_START" "$STAGE_DIR/zshrc" || true)"
end_count="$(grep -Fxc "$PATH_BLOCK_END" "$STAGE_DIR/zshrc" || true)"
ADD_PATH_BLOCK=0
if [ "$start_count" -eq 0 ] && [ "$end_count" -eq 0 ]; then
  printf '\n%s\n%s\n%s\n' "$PATH_BLOCK_START" 'export PATH="$HOME/.local/bin:$PATH"' "$PATH_BLOCK_END" >> "$STAGE_DIR/zshrc"
  ADD_PATH_BLOCK=1
elif [ "$start_count" -ne 1 ] || [ "$end_count" -ne 1 ]; then
  fail 'The ai-dev-env PATH markers in .zshrc are incomplete or duplicated; repair them before reinstalling.'
fi

BACKUP_DIR="$(mktemp -d "$STATE_DIR/backups/$(date '+%Y%m%d-%H%M%S').XXXXXX")"
for ((index=0; index<${#NAMES[@]}; index++)); do
  backup_file "${TARGETS[$index]}" "${BACKUP_NAMES[$index]}"
done
backup_file "$ZSH_CONFIG_FILE" zshrc
for name in "${STATE_FILES[@]}"; do backup_file "$STATE_DIR/$name" "state-$name"; done
mkdir -p "$GHOSTTY_CONFIG_DIR" "$LOCAL_BIN_DIR" "$SHARE_DIR"
TRANSACTION_ACTIVE=1
for ((index=0; index<${#NAMES[@]}; index++)); do
  # Replace a symlink itself, never the user's file behind that link.
  mv -f "$STAGE_DIR/${NAMES[$index]}" "${TARGETS[$index]}"
done
if [ "$ADD_PATH_BLOCK" -eq 1 ]; then
  mv -f "$STAGE_DIR/zshrc" "$ZSH_CONFIG_FILE"
  : > "$STATE_DIR/zsh-path-block-added"
fi

if [ "$SKIP_DEPS" -eq 0 ]; then
  TPM_DIR="$AI_DEV_HOME/.tmux/plugins/tpm"
  if [ ! -d "$TPM_DIR/.git" ]; then
    log 'Installing TPM.'
    git clone https://github.com/tmux-plugins/tpm "$TPM_DIR"
  fi
  # TPM reads its path from a running server. The isolated server avoids
  # reloading or depending on an existing personal server during installation.
  tmux -L "$VERIFY_SOCKET" set-environment -g TMUX_PLUGIN_MANAGER_PATH "$AI_DEV_HOME/.tmux/plugins/"
  VERIFY_CONNECTION="$(tmux -L "$VERIFY_SOCKET" display-message -p -t '=verify:' '#{socket_path},#{pid},0')"
  case "$VERIFY_CONNECTION" in
    /*,[1-9]*,0) ;;
    *) fail 'Could not resolve the isolated tmux server for TPM installation.' ;;
  esac
  log 'Installing declared tmux plugins on an isolated server.'
  TMUX="$VERIFY_CONNECTION" "$TPM_DIR/bin/install_plugins"
fi

for ((index=0; index<${#NAMES[@]}; index++)); do
  name="installed-${NAMES[$index]}.sha256"
  file_hash "${TARGETS[$index]}" > "$STAGE_DIR/state-$name"
  mv -f "$STAGE_DIR/state-$name" "$STATE_DIR/$name"
done
printf '%s\n' "$BACKUP_DIR" > "$STAGE_DIR/state-last-backup"
mv -f "$STAGE_DIR/state-last-backup" "$STATE_DIR/last-backup"
TRANSACTION_ACTIVE=0

if [ "$RELOAD_TMUX" -eq 1 ] && tmux list-sessions >/dev/null 2>&1; then
  tmux source-file "$AI_DEV_HOME/.tmux.conf" || log 'WARNING: running tmux could not reload; the validated config will load on its next start.'
fi
log "Installation complete. Backup: $BACKUP_DIR"
log 'Personal overrides stay in ~/.tmux.local.conf and ~/.config/ghostty/config.local.'
log 'Open a new Ghostty window, run ai-dev-doctor, then dev /path/to/project.'
