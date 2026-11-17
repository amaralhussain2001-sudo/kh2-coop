#!/bin/bash
# TEST ONLY (tenth round, glue 77 --gummiall, candidate v135): THE GUMMI POINTS OF A NON-CANNON WEAPON. Route 0 (kit -gum0), the player
# ships' cannon blocks built as kind 499 (= weapon type 73, generic class; tools/own/make_gumweapon.py, kit -gum0-w499), 14,000 frames,
# probe gscore_probe.py (both scores). As r9_chain34.sh: gw1 only player 1 fires, gw2 only player 2, gw3 both; gc2 = v134 (no glue 77)
# with the same kit, only player 2 fires (control: his points go to player 1 there); gk2 = v135 with the cannons (plain -gum0), only
# player 2 fires (glue 66's cannon path unchanged). Lanes run-x6 .. run-x10.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; T="$P/tools/own"; S3="$P/tests/scripts/lane-s3"; cd "$P" || exit 1
SN="5000,6000,7000,8000,9000,10000,11000,12000,13000,13900"
one() { PROBE="$T/gscore_probe.py" SWEEP_PROBE_WAIT=1200 bash "$T/dusk_one.sh" "r10$1" "patches/$2" test-s1-tt137.iso 14000 "$SN" "$S3/$3" "$S3/$4" $5 $6 $7 2>&1 | head -n 1; }
one gw1 test-own-v135-gum0-w499 gb_p1_fight.txt gb_p2_idle.txt run-x6 31750 28069 &
one gw2 test-own-v135-gum0-w499 gb_p1_idle.txt gb_p2_fight.txt run-x7 31950 28070 &
one gw3 test-own-v135-gum0-w499 gb_p1_fight.txt gb_p2_fight.txt run-x8 32150 28071 &
one gc2 test-own-v134-gum0-w499 gb_p1_idle.txt gb_p2_fight.txt run-x9 32350 28072 &
one gk2 test-own-v135-gum0 gb_p1_idle.txt gb_p2_fight.txt run-x10 32550 28073 &
wait
