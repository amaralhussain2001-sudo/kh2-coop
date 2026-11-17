#!/bin/bash
# TEST ONLY (tenth round): the last Xemnas's laser dome (story fight eh20 74), the five cases of r9_chain63.sh on candidate
# v134 = BUILD 22's files, NEW worker names xz2 .. xz6, lanes run-m, run-v3, run-v3b, run-v3c, run-x1.
# usage: r10_chain29.sh [ownTag]   (default test-own-v134)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v134}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/r10chain29.txt"; }
say "r10chain29 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 "$X-snapB-god-cap-xe0028" "$B/list-eh20.txt"
  say "$1 done"
}
#   xw2 run-v3b   ONLY player 2 presses        xw3 run-v3c   both, player 2 five frames later (xsY's case)
#   xw4 run-x1 both, player 1 five frames later   xw5 run-x4  both in the same frames   xw6 run-x5  ONLY player 1
one xz2 run-m 29050 28081 idle.txt mashrc_long_p2.txt &
one xz3 run-v3 30150 28061 mashrc_long_p1.txt mashrc_long_p2_off5.txt &
one xz4 run-v3b 30350 28062 mashrc_long_p1_off5.txt mashrc_long_p2.txt &
one xz5 run-v3c 30550 28063 mashrc_long_p1.txt mashrc_long_p2.txt &
one xz6 run-x1 30750 28064 mashrc_long_p1.txt idle.txt &
wait
say "r10chain29 through"
