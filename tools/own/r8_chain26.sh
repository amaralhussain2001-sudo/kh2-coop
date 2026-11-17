#!/bin/bash
# TEST ONLY (eighth round, plan row 44 / fault F6): two Drive Forms at once with candidate v47 (forty-first glue: the second
# form's files go behind the files in use; a second form is refused only when the file pool has no room).
#   tf5   player 1 Valor at 4700, player 2 Wisdom at 5400, he reverts at 6400, player 1 at 6800, player 2 opens his list again
#   tf5p  the same with the file pool probe (where the files lie)
#   tf5a  the same with the post-mortem probe (only if something calls abort())
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/tf5.log, tf5p.log, tf5a.log; progress chain26.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain26.txt"; }
say "chain26 start"
TF="4690,5000,5380,5450,5540,5600,5650,5700,5900,6300,6480,6600,6700,6780,6950,7100,7280,7400,7500"
for kv in "tf5 heap_probe.py" "tf5p filepool_probe.py" "tf5a abort_probe.py"; do set -- $kv
  PROBE="$T/$2" LOW=4000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-$1 "$P/patches/test-own-v47-forms-heap-abort" test-s1-hb9f.iso 7600 "$TF" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/$1.log" 2>&1
  echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/$1.log"
  cat "$P/local/tests/t15-$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  say "$1 done"
done
say "chain26 through"
