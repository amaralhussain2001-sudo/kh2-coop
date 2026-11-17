#!/bin/bash
# TEST ONLY (eighth round, the three one-hero small games): THE SECOND HERO MADE AT RUN TIME (fifty-sixth glue,
# --twinmake). Candidate v85 = v84 + that glue, on the v5 test disc (its room data have ONE hero in these three
# games): the toy cannon nm10 63, the carpet escape al14 61, the sidecar eh22 72. Both players move and press.
# Read: is there a second hero (sp_probe.py prints both), the pictures, in sync, the fault line count.
# ONE RUN AT A TIME, hidden, sandbox run-m. Log local/sweep/b15/one3.log; progress chain93.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain93.txt"; }
say "chain93 start"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="4900,5250,5600,5900,6200,6500,6800,7100,7400,7700,8000,8300,8600,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one3 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one3 run-m 29050 28081 test-own-v85-snapB "$L/list-one3.txt"
say "one3 done"
say "chain93 through"
