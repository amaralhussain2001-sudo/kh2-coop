#!/bin/bash
# TEST ONLY (eighth round): ONE RUN AT A TIME on sandbox run-m.
#   zr    the long zero runs of the save data in a New Game state (roam disc), for plan row 39's "place in the save"
#   cap0  Shan-Yu with the build: who is pulled into the boss's paired moves (recorder at 0x00180378: ra, victim,
#         motion id, counter). Both players Circle / Triangle. Defense 150, no HP hold.
#   cap1  the same with the experiment "--react" (a boss's Reaction Command is offered to both heroes)
# Logs: local/sweep/b15/; the recorder's lines are in the log lines and in local/tests/<name>-probe.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"; S="$P/tests/scripts/merge"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain7.txt"; }
say "chain7 start"
PROBE="$T/zrun_probe.py" RANGES=0032BB30:10FC0 MINLEN=100 bash tools/own/dusk_one.sh t15-zrun "$P/patches/test-own-v33" test-m-roam.iso 6000 "4690,5200,5900" "$S/newgame_only.txt" "$O/idle.txt" run-m 29050 28081 > "$B/zrun.log" 2>&1
say "zr done"
CS="5200,5600,6000,6400,6800,7000,7200,7400,7800,8200,8600,9000,9600,10200,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap0 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" \
  bash tools/own/sweep4.sh cap0 run-m 29050 28081 test-own-v33-snapB-def-cap "$L/list-sy.txt"
say "cap0 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" \
  bash tools/own/sweep4.sh cap1 run-m 29050 28081 test-own-v34-react-snapB-def-cap "$L/list-sy.txt"
say "cap1 done"
say "chain7 through"
