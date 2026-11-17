#!/bin/bash
# TEST ONLY (tenth round, several doors: is the W_EX010 pair added at each door tied to a form, and does the one-hero game do it?)
#   nn1 run-x6: v137-forms, NO FORM, five doors (doors6_p1 + doors6nf_p2), filepool_probe.py
#   nn2 run-x8: THE ONE-HERO CONTROL test-v31-e-nn-forms-tpw (= -forms + make_teleport.py: player 1 (01AB0990) to (-640, -550), in
#               the west door's volume, at 5450), player 1 in Final Form (doorsP1f_p1), then the down pushes; filepool_probe.py
#   nn3 run-x9: the same as nn2 with sp_probe.py (rooms, positions)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5300,5700,6300,6900,7300,7900,8300,8900,9300,9900,10500,11400"
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nn1 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 11500 "$SN" "$O/doors6_p1.txt" "$O/doors6nf_p2.txt" run-x6 31750 28069 &
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh nn2 "$P/patches/test-v31-e-nn-forms-tpw" test-s1-hb13s.iso 11500 "$SN" "$O/doorsP1f_p1.txt" "$O/idle.txt" run-x8 32150 28071 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh nn3 "$P/patches/test-v31-e-nn-forms-tpw" test-s1-hb13s.iso 11500 "$SN" "$O/doorsP1f_p1.txt" "$O/idle.txt" run-x9 32350 28072 &
wait
