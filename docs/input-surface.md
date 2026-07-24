# Input surface

**Maintained by the Playtester. Regenerate when the game source is
newer than this file.**

## Prompt types

1. `choice_prompt(prompts)` — prints `1..N`, loops until a valid
   integer in range. The main input.
2. Free text — character name only.
3. `pause()` — bare Enter.
4. `y`/`n` — death-retry prompt in `main()`.

No verb parser. A "command" is a number.

## Verified opening offsets

- `title_screen()` loops **3 times** — three bare Enters
- name (free text)
- 3 stat-increase selections
- 1 trait selection
- 1 starting-weapon selection
- then alternating `pause()` Enters and menu numbers per scene

## Scene sequence

    scene_wake_up → scene_concourse → scene_encounter → scene_surface
    → scene_sector_d → scene_ingram → scene_night → scene_the_war
    → scene_final_choice → ending()

Fixed order. Branching is inside scenes via `player.flags`.

---

_(per-scene prompt counts — populate on first Playtester run)_
