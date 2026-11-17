#!/bin/bash
# TEST ONLY (2026-11-13): last two of the small tests: (1) a Limit in a room with NO helper (hb17 66 NO_FRIEND),
# HP held + Continue kit + Limit kit (test-own-v33-snapB-god-limit); (2) Pride Lands Drive Form retry with a picture
# of the Drive list (kit -forms, script formjump_lk_p2).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"
cd "$P" || exit 1
L=local/sweep; B=local/sweep/b14
SNAPS="5200,5500,5800,6200,6800,7100,7900,8300,8900" LOGDIR=$B TAG=s14d P2S="$O/lim_jump_p2.txt" bash tools/own/sweep3.sh d1 run-m 29050 28081 test-own-v33-snapB-god-limit "$L/list-l2n.txt" &
SNAPS="5200,6380,6530,6620,7000,7400,7750,8000,8900" LOGDIR=$B TAG=s14e P2S="$O/formjump_lk_p2.txt" bash tools/own/sweep3.sh d2 run-v3 30150 28061 test-own-v33-forms "$L/list-lion.txt" &
wait
echo "tests s14d done $(date +%H:%M:%S)" >> "$B/s14-done.txt"
