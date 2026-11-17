#!/bin/bash
# TEST ONLY: the special scenes of this session on one patch folder (sandbox run-v3b), compact results.
# usage: near_batch.sh <ownPatchDirName> <prefix>     -> log local/<prefix>-batch.log
P="/c/Users/PC FORCE/Desktop/New folder (3)"
L="$P/tests/scripts/lane-s1"; O="$P/tests/scripts/own"
PD="$P/patches/$1"; X=$2
LOG="$P/local/$X-batch.log"; : > "$LOG"
one() {  # name probe iso frames snaps p1 p2 grepPattern
  PROBE="$P/tools/own/$2" bash "$P/tools/own/dusk_one.sh" "$X-$1" "$PD" "$3" "$4" "$5" "$6" "$7" run-v3b 30350 28062 2>&1 | head -1 | cut -c1-112 >> "$LOG"
  grep -E "$8" "$P/local/tests/$X-$1-probe.txt" | cut -c1-120 >> "$LOG"
}
one bag-p1   party_probe.py test-s1-tt125.iso 9000 "7000,8000,8900" "$L/s1-c-bag-p1_p1.txt" "$L/s1-c-bag-p1_p2.txt" "^frame"
one bag-p2   party_probe.py test-s1-tt125.iso 9000 "7000,8000,8900" "$L/s1-c-bag-p2_p1.txt" "$L/s1-c-bag-p2_p2.txt" "^frame"
one thorn-p2 room_probe.py  test-s1-tt157.iso 12000 "6000,8000,10000,11900" "$L/s1-g-thorn-p2_p1.txt" "$L/s1-g-thorn-p2_p2.txt" "^frame"
one grand    near_probe.py  test-s1-tt90g.iso 5650 "5300,5600" "$L/s1-job-grand-near_p1.txt" "$L/s1-job-grand-near_p2.txt" "class 00350910"
one dusk     room_probe.py  test-s1-tt127.iso 9000 "8000,8900" "$L/s1-f-dusk-old1_p1.txt" "$L/s1-f-dusk-old1_p2.txt" "^frame"
one mail     menu_probe.py  test-v3-tt91.iso 5700 "5000,5600" "$O/rules_p1.txt" "$O/mailride_p2.txt" "S |S2"
one morale   party_probe.py test-s1-mu68.iso 9000 "5500,7000,8900" "$O/rules_p1.txt" "$O/lockmash_p2.txt" "^frame"
echo "batch done" >> "$LOG"
