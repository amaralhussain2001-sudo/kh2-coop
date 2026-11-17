#!/bin/bash
# (try d = r10_chain46.sh with doorsNNd_p1: a LEFT push into the door at 6000; nc1 / nc2 stood inside the volume and the door did not fire)
# TEST ONLY (tenth round, the one-hero control, try c: doorsNNd_p1 = the walk of try b + up 25 at 5800 into the door's jump volume,
# Final Form in the Borough at 6500, four doors). nc1 run-x6 test-v31-e-nn-forms filepool_probe.py   nc2 run-x8 the same, sp_probe.py
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5900,6300,7100,7700,8700,9700,10700,11400"
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nd1 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsNNd_p1.txt" "$O/idle.txt" run-x6 31750 28069 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh nd2 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doorsNNd_p1.txt" "$O/idle.txt" run-x8 32150 28071 &
wait
