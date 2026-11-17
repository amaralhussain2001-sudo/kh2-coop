#!/bin/bash
# TEST ONLY: the mission sweep, fourth kind (seventh round, the sweep's tail). It is sweep2.sh (same list lines:
# "room worldHex program NAME party map battle event entrance", kit tools/own/make_jumpkit2.py) with four things
# that can be chosen:
#   SNAPS   the probe and picture frames            (default "5200,7000,8900"; early points show a short cup round)
#   P1S/P2S the two button scripts                  (default sweep_p1.txt / mash_long_p2.txt)
#   LOGDIR  where <worker>.log goes                 (default local/sweep; CONTROL RUNS MUST USE local/sweep/ctl,
#           because tools/own/sweep_doc.py reads every local/sweep/*.log as a result of the build)
#   TAG     the first part of the test's name       (default "sw"; controls: "swc")
#   FRAMES  frames of the run (default 9000); TOUT the wall-clock limit in seconds (default 420)
# The base patch folder can be patches/test-empty (the game with no patch: a control with one hero).
# The emulator's fault lines of player 1's PC are kept beside the pictures (<name>-emulog.txt); an old file of that
# name is removed first.
# usage: bash tools/own/sweep3.sh <worker> <sandbox> <port> <pine> <patchDirName> <listFile>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
W=$1; RD=$2; PT=$3; PN=$4; OWN=$5; LIST=$6
SN=${SNAPS:-5200,7000,8900}; S1=${P1S:-$O/sweep_p1.txt}; S2=${P2S:-$O/mash_long_p2.txt}; TG=${TAG:-sw}
LD="$P/${LOGDIR:-local/sweep}"; mkdir -p "$LD"; LOG="$LD/$W.log"
cd "$P" || exit 1
while read -r room w prog name party pm pb pe ent; do
  [ -z "$room" ] && continue
  n="$TG-$name-$prog"
  grep -q "^$room $w $prog " "$LOG" 2>/dev/null && continue
  python -I tools/own/make_jumpkit2.py "patches/$OWN" "patches/test-sweep3-$W" "$w" "$((10#${room:2}))" "$pm" "$pb" "$pe" "${ent:-0}" > /dev/null
  rm -rf "$P/local/tests/$n"; rm -f "$P/local/tests/$n-emulog.txt" "$P/local/tests/$n-probe.txt"
  (python -I "$P/tools/own/sweep_probe.py" "$P/local/tests/$n" "$PN" "$SN" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  r=$(OWN_RUN_DIR=$RD OWN_PORT=$PT bash "$P/tools/own/run_own2.sh" "$n" test-s1-tt137.iso "${FRAMES:-9000}" 4.0 "$SN" "$S1" "$S2" idle 1 "$P/patches/test-sweep3-$W" --pine "$PN" --timeout "${TOUT:-420}" 2>&1 | tail -1 | sed -E "s/^$n: //")
  sleep 2
  echo "$room $w $prog $name $party | $r | $(cat "$P/local/tests/$n-probe.txt" 2>/dev/null)" >> "$LOG"
  if grep -q "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt" 2>/dev/null; then grep "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt" | head -n 60 > "$P/local/tests/$n-emulog.txt"; fi
  if echo "$r" | grep -q "TIMED OUT\|^ *|"; then powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -match 'pcsx2' -and \$_.CommandLine -match '$RD[\\\\/]' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" > /dev/null 2>&1; sleep 2; fi
done < "$LIST"
echo "sweep worker $W done" >> "$LOG"
