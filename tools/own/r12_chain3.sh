#!/bin/bash
# TEST ONLY (part 142): VERIFICATION of the sync skip, exe builds/pic1 + patches/own-view2 (SyncSkip = 00457580-004F3580),
# player 1 8x, player 2 3x, no dumps (the emulator's own check judges). Plus a long Gummi measurement (exe card1, no skip, dumps).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; R="$P/local/sweep/r12"; B="$P/local/sweep/r9"; cd "$P" || exit 1
V="EXE=$P/emulator-src/builds/pic1/pcsx2-qtx64.exe VIEWF=$P/patches/own-view2/SLPM-66675_F266B00B.view NODUMP=1"
grep -m1 " HB04_MS403 " "$B/list-rs6-all.txt" > "$R/list-v-hb04.txt"
( env $V TAG=v1 FRAMES=11100 bash tools/own/pic_sweep.sh v1 run-x5 31550 merged-v19-own-snapB "$R/list-v-hb04.txt" ) &
( env $V TAG=v2 FRAMES=11100 EXTRA2="TestPoke = 6000:000D1000:5A" bash tools/own/pic_sweep.sh v2 run-x6 31750 merged-v19-own-snapB "$R/list-v-hb04.txt" ) &
( env $V TAG=v3 FRAMES=8600 P1S="$O/walkin_late_p1.txt" P2S="$O/walkin_talk_p2.txt" bash tools/own/pic_sweep.sh v3 run-x7 31950 merged-v19-own-snapB-tw2 "$B/list-st-nm10.txt"
  env $V TAG=v4 FRAMES=7000 P1S="$O/pm_open_p1.txt" P2S="$O/pm_jam_p2.txt" bash tools/own/pic_sweep.sh v4 run-x7 31950 merged-v19-own-snapB "$B/list-st-nm10.txt" ) &
( env $V ISO=test-s1-hb10s.iso TAG=v5 FRAMES=6700 P1S="$O/shop_xjam_p1.txt" P2S="$O/shop_buy2_p2.txt" bash tools/own/pic_sweep.sh v5 run-x8 32150 merged-v19-own-shop-w "$R/list-shop.txt"
  env $V ISO=test-s1-hb13s.iso TAG=v6 FRAMES=9600 P1S="$O/worldmap_land_all_p1.txt" P2S="$O/idle.txt" bash tools/own/pic_sweep.sh v6 run-x8 32150 merged-v19-own "$R/list-save.txt" ) &
( ISO=test-s1-tt137.iso TAG=picL DUMPS="5600,8000,12000,16000,20000,24000,28000,32000,36000,39500" FRAMES=40000 P1S="$P/tests/scripts/lane-s3/gb_p1_fight.txt" P2S="$P/tests/scripts/lane-s3/gb_p2_fight.txt" bash tools/own/pic_sweep.sh pl run-x9 32350 merged-v19-own-gum0 "$R/list-gum.txt" ) &
wait
