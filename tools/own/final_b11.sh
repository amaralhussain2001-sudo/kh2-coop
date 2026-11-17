#!/bin/bash
# TEST ONLY: the new things of test build 11 on one own-screen patch folder and its kits:
#   <name>-summon   make_kit2.py --magic --forms=56 --limit --formkeys --drive=5 --byte=36C4:39
#   <name>-sumcs    make_kit2.py --magic --forms=5F --limit --formkeys --drive=5        (Chicken Little, Stitch)
#   <name>-sumdie1  the Summon kit + --die=both
#   <name>-once-snapB  make_healkit.py both 9000 1 --nocure --p1slot=01C6C750 --p2slot=01C6C4E8, then make_snaptest.py B
# A room change while a Summon is out (the gauge kind of both heroes: player 1's slot must end in 01, the
# twin's in 03, when the twin called; the other way round when player 1 called), a Game Over while a Summon is
# out, and Continue after a Game Over inside the first boss fight. Log: local/final-b11.log
# (A probe line can show the SAME slot for both heroes: the engine's player pointer is the twin for a moment
# while an object thinks with him as the player. Look at the picture then; seen once, k11-stitch-p2 f7400.)
# usage: bash tools/own/final_b11.sh <ownPatchDirName> <sandbox> <port> <pine>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"
PD="$P/patches/$1"; RD=$2; PT=$3; PN=$4
LOG="$P/local/final-b11.log"; : > "$LOG"
room() {  # name kit frames snaps p1 p2
  CHAINS="0034E948+48C@1A0:20,000F05CC+48C@1A0:20" RANGES="01D49968:4" PROBE="$P/tools/own/memdump_probe.py" \
    bash "$P/tools/own/dusk_one.sh" "k11-$1" "$PD-$2" test-s1-hb9g.iso "$3" "$4" "$5" "$6" "$RD" "$PT" "$PN" 2>&1 | head -1 | cut -c1-105 >> "$LOG"
  grep -E "chain" "$P/local/tests/k11-$1-probe.txt" | awk 'NR%2==1' \
    | sed -E 's/chain //; s/ 9F 86 01 00 01 00 00 00 64 64 64 64 64 64 64//; s/0034E948\+48C [0-9A-F]+/P1 kind/; s/000F05CC\+48C [0-9A-F]+/twin kind/' \
    | paste - - | cut -c1-80 >> "$LOG"
}
die() {  # name frames snaps p1 p2
  PROBE="$P/tools/own/heal_probe.py" bash "$P/tools/own/dusk_one.sh" "k11-$1" "$PD-sumdie1" test-s1-hb9h.iso "$2" "$3" "$4" "$5" "$RD" "$PT" "$PN" 2>&1 | head -1 | cut -c1-105 >> "$LOG"
  grep -E "^f" "$P/local/tests/k11-$1-probe.txt" | sed -E 's/slot [0-9A-F]+ //g; s/MP [0-9]+\/[0-9]+ //g; s/ \| save26F6 0000//' | cut -c1-125 >> "$LOG"
}
room sum-p2    summon 7500 "5600,6000,6500,7200,7400" "$O/sumroom_p1.txt" "$O/sumroom_p2.txt"
room chick-p2  sumcs  7500 "5600,6000,6500,7200,7400" "$O/sumroom_p1.txt" "$O/sumroom_p2.txt"
room stitch-p2 sumcs  7500 "5600,6000,6500,7200,7400" "$O/sumroom_p1.txt" "$O/sumroom2_p2.txt"
room sum-p1    summon 7800 "5600,6300,6800,7200,7700" "$O/sumroom_call_p1.txt" "$O/roomlate_p2.txt"
die sumdieA 9000  "5300,6100,6500,6800,7100,7400,7800,8300,8900" "$O/sumdie_cont_p1.txt" "$O/summon_only_p2.txt"
die sumdieB 10500 "5600,6100,6900,7500,8100,8400,8800,9300,9900,10400" "$O/sumroomdie_p1.txt" "$O/sumroom_p2.txt"
RANGES="0032BAE0:10,01D5A970:10" PROBE="$P/tools/own/memdump_probe.py" bash "$P/tools/own/dusk_one.sh" k11-thorncont "$PD-once-snapB" test-s1-tt157.iso 13500 \
  "9500,9700,9900,10300,11100,12000,13400" "$O/thorn_cont_p1.txt" "$O/idle.txt" "$RD" "$PT" "$PN" 2>&1 | head -1 | cut -c1-105 >> "$LOG"
awk '{print $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12}' "$P/local/tests/k11-thorncont-probe.txt" | paste - - | cut -c1-110 >> "$LOG"
echo "final done" >> "$LOG"
