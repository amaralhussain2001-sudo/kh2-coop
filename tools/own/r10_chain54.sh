#!/bin/bash
# TEST ONLY (tenth round, ITEM 7 of the user's list: the boss scripts that stand in no room file, docs\ROW9-PAIRED-MOVES.md "NO ROOM").
# Their makers (trap_sysobj_appear in the decoded AI, local\analysis\h\ai): B_AL110 / B_AL120 by the Twin Lords (al03 59); B_EX210 by
# Luxord (eh14 101 / 58); B_EX220 by B_EX160 (eh15 56) and B_EX250 (eh25 89 = program 0x59); B_EX220_LV99 by B_EX160_LV99 (eh15 102);
# B_EX410 by B_EX370 (Zexion, hb34 151). B_AL100_1ST / 2ND: no maker found; B_CA040_PUB: not in the object table.
# Build 23's fight kit test-own-v137-snapB-god-cap, both press (mashrc_long), 20,000 frames, probe cap_log_probe4.py (captures with
# the captor's object number + counts of the hidden objects). Lanes x7 .. x10 (the forks use run-m .. run-x6).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; T="$P/tools/own"; cd "$P" || exit 1
lane() {
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe4.py" FROM=4700 TO=19900 SNAPS="5200,8000,11000,14000,17000,19900" FRAMES=20000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9nr P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh nr$1 $2 $3 $4 test-own-v137-snapB-god-cap "$B/list-nr-r$1.txt"
}
lane 0 run-x7 31950 28070 &
lane 1 run-x8 32150 28071 &
lane 2 run-x9 32350 28072 &
lane 3 run-x10 32550 28073 &
wait
