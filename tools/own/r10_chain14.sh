#!/bin/bash
# TEST ONLY (tenth round, open item b): THE LARGE BODY'S "FULL SWING" WITH ITS ZONES SWITCHED ON BY A KIT (tools/own/make_lbkit.py:
# the group test 0x0019BD08 says "on" for group 6 of object 0x0001). Agrabah's city al00 program 2 (ten Large Bodies, list
# list-al00lb.txt), disc test-s1-tt137.iso, candidate v132, kit -snapB-god-cap-lb (HP held, capture log), probe cap_log_probe3.py
# (each capture with the captor's object number and kind), 16,000 frames. A Full Swing = capture 0xFC by a Large Body on the presser.
#   lbE run-x6  player 1 walks away, player 2 presses (mashrc_long_p2)    lbF run-x7  player 1 presses (tri_long_p1), player 2 idle
#   lbG run-x8  both press (mashrc_long_p1 / _p2)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
one() { ISO=test-s1-tt137.iso PROBE="$T/cap_log_probe3.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 test-own-v132-snapB-god-cap-lb "$B/list-al00lb.txt"; }
one lbE run-x6 31750 28069 walkfar_p1.txt mashrc_long_p2.txt &
one lbF run-x7 31950 28070 tri_long_p1.txt idle.txt &
one lbG run-x8 32150 28071 mashrc_long_p1.txt mashrc_long_p2.txt &
wait
