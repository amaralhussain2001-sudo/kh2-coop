#!/bin/bash
# TEST ONLY (tenth round, the Fortuneteller finding of part 122): THE NO-PATCH CONTROL. The original game (no patch; only the god kit,
# HP held at 150: patches/test-stock-god) in Agrabah's city al00 program 2 (Fortunetellers 447 units from the start), disc
# test-s1-tt137.iso, one hero, 16,000 frames, pictures every 200 frames from 12,000. Does a Clear Shot of the hero make the same
# fault lines (store to 0 at pc 0x16e1a4) without the two-hero build? Lanes run-x5 .. run-x7.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,12400,12800,13200,13600,14000,14200,14400,14800,15200,15600,15900"
one() { ISO=test-s1-tt137.iso PROBE="$T/cap_log_probe3.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/idle.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 test-stock-god "$B/list-al00lb.txt"; }
one ftA run-x5 31550 28068 mashrc_long_p1.txt &
one ftB run-x6 31750 28069 tri_long_p1.txt &
one ftC run-x7 31950 28070 walkfar_p1.txt &
wait
