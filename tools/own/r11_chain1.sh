#!/bin/bash
# TEST ONLY (part 141, the seventy-ninth glue --menuowner): PLAYER 2 TALKS TO THE ELF (nm10, teleport kit -tw2 as wtB), and PLAYER 1
# PRESSES UP at 7500 while player 2's "Make presents? / Let's make it!" box is open (player 2: DOWN 7400, Circle 7600).
#   mo1 run-x5  candidate test-own-mo1 (--menuowner): player 1's UP must do nothing -> the toy cannon starts
#   mo0 run-x6  control merged-v18-own (build 24): player 1's UP moves player 2's hand back
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
SN="7350,7450,7550,7650,7800,8000,8500,9000,10000"
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/sp_probe.py" SNAPS="$SN" FRAMES=10500 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r11 TAG=r11$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one mo1 run-x5 31550 28068 test-own-mo1-snapB-tw2 walkin_up7500_p1.txt walkin_talk_p2.txt "$B/list-st-nm10.txt" &
one mo0 run-x6 31750 28069 merged-v18-own-snapB-tw2 walkin_up7500_p1.txt walkin_talk_p2.txt "$B/list-st-nm10.txt" &
wait
