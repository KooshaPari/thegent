#!/usr/bin/env sh
set -eu

repo_root="$(git rev-parse --show-toplevel)"
worktree_root="${THGENT_WORKTREE_ROOT:-$repo_root/.worktrees}"
allow_legacy="${THGENT_WORKTREE_ALLOW_LEGACY:-0}"

valid_scales="xs s m l xl"
valid_states="active review blocked integration done"

slugify() {
  printf '%s' "$1" | tr '/:@ ' '----' | tr -cd 'A-Za-z0-9._-'
}

usage() {
  cat <<'EOF'
worktree_governance.sh commands:
  path <domain> <scale> <change-anchor> [state]
  new <domain> <scale> <change-anchor> [start-point] [state]
  state <change-anchor> <new-state>
  list
  prune [--dry-run]
  check
EOF
}

ensure_scale() {
  scale="$1"
  case " $valid_scales " in
    *" $scale "*) ;;
    *)
      echo "[FAIL] invalid scale: $scale (expected xs|s|m|l|xl)" >&2
      exit 2
      ;;
  esac
}

ensure_state() {
  state="$1"
  case " $valid_states " in
    *" $state "*) ;;
    *)
      echo "[FAIL] invalid state: $state (expected active|review|blocked|integration|done)" >&2
      exit 2
      ;;
  esac
}

worktree_root_path() {
  printf '%s/%s/%s/%s/%s' "$worktree_root" "$1" "$2" "$3" "$4"
}

