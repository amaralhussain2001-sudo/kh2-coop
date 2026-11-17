#!/bin/bash
# TEST ONLY (tenth round): THE ONE-HERO CONTROL for the W_EX010 pair added at each door during a form (md6, nf5). The no-twin build
# test-v31-e-nn-forms, player 1 alone in Final Form, the walk to the west door aimed four ways (doorsNN1..4_p1: the one-hero camera
# differs from the co-op one, nf4 / nn2 went to a corner; make_teleport.py does not move the hero here). filepool_probe.py: limit
# 018C7440 = the Borough hb09, 018B5C40 = Merlin's house hb13.     ne1 run-x6 / ne2 run-x8 / ne3 run-x9 / ne4 run-x10
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5300,5700,6300,6900,7300,7900,8300,8900,9300,9900,10500,11400"
f() { PROBE="$P/tools/own/filepool_probe.py" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh $1 "$P/patches/test-v31-e-nn-forms" test-s1-hb13s.iso 11500 "$SN" "$O/$2" "$O/idle.txt" $3 $4 $5; }
f ne1 doorsNN1_p1.txt run-x6 31750 28069 &
f ne2 doorsNN2_p1.txt run-x8 32150 28071 &
f ne3 doorsNN3_p1.txt run-x9 32350 28072 &
f ne4 doorsNN4_p1.txt run-x10 32550 28073 &
wait
