#!/bin/bash
# TEST ONLY (sound per hero, 2026-11-18): AREA sounds (kind 4) - Port Royal harbour CA01_MS101 (list-ca51), control build 31
# (run-x6) and candidate test-own-sn1 (run-x7) side by side; same scripts as chain 1.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN=$(seq -s, 6500 100 8400)
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/snd_probe.py" SNAPS="$SN" FRAMES=8600 TOUT=1500 LOGDIR=local/sweep/r15 TAG=r15$1 \
  P1S="$O/snd_still_p1.txt" P2S="$O/snd_far_mash_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 local/sweep/r9/list-ca51.txt; }
one pc run-x6 31750 28069 merged-v23-own &
one pn run-x7 31950 28070 test-own-sn1 &
wait
echo "r15 chain2 done" >> local/sweep/r15/chain2.txt
