#!/bin/bash
# TEST ONLY (eighth round): fault F6 once more, with the post-mortem probe (tools/own/abort_probe.py): WHICH object's
# motion resource is dead when the game calls abort() after player 2 picked Wisdom Form beside a Valor hero.
#   tfpm   candidate v38 (with the thirty-fifth glue), kit -forms-heap-abort, the scripts of run tf2
#   tfw    THE CONTROL: player 2 picks Wisdom ALONE (player 1 stays normal): build 12 + kit -forms + the recorder
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/tfpm.log, tfw.log; progress chain17.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain17.txt"; }
say "chain17 start"
PROBE="$T/abort_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tfpm "$P/patches/test-own-v38-forms-heap-abort" test-s1-hb9f.iso 6000 "4690,5540,5590,5700,5900" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/tfpm.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tfpm.log"
cat "$P/local/tests/t15-tfpm-probe.txt" >> "$B/tfpm.log" 2>/dev/null
say "tfpm done"
PROBE="$T/abort_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-tfw "$P/patches/test-own-v33-forms-abort" test-s1-hb9f.iso 6600 "4690,5540,5590,5700,5900,6300,6500" "$O/ctl_p1.txt" "$O/wisdom_p2.txt" run-m 29050 28081 > "$B/tfw.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/tfw.log"
cat "$P/local/tests/t15-tfw-probe.txt" >> "$B/tfw.log" 2>/dev/null
say "tfw done"
say "chain17 through"
