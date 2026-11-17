#!/bin/bash
# TEST ONLY (eighth round, fault F10): IS XIGBAR'S FAULT "BOTH PLAYERS PRESS THE SAME REACTION COMMAND AT ONCE"?
# Build 13 (v52), two heroes, the recorder at the paired-move routine (victim, move):
#   x15  only PLAYER 1 presses Triangle (player 2: Circle only)
#   x16  only PLAYER 2 presses Triangle (player 1: Circle only)
# and the same two with HP held and the action timeline (x17, x18): does the sniper part end?
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain47.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain47.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain47 start"
CS="5200,5600,6000,6400,6800,7200,7600,8000,8600,9200,10000,11000,11900"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x15 P1S="$O/mashrc_long_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh x15 run-m 29050 28081 test-own-v52-snapB-hp100s-cap "$L/list-xig.txt"
tlb x15; say "x15 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x16 P1S="$O/mash_new_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x16 run-m 29050 28081 test-own-v52-snapB-hp100s-cap "$L/list-xig.txt"
tlb x16; say "x16 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8x17 P1S="$O/mashrc_long_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh x17 run-m 29050 28081 test-own-v52-snapB-god-strong "$L/list-xig.txt"
tlb x17; say "x17 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8x18 P1S="$O/mash_new_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x18 run-m 29050 28081 test-own-v52-snapB-god-strong "$L/list-xig.txt"
tlb x18; say "x18 done"
say "chain47 through"
