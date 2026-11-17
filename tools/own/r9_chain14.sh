#!/bin/bash
# TEST ONLY (ninth round, plan row 39): CANDIDATE v103 (= v102 + kb_after: the twin gets his Keyblade when the heroes are sorted out
# while the room is built; never while a scene plays). Player 2's Keyblade is Oblivion from the start. Four lanes:
#  sfA (run-m)    the Storm Rider mission, attack only (run srC again: does the fight start now, and what does the twin hold)
#  sfB (run-v3)   KING MICKEY'S RESCUE FOR TWO at Storm Rider (both fall at 6500, the roll always wins), attack only
#  sfC (run-v3b)  a save, a Game Over and "Continue" (run keB again)
#  sfD (run-v3c)  a door and back (run kdD again), then sfE: PLAYER 2 changes his Keyblade in his menu (run kcF again)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; M="$P/tools/merge"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain14.txt"; }
say "chain14 start"
MS="5200,6400,6700,6900,7400,8000,9000,10000,11000,11500,11900,12100,12300,12500,12800,13200,13900"
( ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS="5200,6400,7400,8000,9000,9400" FRAMES=9500 TOUT=600 LOGDIR=local/sweep/r9 TAG=r9sfA P1S="$O/mashO_p1.txt" P2S="$O/mashO_p2.txt" bash tools/own/sweep4.sh sfA run-m 29050 28081 test-own-v103-mk0 "$L/list-sr1.txt"; say "sfA done" ) &
( ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS=$MS FRAMES=14000 TOUT=700 SWEEP_PROBE_WAIT=700 LOGDIR=local/sweep/r9 TAG=r9sfB P1S="$O/mashO_p1.txt" P2S="$O/mashO_p2.txt" bash tools/own/sweep4.sh sfB run-v3 30150 28061 test-own-v103-mk "$L/list-sr1.txt"; say "sfB done" ) &
( PROBE="$T/kb_probe.py" SWEEP_PROBE_WAIT=900 bash tools/own/dusk_one.sh r9sfC "$P/patches/test-own-v103-die2-kb" test-m-roam.iso 16000 "6600,7000,8000,9000,9100,9700,10300,12000,15900" "$S/save_cont_p1.txt" "$S/save_cont_p2.txt" run-v3b 30350 28062 > "$B/sfC.log" 2>&1
  echo "TLB misses $(grep -ac 'TLB Miss' local/run-v3b/p1/logs/emulog.txt)" >> "$B/sfC.log"; cat "$P/local/tests/r9sfC-probe.txt" >> "$B/sfC.log" 2>/dev/null; say "sfC done" ) &
( r=$(MRUN_DIR=run-v3c MRUN_PORT=30550 MRUN_PINE=28063 bash "$M/krunx.sh" r9sfD test-m-roam.iso 7400 2.0 "4700,5600,6200,7200" 2 "$S/rt_p1.txt" "$S/rt_p2.txt" idle "$P/patches/test-own-v103-kb38" 2>&1 | head -1 | cut -c12-90)
  echo "sfD: $r | p1 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-v3c/p1/logs/emulog.txt") | p2 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-v3c/p2/logs/emulog.txt" 2>/dev/null)" > "$B/sfD.log"
  cat "$P/local/tests/r9sfD/probe.txt" >> "$B/sfD.log"; say "sfD done"
  ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS="4900,5540,5860,6200,7000,7400" FRAMES=7500 LOGDIR=local/sweep/r9 TAG=r9sfE P1S="$O/kb_atk_p1.txt" P2S="$O/keychg2_p2.txt" bash tools/own/sweep4.sh sfE run-v3c 30550 28063 test-own-v103-kb1 "$L/list-hb13.txt"; say "sfE done" ) &
wait
say "chain14 through"
