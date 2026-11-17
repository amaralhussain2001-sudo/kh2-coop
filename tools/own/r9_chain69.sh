#!/bin/bash
# TEST ONLY (ninth round, after build 21 was packaged): the last Xemnas's laser dome on v129 (= build 21) in the three cases that
# r9_chain63.sh ran only on v128 (NEW worker names: the old ones would skip the room as done). Capture log, HP 40 kit:
#   xv1 run-x7  ONLY player 1 presses     xv5 run-x8  both in the same frames     xv4 run-x9  player 1 five frames later
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=test-own-v129
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain69.txt"; }
say "chain69 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() {  # one <name> <sandbox> <port> <pine> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 "$X-snapB-god-cap-xe0028" "$B/list-eh20.txt"
  say "$1 done"
}
one xv1 run-x7 31950 28070 mashrc_long_p1.txt idle.txt &
one xv5 run-x8 32150 28071 mashrc_long_p1.txt mashrc_long_p2.txt &
one xv4 run-x9 32350 28072 mashrc_long_p1_off5.txt mashrc_long_p2.txt &
wait
say "chain69 through"
