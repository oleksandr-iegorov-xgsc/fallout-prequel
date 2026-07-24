---
name: Bug
about: A crash, hang, or incorrect behaviour
title: ''
labels: bug
---

## Reproducer
<!-- Input sequence, one line per input. Numbered menu selections. -->

```
```

Run with:

    FALLOUT_TEST_MODE=1 timeout 120 python3 fallout_prequel.py < seq.txt

## Observed
<!-- Quote the transcript. Include the exit code.
     If it crashed, paste the GameStateSnapshot dump — it gives the
     scene, flags, and choice history. -->

Exit code: 

## Expected
<!-- Cite a source location or a SOUL.md section. -->

## Minimised
- [ ] Removing any line stops the reproduction
- [ ] Re-verified after minimising (sequences are positional —
      deleting a line shifts everything after it)

## Not one of the known defects
<!-- AGENTS.md §2 documents: unseeded RNG, main() recursion on retry,
     doubled log line in dump_snapshot. -->
- [ ] Confirmed this is distinct from those
