#!/bin/bash
# TEST ONLY (part 141): the final form of --menuowner (candidate test-own-mo3).
#   sx3 run-x7  the shop test of r11_chain2 again (player 2 buys, player 1 presses Cross 4 times)
#   fx3 run-x8  an ordinary fight: nm10 jump, player 1 sweep_p1, player 2 mash_long_p2 (sweep4's default scripts), 9,000 frames
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="4900,5000,5090,5160,5300,5450,5550,5650,5750,5850,5980,6100,6300,6600"
( rm -rf "local/tests/r11sx3"; (python -I tools/own/wallet_probe.py "$P/local/tests/r11sx3" 28070 "$SN" "$P/local/tests/r11sx3-probe.txt" > /dev/null 2>&1 &)
  OWN_RUN_DIR=run-x7 OWN_PORT=31950 bash tools/own/run_own2.sh r11sx3 test-s1-hb10s.iso 6700 4.0 "$SN" "$O/shop_xjam_p1.txt" "$O/shop_buy2_p2.txt" idle 1 "$P/patches/test-own-mo3-shop-w" --pine 28070 --timeout 900 ) &
( ISO=test-v5-tt137.iso PROBE="$P/tools/own/mo_probe.py" SNAPS="5200,7000,8900" FRAMES=9000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r11 TAG=r11fx3 bash tools/own/sweep4.sh fx3 run-x8 32150 28071 test-own-mo3-snapB "$P/local/sweep/r9/list-st-nm10.txt" ) &
wait
