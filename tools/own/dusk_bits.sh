#!/bin/bash
# TEST ONLY: the Old Mansion Dusk fight (hit counter) with only player 2 attacking, on each variant of
# tools/own/make_playerbits.py; prints the picture layout at the end (0 = one view = the story scene plays).
# usage: dusk_bits.sh <prefix> <n>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
L="$P/tests/scripts/lane-s1"
FR="4800,7000,8000,8900"
for b in $(seq 0 $(($2 - 1))); do
  n="h2-plbit$b"
  rm -rf "$P/local/tests/$n"
  (python -I "$P/tools/own/room_probe.py" "$P/local/tests/$n" 28061 "$FR" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  bash "$P/tools/own/run_own.sh" "$n" test-s1-tt127.iso 9000 4.0 "$FR" "$L/s1-f-dusk-old1_p1.txt" "$L/s1-f-dusk-old1_p2.txt" idle 1 "$P/patches/$1$b" --pine 28061 2>&1 | tail -1 | cut -c1-70
  sleep 3
  echo "   bit $b: $(sed -E 's/frame ([0-9]+) room [0-9A-F]+ battle ([0-9A-F]+) layout ([0-9]+).*/\1:b\2:L\3/' "$P/local/tests/$n-probe.txt" | tr '\n' ' ')"
done
