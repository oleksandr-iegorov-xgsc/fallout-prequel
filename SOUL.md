# SOUL.md

**FALLOUT: THE LAST DAY BEFORE**
A text CLI RPG set in August 2077, in the two months before the Great
War.

This file is the game's identity: what it is, what it is for, what it
must never become. It answers *"should this exist?"*
`AGENTS.md` answers *"how do I build it here?"*

**HUMAN-OWNED.** No agent edits this file, in any branch, for any
reason. CI enforces it. When proposed work conflicts with anything
here, the correct action is to stop and escalate — not to implement a
compromise.

---

## 1. Premise

You are a Vault-Tec employee inside an unfinished vault in the summer
of 2077. You have roughly two months. You do not know that, but the
player does — the dread is the point.

Over eight scenes you learn what the vault is actually for, decide who
to trust, and choose what to do with the knowledge. Then the bombs
fall regardless. The game is about what you did with the time, not
whether you stopped anything.

A full run is one sitting. Multiple runs are the intended way to
experience it — different S.P.E.C.I.A.L. builds, different companions,
different endings.

---

## 2. Design pillars

1. **The ending is fixed; the meaning is not.**
   The Great War happens in every run. The player cannot prevent it.
   What varies is who they saved, what they learned, and who they
   became.
   *Rules out:* any "stop the war" path, any ending where 2077 does
   not end in fire, time travel, anything that makes the canon
   negotiable.

2. **One sitting, many runs.**
   A complete playthrough fits in roughly 30–45 minutes. Replay value
   comes from branching, not from length.
   *Rules out:* grinding, filler encounters, padding scenes to
   inflate runtime, anything that makes a second run feel like a
   chore.

3. **Choices are legible before they are made.**
   The player should be able to reason about a choice from the text
   in front of them. Consequences may surprise; the *inputs* to the
   decision may not be hidden.
   *Rules out:* gotcha deaths, invisible stat checks the text does
   not hint at, "correct" answers discoverable only by replaying.

4. **The wasteland is earned, not assumed.**
   Fallout's tone comes from specificity — a brand name, a
   bureaucratic memo, a cheerful voice describing something awful.
   *Rules out:* generic post-apocalyptic filler, lore dumps, winking
   at the audience, jokes that break the period fiction.

5. **The player is complicit.**
   Vault-Tec is doing something monstrous and the player works there.
   Karma tracks what they did about it.
   *Rules out:* a clean hero path, moral choices with no cost, an
   ending where the player is uncomplicatedly good.

---

## 3. Player experience targets

- Session length: 30–45 minutes for a full run
- Tone: retrofuturist dread. Cheerful institutional language
  describing atrocity. 1950s optimism rotting from inside.
- Voice: second person, present tense.
- The player should feel: *complicit, informed, and out of time.*
- The player should never feel: *tricked, or that a replay is
  mandatory homework to find the "real" ending.*
- Failure means a different ending, not a wasted run. Death is a
  legitimate outcome with its own weight.
- The last scene should land even on a first run with poor choices.

---

## 4. Non-goals

A proposal moving toward any of these is rejected regardless of
implementation quality or how common the feature is in the genre.

- **Not commercial.** See §7. Never monetised, never sold, never
  distributed as a product.
- **Not an open world.** The scene sequence is linear; branching
  happens *within* and *between* scenes, not on a map.
- **Not a survival sim.** No hunger, thirst, radiation ticking,
  encumbrance, or crafting.
- **Not multiplayer, networked, or account-based.** No telemetry
  leaving the machine. Ever.
- **Not real-time.** The game waits for the player indefinitely.
- **Not a platform.** No plugin system, no modding API, no player-
  facing scripting language.
- **Not a parser adventure.** Input is numbered menu selection. There
  is no verb parser and there will not be one — see §6.
- **No procedural generation.** Scenes are authored. Every line of
  content is written by a human.
- **No post-War content.** The game ends when the bombs fall. Whatever
  happens after is another game.

---

## 5. Content standards

- **Register:** period-authentic. 2077 as imagined by 1955. Vault-Tec
  corporate cheerfulness, military abbreviation, consumer optimism.
