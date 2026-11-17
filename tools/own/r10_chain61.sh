#!/bin/bash
# RECORD RE-WRITTEN UNDER A NEW NAME (2026-11-16): this chain ran as tools/own/r10_chain55.sh (a fork's run for item 10, take 1); that
# name was later taken by another chain (the Gummi fork's), so the run is kept here, unchanged.
# TEST ONLY (tenth round, item 10 of the user's list, a fork's run; lanes run-x3 .. run-x6): THE FORTUNETELLER'S CLEAR SHOT WITH ONE
# HERO. The ORIGINAL GAME (patches/test-stock-god-cap-lb = test-stock-god + make_rec_cap3.py + make_lbkit.py, the same recorder and
# Large Body kit as lbH's -snapB-god-cap-lb) on the TRUE ONE-HERO jump disc test-s1-tt137solo.iso, Agrabah al00 program 2
# (list-al00lb.txt), 24,000 frames, probe cap_log_probe3.py (a Fortuneteller grab = captor object 000B). sweep4.sh keeps the
# "TLB Miss" lines of player 1's emulator in local/tests/<run>-emulog.txt (lbH, two heroes, build 21: 26 at pc 0x16e1a4 after a Clear Shot).
#   fo1 x3 mashrc_long_p1 (lbH's player 1)   fo2 x4 tri_long_p1   fo3 x5 mashrc_long_p1_s7   fo4 x6 tri_long_p1_s7 (the same presses 7 frames later: another path)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; T="$P/tools/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
one() { ISO=test-s1-tt137solo.iso PROBE="$T/cap_log_probe3.py" FROM=4700 TO=23900 SNAPS="$SN" FRAMES=24000 TOUT=2400 SWEEP_PROBE_WAIT=2400 LOGDIR=local/sweep/r9 TAG=r10$1 P1S="$O/$5" P2S="$O/idle.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 test-stock-god-cap-lb "$B/list-al00lb.txt"; }
one fo1 run-x3 31150 28066 mashrc_long_p1.txt &
one fo2 run-x4 31350 28067 tri_long_p1.txt &
one fo3 run-x5 31550 28068 mashrc_long_p1_s7.txt &
one fo4 run-x6 31750 28069 tri_long_p1_s7.txt &
wait
