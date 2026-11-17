#!/bin/bash
# TEST ONLY (tenth round): THE DRESS REHEARSAL OF THE BUILD 24 PACKAGE (98dad91e6e9e: build 23 + glue 78 --gummitag): two copies of the package on this PC
# (local/kit-test-t, made by tools/package/make_rehearsal_copies.py), hidden. Nothing else runs.
# Log: local/sweep/r9/r10chain64.txt ; results local/tests/p30-rehearsal-b24/
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/r9"
cd "$P" || exit 1
LOG="$B/r10chain64.txt"
echo "r10chain64 start $(date +%H:%M:%S)" >> "$LOG"
python -I tools/package/make_rehearsal_copies.py >> "$LOG" 2>&1
python -I tools/package/rehearse.py p30-rehearsal-b24 --game "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso" --layout 1 --screen 4:3 --frames 9000 --script-a tests/scripts/merge/newgame_p1.txt --script-b tests/scripts/merge/newgame_p2.txt --snap "5180,6400,6912,8900" --snapview >> "$LOG" 2>&1
echo "r10chain64 through $(date +%H:%M:%S)" >> "$LOG"
