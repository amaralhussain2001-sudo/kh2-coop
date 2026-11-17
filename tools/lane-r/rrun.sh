#!/bin/bash
# Lane R (copy of the merge lane runner): one test run with the probe attached through PINE.
# usage: mrun.sh <name> <iso-in-local/iso> <frames> <speed> <snapFrames> <players> <p1script> <p2script|-> <then> [patchDir|-|default] [probe options...]
#   then      = what both pads do after their script ends: idle | random
#   patchDir  = "default" (patches/lane-r-x3), "-" (no patch) or a folder
# Results: local/tests/<name>/ (screenshots, logs, probe.txt, harness.txt)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; snaps=$5; players=$6; s1=$7; s2=$8; then=$9; pdir=${10:-default}
shift 10 2>/dev/null
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
rm -rf "$T"; mkdir -p "$T"
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --snap "$snaps" --script "$s1" --then "$then" --bot "$then" --fresh-card --pine 28131 --run-dir run-r --port 29550
      --timeout 900 --tail 4)
[ "$s2" != "-" ] && args+=(--script2 "$s2")
if [ "$pdir" = "default" ]; then args+=(--patch-dir "$P/patches/lane-r-x3"); elif [ "$pdir" != "-" ]; then args+=(--patch-dir "$pdir"); fi
(python -I "$P/tools/kh2_session.py" "${args[@]}" > "$T/harness.txt" 2>&1 &)
sleep 2
python -I "$P/tools/merge/mprobe.py" "$T" 28131 "$snaps" --timeout 880 "$@" > "$T/probe-console.txt" 2>&1
# wait for the harness to finish (summary.txt appears)
for i in $(seq 1 600); do [ -f "$T/summary.txt" ] && break; sleep 1; done
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -4
