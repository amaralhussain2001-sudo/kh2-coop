#!/bin/bash
# TEST ONLY: the nine Gummi routes, one whole mission each, with two ships (seventh round, twenty-seventh glue).
# Disc test-s1-tt137 + the world-map jump kit + the launcher kit of each route (patches/<own>-gum0 .. -gum8, made
# with tools/own/make_jumpkit.py ... 0F 0 --type1 and tools/own/make_gumlaunch.py). Both players tap fire and
# weave (lane S3's scripts). One line per route in local/sweep/<log>.log; probe lines in local/tests/<name>-probe.txt.
# usage: bash tools/own/gum_routes.sh <ownPatchDirName> <sandbox> <port> <pine> <logName> [routes...]
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S="$P/tests/scripts/lane-s3"
OWN=$1; RD=$2; PT=$3; PN=$4; LOG="$P/local/sweep/$5.log"; shift 5
cd "$P" || exit 1
SN=$(python -c "print(','.join(str(f) for f in range(8000, 40000, 2000)) + ',39900')")
for r in "${@:-0 1 2 3 4 5 6 7 8}"; do
  for r1 in $r; do
    n="gr-$OWN-route$r1"
    out=$(PROBE="$P/tools/own/gummi_probe.py" bash "$P/tools/own/dusk_one.sh" "$n" "patches/$OWN-gum$r1" test-s1-tt137.iso 40000 "$SN" "$S/gb_p1_fight.txt" "$S/gb_p2_fight.txt" "$RD" "$PT" "$PN" 2>&1 | head -n 1)
    echo "route $r1 | $out | $(grep -c 'ship 2 hull' "$P/local/tests/$n-probe.txt") of $(grep -c . "$P/local/tests/$n-probe.txt") snapshots with ship 2 | last: $(tail -n 1 "$P/local/tests/$n-probe.txt" | cut -c1-150)" >> "$LOG"
  done
done
echo "gum routes $OWN done" >> "$LOG"
