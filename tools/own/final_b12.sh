#!/bin/bash
# TEST ONLY: the new things of test build 12 (seventh round) on one own-screen patch folder and its kits
# (bash tools/own/make_kits.sh <name> makes them all). Three parts, so that three sandboxes can share the work:
#   a  the prompt pool in the long Reversal fight (lowest free count of 18), player 2's Summon after a Game Over
#      and Continue (kit -sumkill), a helper's Potion for player 2 (kit -hitems), a Limit by player 2 while the
#      heroes are far apart (kit -limit), the Moogle's workshop on player 2's controller (kit -moogle)
#   b  the world map and "Land" on player 2's controller, Retry of a skate challenge by player 2 (the grey square),
#      the Gummi Ship: two ships (kit -gum0), player 2's pause, player 2 alone through the Gummi Menu
#   c  the long random roam run (kit -kit; 0 fault lines), "player 2 has no hero" (player 2 alone starts the game
#      and plays the carpet escape; plain jump disc), and the special modes on the v5 test disc
#      (test-v5-tt137.iso): Light Cycle, the Pooh flight, the carpet fight above Agrabah
# Every result line ends with the fault line count of player 1's PC ("TLB misses N"). Log: local/final-b12-<part>.log
# usage: bash tools/own/final_b12.sh <ownPatchDirName> <sandbox> <port> <pine> a|b|c
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/tests/scripts/lane-s1"
OWN=$1; PD="$P/patches/$1"; RD=$2; PT=$3; PN=$4; PART=$5
LOG="$P/local/final-b12-$PART.log"; : > "$LOG"
cd "$P" || exit 1
run() {  # name patchDir iso frames snaps p1 p2   (env: PROBE and the probe's own variables)
  bash "$P/tools/own/dusk_one.sh" "b12-$1" "$2" "$3" "$4" "$5" "$6" "$7" "$RD" "$PT" "$PN" 2>&1 | head -n 1 | cut -c1-100 > "$P/local/tests/b12-$1-line.txt"
  echo "$(cat "$P/local/tests/b12-$1-line.txt") | TLB misses $(grep -c 'TLB Miss' "$P/local/$RD/p1/logs/emulog.txt")" >> "$LOG"
}
show() {  # name grepPattern cutWidth [maxLines]
  grep -E "$2" "$P/local/tests/b12-$1-probe.txt" | head -n "${4:-12}" | cut -c1-"$3" | sed 's/^/    /' >> "$LOG"
}
jump() {  # kitDirName worldHex program -> patches/test-b12-<sandbox>
  python -I tools/own/make_jumpkit.py "patches/$1" "patches/test-b12-$RD" "$2" "$3" > /dev/null
}
if [ "$PART" = "a" ]; then
  FROM=5000 POOL_N=18 PROBE="$P/tools/own/pool_trace_probe.py" run pool "$PD" test-s1-tt157.iso 12000 "6000,8000,10000,11900" "$L/s1-g-thorn-p2_p1.txt" "$L/s1-g-thorn-p2_p2.txt"
  tail -n 1 "$P/local/tests/b12-pool-probe.txt" | sed 's/^/    /' >> "$LOG"
  RANGES="000F47C0:40,000F7F30:40,01D49968:4" CHAINS="0034E948+48C@1A8:18,000F05CC+48C@1A8:18" PROBE="$P/tools/own/memdump_probe.py" \
    run sumkill "$PD-sumkill" test-s1-hb9h.iso 10000 "5600,6100,6900,7600,7900,8200,8500,8900,9400,9900" "$O/sumroomdie_p1.txt" "$O/sumroom_p2.txt"
  show sumkill "chain 000F05CC|01D49968" 90 24
  PROBE="$P/tools/own/item_probe.py" run hitems "$PD-hitems" test-g-friends.iso 6000 "4860,4920,4980,5040,5100,5160,5220,5280,5340,5400,5500,5600,5700,5800,5900" "$S/newgame_only.txt" "$O/idle.txt"
  show hitems "^f" 200 15
  PROBE="$P/tools/own/heal_probe.py" run limsplit "$PD-limit" test-g-friends.iso 5900 "4880,5090,5290,5360,5450,5600,5850" "$S/newgame_only.txt" "$O/limsplit_up_p2.txt"
  sed 's/ f\([0-9]*\) L/\nf\1 L/g' "$P/local/tests/b12-limsplit-probe.txt" | sed -E 's/slot [0-9A-F]+ //g; s/ \| save26F6 0000//' | cut -c1-200 | sed 's/^/    /' >> "$LOG"
  PROBE="$P/tools/own/room_probe.py" run moogle "$PD-moogle" test-s1-hb10m.iso 6600 "5250,5450,5560,5660,5800,5900,6000,6100,6300,6550" "$S/newgame_only.txt" "$O/moogle_shop_p2.txt"
  show moogle "." 160 10
