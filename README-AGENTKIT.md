# Agent kit — FALLOUT: THE LAST DAY BEFORE

Drop-in agent infrastructure for this project. Unzip into your repo
root next to `fallout_prequel.py`.

Unlike a generic template, `SOUL.md` and `AGENTS.md` are written
against your actual code — the scene list, the twenty story flags,
`FALLOUT_TEST_MODE`, `GameLogger`, the numbered-menu input surface,
and the unseeded RNG.

---

## Layout

    <repo root>
    ├── fallout_prequel.py         your game (already there)
    │
    ├── SOUL.md                    game identity. HUMAN-OWNED.
    ├── AGENTS.md                  operational contract. HUMAN-OWNED.
    │
    ├── opencode.json              providers, models, permissions
    ├── opencode.local.jsonc.example   vLLM variant (128k/64k split)
    ├── Makefile                   lint / test / smoke / check
    │
    ├── .opencode/agents/          HUMAN-OWNED
    │   ├── builder.md             writes code, opens PRs
    │   ├── reviewer.md            reviews, never pushes
    │   ├── playtester.md          generates menu sequences
    │   ├── planner.md             writes issues, no code
    │   └── ideator.md             weekly proposals (optional)
    │
    ├── .github/
    │   ├── workflows/ci.yml       where rules are ENFORCED
    │   ├── ISSUE_TEMPLATE/{story,bug}.md
    │   └── pull_request_template.md
    │
    ├── scripts/                   run-{builder,reviewer,playtester,planner}.sh
    ├── docs/{AUTH,input-surface}.md
    ├── tests/scripts/             regression corpus
    └── logs/playtest/             notes + generated transcripts

---

## Setup

    # 1. Credentials — see docs/AUTH.md
    opencode
    /connect
    /models

    # 2. GitHub
    gh auth login

    # 3. Labels
    gh label create agent-ready --color 0e8a16
    gh label create needs-human --color d93f0b
    gh label create in-progress --color fbca04
    gh label create design-question --color 5319e7
    gh label create blocked --color b60205

    # 4. Protect main — the real safety mechanism
    gh api -X PUT repos/:owner/:repo/branches/main/protection \
      -f "required_pull_request_reviews[required_approving_review_count]=1" \
      -f "required_status_checks[strict]=true" \
      -f "required_status_checks[contexts][]=Lint / Test / Smoke" \
      -f "required_status_checks[contexts][]=Guardrails" \
      -F "enforce_admins=false" -F "restrictions=null"

    # 5. Go
    ./scripts/run-builder.sh 1

---

## What I filled in from your code

- **Input surface**: numbered menus via `choice_prompt()`, free text
  for the name only. No verb parser. The Playtester's strategies are
  built around numbers, not verbs.
- **Title screen loops 3×** before the name prompt — the offset that
  makes sequences misalign and the character end up named `1`.
  Documented in `docs/input-surface.md` and the corpus README.
- **`FALLOUT_TEST_MODE=1` is mandatory** in every non-interactive run,
  or `slow_print` sleeps per character.
- **RNG is unseeded** — identical input gives different HP. Every
  agent is told not to assert exact HP/damage/XP, the issue template
  says so, and CI warns on it.
- **Twenty story flags** listed by name in `AGENTS.md` §2, with the
  warning that repurposing one silently breaks later branching.
- **`GameLogger` / `GameStateSnapshot`** treated as the verification
  substrate — extend, never replace.
- **Prose is human-only.** The strictest boundary in the kit, since
  the content *is* the game.
- **Non-commercial posture** in `SOUL.md` §7, with a CI check that
  blocks monetisation-adjacent text.

---

## Roadmap encoded in SOUL.md §8

    package split → seeded RNG → save/load, deeper combat, more endings

Planner will refuse to file the last three as `agent-ready` before
the first two land.

---

## Build order

1. **Builder**, against hand-written issues. Learn its failure modes
   first.
2. **Playtester**. Highest value — minimised reproducers become
   permanent tests, so its output compounds.
3. **Reviewer**, once you know what Builder gets wrong.
4. **Planner**, if writing issues becomes your bottleneck.
5. **Ideator**, only if you want it. Usually you don't.

---

## Two things to fix early

**`tests/scripts/golden-path.txt` is weak.** It reaches character
creation correctly (verified) but its choices lead to a death rather
than the ending. A survivable full-playthrough sequence is a good
first issue — until then `make smoke` passes on a run that dies.

**The package split is the first real epic.** One module per issue,
zero behaviour change per PR. `player.py`, `data.py`, `ui.py`,
`logging.py`, then scenes.

---

## Known-fragile

- **opencode's schema moves.** `tools` is deprecated in favour of
  `permission`; these files use `permission`, verified against the
  current docs. Re-check https://opencode.ai/docs/agents before
  trusting them.
- **`SOUL.md` is a convention, not a standard.** It works only because
  `AGENTS.md` and `opencode.json`'s `instructions` array point at it.
- **`bash` permissions are allowlists.** Agents will stall asking for
  commands I didn't anticipate. Intended failure direction, but expect
  tuning in week one.
- **The stdlib-import CI check** is a grep with an allowlist. It passes
  clean on your current file; extend the list as you legitimately add
  stdlib modules.
