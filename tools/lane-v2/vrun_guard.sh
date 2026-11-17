#!/bin/bash
# Lane V2: vrun.sh with a guard against a stalled session.
# usage: vrun_guard.sh <maxSeconds> <vrun.sh arguments...>
# If summary.txt is not there after maxSeconds, this lane's emulator copies (run-v2) are stopped and the last
# "stats" line of player 1's log is printed. Prints "RESULT: finished" or "RESULT: STALLED".
P="/c/Users/PC FORCE/Desktop/New folder (3)"
max=$1; shift
name=$1
T="$P/local/tests/$name"
(bash "$P/tools/lane-v2/vrun.sh" "$@" > "$P/local/tests/_guard_$name.txt" 2>&1 &)
sleep 5
for i in $(seq 1 "$max"); do [ -f "$T/summary.txt" ] && break; sleep 1; done
if [ -f "$T/summary.txt" ]; then
  echo "RESULT: finished"; grep -E "hashes compared|OUT OF SYNC" "$T/harness.txt" | head -2
  head -1 "$T/harness.txt" | grep -o "wall [0-9]* s"
else
  echo "RESULT: STALLED (no summary after $max s)"
  powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -and (\$_.CommandLine -like '*run-v2*' -or \$_.CommandLine -like '*$name*') -and \$_.Name -notlike 'powershell*' -and \$_.CommandLine -notlike '*vrun_guard*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -Confirm:\$false -ErrorAction SilentlyContinue }"
  sleep 3
  grep "stats: frame" "$T/p1.log" | tail -1 | cut -c1-160
  ls "$T" | grep -c png
fi
rm -f "$P/local/tests/_guard_$name.txt"
