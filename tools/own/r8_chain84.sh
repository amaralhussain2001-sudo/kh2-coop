#!/bin/bash
# TEST ONLY (eighth round, the vehicle items): THE FIFTY-FIRST GLUE (--ship2hit, candidate v75 = v74 + that glue):
# can player 2's Gummi ship be hit, has it its own hull, and what happens when a hull is 0.
# Disc test-s1-tt137 + the launcher kit of route 0 (patches/test-own-v75-gum0). Probe gummi_probe.py: both ships'
# hull and state at every snapshot.
#   gh1  nobody fires, both ships where they start (ship 2 is 90 to the side): both hulls should go down
#   gh2  nobody fires, player 2 moves his ship to the left and stays there
#   gh3  both players tap fire and weave (lane S3's scripts), the whole mission, 40,000 frames
# ONE RUN AT A TIME, hidden, sandbox run-m. Log local/sweep/b15/chain84.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S="$P/tests/scripts/lane-s3"; B="$P/local/sweep/b15"
cd "$P" || exit 1
LOG="$B/chain84.txt"
echo "chain84 start $(date +%H:%M:%S)" >> "$LOG"
SN=$(python -c "print(','.join(str(f) for f in range(8000, 24000, 500)) + ',23900')")
one() {  # name frames snaps p1script p2script
  local n=$1
  out=$(PROBE="$P/tools/own/gummi_probe.py" bash "$P/tools/own/dusk_one.sh" "$n" "patches/test-own-v75-gum0" test-s1-tt137.iso "$2" "$3" "$4" "$5" run-m 29050 28081 2>&1 | head -n 1)
  echo "$n | $out | TLB misses $(grep -ac 'TLB Miss' "$P/local/run-m/p1/logs/emulog.txt")" >> "$LOG"
  cp "$P/local/tests/$n-probe.txt" "$B/$n-probe.txt" 2>/dev/null
  echo "$n done $(date +%H:%M:%S)" >> "$LOG"
}
one r8gh1 24000 "$SN" "$S/gb_p1_idle.txt" "$S/gb_p2_idle.txt"
one r8gh2 24000 "$SN" "$S/gb_p1_idle.txt" "$S/gb_p2_left.txt"
SN2=$(python -c "print(','.join(str(f) for f in range(8000, 40000, 2000)) + ',39900')")
one r8gh3 40000 "$SN2" "$S/gb_p1_fight.txt" "$S/gb_p2_fight.txt"
echo "chain84 through $(date +%H:%M:%S)" >> "$LOG"
