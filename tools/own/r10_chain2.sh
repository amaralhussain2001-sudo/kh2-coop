# Tenth round, glue 72: save -> Game Over -> Load Game with DIFFERENT Drive values at the save (kit dvk2: at 4950, in the save menu,
# player 1 gauge 10 bars 1 (save data and slot), player 2 gauge 50 bars 4 (his slot)). v130 and the build-21 control v129.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
export RANGES=0032F058:C,0032E3AC:4,000F47C0:1C
export CHAINS=000F05CC@48C:4,0034E948@48C:4,000F05CC+48C@1B0:C,0034E948+48C@1B0:C,000F05CC+48C@250:4,000F05CC+48C@260:4,0034E948+48C@260:4
SN="4400,5000,5700,6600,7400,8000,8790,8900,9050,9250,9450,9650,9850,10300,11000,12000,13500"
PROBE="$P/tools/own/sweepm_probe.py" bash tools/own/dusk_one.sh dv2-v130 "$P/patches/test-own-v130-dvk2" test-m-roam.iso 14000 $SN "$O/drvload_p1.txt" "$O/drvload_p2.txt" run-x7 31950 28070 &
PROBE="$P/tools/own/sweepm_probe.py" bash tools/own/dusk_one.sh dv2-v129 "$P/patches/test-own-v129-dvk2" test-m-roam.iso 14000 $SN "$O/drvload_p1.txt" "$O/drvload_p2.txt" run-x8 32150 28071 &
wait
