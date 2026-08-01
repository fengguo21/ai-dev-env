#!/usr/bin/env bash
set -Eeuo pipefail

GHOSTTY_CONFIG_FILE="$HOME/.config/ghostty/config"
TMUX_CONFIG_FILE="$HOME/.tmux.conf"
LOCAL_BIN_DIR="$HOME/.local/bin"
ZSH_CONFIG_FILE="$HOME/.zshrc"
STATE_DIR="$HOME/.local/state/ai-dev-env"

log() {
  printf '[ai-dev-env] %s\n' "$*"
}

file_hash() {
  shasum -a 256 "$1" | awk '{print $1}'
}

if [ ! -f "$STATE_DIR/last-backup" ]; then
  log "No installation manifest found; nothing was removed."
  exit 0
fi

BACKUP_DIR="$(sed -n '1p' "$STATE_DIR/last-backup")"
case "$BACKUP_DIR" in
  "$STATE_DIR"/backups/*) ;;
  *)
    log "Refusing to use an unexpected backup path: $BACKUP_DIR"
    exit 1
    ;;
esac
[ -d "$BACKUP_DIR" ] || { log "Backup directory is missing: $BACKUP_DIR"; exit 1; }

restore_managed_file() {
  local target_file="$1"
  local backup_name="$2"
  local hash_manifest="$3"

  if [ -f "$target_file" ]; then
    if [ ! -f "$hash_manifest" ]; then
      log "Preserved $target_file (no installed fingerprint)."
      return
    fi

    if [ "$(file_hash "$target_file")" != "$(sed -n '1p' "$hash_manifest")" ]; then
      log "Preserved $target_file (modified after installation)."
      return
    fi
  fi

  if [ -f "$BACKUP_DIR/$backup_name" ]; then
    mkdir -p "$(dirname "$target_file")"
    cp -p "$BACKUP_DIR/$backup_name" "$target_file"
    log "Restored $target_file"
  elif [ -f "$BACKUP_DIR/$backup_name.absent" ]; then
    rm -f "$target_file"
    log "Removed managed file $target_file"
  else
    log "Preserved $target_file (backup record missing)."
  fi
}

restore_managed_file "$GHOSTTY_CONFIG_FILE" "ghostty-config" "$STATE_DIR/installed-ghostty.sha256"
restore_managed_file "$TMUX_CONFIG_FILE" "tmux.conf" "$STATE_DIR/installed-tmux.sha256"
restore_managed_file "$LOCAL_BIN_DIR/dev" "dev" "$STATE_DIR/installed-dev.sha256"
restore_managed_file "$LOCAL_BIN_DIR/newtask" "newtask" "$STATE_DIR/installed-newtask.sha256"
restore_managed_file "$LOCAL_BIN_DIR/ai-dev-doctor" "ai-dev-doctor" "$STATE_DIR/installed-doctor.sha256"

# Remove only the exact PATH block created by install.sh.
if [ -f "$STATE_DIR/zsh-path-block-added" ] && [ -f "$ZSH_CONFIG_FILE" ]; then
  ZSH_TEMP_FILE="$(mktemp "${TMPDIR:-/tmp}/ai-dev-env-zshrc.XXXXXX")"
  awk '
    $0 == "# >>> ai-dev-env path >>>" { managed = 1; next }
    $0 == "# <<< ai-dev-env path <<<" { managed = 0; next }
    !managed { print }
  ' "$ZSH_CONFIG_FILE" > "$ZSH_TEMP_FILE"
  chmod "$(stat -f '%Lp' "$ZSH_CONFIG_FILE")" "$ZSH_TEMP_FILE"
  mv "$ZSH_TEMP_FILE" "$ZSH_CONFIG_FILE"

  if [ -f "$BACKUP_DIR/zshrc.absent" ] && ! grep -q '[^[:space:]]' "$ZSH_CONFIG_FILE"; then
    rm -f "$ZSH_CONFIG_FILE"
  fi
fi

rm -f \
  "$STATE_DIR/installed-ghostty.sha256" \
  "$STATE_DIR/installed-tmux.sha256" \
  "$STATE_DIR/installed-dev.sha256" \
  "$STATE_DIR/installed-newtask.sha256" \
  "$STATE_DIR/installed-doctor.sha256" \
  "$STATE_DIR/zsh-path-block-added" \
  "$STATE_DIR/last-backup"

log "Configuration uninstall complete."
log "Ghostty, tmux, fonts, TPM, plugins, and backups were intentionally kept."
