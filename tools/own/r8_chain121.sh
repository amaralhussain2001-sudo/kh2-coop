#!/bin/bash
# TEST ONLY (eighth round, plan row 39 stage 1b; A LANE BESIDE THE OTHERS, sandbox run-x4, port 31350, PINE 28067):
# candidate v91, PLAYER 2 IN A DRIVE FORM opens his pause menu (5500) and closes it (5800), as run om10 of stage 1a
# Run om14 again with a kit that writes the hero's five abilities ONCE at frame 4300 (kit -forms2-ab: the -forms kit writes them every frame, which also overwrote what player 2's menu showed); player 2's switches 0002.
# Log local/sweep/b15/om15.log; progress chain121.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
RD=run-x4; PT=31350; PN=28067
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain121.txt"; }
say "chain121 start"
CH=0034E948+48C@180:10,000F05CC+48C@180:10,0034E948+48C@244:4,000F05CC+48C@244:4
RG=0032E074:C,000E7D54:C,0032E390:C,000E7E20:C
PROBE="$T/sweepm_probe.py" CHAINS=$CH RANGES=$RG bash tools/own/dusk_one.sh om15 "$P/patches/test-own-v91-forms2-ab" test-s1-hb9f.iso 7000 "5000,5400,5650,5900,6300,6900" "$S/newgame_only.txt" "$O/ownmenu_form_p2.txt" $RD $PT $PN > "$B/om15.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/$RD/p1/logs/emulog.txt)" >> "$B/om15.log"; cat "$P/local/tests/om15-probe.txt" >> "$B/om15.log" 2>/dev/null
say "om15 done"
say "chain121 through"
