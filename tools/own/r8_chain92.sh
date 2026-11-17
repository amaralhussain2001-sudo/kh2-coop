#!/bin/bash
# TEST ONLY (eighth round, the vehicle items: the three one-hero small games): A FIRST LOOK with what the round has
# learned. The seventh round's test disc with a SECOND copy of every special player object, the original built
# first (test-s1-tt137sp3.iso), and candidate v84 = the final candidate v81 + the fifty-third glue (--norec: a hero
# without a character record has no item places) + the fifty-fourth (--escape2) + the fifty-fifth (--sidecar2).
#   sp-r8-nm63  the toy cannon with two cannons       (seventh round: 50 fault lines, player 2's view wrong)
#   sp-r8-al61  the carpet escape with two heroes     (seventh round: 50 fault lines, confused pictures)
#   sp-r8-eh72  the sidecar with two heroes           (the same)
# ONE RUN AT A TIME, hidden, sandbox run-m. Log local/sweep/sp-r8.log; progress local/sweep/b15/chain92.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
echo "chain92 start $(date +%H:%M:%S)" >> local/sweep/b15/chain92.txt
bash tools/own/sp_batch.sh test-own-v84-snapB run-m 29050 28081 sp-r8 test-s1-tt137sp3.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-sp-r8.txt
for n in sp-r8-nm63 sp-r8-al61 sp-r8-eh72; do echo "$n: $(wc -l < "local/tests/$n-emulog.txt" 2>/dev/null) fault lines kept" >> local/sweep/b15/chain92.txt; done
echo "chain92 through $(date +%H:%M:%S)" >> local/sweep/b15/chain92.txt
