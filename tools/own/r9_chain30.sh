#!/bin/bash
# TEST ONLY (ninth round, job 3): the mirror hero left in FC at the Dark Thorn (bb05 78 on v106, from 8150): his whole state with
# tools/own/hold_state_probe.py at 8100, 8160, 8200, 8260, 8320, 8400, 8900. One lane (run-m). usage: r9_chain30.sh [<own>] [<name>]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v106-snapB-god}; NM=${2:-dtA}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain30.txt"; }
say "chain30 start ($OWN, $NM)"
ISO=test-v5-tt137.iso PROBE="$T/hold_state_probe.py" SNAPS="8100,8160,8200,8260,8320,8400,8900" FRAMES=9000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$NM P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $NM run-m 29050 28081 "$OWN" "$B/list-bb05.txt"
say "$NM done"
