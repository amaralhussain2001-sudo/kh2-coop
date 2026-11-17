#!/bin/bash
# TEST ONLY: the new things of test build 10 on one own-screen patch folder and its -summon kit (make_kit2.py
# --magic --forms=56 --limit --formkeys --drive=5 --byte=36C4:39): Summons called by player 2 and by player 1,
# Dismiss, a second Summon while one is out, the summon gauge running out. Log: local/final-b10.log
# usage: bash tools/own/final_b10.sh <ownPatchDirName> <sandbox> <port> <pine>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"
PD="$P/patches/$1-summon"; RD=$2; PT=$3; PN=$4
LOG="$P/local/final-b10.log"; : > "$LOG"
one() {  # name iso frames snaps p1 p2
  PROBE="$P/tools/own/heal_probe.py" bash "$P/tools/own/dusk_one.sh" "k10-$1" "$PD" "$2" "$3" "$4" "$5" "$6" "$RD" "$PT" "$PN" 2>&1 | head -1 | cut -c1-105 >> "$LOG"
  grep -E "^f" "$P/local/tests/k10-$1-probe.txt" | sed -E 's/slot [0-9A-F]+ //g; s/MP [0-9]+\/[0-9]+ //g' | cut -c1-125 >> "$LOG"
}
one sum-p2   test-g-friends.iso 6400 "4980,5100,5300,5600,6000,6300" "$S/newgame_only.txt" "$O/summon_p2.txt"
one sum2-p2  test-g-friends.iso 6400 "4980,5100,5300,5600,6000,6300" "$S/newgame_only.txt" "$O/summon2_p2.txt"
one sum-p1   test-g-friends.iso 6400 "4980,5100,5300,5600,6000,6300" "$O/summon_p1.txt" "$S/newgame_only.txt"
one dismiss  test-g-friends.iso 6100 "5100,5290,5330,5400,5500,5700,6000" "$S/newgame_only.txt" "$O/summon_dismiss_p2.txt"
one p1second test-g-friends.iso 6100 "5100,5390,5450,5500,5560,5640,5800,6000" "$O/summon_p1second_p1.txt" "$O/summon_only_p2.txt"
one p2second test-g-friends.iso 6100 "5100,5390,5450,5500,5560,5640,5800,6000" "$O/summon_only_p1.txt" "$O/summon_second_p2.txt"
one sumlong  test-s1-hb9f.iso 13100 "5100,6000,7000,8000,9000,10000,11000,12000,13000" "$S/newgame_only.txt" "$O/summon_only_p2.txt"
echo "final done" >> "$LOG"
