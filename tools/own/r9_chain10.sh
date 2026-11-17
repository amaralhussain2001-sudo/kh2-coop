#!/bin/bash
# TEST ONLY (ninth round, plan row 39): CANDIDATE v101 (= v100 + the sixty-fourth glue --bindname), player 2's own Keyblade, the last
# cases, on the four sandboxes the pool sweep leaves free. Player 2's Keyblade is Oblivion from the start (written at frame 3800).
#  kdA (run-m)    BOTH THE SAME: player 1 changes his Keyblade to Oblivion too. Expected: one set of files again (no 2303), both hold it.
#  kdB (run-v3)   A SAVE, A GAME OVER AND "CONTINUE" (the regression's scripts, both heroes' HP held at 1): his Keyblade and his item
#                 places after the Continue.
#  kdC (run-v3b)  KING MICKEY'S RESCUE FOR TWO at Storm Rider (both heroes fall at 6500, the roll always wins): his Keyblade when the
#                 heroes are back.
#  kdD (run-v3c)  A DOOR AND BACK with player 2 attacking in each room (the roam disc).
# Probe tools/own/kb_probe.py. Logs local/sweep/r9/kdA.log ..; progress chain10.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; M="$P/tools/merge"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain10.txt"; }
say "chain10 start"
( ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS="4900,5360,5540,5860,6200,6600,7000,7400" FRAMES=7500 LOGDIR=local/sweep/r9 TAG=r9kdA P1S="$O/keychg2_p1.txt" P2S="$O/keychg_p2.txt" bash tools/own/sweep4.sh kdA run-m 29050 28081 test-own-v101-kb38 "$L/list-hb13.txt"; say "kdA done" ) &
( PROBE="$T/kb_probe.py" SWEEP_PROBE_WAIT=900 bash tools/own/dusk_one.sh r9kdB "$P/patches/test-own-v101-die2-kb" test-m-roam.iso 16000 "6600,7000,8000,9000,9100,9700,10300,11000,12000,13000,15900" "$S/save_cont_p1.txt" "$S/save_cont_p2.txt" run-v3 30150 28061 > "$B/kdB.log" 2>&1
  echo "TLB misses $(grep -ac 'TLB Miss' local/run-v3/p1/logs/emulog.txt)" >> "$B/kdB.log"; cat "$P/local/tests/r9kdB-probe.txt" >> "$B/kdB.log" 2>/dev/null; say "kdB done" ) &
( ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS="5200,6400,6700,6900,7400,8000,9000,10000,11000,11500,11900,12100,12300,12500,12800,13200,13900" FRAMES=14000 TOUT=700 SWEEP_PROBE_WAIT=700 LOGDIR=local/sweep/r9 TAG=r9kdC P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh kdC run-v3b 30350 28062 test-own-v101-mk "$L/list-sr1.txt"; say "kdC done" ) &
( r=$(MRUN_DIR=run-v3c MRUN_PORT=30550 MRUN_PINE=28063 bash "$M/krunx.sh" r9kdD test-m-roam.iso 7400 2.0 "4700,5600,6200,7200" 2 "$S/rt_p1.txt" "$S/rt_p2.txt" idle "$P/patches/test-own-v101-kb38" 2>&1 | head -1 | cut -c12-90)
  echo "kdD: $r | p1 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-v3c/p1/logs/emulog.txt") | p2 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-v3c/p2/logs/emulog.txt" 2>/dev/null)" > "$B/kdD.log"
  cat "$P/local/tests/r9kdD/probe.txt" >> "$B/kdD.log"; say "kdD done" ) &
wait
say "chain10 through"
