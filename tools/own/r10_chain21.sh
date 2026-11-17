#!/bin/bash
# TEST ONLY (tenth round, open item d): THE STORY'S OWN TRIGGERS of the toy cannon (nm10 program 22, the elf N_NM100_RTN at
# (-318.7, 0, 95.8), reaction command 850 "Talk", then the box "Make presents?") and of the carpet escape (al11 program 10, event
# volume e_00 centre (-1108, -500, 861), lane R's rule: both heroes there). Candidate v132, kits -snapB-tw* (make_teleport.py):
#   wtA run-x5  player 1 teleported to the elf at 6000, his Talk, DOWN, Circle
#   wtB run-x6  PLAYER 2 teleported to the elf at 6000, his Talk, DOWN, Circle; player 1 answers late (DOWN 9000, Circle 9200)
#   wtC run-x7  PLAYER 2 teleported into the escape's volume at 6000, player 1 at 8000 (nobody presses)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5900,6050,6500,7000,7350,7450,7700,8000,8500,9100,9300,9600,10000,11000,12000,13000,13900"
one() { ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="$SN" FRAMES=14000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one wtA run-x5 31550 28068 test-own-v132-snapB-tw1 walkin_talk_p1.txt idle.txt "$B/list-st-nm10.txt" &
one wtB run-x6 31750 28069 test-own-v132-snapB-tw2 walkin_late_p1.txt walkin_talk_p2.txt "$B/list-st-nm10.txt" &
one wtC run-x7 31950 28070 test-own-v132-snapB-tw3 ../merge/newgame_only.txt idle.txt "$B/list-st-al11.txt" &
wait
