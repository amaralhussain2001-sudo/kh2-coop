#!/bin/bash
# TEST ONLY (2026-11-13): controls for the Game Over that stopped s14o-HB17_MS405-66 (hb17 66, the 1000 Heartless,
# level 1 heroes both down at 5800, then no pictures, 50 fault lines; base test-own-v33-limit, NO Continue kit).
#   c1  base test-own-v33-snapB (the Continue kit of the jump starts), same buttons
#   c2  base test-own-v33 (the plain build, no kit), same buttons
#   c3  the game with NO patch (test-empty), one hero, controller 2 idle
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
L=local/sweep; B=local/sweep/b14; SL="5200,5500,5800,6200,6800,7100,7900,8300,8900"
SNAPS=$SL LOGDIR=$B TAG=s14c1 P2S="$O/lim_jump_p2.txt" bash tools/own/sweep3.sh c1 run-m 29050 28081 test-own-v33-snapB "$L/list-l2n.txt" &
SNAPS=$SL LOGDIR=$B TAG=s14c2 P2S="$O/lim_jump_p2.txt" bash tools/own/sweep3.sh c2 run-v3 30150 28061 test-own-v33 "$L/list-l2n.txt" &
SNAPS=$SL LOGDIR=$B TAG=s14c3 P2S="$O/idle.txt" bash tools/own/sweep3.sh c3 run-v3b 30350 28062 test-empty "$L/list-l2n.txt" &
wait
echo "tests s14c done $(date +%H:%M:%S)" >> "$B/s14-done.txt"