- **Named entities:** Vault-Tec, RobCo, Steel Dawn, S.P.E.C.I.A.L.,
  caps, Fat Man, super mutants. Use the established vocabulary
  precisely — half-remembered lore reads as carelessness.
- **Existing cast:** Sammy Alvarez (tech), Tinker Tom (science),
  Deputy Cooper (combat), Dr. Emil Ingram (antagonist). New named
  characters require a human decision.
- **Timeline:** August 2077. The Great War is 23 October 2077.
  Nothing may contradict this.
- **Violence:** present and consequential, never gratuitous. The
  horror is institutional, not visceral.
- **Length:** scene prose in short paragraphs. Menu options one line.
  Respect the 60-column header convention already in the code.
- **Accessibility:** ANSI colour is decoration only. Meaning must
  survive a terminal with no colour support. Never encode information
  in colour alone.

---

## 6. Technical identity

Design decisions, not implementation details. Changing these is a
design change requiring a human.

- **Pure text I/O.** No curses, no TUI framework, no mouse, no
  graphics.
- **Input is numbered menu selection**, plus free-text only for the
  character's name. This is the entire input surface and it is
  deliberate — it makes the game exhaustively testable.
- **Offline forever.** No network calls at runtime, for any reason.
- **Standard library only at runtime.** Test and tooling dependencies
  are fine.
- **Seeded RNG.** Every run must be reproducible from
  `(seed, input sequence)`. This is infrastructure for testing and
  for save/load, not a gameplay feature — the player need never see a
  seed. *Current state: `random` is unseeded and identical input
  produces different outcomes. This is a known defect, not a design
  choice.*
- **Crash diagnostics are a feature.** `GameLogger` and
  `GameStateSnapshot` exist so failures are debuggable. Keep them
  working; extend rather than replace.

---

## 7. Legal position

This is a **personal, non-commercial fan project**. Fallout,
Vault-Tec, S.P.E.C.I.A.L., and associated marks are the property of
Bethesda Softworks / ZeniMax Media. This project claims no
affiliation and no ownership of the setting.

Binding constraints:

- Never monetised. No sales, donations, sponsorship, ads, or
  crowdfunding.
- No assets copied from any Fallout title — no ripped text, art,
  audio, or data files. All content in this repository is originally
  written.
- Distribution stays personal. Publishing beyond that is a human
  decision, never an agent's.
- No claim of official status anywhere in the game, repo, or docs.

An agent must never take an action that changes this posture.

---

## 8. Roadmap

Accepted directions. Everything here still requires issues with
mechanical acceptance criteria before an agent touches it.

**Accepted:**

- **Package split.** `fallout_prequel.py` becomes a `src/game/`
  package. Pure refactor — zero behaviour change. This is the
  prerequisite for everything else.
- **Seeded RNG.** Reproducibility from `(seed, inputs)`. Prerequisite
  for save/load and for meaningful automated playtesting.
- **Save/load between sessions.** Persist and restore mid-run.
  Requires seeded RNG first, and a versioned format from day one.
- **More branching endings** beyond the current set, driven by the
  existing flags and karma.
- **Deeper combat.** More tactical texture than attack/dodge/damage —
  without violating pillar 2 (no grinding) or pillar 3 (no hidden
  state).

**Ordering:** package split → seeded RNG → everything else. The last
three are not startable until the first two land.

---

## 9. Open design questions

Unresolved. Agents must **not** resolve these. If work depends on one,
stop and ask.

- [ ] What does "deeper combat" mean concretely? More options per
      turn, positioning, targeted attacks, consumables? Undecided.
- [ ] Save/load granularity: checkpoint per scene, or save anywhere?
- [ ] Should death remain a full restart, or resume from the last
      scene boundary?
- [ ] How many endings is the right number? Current set may already
      be enough.
- [ ] Does level-up ever offer a choice, or stay automatic?

---

## 10. Authority

- `SOUL.md` and `AGENTS.md` are human-owned. No agent edits them.
- Design conflicts are resolved by the human, not by consensus
  between agents.
- Agents do not negotiate with each other. When two roles disagree,
  work stops and the human decides.
- "The tests pass" is not evidence that a change belongs in the game.
  This file is the test for belonging.
- If an agent is uncertain whether something conflicts with this
  file, **that uncertainty is the answer**: escalate.
