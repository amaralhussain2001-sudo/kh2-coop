#!/bin/bash
# TEST ONLY (eighth round, plan row 39 stage 1b; A LANE BESIDE THE OTHERS, sandbox run-x4, port 31350, PINE 28067):
# candidate v91, PLAYER 2 IN A DRIVE FORM opens his pause menu (5500) and closes it (5800), as run om10 of stage 1a
# (kit -forms + the ability writes of frame 4300: hero 819F / 01A0, player 2's switches 0002).
# Log local/sweep/b15/om14.log; progress chain120.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
RD=run-x4; PT=31350; PN=28067
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain120.txt"; }
say "chain120 start"
CH=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4
RG=0032E074:8,000E7D54:8,0032E390:C,000E7E20:C
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG bash tools/own/dusk_one.sh om14 "$P/patches/test-own-v91-forms-ab" test-s1-hb9f.iso 7000 "5000,5400,5650,5900,6300,6900" "$S/newgame_only.txt" "$O/ownmenu_form_p2.txt" $RD $PT $PN > "$B/om14.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/$RD/p1/logs/emulog.txt)" >> "$B/om14.log"; cat "$P/local/tests/om14-probe.txt" >> "$B/om14.log" 2>/dev/null
say "om14 done"
say "chain120 through"
