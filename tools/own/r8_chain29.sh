#!/bin/bash
# TEST ONLY (eighth round, plan row 44): two Drive Forms at once, candidate v49 (glues 30 to 42, the measured needs).
#   tf6  Valor (player 1) + Wisdom (player 2); he reverts at 6400: ONLY Donald may come back; player 1 at 6800: Goofy too
#   tf7  Limit Form + Limit Form (the same files twice); player 2 reverts at 6400, player 1 at 6800
#   tf8  Limit Form (player 1) + Final (player 2); player 1 reverts at 6800 (the helpers must stay away), player 2 at 7200
# Heap recorder lines + the abort recorder in the kit. ONE RUN AT A TIME on sandbox run-m.
# Logs: local/sweep/b15/tf6.log .. tf8.log; progress chain29.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain29.txt"; }
say "chain29 start"
TF="4690,5000,5380,5540,5650,5700,5900,6300,6480,6600,6700,6780,6950,7100,7280,7400,7600,7900"
run() {  # name p1script p2script
  PROBE="$T/heap_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-$1 "$P/patches/test-own-v49-forms-heap-abort" test-s1-hb9f.iso 8000 "$TF" "$O/$2" "$O/$3" run-m 29050 28081 > "$B/$1.log" 2>&1
  echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/$1.log"
  cat "$P/local/tests/t15-$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  say "$1 done"
}
run tf6 twoforms_p1.txt twoforms_p2.txt
run tf7 limitf2_p1.txt limitf2_p2.txt
run tf8 limitf2_p1.txt finalf2_p2.txt
say "chain29 through"
