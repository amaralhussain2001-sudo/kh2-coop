#!/bin/bash
# TEST ONLY (eighth round, job 10, faults F10 / F11): candidate v56 = v54 + the forty-seventh glue (a hero's Reaction
# Command: the sender is "the player" of its callback; an object that holds one hero does not take the other
# hero's command). BOTH players press Circle and Triangle in the same frames (the fault case).
#   x19   Xigbar (eh10 57), the recorder at the paired-move routine (ONE capture at 4988?)
#   x20   the same, HP held, the action timeline of both heroes (does the sniper part end?)
#   lux10 Luxord (eh14 58), the recorder
#   lux11 the same, HP held, the action timeline + pictures (each trick whole on one hero?)
#   cap10 Shan-Yu, the recorder (are the four stray calls of the third clash gone?)
#   xd10  Data Xigbar (eh10 100), HP held, the action timeline
#   gp16  Shan-Yu, player 2 ALONE with the fast mash (he must still win)
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain48.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain48.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain48 start"
CS="5200,5600,6000,6400,6800,7200,7600,8000,8600,9200,10000,11000,11900"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x19 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x19 run-m 29050 28081 test-own-v56-snapB-hp100s-cap "$L/list-xig.txt"
tlb x19; say "x19 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8x20 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x20 run-m 29050 28081 test-own-v56-snapB-god-strong "$L/list-xig.txt"
tlb x20; say "x20 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8lux10 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux10 run-m 29050 28081 test-own-v56-snapB-hp100s-cap "$L/list-lux.txt"
tlb lux10; say "lux10 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5200,5300,5400,5600,6000,6500,6700,7000,7500,8000,9000,10000,11000,11900" FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8lux11 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux11 run-m 29050 28081 test-own-v56-snapB-god-strong "$L/list-lux.txt"
tlb lux11; say "lux11 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap10 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap10 run-m 29050 28081 test-own-v56-snapB-def-cap "$L/list-sy.txt"
tlb cap10; say "cap10 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8xd10 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh xd10 run-m 29050 28081 test-own-v56-snapB-god-strong "$L/list-xigd.txt"
tlb xd10; say "xd10 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp16 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh gp16 run-m 29050 28081 test-own-v56-snapB-god-strong "$L/list-sy.txt"
tlb gp16; say "gp16 done"
say "chain48 through"
