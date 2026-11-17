#!/bin/bash
# TEST ONLY (tenth round, open item b): run lbG (v132 + the Full Swing zones kit, both players press) had 26 fault lines (store to 0
# at pc 0x16e1a4, script call 0x0016E180, about frame 14,200, after a Full Swing by player 1). THE ONE-HERO CONTROL with the same
# kit: the no-twin build test-v31-c-nn (-snapB-god-cap-lb), player 1 presses as in lbG; a second control with player 1's
# Triangle only; and lbG once more (new name lbH) to see whether it comes again. Lanes run-x5, run-x6, run-x7.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,14200,14400,15000,15900"
one() { ISO=test-s1-tt137.iso PROBE="$T/cap_log_probe3.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 $7 "$B/list-al00lb.txt"; }
one lbN1 run-x5 31550 28068 mashrc_long_p1.txt idle.txt test-v31-c-nn-snapB-god-cap-lb &
one lbN2 run-x6 31750 28069 tri_long_p1.txt idle.txt test-v31-c-nn-snapB-god-cap-lb &
one lbH run-x7 31950 28070 mashrc_long_p1.txt mashrc_long_p2.txt test-own-v132-snapB-god-cap-lb &
wait
