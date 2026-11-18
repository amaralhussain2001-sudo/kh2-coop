#!/bin/bash
# TEST ONLY (part 142): exe builds/pic2 + patches/own-view3 (SyncSkip + SyncSkipWhile for the Gummi Menu), player 1 8x, player 2 3x.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; R="$P/local/sweep/r12"; cd "$P" || exit 1
export EXE="$P/emulator-src/builds/pic2/pcsx2-qtx64.exe" VIEWF="$P/patches/own-view3/SLPM-66675_F266B00B.view" NODUMP=1
G="$P/tests/scripts/lane-s3"
( ISO=test-s1-tt137.iso TAG=g1 FRAMES=14000 P1S="$G/gb_p1_fight.txt" P2S="$G/gb_p2_fight.txt" bash tools/own/pic_sweep.sh g1 run-x5 31550 merged-v19-own-gum0 "$R/list-gum.txt" ) &
( ISO=test-s1-tt137.iso TAG=g2 FRAMES=14000 EXTRA2="TestPoke = 9000:00E9F800:5A" P1S="$G/gb_p1_fight.txt" P2S="$G/gb_p2_fight.txt" bash tools/own/pic_sweep.sh g2 run-x6 31750 merged-v19-own-gum0 "$R/list-gum.txt" ) &
( TAG=v1b FRAMES=11100 bash tools/own/pic_sweep.sh v1b run-x7 31950 merged-v19-own-snapB "$R/list-v-hb04.txt" ) &
( TAG=v2b FRAMES=11100 EXTRA2="TestPoke = 6000:000D1000:5A" bash tools/own/pic_sweep.sh v2b run-x8 32150 merged-v19-own-snapB "$R/list-v-hb04.txt" ) &
wait
