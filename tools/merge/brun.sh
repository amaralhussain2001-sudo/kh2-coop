#!/bin/bash
# Boss check for the merged build: a run on a boss jump disc with the unit-slot watcher (lane B75's slots_watch.py)
# attached through PINE. Uses lane B75's emulator copies (local/run-b75, port 30250, PINE 28201), so it can run
# beside the combined suite (local/run-m).
# usage: brun.sh <name> <iso-in-local/iso> <frames> <speed> <snapFrames> <players> <p1script> <p2script|-> <then> <patchDir> [watcher options...]
#   then = idle | random (what both pads do after their scripts)
#   watcher options: none = READ ONLY (allowed with two linked copies).
#                    --boost-heroes N, --set, --setmax = memory writes: ONE-COPY TESTS ONLY.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; snaps=$5; players=$6; s1=$7; s2=$8; then=$9; pdir=${10}
shift 10
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
rm -rf "$T"; mkdir -p "$T"
python -I "$P/tools/lane-b75/slots_watch.py" 28201 600 "$T/slots.tsv" "$@" > "$T/watch.out" 2>&1 &
WP=$!
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --snap "$snaps" --script "$s1" --then "$then" --bot "$then" --fresh-card --pine 28201 --run-dir run-b75 --port 30250
      --timeout 900 --tail 4 --patch-dir "$pdir")
[ "$s2" != "-" ] && args+=(--script2 "$s2")
python -I "$P/tools/kh2_session.py" "${args[@]}" > "$T/harness.txt" 2>&1
kill $WP 2>/dev/null; wait $WP 2>/dev/null
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -4
a=0; b=0
for f in "$T"/p1_f*.png; do
  g="${f/p1_f/p2_f}"; b=$((b+1))
  [ -f "$g" ] && [ "$(sha1sum "$f" | cut -c1-40)" = "$(sha1sum "$g" | cut -c1-40)" ] && a=$((a+1))
done
echo "screenshots p1: $b, pairs identical: $a; different p1 pictures: $(cd "$T" && md5sum p1_f*.png 2>/dev/null | awk '{print $1}' | sort -u | wc -l)"
echo "emulator log, TLB misses p1: $(grep -c 'TLB Miss' "$P/local/run-b75/p1/logs/emulog.txt" 2>/dev/null)"
echo "--- slots (first 12 lines with a battle, then last 3)"
awk -F'\t' '$3==1' "$T/slots.tsv" | head -12
tail -3 "$T/slots.tsv"
