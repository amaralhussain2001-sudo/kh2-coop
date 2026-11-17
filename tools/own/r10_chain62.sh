#!/bin/bash
# RECORD RE-WRITTEN UNDER A NEW NAME (2026-11-16): this chain ran as tools/own/r10_chain56.sh (a fork's run for item 9b); that name was
# later taken by another chain (the eh25 controls), so the run is kept here, unchanged.
# TEST ONLY (tenth round, item 9b, a fork's run; lanes run-x3 .. run-x6): mm1 showed that after player 2's Final Form RAN OUT BY ITSELF
# (no revert) one W_EX010 pair per door keeps coming (a sliding window of eleven), while after a REVERT (oh1 one hero, rv1 co-op)
# they collapse to one. Is that the game's own after a timeout? 16 doors at 650 frames, the form runs out on the way. filepool_probe.py.
#   tm1 x3  THE ONE-HERO ORIGINAL GAME (test-stock-god-forms, disc test-s1-hb13solo), player 1's Final Form (doorsManyP1f_p1)
#   tm2 x4  co-op v137-forms, PLAYER 1's Final Form (the game's own path), player 2 follows (doorsManyP1f_p1 / _p2)
#   tm3 x5  co-op v137-forms, TWO FORMS (player 1 Limit, player 2 Final), 16 doors (formdoorsMany_p1 / _p2)
#   tm4 x6  as tm1 with sp_probe.py (rooms: do the doors fire in the one-hero game at this pace?)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SB="5300,5900,6700,7350,8000,8650,9300,9950,10600,11250,11900,12550,13200,13850,14500,15150,15800,16450"
SC="5300,6300,7100,7750,8400,9050,9700,10350,11000,11650,12300,12950,13600,14250,14900,15550,16200,16850"
fp() { PROBE="$P/tools/own/$5" LOW=2000 SWEEP_PROBE_WAIT=900 bash tools/own/dusk_one.sh $1 "$P/patches/$6" $7 $8 "$9" "$O/${10}" "$O/${11}" $2 $3 $4; }
fp tm1 run-x3 31150 28066 filepool_probe.py test-stock-god-forms test-s1-hb13solo.iso 17000 "$SB" doorsManyP1f_p1.txt idle.txt &
fp tm2 run-x4 31350 28067 filepool_probe.py test-own-v137-forms test-s1-hb13s.iso 17000 "$SB" doorsManyP1f_p1.txt doorsManyP1f_p2.txt &
fp tm3 run-x5 31550 28068 filepool_probe.py test-own-v137-forms test-s1-hb13s.iso 17500 "$SC" formdoorsMany_p1.txt formdoorsMany_p2.txt &
fp tm4 run-x6 31750 28069 sp_probe.py test-stock-god-forms test-s1-hb13solo.iso 17000 "$SB" doorsManyP1f_p1.txt idle.txt &
wait
