#!/bin/bash
# TEST ONLY (tenth round, run B of r10_chain38.sh): boot WITH THE CARD local/cards/dvtitle.ps2 (file 01 saved by ta1: player 2's
# gauge 50 bars 4), LOAD GAME FROM THE TITLE SCREEN, read the Drive values. Plain patches (no kit). tb1 / tb2 = two button variants
# on v137 (calibration); then the same on v134 (build 22) once the variant is known.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
export RANGES=0032F058:C,0032E3AC:4,000F47C0:1C
export CHAINS=000F05CC@48C:4,0034E948@48C:4,000F05CC+48C@1B0:C,0034E948+48C@1B0:C,000F05CC+48C@250:4,000F05CC+48C@260:4,0034E948+48C@260:4
SN="2950,3050,3250,3500,3750,4000,4250,4500,5000,6000,7500,8900"
CARD="C:/Users/PCFORC~1/AppData/Local/Temp/claude/cdca3cd92bc74bb0/cd572676-0336-44f2-bfb2-721e56869cd0/scratchpad/dvtitle.ps2"  # (a copy of local/cards/dvtitle.ps2, path without spaces)
# one(): dusk_one.sh's three steps with --card added (dusk_one.sh passes no extra options)
one() { n=$1; rm -rf "$P/local/tests/$n"; (python -I "$P/tools/own/sweepm_probe.py" "$P/local/tests/$n" "$7" "$SN" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  OWN_RUN_DIR=$5 OWN_PORT=$6 bash "$P/tools/own/run_own2.sh" "$n" test-m-roam.iso 9000 4.0 "$SN" "$3" "$4" idle 1 "$2" --pine "$7" --card "$CARD" 2>&1 | tail -1 | cut -c1-110; }
one tb1 "$P/patches/test-own-v137" "$O/dvtitleB1_p1.txt" "$O/idle.txt" run-x4 31350 28067 &
one tb2 "$P/patches/test-own-v137" "$O/dvtitleB2_p1.txt" "$O/idle.txt" run-x5 31550 28068 &
wait
