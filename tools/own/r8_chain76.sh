#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): the EXPERIMENT --together, SEVENTH form (candidate v70): is
# Shan-Yu's fight still WON with two heroes in the clash, and does it work with the roles the other way round
# (player 1's hero is the boss's own, player 2's hero the second one).
#   tg22  player 1 idle near the gate, player 2 fights with the fast mash, 24,000 frames: is the fight won
#   tg23  player 1 fights with the fast mash, player 2 idle, 24,000 frames: is the fight won
#   tg24  player 1 presses ONLY Circle, player 2 ONLY Triangle, 12,000 frames, the action timeline: does player
#         2's hero (the second one now) push with his own Triangle
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tg22.log ..; progress chain76.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain76.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain76 start"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg22 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tg22 run-m 29050 28081 test-own-v70-snapB-god-strong "$L/list-sy.txt"
tlb tg22; say "tg22 done"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg23 P1S="$O/mashfast_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh tg23 run-m 29050 28081 test-own-v70-snapB-god-strong "$L/list-sy.txt"
tlb tg23; say "tg23 done"
SN="5240,5280,5300,5310,5340,5400,5440,5480,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,8000,9500,11900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg24 P1S="$O/mash_new_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh tg24 run-m 29050 28081 test-own-v70-snapB-god-strong "$L/list-sy.txt"
tlb tg24; say "tg24 done"
say "chain76 through"
