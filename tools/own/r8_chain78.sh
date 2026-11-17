#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): the EXPERIMENT --together, NINTH form (candidate v72: the second copy does not step the boss's numbers; a pair
# is made only by a hook that comes from an enemy's own script and is not the answer to a hero's command).
#   tg25  player 1 presses ONLY Triangle, player 2 ONLY Circle: both in the clash, player 1's presses push
#   tg26  both press Circle and Triangle
#   tg27  player 1 ONLY Circle, player 2 ONLY Triangle (the roles the other way round)
#   tg28  player 1 idle near the gate, player 2 fast mash, 24,000 frames: is the fight won, is the gate destroyed
#   tg29  player 1 fast mash, player 2 idle, 24,000 frames: the same
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tg25.log ..; progress chain78.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain78.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
K=test-own-v72-snapB-god-strong
say "chain78 start"
SN="5240,5280,5300,5310,5340,5400,5440,5480,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,8000,9500,11900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg25 P1S="$O/tri_only_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh tg25 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg25; say "tg25 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg26 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh tg26 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg26; say "tg26 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg27 P1S="$O/mash_new_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh tg27 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg27; say "tg27 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg28 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tg28 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg28; say "tg28 done"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg29 P1S="$O/mashfast_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh tg29 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg29; say "tg29 done"
say "chain78 through"
