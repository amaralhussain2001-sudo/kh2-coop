#!/bin/bash
# TEST ONLY (ninth round, job 3): the last Xemnas (eh20 74): every object with an HP record (tools/own/enemy_probe.py), to find the
# boss's HP record. One lane (run-m), 6,200 frames. usage: r9_chain40.sh [<own>] [<name>] [<snaps>] [<frames>] [<probe>]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v107-snapB-god}; NM=${2:-xeA}; SN=${3:-5200,6000}; FR=${4:-6200}; PRB=${5:-enemy_probe.py}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain40.txt"; }
say "chain40 start ($OWN, $NM)"
ISO=test-v5-tt137.iso PROBE="$T/$PRB" FROM=4700 TO=$((FR - 100)) SNAPS="$SN" FRAMES=$FR TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/r9 TAG=r9$NM P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $NM ${6:-run-m} ${7:-29050} ${8:-28081} "$OWN" "$B/list-eh20.txt"
say "$NM done"
