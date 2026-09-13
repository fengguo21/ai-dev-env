#!/usr/bin/env bash
# Shared, side-effect-free helpers. Compatible with macOS Bash 3.2.

ai_canonical_dir() {
  (cd -- "$1" 2>/dev/null && pwd -P)
}

ai_hash() {
  printf '%s' "$1" | shasum -a 256 | awk '{print substr($1, 1, 10)}'
}

ai_slug() {
  local slug
  slug="$(printf '%s' "$1" | LC_ALL=C tr '[:space:].' '-' | LC_ALL=C tr -cd 'A-Za-z0-9_-')"
  printf '%s' "${slug:-project}"
}

ai_repo_primary() {
  local entry
  while IFS= read -r -d '' entry; do
    case "$entry" in
      'worktree '*) ai_canonical_dir "${entry#worktree }"; return ;;
    esac
  done < <(git -C "${1:-.}" worktree list --porcelain -z 2>/dev/null)
  return 1
}

ai_repo_id() {
  local root
  root="$(ai_repo_primary "${1:-.}")" || return 1
  printf '%s-%s\n' "$(ai_slug "${root##*/}")" "$(ai_hash "$root")"
}

ai_session_name() {
  local root
  root="$(ai_canonical_dir "$1")" || return 1
  printf 'ai-%s-%s\n' "$(ai_slug "${root##*/}")" "$(ai_hash "$root")"
}

ai_dev_exec() {
  if [ -n "${SCRIPT_ROOT:-}" ] && [ -f "$SCRIPT_ROOT/dev" ]; then
    printf '%s\n' "$SCRIPT_ROOT/dev"
  else
    command -v dev
  fi
}

# Bound optional catalog queries without requiring GNU timeout on macOS.
ai_timeout() (
  local seconds="$1" child timer result=0
  shift
  "$@" &
  child=$!
  (sleep "$seconds"; kill -TERM "$child" 2>/dev/null; sleep 1; kill -KILL "$child" 2>/dev/null) &
  timer=$!
  wait "$child" || result=$?
  kill "$timer" 2>/dev/null || true
  wait "$timer" 2>/dev/null || true
  return "$result"
)

# Optional isolated socket for diagnostics and automation, never the live server.
if [ -n "${AI_DEV_TMUX_SOCKET:-}" ]; then
  tmux() { command tmux -L "$AI_DEV_TMUX_SOCKET" "$@"; }
fi
