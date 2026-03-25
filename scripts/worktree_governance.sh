#!/usr/bin/env sh
set -eu

repo_root="$(git rev-parse --show-toplevel)"
worktree_root="${THGENT_WORKTREE_ROOT:-$repo_root/.worktrees}"
valid_states="active review blocked integration done"

die() {
  echo "[FAIL] $*" >&2
  exit 1
}

warn() {
  echo "[WARN] $*" >&2
}

usage() {
  cat >&2 <<'EOF'
usage: worktree_governance.sh <check|path|new|state|migrate-legacy|list|prune|refresh> ...

  path <domain> <scale> <change-anchor> <state>
  new <domain> <scale> <change-anchor> [start-point]
  state <change-anchor> <new-state>
  migrate-legacy <legacy-path> <domain> <scale> <change-anchor> [<state>]
  list
  prune [--dry-run]
  refresh <change-anchor> [--remote <name>] [--ref <upstream-ref>] [--strategy <rebase|merge>]
  check
EOF
  exit 2
}

is_valid_state() {
  case " $valid_states " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

validate_path_component() {
  field="$1"
  value="$2"

  case "$value" in
    ""|-*|*[!a-z0-9-]*)
      die "invalid $field: $value (expected [a-z0-9-]+)"
      ;;
  esac
}

validate_remote_name() {
  remote="$1"

  case "$remote" in
    ""|-*|*[!a-zA-Z0-9._-]*)
      die "invalid remote name: $remote (expected [a-zA-Z0-9._-]+)"
      ;;
  esac
}

validate_ref_name() {
  ref="$1"

  case "$ref" in
    ""|-*|*[!a-zA-Z0-9._/-]*)
      die "invalid upstream ref: $ref (expected a conservative branch/ref name)"
      ;;
  esac
}

validate_start_point() {
  start_point="$1"

  case "$start_point" in
    -*)
      die "invalid start point: $start_point"
      ;;
  esac

  git rev-parse --verify --quiet "${start_point}^{commit}" >/dev/null 2>&1 || die "invalid start point: $start_point"
}

escape_glob() {
  printf '%s' "$1" | sed 's/[][?*]/\\&/g'
}

