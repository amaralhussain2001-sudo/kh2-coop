#!/bin/bash
# TEST ONLY (part 143, glue 80 --difficulty): the same two fights at difficulty 0 / 1 / 2 (candidate test-own-dh1, kit -snapB plus the
# difficulty patch line); probe tools/own/hp_probe.py lists every unit slot's entry id and maximum HP.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
one() { ISO=test-v5-tt137.iso PROBE="$P/tools/own/hp_probe.py" SNAPS="5200,6500,8000,9500" FRAMES=9600 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r13 TAG=r13$1 P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$P/local/sweep/r12/list-dh.txt"; }
one d0 run-x5 31550 28068 test-own-dh1-snapB-d0 &
one d1 run-x6 31750 28069 test-own-dh1-snapB-d1 &
one d2 run-x7 31950 28070 test-own-dh1-snapB-d2 &
wait
