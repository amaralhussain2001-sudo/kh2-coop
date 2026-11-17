#!/bin/bash
# TEST ONLY (eighth round, plan row 44 / fault F6): two Drive Forms at once with candidate v45 (thirty-fifth glue, second
# version: the form files are not let go while the other hero is in a form).
#   tf4   player 1 Valor at 4700, player 2 Wisdom at 5400, he reverts at 6400, player 1 at 6800, player 2 opens his list again
#         (heap recorder lines)
#   tf4b  the same with the post-mortem probe (only if something calls abort())
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/tf4.log, tf4b.log; progress chain21.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain21.txt"; }
say "chain21 start"
TF="4690,5000,5380,5450,5540,5600,5650,5700,5900,6300,6480,6600,6700,6780,6950,7100,7280,7400,7500"
PROBE="$T/heap_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tf4 "$P/patches/test-own-v45-forms-heap-abort" test-s1-hb9f.iso 7600 "$TF" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/tf4.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tf4.log"
cat "$P/local/tests/t15-tf4-probe.txt" >> "$B/tf4.log" 2>/dev/null
say "tf4 done"
PROBE="$T/abort_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tf4b "$P/patches/test-own-v45-forms-heap-abort" test-s1-hb9f.iso 7600 "$TF" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/tf4b.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tf4b.log"
cat "$P/local/tests/t15-tf4b-probe.txt" >> "$B/tf4b.log" 2>/dev/null
say "tf4b done"
say "chain21 through"
