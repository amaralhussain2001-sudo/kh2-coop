#!/bin/bash
# TEST ONLY (eighth round, the toy cannon): candidate v87 = v86 + the own-screen option --cannon1view (one view while
# the engine's player is a toy cannon). The v5 test disc, nm10 63, both players press. Read: both players' pictures
# (the same picture, both cannons seen from behind?), the score and the toy count, in sync, the fault line count.
# ONE RUN, hidden, sandbox run-m. Log local/sweep/b15/one7.log; progress chain96.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain96.txt"; }
say "chain96 start"
ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="4900,5250,5600,5900,6200,6500,6800,7100,7400,7700,8000,8300,8600,8900" FRAMES=9000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8one7 P1S="$O/sp_p1.txt" P2S="$O/sp_p2.txt" bash tools/own/sweep4.sh one7 run-m 29050 28081 test-own-v87-snapB "$L/list-nm63.txt"
say "one7 done"
say "chain96 through"
