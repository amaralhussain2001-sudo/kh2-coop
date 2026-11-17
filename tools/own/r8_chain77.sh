#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): THE CONTROL for the runs tg22 / tg23 on BUILD 15 (candidate
# v62, no --together): the same scripts, the same 24,000 frames. Is Shan-Yu's fight won, is the gate destroyed.
#   tgc1  player 1 idle near the gate, player 2 fights with the fast mash
#   tgc2  player 1 fights with the fast mash, player 2 idle
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tgc1.log, tgc2.log; progress chain77.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain77.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain77 start"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tgc1 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tgc1 run-m 29050 28081 test-own-v62-snapB-god-strong "$L/list-sy.txt"
tlb tgc1; say "tgc1 done"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tgc2 P1S="$O/mashfast_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh tgc2 run-m 29050 28081 test-own-v62-snapB-god-strong "$L/list-sy.txt"
tlb tgc2; say "tgc2 done"
say "chain77 through"
