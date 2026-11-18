#!/bin/bash
# TEST ONLY (part 142): WHICH MEMORY DIFFERS WHEN THE TWO PCs DRAW AT DIFFERENT PICTURE QUALITY (player 1 8x, player 2 3x)?
# build 27 (merged-v19-own, exe builds/card1), EE dumps compared by tools/own/ramdiff.py; logs local/sweep/r12/<worker>.log
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; R="$P/local/sweep/r12"; B="$P/local/sweep/r9"; cd "$P" || exit 1
fights() { TAG=pic$1 bash tools/own/pic_sweep.sh pf$1 $2 $3 merged-v19-own-snapB "$R/list-pic-r$1.txt"; }
fights 0 run-x5 31550 & fights 1 run-x6 31750 & fights 2 run-x7 31950 & fights 3 run-x8 32150 &
( # the screens with an owner: talk (box open 7300 .. 7600, rules screen 8000), pause menu (open 6300 .. 6900), shop (open 5160 .. 6100)
  TAG=picT DUMPS="2000,7350,7550,8000" FRAMES=8100 P1S="$O/walkin_late_p1.txt" P2S="$O/walkin_talk_p2.txt" bash tools/own/pic_sweep.sh ps run-x9 32350 merged-v19-own-snapB-tw2 "$B/list-st-nm10.txt"
  TAG=picM DUMPS="6300,6600,6900" FRAMES=7000 P1S="$O/pm_open_p1.txt" P2S="$O/pm_jam_p2.txt" bash tools/own/pic_sweep.sh pm run-x9 32350 merged-v19-own-snapB "$B/list-st-nm10.txt"
  ISO=test-s1-hb10s.iso TAG=picS DUMPS="5300,5650,5980,6300" FRAMES=6700 P1S="$O/shop_xjam_p1.txt" P2S="$O/shop_buy2_p2.txt" bash tools/own/pic_sweep.sh pshop run-x9 32350 merged-v19-own-shop-w "$R/list-shop.txt" ) &
( for r in 0 3; do ISO=test-s1-tt137.iso TAG=picG$r DUMPS="6000,9000,12000,14000" FRAMES=14100 P1S="$P/tests/scripts/lane-s3/gb_p1_fight.txt" P2S="$P/tests/scripts/lane-s3/gb_p2_fight.txt" bash tools/own/pic_sweep.sh pg$r run-x10 32550 merged-v19-own-gum$r "$R/list-gum.txt"; done ) &
wait
