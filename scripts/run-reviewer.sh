#!/usr/bin/env bash
# Review one open PR.
#   ./scripts/run-reviewer.sh 7
set -euo pipefail
PR="${1:?usage: run-reviewer.sh <pr-number>}"

echo "Reviewer -> PR #${PR}"

opencode run --agent reviewer \
  "Review PR #${PR} on FALLOUT: THE LAST DAY BEFORE. Read the linked issue's acceptance criteria BEFORE the diff. Check out the branch and run 'make check' yourself — do not trust the PR body. Check especially: does the diff add or rewrite scene prose (human-only), and does any test assert exact HP/damage/XP (flaky, RNG is unseeded). Report any mismatch between what the PR claims and what you observed."
