#!/bin/bash
# TEST ONLY (part 141): the fourth form (candidate test-own-mo5). tk5 = tk4 (player 1 START 7500 + UP 7550 in player 2's talk),
# tw5 = the plain talk (player 2 talks and chooses, player 1 idle: the game must start), pm5 = pm1 (the pause menu, player 1 opens).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/mo_probe.py" SNAPS="$9" FRAMES=${10} TOUT=1300 SWEEP_PROBE_WAIT=1300 LOGDIR=local/sweep/r11 TAG=r11$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one tk5 run-x5 31550 28068 test-own-mo5-snapB-tw2 walkin_startup_p1.txt walkin_talk_p2.txt "$B/list-st-nm10.txt" "7450,7530,7580,7650,8000,8500" 8600 &
one tw5 run-x6 31750 28069 test-own-mo5-snapB-tw2 walkin_late_p1.txt walkin_talk_p2.txt "$B/list-st-nm10.txt" "7450,7650,8000" 8100 &
one pm5 run-x7 31950 28070 test-own-mo5-snapB pm_open_p1.txt pm_jam_p2.txt "$B/list-st-nm10.txt" "6300,6700,6900" 7000 &
wait
