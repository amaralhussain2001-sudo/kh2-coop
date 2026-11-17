#!/bin/bash
# TEST ONLY (tenth round, the one-hero control, try b: the form taken in the Borough after a door walked without one; nf4 / ne1..ne6
# glided along the west door's wall in Final Form and the door did not fire). doorsNNb_p1 (+ doorsNNb_p2 for the co-op run).
#   nb1 run-x6 test-v31-e-nn-forms filepool_probe.py    nb2 run-x8 the same, sp_probe.py    nb3 run-x9 v137-forms (co-op, player 1 in
#   Final Form the same way, player 2 follows) filepool_probe.py
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5300,5700,6150,6600,7300,8300,9300,10300,11000,11400"
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nb1 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsNNb_p1.txt" "$O/idle.txt" run-x6 31750 28069 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh nb2 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsNNb_p1.txt" "$O/idle.txt" run-x8 32150 28071 &
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nb3 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsNNb_p1.txt" "$O/doorsNNb_p2.txt" run-x9 32350 28072 &
wait
