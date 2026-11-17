#!/bin/bash
# TEST ONLY (tenth round, glue 73): AN ETHER ON THE PARTNER. Quiet Borough disc test-s1-hb9f.iso, kit -eth2 on v132: the Items row,
# Ethers (item 3) in both players' places and stocks at 4300, both heroes' MP 10 at 4900 (slots 0x01C6C4E8 / 0x01C6C750 + 0x180).
#   ea run-x5  player 1, LAST row (player 2)      eb run-x6  player 2, FIRST row (player 1)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; cd "$P" || exit 1
SN="4950,5000,5100,5220,5250,5280,5320,5400,5500,5590"
run() { PROBE="$P/tools/own/prize_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/$2" test-s1-hb9f.iso 5600 $SN "$3" "$4" $5 $6 $7; }
run ea-v132 test-own-v132-eth2 "$O/useitem_last_p1.txt" "$O/idle.txt" run-x5 31550 28068 &
run eb-v132 test-own-v132-eth2 "$S/newgame_only.txt" "$O/useitem4_p2.txt" run-x6 31750 28069 &
wait
