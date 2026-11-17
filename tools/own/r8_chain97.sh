#!/bin/bash
# TEST ONLY (eighth round): CANDIDATE v88 (build 16 + the glues 53 to 56 + the own-screen option --cannon1view: a
# second hero in the three one-hero small games, made at run time) BEFORE its whole regression, on the v5 test disc.
#   one8  the toy cannon nm10 63, 16,000 frames: both cannons, one view, how the game ends
#   one9  the carpet escape al14 61 and the sidecar eh22 72, 9,000 frames
# Both players move and press (sp_p1 / sp_p2). Probe sp_probe.py. ONE RUN AT A TIME, hidden, sandbox run-m.
# Logs local/sweep/b15/one8.log, one9.log; progress chain97.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain97.txt"; }
say "chain97 start"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900" FRAMES=16000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8one8 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one8 run-m 29050 28081 test-own-v88-snapB "$L/list-nm63.txt"
say "one8 done"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="4900,5250,5600,5900,6200,6500,6800,7100,7400,7700,8000,8300,8600,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one9 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one9 run-m 29050 28081 test-own-v88-snapB "$L/list-one2.txt"
say "one9 done"
say "chain97 through"
