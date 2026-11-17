#!/bin/bash
# Lane H: one test run with the targeting recorder (hrec.py) attached through PINE.
# usage: hrun.sh <name> <iso-in-local/iso> <frames> <speed> <players> <p1script> <p2script|-> <then> <patchDir|-> <scanFrame> <endFrame> <windows|-> [snapFrames] [extra harness args...]
#   then = what both pads do after their script ends: idle | random
# Results: local/tests/<name>/ (logs, hrec.csv, rec.txt, harness.txt)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; players=$5; s1=$6; s2=$7; then=$8; pdir=$9; scan=${10}; endf=${11}; win=${12}; snaps=${13:-}
shift 13 2>/dev/null
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
mkdir -p "$T"
rm -f "$T/summary.txt" "$T/hrec.csv" "$T/rec.txt" "$T/harness.txt"
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --script "$s1" --then "$then" --bot "$then" --fresh-card --pine 28111 --run-dir run-h --port 29350
      --timeout 900 --tail 4)
[ "$pdir" != "-" ] && { [ -d "$pdir" ] || { echo "patch folder missing: $pdir"; exit 1; }; args+=(--patch-dir "$pdir"); }
[ "$s2" != "-" ] && args+=(--script2 "$s2")
[ -n "$snaps" ] && [ "$snaps" != "-" ] && args+=(--snap "$snaps")
(python -I "$P/tools/kh2_session.py" "${args[@]}" "$@" > "$T/harness.txt" 2>&1 &)
sleep 2
wargs=()
[ "$win" != "-" ] && wargs=(--windows "$win")
python -I "$P/tools/lane-h/hrec.py" "$T" 28111 "$scan" "$endf" "${wargs[@]}" > "$T/rec.txt" 2>&1
for i in $(seq 1 600); do [ -f "$T/summary.txt" ] && break; sleep 1; done
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -3
cat "$T/rec.txt"
