#!/bin/bash
# TEST ONLY (eighth round, plan row 9, first step): candidate v43 (glues 30 to 39). Shan-Yu, HP held, strong heroes.
#   gp6  player 2 ALONE fights (player 1 only starts the game): his hero in the clash AND "Press" in HIS menu
#   gp7  the mirror: player 1 ALONE fights, player 2 stands idle: nothing may change for player 1
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/gp6.log, gp7.log; progress chain18.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain18.txt"; }
say "chain18 start"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp6 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh gp6 run-m 29050 28081 test-own-v43-snapB-god-strong "$L/list-sy.txt"
say "gp6 done"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp7 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh gp7 run-m 29050 28081 test-own-v43-snapB-god-strong "$L/list-sy.txt"
say "gp7 done"
# cap3: both players Circle / Triangle with the recorder at the paired-move routine: one clash must keep ONE hero from its start
# (move FC) to its end (move FE). Run cap2 (candidate v39) mixed the two heroes inside a clash.
CS="5200,5600,6000,6400,6800,7000,7200,7400,7800,8200,8600,9000,9600,10200,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap3 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap3 run-m 29050 28081 test-own-v43-snapB-def-cap "$L/list-sy.txt"
say "cap3 done"
say "chain18 through"
