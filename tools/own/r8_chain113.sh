#!/bin/bash
# TEST ONLY (eighth round, plan row 9, the other fights; A LANE BESIDE THE QUEUE since the user said on 2026-11-14
# 23:50 "i'm not going to play so you can run several tests"): the first five boss rooms of r8_chain111.sh
# (local/sweep/list-r9ha.txt: the Dark Thorn, Cerberus, Scar, Xaldin, Demyx in the Underworld) on the NEW sandbox
# run-x1 (port 30750, PINE 28064). Everything else as chain 111: candidate v89 with HP held at 150, the v5 test
# disc, 20,000 frames, both players Circle / Triangle / R1, probe act_poll_probe.py. r8_chain111.sh is NOT run.
# Log local/sweep/b15/r9ha.log; progress chain113.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain113.txt"; }
say "chain113 start"
ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8r9h P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh r9ha run-x1 30750 28064 test-own-v89-snapB-god "$L/list-r9ha.txt"
say "chain113 through"
