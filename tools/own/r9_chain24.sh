#!/bin/bash
# TEST ONLY (ninth round, job 5), one lane (run-x4): cnD = the toy cannon on v103 + --cannon2view (third form) with tools/own/cam_probe.py:
# what the two cameras are while the cannon game runs (kinds, targets, places). 9,000 frames. usage: r9_chain24.sh [<own>] [<name>]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v103e-snapB}; NM=${2:-cnD}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain24.txt"; }
say "chain24 start ($OWN, $NM)"
ISO=test-v5-tt137.iso PROBE="$T/cam_probe.py" SNAPS="5200,6000,6500,7000,7500,8000,8900" FRAMES=9000 TOUT=900 SWEEP_PROBE_WAIT=900 LOGDIR=local/sweep/r9 TAG=r9$NM P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh $NM run-x4 31350 28067 "$OWN" "$L/list-nm63.txt"
say "$NM done"
