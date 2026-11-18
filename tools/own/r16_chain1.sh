#!/bin/bash
# TEST ONLY (partner's Drive display, part 150): dump both big gauges' parts in AL03_MS103 on build 32 (merged-v24-own).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
ISO=test-v5-tt137.iso PROBE="$P/tools/own/gauge_probe.py" SNAPS="6500,7000" FRAMES=7100 TOUT=1200 LOGDIR=local/sweep/r16 TAG=r16g \
  P1S="$O/snd_still_p1.txt" P2S="$O/snd_far_mash_p2.txt" bash tools/own/sweep4.sh g1 run-x5 31550 28068 merged-v24-own local/sweep/r15/list-al03.txt
echo "r16 chain1 done" >> local/sweep/r16/chain1.txt
