#!/bin/bash
# TEST ONLY (tenth round, second try nf4..nf6 with scripts built on finaldoorP1; nf1..nf3 took no form; glue 75 / several doors: every crossing with a form adds a W_EX010 pair to the file pool, md6). Is that
# the game's own? nf1 run-x6: THE ONE-HERO CONTROL test-v31-e-nn-forms (no twin; player 1 alone in Final Form through the doors);
# nf2 run-x8: v137-forms, PLAYER 1 in Final Form (the game's own path), player 2 no form follows. filepool_probe.py; doorsP1f_p1/p2.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5300,5700,6300,6900,7300,7900,8300,8900,9300,9900,10500,11400"
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nf4 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsP1f_p1.txt" "$O/idle.txt" run-x6 31750 28069 &
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nf5 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsP1f_p1.txt" "$O/doorsP1f_p2.txt" run-x8 32150 28071 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh nf6 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsP1f_p1.txt" "$O/idle.txt" run-x9 32350 28072 &
wait
