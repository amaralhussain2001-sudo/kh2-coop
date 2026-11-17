#!/bin/bash
# TEST ONLY (ninth round, job 4): THE GROUNDSHAKER'S CAUSE MADE ON PURPOSE ON v107: a stray capture FE of player 1's FREE hero at 8450, while
# player 2's hero rides (in run gsG the hero was in a move of his own at 8300, so the capture was made as the game does).
# It must NOT be made. One lane. usage: r9_chain36.sh [<own>] [<name>] [<sandbox> <port> <pine>]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v107-snapB-god-orph845}; NM=${2:-gsI}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain36.txt"; }
say "chain36 start ($OWN, $NM)"
ISO=test-v5-tt137.iso PROBE="$T/cap_log_probe2.py" FROM=4700 TO=13900 SNAPS="5200,8000,8500,9000,11000,13900" FRAMES=14000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$NM P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $NM ${3:-run-x5} ${4:-31550} ${5:-28068} "$OWN" "$L/list-lk15.txt"
say "$NM done"
