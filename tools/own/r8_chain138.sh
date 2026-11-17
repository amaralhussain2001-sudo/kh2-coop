#!/bin/bash
# TEST ONLY (eighth round, job 12): THE DRESS REHEARSAL OF THE BUILD 19 PACKAGE (id 6a9309aadd28): two copies of the
# package on this PC (local/kit-test-t, made by tools/package/make_rehearsal_copies.py), hidden. Nothing else runs.
# Log: local/sweep/b15/chain138.txt ; results local/tests/p23-rehearsal-b19/
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/b15"
cd "$P" || exit 1
LOG="$B/chain138.txt"
echo "chain138 start $(date +%H:%M:%S)" >> "$LOG"
python -I tools/package/rehearse.py p23-rehearsal-b19 --game "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso" --layout 1 --screen 4:3 --frames 9000 --script-a tests/scripts/merge/newgame_p1.txt --script-b tests/scripts/merge/newgame_p2.txt --snap "5180,6400,6912,8900" --snapview >> "$LOG" 2>&1
echo "chain138 through $(date +%H:%M:%S)" >> "$LOG"
