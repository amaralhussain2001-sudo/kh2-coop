#!/bin/bash
# TEST ONLY (ninth round, job 5): THE TOY CANNON AND THE CARPET ESCAPE ENTERED FROM THE STORY, second try: player 1's hero is set beside the
# story's talk point at frame 6000 (make_teleport.py) and presses only Triangle up to 12000 (make_story_scripts.py).
#   run-x2: stD = room nm10, event program 22, the talk point f51y at (-319, 0, 96)   run-x3: stE = room al11, event program 10, the point m_80 at (0, -200, 30)
# usage: r9_chain39.sh [<ownBase>]   Logs local/sweep/r9/stD.log, stE.log; progress chain39.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
OWN=${1:-test-own-v107-snapB}
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain39.txt"; }
say "chain39 start ($OWN)"
ST=$(python -c "print(','.join(str(f) for f in range(5000, 30000, 1000)) + ',29900')")
one() {  # one <name> <sandbox> <port> <pine> <own> <list> <p1> <p2>
  ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="$ST" FRAMES=30000 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/$7" P2S="$O/$8" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$6"
  say "$1 done"
}
one stD run-x2 30950 28065 $OWN-tpnm "$B/list-st-nm10.txt" story_cannon_p1.txt cannon_p2.txt &
one stE run-x3 31150 28066 $OWN-tpal "$B/list-st-al11.txt" story_mash_p1.txt mashrc_long_p2.txt &
wait
say "chain39 through"
