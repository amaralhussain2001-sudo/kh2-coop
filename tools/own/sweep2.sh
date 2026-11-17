#!/bin/bash
# TEST ONLY: the mission sweep, third kind (seventh round): list lines with their own map, battle and event
# programs and entrance ("room worldHex program NAME party map battle event entrance", made by
# tools/own/sweep_lists3.py; kit tools/own/make_jumpkit2.py). The rest is sweep1.sh, which is like sweep.sh, but
#   - the jump is a Type 1 jump into the mission's ROOM with the program number written into the save data
#     (tools/own/make_jumpkit1.py): for the programs the world's table does not know, and for reruns;
#   - the wall-clock limit is 420 seconds (sweep.sh: 200; slow missions ran into it);
#   - the emulator's log of player 1's PC is kept beside the pictures (<name>-emulog.txt) when it has fault lines.
# A list line: "room worldHex program NAME party" (the room's number is taken from its name: al14 = area 14).
# One result line per mission in local/sweep/<worker>.log (a mission already in THAT log is skipped).
# usage: bash tools/own/sweep2.sh <worker> <sandbox> <port> <pine> <ownPatchDirName> <listFile> [type2]
#   type2 = use the Type 2 jump of sweep.sh (make_jumpkit.py) with the longer limit (for reruns of slow missions)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
W=$1; RD=$2; PT=$3; PN=$4; OWN=$5; LIST=$6; KIND=${7:-type1}
LOG="$P/local/sweep/$W.log"
cd "$P" || exit 1
while read -r room w prog name party pm pb pe ent; do
  [ -z "$room" ] && continue
  n="sw-$name-$prog"
  grep -q "^$room $w $prog " "$LOG" 2>/dev/null && continue
  python -I tools/own/make_jumpkit2.py "patches/$OWN" "patches/test-sweep-$W" "$w" "$((10#${room:2}))" "$pm" "$pb" "$pe" "${ent:-0}" > /dev/null
  rm -rf "$P/local/tests/$n"
  (python -I "$P/tools/own/sweep_probe.py" "$P/local/tests/$n" "$PN" "5200,7000,8900" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  r=$(OWN_RUN_DIR=$RD OWN_PORT=$PT bash "$P/tools/own/run_own2.sh" "$n" test-s1-tt137.iso 9000 4.0 "5200,7000,8900" "$O/sweep_p1.txt" "$O/mash_long_p2.txt" idle 1 "$P/patches/test-sweep-$W" --pine "$PN" --timeout 420 2>&1 | tail -1 | sed -E "s/^$n: //")
  sleep 2
  echo "$room $w $prog $name $party | $r | $(cat "$P/local/tests/$n-probe.txt" 2>/dev/null)" >> "$LOG"
  if grep -q "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt" 2>/dev/null; then grep "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt" | head -n 60 > "$P/local/tests/$n-emulog.txt"; fi
  if echo "$r" | grep -q "TIMED OUT\|^ *|"; then powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -match 'pcsx2' -and \$_.CommandLine -match '$RD\\' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" > /dev/null 2>&1; sleep 2; fi
done < "$LIST"
echo "sweep worker $W done" >> "$LOG"
