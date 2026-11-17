#!/bin/bash
# TEST ONLY (2026-11-13): control: PLAYER 1 tries Drive in Pride Lands (lk14 55, kit -forms), player 2 idle.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
SNAPS="5200,6380,6530,6620,7000,7400,7750,8000,8900" LOGDIR=local/sweep/b14 TAG=s14g P1S="$O/formjump_lk_p1.txt" P2S="$O/idle.txt" \
  bash tools/own/sweep3.sh d3 run-m 29050 28081 test-own-v33-forms local/sweep/list-lion.txt
echo "tests s14e done $(date +%H:%M:%S)" >> local/sweep/b14/s14-done.txt
