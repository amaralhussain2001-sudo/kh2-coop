#!/bin/bash
# TEST ONLY (eighth round, faults F10 / F11): the runs of r8_chain48.sh once more on candidate v58 = v56 + "the hero
# it held less than 90 steps ago" in the forty-seventh glue and the step stamp of the sender note: x23 x24 (Xigbar), lux14 lux15 (Luxord), cap12 (Shan-Yu,
# both press: are the four stray calls gone?), xd12 (Data Xigbar), gp18 (Shan-Yu, player 2 alone must still win).
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain50.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain50.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain50 start"
CS="5200,5600,6000,6400,6800,7200,7600,8000,8600,9200,10000,11000,11900"
S4="5200,5600,6000,6500,7000,7500,8000,9000,10000,11000,11900"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8x23 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x23 run-m 29050 28081 test-own-v58-snapB-hp100s-cap "$L/list-xig.txt"
tlb x23; say "x23 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8x24 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh x24 run-m 29050 28081 test-own-v58-snapB-god-strong "$L/list-xig.txt"
tlb x24; say "x24 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=600 LOGDIR=local/sweep/b15 TAG=r8lux14 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux14 run-m 29050 28081 test-own-v58-snapB-hp100s-cap "$L/list-lux.txt"
tlb lux14; say "lux14 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS="5200,5300,5400,5600,6000,6500,6700,7000,7500,8000,9000,10000,11000,11900" FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8lux15 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh lux15 run-m 29050 28081 test-own-v58-snapB-god-strong "$L/list-lux.txt"
tlb lux15; say "lux15 done"
PROBE="$T/rec_probe.py" SNAPS=$CS FRAMES=12000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8cap12 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh cap12 run-m 29050 28081 test-own-v58-snapB-def-cap "$L/list-sy.txt"
tlb cap12; say "cap12 done"
PROBE="$T/act_poll_probe.py" FROM=4700 TO=11900 SNAPS=$S4 FRAMES=12000 TOUT=600 SWEEP_PROBE_WAIT=600 LOGDIR=local/sweep/b15 TAG=r8xd12 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh xd12 run-m 29050 28081 test-own-v58-snapB-god-strong "$L/list-xigd.txt"
tlb xd12; say "xd12 done"
LONG="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8gp18 P1S="$O/ctl_p1.txt" P2S="$O/mashfast_p2.txt" bash tools/own/sweep4.sh gp18 run-m 29050 28081 test-own-v58-snapB-god-strong "$L/list-sy.txt"
tlb gp18; say "gp18 done"
say "chain50 through"
