#!/bin/bash
# Lane H: run several recorder tests one after the other and collect their summaries.
# usage: batch.sh <outfile-in-local/analysis/h> <patchDir> <prefix> <disc:testname[:frames[:p1script[:p2script[:then]]]]> ...
P="/c/Users/PC FORCE/Desktop/New folder (3)"
out="$P/local/analysis/h/$1"; pdir=$2; prefix=$3; shift 3
S="$P/tests/scripts/lane-h"
: > "$out"
for item in "$@"; do
  IFS=':' read -r disc name frames s1 s2 then <<< "$item"
  frames=${frames:-7200}; s1=${s1:-newgame_idle.txt}; s2=${s2:-idle.txt}; then=${then:-idle}
  endf=$((frames - 50))
  q=$(( (endf - 4700) / 4 ))
  W="a:4700-$((4700+q)),b:$((4700+q))-$((4700+2*q)),c:$((4700+2*q))-$((4700+3*q)),d:$((4700+3*q))-$endf"
  echo "=== $prefix-$name  ($disc, $frames frames, pads: $s1 / $s2, then $then)" >> "$out"
  "$P/tools/lane-h/hrun.sh" "$prefix-$name" "$disc" "$frames" 2 2 "$S/$s1" "$S/$s2" "$then" "$pdir" 4700 "$endf" "$W" "5000,6000,$((frames-200))" >> "$out" 2>&1
done
echo "BATCH DONE" >> "$out"
