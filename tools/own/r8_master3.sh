#!/bin/bash
# TEST ONLY (eighth round): THE ONE QUEUE after r8_master2.sh. Strictly one run after the other, in ONE shell.
# Start it with KH2_TEST_SHOW=1 to see the windows. Progress: local/sweep/b15/master3.txt
# To add runs while it is going: write a NEW chain file and name it in local/sweep/b15/master3-more.txt (one chain
# number a line); this script reads that file again each time a chain ends. Never edit a chain that has started.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/b15"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/master3.txt"; }
say "master3 start"
: > "$B/master3-done.txt"
echo 15 > "$B/master3-more.txt"
echo 16 >> "$B/master3-more.txt"
while :; do
  next=""
  while read -r c; do
    [ -z "$c" ] && continue
    grep -qx "$c" "$B/master3-done.txt" || { next="$c"; break; }
  done < "$B/master3-more.txt"
  [ -z "$next" ] && break
  say "chain $next start"
  bash "tools/own/r8_chain$next.sh"
  echo "$next" >> "$B/master3-done.txt"
  say "chain $next done"
done
say "master3 through"
