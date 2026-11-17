#!/bin/bash
# TEST ONLY (eighth round, job 12): THE DRESS REHEARSAL OF THE BUILD 13 PACKAGE, as one step of the one queue (so
# that it never runs beside another test). It WAITS (at most 45 minutes) for the file local/sweep/b15/go42.txt,
# which is written by hand when the regression is read, the package is built and the rehearsal copies are made
# (tools/package/make_rehearsal_copies.py). No go file in that time: nothing is run.
# Log: local/sweep/b15/chain42.txt ; results local/tests/p17-rehearsal-b13/
P="/c/Users/PC FORCE/Desktop/New folder (3)"
B="$P/local/sweep/b15"
cd "$P" || exit 1
LOG="$B/chain42.txt"
echo "chain42 start $(date +%H:%M:%S)" >> "$LOG"
n=0
while [ ! -f "$B/go42.txt" ] && [ $n -lt 270 ]; do sleep 10; n=$((n+1)); done
if [ ! -f "$B/go42.txt" ]; then echo "chain42: no go file, nothing run $(date +%H:%M:%S)" >> "$LOG"; exit 0; fi
echo "chain42 go $(date +%H:%M:%S)" >> "$LOG"
python -I tools/package/rehearse.py p17-rehearsal-b13 --game "Kingdom Hearts II - Final Mix (2 Players TEST v5).iso" --layout 1 --screen 4:3 --frames 9000 --script-a tests/scripts/merge/newgame_p1.txt --script-b tests/scripts/merge/newgame_p2.txt --snap "5180,6400,6912,8900" --snapview >> "$LOG" 2>&1
echo "chain42 through $(date +%H:%M:%S)" >> "$LOG"
