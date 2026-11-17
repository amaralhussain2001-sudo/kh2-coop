#!/bin/bash
# TEST ONLY (tenth round, the one-hero control, try c: doorsNNc_p1 = the walk of try b + up 25 at 5800 into the door's jump volume,
# Final Form in the Borough at 6500, four doors). nc1 run-x6 test-v31-e-nn-forms filepool_probe.py   nc2 run-x8 the same, sp_probe.py
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5700,6100,6900,7500,8500,9500,10500,11400"
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nc1 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsNNc_p1.txt" "$O/idle.txt" run-x6 31750 28069 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh nc2 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsNNc_p1.txt" "$O/idle.txt" run-x8 32150 28071 &
wait
