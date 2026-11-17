#!/bin/bash
# TEST ONLY (eighth round, plan row 45): WHAT THE GAME DOES WHEN KING MICKEY'S HP REACHES 0. Run mkD (two Mickeys) left both
# standing at 0 / 60 for 8,000 frames with no Game Over. mkE = THE CONTROL: the same kit on the build with ONE Mickey
# (candidate v51m1, option --mickey1), player 1 plays him.
# ONE RUN on sandbox run-m. Log: local/sweep/b15/mkE.log (+ mkE-tlb.txt); progress chain34.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain34.txt"; }
say "chain34 start"
MS="5200,6400,6700,6900,7000,7400,7700,7900,8000,8100,8200,8400,8700,9000,9500,10000,10400,10700,10900,11000,11400,12000,13000,14000,15000,15900"
PROBE="$T/sweepm_probe.py" RANGES=0034E948:8,000F05CC:4,000E7C00:4,000E7100:14 SNAPS=$MS FRAMES=16000 TOUT=400 SWEEP_PROBE_WAIT=400 LOGDIR=local/sweep/b15 TAG=r8mkE P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh mkE run-m 29050 28081 test-own-v51m1-snapB-kill65-roll-abort-mk80 "$L/list-sy.txt"
grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -80 > "$B/mkE-tlb.txt"
say "mkE done"
say "chain34 through"
