#!/bin/bash
# Own-screen test batch (the runs of batch_v6.sh) for a patch folder given by its name in patches: <name>, <name>-kit, <name>-die2.
# usage: bash tools/own/batch_v7.sh [name]     -> log local/own-batch7.log, results local/tests/y*v-...
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S="$P/tests/scripts/merge"
O="$P/tests/scripts/own"
R="$P/tools/own/run_own.sh"
PB=${1:-test-own-v6-e}
LOG="$P/local/own-batch7.log"
: > "$LOG"
bash "$R" y1v-long-roam test-m-roam.iso 34000 4.0 "4700,7300,12000,18000,24000,33900" "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random 4 "$P/patches/${PB}-kit" >> "$LOG" 2>&1
bash "$R" y2v-cont test-m-roam.iso 16000 2.0 "6600,7000,8000,9000,9100,9700,10300,11000,12000,13000,15900" "$S/save_cont_p1.txt" "$S/save_cont_p2.txt" idle 4 "$P/patches/${PB}-die2" >> "$LOG" 2>&1
bash "$R" y4v-menu test-m-roam.iso 5300 2.0 "4800,4850,5040,5100,5150,5250" "$O/menu_p1.txt" "$O/menu_p2.txt" idle 4 "$P/patches/${PB}-kit" >> "$LOG" 2>&1
bash "$R" y6v-pace test-m-fight.iso 5800 1.0 "4700,5200,5700" "$S/atk_p1.txt" "$S/atk_p2.txt" idle 4 "$P/patches/${PB}" >> "$LOG" 2>&1
bash "$R" y7v-newgame kh2-coop-v2.iso 9000 2.0 "5180,6400,6912,8900" "$S/newgame_p1.txt" "$S/newgame_p2.txt" random 4 "$P/patches/${PB}" >> "$LOG" 2>&1
bash "$R" y8v-fight-random test-m-fight.iso 12000 4.0 "4700,6300,9000,11900" "$S/newgame_only.txt" "$S/wait_3700.txt" random 4 "$P/patches/${PB}-kit" >> "$LOG" 2>&1
echo "batch done" >> "$LOG"
