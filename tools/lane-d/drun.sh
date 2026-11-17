#!/bin/bash
# Lane D: one test run with the slot watcher attached through PINE (read-only).
# usage: drun.sh <name> <iso-in-local/iso> <patchDir> <frames> <snapFrames> <watchSeconds> <p1script> [then] [players] [p2script] [speed]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; pdir=$3; frames=$4; snaps=$5; secs=$6; script=$7; then=${8:-idle}; players=${9:-1}; script2=${10:-}; speed=${11:-2}
slots="0"; [ "$players" = "2" ] && slots="0,1"
extra=(); [ -n "$script2" ] && extra=(--script2 "$script2")
(python -I "$P/tools/kh2_session.py" run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" \
   --speed "$speed" --snap "$snaps" --script "$script" "${extra[@]}" --then "$then" --bot "$then" --fresh-card --pine 28041 \
   --run-dir run-d --port 28650 --patch-dir "$pdir" --timeout 400 --tail 3 > "$P/local/analysis/d/$name-harness.txt" 2>&1 &)
sleep 2
python -I "$P/tools/lane-d/slots.py" 28041 "$secs" --n 10 --out "$P/local/analysis/d/$name-slots.txt" > /dev/null 2>&1
sleep 6
tail -2 "$P/local/analysis/d/$name-harness.txt"
