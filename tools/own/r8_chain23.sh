#!/bin/bash
# TEST ONLY (eighth round, plan row 44 / fault F6): THE OBJECT FILE POOL with one and with two Drive Forms.
#   fp1  candidate v45 + kits -forms-heap-abort, the scripts of run tf2: the pool at 4690 (both normal), 5000 and 5540
#        (player 1 in Valor), 5590 / 5700 (player 2 has picked Wisdom; the game spins in the abort recorder from 5596)
#   fp2  build 12, player 2 ALONE in Wisdom (the scripts of run tfw): the pool with one form
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/fp1.log, fp2.log; progress chain23.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain23.txt"; }
say "chain23 start"
PROBE="$T/filepool_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-fp1 "$P/patches/test-own-v45-forms-heap-abort" test-s1-hb9f.iso 6000 "4690,5000,5540,5590,5700" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/fp1.log" 2>&1
cat "$P/local/tests/t15-fp1-probe.txt" >> "$B/fp1.log" 2>/dev/null
say "fp1 done"
PROBE="$T/filepool_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-fp2 "$P/patches/test-own-v33-forms-abort" test-s1-hb9f.iso 6000 "4690,5540,5700,5900" "$O/ctl_p1.txt" "$O/wisdom_p2.txt" run-m 29050 28081 > "$B/fp2.log" 2>&1
cat "$P/local/tests/t15-fp2-probe.txt" >> "$B/fp2.log" 2>/dev/null
say "fp2 done"
say "chain23 through"
