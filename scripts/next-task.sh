#!/usr/bin/env bash
# Next agent-ready issue number, oldest first.
# Empty output means the queue is empty — a normal state.
set -euo pipefail
gh issue list --label agent-ready --state open \
  --json number,createdAt \
  --jq 'sort_by(.createdAt) | .[0] | select(. != null) | .number'
