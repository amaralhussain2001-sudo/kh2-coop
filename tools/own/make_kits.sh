#!/bin/bash
# TEST ONLY: every kit folder the regression needs beside one own-screen patch folder (seventh round).
#   -kit -die2 -forms -formdie -rec -mail -fheal -limit        (final_b9.sh, batch_v7.sh)
#   -summon                                                    (final_b10.sh)
#   -sumcs -sumdie1 -once -once-snapB                          (final_b11.sh)
#   -snapB -sumkill -sumkill7 -hitems0 -hitems -moogle -wm -gum0 .. -gum8   (final_b12.sh, gum_routes2.sh)
# usage: bash tools/own/make_kits.sh <ownPatchDirName>          (the folder patches/<name> must exist)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
cd "$P" || exit 1
X="patches/$1"
[ -f "$X/SLPM-66675_F266B00B.pnach" ] || { echo "no patch in $X"; exit 1; }
K="python -I tools/own/make_kit2.py"
$K "$X" "$X-kit" --magic > /dev/null
$K "$X" "$X-die2" --die=both > /dev/null
$K "$X" "$X-forms" --magic --forms=56 --limit --drive=5 --formkeys > /dev/null
$K "$X" "$X-formdie" --magic --forms=56 --limit --drive=5 --formkeys --die=both > /dev/null
python -I tools/own/make_rec_offer.py "$X" "$X-rec" 299 > /dev/null
python -I tools/own/make_mailpins.py "$X" "$X-mail" > /dev/null
python -I tools/own/make_healkit.py "$X" "$X-fheal" p2 4900 3 --p1slot=01C6C750 --p2slot=01C6C018 > /dev/null
$K "$X" "$X-limit" --limits > /dev/null
$K "$X" "$X-summon" --magic --forms=56 --limit --formkeys --drive=5 --byte=36C4:39 > /dev/null
$K "$X" "$X-sumcs" --magic --forms=5F --limit --formkeys --drive=5 > /dev/null
$K "$X" "$X-sumdie1" --magic --forms=56 --limit --formkeys --drive=5 --byte=36C4:39 --die=both > /dev/null
python -I tools/own/make_healkit.py "$X" "$X-once" both 9000 1 --nocure --p1slot=01C6C750 --p2slot=01C6C4E8 > /dev/null
python -I tools/own/make_snaptest.py "$X-once" "$X-once-snapB" B > /dev/null
python -I tools/own/make_snaptest.py "$X" "$X-snapB" B > /dev/null
# final_b12.sh (seventh round)
python -I tools/own/make_killkit.py "$X-summon" "$X-sumkill" hero@7700,twin@7700 > /dev/null
python -I tools/own/make_killkit.py "$X-summon" "$X-sumkill7" hero@7000,twin@7000 > /dev/null
python -I tools/own/make_hitemkit.py "$X" "$X-hitems0" > /dev/null
python -I tools/own/make_healkit.py "$X-hitems0" "$X-hitems" p2 4900 3 --nocure --p1slot=01C6C750 --p2slot=01C6C018 > /dev/null
# player 2's hero held 60 units beside the Moogle of the disc test-s1-hb10m (the twin's object there: 0x01A93E90)
python -I tools/own/make_pin.py "$X" "$X-moogle" 000F05CC 3E90 01A93F00=C47DC000 01A93F08=44898000 01A943D0=C47DC000 01A943D8=44898000 01A94420=C47DC000 01A94428=44898000 01A94450=C47DC000 01A94458=44898000 01A94570=C47DC000 01A94578=44898000 01A945B0=C47DC000 01A945B8=44898000 01A945C0=C47DC000 01A945C8=44898000 01A946D0=C47DC000 01A946D8=44898000 01A94AD0=C47DC000 01A94AD8=44898000 > /dev/null
# the Gummi tests: New Game jumps to the world map (Type 1 jump kit), there route N starts by itself
python -I tools/own/make_jumpkit.py "$X" "$X-wm" 0F 0 --type1 > /dev/null
for r in 0 1 2 3 4 5 6 7 8; do python -I tools/own/make_gumlaunch.py "$X-wm" "$X-gum$r" $r > /dev/null; done
ls -d "$X"-* | wc -l
