#!/bin/bash
# TEST ONLY (2026-11-13): the Hydra freeze, three controls at once on the three idle sandboxes (9,000 frames).
#   A no patch at all (one hero), player 1 = mashrc_long_p1 (Circle every 20, Triangle every 60)
#   B build 12 candidate, player 1 = mashrc_long_p1, player 2 idle
#   C build 12 candidate, player 1 = the sweep's script, player 2 = mashrc_long_p2
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="/c/Users/PC FORCE/Desktop/New folder (3)/tests/scripts/own"
cd "$P" || exit 1
SNAPS=5200,6000,7000,8900 LOGDIR=local/sweep/b13c TAG=hyA P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep3.sh hyA run-m 29050 28081 test-empty local/sweep/list-hy.txt &
SNAPS=5200,6000,7000,8900 LOGDIR=local/sweep/b13c TAG=hyB P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep3.sh hyB run-v3 30150 28061 test-own-v33-snapB local/sweep/list-hy.txt &
SNAPS=5200,6000,7000,8900 LOGDIR=local/sweep/b13c TAG=hyC P1S="$O/sweep_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep3.sh hyC run-v3b 30350 28062 test-own-v33-snapB local/sweep/list-hy.txt &
wait
echo "hydra controls done $(date +%H:%M:%S)" >> local/sweep/b13c/hy-done.txt
