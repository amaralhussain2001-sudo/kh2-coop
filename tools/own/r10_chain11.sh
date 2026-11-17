#!/bin/bash
# TEST ONLY (tenth round, glue 73 --itemtarget): THE TWIN IS DOWN, on the quiet Borough disc test-s1-hb9f.iso (no enemies, no
# save point: in Merlin's house the save point raised the twin at once). Kits as r10_chain10.sh: -oi1hkt5 (Items row, Potions,
# HP 10 at 4900, the twin falls at 5150).
#   km run-x5  v131 player 1 LAST row (the down twin)     kn run-x6  v131 player 1 FIRST row (himself)
#   ko run-x7  v130 player 1 "Sora" (control: lane N's rule gives the down twin the Potion)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; cd "$P" || exit 1
SN="4950,5000,5100,5220,5250,5280,5320,5400,5500,5590"
run() { PROBE="$P/tools/own/prize_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/$2" test-s1-hb9f.iso 5600 $SN "$3" "$4" $5 $6 $7; }
run km-v131 test-own-v131-oi1hkt5 "$O/useitem_last_p1.txt" "$O/idle.txt" run-x5 31550 28068 &
run kn-v131 test-own-v131-oi1hkt5 "$O/useitem4_p1.txt" "$O/idle.txt" run-x6 31750 28069 &
run ko-v130 test-own-v130-oi1hkt5 "$O/useitem4_p1.txt" "$O/idle.txt" run-x7 31950 28070 &
wait
