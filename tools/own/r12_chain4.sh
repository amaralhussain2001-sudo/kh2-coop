#!/bin/bash
# TEST ONLY (part 142): VERIFICATION of the sync skip (r12_chain3's v1 .. v6 again; its "env $V" broke on the spaces in the paths).
# exe builds/pic1 + patches/own-view2 (SyncSkip = 00457580-004F3580), player 1 8x, player 2 3x, no dumps.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; R="$P/local/sweep/r12"; B="$P/local/sweep/r9"; cd "$P" || exit 1
export EXE="$P/emulator-src/builds/pic1/pcsx2-qtx64.exe" VIEWF="$P/patches/own-view2/SLPM-66675_F266B00B.view" NODUMP=1
( TAG=v1 FRAMES=11100 bash tools/own/pic_sweep.sh v1 run-x5 31550 merged-v19-own-snapB "$R/list-v-hb04.txt" ) &
( TAG=v2 FRAMES=11100 EXTRA2="TestPoke = 6000:000D1000:5A" bash tools/own/pic_sweep.sh v2 run-x6 31750 merged-v19-own-snapB "$R/list-v-hb04.txt" ) &
( TAG=v3 FRAMES=8600 P1S="$O/walkin_late_p1.txt" P2S="$O/walkin_talk_p2.txt" bash tools/own/pic_sweep.sh v3 run-x7 31950 merged-v19-own-snapB-tw2 "$B/list-st-nm10.txt"
  TAG=v4 FRAMES=7000 P1S="$O/pm_open_p1.txt" P2S="$O/pm_jam_p2.txt" bash tools/own/pic_sweep.sh v4 run-x7 31950 merged-v19-own-snapB "$B/list-st-nm10.txt" ) &
( ISO=test-s1-hb10s.iso TAG=v5 FRAMES=6700 P1S="$O/shop_xjam_p1.txt" P2S="$O/shop_buy2_p2.txt" bash tools/own/pic_sweep.sh v5 run-x8 32150 merged-v19-own-shop-w "$R/list-shop.txt"
  ISO=test-s1-hb13s.iso TAG=v6 FRAMES=9600 P1S="$O/worldmap_land_all_p1.txt" P2S="$O/idle.txt" bash tools/own/pic_sweep.sh v6 run-x8 32150 merged-v19-own "$R/list-save.txt" ) &
wait
