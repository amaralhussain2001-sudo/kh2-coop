#!/bin/bash
# TEST ONLY (tenth round, the W_EX010 pair added at each door during a form): rv1 run-x6 / rv2 run-x8: v137-forms, player 2 in Final
# Form through five doors, REVERT at 9800, two more doors (doorsRv_p1/p2): are the pairs freed once the form is over? rv1
# filepool_probe.py, rv2 sp_probe.py (rooms, positions; the picture at 10000 shows the revert). ne5 run-x9 / ne6 run-x10: the one-hero
# control's aims doorsNN1 / doorsNN3 with sp_probe.py (where does the hero go?).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5700,7300,8700,9700,10000,10500,11000,11500,12000,12400"
SNN="4690,5000,5300,5400,5450,5500,5550,5600,5700,6000"
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh rv1 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 12500 "$SN" "$O/doorsRv_p1.txt" "$O/doorsRv_p2.txt" run-x6 31750 28069 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh rv2 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 12500 "$SN" "$O/doorsRv_p1.txt" "$O/doorsRv_p2.txt" run-x8 32150 28071 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh ne5 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 6100 "$SNN" "$O/doorsNN1_p1.txt" "$O/idle.txt" run-x9 32350 28072 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh ne6 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 6100 "$SNN" "$O/doorsNN3_p1.txt" "$O/idle.txt" run-x10 32550 28073 &
wait
