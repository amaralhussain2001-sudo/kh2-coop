#!/bin/bash
# TEST ONLY (area sounds, part 149): candidate test-own-sn4 (--sound2 --sound2area, with the "move a0,s0" fix) in hb23 and hb25;
# compare with chain 3's controls r15ac23 / r15ac25 (snd_area_cmp.py).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN=$(seq -s, 6500 100 8400)
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/snd_probe.py" SNAPS="$SN" FRAMES=8600 TOUT=1500 LOGDIR=local/sweep/r15 TAG=r15$1 \
  P1S="$O/snd_still_p1.txt" P2S="$O/snd_far_mash_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 $6; }
one bn23 run-x6 31750 28069 test-own-sn4 local/sweep/r15/list-hb23.txt &
one bn25 run-x8 32150 28071 test-own-sn4 local/sweep/r15/list-hb25.txt &
wait
echo "r15 chain4 done" >> local/sweep/r15/chain4.txt
