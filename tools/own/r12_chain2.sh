#!/bin/bash
# TEST ONLY (part 142): the second differing area of r12 (Gummi runs, f6000, 0x00E9FB48 ..): dumps every 400 frames 4400 .. 8400 on
# routes 0 and 3; and the talk / pause menu / shop runs again with ramdiff's full extents. Player 1 8x, player 2 3x.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; R="$P/local/sweep/r12"; B="$P/local/sweep/r9"; cd "$P" || exit 1
D="4400,4800,5200,5600,6000,6400,6800,7200,7600,8000,8400"
for r in 0 3; do ( ISO=test-s1-tt137.iso TAG=picH$r DUMPS="$D" FRAMES=8500 P1S="$P/tests/scripts/lane-s3/gb_p1_fight.txt" P2S="$P/tests/scripts/lane-s3/gb_p2_fight.txt" bash tools/own/pic_sweep.sh ph$r run-x$((5 + r / 3)) $((31550 + 200 * (r / 3))) merged-v19-own-gum$r "$R/list-gum.txt" ) & done
( TAG=picT2 DUMPS="7350,7550" FRAMES=7700 P1S="$O/walkin_late_p1.txt" P2S="$O/walkin_talk_p2.txt" bash tools/own/pic_sweep.sh ps2 run-x7 31950 merged-v19-own-snapB-tw2 "$B/list-st-nm10.txt" ) &
( TAG=picM2 DUMPS="6300,6900" FRAMES=7000 P1S="$O/pm_open_p1.txt" P2S="$O/pm_jam_p2.txt" bash tools/own/pic_sweep.sh pm2 run-x8 32150 merged-v19-own-snapB "$B/list-st-nm10.txt" ) &
( ISO=test-s1-hb10s.iso TAG=picS2 DUMPS="5300,5980,6300" FRAMES=6700 P1S="$O/shop_xjam_p1.txt" P2S="$O/shop_buy2_p2.txt" bash tools/own/pic_sweep.sh pshop2 run-x9 32350 merged-v19-own-shop-w "$R/list-shop.txt" ) &
wait
