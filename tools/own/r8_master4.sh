#!/bin/bash
# TEST ONLY (eighth round): THE ONE QUEUE after r8_master3.sh (which ended when its list was done). Strictly one run
# after the other, in ONE shell. Start it with KH2_TEST_SHOW=1 to see the windows. Progress: local/sweep/b15/master4.txt
# It runs the chains named in local/sweep/b15/master4-more.txt (one chain number a line; the file must be there
# BEFORE the start) and reads that file again each time a chain ends. To add runs: a NEW chain file and its number
# into that list (temp file + mv). Never edit a chain that has started. The queue ends when the list is done.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/b15"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/master4.txt"; }
say "master4 start"
: > "$B/master4-done.txt"
while :; do
  next=""
  while read -r c; do
    [ -z "$c" ] && continue
    grep -qx "$c" "$B/master4-done.txt" || { next="$c"; break; }
  done < "$B/master4-more.txt"
  [ -z "$next" ] && break
  say "chain $next start"
  bash "tools/own/r8_chain$next.sh"
  echo "$next" >> "$B/master4-done.txt"
  say "chain $next done"
done
say "master4 through"
