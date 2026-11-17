#!/bin/bash
# TEST ONLY (eighth round, register G5): the Samurai duel and the Large Body, fifth try, candidate v52, HP held,
# player 1 only starts the game, player 2 presses ONLY Triangle every 10 frames. Action timeline + pictures.
#   sam5  hb25, battle program 1: eight Samurai, the nearest 272 units from the heroes' place
#   lb5   he05, battle program 111 WITHOUT the mission's event program (so Auron and his Limit are not there):
#         one Large Body 304 units from the heroes' place
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/sam5.log, lb5.log; progress chain22.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain22.txt"; }
say "chain22 start"
S4="4800,5000,5200,5400,5600,5800,6000,6300,6600,7000,7500,8000,8500,9000,10000,11000,11900"
echo "hb25 04 1 HB25_ROAM NO_FRIEND 1 1 1 0" > "$L/list-hb25.txt"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8sam5 P1S="$O/ctl_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh sam5 run-m 29050 28081 test-own-v52-snapB-god "$L/list-hb25.txt"
say "sam5 done"
echo "he05 06 111 HE05_LB NO_FRIEND 111 111 0 0" > "$L/list-he05e.txt"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8lb5 P1S="$O/ctl_p1.txt" P2S="$O/tri_long_p2.txt" bash tools/own/sweep4.sh lb5 run-m 29050 28081 test-own-v52-snapB-god "$L/list-he05e.txt"
say "lb5 done"
say "chain22 through"
