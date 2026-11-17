#!/bin/bash
# TEST ONLY (eighth round, faults F10 / F11): the runs of r8_chain48.sh once more on candidate v57 = v56 + "the hero
# it held less than 90 steps ago" in the forty-seventh glue: x21 x22 (Xigbar), lux12 lux13 (Luxord), cap11 (Shan-Yu,
# both press: are the four stray calls gone?), xd11 (Data Xigbar), gp17 (Shan-Yu, player 2 alone must still win).
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain49.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain49.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain49 start"
CS="5200,5600,6000,6400,6800,7200,7600,8000,8600,9200,10000,11000,11900"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x21 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x21 run-m 29050 28081 test-own-v57-snapB-hp100s-cap "$L/list-xig.txt"
tlb x21; say "x21 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8x22 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x22 run-m 29050 28081 test-own-v57-snapB-god-strong "$L/list-xig.txt"
tlb x22; say "x22 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8lux12 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux12 run-m 29050 28081 test-own-v57-snapB-hp100s-cap "$L/list-lux.txt"
tlb lux12; say "lux12 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5200,5300,5400,5600,6000,6500,6700,7000,7500,8000,9000,10000,11000,11900" FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8lux13 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux13 run-m 29050 28081 test-own-v57-snapB-god-strong "$L/list-lux.txt"
tlb lux13; say "lux13 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap11 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap11 run-m 29050 28081 test-own-v57-snapB-def-cap "$L/list-sy.txt"
tlb cap11; say "cap11 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8xd11 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh xd11 run-m 29050 28081 test-own-v57-snapB-god-strong "$L/list-xigd.txt"
tlb xd11; say "xd11 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp17 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh gp17 run-m 29050 28081 test-own-v57-snapB-god-strong "$L/list-sy.txt"
tlb gp17; say "gp17 done"
say "chain49 through"
