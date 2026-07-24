# AGENTS.md

Operational contract for every agent working in this repository.
Read completely before taking any action.

- **Whether something belongs in the game** → `SOUL.md`
- **How to build it here** → this file
- **Role-specific constraints** → `.opencode/agents/<role>.md`

Precedence on conflict: `SOUL.md` > `AGENTS.md` > role file > your own
judgement. Never the reverse.

---

## 1. Project

**FALLOUT: THE LAST DAY BEFORE** — a text CLI RPG in Python.
Personal non-commercial fan project (`SOUL.md` §7).

### Current state

The game is one module, `fallout_prequel.py`, roughly 1450 lines.
The package split to `src/game/` is accepted (`SOUL.md` §8) but not
done. Until it lands, work in the single file.

    fallout_prequel.py       the entire game (current)
    tests/                   pytest suites
    tests/scripts/           input sequences — regression corpus
    logs/playtest/           human playtest notes
    logs/playtest/generated/ agent sequences + transcripts
    docs/input-surface.md    cached input-surface model (generated)

### Target state (post-split)

    src/game/__init__.py
    src/game/__main__.py     entrypoint — ONLY place input() may appear
    src/game/player.py       Player, S.P.E.C.I.A.L., XP, combat maths
    src/game/data.py         WEAPONS, ARMORS, ENEMIES, COMPANIONS
    src/game/scenes/         one module per scene
    src/game/ui.py           C, cls, slow_print, header, choice_prompt
    src/game/logging.py      GameLogger, GameStateSnapshot

Runtime: Python 3.12, **standard library only** (`SOUL.md` §6).
Tooling: `uv`, `pytest`, `ruff`, `mypy`.

---

## 2. Architecture you must know

### Input surface

The entire input surface is:

1. **Numbered menu selection** via `choice_prompt(prompts)` — prints
   options `1..N`, loops until a valid integer in range.
2. **Free text** for the character's name only.
3. **Bare Enter** at `pause()`.
4. **`y`/`n`** at the death-retry prompt.

There is no verb parser and there will never be one (`SOUL.md` §6).
A "command" in this game is a number. Design tests accordingly.

### Scene flow

`main()` runs a fixed linear list:

    scene_wake_up → scene_concourse → scene_encounter → scene_surface
    → scene_sector_d → scene_ingram → scene_night → scene_the_war
    → scene_final_choice → ending()

A scene returning `"death"` triggers `death_screen()` and a retry
prompt. Branching happens *inside* scenes via `player.flags` and
karma — not by reordering this list.

### State

`Player` holds `spec` (S.P.E.C.I.A.L.), `hp`, `xp`, `level`, `karma`,
`caps`, `inventory`, `equipment`, `companion`, and `flags`.

Story flags currently in use:

    blackmailed, escape_plan, experiment_truth, freed_them, has_chip,
    has_codes, ingram, ingram_alliance, knows_truth, poison_water,
    purity_badge, purity_foreknowledge, ready_to_escape,
    reported_sector_d, sector_d, soldier_warning, stay_and_fight,
    suspicions, tom_joined, truth_broadcast

Adding a flag is cheap. Removing or repurposing one is a content
change that can silently break a later scene's branching — check
every scene before touching an existing flag.

### Test hooks that already exist

- **`FALLOUT_TEST_MODE=1`** — disables typewriter delays in
  `slow_print` and `vault_text`. **Always set this** in tests and
  scripted runs; without it a run takes minutes of real sleep.
- **`GameLogger`** — ring buffer of the last 200 events (scene,
  choice, karma, flag, combat, level).
- **`GameStateSnapshot`** — full player state plus event log,
  rendered as text. Dumped to stderr and to
  `~/.local/share/fallout_prequel/debug_*.log` on crash or death.

These are the verification substrate. Extend them; do not replace
them.

### Known defects

Documented so you do not "discover" them as new findings:

- **RNG is unseeded.** Identical input produces different outcomes.
  `SOUL.md` §6 requires seeded RNG; this is the gap. Until it is
  fixed, do not assert exact HP, damage, or XP in tests — assert
  invariants and ranges.
- **`main()` recurses on retry**, so repeated deaths grow the stack.
- **`dump_snapshot` prints its log-file line twice.**

---

## 3. Commands

The only sanctioned ways to verify anything.

    uv sync                  install dependencies
    make lint                ruff + mypy — must exit 0
    make test                pytest — must exit 0
    make smoke               every script in tests/scripts/ — exit 0
    make check               lint + test + smoke, in order

Run a scripted sequence by hand:

    FALLOUT_TEST_MODE=1 timeout 120 \
      python3 fallout_prequel.py < seq.txt > transcript.txt 2>&1
    echo "exit: $?"

Interactive play:

    python3 fallout_prequel.py        # HUMANS ONLY

If a command you need does not exist, say so and stop. Do not
improvise a substitute.

