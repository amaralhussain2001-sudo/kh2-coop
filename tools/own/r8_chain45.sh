#!/bin/bash
# TEST ONLY (eighth round, job 10, faults F10 / F11): candidate v55 = v54 + the forty-sixth glue (a script's "the
# player" = the held hero, else the hero held a moment ago, else THE NEARER hero, in every runner; Luxord's card /
# die asks the same routine).
#   x9    Xigbar (eh10 57), two heroes, v55, the recorder at the paired-move routine (one capture, as with one hero?)
#   x10   the same, HP held, the action timeline of both heroes (does the sniper part end?)
#   lux8  Luxord (eh14 58), two heroes, v55, the recorder
#   lux9  the same, HP held, the action timeline
#   cap9  Shan-Yu, both press, v55, the recorder (nothing may get worse)
#   xd9   Data Xigbar (eh10 100), v55, HP held, the action timeline
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain45.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain45.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain45 start"
CS="5200,5600,6000,6400,6800,7200,7600,8000,8600,9200,10000,11000,11900"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x9 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x9 run-m 29050 28081 test-own-v55-snapB-hp100s-cap "$L/list-xig.txt"
tlb x9; say "x9 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8x10 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x10 run-m 29050 28081 test-own-v55-snapB-god-strong "$L/list-xig.txt"
tlb x10; say "x10 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8lux8 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux8 run-m 29050 28081 test-own-v55-snapB-hp100s-cap "$L/list-lux.txt"
tlb lux8; say "lux8 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8lux9 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux9 run-m 29050 28081 test-own-v55-snapB-god-strong "$L/list-lux.txt"
tlb lux9; say "lux9 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap9 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap9 run-m 29050 28081 test-own-v55-snapB-def-cap "$L/list-sy.txt"
tlb cap9; say "cap9 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8xd9 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh xd9 run-m 29050 28081 test-own-v55-snapB-god-strong "$L/list-xigd.txt"
tlb xd9; say "xd9 done"
say "chain45 through"
