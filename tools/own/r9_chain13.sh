#!/bin/bash
# TEST ONLY (ninth round): WHICH PART OF THE KEYBLADE GLUE KEEPS THE STORM RIDER MISSION IN ITS OPENING SCENE (run srC)? Candidate v102,
# player 2's Keyblade = Oblivion, the same jump and scripts; one routine switched off in each lane (kits made with make_reword.py):
#  srG (run-m)  without kb_fix     srH (run-v3)  without kb_rec     srI (run-v3b)  without kb_ctor
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain13.txt"; }
say "chain13 start"
run() {  # run <worker> <sandbox> <port> <pine> <kit>
  ISO=test-v5-tt137.iso SNAPS="5200,6400,7400" FRAMES=7500 TOUT=600 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashO_p1.txt" P2S="$O/mashO_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$L/list-sr1.txt"
  say "$1 done"
}
run srG run-m 29050 28081 test-own-v102-mk0-nofix &
run srH run-v3 30150 28061 test-own-v102-mk0-norec &
run srI run-v3b 30350 28062 test-own-v102-mk0-noctor &
wait
say "chain13 through"
