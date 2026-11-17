#!/bin/bash
# TEST ONLY (eighth round, plan row 9, first step): candidate v46 (the "held by this object" test put right).
#   gp8   Shan-Yu, player 2 ALONE fights: his hero in the clash AND "Press" in HIS menu; can he beat Shan-Yu now?
#   cap4  both players press, the recorder at the paired-move routine: one clash keeps ONE hero from 0xFC to 0xFE
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/gp8.log, cap4.log; progress chain24.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain24.txt"; }
say "chain24 start"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp8 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh gp8 run-m 29050 28081 test-own-v46-snapB-god-strong "$L/list-sy.txt"
say "gp8 done"
CS="5200,5600,6000,6400,6800,7000,7200,7400,7800,8200,8600,9000,9600,10200,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap4 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap4 run-m 29050 28081 test-own-v46-snapB-def-cap "$L/list-sy.txt"
say "cap4 done"
say "chain24 through"
