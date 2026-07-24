#!/usr/bin/env bash
# Run Playtester with one strategy.
#
#   ./scripts/run-playtester.sh coverage
#   ./scripts/run-playtester.sh random 20260723
set -euo pipefail

STRATEGY="${1:?usage: run-playtester.sh <coverage|adversarial|malformed|exhaust|random> [seed]}"
SEED="${2:-$RANDOM}"

case "$STRATEGY" in
  coverage|adversarial|malformed|exhaust|random) ;;
  *) echo "Unknown strategy: $STRATEGY" >&2; exit 1 ;;
esac

echo "Playtester -> ${STRATEGY} (seed ${SEED})"

opencode run --agent playtester \
  "Run a playtest pass on FALLOUT: THE LAST DAY BEFORE using the '${STRATEGY}' strategy with seed ${SEED}. Follow .opencode/agents/playtester.md exactly. Remember the input surface is numbered menu selection, not verbs, and sequences are positional. Always FALLOUT_TEST_MODE=1 and timeout. Report findings only from transcripts you actually produced. Zero findings is a valid outcome."
