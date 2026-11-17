#!/bin/bash
# TEST ONLY: one run of an S1 test disc on the own-screen build with the room probe (layout byte at the snapshots;
# 0 = one view = a story scene plays).
# usage: dusk_one.sh <name> <patchDir> <iso> <frames> <snapFrames> <p1script> <p2script> [sandbox port pine]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
n=$1; pd=$2; iso=$3; fr=$4; FR=$5; s1=$6; s2=$7
RD=${8:-run-v3}; PT=${9:-30150}; PN=${10:-28061}
rm -rf "$P/local/tests/$n"
(python -I "${PROBE:-$P/tools/own/room_probe.py}" "$P/local/tests/$n" "$PN" "$FR" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
OWN_RUN_DIR=$RD OWN_PORT=$PT bash "$P/tools/own/run_own2.sh" "$n" "$iso" "$fr" 4.0 "$FR" "$s1" "$s2" "${OWN_THEN:-idle}" 1 "$pd" --pine "$PN" 2>&1 | tail -1 | cut -c1-110
sleep 3
echo "   $n: $(sed -E 's/frame ([0-9]+) room [0-9A-F]+ battle ([0-9A-F]+) layout ([0-9]+).*/\1:b\2:L\3/' "$P/local/tests/$n-probe.txt" | tr '\n' ' ')"
