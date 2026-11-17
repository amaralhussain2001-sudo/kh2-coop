#!/bin/bash
# TEST ONLY (ninth round): DOES THE STORM RIDER MISSION (mu08 79) START? In runs kdC / keC / keD (candidates v101 / v102 with player 2's
# Keyblade = Oblivion) the picture stayed on the mission's opening scene. Four lanes, the same jump and scripts (attack only), 9,500 frames:
#  srA (run-m)    candidate v102, kit -snapB (both hold the Kingdom Key)
#  srB (run-v3)   BUILD 19's own-screen patch (test-own-v94-snapB): the control
#  srC (run-v3b)  candidate v102, kit -mk0 (player 2's Keyblade = Oblivion, written at 3800)
#  srD (run-v3c)  the item candidate v97, kit -snapB
# Logs local/sweep/r9/srA.log ..; progress chain12.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain12.txt"; }
say "chain12 start"
run() {  # run <worker> <sandbox> <port> <pine> <kit>
  ISO=test-v5-tt137.iso SNAPS="5200,6400,7400,8000,9000,9400" FRAMES=9500 TOUT=600 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashO_p1.txt" P2S="$O/mashO_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$L/list-sr1.txt"
  say "$1 done"
}
run srA run-m 29050 28081 test-own-v102-snapB &
run srB run-v3 30150 28061 test-own-v94-snapB &
run srC run-v3b 30350 28062 test-own-v102-mk0 &
run srD run-v3c 30550 28063 test-own-v97-snapB &
wait
say "chain12 through"
