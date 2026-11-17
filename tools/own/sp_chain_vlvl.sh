#!/bin/bash
# TEST ONLY (2026-11-13): the form EXP test, Valor LEVEL-UP with both heroes: kit -forms-vexp (EXP = 1000 at 5100), friends fight disc.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"
cd "$P" || exit 1
SN="4820,4860,4900,5200,5500,5800,6100,6400,6900"
R="0032EE24:8,0032EE5C:8,0032EE94:8,0032EECC:8,0032EF04:8"
( RANGES=$R PROBE="$P/tools/own/memdump_probe.py" bash tools/own/dusk_one.sh t13-vlvl-p2 "$P/patches/test-own-v33-forms-vexp" test-g-friends.iso 7000 "$SN" "$S/newgame_only.txt" "$O/valor_fight_p2.txt" run-m 29050 28081 > local/sweep/b13/vlvl-p2.log 2>&1; echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> local/sweep/b13/vlvl-p2.log ) &
( RANGES=$R PROBE="$P/tools/own/memdump_probe.py" bash tools/own/dusk_one.sh t13-vlvl-p1 "$P/patches/test-own-v33-forms-vexp" test-g-friends.iso 7000 "$SN" "$O/valor_fight_p1.txt" "$O/idle.txt" run-v3 30150 28061 > local/sweep/b13/vlvl-p1.log 2>&1; echo "TLB misses $(grep -c 'TLB Miss' local/run-v3/p1/logs/emulog.txt)" >> local/sweep/b13/vlvl-p1.log ) &
wait
