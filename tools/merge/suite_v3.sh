#!/bin/bash
# Combined test suite for merged build 3 (repeats the merge lane's tests with patches/merged-v3).
# usage: bash tools/merge/suite_v3.sh [patchDir]     -> log in local/m3-suite.log, results in local/tests/m3-*
P="/c/Users/PC FORCE/Desktop/New folder (3)"
PD="${1:-$P/patches/merged-v3}"
S="$P/tests/scripts/merge"
M="$P/tools/merge"
LOG="$P/local/m3-suite.log"
: > "$LOG"
[ -f "$PD/SLPM-66675_F266B00B.pnach" ] || { echo "NO PATCH FILE in $PD" | tee -a "$LOG"; exit 1; }
echo "patch: $PD ($(grep -c '^patch=' "$PD/SLPM-66675_F266B00B.pnach") words)" >> "$LOG"
if [ ! -f "$P/local/iso/test-m-solo.iso" ]; then
  echo "=== building test-m-solo.iso" >> "$LOG"
  python -I "$M/build_disc_m.py" test-m-solo.iso --no-twin --overlay "$P/local/variants/b-roam/built/ard" >> "$LOG" 2>&1
fi
run() { echo "=== $1" >> "$LOG"; shift; "$@" >> "$LOG" 2>&1; }
run m3-a-ctl          bash "$M/mrun.sh" m3-a-ctl test-m-roam.iso 5600 1.0 "4650,4800,4880,5000,5112,5190,5212,5300" 2 "$S/ctl_p1.txt" "$S/ctl_p2.txt" idle "$PD"
run m3-c-fight-idle   bash "$M/mrun.sh" m3-c-fight-idle test-m-fight.iso 10400 2.0 "4700,5200,5700,6200,6700,7200,7700,8200,8700,9200,9700,10300" 2 "$S/fight_idle_p1.txt" "$S/idle_p2.txt" idle "$PD"
run m3-d-roundtrip    bash "$M/mrun.sh" m3-d-roundtrip test-m-roam.iso 7400 2.0 "4700,5300,5620,6200,6520,7200" 2 "$S/rt_p1.txt" "$S/rt_p2.txt" idle "$PD"
run m3-d-door-p1alone bash "$M/mrun.sh" m3-d-door-p1alone test-m-roam.iso 5400 1.0 "4480,4650,4780,4900,5100,5350" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" idle "$PD"
run m3-e-newgame      bash "$M/mrun.sh" m3-e-newgame kh2-coop-v1.iso 16000 2.0 "5180,6400,6600,6912,10000,13000,15900" 2 "$S/newgame_p1.txt" "$S/newgame_p2.txt" random "$PD"
run m3-i-attack       bash "$M/mrecrun.sh" m3-i-attack test-m-fight.iso 5900 1.0 2 "$S/atk_p1.txt" "$S/atk_p2.txt" idle "$PD" 4678 5878 "p2only:4700-5040,p1only:5100-5440,both:5500-5840" "4690,5050,5450,5850"
run m3-l-sync-roam    bash "$M/mrun.sh" m3-l-sync-roam test-m-roam.iso 34000 4.0 "4700,5300,7300,12000,18000,24000,30000,33900" 2 "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random "$PD"
run m3-l-sync-fight   bash "$M/mrun.sh" m3-l-sync-fight test-m-fight.iso 7300 4.0 "4700,5500,6300,7200" 2 "$S/newgame_only.txt" "$S/wait_3700.txt" random "$PD"
run m3-h-solo         bash "$M/mrun.sh" m3-h-solo test-m-solo.iso 12000 4.0 "4480,4900,8000,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$PD"
for t in m3-a-ctl m3-c-fight-idle m3-d-roundtrip m3-d-door-p1alone m3-e-newgame m3-l-sync-roam m3-l-sync-fight m3-h-solo; do
  echo "--- psum $t" >> "$LOG"
  python -I "$M/psum.py" "$P/local/tests/$t" >> "$LOG" 2>&1
  a=0; b=0
  for f in "$P/local/tests/$t"/p1_f*.png; do
    g="${f/p1_f/p2_f}"; b=$((b+1))
    [ -f "$g" ] && [ "$(sha1sum "$f" | cut -c1-40)" = "$(sha1sum "$g" | cut -c1-40)" ] && a=$((a+1))
  done
  echo "    screenshot pairs identical: $a of $b" >> "$LOG"
done
echo "=== solo pictures against merged-v2 (m2-v2-h-solo)" >> "$LOG"
for f in 004480 004900 008000 011900; do
  x=$(sha1sum "$P/local/tests/m3-h-solo/p1_f$f.png" 2>/dev/null | cut -c1-12); y=$(sha1sum "$P/local/tests/m2-v2-h-solo/p1_f$f.png" 2>/dev/null | cut -c1-12)
  echo "    f$f v3=$x v2=$y $([ -n "$x" ] && [ "$x" = "$y" ] && echo SAME || echo DIFFERENT)" >> "$LOG"
done
echo "SUITE DONE" >> "$LOG"
