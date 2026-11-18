#!/bin/bash
# TEST ONLY (part 141, --menuowner): PLAYER 2 BUYS A POTION (disc test-s1-hb10s, kit -shop-w as wa6: player 2 pinned at the item stall,
# wallets 5,000 / 3,000), and PLAYER 1 PRESSES CROSS at 5450, 5550, 5650, 5800 while player 2's shop is open.
#   sx1 run-x7  candidate test-own-mo1: player 1's Cross must do nothing -> player 2's wallet 2,960, his stock holds the Potion
#   sx0 run-x8  control merged-v18-own (build 24): player 1's Cross backs out of player 2's shop
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="4900,5000,5090,5160,5300,5450,5550,5650,5750,5850,5980,6100,6300,6600"
one() { n=$1; rm -rf "local/tests/$n"; (python -I tools/own/wallet_probe.py "$P/local/tests/$n" $4 "$SN" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  OWN_RUN_DIR=$2 OWN_PORT=$3 bash tools/own/run_own2.sh "$n" test-s1-hb10s.iso 6700 4.0 "$SN" "$O/shop_xjam_p1.txt" "$O/shop_buy2_p2.txt" idle 1 "$P/patches/$5" --pine $4 --timeout 900; }
one r11sx1 run-x7 31950 28070 test-own-mo1-shop-w &
one r11sx0 run-x8 32150 28071 merged-v18-own-shop-w &
wait
