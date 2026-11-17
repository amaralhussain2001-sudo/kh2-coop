#!/bin/bash
# TEST ONLY: the quiet Borough with Donald and Goofy (disc test-s1-hb9f), player 2 runs far away; one run per
# variant folder; prints where the helpers are at the end. Log: local/<logname>.log
# usage: leader_bits.sh <logname> <patchDirName> [<patchDirName> ...]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
LOG="$P/local/$1.log"; shift
: > "$LOG"
for v in "$@"; do
  n="w-$v"
  PROBE="$P/tools/own/party_probe.py" bash "$P/tools/own/dusk_one.sh" "$n" "$P/patches/$v" test-s1-hb9f.iso 6400 "5200,6300" "$P/tests/scripts/merge/newgame_only.txt" "$P/tests/scripts/own/far_p2.txt" run-v3 30150 28061 2>&1 | head -1 | cut -c1-100 >> "$LOG"
  grep -A4 "frame 6300" "$P/local/tests/$n-probe.txt" | grep "heroes\|party [12]" | sed -E 's/class [0-9A-F]+ update [0-9A-F]+ //' | cut -c1-110 >> "$LOG"
done
echo "bits done" >> "$LOG"
