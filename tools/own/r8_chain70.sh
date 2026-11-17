#!/bin/bash
# TEST ONLY (eighth round, plan row 9's second half): the EXPERIMENT --together in its second form (candidate v65:
# Shan-Yu's room only; the second hero is noted, freed by the release rule, gets the command in his menu, and
# his press is sent as the first hero's). Shan-Yu, HP held, strong.
#   tg4  player 1 idle near the gate, player 2 fights with the fast mash: the second hero (player 1's) is pulled
#        into every clash: is he FREED after it, is "Press" in HIS menu too
#   tg5  player 1 presses ONLY Triangle, player 2 presses ONLY Circle: a push (0xFF) can come only from the second
#        hero's press: does it count
#   tg6  both press Circle and Triangle
# Read: the action timeline of both heroes (act_poll_probe.py) and a picture every 100 frames from 5500 to 7500.
# ONE RUN AT A TIME, hidden, sandbox run-m. Logs local/sweep/b15/tg4.log ..; progress chain70.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain70.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain70 start"
SN="5300,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,8000,9500,11900"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg4 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh tg4 run-m 29050 28081 test-own-v65-snapB-god-strong "$L/list-sy.txt"
tlb tg4; say "tg4 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg5 P1S="$O/tri_only_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh tg5 run-m 29050 28081 test-own-v65-snapB-god-strong "$L/list-sy.txt"
tlb tg5; say "tg5 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$SN FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8tg6 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh tg6 run-m 29050 28081 test-own-v65-snapB-god-strong "$L/list-sy.txt"
tlb tg6; say "tg6 done"
say "chain70 through"
