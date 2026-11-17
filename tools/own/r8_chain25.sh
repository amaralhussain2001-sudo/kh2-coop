#!/bin/bash
# TEST ONLY (eighth round, plan row 44): HOW MUCH OF THE OBJECT FILE POOL EACH DRIVE FORM NEEDS. Build 12 + kit -forms,
# player 2 alone takes Limit Form (fp3), Master (fp4), Final (fp5); the pool before (4690) and after (5900).
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/fp3.log .. fp5.log; progress chain25.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain25.txt"; }
say "chain25 start"
for kv in "fp3 limitf" "fp4 masterf" "fp5 finalf"; do set -- $kv
  PROBE="$T/filepool_probe.py" LOW=3000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-$1 "$P/patches/test-own-v33-forms-abort" test-s1-hb9f.iso 6000 "4690,5900" "$O/ctl_p1.txt" "$O/$2_p2.txt" run-m 29050 28081 > "$B/$1.log" 2>&1
  cat "$P/local/tests/t15-$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  say "$1 done"
done
say "chain25 through"