list_worktrees() {
  git worktree list --porcelain | awk '
    /^worktree / { path=$2; next }
    /^branch / {
      sub(/^refs\/heads\//, "", $2);
      print path "|" $2
    }
  '
}

current_worktree_by_anchor() {
  anchor="$1"
  list_worktrees | while IFS='|' read -r path branch; do
    rel="${path#"$worktree_root"/}"
    if [ "$rel" = "$path" ]; then
      continue
    fi
    if [ "$(printf '%s' "$rel" | awk -F/ '{print $3}')" = "$anchor" ]; then
      printf '%s\n' "$path"
    fi
  done
}

ensure_parent_path() {
  if [ ! -d "$worktree_root" ]; then
    mkdir -p "$worktree_root"
  fi
}

path_cmd() {
  domain="${1:?usage: worktree_governance.sh path <domain> <scale> <change-anchor> [state]}"
  scale="${2:?usage: worktree_governance.sh path <domain> <scale> <change-anchor> [state]}"
  anchor="${3:?usage: worktree_governance.sh path <domain> <scale> <change-anchor> [state]}"
  state="${4:-active}"
  ensure_scale "$scale"
  ensure_state "$state"
  printf '%s\n' "$(worktree_root_path "$domain" "$scale" "$(slugify "$anchor")" "$state")"
}

new_cmd() {
  domain="${1:?usage: worktree_governance.sh new <domain> <scale> <change-anchor> [start-point] [state]}"
  scale="${2:?usage: worktree_governance.sh new <domain> <scale> <change-anchor> [start-point] [state]}"
  anchor="${3:?usage: worktree_governance.sh new <domain> <scale> <change-anchor> [start-point] [state]}"
  start_point="${4:-main}"
  state="${5:-active}"
  ensure_scale "$scale"
  ensure_state "$state"

  slug_anchor="$(slugify "$anchor")"
  branch="$domain/$scale/$slug_anchor"
  target_path="$(worktree_root_path "$domain" "$scale" "$slug_anchor" "$state")"

  ensure_parent_path

  if git show-ref --verify --quiet "refs/heads/$branch"; then
    existing="$(list_worktrees | awk -F'|' -v branch="$branch" '$2 == branch { print $1 }' )"
    if [ -n "$existing" ]; then
      echo "[OK] Existing worktree for $branch: $existing"
      printf '%s\n' "$existing"
      return 0
    fi
    git worktree add "$target_path" "$branch"
  else
    git worktree add -b "$branch" "$target_path" "$start_point"
  fi

  printf '%s\n' "$target_path"
}

state_cmd() {
  anchor="${1:?usage: worktree_governance.sh state <change-anchor> <new-state>}"
  new_state="${2:?usage: worktree_governance.sh state <change-anchor> <new-state>}"
  ensure_state "$new_state"
  slug_anchor="$(slugify "$anchor")"

  matches="$(current_worktree_by_anchor "$slug_anchor")"
  if [ -z "$matches" ]; then
    echo "[FAIL] no governed worktree found for change-anchor: $slug_anchor" >&2
    exit 2
  fi

  count=0
  first_path=""
  while IFS= read -r path; do
    [ -z "$path" ] && continue
    count=$((count + 1))
    first_path="$path"
  done <<EOF
$matches
EOF

  if [ "$count" -ne 1 ]; then
    echo "[FAIL] change-anchor is ambiguous: $slug_anchor (found $count matches)" >&2
    printf '%s\n' "$matches" >&2
    exit 2
  fi

  current_state="$(printf '%s' "$first_path" | awk -F/ '{print $NF}')"
  if [ "$current_state" = "$new_state" ]; then
    printf '%s\n' "$first_path"
    return 0
  fi

  parent="$(printf '%s' "$first_path" | sed 's#/[^/]*$##')"
  target="$parent/$new_state"
  git worktree move -f -f "$first_path" "$target"
  printf '%s\n' "$target"
}

list_cmd() {
  list_worktrees | while IFS='|' read -r path branch; do
    rel="${path#"$worktree_root"/}"
    if [ "$rel" = "$path" ]; then
      printf '%s %s %s\n' "external" "-" "$path"
      continue
    fi
    domain="$(printf '%s' "$rel" | awk -F/ '{print $1}')"
    scale="$(printf '%s' "$rel" | awk -F/ '{print $2}')"
    anchor="$(printf '%s' "$rel" | awk -F/ '{print $3}')"
    state="$(printf '%s' "$rel" | awk -F/ '{print $4}')"
    printf '%-20s %-6s %-30s %-10s %s (%s)\n' "$domain" "$scale" "$anchor" "$state" "$path" "$branch"
  done
}

prune_cmd() {
  dry_run="${1:-}"
  if [ "$dry_run" = "--dry-run" ]; then
    is_dry_run=1
  elif [ -n "$dry_run" ]; then
    echo "usage: worktree_governance.sh prune [--dry-run]" >&2
    exit 2
  else
    is_dry_run=0
  fi

  list_worktrees | while IFS='|' read -r path branch; do
    rel="${path#"$worktree_root"/}"
    if [ "$rel" = "$path" ]; then
      continue
    fi
    if [ "$(printf '%s' "$rel" | awk -F/ '{if (NF==4 && $4=="done") print 1; else print 0}')" = "1" ]; then
      if [ "$is_dry_run" -eq 1 ]; then
        echo "[DRY-RUN] git worktree remove --force $path"
      else
        git worktree remove --force "$path"
      fi
    fi
  done
}

check_cmd() {
  failed=0
  while IFS='|' read -r path branch; do
    if [ "$path" = "$repo_root" ]; then
      continue
    fi

    rel="${path#"$worktree_root"/}"
    if [ "$rel" = "$path" ]; then
      if [ "$allow_legacy" = "1" ]; then
        echo "[WARN] legacy worktree path allowed: $path" >&2
        continue
      fi
      echo "[FAIL] worktree outside required root ($worktree_root): $path" >&2
      failed=1
      continue
    fi

    extra_fields=
    IFS='/' read -r domain scale anchor state extra_fields <<EOF
$rel
EOF

    if [ -z "$domain" ] || [ -z "$scale" ] || [ -z "$anchor" ] || [ -z "$state" ] || [ -n "$extra_fields" ]; then
      if [ "$allow_legacy" = "1" ]; then
        echo "[WARN] legacy layout allowed: $path" >&2
      else
        echo "[FAIL] invalid worktree layout: $path" >&2
        failed=1
      fi
      continue
    fi

    case " $valid_scales " in
      *" $scale "*) ;;
      *)
        if [ "$allow_legacy" = "1" ]; then
          echo "[WARN] legacy scale allowed: $path" >&2
        else
          echo "[FAIL] invalid worktree scale ($scale): $path" >&2
          failed=1
        fi
        ;;
    esac

    case " $valid_states " in
      *" $state "*) ;;
      *)
        if [ "$allow_legacy" = "1" ]; then
          echo "[WARN] legacy state allowed: $path" >&2
        else
          echo "[FAIL] invalid worktree state ($state): $path" >&2
          failed=1
        fi
        ;;
    esac
  done <<EOF
$(list_worktrees)
EOF

  if [ "$failed" -ne 0 ]; then
    exit 1
  fi
  echo "[OK] worktree governance check passed"
}

cmd="${1:-check}"
shift || true

case "$cmd" in
  path)
    path_cmd "$@"
    ;;
  new)
    new_cmd "$@"
    ;;
  state)
    state_cmd "$@"
    ;;
  list)
    [ $# -eq 0 ] || { usage >&2; exit 2; }
    list_cmd
    ;;
  prune)
    prune_cmd "$@"
    ;;
  check)
    [ $# -eq 0 ] || { usage >&2; exit 2; }
    check_cmd
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
