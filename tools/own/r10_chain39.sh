#!/bin/bash
# TEST ONLY (tenth round). md1 run-x6: calibration for SEVERAL DOORS IN A ROW (glue 75): kit v137-forms, disc test-s1-hb13s,
# finaldoor4_p1/p2 (player 2 in Final Form through the west door, then right / left / right), probe sp_probe.py (room and both
# heroes' positions) at each step.   tb3 run-x7: the title Load Game (r10_chain38b.sh's tb1) on v134 = build 22's own file.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh md1 "$P/patches/test-own-v137-forms" test-s1-hb13s.iso 9000 "4690,5300,5590,6000,6250,6450,7000,7250,7850,8100,8900" "$O/finaldoor4_p1.txt" "$O/finaldoor4_p2.txt" run-x6 31750 28069 &
CARD="C:/Users/PCFORC~1/AppData/Local/Temp/claude/cdca3cd92bc74bb0/cd572676-0336-44f2-bfb2-721e56869cd0/scratchpad/dvtitle.ps2"
SN="2950,3500,3750,4250,5000,6000,8900"
export RANGES=0032F058:C,0032E3AC:4,000F47C0:1C
export CHAINS=000F05CC+48C@1B0:C,0034E948+48C@1B0:C
( n=tb3; rm -rf "$P/local/tests/$n"; (python -I "$P/tools/own/sweepm_probe.py" "$P/local/tests/$n" 28070 "$SN" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  OWN_RUN_DIR=run-x7 OWN_PORT=31950 bash "$P/tools/own/run_own2.sh" "$n" test-m-roam.iso 9000 4.0 "$SN" "$O/dvtitleB1_p1.txt" "$O/idle.txt" idle 1 "$P/patches/test-own-v134" --pine 28070 --card "$CARD" 2>&1 | tail -1 | cut -c1-110 ) &
wait
