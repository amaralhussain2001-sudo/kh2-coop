#!/bin/bash
# TEST ONLY (ninth round, job 3): DATA LUXORD's long FE of player 1's hero: since which build. eh14 101, HP held, mashrc_long, 12,000 frames,
# probe act_poll_probe.py, on build 14 (v58), v64, v74, v89. usage: r9_chain35.sh  (lanes run-x5, run-x6, run-v3c, run-x1)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain35.txt"; }
say "chain35 start"
one() {  # one <name> <sandbox> <port> <pine> <own>
  ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5200,8000,11000,11900" FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$B/list-eh14d.txt"
  say "$1 done"
}
one lxJ run-x5 31550 28068 test-own-v58-snapB-god &
one lxK run-x6 31750 28069 test-own-v64-snapB-god &
one lxL run-v3c 30550 28063 test-own-v74-snapB-god &
one lxM run-x1 30750 28064 test-own-v89-snapB-god &
wait
say "chain35 through"
