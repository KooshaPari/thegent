#!/usr/bin/env bash
set -euo pipefail

ALLOWED_OWNER="${GH_NAMESPACE_ALLOWED_OWNER:-KooshaPari}"
AUTO_REDIRECT="${GH_NAMESPACE_GUARD_REDIRECT:-0}"

usage() {
  cat <<USAGE
Usage: $(basename "$0") <gh args...>

Guards PR/issue creation so targets must be under ${ALLOWED_OWNER}/*.

Env:
  GH_NAMESPACE_ALLOWED_OWNER   Allowed owner (default: KooshaPari)
  GH_NAMESPACE_GUARD_REDIRECT  1 to auto-rewrite target repo owner
USAGE
}

if [[ $# -eq 0 ]]; then
  usage
  exit 2
fi

sub1="${1:-}"
sub2="${2:-}"

is_guarded_create=0
if [[ "$sub1" == "pr" && "$sub2" == "create" ]]; then
  is_guarded_create=1
fi
if [[ "$sub1" == "issue" && "$sub2" == "create" ]]; then
  is_guarded_create=1
fi

extract_repo() {
  local -a argv=("$@")
  local i=0
  while (( i < ${#argv[@]} )); do
    case "${argv[$i]}" in
      -R|--repo)
        if (( i + 1 < ${#argv[@]} )); then
          printf '%s\n' "${argv[$((i+1))]}"
          return 0
        fi
        ;;
      --repo=*)
        printf '%s\n' "${argv[$i]#--repo=}"
        return 0
        ;;
    esac
    ((i+=1))
  done

  gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || true
}

if [[ "$is_guarded_create" -eq 1 ]]; then
  repo="$(extract_repo "$@")"
  if [[ -z "$repo" || "$repo" != */* ]]; then
    echo "namespace-guard: could not resolve target repository for creation command" >&2
    echo "namespace-guard: pass --repo ${ALLOWED_OWNER}/<repo> explicitly" >&2
    exit 42
  fi

  owner="${repo%%/*}"
  name="${repo#*/}"

  if [[ "$owner" != "$ALLOWED_OWNER" ]]; then
    redirected_repo="${ALLOWED_OWNER}/${name}"
    echo "namespace-guard: blocked $sub1 $sub2 on non-owned target '$repo'" >&2
    echo "namespace-guard: required namespace is '${ALLOWED_OWNER}/*'" >&2

    if [[ "$AUTO_REDIRECT" == "1" ]]; then
      # Remove explicit repo flags then inject rewritten --repo.
      new_args=()
      skip_next=0
      for arg in "$@"; do
        if [[ "$skip_next" == "1" ]]; then
          skip_next=0
          continue
        fi
        case "$arg" in
          -R|--repo)
            skip_next=1
            ;;
          --repo=*)
            ;;
          *)
            new_args+=("$arg")
            ;;
        esac
      done
      new_args+=("--repo" "$redirected_repo")
      echo "namespace-guard: auto-redirect enabled; rerouting to '$redirected_repo'" >&2
      exec gh "${new_args[@]}"
    fi

    echo "namespace-guard: rerun as:" >&2
    echo "  gh $sub1 $sub2 --repo $redirected_repo ..." >&2
    exit 42
  fi
fi

exec gh "$@"
