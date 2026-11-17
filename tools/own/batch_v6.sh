#!/bin/bash
# Own-screen test batch for the final own-screen patch (merged-v6-own): the runs of the first batch (u1..u7)
# again, with the test-kit variant where menus matter. Hidden desktop, own-view emulator on both copies.
# usage: bash tools/own/batch_v6.sh     -> log local/own-batch.log, results local/tests/x*-...
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S="$P/tests/scripts/merge"
O="$P/tests/scripts/own"
R="$P/tools/own/run_own.sh"
LOG="$P/local/own-batch.log"
: > "$LOG"
bash "$R" x1-long-roam test-m-roam.iso 34000 4.0 "4700,7300,12000,18000,24000,33900" "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random 4 "$P/patches/test-own-v6-kit" >> "$LOG" 2>&1
bash "$R" x2-cont test-m-roam.iso 16000 2.0 "6600,7000,8000,9000,9100,9700,10300,11000,12000,13000,15900" "$S/save_cont_p1.txt" "$S/save_cont_p2.txt" idle 4 "$P/patches/test-own-v6-die2" >> "$LOG" 2>&1
bash "$R" x4-menu test-m-roam.iso 5300 2.0 "4800,4850,5040,5100,5150,5250" "$O/menu_p1.txt" "$O/menu_p2.txt" idle 4 "$P/patches/test-own-v6-kit" >> "$LOG" 2>&1
bash "$R" x6-pace test-m-fight.iso 5800 1.0 "4700,5200,5700" "$S/atk_p1.txt" "$S/atk_p2.txt" idle 4 "$P/patches/merged-v6-own" >> "$LOG" 2>&1
bash "$R" x7-newgame kh2-coop-v2.iso 9000 2.0 "5180,6400,6912,8900" "$S/newgame_p1.txt" "$S/newgame_p2.txt" random 4 "$P/patches/merged-v6-own" >> "$LOG" 2>&1
bash "$R" x8-fight-random test-m-fight.iso 12000 4.0 "4700,6300,9000,11900" "$S/newgame_only.txt" "$S/wait_3700.txt" random 4 "$P/patches/test-own-v6-kit" >> "$LOG" 2>&1
echo "batch done" >> "$LOG"
