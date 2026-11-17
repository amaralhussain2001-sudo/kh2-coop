#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): the EXPERIMENT --together --together-far (candidate v64: a
# boss's paired move is started on the other hero too, AT ANY DISTANCE; run tg1 had player 1's hero too far away).
#   tg3  Shan-Yu, both players press Circle / Triangle (HP held, strong): the action timeline and a picture every
#        100 frames from 5500 to 7500. THE QUESTIONS: do both stand in the clash, inside each other or not, does
#        the second hero get free, does the clash end.
# ONE RUN, hidden, sandbox run-m. Log local/sweep/b15/tg3.log; progress chain69.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain69.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain69 start"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5300,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,8000,9500,11900" FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg3 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh tg3 run-m 29050 28081 test-own-v64-snapB-god-strong "$L/list-sy.txt"
tlb tg3; say "tg3 done"
say "chain69 through"
