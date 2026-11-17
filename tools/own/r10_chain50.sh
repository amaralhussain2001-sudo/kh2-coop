#!/bin/bash
# TEST ONLY (tenth round, the user's shop girl, take 2): after New Game the room holds three people only (gl2: N_EX500_RTN (-1297, -2897),
# N_EX510_RTN (-981, -2716), N_EX520_RTN (-1273, -3085)). Walk up to them and talk; npc_probe.py around them (flags +0C each frame).
#   gt1 x8 player 1 up 185     gt2 x9 player 1 up 200     gt3 x10 player 2 up 200 (player 2 talks)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="6290,6495,6560,6700,7000,7500,8000,8500,9300"
export NPC_AT="-1200,-2900" NPC_RADIUS=900
g() { PROBE="$P/tools/own/npc_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/test-package-v3" kh2-coop-v5.iso 9400 "$SN" "$O/$2" "$O/$3" $4 $5 $6; }
g gt1 friends185_p1.txt idle.txt run-x8 32150 28071 &
g gt2 friends200_p1.txt idle.txt run-x9 32350 28072 &
g gt3 ng_stand_p1.txt friends200_p2.txt run-x10 32550 28073 &
wait
