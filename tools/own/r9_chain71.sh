#!/bin/bash
# TEST ONLY (ninth round, job 7): THE DRESS REHEARSAL OF THE BUILD 21 PACKAGE: two copies of the package on this PC
# (local/kit-test-t, made by tools/package/make_rehearsal_copies.py), hidden. Nothing else runs.
# Log: local/sweep/r9/chain71.txt ; results local/tests/p26-rehearsal-b21b/
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/r9"
cd "$P" || exit 1
LOG="$B/chain71.txt"
echo "chain71 start $(date +%H:%M:%S)" >> "$LOG"
python -I tools/package/make_rehearsal_copies.py >> "$LOG" 2>&1
python -I tools/package/rehearse.py p26-rehearsal-b21b --game "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso" --layout 1 --screen 4:3 --frames 9000 --script-a tests/scripts/merge/newgame_p1.txt --script-b tests/scripts/merge/newgame_p2.txt --snap "5180,6400,6912,8900" --snapview >> "$LOG" 2>&1
echo "chain71 through $(date +%H:%M:%S)" >> "$LOG"
