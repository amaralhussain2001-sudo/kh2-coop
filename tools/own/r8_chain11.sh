#!/bin/bash
# TEST ONLY (eighth round): the candidate patches/test-own-v35 (base test-v8-b: glues 30, 31, 32 of merge_v7.py).
#   rv4  plan row 40: the revenge recorder on the candidate, Shan-Yu, both players hit. A hero's hit of 8 must
#        arrive as 6.0 (0.75); helpers' hits still add 8.
#   gu   plan row 43: the twin falls at 6500 in the 1000 Heartless (nobody there to heal him) and gets up by
#        himself 2,700 frames later: with 6 of 20 HP (one above the low-HP line), not 5. HP timeline.
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/rv4.log, gu.log
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
RV="5200,5600,6000,6400,6800,7200,7600,8000,8900,10000,11900"
PROBE="$T/sweepm_probe.py" RANGES=000F1FC0:20 SNAPS=$RV FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/b15 TAG=r8rv4 \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh rv4 run-m 29050 28081 test-own-v35-snapB-god-rev "$L/list-sy.txt"
echo "rv4 done $(date +%H:%M:%S)" >> "$B/chain11.txt"
PROBE="$T/hp_poll_probe.py" FROM=6400 TO=9900 SWEEP_PROBE_WAIT=900 SNAPS="5200,6600,9100,9300,9900" FRAMES=10000 TOUT=900 LOGDIR=local/sweep/b15 TAG=r8gu \
  P1S="$O/mash_new40_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh gu run-m 29050 28081 test-own-v35-snapB-def-kill65p2 "$L/list-hb17.txt"
echo "gu done $(date +%H:%M:%S)" >> "$B/chain11.txt"
echo "chain11 through $(date +%H:%M:%S)" >> "$B/chain11.txt"
