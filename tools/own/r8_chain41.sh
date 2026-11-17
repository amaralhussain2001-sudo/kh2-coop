#!/bin/bash
# TEST ONLY (eighth round, job 12: the regression of v52). CONTROL RUNS WITH BUILD 12's kits for the two tests of
# regression step 6 whose numbers differ from build 11's saved log (build 12's own log of that step was not kept):
#   c12-formdie  a Game Over while player 2 is in a form, Continue (kit test-own-v33-formdie): where is the game at 12500?
#   c12-heal     whom Donald heals, the twin at 3 of 20 HP (kit test-own-v33-fheal)
# ONE RUN AT A TIME on sandbox run-v3c. Log: local/sweep/b15/chain41.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; B="$P/local/sweep/b15"
cd "$P" || exit 1
LOG="$B/chain41.txt"
echo "chain41 start $(date +%H:%M:%S)" >> "$LOG"
one() {  # name probe iso frames snaps p1 p2 patchDir
  PROBE="$P/tools/own/$2" bash "$P/tools/own/dusk_one.sh" "c12-$1" "$8" "$3" "$4" "$5" "$6" "$7" run-v3c 30550 28063 2>&1 | head -1 | cut -c1-105 >> "$LOG"
  cut -c1-420 "$P/local/tests/c12-$1-probe.txt" >> "$LOG"
}
one formdie drv_probe2.py test-m-roam.iso 12600 "6600,7400,8600,9400,12500" "$O/gocont2_p1.txt" "$O/formdie2_p2.txt" "$P/patches/test-own-v33-formdie"
one heal    heal_probe.py test-g-friends.iso 6000 "4850,4950,5050,5150,5250,5350" "$S/newgame_only.txt" "$O/idle.txt" "$P/patches/test-own-v33-fheal"
echo "chain41 through $(date +%H:%M:%S)" >> "$LOG"
