#!/bin/bash
# TEST ONLY (ninth round, job 4): the stray capture at 8300 on v106 (run gsD: the weak pair ended after 60 steps, but player 1's hero
# was still in FE afterwards): the same run with tools/own/hold_state_probe.py every 20 frames from 8280 to 8560 and at 8700, 9000.
# One lane (run-x6). usage: r9_chain27.sh [<own>] [<name>]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v106-snapB-god-orph83}; NM=${2:-gsF}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain27.txt"; }
say "chain27 start ($OWN, $NM)"
SN=$(python -c "print(','.join(str(f) for f in range(8280, 8580, 20)) + ',8700,9000')")
ISO=test-v5-tt137.iso PROBE="$T/hold_state_probe.py" SNAPS="$SN" FRAMES=9100 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$NM P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh $NM run-x6 31750 28069 "$OWN" "$L/list-lk15.txt"
say "$NM done"
