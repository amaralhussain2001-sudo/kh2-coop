#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): the EXPERIMENT --together, TENTH form (candidate v73: the second copy does not step the boss's numbers; a pair
# is made only by a hook that comes from an enemy's own script and is not the answer to a hero's command).
#   tg30  player 1 presses ONLY Triangle, player 2 ONLY Circle: both in the clash, player 1's presses push
#   tg31  both press Circle and Triangle
#   tg32  player 1 ONLY Circle, player 2 ONLY Triangle (the roles the other way round)
#   tg33  player 1 idle near the gate, player 2 fast mash, 24,000 frames: is the fight won, is the gate destroyed
#   tg34  player 1 fast mash, player 2 idle, 24,000 frames: the same
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tg30.log ..; progress chain79.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain79.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
K=test-own-v73-snapB-god-strong
say "chain79 start"
SN="5240,5280,5300,5310,5340,5400,5440,5480,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,8000,9500,11900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg30 P1S="$O/tri_only_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh tg30 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg30; say "tg30 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg31 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh tg31 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg31; say "tg31 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg32 P1S="$O/mash_new_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh tg32 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg32; say "tg32 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg33 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tg33 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg33; say "tg33 done"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8tg34 P1S="$O/mashfast_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh tg34 run-m 29050 28081 $K "$L/list-sy.txt"
tlb tg34; say "tg34 done"
say "chain79 through"
