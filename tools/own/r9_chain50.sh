#!/bin/bash
# TEST ONLY (ninth round, job 2 of the prompt of 2026-11-15): GUMMI ROUTE 8'S FIRST TRY on test patches, ONE RUN AFTER THE OTHER, hidden
# (the user is playing). 16,600 frames each: the score, the kills and both hulls at 8000 .. 16500 tell whether the
# flight is build 19's (17,849 / 31,609 / 43,299 points at 12000 / 14000 / 16000, ship 2's hull 155 at 14000) or
# build 20's (17,799 / 31,529 / 43,219; 175).
# usage: r9_chain50.sh <sandbox> <port> <pine> <ownPatchDirName> [<ownPatchDirName> ...]   (each needs its kit <own>-gum8)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S="$P/tests/scripts/lane-s3"; B="$P/local/sweep/r9"
RD=$1; PT=$2; PN=$3; shift 3
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain50.txt"; }
for OWN in "$@"; do
  n="g8-$OWN"
  say "$n start"
  out=$(PROBE="$P/tools/own/gummi_probe.py" bash "$P/tools/own/dusk_one.sh" "$n" "patches/$OWN-gum8" test-s1-tt137.iso 16600 "8000,10000,12000,14000,16000,16500" "$S/gb_p1_fight.txt" "$S/gb_p2_fight.txt" "$RD" "$PT" "$PN" 2>&1 | head -n 1)
  echo "$n | $out | TLB misses $(grep -c "TLB Miss" "$P/local/$RD/p1/logs/emulog.txt") | $(sed -n '3p;4p;5p' "$P/local/tests/$n-probe.txt" | grep -o 'score [0-9]*' | tr '\n' ' ') | $(sed -n '4p' "$P/local/tests/$n-probe.txt" | grep -o 'ship 2 hull [0-9]*')" >> "$B/chain50.log"
  say "$n done"
done
say "chain50 through"
