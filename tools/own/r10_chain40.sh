#!/bin/bash
# TEST ONLY (tenth round, glue 75, SEVERAL DOORS IN A ROW; second try md5..md7 with doors6 = down at each door, md2..md4 doors5 made two crossings): kit v137-forms, disc test-s1-hb13s, doors5_p1/p2 (player 2 in Final
# Form through the west door to the Borough hb09, then back, west again, back: four crossings). The door back is hb09's place-13
# volume at (1370, -275, -520). Three probes, the same scripts:  md2 run-x6 sp_probe.py (rooms, positions)  md3 run-x8
# filepool_probe.py (the form's files, the pool)  md4 run-x9 bind_probe.py (player 2's second Keyblade bound by number).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5300,5590,6000,6300,6700,7300,7700,8300,8700,9300,9700,10300,10900"
fr() { PROBE="$P/tools/own/$5" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh $1 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 11000 "$SN" "$O/doors6_p1.txt" "$O/doors6_p2.txt" $2 $3 $4; }
fr md5 run-x6 31750 28069 sp_probe.py &
fr md6 run-x8 32150 28071 filepool_probe.py &
fr md7 run-x9 32350 28072 bind_probe.py &
wait
