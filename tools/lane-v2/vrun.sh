#!/bin/bash
# Lane V2: one sandbox test run, optionally with a probe program attached through PINE while it runs.
# usage: vrun.sh <name> <iso-in-local/iso> <frames> <speed> <snapFrames> <players> <p1script> <p2script|-> <then> <patchDir|-> [probe command words...]
#   then     = what the pads do after their script ends: idle | random
#   patchDir = "-" (no patch) or a folder with the .pnach
#   probe    = a command run after the emulators start (it gets no extra arguments), e.g.
#              python -I tools/lane-v2/hudtasks.py <testdir> 28181 5000 out.txt
# Results: local/tests/<name>/ (screenshots, logs, harness.txt, probe-console.txt)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; snaps=$5; players=$6; s1=$7; s2=$8; then=$9; pdir=${10}
shift 10
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
rm -rf "$T"; mkdir -p "$T"
if [ "$pdir" != "-" ] && [ ! -f "$pdir/SLPM-66675_F266B00B.pnach" ]; then echo "NO PATCH FILE in $pdir"; exit 1; fi
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --snap "$snaps" --script "$s1" --then "$then" --bot "$then" --fresh-card --pine 28181 --run-dir run-v2 --port 30050
      --timeout 1500 --tail 4)
[ "$s2" != "-" ] && args+=(--script2 "$s2")
[ "$pdir" != "-" ] && args+=(--patch-dir "$pdir")
[ -n "$V2_EE" ] && args+=(--ee-rate "$V2_EE")
(python -I "$P/tools/kh2_session.py" "${args[@]}" > "$T/harness.txt" 2>&1 &)
sleep 2
if [ $# -gt 0 ]; then "$@" > "$T/probe-console.txt" 2>&1; fi
for i in $(seq 1 1500); do [ -f "$T/summary.txt" ] && break; sleep 1; done
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -4