is_under_worktree_root() {
  escaped_root="$(escape_glob "$worktree_root")"
  case "$1" in
    "$escaped_root"/*) return 0 ;;
    *) return 1 ;;
  esac
}

is_structured_worktree_path() {
  [ "$(dirname "$(dirname "$(dirname "$(dirname "$1")")")")" = "$worktree_root" ] || return 1
  case "$(basename "$(dirname "$(dirname "$(dirname "$1")")")")" in ""|-*|*[!a-z0-9-]*) return 1 ;; esac
  case "$(basename "$(dirname "$(dirname "$1")")")" in ""|-*|*[!a-z0-9-]*) return 1 ;; esac
  case "$(basename "$(dirname "$1")")" in ""|-*|*[!a-z0-9-]*) return 1 ;; esac
  return 0
}

branch_name() {
  printf '%s/%s/%s' "$1" "$2" "$3"
}

worktree_path() {
  printf '%s/%s/%s/%s/%s' "$worktree_root" "$1" "$2" "$3" "$4"
}

parse_structured_path() {
  structured_state="$(basename "$1")"
  structured_change_anchor="$(basename "$(dirname "$1")")"
  structured_scale="$(basename "$(dirname "$(dirname "$1")")")"
  structured_domain="$(basename "$(dirname "$(dirname "$(dirname "$1")")")")"
  validate_path_component "structured domain" "$structured_domain"
  validate_path_component "structured scale" "$structured_scale"
  validate_path_component "structured change anchor" "$structured_change_anchor"
  is_valid_state "$structured_state" || die "invalid structured state: $structured_state"
}

emit_worktree_record() {
  path="$1"; branch="$2"; prunable="$3"
  if [ "$path" = "$repo_root" ]; then
    printf 'state=primary branch=%s path=%s prunable=%s\n' "${branch:-detached}" "$path" "$prunable"
  elif is_structured_worktree_path "$path"; then
    parse_structured_path "$path"
    printf 'state=%s branch=%s path=%s prunable=%s\n' "$structured_state" "$branch" "$path" "$prunable"
  else
    printf 'state=legacy branch=%s path=%s prunable=%s\n' "$branch" "$path" "$prunable"
  fi
}

validate_structured_worktree_record() {
  path="$1"; branch="$2"; prunable="$3"
  is_under_worktree_root "$path" || { warn "worktree outside required root ($worktree_root): $path"; failed=1; return 0; }
  if ! is_structured_worktree_path "$path"; then
    warn "legacy or malformed worktree inside structured root: $path"; failed=1; return 0
  fi
  parse_structured_path "$path"
  expected_path="$(worktree_path "$structured_domain" "$structured_scale" "$structured_change_anchor" "$structured_state")"
  expected_branch="$(branch_name "$structured_domain" "$structured_scale" "$structured_change_anchor")"
  if ! is_valid_state "$structured_state"; then warn "invalid worktree state: $path"; failed=1; fi
  [ "$path" = "$expected_path" ] || { warn "worktree path mismatch: expected $expected_path, found $path"; failed=1; }
  [ "$branch" = "$expected_branch" ] || { warn "worktree branch mismatch: expected $expected_branch, found ${branch:-<detached>}"; failed=1; }
  [ "$prunable" = "1" ] || return 0
  warn "worktree is prunable/broken: $path"
  failed=1
}

record_list() {
  git worktree list --porcelain |
    awk '
      function emit() {
        if (path == "") {
          return
        }
        print path "\t" branch "\t" prunable
      }

      /^worktree / {
        emit()
        path = substr($0, 10)
        branch = ""
        prunable = 0
        next
      }

      /^branch / {
        branch = substr($0, 8)
        if (branch == "HEAD") {
          branch = ""
        } else if (branch ~ /^refs\/heads\//) {
          branch = substr(branch, 12)
        }
        next
      }

      /^prunable / {
        prunable = 1
        next
      }

      END {
        emit()
      }
    '
}

find_record_by_anchor() {
  anchor="$1"
  match_count="$(record_list | awk -F '\t' -v anchor="$anchor" '
    {
      n = split($1, parts, "/")
      if (n >= 2 && parts[n - 1] == anchor) {
        matches += 1
      }
    }

    END {
      print matches + 0
    }
  ')"

  case "$match_count" in
    0)
      die "no worktree found for change anchor: $anchor"
      ;;
    1)
      record_list | awk -F '\t' -v anchor="$anchor" '
        {
          n = split($1, parts, "/")
          if (n >= 2 && parts[n - 1] == anchor) {
            print $0
            exit 0
          }
        }
      '
      ;;
    *)
      die "ambiguous change anchor: $anchor ($match_count worktrees match)"
      ;;
  esac
}

find_record_by_path() {
  legacy_path="$1"
  record_list | awk -F '\t' -v path="$legacy_path" '
    $1 == path {
      print $0
      exit 0
    }
  '
}

cmd="${1:-check}"
shift || true

case "$cmd" in
  path)
    [ "$#" -eq 4 ] || usage
    domain="$1"
    scale="$2"
    change_anchor="$3"
    state="$4"
    validate_path_component "domain" "$domain"
    validate_path_component "scale" "$scale"
    validate_path_component "change anchor" "$change_anchor"
    is_valid_state "$state" || die "invalid state: $state"
    printf '%s\n' "$(worktree_path "$domain" "$scale" "$change_anchor" "$state")"
    ;;

  new)
    [ "$#" -ge 3 ] && [ "$#" -le 4 ] || usage
    domain="$1"
    scale="$2"
    change_anchor="$3"
    start_point="${4:-main}"
    validate_path_component "domain" "$domain"
    validate_path_component "scale" "$scale"
    validate_path_component "change anchor" "$change_anchor"
    validate_start_point "$start_point"
    target_branch="$(branch_name "$domain" "$scale" "$change_anchor")"
    target_path="$(worktree_path "$domain" "$scale" "$change_anchor" active)"
    mkdir -p "$(dirname "$target_path")"
    [ ! -e "$target_path" ] || die "target path already exists: $target_path"
    git worktree add -b "$target_branch" "$target_path" "$start_point"
    printf '%s\n' "$target_path"
    ;;

  refresh)
    [ "$#" -ge 1 ] || usage
    change_anchor="$1"
    shift
    validate_path_component "change anchor" "$change_anchor"
    remote="origin"
    upstream_ref=""
    strategy="rebase"
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --remote)
          [ "$#" -ge 2 ] || usage
          remote="$2"
          shift 2
          ;;
        --ref|--upstream)
          [ "$#" -ge 2 ] || usage
          upstream_ref="$2"
          shift 2
          ;;
        --strategy)
          [ "$#" -ge 2 ] || usage
          strategy="$2"
          shift 2
          ;;
        *)
          usage
          ;;
      esac
    done

    validate_remote_name "$remote"
    case "$strategy" in
      rebase|merge) ;;
      *) die "invalid strategy: $strategy" ;;
    esac

    record="$(find_record_by_anchor "$change_anchor")"
    record_path="$(printf '%s\n' "$record" | awk -F '\t' '{print $1}')"
    record_branch="$(printf '%s\n' "$record" | awk -F '\t' '{print $2}')"

    [ "$record_path" != "$repo_root" ] || die "change anchor belongs to the primary checkout: $change_anchor"
    is_under_worktree_root "$record_path" || die "worktree outside required root ($worktree_root): $record_path"

    parse_structured_path "$record_path"
    expected_branch="$(branch_name "$structured_domain" "$structured_scale" "$structured_change_anchor")"
    [ "$record_branch" = "$expected_branch" ] || die "branch/path mismatch: $record_branch != $expected_branch"

    if [ -z "$upstream_ref" ]; then
      upstream_ref="$remote/$record_branch"
    fi
    validate_ref_name "$upstream_ref"

    dirty_status="$(git -C "$record_path" status --porcelain)"
    [ -z "$dirty_status" ] || die "worktree has uncommitted changes: $record_path"

    git fetch "$remote" --prune
    git -C "$record_path" rev-parse --verify "${upstream_ref}^{commit}" >/dev/null 2>&1 || die "invalid upstream ref: $upstream_ref"

    case "$strategy" in
      rebase)
        git -C "$record_path" rebase "$upstream_ref"
        ;;
      merge)
        git -C "$record_path" merge --no-ff --no-edit "$upstream_ref"
        ;;
    esac

    printf '[OK] refreshed worktree: %s -> %s (%s)\n' "$record_path" "$upstream_ref" "$strategy"
    ;;

  migrate-legacy)
    [ "$#" -ge 4 ] && [ "$#" -le 5 ] || usage
    legacy_path="$1"
    domain="$2"
    scale="$3"
    change_anchor="$4"
    new_state="${5:-active}"
    validate_path_component "domain" "$domain"
    validate_path_component "scale" "$scale"
    validate_path_component "change anchor" "$change_anchor"
    is_valid_state "$new_state" || die "invalid state: $new_state"

    record="$(find_record_by_path "$legacy_path")"
    [ -n "$record" ] || die "no worktree found at path: $legacy_path"
    record_path="$(printf '%s\n' "$record" | awk -F '\t' '{print $1}')"
    record_branch="$(printf '%s\n' "$record" | awk -F '\t' '{print $2}')"

    [ "$record_path" != "$repo_root" ] || die "primary checkout cannot be migrated: $legacy_path"
    is_under_worktree_root "$record_path" && die "worktree already under structured root: $record_path"

    dirty_status="$(git -C "$record_path" status --porcelain)"
    [ -z "$dirty_status" ] || die "worktree has uncommitted changes: $record_path"
    [ "$record_branch" != "" ] && [ "$record_branch" != "(detached)" ] || die "worktree is detached: $record_path"

    target_branch="$(branch_name "$domain" "$scale" "$change_anchor")"
    target_path="$(worktree_path "$domain" "$scale" "$change_anchor" "$new_state")"
    [ ! -e "$target_path" ] || die "target path already exists: $target_path"
    git show-ref --verify --quiet "refs/heads/$target_branch" && die "target branch already exists: $target_branch"

    git -C "$record_path" branch -m "$target_branch"
    mkdir -p "$(dirname "$target_path")"
    git worktree move "$record_path" "$target_path"
    printf '[OK] migrated legacy worktree: %s -> %s (%s)\n' "$record_path" "$target_path" "$target_branch"
    ;;

  state)
    [ "$#" -eq 2 ] || usage
    change_anchor="$1"
    new_state="$2"
    validate_path_component "change anchor" "$change_anchor"
    is_valid_state "$new_state" || die "invalid state: $new_state"

    record="$(find_record_by_anchor "$change_anchor")"
    record_path="$(printf '%s\n' "$record" | awk -F '\t' '{print $1}')"
    record_branch="$(printf '%s\n' "$record" | awk -F '\t' '{print $2}')"

    [ "$record_path" != "$repo_root" ] || die "change anchor belongs to the primary checkout: $change_anchor"
    is_under_worktree_root "$record_path" || die "worktree outside required root ($worktree_root): $record_path"

    parse_structured_path "$record_path"
    expected_branch="$(branch_name "$structured_domain" "$structured_scale" "$structured_change_anchor")"
    [ "$record_branch" = "$expected_branch" ] || die "branch/path mismatch: $record_branch != $expected_branch"

    new_path="$(worktree_path "$structured_domain" "$structured_scale" "$structured_change_anchor" "$new_state")"
    [ "$record_path" != "$new_path" ] || {
      printf '%s\n' "$new_path"
      exit 0
    }
    mkdir -p "$(dirname "$new_path")"
    [ ! -e "$new_path" ] || die "target path already exists: $new_path"
    git worktree move "$record_path" "$new_path"
    printf '%s\n' "$new_path"
    ;;

  list)
    [ "$#" -eq 0 ] || usage
    records="$(record_list)"
    if [ -z "$records" ]; then
      exit 0
    fi
    while IFS="$(printf '\t')" read -r path branch prunable; do
      [ -n "$path" ] || continue
      emit_worktree_record "$path" "$branch" "$prunable"
    done <<EOF
$records
EOF
    ;;

  prune)
    dry_run=0
    if [ "${1:-}" = "--dry-run" ]; then
      dry_run=1
      shift
    fi
    [ "$#" -eq 0 ] || usage

    records="$(record_list)"
    if [ -n "$records" ]; then
      while IFS="$(printf '\t')" read -r path branch prunable; do
        [ -n "$path" ] || continue
        [ "$path" != "$repo_root" ] || continue

        if ! is_structured_worktree_path "$path"; then
          validate_structured_worktree_record "$path" "$branch" "$prunable"
          continue
        fi

        parse_structured_path "$path"
        expected_path="$(worktree_path "$structured_domain" "$structured_scale" "$structured_change_anchor" "$structured_state")"
        [ "$path" = "$expected_path" ] || die "worktree path mismatch: expected $expected_path, found $path"
        [ "$structured_state" = "done" ] || continue
        [ "$prunable" = "1" ] || die "refusing to prune live done worktree: $path"
        if [ "$dry_run" = 1 ]; then
          echo "[DRY-RUN] remove done worktree: $path"
        else
          git worktree remove --force "$path"
        fi
      done <<EOF
$records
EOF
    fi

    if [ "$dry_run" = 1 ]; then
      git worktree prune --dry-run
    else
      git worktree prune
      echo "[OK] worktree prune complete"
    fi
    ;;

  check)
    [ "$#" -eq 0 ] || usage
    failed=0
    records="$(record_list)"
    if [ -n "$records" ]; then
      while IFS="$(printf '\t')" read -r path branch prunable; do
        [ -n "$path" ] || continue
        [ "$path" != "$repo_root" ] || continue
        validate_structured_worktree_record "$path" "$branch" "$prunable"
      done <<EOF
$records
EOF
    fi

    if [ "$failed" -ne 0 ]; then
      exit 1
    fi
    echo "[OK] worktree governance check passed"
    ;;

  *)
    usage
    ;;
esac
