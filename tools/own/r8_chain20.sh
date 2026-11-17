#!/bin/bash
# TEST ONLY (eighth round, register G5 and plan row 44): Final Form through the west door of Merlin's House.
#   ffd4  build 12 again (run ffd3 had ONE fault line: which address?), the whole emulator log kept
#   ffd5  candidate v44 (fortieth glue): Donald and Goofy must NOT stand in the new room while player 2 is in Final Form
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/finaldoor4.log, finaldoor5.log; progress chain20.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain20.txt"; }
say "chain20 start"
FS="4690,5000,5250,5380,5600,5800,6000,6100,6230,6260,6450,6630,6660,6900,7100,7350"
for kv in "finaldoor4 test-own-v33-forms" "finaldoor5 test-own-v44-forms"; do set -- $kv
  PROBE="$T/sweep_probe.py" bash tools/own/dusk_one.sh t15-$1 "$P/patches/$2" test-s1-hb13s.iso 7400 "$FS" "$O/finaldoor3_p1.txt" "$O/finaldoor3_p2.txt" run-m 29050 28081 > "$B/$1.log" 2>&1
  echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/$1.log"
  grep -a 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -20 >> "$B/$1.log"
  cat "$P/local/tests/t15-$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  say "$1 done"
done
say "chain20 through"
