#!/bin/bash
# TEST ONLY (ninth round), the Keyblade candidate v100 on the four sandboxes the pool sweep leaves free:
#  f8A (run-m)    REGISTER F8, the fault line "pc 0x00168B38, address 4" when player 2 takes Final Form: the recorder at that routine
#                 (make_rec_bar0.py) names the caller. Fight disc hb9f, kit -forms, player 2: final_p2.txt.
#  kfA (run-v3)   A DRIVE FORM WITH TWO DIFFERENT KEYBLADES: player 2's Keyblade is Oblivion (written at 3800), he takes the first form
#                 at 4700 and reverts at 6000. Which weapons does his form body hold, and his normal body afterwards.
#  kfB (run-v3b)  BOTH in a form (player 1 Valor at 4700, player 2 the first row of his list at 5400), player 2's Keyblade Oblivion.
#  scA (run-v3c)  THE SHORTCUTS: player 1's are Fire / Blizzard / Thunder / Cure (the -kit kit), player 2's are written once in the
#                 other order (Cure / Thunder / Blizzard / Fire). Player 2 holds L1 from 5000: the picture p2_f005060 shows his row.
# Logs local/sweep/r9/f8A.log ..; progress chain8.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain8.txt"; }
say "chain8 start"
one() {  # one <name> <kit> <iso> <frames> <snaps> <p1script> <p2script> <sandbox> <port> <pine> <probe>
  PROBE="$T/${11}" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh r9$1 "$P/patches/$2" $3 $4 "$5" "$6" "$7" $8 $9 ${10} > "$B/$1.log" 2>&1
  echo "TLB misses $(grep -ac 'TLB Miss' local/$8/p1/logs/emulog.txt)" >> "$B/$1.log"
  grep -a 'TLB Miss' local/$8/p1/logs/emulog.txt | head -8 >> "$B/$1.log"
  cat "$P/local/tests/r9$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  say "$1 done"
}
one f8A test-own-v100-forms-bar test-s1-hb9f.iso 6600 "4690,5000,5600,6400" "$S/newgame_only.txt" "$O/final_p2.txt" run-m 29050 28081 rec_probe.py &
one kfA test-own-v100-forms-kb test-s1-hb9f.iso 7000 "4690,5000,5400,5900,6300,6900" "$S/newgame_only.txt" "$O/drive2_p2.txt" run-v3 30150 28061 kb_probe.py &
one kfB test-own-v100-forms-kb test-s1-hb9f.iso 7600 "4690,5000,5350,5700,6200,6600,7000,7500" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-v3b 30350 28062 kb_probe.py &
one scA test-own-v100-sc test-m-roam.iso 5400 "4690,5060,5200" "$S/newgame_only.txt" "$O/menu_p2.txt" run-v3c 30550 28063 kb_probe.py &
wait
say "chain8 through"
