#!/bin/bash
# TEST ONLY (eighth round): candidate v58, Storm Rider with two King Mickeys ONCE MORE AND LONGER (14,000 frames):
# run mkS5 ended at 12,000 while the rescue's end move (253, action 0xFD on both heroes) was still playing.
#   mkS6   both heroes fall at 6500, a King Mickey for each, the end of the rescue, the fight after it
# ONE RUN on sandbox run-m. Log: local/sweep/b15/mkS6.log; progress chain55.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain55.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain55 start"
M3="5200,6400,6700,6900,7400,8000,9000,10000,11000,11500,11900,12100,12300,12500,12800,13200,13900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$M3 FRAMES=14000 TOUT=500 SWEEP_PROBE_WAIT=500 LOGDIR=local/sweep/b15 TAG=r8mkS6 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkS6 run-m 29050 28081 test-own-v58-snapB-kill65-roll-abort "$L/list-sr1.txt"
tlb mkS6; say "mkS6 done"
say "chain55 through"
