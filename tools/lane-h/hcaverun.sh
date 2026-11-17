#!/bin/bash
# Lane H: one test run with the code-cave watcher (hcave.py) attached through PINE.
# usage: hcaverun.sh <name> <iso-in-local/iso> <frames> <speed> <players> <p1script> <p2script|-> <then> <patchDir|-> <checkFrames> [snapFrames]
#   without a patch folder: counts non-zero words in 0x000F2000-0x000F27FF (must stay 0 in the unpatched game);
#   with one: counts words that differ from the patch file (must stay 0) and shows this lane's variables.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
name=$1; iso=$2; frames=$3; speed=$4; players=$5; s1=$6; s2=$7; then=$8; pdir=$9; checks=${10}; snaps=${11:-}
slots="0"; [ "$players" = "2" ] && slots="0,1"
T="$P/local/tests/$name"
mkdir -p "$T"
rm -f "$T/summary.txt" "$T/cave.txt" "$T/harness.txt"
args=(run "$name" --iso "$P/local/iso/$iso" --players "$players" --slots "$slots" --frames "$frames" --speed "$speed"
      --script "$s1" --then "$then" --bot "$then" --fresh-card --pine 28111 --run-dir run-h --port 29350
      --timeout 900 --tail 4)
cargs=()
if [ "$pdir" != "-" ]; then
  [ -d "$pdir" ] || { echo "patch folder missing: $pdir"; exit 1; }
  args+=(--patch-dir "$pdir"); cargs=(--pnach "$pdir/SLPM-66675_F266B00B.pnach")
fi
[ "$s2" != "-" ] && args+=(--script2 "$s2")
[ -n "$snaps" ] && args+=(--snap "$snaps")
(python -I "$P/tools/kh2_session.py" "${args[@]}" > "$T/harness.txt" 2>&1 &)
sleep 2
python -I "$P/tools/lane-h/hcave.py" 28111 "$checks" "${cargs[@]}" > "$T/cave.txt" 2>&1
for i in $(seq 1 900); do [ -f "$T/summary.txt" ] && break; sleep 1; done
grep -E "session closed|OUT OF SYNC|TIMED OUT|refused" "$T/harness.txt" | head -3
cat "$T/cave.txt"
if [ -n "$snaps" ] && [ "$players" = "2" ]; then
  same=0; diff=0
  for f in "$T"/p1_f*.png; do b=$(basename "$f"); g="$T/p2_${b#p1_}"; [ -f "$g" ] || continue
    if [ "$(sha1sum < "$f")" = "$(sha1sum < "$g")" ]; then same=$((same+1)); else diff=$((diff+1)); fi; done
  echo "screenshot pairs identical: $same, different: $diff"
fi
