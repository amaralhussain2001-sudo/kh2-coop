#!/bin/bash
# Merge lane: one test run with lane E's memory check (tools/lane-e/cavecheck.py, read-only) attached through PINE.
# usage: mcave.sh <name> <iso-in-local/iso> <frames> <speed> <snapFrames> <players> <p1script> <p2script|-> <then> <patchDir|-> [cavecheck options...]
#   without a patch: reports anything the game itself puts into 0x000F0000-0x000F0FFF, and with --wide the 4 KB
#   blocks of 0x00080000-0x000FFFFF that hold data (this covers lane G's S2 block 0x000F1000-0x000F1AFF);
#   with a patch and --pnach <file>: reports words of 0x000F0000-0x000F0FFF that differ from the patch file.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; snaps=$5; players=$6; s1=$7; s2=$8; then=$9; pdir=${10}
shift 10
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
rm -rf "$T"; mkdir -p "$T"
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --snap "$snaps" --script "$s1" --then "$then" --bot "$then" --fresh-card --pine 28081 --run-dir run-m --port 29050
      --timeout 900 --tail 4)
[ "$s2" != "-" ] && args+=(--script2 "$s2")
[ "$pdir" != "-" ] && args+=(--patch-dir "$pdir")
(python -I "$P/tools/kh2_session.py" "${args[@]}" > "$T/harness.txt" 2>&1 &)
sleep 2
python -I "$P/tools/lane-e/cavecheck.py" "$T" 28081 "$snaps" "$@" > "$T/cave.txt" 2>&1
for i in $(seq 1 600); do [ -f "$T/summary.txt" ] && break; sleep 1; done
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -2
cat "$T/cave.txt"
