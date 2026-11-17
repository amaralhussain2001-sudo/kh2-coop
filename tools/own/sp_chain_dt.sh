#!/bin/bash
# TEST ONLY (2026-11-13): the white soft lock after Twin Howl in Dark Thorn's fight (BB05_MS104B, map 79 / battle 81),
# three controls after sp_chain_j.sh: 12,000 frames, both players mashrc_long, the same jump as the long run.
#   L1 build 12 candidate WITHOUT the HP kit     L2 NO patch (one hero), player 1 mashrc_long_p1     L3 the long run's patch again
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "jump-map controls done" local/sweep/b13c/hy-done.txt 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 15" > /dev/null; done
SN=5000,5200,5400,5700,6000,6500,7000,8000,9000,10500,11900
SNAPS=$SN FRAMES=12000 TOUT=420 SWEEP_PROBE_WAIT=420 LOGDIR=local/sweep/b13c TAG=dtL1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep3.sh dtL1 run-m 29050 28081 test-own-v33-snapB local/sweep/list-dt.txt &
SNAPS=$SN FRAMES=12000 TOUT=420 SWEEP_PROBE_WAIT=420 LOGDIR=local/sweep/b13c TAG=dtL2 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep3.sh dtL2 run-v3 30150 28061 test-empty local/sweep/list-dt.txt &
SNAPS=$SN FRAMES=12000 TOUT=420 SWEEP_PROBE_WAIT=420 LOGDIR=local/sweep/b13c TAG=dtL3 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep3.sh dtL3 run-v3b 30350 28062 test-own-v33-snapB-god local/sweep/list-dt.txt &
wait
echo "dark thorn controls done $(date +%H:%M:%S)" >> local/sweep/b13c/hy-done.txt
