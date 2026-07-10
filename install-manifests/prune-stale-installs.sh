#!/usr/bin/env bash
# Remove ONLY symlinks that point into this skills repo and are NOT in the
# keep manifests. Preserves real directories and external skills.
#
# Usage:
#   ./install-manifests/prune-stale-installs.sh              # dry-run all known paths
#   ./install-manifests/prune-stale-installs.sh --apply      # apply
#   ./install-manifests/prune-stale-installs.sh --apply ~/.claude/skills
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEEP_PUBLIC="$REPO_ROOT/install-manifests/codex-keep.txt"
KEEP_LOCAL="$REPO_ROOT/install-manifests/codex-keep.local.txt"
APPLY=0
TARGETS=()

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    -h|--help)
      sed -n '1,12p' "$0"
      exit 0
      ;;
    *) TARGETS+=("$arg") ;;
  esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  TARGETS=(
    "$HOME/.agents/skills"
    "$HOME/.claude/skills"
    "$HOME/.config/opencode/skill"
    "$HOME/.gemini/skills"
    "$HOME/.kiro/skills"
  )
fi

load_keep() {
  local f
  KEEP_SET=()
  for f in "$KEEP_PUBLIC" "$KEEP_LOCAL"; do
    [[ -f "$f" ]] || continue
    while IFS= read -r line || [[ -n "$line" ]]; do
      [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
      KEEP_SET+=("$line")
    done < "$f"
  done
}

is_keep() {
  local name="$1" k
  for k in "${KEEP_SET[@]}"; do
    [[ "$k" == "$name" ]] && return 0
  done
  return 1
}

# True if resolved path is under this repo's skill tree
is_repo_skill_target() {
  local resolved="$1"
  [[ "$resolved" == "$REPO_ROOT"/* ]] || return 1
  # skill root is REPO_ROOT/<skill-name>
  local rel="${resolved#"$REPO_ROOT"/}"
  local top="${rel%%/*}"
  [[ -n "$top" && -f "$REPO_ROOT/$top/SKILL.md" ]]
}

prune_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "SKIP missing $dir"
    return 0
  fi
  echo "=== $dir ==="
  local name target resolved removed=0 kept=0 external=0 realdir=0
  shopt -s nullglob
  for entry in "$dir"/*; do
    name="$(basename "$entry")"
    if [[ ! -L "$entry" ]]; then
      if [[ -d "$entry" ]]; then
        echo "KEEP real-dir $name"
        realdir=$((realdir + 1))
      else
        echo "KEEP non-link $name"
        external=$((external + 1))
      fi
      continue
    fi
    target="$(readlink "$entry")"
    resolved="$(readlink -f "$entry" 2>/dev/null || true)"
    if [[ -z "$resolved" ]] || ! is_repo_skill_target "$resolved"; then
      echo "KEEP external-link $name -> $target"
      external=$((external + 1))
      continue
    fi
    if is_keep "$name"; then
      # ensure points at repo skill dir (not nested)
      local want="$REPO_ROOT/$name"
      if [[ "$resolved" != "$(readlink -f "$want")" ]]; then
        echo "RELINK keep $name -> $want"
        if [[ $APPLY -eq 1 ]]; then
          ln -sfn "$want" "$entry"
        fi
      else
        echo "KEEP keep-set $name"
      fi
      kept=$((kept + 1))
      continue
    fi
    echo "PRUNE $name -> $resolved"
    if [[ $APPLY -eq 1 ]]; then
      rm -f "$entry"
    fi
    removed=$((removed + 1))
  done
  echo "summary kept=$kept pruned=$removed external=$external realdir=$realdir apply=$APPLY"
}

load_keep
echo "repo=$REPO_ROOT"
echo "keep=${KEEP_SET[*]}"
echo "mode=$([[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN)"

for t in "${TARGETS[@]}"; do
  prune_dir "$t"
done
