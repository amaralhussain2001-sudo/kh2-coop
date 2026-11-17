#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): the EXPERIMENT --together (candidate v63 = build 15 + the
# fiftieth glue: a boss's paired move is started on the other hero too when he is up and within 800 units).
#   tg1  Shan-Yu, both players press Circle / Triangle (HP held, strong): the action timeline of both heroes and
#        pictures through the first two clashes. THE QUESTIONS: are both in the move, do they stand inside each
#        other, does the second hero get free at the end, does the clash still end.
#   tg2  Shan-Yu, player 2 alone with the fast mash, 24,000 frames: is the fight still won.
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tg1.log, tg2.log; progress chain68.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain68.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain68 start"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5300,5560,5600,5650,5700,5800,5900,5980,6100,6520,6600,6800,7000,8000,9500,11900" FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh tg1 run-m 29050 28081 test-own-v63-snapB-god-strong "$L/list-sy.txt"
tlb tg1; say "tg1 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg2 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tg2 run-m 29050 28081 test-own-v63-snapB-god-strong "$L/list-sy.txt"
tlb tg2; say "tg2 done"
say "chain68 through"
