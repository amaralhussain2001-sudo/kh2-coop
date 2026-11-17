#!/bin/bash
# TEST ONLY (tenth round, after a review): beside the regression b32 (run-m .. run-x4), on x5 .. x10:
#   fd1 x5  v137-forms TWO FORMS (player 1 Limit, player 2 Final) through the west door and three more (formdoors2_p1/p2), filepool_probe.py
#   fd2 x6  the same, sp_probe.py (rooms, positions)          fd3 x7  the same on v134-forms (build 22, the user's), filepool_probe.py
#   sc1 x8  THE STOCK-GAME CONTROL test-stock-god-forms (the original game, HP held, no exit rule), one hero, doorsNNc_p1, filepool_probe.py
#   sc2 x9  the same, sp_probe.py
#   gl1 x10 the shop girl: the package's patch, New Game, player 1 walks to her and talks (shopgirl_p1), npc_probe.py (objects near her)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5300,5700,6300,6900,7300,7900,8300,8900,9300,9900"
fp() { PROBE="$P/tools/own/$5" LOW=2000 SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh $1 "$P/patches/$6" test-s1-hb13s.iso 10000 "$SN" "$O/$7" "$O/$8" $2 $3 $4; }
fp fd1 run-x5 31550 28068 filepool_probe.py test-own-v137-forms formdoors2_p1.txt formdoors2_p2.txt &
fp fd2 run-x6 31750 28069 sp_probe.py test-own-v137-forms formdoors2_p1.txt formdoors2_p2.txt &
fp fd3 run-x7 31950 28070 filepool_probe.py test-own-v134-forms formdoors2_p1.txt formdoors2_p2.txt &
fp sc1 run-x8 32150 28071 filepool_probe.py test-stock-god-forms doorsNNc_p1.txt idle.txt &
fp sc2 run-x9 32350 28072 sp_probe.py test-stock-god-forms doorsNNc_p1.txt idle.txt &
PROBE="$P/tools/own/npc_probe.py" bash tools/own/dusk_one.sh gl1 "$P/patches/test-package-v3" kh2-coop-v5.iso 9400 "6290,6430,6600,7000,7800,8300,9300" "$O/shopgirl_p1.txt" "$O/idle.txt" run-x10 32550 28073 &
wait
