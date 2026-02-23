#!/usr/bin/env sh
set -eu

repo_root="$(git rev-parse --show-toplevel)"
repo_name="$(basename "$repo_root")"
worktree_root="${THGENT_WORKTREE_ROOT:-$repo_root/.worktrees}"
allow_legacy="${THGENT_WORKTREE_ALLOW_LEGACY:-0}"

slugify() {
  printf '%s' "$1" | tr '/:@ ' '----' | tr -cd 'A-Za-z0-9._-'
}

cmd="${1:-check}"
shift || true

case "$cmd" in
  path)
    branch="${1:?usage: worktree_governance.sh path <branch>}"
    printf '%s/%s--%s\n' "$worktree_root" "$repo_name" "$(slugify "$branch")"
    ;;

  new)
    branch="${1:?usage: worktree_governance.sh new <branch> [start-point]}"
    start_point="${2:-main}"
    target_path="$(printf '%s/%s--%s' "$worktree_root" "$repo_name" "$(slugify "$branch")")"
    mkdir -p "$worktree_root"
    git worktree add -b "$branch" "$target_path" "$start_point"
    printf '%s\n' "$target_path"
    ;;

  check)
    failed=0
    while IFS= read -r line; do
      case "$line" in
        worktree\ *)
          wt_path="${line#worktree }"
          if [ "$wt_path" = "$repo_root" ]; then
            continue
          fi
          case "$wt_path" in
            "$worktree_root"/*) : ;;
            *)
              if [ "$allow_legacy" = "1" ]; then
                echo "[WARN] legacy worktree path allowed: $wt_path" >&2
              else
                echo "[FAIL] worktree outside required root ($worktree_root): $wt_path" >&2
                failed=1
              fi
              continue
              ;;
          esac

          wt_base="$(basename "$wt_path")"
          case "$wt_base" in
            "$repo_name"--*)
              ;;
            *)
              if [ "$allow_legacy" = "1" ]; then
                echo "[WARN] legacy worktree name allowed: $wt_base" >&2
              else
                echo "[FAIL] worktree name must match ${repo_name}--<branch-slug>: $wt_base" >&2
                failed=1
              fi
              ;;
          esac
          ;;
      esac
    done <<EOF
$(git worktree list --porcelain)
EOF

    if [ "$failed" -ne 0 ]; then
      exit 1
    fi
    echo "[OK] worktree governance check passed"
    ;;

  *)
    echo "usage: worktree_governance.sh <check|new|path> ..." >&2
    exit 2
    ;;
esac
