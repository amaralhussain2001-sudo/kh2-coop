#!/bin/bash
# TEST ONLY (tenth round, item 10, take 4; a fork's run, lanes run-x3 .. run-x6): as r10_chain58.sh (the one-hero ORIGINAL GAME jumped
# like lbH: patches/test-stock-god-cap-lb-al00solo on test-s1-tt137solo) but 40,000 frames and mash40k_s0/s3/s11/s17_p1 (mashrc_long_p1's
# pattern continued to 40,000, shifted 0 / 3 / 11 / 17 frames). run_own2.sh is called directly to pass --timeout 2600.
#   fc1 x3 s0   fc2 x4 s3   fc3 x5 s11   fc4 x6 s17
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="6000,9000,12000,15000,18000,21000,24000,27000,30000,33000,36000,39900"
f() { n=$1; rm -rf "$P/local/tests/$n"; (python -I "$P/tools/own/cap_log_probe3.py" "$P/local/tests/$n" "$5" "$SN" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  OWN_RUN_DIR=$3 OWN_PORT=$4 bash "$P/tools/own/run_own2.sh" "$n" test-s1-tt137solo.iso 40000 4.0 "$SN" "$O/$2" "$O/idle.txt" idle 1 "$P/patches/test-stock-god-cap-lb-al00solo" --pine "$5" --timeout 2600 2>&1 | tail -1 | cut -c1-110
  echo "$n $3 null stores at 0x16e1a4: $(grep -c 'pc=0x16e1a4' "$P/local/$3/p1/logs/emulog.txt") | all fault lines $(grep -c 'pc=0x' "$P/local/$3/p1/logs/emulog.txt")"; }
f fc1 mash40k_s0_p1.txt run-x3 31150 28066 &
f fc2 mash40k_s3_p1.txt run-x4 31350 28067 &
f fc3 mash40k_s11_p1.txt run-x5 31550 28068 &
f fc4 mash40k_s17_p1.txt run-x6 31750 28069 &
wait
