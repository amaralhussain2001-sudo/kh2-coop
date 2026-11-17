#!/bin/bash
# TEST ONLY: the new things of test build 8 on one own-screen patch folder (and its -forms kit): helper split,
# Valor and Master Form for player 2, the boss fight with two views, the five skate challenges and Mail Delivery
# on the v4 data, New Game on the full v4 disc. Log: local/final-b8.log
# usage: bash tools/own/final_b8.sh <ownPatchDirName> <sandbox> <port> <pine> <part: a|b>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/tests/scripts/lane-s1"; S="$P/tests/scripts/merge"
PD="$P/patches/$1"; RD=$2; PT=$3; PN=$4
LOG="$P/local/final-b8-$5.log"; : > "$LOG"
one() {  # name probe iso frames snaps p1 p2 patchDir grepPattern
  PROBE="$P/tools/own/$2" bash "$P/tools/own/dusk_one.sh" "k8-$1" "$8" "$3" "$4" "$5" "$6" "$7" "$RD" "$PT" "$PN" 2>&1 | head -1 | cut -c1-105 >> "$LOG"
  grep -E "$9" "$P/local/tests/k8-$1-probe.txt" | sed -E 's/class [0-9A-F]+ update [0-9A-F]+ //' | cut -c1-125 >> "$LOG"
}
if [ "$5" = a ]; then
  one split   party_probe.py test-s1-hb9f.iso 8600 "5200,6300,7400,8500" "$S/newgame_only.txt" "$O/farback_p2.txt" "$PD" "heroes|party [12]"
  one valor   drv_probe2.py  test-s1-hb9f.iso 7000 "5000,5900,6900" "$S/newgame_only.txt" "$O/drive2_p2.txt" "$PD-forms" "^f"
  one master  drv_probe2.py  test-s1-hb9f.iso 7000 "5100,5900,6900" "$S/newgame_only.txt" "$O/master_p2.txt" "$PD-forms" "^f"
  one thorn   bm_probe.py    test-s1-tt157.iso 9100 "$(python -c "print(','.join(str(f) for f in range(5000, 9001, 160)))")" "$L/s1-g-thorn-p2_p1.txt" "$L/s1-g-thorn-p2_p2.txt" "$PD" "hold 1"
  one musplit party_probe.py test-s1-mu68.iso 9000 "6000,8000" "$O/rules_p1.txt" "$O/mash_p2.txt" "$PD" "heroes|party [12]"
else
  for t in al109 tt187 hb99 nm75 ca88 tt91; do
    one "skate-$t" menu_probe.py "test-v4-$t.iso" 6000 "5400,5900" "$O/rules_p1.txt" "$O/mailride_p2.txt" "$PD" "board mode"
  done
  one roam2   menu_probe.py  test-s1-skate-s2.iso 5700 "4950,5300" "$L/s1-skate-s2_p1.txt" "$O/skate_late_p2.txt" "$PD" "board mode"
  one newgame room_probe.py  kh2-coop-v4.iso 12000 "6000,11900" "$S/newgame_p1.txt" "$S/newgame_p2.txt" "$PD" "^frame"
fi
echo "final done" >> "$LOG"
