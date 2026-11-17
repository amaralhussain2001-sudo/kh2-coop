#!/bin/bash
# TEST ONLY (eighth round), candidate v52 (= v51 + the short "who was held" memory in glues 36 and 39):
#   cap7  Shan-Yu, both players press, the recorder at the paired-move routine: EVERY clash must keep one hero
#   gp14  Shan-Yu, player 2 alone with the fast mash: the prompt in his menu, the fight won
#   mkS3  Storm Rider, both fall at 6500: two Mickeys, both heroes back (nothing of the rescue may have changed)
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/cap7.log, gp14.log, mkS3.log; progress chain36.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain36.txt"; }
say "chain36 start"
CS="5200,5600,6000,6400,6800,7000,7200,7400,7800,8200,8600,9000,9600,10200,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap7 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap7 run-m 29050 28081 test-own-v52-snapB-def-cap "$L/list-sy.txt"
say "cap7 done"
LONG="5200,5500,6000,6500,7000,7500,8000,8500,9000,9500,10000,10500,11000,11500,12000,12500,13000,13500,14000,14500,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp14 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh gp14 run-m 29050 28081 test-own-v52-snapB-god-strong "$L/list-sy.txt"
say "gp14 done"
M2="5200,6400,6700,6900,7000,7400,8000,8500,8900,9500,10000,11000,11900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$M2 FRAMES=12000 TOUT=400 SWEEP_PROBE_WAIT=400 LOGDIR=local/sweep/b15 TAG=r8mkS3 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS3 run-m 29050 28081 test-own-v52-snapB-kill65-roll-abort "$L/list-sr1.txt"
say "mkS3 done"
say "chain36 through"
