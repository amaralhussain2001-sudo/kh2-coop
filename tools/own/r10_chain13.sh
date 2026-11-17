#!/bin/bash
# TEST ONLY (tenth round): the last Xemnas's laser dome (story fight eh20 74), the five cases of r9_chain63.sh on candidate
# v132 (build 21 + glues 72 and 73), NEW worker names xw2 .. xw6, lanes run-v3b, run-v3c, run-x1, run-x4, run-x5.
# usage: r10_chain13.sh [ownTag]   (default test-own-v132)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v132}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/r10chain13.txt"; }
say "r10chain13 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 "$X-snapB-god-cap-xe0028" "$B/list-eh20.txt"
  say "$1 done"
}
#   xw2 run-v3b   ONLY player 2 presses        xw3 run-v3c   both, player 2 five frames later (xsY's case)
#   xw4 run-x1 both, player 1 five frames later   xw5 run-x4  both in the same frames   xw6 run-x5  ONLY player 1
one xw2 run-v3b 30350 28062 idle.txt mashrc_long_p2.txt &
one xw3 run-v3c 30550 28063 mashrc_long_p1.txt mashrc_long_p2_off5.txt &
one xw4 run-x1 30750 28064 mashrc_long_p1_off5.txt mashrc_long_p2.txt &
one xw5 run-x4 31350 28067 mashrc_long_p1.txt mashrc_long_p2.txt &
one xw6 run-x5 31550 28068 mashrc_long_p1.txt idle.txt &
wait
say "r10chain13 through"