---

## 4. Verification rules

Absolute. These exist because an agent once "verified" a feature by
writing a Python script that reimplemented the game logic and testing
that instead.

1. **Never reimplement game logic to test it.** A test that does not
   import from the real module and exercise the real code path is not
   a test. Delete it.
2. **Never call `input()` outside the entrypoint.** Today that means
   `choice_prompt`, `pause`, `character_creation`, and the retry
   prompt in `main()`; after the split, only `src/game/__main__.py`
   and `ui.py`. CI greps for new occurrences. Tests drive the game
   through piped stdin.
3. **Always set `FALLOUT_TEST_MODE=1`** in any non-interactive run.
4. **Always wrap scripted runs in `timeout`.** A hang is a finding,
   not a reason to wait.
5. **Never claim something works without running a command from §3.**
   Quote the real exit status in the PR body.
6. **Never fabricate output.** If you did not run it, you did not run
   it.
7. **New behaviour requires a test.** Content and scene changes
   require a sequence under `tests/scripts/` that reaches the changed
   content.
8. **Do not assert exact combat numbers** while RNG is unseeded (§2).
   Assert invariants: HP never exceeds `max_hp`, karma moves in the
   right direction, the expected flag is set, the run terminates.
9. **If a change cannot be mechanically verified**, say so under
   `## Not verified` in the PR and stop. That is an acceptable
   outcome. Inventing evidence is not.

---

## 5. Git workflow

- Branch from `main`. Never commit to `main`. Never force-push, on
  any branch.
- Branch naming: `<type>/<issue>-<slug>`
  Types: `feat`, `fix`, `refactor`, `content`, `test`, `chore`, `ci`
  Example: `refactor/12-extract-player-module`
- Conventional Commits: `fix(combat): prevent negative damage`
- One issue → one branch → one PR. No "while I was in there".
- Rebase on `main` before opening the PR. Do not merge `main` in.

---

## 6. Issue lifecycle

All work originates from a GitHub Issue labelled `agent-ready`. An
agent never invents its own task.

1. `gh issue view <n>` — read the acceptance criteria in full.
2. If any criterion is ambiguous or not mechanically checkable:
   comment on the issue and **stop**. Do not guess. Do not pick the
   interpretation easiest to implement.
3. `gh issue edit <n> --add-label in-progress`
4. Branch, implement, verify.
5. `gh pr create --fill --base main` with `Closes #<n>` and the §8
   sections.
6. CI fails → fix, push, repeat. **Three failures on the same root
   cause** → stop, comment with what you tried and observed, wait.
7. Never merge. Never approve. `main` is protected.

---

## 7. Scope boundaries

**MAY do autonomously**, given an `agent-ready` issue:

- Bug fixes with a reproducing test
- Refactors with **zero** behaviour change (including the §8 package
  split, one module per issue)
- Test coverage and regression sequences
- Tooling, CI, developer scripts
- Documentation
- Typos and formatting in existing scene prose

**MUST NOT do without an explicit human decision:**

- **Writing or rewriting scene prose.** The content is the game
  (`SOUL.md` pillar 4). Fixing a typo is fine; authoring a paragraph
  is not.
- New scenes, endings, characters, companions, weapons, armour,
  enemies, or story flags
- Combat, karma, XP, or S.P.E.C.I.A.L. balance changes
- Anything a player would call "how the game feels"
- Save-format design or changes (once it exists)
- Deleting content
- Adding a runtime dependency (`SOUL.md` §6 forbids these)
- Anything touching the legal posture in `SOUL.md` §7 — licence
  files, distribution, publishing, README claims about the project's
  status
- Editing `SOUL.md`, `AGENTS.md`, or anything under `.opencode/`
- Editing `.github/workflows/` unless the issue is explicitly about
  CI
- Changing branch protection, tokens, or repo settings

"Compiles and tests pass" is not "the game is good." Everything
touching player experience is human-gated. That boundary is the point
of this section, not a formality.

---

## 8. Pull request format

    ## What
    One paragraph.

    ## Why
    Closes #<n>

    ## Verification
    - make lint: pass
    - make test: pass (N passed)
    - make smoke: pass
    - <any sequence run, with path and exit code>

    ## Not verified
    Anything not mechanically checked. "nothing" if fully covered.

    ## Risk
    What could this break that CI would not catch?

A PR without a truthful `## Verification` section is rejected on
sight.

---

## 9. Escalation

Stop and ask a human when:

- Acceptance criteria are ambiguous
- The work conflicts with `SOUL.md`
- The change would require writing scene prose
- The fix needs a file forbidden in §7
- CI fails three times on one root cause
- You find a second bug while fixing the first — file a new issue, do
  not fix it here
- You are uncertain whether something is in scope

Escalating costs a day. Guessing wrong costs a merged mistake nobody
reviewed properly. Prefer the day.
