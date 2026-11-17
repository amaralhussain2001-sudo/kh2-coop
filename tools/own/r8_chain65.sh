#!/bin/bash
# TEST ONLY (eighth round, job 11 = plan row 39, stage 1a): candidate v62, PLAYER 2'S PAUSE MENU IN THREE HARDER PLACES
#   om9   in a fight (hb17 66, HP held): he attacks, opens the menu at 5600, closes it at 6000, attacks on
#   om10  while he is in a Drive Form (the quiet Borough disc, forms kit): menu 5500 to 5800, revert at 6000
#   om11  as ROXAS at the real start of the game (the v5 disc, New Game): menu 9200 to 9700
# (om9 / om10 with item 0x35 in the hero's accessory place and 0x28 in player 2's, written once at 4300.)
# ONE RUN AT A TIME, hidden. Logs local/sweep/b15/om9.log ..; progress chain65.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain65.txt"; }
tlb() { grep -a -B2 'TLB Miss' local/run-m/p1/logs/emulog.txt | head -30 > "$B/$1-tlb.txt"; }
say "chain65 start"
CH=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4
RG=0032E020:40,000E7D00:40,000E7E20:C
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG SNAPS="5200,5700,5900,6200,6900" FRAMES=7000 LOGDIR=local/sweep/b15 TAG=r8om9 P1S="$O/mash_new40_p1.txt" P2S="$O/ownmenu_fight_p2.txt" bash tools/own/sweep4.sh om9 run-m 29050 28081 test-own-v62-snapB-god-acc "$L/list-hb17.txt"
tlb om9; say "om9 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG bash tools/own/dusk_one.sh om10 "$P/patches/test-own-v62-forms-acc" test-s1-hb9f.iso 7000 "5000,5400,5650,5900,6300,6900" "$S/newgame_only.txt" "$O/ownmenu_form_p2.txt" run-m 29050 28081 > "$B/om10.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/om10.log"; cat "$P/local/tests/om10-probe.txt" >> "$B/om10.log" 2>/dev/null
say "om10 done"
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG bash tools/own/dusk_one.sh om11 "$P/patches/test-own-v62" kh2-coop-v5.iso 10200 "8900,9400,9600,9900,10100" "$S/newgame_p1.txt" "$O/ownmenu_roxas_p2.txt" run-m 29050 28081 > "$B/om11.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/om11.log"; cat "$P/local/tests/om11-probe.txt" >> "$B/om11.log" 2>/dev/null
say "om11 done"
say "chain65 through"
