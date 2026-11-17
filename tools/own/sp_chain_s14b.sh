#!/bin/bash
# TEST ONLY (2026-11-13): second pass of sp_chain_s14.sh. Player 2 picks the SECOND row of the Limit list (pass 1 got
# Goofy's Whirli-Goof first in 6 of 8 guest rooms), and a Limit try in a room with no helper (hb17 66, the 1000
# Heartless, NO_FRIEND). Logs in local/sweep/b14/.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
L=local/sweep; B=local/sweep/b14
SL="5200,5500,5800,6200,6800,7100,7900,8300,8900"
run() { SNAPS=$SL LOGDIR=$B TAG=$1 P2S="$O/$2" bash tools/own/sweep3.sh "$3" "$4" "$5" "$6" test-own-v33-limit "$L/$7"; }
run s14m lim_jump2_p2.txt l2a run-m 29050 28081 list-l2a.txt &
run s14m lim_jump2_p2.txt l2b run-v3 30150 28061 list-l2b.txt &
run s14m lim_jump2_p2.txt l2c run-v3b 30350 28062 list-l2c.txt &
( run s14m lim_jump2_p2.txt l2d run-v3c 30550 28063 list-l2d.txt; run s14o lim_jump_p2.txt l2n run-v3c 30550 28063 list-l2n.txt ) &
wait
echo "tests s14b done $(date +%H:%M:%S)" >> "$B/s14-done.txt"
