#!/bin/bash
# TEST ONLY (tenth round, open item h): the ONE-HERO CONTROL of the Data fight's laser dome (eh20 98): the no-twin build
# test-v31-a-nn with the same kits (snapB, god, capture log, Xemnas's HP words 40 at 6500), player 1 presses as in xd6/xv1
# (mashrc_long_p1), player 2's pad idle. Lane run-x5. Compare with the two-hero runs xd2 .. xd6 (r10_chain4.sh).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
SN="5200,6000,7000,7400,7800,8000,8400,9000,10000,11000,12000,13000,14000,15000,15900"
ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9xn1 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh xn1 run-x5 31550 28068 test-v31-a-nn-snapB-god-cap-xe0028 "$B/list-eh20-98.txt"
