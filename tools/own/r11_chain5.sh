#!/bin/bash
# TEST ONLY (part 141): the seventy-ninth glue's third form (candidate test-own-mo4).
#   tk4 run-x5  the elf talk (player 2), player 1 presses START at 7500 and UP at 7550: the owner must stay 2, the game must start
#   rl4 run-x6  player 2 opens (START 6200) and closes (Cross 6400) the pause menu; player 1 opens it (6700), DOWN (6900)
#   pm4 run-x7  the pause menu test pm1 again
#   sx4 run-x8  the shop test again
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; cd "$P" || exit 1
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/mo_probe.py" SNAPS="$9" FRAMES=${10} TOUT=1300 SWEEP_PROBE_WAIT=1300 LOGDIR=local/sweep/r11 TAG=r11$1 P1S="$O/$6" P2S="$O/$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$8"; }
one tk4 run-x5 31550 28068 test-own-mo4-snapB-tw2 walkin_startup_p1.txt walkin_talk_p2.txt "$B/list-st-nm10.txt" "7450,7530,7580,7650,8000,8500" 8600 &
one rl4 run-x6 31750 28069 test-own-mo4-snapB pm_open6700_p1.txt pm_openclose_p2.txt "$B/list-st-nm10.txt" "6300,6500,6800,7000,7200" 7300 &
one pm4 run-x7 31950 28070 test-own-mo4-snapB pm_open_p1.txt pm_jam_p2.txt "$B/list-st-nm10.txt" "6300,6700,6900" 7000 &
SN="4900,5000,5090,5160,5300,5450,5550,5650,5750,5850,5980,6100,6300,6600"
( rm -rf "local/tests/r11sx4"; (python -I tools/own/wallet_probe.py "$P/local/tests/r11sx4" 28071 "$SN" "$P/local/tests/r11sx4-probe.txt" > /dev/null 2>&1 &)
  OWN_RUN_DIR=run-x8 OWN_PORT=32150 bash tools/own/run_own2.sh r11sx4 test-s1-hb10s.iso 6700 4.0 "$SN" "$O/shop_xjam_p1.txt" "$O/shop_buy2_p2.txt" idle 1 "$P/patches/test-own-mo4-shop-w" --pine 28071 --timeout 900 ) &
wait
