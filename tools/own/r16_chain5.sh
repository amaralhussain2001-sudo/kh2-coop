#!/bin/bash
# TEST ONLY (partner's Drive display, part 150): test-own-pd2 (range check fix). (1) AL03 pictures again, TLB misses must be 0;
# (2) roam disc + forms kit: player 2 goes into a Drive Form (drive_p2), player 1 must see the partner's FORM strip.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
bash tools/own/r16_chain3.sh r test-own-pd3 &
PROBE="$P/tools/own/gauge_probe.py" bash tools/own/dusk_one.sh r16-form3 "$P/patches/test-own-pd3-forms" test-m-roam.iso 6400 5000,5300,5600,6000,6300 \
  "$O/drivelate_p1.txt" "$O/drive_p2.txt" run-x6 31750 28069 > local/sweep/r16/form3.log 2>&1 &
wait
echo "r16 chain5 done" >> local/sweep/r16/chain5.txt
