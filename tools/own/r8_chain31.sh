#!/bin/bash
# TEST ONLY (eighth round, plan row 9 / register G3): candidate v50, Shan-Yu, player 2 ALONE with a FAST mash (Circle and
# Triangle in turn every 6 frames): with "Press" in his own menu he must win the clashes and the fight.
# ONE RUN on sandbox run-m. Log: local/sweep/b15/gp13.log; progress chain31.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain31.txt"; }
say "chain31 start"
LONG="5200,5500,6000,6500,7000,7500,8000,8500,9000,9500,10000,10500,11000,11500,12000,12500,13000,13500,14000,14500,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp13 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh gp13 run-m 29050 28081 test-own-v50-snapB-god-strong "$L/list-sy.txt"
say "gp13 done"
say "chain31 through"
