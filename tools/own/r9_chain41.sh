#!/bin/bash
# TEST ONLY (ninth round, job 3): THE LAST XEMNAS (eh20 74) PUSHED INTO HIS LATER PARTS: at frame 6500 both Xemnas objects' HP (records
# 0x01C6C018, 0x01C6BDB0; 525 at the start) are written once (make_once.py): xeB = 150, xeC = 40, xeD = 1. v107 with the capture log,
# 20,000 frames, both players Circle / Triangle / R1. Lanes run-m, run-v3, run-v3b. Logs local/sweep/r9/xeB.log ..; progress chain41.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain41.txt"; }
say "chain41 start"
one() {  # one <name> <sandbox> <port> <pine> <own>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=19900 SNAPS="6400,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$B/list-eh20.txt"
  say "$1 done"
}
one xeB run-m 29050 28081 test-own-v107-snapB-god-cap-xe0096 &
one xeC run-v3 30150 28061 test-own-v107-snapB-god-cap-xe0028 &
one xeD run-v3b 30350 28062 test-own-v107-snapB-god-cap-xe0001 &
wait
say "chain41 through"
