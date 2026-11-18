#!/bin/bash
# TEST ONLY (partner's Drive display, part 150): test-own-pd2 (range check fix). (1) AL03 pictures again, TLB misses must be 0;
# (2) roam disc + forms kit: player 2 goes into a Drive Form (drive_p2), player 1 must see the partner's FORM strip.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
bash tools/own/r16_chain3.sh q test-own-pd2 &
PROBE="$P/tools/own/gauge_probe.py" bash tools/own/dusk_one.sh r16-form "$P/patches/test-own-pd2-forms" test-m-roam.iso 6400 5000,5300,5600,6000,6300 \
  "$O/drivelate_p1.txt" "$O/drive_p2.txt" run-x6 31750 28069 > local/sweep/r16/form.log 2>&1 &
wait
echo "r16 chain4 done" >> local/sweep/r16/chain4.txt
