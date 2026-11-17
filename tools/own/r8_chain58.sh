#!/bin/bash
# TEST ONLY (eighth round, job 11 = plan row 39, stage 1, step 1): candidate v59 = build 14 + the forty-eighth glue
# (--ownrec: the second hero's unit slot reads a character record T of his own, at first a full copy).
# NOTHING MAY CHANGE FOR THE PLAYERS IN THIS STEP.
#   or1    a fight (hb17 66, HP held): both slots' record pointers (slot + 0x244), stat words, record T beside Sora's
#   then the form / Game Over / heal / Limit tests of the regression (final_b9.sh a: 12 runs, names k9-*),
#   the Summon tests (final_b10.sh: 7 runs, names k10-*), and
#   mkS7   Storm Rider, both fall, a King Mickey for each (the rescue builds new bodies and slots)
# ONE RUN AT A TIME, hidden. Logs: local/sweep/b15/or1.log, local/final-b9-a.log, local/final-b10.log, mkS7.log
# (build 14's logs of final_b9 / final_b10 are saved in local/reg-b14/). Progress: local/sweep/b15/chain58.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain58.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain58 start"
PROBE="$T/sweepm_probe.py" CHAINS=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4,0034E948+48C@0:8,000F05CC+48C@0:8 RANGES=000E7D00:20,0032E020:20,000E7E20:4 SNAPS="5200,6000,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8or1 \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh or1 run-m 29050 28081 test-own-v59-snapB-god "$L/list-hb17.txt"
tlb or1; say "or1 done"
bash tools/own/final_b9.sh test-own-v59 run-v3c 30550 28063 a > /dev/null 2>&1
say "final_b9 a done"
bash tools/own/final_b10.sh test-own-v59 run-v3b 30350 28062 > /dev/null 2>&1
say "final_b10 done"
M3="5200,6400,6700,6900,7400,8000,9000,10000,11000,11500,11900,12100,12300,12500,12800,13200,13900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14,000E7E20:4 SNAPS=$M3 FRAMES=14000 TOUT=500 SWEEP_PROBE_WAIT=500 LOGDIR=local/sweep/b15 TAG=r8mkS7 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS7 run-m 29050 28081 test-own-v59-snapB-kill65-roll-abort "$L/list-sr1.txt"
tlb mkS7; say "mkS7 done"
say "chain58 through"
