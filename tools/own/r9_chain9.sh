#!/bin/bash
# TEST ONLY (ninth round), REGISTER F8 (one fault line "pc 0x00168B38, address 4" when player 2 takes Final Form), on the Keyblade
# candidate v100 with the recorder at that routine (make_rec_bar0.py): the two runs in which F8 was seen in the eighth round:
#  f8B (run-m)   ffd3 again: Merlin's House with the helpers (disc hb13s), player 2 takes Final Form and goes through the west door.
#  f8C (run-v3)  tf8b again: the fight disc hb9f, player 1 Limit Form, player 2 Final.
# Logs local/sweep/r9/f8B.log, f8C.log; progress chain9.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain9.txt"; }
say "chain9 start"
one() {  # one <name> <kit> <iso> <frames> <snaps> <p1script> <p2script> <sandbox> <port> <pine> <probe>
  PROBE="$T/${11}" SWEEP_PROBE_WAIT=400 bash tools/own/dusk_one.sh r9$1 "$P/patches/$2" $3 $4 "$5" "$6" "$7" $8 $9 ${10} > "$B/$1.log" 2>&1
  echo "TLB misses $(grep -ac 'TLB Miss' local/$8/p1/logs/emulog.txt)" >> "$B/$1.log"
  grep -a 'TLB Miss' local/$8/p1/logs/emulog.txt | head -8 >> "$B/$1.log"
  cat "$P/local/tests/r9$1-probe.txt" >> "$B/$1.log" 2>/dev/null
  say "$1 done"
}
one f8B ${KIT:-test-own-v100-forms-bar} test-s1-hb13s.iso 7400 "4690,5250,5600,6100,6450,6900,7350" "$O/finaldoor3_p1.txt" "$O/finaldoor3_p2.txt" run-m 29050 28081 rec_probe.py &
one f8C ${KIT:-test-own-v100-forms-bar} test-s1-hb9f.iso 8000 "4690,5380,5700,6300,6780,7400,7900" "$O/limitf2_p1.txt" "$O/finalf2_p2.txt" run-v3 30150 28061 rec_probe.py &
wait
say "chain9 through"
