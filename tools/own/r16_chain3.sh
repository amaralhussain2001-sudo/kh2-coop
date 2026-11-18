#!/bin/bash
# TEST ONLY (partner's Drive display, part 150): test-own-pd1 (make_own --partnerdrive) in AL03_MS103, pictures of both PCs.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
ISO=test-v5-tt137.iso PROBE="$P/tools/own/gauge_probe.py" SNAPS="6500,7000,7600,8200" FRAMES=8400 TOUT=1300 LOGDIR=local/sweep/r16 TAG=r16${1:-p} \
  P1S="$O/snd_still_p1.txt" P2S="$O/snd_far_mash_p2.txt" bash tools/own/sweep4.sh ${1:-p}1 run-x5 31550 28068 ${2:-test-own-pd1} local/sweep/r15/list-al03.txt
echo "r16 chain3 ${1:-p} done" >> local/sweep/r16/chain3.txt
