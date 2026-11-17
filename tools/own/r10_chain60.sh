#!/bin/bash
# RECORD RE-WRITTEN UNDER A NEW NAME (2026-11-16): this chain ran as tools/own/r10_chain54.sh (a fork's run for items 9a / 9b); that
# name was later taken by another chain (item 7), so the run is kept here, unchanged.
# TEST ONLY (tenth round, items 9a / 9b of the user's list, a fork's run; lanes run-x3 .. run-x6 only):
#   oh1 x3  9a THE ONE-HERO CONTROL: the ORIGINAL GAME (patches/test-stock-god-forms = empty patch + god kit + forms kit) on the NEW
#           one-hero disc test-s1-hb13solo.iso (build_disc.py hb13solo --jump1 "HB 13 99" --party DEFAULT --mod
#           tools/lane-s1/mods/hb13-save-friends --no-twin), doorsSolo_p1 (Final Form, five doors, revert, two doors), filepool_probe.py
#   oh2 x4  the same, sp_probe.py (rooms, positions)
#   mm1 x5  9b co-op v137-forms, player 2 in Final Form, a door every 650 frames (doorsMany_p1/p2), filepool_probe.py
#   mm2 x6  the same, sweepm_probe.py with player 1's / player 2's Drive slot (01C6C698 / 01C6C900: gauge, bars, most)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SA="5300,5700,6300,6900,7300,7900,8300,8900,9300,9900,10300,10900,11300,11900,12400"
SB="5300,5900,6700,7350,8000,8650,9300,9950,10600,11250,11900,12550,13200,13850,14500,15150,15800,16450"
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=600 bash tools/own/dusk_one.sh oh1 "$P/patches/test-stock-god-forms" test-s1-hb13solo.iso 12500 "$SA" "$O/doorsSolo_p1.txt" "$O/idle.txt" run-x3 31150 28066 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh oh2 "$P/patches/test-stock-god-forms" test-s1-hb13solo.iso 12500 "$SA" "$O/doorsSolo_p1.txt" "$O/idle.txt" run-x4 31350 28067 &
PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=900 bash tools/own/dusk_one.sh mm1 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 17000 "$SB" "$O/doorsMany_p1.txt" "$O/doorsMany_p2.txt" run-x5 31550 28068 &
RANGES=01C6C698:4,01C6C900:4 PROBE="$P/tools/own/sweepm_probe.py" SWEEP_PROBE_WAIT=900 bash tools/own/dusk_one.sh mm2 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 17000 "$SB" "$O/doorsMany_p1.txt" "$O/doorsMany_p2.txt" run-x6 31750 28069 &
wait
