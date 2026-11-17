#!/bin/bash
# TEST ONLY (eighth round, job 7): enemy spawn zones react to player 2 (thirtieth glue, tools/merge/merge_v7.py).
# The Borough, entrance 2, battle program 1: a group of Heartless appears ahead of the heroes when "the hero" walks
# in. Player 1 only starts the game and stands still; player 2 runs forward alone at 4900.
#   sp1  the candidate patches/test-own-v34 (base test-v8-a): the enemies must appear (battle word 1 or 2)
#   sp0  build 12 (patches/test-own-v33): they must not (the control)
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/sp1.log, sp0.log
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain8.txt"; }
echo "hb09 04 1 HB09_ROAM DEFAULT 0 1 0 2" > "$L/list-sp.txt"
say "chain8 start"
SNAPS="4690,4880,5000,5100,5300,5600,6000,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8sp1 P1S="$O/ctl_p1.txt" P2S="$O/spawn2_p2.txt" \
  bash tools/own/sweep4.sh sp1 run-m 29050 28081 test-own-v35 "$L/list-sp.txt"
say "sp1 done"
SNAPS="4690,4880,5000,5100,5300,5600,6000,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8sp0 P1S="$O/ctl_p1.txt" P2S="$O/spawn2_p2.txt" \
  bash tools/own/sweep4.sh sp0 run-m 29050 28081 test-own-v33 "$L/list-sp.txt"
say "sp0 done"
say "chain8 through"
