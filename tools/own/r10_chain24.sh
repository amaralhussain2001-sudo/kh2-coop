#!/bin/bash
# TEST ONLY (tenth round): runs lbG / lbH (v132 + the Full Swing zones kit make_lbkit.py, both players press) had 26 fault lines
# (store to 0 at pc 0x16e1a4 = script call (0, 76), handler 0x0016E180) at about frame 14,200, when player 1 used the Fortuneteller's
# reaction command "Clear Shot". Here candidate v134 with glue 76 (--setposguard) (run lbJ, lane run-x7): no fault line expected.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,14200,14400,15000,15900"
one() { ISO=test-s1-tt137.iso PROBE="$T/cap_log_probe3.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 $7 "$B/list-al00lb.txt"; }
one lbJ run-x7 31950 28070 mashrc_long_p1.txt mashrc_long_p2.txt test-own-v134-snapB-god-cap-lb &
wait
