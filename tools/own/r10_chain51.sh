#!/bin/bash
# TEST ONLY (tenth round, the user's shop girl, take 3): the talk with the three friends at the clothes shop (N_EX500 / 510 / 520) waits
# for both heroes ("Waiting for the other player.", gt1..gt3). Both walk up; ts1 x9: player 1 talks; ts2 x10: player 2 talks.
# npc_probe.py around them; both pictures through the talk and after it.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="6560,7000,8000,9000,10000,11000,11700,12200,12800,13400"
export NPC_AT="-1200,-2900" NPC_RADIUS=1500
g() { PROBE="$P/tools/own/npc_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/test-package-v3" kh2-coop-v5.iso 13500 "$SN" "$O/$2" "$O/$3" $4 $5 $6; }
g ts1 friendsT_p1.txt friendsW_p2.txt run-x9 32350 28072 &
g ts2 friendsW_p1.txt friendsT_p2.txt run-x10 32550 28073 &
wait
