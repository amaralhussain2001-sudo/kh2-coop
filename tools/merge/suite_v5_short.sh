#!/bin/bash
# Short check of a shared-screen patch: the New Game run, the long random roam and the one-hero run of suite_v5.sh.
# usage: bash tools/merge/suite_v5_short.sh <patchDir>   -> log local/m5s-suite.log, results local/tests/m5s-*
P="/c/Users/PC FORCE/Desktop/New folder (3)"
PD="$1"
S="$P/tests/scripts/merge"
M="$P/tools/merge"
LOG="$P/local/m5s-suite.log"
: > "$LOG"
run() { echo "=== $1" >> "$LOG"; shift; "$@" >> "$LOG" 2>&1; }
run m5s-e-newgame   bash "$M/mrun.sh" m5s-e-newgame kh2-coop-v2.iso 16000 2.0 "5180,6400,6600,6912,10000,13000,15900" 2 "$S/newgame_p1.txt" "$S/newgame_p2.txt" random "$PD"
run m5s-l-sync-roam bash "$M/mrun.sh" m5s-l-sync-roam test-m-roam.iso 34000 4.0 "4700,5300,7300,12000,18000,24000,30000,33900" 2 "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random "$PD"
run m5s-h-solo      bash "$M/mrun.sh" m5s-h-solo test-m-solo.iso 12000 4.0 "4480,4900,8000,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$PD"
echo "=== solo pictures against merged build 5 (m5-h-solo)" >> "$LOG"
for f in 004480 004900 008000 011900; do
  x=$(sha1sum "$P/local/tests/m5s-h-solo/p1_f$f.png" 2>/dev/null | cut -c1-12); y=$(sha1sum "$P/local/tests/m5-h-solo/p1_f$f.png" 2>/dev/null | cut -c1-12)
  echo "    f$f new=$x v5=$y $([ -n "$x" ] && [ "$x" = "$y" ] && echo SAME || echo DIFFERENT)" >> "$LOG"
done
