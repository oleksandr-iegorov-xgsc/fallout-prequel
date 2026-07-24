#!/usr/bin/env bash
# Turn an accepted idea into issues.
#   ./scripts/run-planner.sh "split Player class into its own module"
set -euo pipefail
IDEA="${1:?usage: run-planner.sh \"<idea>\"}"

opencode run --agent planner \
  "Turn this into GitHub issues for FALLOUT: THE LAST DAY BEFORE: ${IDEA}. Check it against SOUL.md pillars, non-goals, roadmap ordering, and open questions first. Respect the three-file rule. Never write criteria asserting exact HP/damage/XP. If it requires new scene prose, label needs-human and say why."
