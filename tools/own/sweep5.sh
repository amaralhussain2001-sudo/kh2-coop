#!/bin/bash
# TEST ONLY: sweep4.sh + JUMPREC (the jump record address of another jump disc, hex; make_jumpkit3.py):
#   PROBE   the probe script                         (default tools/own/sweep_probe.py; heap runs: heap_probe.py)
#   ISO     the jump disc in local/iso               (default test-s1-tt137.iso; disc v5's data: test-v5-tt137.iso)
# Everything else as sweep3.sh: SNAPS, P1S/P2S, LOGDIR, TAG, FRAMES, TOUT, SWEEP_PROBE_WAIT; list lines
# "room worldHex program NAME party map battle event entrance". A probe that writes several lines is put on one
# line of the log (lines joined by " ; ").
# KH2_TEST_SHOW=1 in the environment shows the two emulator windows on the user's desktop.
# usage: bash tools/own/sweep4.sh <worker> <sandbox> <port> <pine> <patchDirName> <listFile>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
W=$1; RD=$2; PT=$3; PN=$4; OWN=$5; LIST=$6
SN=${SNAPS:-5200,7000,8900}; S1=${P1S:-$O/sweep_p1.txt}; S2=${P2S:-$O/mash_long_p2.txt}; TG=${TAG:-sw}
PR=${PROBE:-$P/tools/own/sweep_probe.py}; DISC=${ISO:-test-s1-tt137.iso}
LD="$P/${LOGDIR:-local/sweep/b15}"; mkdir -p "$LD"; LOG="$LD/$W.log"
cd "$P" || exit 1
while read -r room w prog name party pm pb pe ent; do
  [ -z "$room" ] && continue
  n="$TG-$name-$prog"
  grep -q "^$room $w $prog " "$LOG" 2>/dev/null && continue
  python -I tools/own/make_jumpkit3.py "patches/$OWN" "patches/test-sweep5-$W" "$w" "$((10#${room:2}))" "$pm" "$pb" "$pe" "${ent:-0}" > /dev/null
  rm -rf "$P/local/tests/$n"; rm -f "$P/local/tests/$n-emulog.txt" "$P/local/tests/$n-probe.txt"
  (python -I "$PR" "$P/local/tests/$n" "$PN" "$SN" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  r=$(OWN_RUN_DIR=$RD OWN_PORT=$PT bash "$P/tools/own/run_own2.sh" "$n" "$DISC" "${FRAMES:-9000}" 4.0 "$SN" "$S1" "$S2" idle 1 "$P/patches/test-sweep5-$W" --pine "$PN" --timeout "${TOUT:-420}" 2>&1 | tail -1 | sed -E "s/^$n: //")
  sleep 2
  echo "$room $w $prog $name $party | $r | $(tr '\n' ';' < "$P/local/tests/$n-probe.txt" 2>/dev/null | sed 's/;/ ; /g')" >> "$LOG"
  if grep -q "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt" 2>/dev/null; then grep "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt" | head -n 60 > "$P/local/tests/$n-emulog.txt"; fi
  if echo "$r" | grep -q "TIMED OUT\|^ *|"; then powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -match 'pcsx2' -and \$_.CommandLine -match '$RD[\\\\/]' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" > /dev/null 2>&1; sleep 2; fi
done < "$LIST"
echo "sweep worker $W done" >> "$LOG"
