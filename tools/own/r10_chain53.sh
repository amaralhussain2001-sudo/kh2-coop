#!/bin/bash
# TEST ONLY (tenth round, the user's shop girl, take 4): the room data of Market Street holds the accessory shop girl at (-2891, -889)
# as N_EX690_TT_ACCE_RTN (0x0547) AND as a shop TUTORIAL copy N_EX690_TT_TUTOR_RTN (0x0849). After the friends' scene both heroes walk
# to her and talk. npc_probe.py near her (objects, flags +0C) and both pictures, before / during / after the talk.
#   sh1 x8 player 1 talks, walk 85    sh2 x9 player 1 talks, walk 100    sh3 x10 player 1 talks, walk 115    sh4 x7 player 2 talks, walk 100
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="9250,9440,9600,10000,10500,11000,11500,12000,12600,13300,13900"
export NPC_AT="-2891,-889" NPC_RADIUS=1200
g() { PROBE="$P/tools/own/npc_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/test-package-v3" kh2-coop-v5.iso 14000 "$SN" "$O/$2" "$O/$3" $4 $5 $6; }
g sh1 shopT85_p1.txt shopW85_p2.txt run-x8 32150 28071 &
g sh2 shopT100_p1.txt shopW100_p2.txt run-x9 32350 28072 &
g sh3 shopT115_p1.txt shopW115_p2.txt run-x10 32550 28073 &
g sh4 shopW100_p1.txt shopT100_p2.txt run-x7 31950 28070 &
wait
