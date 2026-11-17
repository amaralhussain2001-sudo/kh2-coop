#!/bin/bash
# TEST ONLY (tenth round, glue 73 second form, candidate v134 = BUILD 22's files): the target choice again, all cases, one Potion per run.
#   pa run-x5  friends disc, player 2 FIRST row (player 1)     pb run-x6  friends disc, player 2 LAST row (himself)
#   pc run-x7  friends disc, player 1 FIRST row (himself)      pd run-x8  friends disc, player 1 LAST row (player 2)
#   pe run-x9  quiet Borough, twin down at 5150, player 1 LAST row (the twin)
#   pf run-x10 quiet Borough, twin down at 5150, player 1 FIRST row (himself -> by the new rule the down twin gets it)
#   then: pg run-x5 Merlin's house, hero down at 5150, player 2 FIRST row (player 1)
#         ph run-x6 Merlin's house, hero down at 5150, player 2 LAST row (himself -> by the new rule the down hero gets it)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; cd "$P" || exit 1
SN="4950,5000,5100,5220,5250,5280,5320,5400,5500,5590"
run() { PROBE="$P/tools/own/prize_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/$2" $3 5600 $SN "$4" "$5" $6 $7 $8; }
run pa-v134 test-own-v134-oi1h test-g-friends.iso "$S/newgame_only.txt" "$O/useitem4_p2.txt" run-x2 30950 28065 &
run pb-v134 test-own-v134-oi1h test-g-friends.iso "$S/newgame_only.txt" "$O/useitem_last_p2.txt" run-x3 31150 28066 &
run pc-v134 test-own-v134-oi1h test-g-friends.iso "$O/useitem4_p1.txt" "$O/idle.txt" run-x4 31350 28067 &
run pd-v134 test-own-v134-oi1h test-g-friends.iso "$O/useitem_last_p1.txt" "$O/idle.txt" run-x7 31950 28070 &
run pe-v134 test-own-v134-oi1hkt5 test-s1-hb9f.iso "$O/useitem_last_p1.txt" "$O/idle.txt" run-x8 32150 28071 &
run pf-v134 test-own-v134-oi1hkt5 test-s1-hb9f.iso "$O/useitem4_p1.txt" "$O/idle.txt" run-x9 32350 28072 &
run pg-v134 test-own-v134-oi1hkh5 test-m-roam.iso "$S/newgame_only.txt" "$O/useitem4_p2.txt" run-x10 32550 28073 &
wait
run ph-v134 test-own-v134-oi1hkh5 test-m-roam.iso "$S/newgame_only.txt" "$O/useitem_last_p2.txt" run-x2 30950 28065 &
wait
