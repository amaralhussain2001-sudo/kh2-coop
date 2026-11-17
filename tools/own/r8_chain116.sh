#!/bin/bash
# TEST ONLY (eighth round, job 12): THE RUNS OF REGRESSION STEPS 1 TO 3 ONCE MORE WITH THEIR FAULT LINE COUNT.
# suite_v6.sh / suite_v5_short.sh / the one-hero control print "in sync" but no "TLB misses N" (mrun.sh does not
# count). Here the same thirteen runs (same discs, frames, scripts; names z18-*) and after each one the count of
# 'TLB Miss' lines in the sandbox's emulator log. ONE RUN AT A TIME on sandbox run-m.
# Log: local/sweep/b15/chain116.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
S="$P/tests/scripts/merge"; M="$P/tools/merge"; B="$P/local/sweep/b15"
OWN="$P/patches/test-own-v89"; SH="$P/patches/test-v14-a"; NN="$P/patches/test-v14-a-nn"
cd "$P" || exit 1
export MRUN_DIR=run-x3 MRUN_PORT=31150 MRUN_PINE=28066     # A LANE BESIDE THE QUEUE (the user, 2026-11-14 23:50: several tests at once); r8_chain109.sh is NOT run
LOG="$B/chain116.txt"
echo "chain116 start $(date +%H:%M:%S)" >> "$LOG"
run() {  # name, then the command
  local n=$1; shift
  r=$("$@" 2>&1 | head -1 | cut -c12-90)
  echo "$n: $r | p1 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-x3/p1/logs/emulog.txt") | p2 TLB misses $(grep -ac 'TLB Miss' "$P/local/run-x3/p2/logs/emulog.txt" 2>/dev/null)" >> "$LOG"
}
run z18-a-ctl          bash "$M/mrunx.sh" z18-a-ctl test-m-roam.iso 5600 1.0 "4650,5000,5300" 2 "$S/ctl_p1.txt" "$S/ctl_p2.txt" idle "$OWN"
run z18-c-fight-idle   bash "$M/mrunx.sh" z18-c-fight-idle test-m-fight.iso 10400 2.0 "4700,7200,10300" 2 "$S/fight_idle_p1.txt" "$S/idle_p2.txt" idle "$OWN"
run z18-d-roundtrip    bash "$M/mrunx.sh" z18-d-roundtrip test-m-roam.iso 7400 2.0 "4700,6200,7200" 2 "$S/rt_p1.txt" "$S/rt_p2.txt" idle "$OWN"
run z18-d-door-p1alone bash "$M/mrunx.sh" z18-d-door-p1alone test-m-roam.iso 5400 1.0 "4480,4900,5350" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" idle "$OWN"
run z18-e-newgame      bash "$M/mrunx.sh" z18-e-newgame kh2-coop-v2.iso 16000 2.0 "5180,10000,15900" 2 "$S/newgame_p1.txt" "$S/newgame_p2.txt" random "$OWN"
run z18-i-attack       bash "$M/mrecrunx.sh" z18-i-attack test-m-fight.iso 5900 1.0 2 "$S/atk_p1.txt" "$S/atk_p2.txt" idle "$OWN" 4678 5878 "p2only:4700-5040,p1only:5100-5440,both:5500-5840" "4690,5050,5450,5850"
run z18-l-sync-roam    bash "$M/mrunx.sh" z18-l-sync-roam test-m-roam.iso 34000 4.0 "4700,18000,33900" 2 "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random "$OWN"
run z18-l-sync-fight   bash "$M/mrunx.sh" z18-l-sync-fight test-m-fight.iso 7300 4.0 "4700,7200" 2 "$S/newgame_only.txt" "$S/wait_3700.txt" random "$OWN"
run z18-h-solo         bash "$M/mrunx.sh" z18-h-solo test-m-solo.iso 12000 4.0 "4480,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$OWN"
run z18s-e-newgame     bash "$M/mrunx.sh" z18s-e-newgame kh2-coop-v2.iso 16000 2.0 "5180,10000,15900" 2 "$S/newgame_p1.txt" "$S/newgame_p2.txt" random "$SH"
run z18s-l-sync-roam   bash "$M/mrunx.sh" z18s-l-sync-roam test-m-roam.iso 34000 4.0 "4700,18000,33900" 2 "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random "$SH"
run z18s-h-solo        bash "$M/mrunx.sh" z18s-h-solo test-m-solo.iso 12000 4.0 "4480,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$SH"
run z18-solo-nn        bash "$M/mrunx.sh" z18-solo-nn test-m-solo.iso 12000 4.0 "4480,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$NN"
echo "chain116 through $(date +%H:%M:%S)" >> "$LOG"
