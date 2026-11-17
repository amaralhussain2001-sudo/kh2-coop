#!/bin/bash
# TEST ONLY (tenth round, ITEM 8, glue 78 --gummitag): RECONSTRUCTED RECORD. The fork's own chain was written as r10_chain54.sh and
# was overwritten at 15:16 by the item-7 chain of the same name (its runs had already started, so the results stand). This file
# repeats what the fork's notes (STATE part 134) name: route 0 (kits -gum0, -gum0-w499 = cannon blocks built as kind 499 = type 73,
# -gum0-w505 = kind 505 = type 71), 14,000 frames, probe gqtab_probe.py, scripts of r10_chain26.sh, lanes run-m .. run-x2, two batches of six.
#   v138 w499: ta1 P1 fires / ta2 P2 / ta3 both     v138 w505: tb1 / tb2 / tb3
#   v137 controls: td1 w499 P1 fires, td2 w505 P2 fires, td3 w505 both     v138 plain cannons: tc1 / tc2 / tc3
P="/c/Users/PC FORCE/Desktop/New folder (3)"; T="$P/tools/own"; S3="$P/tests/scripts/lane-s3"; cd "$P" || exit 1
SN="5000,6000,7000,8000,9000,10000,11000,12000,13000,13900"
one() { PROBE="$T/gqtab_probe.py" SWEEP_PROBE_WAIT=1200 bash "$T/dusk_one.sh" "r10$1" "patches/$2" test-s1-tt137.iso 14000 "$SN" "$S3/$3" "$S3/$4" $5 $6 $7 2>&1 | head -n 1; }
F1="gb_p1_fight.txt gb_p2_idle.txt"; F2="gb_p1_idle.txt gb_p2_fight.txt"; F3="gb_p1_fight.txt gb_p2_fight.txt"
one ta1 test-own-v138-gum0-w499 $F1 run-m 29050 28081 &
one ta2 test-own-v138-gum0-w499 $F2 run-v3 30150 28061 &
one ta3 test-own-v138-gum0-w499 $F3 run-v3b 30350 28062 &
one tb1 test-own-v138-gum0-w505 $F1 run-v3c 30550 28063 &
one tb2 test-own-v138-gum0-w505 $F2 run-x1 30750 28064 &
one tb3 test-own-v138-gum0-w505 $F3 run-x2 30950 28065 &
wait
one td1 test-own-v137-gum0-w499 $F1 run-m 29050 28081 &
one td2 test-own-v137-gum0-w505 $F2 run-v3 30150 28061 &
one td3 test-own-v137-gum0-w505 $F3 run-v3b 30350 28062 &
one tc1 test-own-v138-gum0 $F1 run-v3c 30550 28063 &
one tc2 test-own-v138-gum0 $F2 run-x1 30750 28064 &
one tc3 test-own-v138-gum0 $F3 run-x2 30950 28065 &
wait
