#!/bin/bash
# Merge lane: one test run with the per-frame recorder (mrec.py) attached through PINE.
# usage: mrecrun.sh <name> <iso-in-local/iso> <frames> <speed> <players> <p1script> <p2script|-> <then> <patchDir> <scanFrame> <endFrame> <windows> [snapFrames]
# Results: local/tests/<name>/ (logs, rec.csv, rec.txt, harness.txt)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; players=$5; s1=$6; s2=$7; then=$8; pdir=$9; scan=${10}; endf=${11}; win=${12}; snaps=${13:-}
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
rm -rf "$T"; mkdir -p "$T"
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --script "$s1" --then "$then" --bot "$then" --fresh-card --pine 28081 --run-dir run-m --port 29050
      --timeout 900 --tail 4 --patch-dir "$pdir")
[ "$s2" != "-" ] && args+=(--script2 "$s2")
[ -n "$snaps" ] && args+=(--snap "$snaps")
(python -I "$P/tools/kh2_session.py" "${args[@]}" > "$T/harness.txt" 2>&1 &)
sleep 2
python -I "$P/tools/merge/mrec.py" "$T" 28081 "$scan" "$endf" --windows "$win" > "$T/rec.txt" 2>&1
for i in $(seq 1 600); do [ -f "$T/summary.txt" ] && break; sleep 1; done
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -3
cat "$T/rec.txt"
