#!/bin/bash
# TEST ONLY (2026-11-13, tests-only session, the user: "try to do some tests it is everything is fine"): some of the
# smaller tests of the job list (register G5) on the build 12 candidate test-own-v33 + test kits. Clean jumps
# (map = battle = event = the program, finding T1). Logs in local/sweep/b14/ (NOT local/sweep/*.log).
#   lim0 / lim1  player 2 starts the first Limit in rooms with each of the 8 other guests (kit -limit), and once in a
#                room with no helper at all (mu08 104 NO_FRIEND)
#   fm           player 2's Drive Form in Halloween Town, Space Paranoids, Timeless River, Pride Lands (kit -forms)
#   far          the 1000 Heartless with player 2 far away for 3,600 frames (HP held, kit -snapB-god)
#   lion         player 2's lion falls at 6500 in Pride Lands (kit -snapB-kill65p2), player 1 goes on
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
L=local/sweep; B=local/sweep/b14; mkdir -p "$B"
SL="5200,5500,5800,6200,6800,7100,7900,8300,8900"
SF="5200,5600,5900,6400,7000,7300,8000,8900"
( SNAPS=$SL LOGDIR=$B TAG=s14l P2S="$O/lim_jump_p2.txt" bash tools/own/sweep3.sh lim0 run-m 29050 28081 test-own-v33-limit "$L/list-lim0.txt" ) &
( SNAPS=$SL LOGDIR=$B TAG=s14l P2S="$O/lim_jump_p2.txt" bash tools/own/sweep3.sh lim1 run-v3 30150 28061 test-own-v33-limit "$L/list-lim1.txt" ) &
( SNAPS=$SF LOGDIR=$B TAG=s14f P2S="$O/formjump_p2.txt" bash tools/own/sweep3.sh fm run-v3b 30350 28062 test-own-v33-forms "$L/list-fm.txt" ) &
(
  SNAPS="5200,6000,7000,8000,9000,10000,11000,11900" FRAMES=12000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=$B TAG=s14r \
    P1S="$O/mashrc_long_p1.txt" P2S="$O/farjump_p2.txt" bash tools/own/sweep3.sh far run-v3c 30550 28063 test-own-v33-snapB-god "$L/list-far.txt"
  SNAPS="5200,6400,6600,6800,7000,7400,8000,8900" LOGDIR=$B TAG=s14n \
    bash tools/own/sweep3.sh lion run-v3c 30550 28063 test-own-v33-snapB-kill65p2 "$L/list-lion.txt"
) &
wait
echo "tests s14 done $(date +%H:%M:%S)" >> "$B/s14-done.txt"
