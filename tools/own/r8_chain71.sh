#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): the EXPERIMENT --together in its THIRD form (candidate v66:
# Shan-Yu's room only; when the boss's script hooks its "hero side" script onto one hero, the other hero, when he is
# near, gets HIS OWN COPY of that hooked script; captures made by the boss's own script are copied to him; both
# heroes of the pair may press). Shan-Yu, HP held, strong.
#   tg7  player 1 presses ONLY Triangle, player 2 presses ONLY Circle (as tg5): is "Press" in the second hero's
#        menu now, does HIS press push (0xFF), does his move end by itself (no stiff pose)
#   tg8  both press Circle and Triangle (as tg6)
#   tg9  player 1 idle near the gate, player 2 fights with the fast mash (as tg4): the idle second hero
# Read: the action timeline of both heroes (act_poll_probe.py) and a picture every 100 frames from 5500 to 7500.
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tg7.log ..; progress chain71.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain71.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain71 start"
SN="5300,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,8000,9500,11900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg7 P1S="$O/tri_only_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh tg7 run-m 29050 28081 test-own-v66-snapB-god-strong "$L/list-sy.txt"
tlb tg7; say "tg7 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg8 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh tg8 run-m 29050 28081 test-own-v66-snapB-god-strong "$L/list-sy.txt"
tlb tg8; say "tg8 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg9 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tg9 run-m 29050 28081 test-own-v66-snapB-god-strong "$L/list-sy.txt"
tlb tg9; say "tg9 done"
say "chain71 through"
