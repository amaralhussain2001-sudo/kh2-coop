#!/bin/bash
# TEST ONLY (part 141, --menuowner): THE PAUSE MENU. Disc test-v5-tt137 jump to nm10, kit -snapB.
#   pm1 run-x5  candidate test-own-mo3: player 1 opens (START 6200), player 2 DOWN x3 (6400..6600), player 1 DOWN (6800)
#   pm2 run-x6  candidate test-own-mo3: player 2 opens (START 6200), player 1 DOWN x3, player 2 DOWN (6800)
#   pm0 run-x7  control merged-v18-own (build 24): as pm1
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
SN="6150,6300,6450,6550,6700,6900"
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/mo_probe.py" SNAPS="$SN" FRAMES=7000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r11 TAG=r11$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one pm1 run-x5 31550 28068 test-own-mo3-snapB pm_open_p1.txt pm_jam_p2.txt "$B/list-st-nm10.txt" &
one pm2 run-x6 31750 28069 test-own-mo3-snapB pm_jam_p1.txt pm_open_p2.txt "$B/list-st-nm10.txt" &
one pm0 run-x7 31950 28070 merged-v18-own-snapB pm_open_p1.txt pm_jam_p2.txt "$B/list-st-nm10.txt" &
wait