fi
if [ "$PART" = "b" ]; then
  PROBE="$P/tools/own/room_probe.py" run wm-p2 "$PD" test-s1-hb13s.iso 9400 "7250,7460,7700,8000,8200,8400,8700,9300" "$O/worldmap_p1.txt" "$O/worldmap_p2.txt"
  show wm-p2 "." 160 8
  PROBE="$P/tools/own/room_probe.py" run wmland-p2 "$PD" test-s1-hb13s.iso 8600 "7250,7380,7520,7680,7900,8200,8500" "$O/worldmap_p1.txt" "$O/worldmap_land_p2.txt"
  show wmland-p2 "." 160 8
  PROBE="$P/tools/own/menu_probe.py" run skate-retry "$PD" test-v4-al109.iso 13000 "8500,9030,9100,9300,9800,10500,11500,12900" "$O/rules_p1.txt" "$O/skate_retry_p2.txt"
  show skate-retry "." 160 8
  PROBE="$P/tools/own/gummi_probe.py" run gum-ships "$PD-gum0" test-s1-tt137.iso 12000 "5200,6000,6400,6800,7200,7600,8200,8500,8800,9100,9500,10500,11900" "$O/gum2_p1.txt" "$O/gum2_p2.txt"
  show gum-ships "." 200 13
  PROBE="$P/tools/own/gummi_probe.py" run gum-pause "$PD-gum0" test-s1-tt137.iso 12000 "7800,8100,8300,8500,8700,8900,9100,9300,9450,9600,9800,10200,10600,11900" "$O/gumpause_p1.txt" "$O/gumpause_p2.txt"
  show gum-pause "." 200 14
  PROBE="$P/tools/own/gummi_probe.py" run gum-p2menu "$PD-gum0" test-s1-tt137.iso 12000 "4800,5600,6400,7200,7900,8200,8700,9000,9600,10500,11900" "$O/gum_new_p1.txt" "$O/gum_fly_p2.txt"
  show gum-p2menu "." 200 11
fi
if [ "$PART" = "c" ]; then
  OWN_THEN=random run longroam "$PD-kit" test-m-roam.iso 34000 "4700,33900" "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt"
  # New Game on the full disc v5 (final_b9.sh part b does the same on disc v4)
  PROBE="$P/tools/own/room_probe.py" run newgame-v5 "$PD" kh2-coop-v5.iso 12000 "6000,11900" "$S/newgame_p1.txt" "$S/newgame_p2.txt"
  show newgame-v5 "^frame" 160 4
  SN="4900,5250,5600,5900,6200,6500,6800,7100,7400,7700,8000,8300,8600,8900"
  jump "$OWN-snapB" 07 61
  PROBE="$P/tools/own/sp_probe.py" run alone-al61 "$P/patches/test-b12-$RD" test-s1-tt137.iso 9000 "$SN" "$O/none_p1.txt" "$O/alone_p2.txt"
  show alone-al61 "^f" 200 14
  # (eh58 = EH14_MS103, the start of the Luxord fight: 5 fault lines without the gauge guard of make_own.py)
  for m in "tr61 11 61" "po55 09 55" "al62 07 62" "al100 07 100" "eh58 12 58"; do
    set -- $m
    jump "$OWN-snapB" "$2" "$3"
    PROBE="$P/tools/own/sp_probe.py" run "v5-$1" "$P/patches/test-b12-$RD" test-v5-tt137.iso 9000 "$SN" "$O/sp_p1.txt" "$O/sp_p2.txt"
    show "v5-$1" "^f" 200 14
  done
fi
echo "final b12 $PART done" >> "$LOG"
