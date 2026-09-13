#!/usr/bin/env bash
set -Eeuo pipefail

AI_DEV_HOME="${AI_DEV_HOME:-$HOME}"
log() { printf '[ai-dev-env] %s\n' "$*"; }
case "${1:-}" in
  -h|--help) printf '%s\n' 'Usage: uninstall.sh' 'AI_DEV_HOME overrides the configuration destination.'; exit 0 ;;
  '') ;;
  *) log "Unknown option: $1"; exit 1 ;;
esac
case "$AI_DEV_HOME" in /*) ;; *) log 'AI_DEV_HOME must be an absolute path.'; exit 1 ;; esac
AI_DEV_HOME="${AI_DEV_HOME%/}"
[ -n "$AI_DEV_HOME" ] || { log 'Refusing the filesystem root as destination.'; exit 1; }
STATE_DIR="$AI_DEV_HOME/.local/state/ai-dev-env"
LOCAL_BIN_DIR="$AI_DEV_HOME/.local/bin"
ZSH_CONFIG_FILE="$AI_DEV_HOME/.zshrc"
PRESERVED_HELPER=0
ZSH_TEMP_FILE=""
file_hash() { shasum -a 256 "$1" | awk '{print $1}'; }

if [ ! -f "$STATE_DIR/last-backup" ]; then
  log 'No installation manifest found; nothing was removed.'
  exit 0
fi
BACKUP_DIR="$(sed -n '1p' "$STATE_DIR/last-backup")"
[ -d "$BACKUP_DIR" ] || { log "Backup directory is missing: $BACKUP_DIR"; exit 1; }
BACKUP_ROOT="$(cd "$STATE_DIR/backups" && pwd -P)"
BACKUP_DIR="$(cd "$BACKUP_DIR" && pwd -P)"
case "$BACKUP_DIR" in
  "$BACKUP_ROOT"/*) ;;
  *) log "Refusing an unexpected backup path: $BACKUP_DIR"; exit 1 ;;
esac
mkdir "$STATE_DIR/install.lock" 2>/dev/null || { log "Another install/uninstall is running (lock: $STATE_DIR/install.lock)."; exit 1; }
cleanup() {
  local status=$?
  trap - EXIT INT TERM
  if [ -n "$ZSH_TEMP_FILE" ]; then rm -f "$ZSH_TEMP_FILE"; fi
  rmdir "$STATE_DIR/install.lock" 2>/dev/null || true
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

restore_managed_file() {
  local target="$1" backup_name="$2" manifest="$STATE_DIR/installed-$3.sha256"
  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ ! -f "$target" ] || [ ! -f "$manifest" ] || \
       [ "$(file_hash "$target")" != "$(sed -n '1p' "$manifest")" ]; then
      log "Preserved $target (modified or no installed fingerprint)."
      case "$3" in dev|newtask|task) PRESERVED_HELPER=1 ;; esac
      return 0
    fi
  fi
  if [ -e "$BACKUP_DIR/$backup_name" ] || [ -L "$BACKUP_DIR/$backup_name" ]; then
    mkdir -p "$(dirname "$target")"
    rm -f "$target"
    cp -Pp "$BACKUP_DIR/$backup_name" "$target"
    log "Restored $target"
  elif [ -f "$BACKUP_DIR/$backup_name.absent" ]; then
    rm -f "$target"
    log "Removed managed file $target"
  else
    log "Preserved $target (backup record missing)."
    case "$3" in dev|newtask|task) PRESERVED_HELPER=1 ;; esac
  fi
}
restore_managed_file "$AI_DEV_HOME/.config/ghostty/config" ghostty-config ghostty
restore_managed_file "$AI_DEV_HOME/.tmux.conf" tmux.conf tmux
restore_managed_file "$LOCAL_BIN_DIR/dev" dev dev
restore_managed_file "$LOCAL_BIN_DIR/newtask" newtask newtask
restore_managed_file "$LOCAL_BIN_DIR/task" task task
restore_managed_file "$LOCAL_BIN_DIR/ai-dev-doctor" ai-dev-doctor doctor
if [ "$PRESERVED_HELPER" -eq 0 ]; then
  restore_managed_file "$AI_DEV_HOME/.local/share/ai-dev-env/common.sh" common.sh common
else
  log 'Preserved common.sh because a retained helper may require it.'
fi

# Match all three original lines. Edited/incomplete markers must never delete
# unrelated shell configuration, including everything after a missing end marker.
if [ -f "$STATE_DIR/zsh-path-block-added" ] && [ -f "$ZSH_CONFIG_FILE" ]; then
  ZSH_TEMP_FILE="$(mktemp "$STATE_DIR/.zshrc.XXXXXX")"
  cp -Lp "$ZSH_CONFIG_FILE" "$ZSH_TEMP_FILE"
  if awk '
    { lines[NR] = $0 }
    END {
      for (i = 1; i <= NR; i++) {
        if (lines[i] == "# >>> ai-dev-env path >>>" &&
            lines[i + 1] == "export PATH=\"$HOME/.local/bin:$PATH\"" &&
            lines[i + 2] == "# <<< ai-dev-env path <<<") {
          i += 2; removed = 1
        } else print lines[i]
      }
      if (!removed) exit 3
    }
  ' "$ZSH_CONFIG_FILE" > "$ZSH_TEMP_FILE"; then
    mv -f "$ZSH_TEMP_FILE" "$ZSH_CONFIG_FILE"
    if [ -f "$BACKUP_DIR/zshrc.absent" ] && ! grep '[^[:space:]]' "$ZSH_CONFIG_FILE" >/dev/null; then
      rm -f "$ZSH_CONFIG_FILE"
    fi
  else
    log 'Preserved the edited/incomplete PATH block in .zshrc.'
  fi
fi

for name in ghostty tmux dev newtask task doctor common; do
  rm -f "$STATE_DIR/installed-$name.sha256"
done
rm -f "$STATE_DIR/zsh-path-block-added" "$STATE_DIR/last-backup"
log 'Configuration uninstall complete; the latest pre-install files were restored where unchanged.'
log 'Personal override files, installed software, TPM/plugins, and backups were kept.'
