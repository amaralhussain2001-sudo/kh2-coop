#!/bin/bash
# TEST ONLY (ninth round, plan row 39): CANDIDATE v98 (= v97 + the sixty-third glue --ownkey: player 2's own Keyblade), two lanes
# beside the regression of v97 (run-x5 / run-x6 only):
#  kbA (run-x5)  PLAYER 1 changes his Keyblade in his menu (Kingdom Key -> the next one), both attack afterwards.
#                Expected: player 1 holds the new Keyblade, player 2 still the Kingdom Key (its files now have the number 2303).
#  kbB (run-x6)  PLAYER 2 changes HIS Keyblade in his menu, both attack afterwards. Expected: only the twin's changes.
#  kbC (run-x5)  player 2's Keyblade is another one from the start (written at frame 4300): does the twin get it when the room is built.
#  kbD (run-x6)  kbB, then PLAYER 1 changes his too (both hold the same again at the end).
# Probe tools/own/kb_probe.py. Logs local/sweep/r9/kbA.log ..; progress chain4.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
mkdir -p "$B"; cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain4.txt"; }
say "chain4 start"
run() {  # run <worker> <sandbox> <port> <pine> <kit> <p1script> <p2script> <snaps> <frames>
  ISO=test-v5-tt137.iso PROBE="$T/kb_probe.py" SNAPS=$8 FRAMES=$9 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$6" P2S="$7" bash tools/own/sweep4.sh $1 $2 $3 $4 $5 "$L/list-hb13.txt"
  say "$1 done"
}
SN="4900,5060,5360,5540,5860,5960,6200,6600,7000,7400"
( run kbA run-x5 31550 28068 test-own-v98-kb1 "$O/keychg2_p1.txt" "$O/keychg_p2.txt" $SN 7500
  run kbC run-x5 31550 28068 test-own-v98-kb2 "$S/newgame_only.txt" "$O/keychg_p2.txt" "4900,5360,6200,7000" 7200 ) &
( run kbB run-x6 31750 28069 test-own-v98-kb1 "$O/kb_atk_p1.txt" "$O/keychg2_p2.txt" $SN 7500 ) &
wait
say "chain4 through"
