#!/bin/bash
# TEST ONLY (2026-11-13): the crash of HE08_MS107 (Pete with Hercules) in the long HP-held run, three controls at once.
#   G NO patch, player 1 = mashrc_long_p1                     (does the original game crash with these buttons?)
#   H build 12 candidate WITHOUT the HP kit, both mashrc_long (is the HP kit needed for the crash?)
#   I build 12 candidate WITH the HP kit, the sweep's buttons (are the buttons needed?)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
SN=5200,6000,7000,8900
SNAPS=$SN TOUT=300 LOGDIR=local/sweep/b13c TAG=pwG P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep3.sh pwG run-m 29050 28081 test-empty local/sweep/list-pw.txt &
SNAPS=$SN TOUT=300 LOGDIR=local/sweep/b13c TAG=pwH P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep3.sh pwH run-v3 30150 28061 test-own-v33-snapB local/sweep/list-pw.txt &
SNAPS=$SN TOUT=300 LOGDIR=local/sweep/b13c TAG=pwI P1S="$O/sweep_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep3.sh pwI run-v3b 30350 28062 test-own-v33-snapB-god local/sweep/list-pw.txt &
wait
echo "pete-hercules controls done $(date +%H:%M:%S)" >> local/sweep/b13c/hy-done.txt
