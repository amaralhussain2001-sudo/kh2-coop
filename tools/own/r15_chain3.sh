#!/bin/bash
# TEST ONLY (area sounds, 2026-11-18, part 149): the only two rooms with area-sound faces (tools/sound-areas): hb23 and hb25 (map
# program 0). Control merged-v24-own (build 32, sn_view only) and candidate test-own-sn3 (+ --sound2area) in each room.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN=$(seq -s, 6500 100 8400)
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/snd_probe.py" SNAPS="$SN" FRAMES=8600 TOUT=1500 LOGDIR=local/sweep/r15 TAG=r15$1 \
  P1S="$O/snd_still_p1.txt" P2S="$O/snd_far_mash_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 $6; }
one ac23 run-x5 31550 28068 merged-v24-own local/sweep/r15/list-hb23.txt &
one an23 run-x6 31750 28069 test-own-sn3 local/sweep/r15/list-hb23.txt &
one ac25 run-x7 31950 28070 merged-v24-own local/sweep/r15/list-hb25.txt &
one an25 run-x8 32150 28071 test-own-sn3 local/sweep/r15/list-hb25.txt &
wait
echo "r15 chain3 done" >> local/sweep/r15/chain3.txt
