#!/bin/bash
# TEST ONLY (eighth round, plan row 9): WHO OFFERS "Press" (command 270) and to whose control object, candidate v46,
# Shan-Yu, player 2 alone fights. The recorder at "offer a command to a control object's slot" (make_rec_offer.py).
# ONE RUN on sandbox run-m. Log: local/sweep/b15/of270.log; progress chain27.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain27.txt"; }
say "chain27 start"
PROBE="$T/offer_probe.py" SNAPS="5200,6000,7000,8000,9000,10000,11000,11900" FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8of270 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh of270 run-m 29050 28081 test-own-v46-snapB-strong-rec270 "$L/list-sy.txt"
say "of270 done"
say "chain27 through"
