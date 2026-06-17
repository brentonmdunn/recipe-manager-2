#!/usr/bin/env bash
# Pull the latest code and redeploy the Recipe Manager stack in place.
#
# - Fetches + fast-forwards the current branch (default: main).
# - Rebuilds images and restarts the stack with `docker compose up -d --build`.
# - Prunes dangling images afterwards to reclaim disk space.
#
# Use `--no-pull` to skip the git pull step (useful when deploying a local
# change you haven't pushed yet) and `--branch <name>` to update a different
# branch.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

log() { printf '\033[1;34m[update]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[update]\033[0m %s\n' "$*" >&2; }
err() { printf '\033[1;31m[update]\033[0m %s\n' "$*" >&2; }

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
BRANCH="${BRANCH:-main}"
DO_PULL=1
DO_PRUNE=1

usage() {
  cat <<EOF
Usage: $(basename "$0") [--no-pull] [--no-prune] [--branch <name>]

Options:
  --no-pull         Skip 'git pull'; deploy whatever is currently checked out.
  --no-prune        Skip 'docker image prune' at the end.
  --branch <name>   Branch to update (default: $BRANCH).
  -h, --help        Show this help.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --no-pull) DO_PULL=0; shift ;;
    --no-prune) DO_PRUNE=0; shift ;;
    --branch) BRANCH="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Required command '$1' not found in PATH."
    exit 1
  fi
}

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

require_cmd docker
require_cmd git
if ! docker compose version >/dev/null 2>&1; then
  err "'docker compose' plugin not available. Install Docker Compose v2."
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  err "Compose file '$COMPOSE_FILE' not found (run from the repo root)."
  exit 1
fi

if [ "$DO_PULL" -eq 1 ]; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    err "Working tree has uncommitted changes. Commit, stash, or rerun with --no-pull."
    git status --short
    exit 1
  fi
  log "Fetching latest refs from origin..."
  git fetch --prune origin
  current_branch="$(git rev-parse --abbrev-ref HEAD)"
  if [ "$current_branch" != "$BRANCH" ]; then
    log "Checking out $BRANCH (was $current_branch)."
    git checkout "$BRANCH"
  fi
  log "Fast-forwarding $BRANCH..."
  git merge --ff-only "origin/$BRANCH"
else
  log "Skipping git pull (--no-pull)."
fi

log "Rebuilding and restarting containers..."
compose up -d --build --remove-orphans

log "Current status:"
compose ps

if [ "$DO_PRUNE" -eq 1 ]; then
  log "Pruning dangling images..."
  docker image prune -f >/dev/null
fi

log "Update complete."
