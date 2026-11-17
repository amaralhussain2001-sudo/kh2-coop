#!/bin/bash
# TEST ONLY (eighth round, job 10: Xigbar's sniper part, Luxord's card trick), after the regression.
# Candidates: v52 (the regression's), v54 = v52 + glue 44 (capture form for the right hero) + glue 45 (a script's
# "the player" = the hero its object holds, in every runner).
#   x1    Xigbar (eh10 57), ONE hero (the jump disc without the twin), build 12: what the game's own sniper part does
#         to the hero (the recorder at the paired-move routine: victim, move, counter)
#   x2    the same fight, two heroes, candidate v52, the same recorder
#   x3    the same, candidate v54
#   x4    the same, candidate v54, HP held, the action timeline of both heroes (do they get out of the sniper part?)
#   lux6  Luxord (eh14 58), ONE hero, build 12, the recorder
#   lux7  Luxord, two heroes, candidate v54, the recorder
#   lux5  Luxord, two heroes, candidate v54, HP held, the action timeline; the fault lines kept
#   cap8  Shan-Yu, both press, candidate v54, the recorder (nothing may get worse)
#   gp15  Shan-Yu, player 2 alone with the fast mash, candidate v54
#   mkS4  Storm Rider, two Mickeys, candidate v54
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain40.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain40.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain40 start"
CS="5200,5600,6000,6400,6800,7200,7600,8000,8600,9200,10000,11000,11900"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
JUMPREC=01C562D0 ISO=test-s1-tt137solo.iso PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x1 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep5.sh x1 run-m 29050 28081 test-own-v33-snapB-hp100s-cap "$L/list-xig.txt"
tlb x1; say "x1 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x2 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x2 run-m 29050 28081 test-own-v52-snapB-hp100s-cap "$L/list-xig.txt"
tlb x2; say "x2 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x3 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x3 run-m 29050 28081 test-own-v54-snapB-hp100s-cap "$L/list-xig.txt"
tlb x3; say "x3 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8x4 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x4 run-m 29050 28081 test-own-v54-snapB-god-strong "$L/list-xig.txt"
tlb x4; say "x4 done"
JUMPREC=01C562D0 ISO=test-s1-tt137solo.iso PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8lux6 P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep5.sh lux6 run-m 29050 28081 test-own-v33-snapB-hp100s-cap "$L/list-lux.txt"
tlb lux6; say "lux6 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8lux7 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux7 run-m 29050 28081 test-own-v54-snapB-hp100s-cap "$L/list-lux.txt"
tlb lux7; say "lux7 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8lux5 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux5 run-m 29050 28081 test-own-v54-snapB-god-strong "$L/list-lux.txt"
tlb lux5; say "lux5 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap8 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap8 run-m 29050 28081 test-own-v54-snapB-def-cap "$L/list-sy.txt"
tlb cap8; say "cap8 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp15 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh gp15 run-m 29050 28081 test-own-v54-snapB-god-strong "$L/list-sy.txt"
tlb gp15; say "gp15 done"
M2="5200,6400,6700,6900,7000,7400,8000,8500,8900,9500,10000,11000,11900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$M2 FRAMES=12000 TOUT=400 SWEEP_PROBE_WAIT=400 LOGDIR=local/sweep/b15 TAG=r8mkS4 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS4 run-m 29050 28081 test-own-v54-snapB-kill65-roll-abort "$L/list-sr1.txt"
tlb mkS4; say "mkS4 done"
say "chain40 through"
