#!/bin/bash
# TEST ONLY (eighth round, job 11 = plan row 39, stage 1a): candidate v62, two menu tests aimed better than om9 / om11
# (there START opened the game's pause screen: a mission fight, a story scene):
#   om12  as ROXAS at the real start with free control: player 2's menu 8920 to 9120
#   om13  a free-roam fight (the fight disc, Heartless around): player 2 attacks, menu 5600 to 6000, attacks on;
#         item 0x35 in the hero's accessory place and 0x28 in player 2's (written once at 4300)
# ONE RUN AT A TIME, hidden. Logs local/sweep/b15/om12.log, om13.log; progress chain67.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; B="$P/local/sweep/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain67.txt"; }
say "chain67 start"
CH=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4
RG=0032E020:40,000E7D00:40,000E7E20:C
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG bash tools/own/dusk_one.sh om12 "$P/patches/test-own-v62" kh2-coop-v5.iso 9600 "8900,9000,9080,9200,9400,9500" "$S/newgame_p1.txt" "$O/ownmenu_roxas2_p2.txt" run-m 29050 28081 > "$B/om12.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/om12.log"; cat "$P/local/tests/om12-probe.txt" >> "$B/om12.log" 2>/dev/null
say "om12 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG bash tools/own/dusk_one.sh om13 "$P/patches/test-own-v62-acc" test-m-fight.iso 7000 "5200,5700,5900,6200,6500,6900" "$S/fight_idle_p1.txt" "$O/ownmenu_fight2_p2.txt" run-m 29050 28081 > "$B/om13.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/om13.log"; cat "$P/local/tests/om13-probe.txt" >> "$B/om13.log" 2>/dev/null
say "om13 done"
say "chain67 through"
