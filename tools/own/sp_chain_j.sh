#!/bin/bash
# TEST ONLY (2026-11-13): the three fights that stopped (the Hydra, Timeless River's last Pete fight, Pete with
# Hercules) again, with the jump of the clean sweep runs (map = battle = event = the mission's program) instead of
# map program 0; build 12 candidate + HP kit, both players mashrc_long (Circle, Triangle, R1), 16,000 frames.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
while [ ! -f local/sweep/b13/t-done.txt ]; do powershell -NoProfile -Command "Start-Sleep -Seconds 15" > /dev/null; done   # after sp_chain_t.sh
SN=5200,6000,7000,8000,9000,10000,12000,14000,15900
for x in "1 run-m 29050 28081" "2 run-v3 30150 28061" "3 run-v3b 30350 28062"; do
  set -- $x
  SNAPS=$SN FRAMES=16000 TOUT=420 SWEEP_PROBE_WAIT=420 LOGDIR=local/sweep/b13c TAG=jm$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" \
    bash tools/own/sweep3.sh "jm$1" "$2" "$3" "$4" test-own-v33-snapB-god "local/sweep/list-j$1.txt" &
done
wait
echo "jump-map controls done $(date +%H:%M:%S)" >> local/sweep/b13c/hy-done.txt
