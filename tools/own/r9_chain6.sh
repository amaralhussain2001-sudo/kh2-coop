#!/bin/bash
# TEST ONLY (ninth round, plan row 39): CANDIDATE v100 (= v99 + kb_fix: the twin gets his Keyblade as soon as its files are loaded; names kcE .. kcH; player 2 stands still in kcH
# files), on run-x5 / run-x6 beside the regression of v97:
#  kbE (run-x5)  PLAYER 1 changes his Keyblade, both attack (run kbA again: now without a fault line?).
#  kbF (run-x6)  PLAYER 2 changes his, both attack (run kbB again).
#  kcG (run-x5)  THE ROOM CHANGE: the roam disc, player 2's Keyblade is Oblivion from the start (kit), both walk through the door
#                and back (the regression's roundtrip scripts). Expected after the door: the twin holds Oblivion, files 2303.
#  kbH (run-x6)  PLAYER 2 changes his (5000), then PLAYER 1 changes his to the same one (6300): one set of files again.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"; M="$P/tools/merge"
mkdir -p "$B"; cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain6.txt"; }
say "chain6 start"
run() {  # run <worker> <sandbox> <port> <pine> <kit> <p1script> <p2script> <snaps> <frames>
  ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS=$8 FRAMES=$9 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$6" P2S="$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$L/list-hb13.txt"
  say "$1 done"
}
SN="4900,5060,5360,5540,5860,5960,6200,6600,7000,7400"
( run kcE run-x5 31550 28068 test-own-v100-kb1 "$O/keychg2_p1.txt" "$O/keychg_p2.txt" $SN 7500
  r=$(MRUN_DIR=run-x5 MRUN_PORT=31550 MRUN_PINE=28068 bash "$M/krunx.sh" r9kcG test-m-roam.iso 7400 2.0 "4700,5600,6200,7200" 2 "$S/rt_p1.txt" "$S/rt_p2.txt" idle "$P/patches/test-own-v100-kb2" 2>&1 | head -1 | cut -c12-90)
  echo "kcG: $r | p1 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-x5/p1/logs/emulog.txt") | p2 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-x5/p2/logs/emulog.txt" 2>/dev/null)" > "$B/kcG.log"
  cat "$P/local/tests/r9kcG/probe.txt" >> "$B/kcG.log"; say "kcG done" ) &
( run kcF run-x6 31750 28069 test-own-v100-kb1 "$O/kb_atk_p1.txt" "$O/keychg2_p2.txt" $SN 7500
  run kcH run-x6 31750 28069 test-own-v100-kb1 "$O/kb_late_p1.txt" "$O/keychg3_p2.txt" "4900,5860,6200,6840,7160,7400,8000,8300" 8400 ) &
wait
say "chain6 through"
