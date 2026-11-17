#!/bin/bash
# TEST ONLY: the mission sweep (seventh round). Every line of a list file "room worldHex program NAME party" is one
# run on the jump disc test-s1-tt137 with a jump kit (tools/own/make_jumpkit.py): New Game jumps into that mission
# program; player 1 presses Circle now and then, player 2 presses Circle all the time; 9,000 frames.
# One result line per mission in local/sweep/<worker>.log. Pictures: local/tests/sw-<NAME>-<program>/.
# usage: bash tools/own/sweep.sh <worker> <sandbox> <port> <pine> <ownPatchDirName> <listFile>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
W=$1; RD=$2; PT=$3; PN=$4; OWN=$5; LIST=$6
LOG="$P/local/sweep/$W.log"
cd "$P" || exit 1
while read -r room w prog name party; do
  [ -z "$room" ] && continue
  n="sw-$name-$prog"
  grep -q "^$room $w $prog " "$LOG" 2>/dev/null && continue
  python -I tools/own/make_jumpkit.py "patches/$OWN" "patches/test-sweep-$W" "$w" "$prog" > /dev/null
  rm -rf "$P/local/tests/$n"
  (python -I "$P/tools/own/sweep_probe.py" "$P/local/tests/$n" "$PN" "5200,7000,8900" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  r=$(OWN_RUN_DIR=$RD OWN_PORT=$PT bash "$P/tools/own/run_own2.sh" "$n" test-s1-tt137.iso 9000 4.0 "5200,7000,8900" "$O/sweep_p1.txt" "$O/mash_long_p2.txt" idle 1 "$P/patches/test-sweep-$W" --pine "$PN" --timeout 200 2>&1 | tail -1 | sed -E "s/^$n: //")
  sleep 2
  echo "$room $w $prog $name $party | $r | $(cat "$P/local/tests/$n-probe.txt" 2>/dev/null)" >> "$LOG"
  if echo "$r" | grep -q "TIMED OUT\|^ *|"; then powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -match 'pcsx2' -and \$_.CommandLine -match '$RD\\' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" > /dev/null 2>&1; sleep 2; fi
done < "$LIST"
echo "sweep worker $W done" >> "$LOG"
