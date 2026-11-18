#!/bin/bash
# TEST ONLY (sound per hero, 2026-11-18): the CONTROL. Build 31 (merged-v23-own), AL03_MS103, player 1 stands still,
# player 2 runs away and attacks; snd_probe reads the 3D sound list (volume +40, pan +44) and both listeners.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN=$(seq -s, 6500 100 8400)
ISO=test-v5-tt137.iso PROBE="$P/tools/own/snd_probe.py" SNAPS="$SN" FRAMES=8600 TOUT=1500 LOGDIR=local/sweep/r15 TAG=r15${1:-c} \
  P1S="$O/snd_still_p1.txt" P2S="$O/snd_far_mash_p2.txt" bash tools/own/sweep4.sh ${1:-sc} run-x5 31550 28068 ${2:-merged-v23-own} local/sweep/r15/list-al03.txt
echo "r15 chain1 ${1:-sc} done" >> local/sweep/r15/chain1.txt
