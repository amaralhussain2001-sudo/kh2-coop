#!/bin/bash
# TEST ONLY (tenth round, glue 73 --itemtarget): THE PARTNER IS DOWN. As r10_chain7.sh (test-m-fight.iso, kit -oi1h: Items row,
# Potions, both heroes' HP 10 at 4900) + a fall at 4960 (make_killkit.py: -oi1hkt the twin, -oi1hkh player 1's hero).
#   ka run-x5  v131 twin down, player 1 LAST row (the twin)      kb run-x6  v131 twin down, player 1 FIRST row (himself)
#   kc run-x7  v130 twin down, player 1 "Sora" (control, lane N's rule: the down twin gets it)
#   kd run-x8  v131 hero down, player 2 FIRST row (player 1's hero)   ke run-x9 v131 hero down, player 2 LAST row (himself)
#   kf run-x10 v130 hero down, player 2 "Sora" (control)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; cd "$P" || exit 1
SN="4950,5000,5100,5220,5250,5280,5320,5400,5500,5590"
run() { PROBE="$P/tools/own/prize_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/$2" test-m-fight.iso 5600 $SN "$3" "$4" $5 $6 $7; }
run ka2-v131 test-own-v131-oi1hkt "$O/useitem_last_p1.txt" "$O/idle.txt" run-x5 31550 28068 &
run kb2-v131 test-own-v131-oi1hkt "$O/useitem4_p1.txt" "$O/idle.txt" run-x6 31750 28069 &
run kc2-v130 test-own-v130-oi1hkt "$O/useitem4_p1.txt" "$O/idle.txt" run-x7 31950 28070 &
run kd2-v131 test-own-v131-oi1hkh "$S/newgame_only.txt" "$O/useitem4_p2.txt" run-x8 32150 28071 &
run ke2-v131 test-own-v131-oi1hkh "$S/newgame_only.txt" "$O/useitem_last_p2.txt" run-x9 32350 28072 &
run kf2-v130 test-own-v130-oi1hkh "$S/newgame_only.txt" "$O/useitem4_p2.txt" run-x10 32550 28073 &
wait
