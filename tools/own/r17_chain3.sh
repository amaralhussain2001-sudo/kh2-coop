#!/bin/bash
# TEST ONLY (part 151): THE FIRST TOWN again, with lane T's New Game script (skips the opening movie): merged-v26-own on the shipped
# disc (kh2-coop-v5); the partner's Drive strip must stay hidden there (the game hides the Drive gauge in the first town).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
PROBE="$P/tools/own/gauge_probe.py" bash tools/own/dusk_one.sh r17-town2 "$P/patches/merged-v26-own" kh2-coop-v5.iso 7600 6340,6912,7300,7550 \
  "$O/town_new_p1.txt" "$O/idle9000_p2.txt" run-x8 32150 28071 > local/sweep/r17/town2.log 2>&1
echo "r17 chain3 done" >> local/sweep/r17/chain1.txt
