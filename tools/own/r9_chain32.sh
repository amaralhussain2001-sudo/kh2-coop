#!/bin/bash
# TEST ONLY (ninth round, job 3): WHICH CALLS FREE A HERO WHOM NO SCRIPT ENDS: the Dark Thorn (bb05 78) on v106: the mirror hero (player
# 1's) is left in FC from 8150 (run h6). At frame 9000 one "let him go" in six ways (tools/own/make_release_test.py, kits -rel1 .. -rel6).
# Six lanes, 10,200 frames each, probe cap_log_probe2.py (action, held bit, hook). Logs local/sweep/r9/rl1.log .. rl6.log; chain32.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain32.txt"; }
say "chain32 start"
one() {  # one <variant> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=10100 SNAPS="5200,8000,8900,9100,9500,10100" FRAMES=10200 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9rl$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh rl$1 $2 $3 $4 test-own-v106-snapB-god-rel$1 "$B/list-bb05.txt"
  say "rl$1 done"
}
one 12 run-m 29050 28081 &
one 13 run-v3 30150 28061 &
one 14 run-v3b 30350 28062 &
wait
say "chain32 through"
