#!/bin/bash
# TEST ONLY (ninth round, plan row 39, player 2's own Keyblade): THE FILE POOL IN EVERY MISSION with the Keyblade candidate (the hero's
# block of the pool is 256 KB bigger): the 302 missions of the seventh round's sweep on six lanes (run-x1 .. run-x6), disc v5's data,
# 7,100 frames each, looks at 5200 and 7000. Probe tools/own/kb_probe.py: "kept files end N of LIMIT (free F)".
# The question: is there a mission where the files that must stay do not fit (free < 0), and how much room is left for a Drive Form.
# usage: bash tools/own/r9_chain7.sh <ownPatchDirName>        logs local/sweep/r9/pool0.log .. pool5.log; progress chain7.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v100}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain7.txt"; }
say "chain7 start ($OWN)"
lane() {  # lane <k> <sandbox> <port> <pine>
  ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS="5200,7000" FRAMES=7100 LOGDIR=local/sweep/r9 TAG=r9pl bash tools/own/sweep6.sh pool$1 $2 $3 $4 "$OWN" "$B/list-pool-$1.txt"
  say "pool$1 done"
}
lane 0 run-x1 30750 28064 &
lane 1 run-x2 30950 28065 &
lane 2 run-x3 31150 28066 &
lane 3 run-x4 31350 28067 &
lane 4 run-x5 31550 28068 &
lane 5 run-x6 31750 28069 &
wait
say "chain7 through"
