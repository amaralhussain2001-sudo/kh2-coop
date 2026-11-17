#!/bin/bash
# TEST ONLY (tenth round, glue 74): bR3 again as bR4 with both players' item places (0x0032E054 .., 0x0032E370 ..), player 2's stock
# (0x0032E380 ..) and the game's first bag bytes (0x0032F0B0 ..) read whole: where does a picked-up Potion go?
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
bx() { RANGES=0032E054:10,0032E370:20,0032F0B0:20,000F1D00:14 ISO=test-s1-tt137.iso PROBE="$T/sweepm_probe.py" FROM=4700 TO=15900 SNAPS="$SN" FRAMES=16000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$5" P2S="$O/$6" bash tools/own/sweep4.sh $1 $2 $3 $4 $7 "$B/list-al00lb.txt"; }
fr() { PROBE="$T/$5" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh $1 "$P/patches/test-own-v134-forms" test-s1-hb13s.iso $6 "$7" "$O/$8" "$O/$9" $2 $3 $4 > "$B/$1.log" 2>&1; }
bx bR4 run-v3b 30350 28062 walkfar_p1.txt mashrc_long_p2.txt test-own-v134-snapB-god-strong-rbp &
wait
