#!/usr/bin/env bash
# Run Builder against one issue. Fresh context per issue.
#
#   ./scripts/run-builder.sh 12
#   ./scripts/run-builder.sh          # next in queue
set -euo pipefail

ISSUE="${1:-$(./scripts/next-task.sh)}"
if [ -z "$ISSUE" ]; then
  echo "No agent-ready issues. Nothing to do."
  exit 0
fi

echo "Builder -> issue #${ISSUE}"
# export GH_TOKEN="${BUILDER_TOKEN:-$GH_TOKEN}"

opencode run --agent builder \
  "Work GitHub issue #${ISSUE} on FALLOUT: THE LAST DAY BEFORE. Follow AGENTS.md exactly. Read the issue with 'gh issue view ${ISSUE}' first. Set FALLOUT_TEST_MODE=1 and wrap in timeout for every non-interactive run. Do not write scene prose. If the acceptance criteria are ambiguous, comment on the issue and stop."
