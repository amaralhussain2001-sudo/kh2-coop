#!/bin/bash
# TEST ONLY: special-mode missions on a disc that has a second copy of every special player object
# (test-s1-tt137sp.iso and later). Each list line: "<name> <worldHex> <program> [area]" (with an area the jump is
# the Type 1 kind of tools/own/make_jumpkit1.py). Probe tools/own/sp_probe.py (both heroes' places and HP),
# 14 snapshots, a contact sheet. One result line per test in local/sweep/<log>.log.
# usage: bash tools/own/sp_batch.sh <ownPatchDir> <sandbox> <port> <pine> <log> <iso> <p1script> <p2script> <listFile>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
OWN=$1; RD=$2; PT=$3; PN=$4; LOG="$P/local/sweep/$5.log"; ISO=$6; S1=$7; S2=$8; LIST=$9
cd "$P" || exit 1
SN="4900,5250,5600,5900,6200,6500,6800,7100,7400,7700,8000,8300,8600,8900"
while read -r name w prog area; do
  [ -z "$name" ] && continue
  n="sp-$name"
  if [ -n "$area" ]; then
    python -I tools/own/make_jumpkit1.py "patches/$OWN" "patches/test-sp-$RD" "$w" "$area" "$prog" > /dev/null
  else
    python -I tools/own/make_jumpkit.py "patches/$OWN" "patches/test-sp-$RD" "$w" "$prog" > /dev/null
  fi
  out=$(PROBE="$P/tools/own/sp_probe.py" bash "$P/tools/own/dusk_one.sh" "$n" "patches/test-sp-$RD" "$ISO" 9000 "$SN" "$S1" "$S2" "$RD" "$PT" "$PN" 2>&1 | head -n 1)
  python "$P/tools/own/sheet.py" "$P/local/tests/$n" 300 > /dev/null 2>&1
  echo "$name $w $prog | $out" >> "$LOG"
  sed 's/^/    /' "$P/local/tests/$n-probe.txt" | cut -c1-240 >> "$LOG"
  grep "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt" 2>/dev/null | head -n 40 > "$P/local/tests/$n-emulog.txt"
done < "$LIST"
echo "sp batch done" >> "$LOG"
