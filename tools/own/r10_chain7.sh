#!/bin/bash
# TEST ONLY (tenth round, glue 73 --itemtarget, candidate v131): THE TARGET CHOICE FOR A POTION. Disc test-g-friends.iso (Donald
# and Goofy are there), kit -oi1h: the command menu's Items row, Potions in both players' places, both heroes' HP 10 at 4900 (5 ended the mission: its story scene comes at 30 % HP).
# One Potion each run, at 5000 .. 5300. Probe prize_probe.py (both heroes' HP). Pictures of the PARTY window.
#   ia run-x5  v131 player 2, FIRST row (player 1's hero)     ib run-x6  v131 player 2, LAST row (himself)
#   ic run-x7  v131 player 1, FIRST row (himself)             id run-x8  v131 player 1, LAST row (player 2's hero)
#   ie run-x9  v130 player 2, first row (control: lane N's rule)   if run-x10 v130 player 1, down three rows (control)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; cd "$P" || exit 1
SN="4950,5100,5180,5220,5250,5280,5320,5400,5500,5590"
run() { PROBE="$P/tools/own/prize_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/$2" test-g-friends.iso 5600 $SN "$3" "$4" $5 $6 $7; }
run ia2-v131 test-own-v131-oi1h "$S/newgame_only.txt" "$O/useitem4_p2.txt" run-x5 31550 28068 &
run ib2-v131 test-own-v131-oi1h "$S/newgame_only.txt" "$O/useitem_last_p2.txt" run-x6 31750 28069 &
run ic2-v131 test-own-v131-oi1h "$O/useitem4_p1.txt" "$O/idle.txt" run-x7 31950 28070 &
run id2-v131 test-own-v131-oi1h "$O/useitem_last_p1.txt" "$O/idle.txt" run-x8 32150 28071 &
run ie2-v130 test-own-v130-oi1h "$S/newgame_only.txt" "$O/useitem4_p2.txt" run-x9 32350 28072 &
run if2-v130 test-own-v130-oi1h "$O/useitem_last_p1.txt" "$O/idle.txt" run-x10 32550 28073 &
wait
