#!/bin/bash
# TEST ONLY (tenth round, build 23 candidate v137 = build 22 + glue 66's shots' table moved to 0x000DF000,
# tools/merge/edit_merge_v7_gqtable.py): Gummi route 0 (kit -gum0), 14,000 frames, probe gqtab_probe.py (score split, the
# table's bytes, the memory below it, glues 72 .. 75's code words), scripts of r10_chain26.sh.
#   v137: q1 only player 1 fires / q2 only player 2 / q3 both      v134 (build 22) controls: q4 / q5 / q6 (the same three)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; T="$P/tools/own"; S3="$P/tests/scripts/lane-s3"; cd "$P" || exit 1
SN="5000,6000,7000,8000,9000,10000,11000,12000,13000,13900"
one() { PROBE="$T/gqtab_probe.py" SWEEP_PROBE_WAIT=1200 bash "$T/dusk_one.sh" "r10$1" "patches/$2" test-s1-tt137.iso 14000 "$SN" "$S3/$3" "$S3/$4" $5 $6 $7 2>&1 | head -n 1; }
F1="gb_p1_fight.txt gb_p2_idle.txt"; F2="gb_p1_idle.txt gb_p2_fight.txt"; F3="gb_p1_fight.txt gb_p2_fight.txt"
one q1 test-own-v137-gum0 $F1 run-m 29050 28081 &
one q2 test-own-v137-gum0 $F2 run-v3 30150 28061 &
one q3 test-own-v137-gum0 $F3 run-v3b 30350 28062 &
one q4 test-own-v134-gum0 $F1 run-v3c 30550 28063 &
one q5 test-own-v134-gum0 $F2 run-x1 30750 28064 &
one q6 test-own-v134-gum0 $F3 run-x2 30950 28065 &
wait
