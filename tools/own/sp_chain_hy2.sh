#!/bin/bash
# TEST ONLY (2026-11-13): second Hydra / Pete controls on the three idle sandboxes.
#   D Timeless River, last Pete fight: NO patch, player 1 = mashrc_long_p1 (Triangle from 4540)
#   E the Hydra on the build 12 candidate, both players mashrc_late (Triangle only from 6500), 12,000 frames
#   F Pete on the build 12 candidate, both players mashrc_late, 12,000 frames
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
SN=5200,6000,6600,7400,8200,9000,10000,11900
SNAPS=$SN FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b13c TAG=ptD P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep3.sh ptD run-m 29050 28081 test-empty local/sweep/list-pt.txt &
SNAPS=$SN FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b13c TAG=hyE P1S="$O/mashrc_late_p1.txt" P2S="$O/mashrc_late_p2.txt" bash tools/own/sweep3.sh hyE run-v3 30150 28061 test-own-v33-snapB local/sweep/list-hy.txt &
SNAPS=$SN FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b13c TAG=ptF P1S="$O/mashrc_late_p1.txt" P2S="$O/mashrc_late_p2.txt" bash tools/own/sweep3.sh ptF run-v3b 30350 28062 test-own-v33-snapB local/sweep/list-pt.txt &
wait
echo "hydra / pete controls 2 done $(date +%H:%M:%S)" >> local/sweep/b13c/hy-done.txt
