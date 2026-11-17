#!/bin/bash
# TEST ONLY (tenth round, open item d): CALIBRATION for the walk-in tests: the heroes' object addresses on v132 in nm10 program 22
# (the toy cannon's elf) and al11 program 10 (the carpet escape's volume). No teleport; 6,000 frames; sp_probe.py.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; cd "$P" || exit 1
one() { ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5000,5500,5900" FRAMES=6000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$S/newgame_only.txt" P2S="$O/idle.txt" bash tools/own/sweep4.sh $1 $2 $3 $4 test-own-v132-snapB "$5"; }
one wcA run-x7 31950 28070 "$B/list-st-nm10.txt" &
one wcB run-x8 32150 28071 "$B/list-st-al11.txt" &
wait
