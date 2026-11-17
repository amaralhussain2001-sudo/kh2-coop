#!/bin/bash
# TEST ONLY: on run-v3c after the Gummi route runs: one no-patch control, three runs with the patch on the plain
# jump disc (fault lines kept), then the Gummi checks on the new merge code, then a sweep worker (list x2).
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"
cd "$P" || exit 1
while ! grep -q "gum routes" local/sweep/gummi-v28.log 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 10" > /dev/null; done
bash tools/own/sp_batch.sh test-empty run-v3c 30550 28063 spc2 test-s1-tt137.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-spc2.txt
bash tools/own/sp_batch.sh test-own-v29-snapB run-v3c 30550 28063 spp test-s1-tt137.iso "$O/sp_p1.txt" "$O/sp_p2.txt" local/sweep/list-spp.txt
G="$P/local/sweep/gum29.log"
one() {  # name kit frames snaps p1 p2
  out=$(PROBE="$P/tools/own/gummi_probe.py" bash "$P/tools/own/dusk_one.sh" "$1" "patches/test-own-v29-$2" test-s1-tt137.iso "$3" "$4" "$5" "$6" run-v3c 30550 28063 2>&1 | head -n 1)
  echo "$1 | $out | TLB misses $(grep -c 'TLB Miss' "$P/local/run-v3c/p1/logs/emulog.txt")" >> "$G"
  sed 's/^/    /' "$P/local/tests/$1-probe.txt" | cut -c1-200 >> "$G"
}
one g9-ships gum0 12000 "5200,6000,6400,6800,7200,7600,8200,8500,8800,9100,9500,10500,11900" "$O/gum2_p1.txt" "$O/gum2_p2.txt"
one g9-pause gum0 12000 "7800,8100,8300,8500,8700,8900,9100,9300,9450,9600,9800,10200,10600,11900" "$O/gumpause_p1.txt" "$O/gumpause_p2.txt"
one g9-p2menu gum0 12000 "4800,5600,6400,7200,7900,8200,8700,9000,9600,10500,11900" "$O/gum_new_p1.txt" "$O/gum_fly_p2.txt"
echo "gum29 done" >> "$G"
bash tools/own/sweep1.sh x2 run-v3c 30550 28063 test-own-v28-snapB local/sweep/list-x2.txt type2
