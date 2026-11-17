#!/bin/bash
# TEST ONLY: who scores in a skate challenge? Two runs per disc: only player 2 presses random buttons, then only
# player 1. Contact sheets in local/tests/x2-<name>-p2 / -p1. Log: local/v4-score-tests.log
# usage: bash tools/boards/score_tests.sh <ownPatchDir> <name> ...
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
PD=$1; shift
LOG="$P/local/v4-score-tests.log"
for n in "$@"; do
  OWN_THEN=random PROBE="$P/tools/own/party_probe.py" bash "$P/tools/own/dusk_one.sh" "x2-$n-p2" "$PD" "test-v4-$n.iso" 9000 "5400,6500,7500,8900" "$O/rules_p1.txt" "$O/rules_then_p2.txt" run-v3b 30350 28062 2>&1 | head -1 | cut -c1-110 >> "$LOG"
  OWN_THEN=random PROBE="$P/tools/own/party_probe.py" bash "$P/tools/own/dusk_one.sh" "x2-$n-p1" "$PD" "test-v4-$n.iso" 9000 "5400,6500,7500,8900" "$O/rules_then_p1.txt" "$O/idle.txt" run-v3b 30350 28062 2>&1 | head -1 | cut -c1-110 >> "$LOG"
  (cd "$P" && python tools/own/sheet.py "local/tests/x2-$n-p2" 520 > /dev/null 2>&1; python tools/own/sheet.py "local/tests/x2-$n-p1" 520 > /dev/null 2>&1)
done
echo "score tests done" >> "$LOG"
