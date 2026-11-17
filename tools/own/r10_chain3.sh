# Tenth round, glue 72: save -> Game Over -> Load Game where the session's values differ from the save's. Kit dvk3 = dvk2
# (at 4950 in the save menu: player 1 gauge 10 bars 1, player 2 gauge 50 bars 4) + at 6000 (after the save): player 1's
# slot gauge 20 bars 2, player 2's slot gauge 5 bars 0. dvk3x = the same with dv_load switched off (tests dv_ext alone).
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
export RANGES=0032F058:C,0032E3AC:4,000F47C0:1C
export CHAINS=000F05CC@48C:4,0034E948@48C:4,000F05CC+48C@1B0:C,0034E948+48C@1B0:C,000F05CC+48C@250:4,000F05CC+48C@260:4,0034E948+48C@260:4
SN="4400,5000,5700,6600,7400,8000,8790,8900,9050,9250,9450,9650,9850,10300,11000,12000,13500"
run() { PROBE="$P/tools/own/sweepm_probe.py" bash tools/own/dusk_one.sh $1 "$P/patches/$2" test-m-roam.iso 14000 $SN "$O/drvload_p1.txt" "$O/drvload_p2.txt" $3 $4 $5; }
run dv3-v130 test-own-v130-dvk3 run-x7 31950 28070 &
run dv3-v129 test-own-v129-dvk3 run-x8 32150 28071 &
run dv3-v130x test-own-v130-dvk3x run-x9 32350 28072 &
wait
