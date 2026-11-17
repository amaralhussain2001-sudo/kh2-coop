#!/bin/bash
# TEST ONLY (tenth round, glue 72 by a LOAD GAME FROM THE TITLE SCREEN, until now a HYPOTHESIS). Run A (ta1, v137 kit -dvk2 =
# make_kit2 --die=both --drivemax=5 + make_once 4950: player 1 gauge 10 bars 1, PLAYER 2 GAUGE 50 BARS 4): New Game, save to file 01,
# stand; its memory card is kept as local/cards/dvtitle.ps2.  Run B (r10_chain38b.sh) boots with that card.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
export RANGES=0032F058:C,0032E3AC:4,000F47C0:1C
export CHAINS=000F05CC@48C:4,0034E948@48C:4,000F05CC+48C@1B0:C,0034E948+48C@1B0:C,000F05CC+48C@250:4,000F05CC+48C@260:4,0034E948+48C@260:4
PROBE="$P/tools/own/sweepm_probe.py" bash tools/own/dusk_one.sh ta1 "$P/patches/test-own-v137-dvk2" test-m-roam.iso 7000 "4400,5000,5700,6600,6900" "$O/dvtitleA_p1.txt" "$O/idle.txt" run-x3 31150 28066
mkdir -p local/cards && cp local/run-x3/p1/memcards/Mcd001.ps2 local/cards/dvtitle.ps2 && cmp local/run-x3/p1/memcards/Mcd001.ps2 local/run-x3/p2/memcards/Mcd001.ps2 && echo "card kept (both copies' cards identical)"
