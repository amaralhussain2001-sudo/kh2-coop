#!/bin/bash
# TEST ONLY (tenth round, glue 77 second form --gummiall with the pointer check, candidate v136): THE GUMMI POINTS OF NON-CANNON
# WEAPONS, TWELVE LANES AT ONCE. Route 0 (kit -gum0), 14,000 frames, probe gscore_probe.py; scripts of r9_chain34.sh.
#   kits: -gum0-w499 (cannon blocks of the player ships built as kind 499 = type 73), -gum0-w505 (kind 505 = type 71), plain -gum0.
#   v136 w499: ha1 P1 fires / ha2 P2 / ha3 both     v136 w505: hb1 / hb2 / hb3     v136 cannons: hk1 / hk2 / hk3
#   v134 (no glue 77) controls: hc1 w499 P1 fires, hc3 w499 both (do the kit's weapons fault without glue 77?), hc5 w505 P2 fires
P="/c/Users/PC FORCE/Desktop/New folder (3)"; T="$P/tools/own"; S3="$P/tests/scripts/lane-s3"; cd "$P" || exit 1
SN="5000,6000,7000,8000,9000,10000,11000,12000,13000,13900"
one() { PROBE="$T/gscore_probe.py" SWEEP_PROBE_WAIT=1200 bash "$T/dusk_one.sh" "r10$1" "patches/$2" test-s1-tt137.iso 14000 "$SN" "$S3/$3" "$S3/$4" $5 $6 $7 2>&1 | head -n 1; }
F1="gb_p1_fight.txt gb_p2_idle.txt"; F2="gb_p1_idle.txt gb_p2_fight.txt"; F3="gb_p1_fight.txt gb_p2_fight.txt"
one ha1 test-own-v136-gum0-w499 $F1 run-m 29050 28081 &
one ha2 test-own-v136-gum0-w499 $F2 run-v3 30150 28061 &
one ha3 test-own-v136-gum0-w499 $F3 run-v3b 30350 28062 &
one hb1 test-own-v136-gum0-w505 $F1 run-v3c 30550 28063 &
one hb2 test-own-v136-gum0-w505 $F2 run-x1 30750 28064 &
one hb3 test-own-v136-gum0-w505 $F3 run-x2 30950 28065 &
one hk1 test-own-v136-gum0 $F1 run-x3 31150 28066 &
one hk2 test-own-v136-gum0 $F2 run-x4 31350 28067 &
one hk3 test-own-v136-gum0 $F3 run-x5 31550 28068 &
one hc1 test-own-v134-gum0-w499 $F1 run-x6 31750 28069 &
one hc3 test-own-v134-gum0-w499 $F3 run-x7 31950 28070 &
one hc5 test-own-v134-gum0-w505 $F2 run-x8 32150 28071 &
wait
