#!/bin/bash
# TEST ONLY (eighth round, the vehicle items): THE FIFTY-FIRST GLUE, THIRD FORM (candidate v79: a repair mends both ships; the mission is over
# when either ship falls; the one hull gauge shows the weaker ship). v80 = the same with the test option
# --ship2first (only ship 2 is asked "are you hit", so ship 2 is the one that falls).
#   gh7  v78, nobody fires: ship 2's hull goes to 0: does ship 1 go with it, is the mission over the game's way
#   gh8  v77, nobody fires: both ships are hit; the gauge
#   gh9  v77, both players tap fire and weave, the whole mission, 40,000 frames
# ONE RUN AT A TIME, hidden, sandbox run-m. Log local/sweep/b15/chain87.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S="$P/tests/scripts/lane-s3"; B="$P/local/sweep/b15"
cd "$P" || exit 1
LOG="$B/chain87.txt"
echo "chain87 start $(date +%H:%M:%S)" >> "$LOG"
SN=$(python -c "print(','.join(str(f) for f in range(8000, 24000, 500)) + ',23900')")
one() {  # name patch frames snaps p1script p2script
  local n=$1
  out=$(PROBE="$P/tools/own/gummi_probe.py" bash "$P/tools/own/dusk_one.sh" "$n" "patches/$2" test-s1-tt137.iso "$3" "$4" "$5" "$6" run-m 29050 28081 2>&1 | head -n 1)
  echo "$n | $out | TLB misses $(grep -ac 'TLB Miss' "$P/local/run-m/p1/logs/emulog.txt")" >> "$LOG"
  cp "$P/local/tests/$n-probe.txt" "$B/$n-probe.txt" 2>/dev/null
  echo "$n done $(date +%H:%M:%S)" >> "$LOG"
}
one r8gh7 test-own-v80-gum0 24000 "$SN" "$S/gb_p1_idle.txt" "$S/gb_p2_idle.txt"
one r8gh8 test-own-v79-gum0 24000 "$SN" "$S/gb_p1_idle.txt" "$S/gb_p2_idle.txt"
SN2=$(python -c "print(','.join(str(f) for f in range(8000, 40000, 2000)) + ',39900')")
one r8gh9 test-own-v79-gum0 40000 "$SN2" "$S/gb_p1_fight.txt" "$S/gb_p2_fight.txt"
echo "chain87 through $(date +%H:%M:%S)" >> "$LOG"
