#!/bin/bash
# TEST ONLY (tenth round, the user's report: "when i click new game i talk with a girl in the shop after i talk with her i still saw her
# in Player1 but not player 2"). Real disc kh2-coop-v5.iso, the package's own patch (patches/test-package-v3), New Game: Market Street
# (tt07, program 0x14). The accessory shop girl N_EX690_TT_ACCE_RTN (0x0547; tutorial copy 0x0849) at (-2891, -889). Kits
# test-pkg-tpsg1 / -tpsg2 = make_teleport.py: player 1 (01AAB2F0) / player 2 (01A90B00) to (-2790, -960) at 6200.
#   sg3 run-x7  player 1 WALKS to her and talks     sg4 run-x8  player 2 walks to her and talks (the teleport kits did not move
#   the heroes in this room, sg1 / sg2)
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="6290,6430,6600,7000,7800,8300,8800,9300"
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh sg5 "$P/patches/test-package-v3" kh2-coop-v5.iso 9400 "$SN" "$O/shopgirl_p1.txt" "$O/idle.txt" run-x7 31950 28070 &
PROBE="$P/tools/own/sp_probe.py" bash tools/own/dusk_one.sh sg6 "$P/patches/test-package-v3" kh2-coop-v5.iso 9400 "$SN" "$O/ng_stand_p1.txt" "$O/shopgirl_p2.txt" run-x8 32150 28071 &
wait
