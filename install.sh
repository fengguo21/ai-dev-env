#!/usr/bin/env bash
set -Eeuo pipefail

AI_DEV_VERSION="1.1.0"
SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GHOSTTY_CONFIG_DIR="$HOME/.config/ghostty"
GHOSTTY_CONFIG_FILE="$GHOSTTY_CONFIG_DIR/config"
TMUX_CONFIG_FILE="$HOME/.tmux.conf"
LOCAL_BIN_DIR="$HOME/.local/bin"
ZSH_CONFIG_FILE="$HOME/.zshrc"

STATE_DIR="$HOME/.local/state/ai-dev-env"
RUN_STAMP="$(date '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$STATE_DIR/backups/$RUN_STAMP"

log() {
  printf '[ai-dev-env] %s\n' "$*"
}

fail() {
  printf '[ai-dev-env] ERROR: %s\n' "$*" >&2
  exit 1
}

file_hash() {
  shasum -a 256 "$1" | awk '{print $1}'
}

backup_file() {
  local target_file="$1"
  local backup_name="$2"

  if [ -f "$target_file" ]; then
    cp -p "$target_file" "$BACKUP_DIR/$backup_name"
  else
    : > "$BACKUP_DIR/$backup_name.absent"
  fi
}

find_ghostty() {
  if command -v ghostty >/dev/null 2>&1; then
    command -v ghostty
  elif [ -x "/Applications/Ghostty.app/Contents/MacOS/ghostty" ]; then
    printf '%s\n' "/Applications/Ghostty.app/Contents/MacOS/ghostty"
  elif [ -x "$HOME/Applications/Ghostty.app/Contents/MacOS/ghostty" ]; then
    printf '%s\n' "$HOME/Applications/Ghostty.app/Contents/MacOS/ghostty"
  else
    return 1
  fi
}

resolve_brew() {
  if command -v brew >/dev/null 2>&1; then
    command -v brew
  elif [ -x "/opt/homebrew/bin/brew" ]; then
    printf '%s\n' "/opt/homebrew/bin/brew"
  elif [ -x "/usr/local/bin/brew" ]; then
    printf '%s\n' "/usr/local/bin/brew"
  else
    return 1
  fi
}

if [ "$(uname -s)" != "Darwin" ]; then
  fail "v1.1 is designed for macOS."
fi

log "Installing AI Dev Environment v$AI_DEV_VERSION"

BREW_EXECUTABLE="$(resolve_brew || true)"
if [ -z "$BREW_EXECUTABLE" ]; then
  log "Homebrew not found; starting the official installer."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  BREW_EXECUTABLE="$(resolve_brew || true)"
fi
[ -n "$BREW_EXECUTABLE" ] || fail "Homebrew installation finished but brew is not available."

# Make a newly installed Homebrew usable during this same script run.
eval "$("$BREW_EXECUTABLE" shellenv)"

GHOSTTY_EXECUTABLE="$(find_ghostty || true)"
if [ -z "$GHOSTTY_EXECUTABLE" ]; then
  log "Installing Ghostty."
  "$BREW_EXECUTABLE" install --cask ghostty
fi

if ! command -v tmux >/dev/null 2>&1; then
  log "Installing tmux."
  "$BREW_EXECUTABLE" install tmux
fi

if ! command -v git >/dev/null 2>&1; then
  log "Installing Git."
  "$BREW_EXECUTABLE" install git
fi

if ! "$BREW_EXECUTABLE" list --cask font-jetbrains-mono-nerd-font >/dev/null 2>&1; then
  log "Installing JetBrains Mono Nerd Font."
  "$BREW_EXECUTABLE" install --cask font-jetbrains-mono-nerd-font
fi

GHOSTTY_EXECUTABLE="$(find_ghostty || true)"
[ -n "$GHOSTTY_EXECUTABLE" ] || fail "Ghostty was installed but its executable could not be found."

mkdir -p "$GHOSTTY_CONFIG_DIR" "$LOCAL_BIN_DIR" "$BACKUP_DIR"

# Preserve the state immediately before every install/upgrade.
backup_file "$GHOSTTY_CONFIG_FILE" "ghostty-config"
backup_file "$TMUX_CONFIG_FILE" "tmux.conf"
backup_file "$LOCAL_BIN_DIR/dev" "dev"
backup_file "$LOCAL_BIN_DIR/newtask" "newtask"
backup_file "$LOCAL_BIN_DIR/ai-dev-doctor" "ai-dev-doctor"
backup_file "$ZSH_CONFIG_FILE" "zshrc"
printf '%s\n' "$BACKUP_DIR" > "$STATE_DIR/last-backup"

