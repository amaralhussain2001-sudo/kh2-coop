#!/bin/bash
# TEST ONLY (tenth round, candidate v136 = glues 72 .. 77): two checks on the free lanes while r10_chain26.sh runs:
#   lbK run-x9  the Fortuneteller scene of lbH / lbJ (kit -snapB-god-cap-lb, both press): no fault line expected (glue 76)
#   bxA6 run-x10 item boxes, player 2 fights, player 1 far away (kit -snapB-god-strong-box): both bags grow (glue 74)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,14200,15000,15900"
ISO=test-s1-tt137.iso PROBE="$T/cap_log_probe3.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9lbK P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lbK run-x9 32350 28072 test-own-v136-snapB-god-cap-lb "$B/list-al00lb.txt" &
RANGES=0032F13C:4,0032E3D8:4 ISO=test-s1-tt137.iso PROBE="$T/sweepm_probe.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9bxA6 P1S="$O/walkfar_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh bxA6 run-x10 32550 28073 test-own-v136-snapB-god-strong-box "$B/list-al00lb.txt" &
wait
