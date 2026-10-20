#!/usr/bin/env bash
# Applies repository settings and protects the default branch on GitHub.
#
# Usage (on Windows, from Git Bash): bash scripts/setup-github.sh [solo|team] [extra required check]...
#   solo: pull request + green CI required, no approval (GitHub forbids approving your own PR).
#   team: same, plus one approving review from any collaborator with write access, and
#         stale-approval dismissal. Needs at least one collaborator besides you with write access,
#         or no PR of yours could ever be merged. .github/CODEOWNERS only requests reviewers.
#         Requiring code-owner approval instead (REQUIRE_CODE_OWNER_REVIEW=true) needs at least two
#         owners who review each other: nobody can approve their own PR.
#   Extra arguments are more CI job names that must pass, e.g. "stack (python)".
#
# Requires an authenticated GitHub CLI (`gh auth login`). Safe to re-run.
# Branch rulesets need a public repository, or GitHub Pro/Team for a private one.
set -euo pipefail

readonly MODE="${1:-solo}"
if (( $# > 0 )); then shift; fi
readonly RULESET_NAME="protect-default-branch"
# Must match the CI job name in .github/workflows/ci.yml.
readonly REQUIRED_CHECK="check"
# Off by default: with a single code owner, that owner's own PRs could never be approved.
readonly REQUIRE_CODE_OWNER_REVIEW="${REQUIRE_CODE_OWNER_REVIEW:-false}"

required_checks_json="{ \"context\": \"$REQUIRED_CHECK\" }"
required_checks_list="$REQUIRED_CHECK"
for extra_check in "$@"; do
  required_checks_json+=", { \"context\": \"$extra_check\" }"
  required_checks_list+=", $extra_check"
done

case "$MODE" in
  solo) approval_count=0; is_team=false ;;
  team) approval_count=1; is_team=true ;;
  *) echo "Unknown mode '$MODE' (expected solo or team)" >&2; exit 1 ;;
esac
case "$REQUIRE_CODE_OWNER_REVIEW" in
  true | false) ;;
  *) echo "REQUIRE_CODE_OWNER_REVIEW must be true or false" >&2; exit 1 ;;
esac

repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"

# A required approval with nobody else able to give it would block every PR for good.
# Compare with the signed-in user, not the repository owner, which may be an organization.
if [[ "$MODE" == team ]]; then
  me="$(gh api user --jq .login)"
  other_writers="$(gh api "repos/$repo/collaborators" --paginate \
    --jq ".[] | select(.login != \"$me\" and .permissions.push) | .login")"
  if [[ -z "$other_writers" ]]; then
    echo "Team mode needs a collaborator besides $me with write access: with only you, every PR" >&2
    echo "would wait for an approval nobody can give. Add one first, or use solo mode." >&2
    exit 1
  fi
fi

echo "Configuring $repo in $MODE mode (required checks: $required_checks_list)"

# Squash merge only: one commit per pull request keeps main's history readable.
gh repo edit "$repo" \
  --enable-squash-merge \
  --enable-merge-commit=false \
  --enable-rebase-merge=false \
  --delete-branch-on-merge \
  --enable-auto-merge

# Dependency graph + Dependabot alerts: the dependency-review license check needs the graph, and
# a repository made public after being private does not always have it.
gh api --method PUT "repos/$repo/vulnerability-alerts" >/dev/null

ruleset_json="$(cat <<JSON
{
  "name": "$RULESET_NAME",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": $approval_count,
        "dismiss_stale_reviews_on_push": $is_team,
        "require_code_owner_review": $REQUIRE_CODE_OWNER_REVIEW,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [$required_checks_json]
      }
    }
  ]
}
JSON
)"

existing_id="$(gh api "repos/$repo/rulesets" --jq ".[] | select(.name == \"$RULESET_NAME\") | .id")"
if [[ -n "$existing_id" ]]; then
  gh api --method PUT "repos/$repo/rulesets/$existing_id" --input - <<<"$ruleset_json" >/dev/null
  echo "Updated ruleset '$RULESET_NAME'"
else
  gh api --method POST "repos/$repo/rulesets" --input - <<<"$ruleset_json" >/dev/null
  echo "Created ruleset '$RULESET_NAME'"
fi
