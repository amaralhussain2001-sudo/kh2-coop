#!/bin/bash
# TEST ONLY (tenth round, item 7 follow-up): eh25 program 0x59 (89) gave 2 fault lines "pc=0x19b2e8 addr=0x4" during its load on
# v137-snapB-god-cap (r10_chain54.sh nr1). Controls, 9,000 frames, the same jump and presses: nc1 x7 the no-twin build test-v32-a-nn,
# nc2 x8 test-own-v137 (no fight kit), nc3 x9 test-own-v134-snapB-god-cap (build 22's kit), nc4 x10 v137-snapB-god-cap again.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; B="$P/local/sweep/r9"; T="$P/tools/own"; cd "$P" || exit 1
lane() {
  ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe4.py" FROM=4700 TO=8900 SNAPS="5200,7000,8900" FRAMES=9000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$B/list-nrc.txt"
}
lane nc1 run-x7 31950 28070 test-v32-a-nn &
lane nc2 run-x8 32150 28071 test-own-v137 &
lane nc3 run-x9 32350 28072 test-own-v134-snapB-god-cap &
lane nc4 run-x10 32550 28073 test-own-v137-snapB-god-cap &
wait