install -m 0644 "$SCRIPT_ROOT/config/ghostty.conf" "$GHOSTTY_CONFIG_FILE"
install -m 0644 "$SCRIPT_ROOT/config/tmux.conf" "$TMUX_CONFIG_FILE"
install -m 0755 "$SCRIPT_ROOT/dev" "$LOCAL_BIN_DIR/dev"
install -m 0755 "$SCRIPT_ROOT/newtask" "$LOCAL_BIN_DIR/newtask"
install -m 0755 "$SCRIPT_ROOT/doctor" "$LOCAL_BIN_DIR/ai-dev-doctor"

# Ensure the helper commands remain available in future zsh sessions.
PATH_BLOCK_START="# >>> ai-dev-env path >>>"
PATH_BLOCK_END="# <<< ai-dev-env path <<<"
if ! grep -Fq "$PATH_BLOCK_START" "$ZSH_CONFIG_FILE" 2>/dev/null; then
  {
    printf '\n%s\n' "$PATH_BLOCK_START"
    printf 'export PATH="$HOME/.local/bin:$PATH"\n'
    printf '%s\n' "$PATH_BLOCK_END"
  } >> "$ZSH_CONFIG_FILE"
  : > "$STATE_DIR/zsh-path-block-added"
fi
export PATH="$LOCAL_BIN_DIR:$PATH"

# Record installed fingerprints so uninstall.sh never overwrites later edits.
file_hash "$GHOSTTY_CONFIG_FILE" > "$STATE_DIR/installed-ghostty.sha256"
file_hash "$TMUX_CONFIG_FILE" > "$STATE_DIR/installed-tmux.sha256"
file_hash "$LOCAL_BIN_DIR/dev" > "$STATE_DIR/installed-dev.sha256"
file_hash "$LOCAL_BIN_DIR/newtask" > "$STATE_DIR/installed-newtask.sha256"
file_hash "$LOCAL_BIN_DIR/ai-dev-doctor" > "$STATE_DIR/installed-doctor.sha256"

TPM_DIR="$HOME/.tmux/plugins/tpm"
if [ ! -d "$TPM_DIR/.git" ]; then
  log "Installing TPM."
  git clone https://github.com/tmux-plugins/tpm "$TPM_DIR"
fi

log "Installing declared tmux plugins."
"$TPM_DIR/bin/install_plugins"

log "Validating Ghostty configuration."
"$GHOSTTY_EXECUTABLE" +validate-config --config-file="$GHOSTTY_CONFIG_FILE"

if ! "$GHOSTTY_EXECUTABLE" +list-fonts | grep -Fxq "JetBrainsMono Nerd Font Mono"; then
  fail "Ghostty cannot see 'JetBrainsMono Nerd Font Mono'. Restart macOS and rerun the installer."
fi

# Validate core tmux syntax on an isolated socket without loading TPM restore.
TMUX_VERIFY_CONFIG="$(mktemp "${TMPDIR:-/tmp}/ai-dev-env-tmux.XXXXXX")"
TMUX_VERIFY_SOCKET="ai-dev-env-verify-$$"
cleanup_verify() {
  tmux -L "$TMUX_VERIFY_SOCKET" kill-server >/dev/null 2>&1 || true
  rm -f "$TMUX_VERIFY_CONFIG"
}
trap cleanup_verify EXIT
sed '/^[[:space:]]*run-shell.*tpm\/tpm/d' "$TMUX_CONFIG_FILE" > "$TMUX_VERIFY_CONFIG"
tmux -L "$TMUX_VERIFY_SOCKET" -f "$TMUX_VERIFY_CONFIG" new-session -d -s verify
cleanup_verify
trap - EXIT

# Existing sessions receive the new style immediately; otherwise the next
# `dev` or `tmux` start loads it normally.
if tmux list-sessions >/dev/null 2>&1; then
  tmux source-file "$TMUX_CONFIG_FILE"
fi

log "Installation complete."
log "Backup: $BACKUP_DIR"
log "Open a new Ghostty window (or run: source ~/.zshrc), then run: ai-dev-doctor"
log "Start a project workspace with: dev /path/to/project"
