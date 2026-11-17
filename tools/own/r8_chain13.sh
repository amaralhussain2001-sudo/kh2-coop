#!/bin/bash
# TEST ONLY (eighth round, register G5, second tries). ONE RUN AT A TIME on sandbox run-m.
#   eth2  player 2's Ether, tried four times after five Fire spells (run eth's one try was broken off by a hit)
#   gh2   who heals player 2 (Mulan carries two Potions, player 2's HP is set to 3 at 6000): the helpers' action
#         words in the timeline (tools/own/heal_poll_probe.py)
#   ex13  Merlin's House with helpers (disc test-s1-hb13s): where do the heroes stand and which way do "stick up"
#         and "stick right" move them? (for the Final Form door test; the door's box is at -645 / -550)
# Logs: local/sweep/b15/eth2.log, gh2.log, ex13.log
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
PROBE="$T/hp_poll_probe.py" FROM=4600 TO=6400 SNAPS="4690,5290,5440,5590,5740,6400" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8eth2 \
  P1S="$O/mash_new40_p1.txt" P2S="$O/ether2_p2.txt" bash tools/own/sweep4.sh eth2 run-m 29050 28081 test-own-v33-snapB-eth "$L/list-hb17.txt"
echo "eth2 done $(date +%H:%M:%S)" >> "$B/chain13.txt"
PROBE="$T/heal_poll_probe.py" FROM=5950 TO=6400 WATCH=0032E5B8:4 SNAPS="5990,6020,6040,6060,6100,6400" FRAMES=6500 LOGDIR=local/sweep/b15 TAG=r8gh2 \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh gh2 run-m 29050 28081 test-own-v33-snapB-strong-mulan-low "$L/list-mu08.txt"
echo "gh2 done $(date +%H:%M:%S)" >> "$B/chain13.txt"
POINTS="-645:-550" PROBE="$T/pos_probe.py" bash tools/own/dusk_one.sh t15-ex13 "$P/patches/test-own-v33-forms" test-s1-hb13s.iso 5400 "4690,4790,4850,4990,5050,5300" "$O/explore_p1.txt" "$O/explore_p2.txt" run-m 29050 28081 > "$B/ex13.log" 2>&1
cat "$P/local/tests/t15-ex13-probe.txt" >> "$B/ex13.log" 2>/dev/null
echo "ex13 done $(date +%H:%M:%S)" >> "$B/chain13.txt"
# (added 2026-11-14 00:46) gu2 / gu3: plan row 43 again in a QUIET room (run gu: player 1 died too, Game Over). Merlin's House
# (roam disc), the twin falls at 4800 and gets up by himself about 340 frames later (the timer runs 8 times faster outside a
# fight): candidate v37 -> 6 of 20 HP, build 12 -> 5 of 20. HP timelines.
S="$P/tests/scripts/merge"
for kv in "gu2 test-own-v37-kill48p2" "gu3 test-own-v33-kill48p2"; do set -- $kv
  PROBE="$T/hp_poll_probe.py" FROM=4700 TO=5900 bash tools/own/dusk_one.sh t15-$1 "$P/patches/$2" test-m-roam.iso 6000 "4690,4900,5300,5900" "$S/newgame_only.txt" "$O/idle.txt" run-m 29050 28081 > "$B/$1.log" 2>&1
  cat "$P/local/tests/t15-$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  echo "$1 done $(date +%H:%M:%S)" >> "$B/chain13.txt"
done
# tf2 / tf0: plan row 44, two Drive Forms at once (quiet Borough with Donald and Goofy, kit -forms + the heap recorder): player 1 takes
# Valor at 4700, player 2 takes the first row of HIS list at 5400, he reverts at 6400, player 1 at 6800, player 2 opens the list again.
# tf2 = candidate v37 (thirty-fourth glue), tf0 = build 12 (the control: his Drive must do nothing there).
TF="4690,5000,5380,5450,5540,5700,5900,6300,6480,6600,6780,6950,7100,7280,7400,7500"
for kv in "tf2 test-own-v37-forms-heap" "tf0 test-own-v33-forms-heap"; do set -- $kv
  PROBE="$T/heap_probe.py" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh t15-$1 "$P/patches/$2" test-s1-hb9f.iso 7600 "$TF" "$O/twoforms_p1.txt" "$O/twoforms_p2.txt" run-m 29050 28081 > "$B/$1.log" 2>&1
  echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/$1.log"
  cat "$P/local/tests/t15-$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  echo "$1 done $(date +%H:%M:%S)" >> "$B/chain13.txt"
done
echo "chain13 through $(date +%H:%M:%S)" >> "$B/chain13.txt"
