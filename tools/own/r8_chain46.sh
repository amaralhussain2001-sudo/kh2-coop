#!/bin/bash
# TEST ONLY (eighth round, fault F10): WHO MAKES XIGBAR'S SECOND CAPTURE? Build 13 (v52), two heroes, the recorder
# at the paired-move routine 0x00180378 with the STACK kept at call 2 (the twin's 0xFC at 4988), call 3 (0xFD at
# 5048) and call 4 (the first 0xFF); and once with the CAPTOR in the ring (a0 = the captor's motion part, a1 = the victim).
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress chain46.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain46.txt"; }
say "chain46 start"
for n in 2 3 4; do
  PROBE="$T/rec_probe.py" SNAPS="5200,5400,5900" FRAMES=6000 TOUT=400 LOGDIR=local/sweep/b15 TAG=r8xn$n P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh xn$n run-m 29050 28081 test-own-v52-snapB-hp100s-capn$n "$L/list-xig.txt"
  say "xn$n done"
done
PROBE="$T/rec_probe.py" SNAPS="5200,5400,5900" FRAMES=6000 TOUT=400 LOGDIR=local/sweep/b15 TAG=r8xc P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh xc run-m 29050 28081 test-own-v52-snapB-hp100s-capc "$L/list-xig.txt"
say "xc done"
say "chain46 through"
