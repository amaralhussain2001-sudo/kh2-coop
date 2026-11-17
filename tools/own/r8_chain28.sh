#!/bin/bash
# TEST ONLY (eighth round, plan row 9, first step): candidate v48 (the twin's own script callbacks see him as the player).
#   gp9   Shan-Yu, player 2 ALONE fights: his hero in the clash AND "Press" in HIS menu (pictures every 500 frames)
#   cap5  both players press, the recorder at the paired-move routine: one clash keeps ONE hero from 0xFC to 0xFE
#   gp10  the mirror: player 1 ALONE fights, player 2 idle
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/gp9.log, cap5.log, gp10.log; progress chain28.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain28.txt"; }
say "chain28 start"
LONG="5200,5500,6000,6500,7000,7500,8000,8500,9000,9500,10000,10500,11000,11500,12000,12500,13000,13500,14000,14500,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp9 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh gp9 run-m 29050 28081 test-own-v48-snapB-god-strong "$L/list-sy.txt"
say "gp9 done"
CS="5200,5600,6000,6400,6800,7000,7200,7400,7800,8200,8600,9000,9600,10200,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap5 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap5 run-m 29050 28081 test-own-v48-snapB-def-cap "$L/list-sy.txt"
say "cap5 done"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp10 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh gp10 run-m 29050 28081 test-own-v48-snapB-god-strong "$L/list-sy.txt"
say "gp10 done"
say "chain28 through"
