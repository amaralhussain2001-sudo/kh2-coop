#!/bin/bash
# TEST ONLY (eighth round, plan row 9, the other fights; a lane, sandbox run-x1): THE TEN BOSS ROOMS AGAIN ON CANDIDATE
# v92 (= v91 + the fifty-ninth glue --onevictim: a boss that holds one hero makes its further captures on that
# hero), five of them here (local/sweep/list-r9hc.txt). Everything as in r8_chain113.sh / r8_chain114.sh (HP held at
# 150, the v5 test disc, 20,000 frames, both players Circle / Triangle / R1, probe act_poll_probe.py); run names
# r8r9k-*. THE QUESTION: is the hero at the Groundshaker (lk15 59) let go now, and is nothing else worse.
# Log local/sweep/b15/r9hc.log; progress chain124.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain124.txt"; }
say "chain124 start"
ISO=test-v5-tt137.iso PROBE="$T/act_poll_probe.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8r9k P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh r9hc run-x1 30750 28064 test-own-v92-snapB-god "$L/list-r9hc.txt"
say "chain124 through"
