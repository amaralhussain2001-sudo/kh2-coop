#!/bin/bash
# TEST ONLY: run the Grandstander "player 2 swings" test on each variant of tools/own/make_playerbits.py and print
# the ball script's biggest hit counter and landing counter (near_probe.py). usage: grand_bits.sh <prefix> <n>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
L="$P/tests/scripts/lane-s1"
FR="4790,4830,4860,4900,4950,5000,5100,5300"
for b in $(seq 0 $(($2 - 1))); do
  n="g5-plbit$b"
  rm -rf "$P/local/tests/$n"
  (python -I "$P/tools/own/near_probe.py" "$P/local/tests/$n" 28061 "$FR" "$P/local/tests/$n-probe.txt" 1500 > /dev/null 2>&1 &)
  bash "$P/tools/own/run_own.sh" "$n" test-s1-tt90g.iso 5350 2.0 "$FR" "$L/s1-job-grand-near_p1.txt" "$L/s1-job-grand-near_p2.txt" idle 1 "$P/patches/$1$b" --pine 28061 2>&1 | tail -1 | cut -c1-75
  sleep 4
  echo "   bit $b: hits/landings seen: $(grep 'class 00350910 pos' "$P/local/tests/$n-probe.txt" | sed -E 's/.*W0 -> [0-9A-F]+: //' | awk '{print $6"/"$5}' | sort -u | tr '\n' ' ')"
done
