#!/bin/bash
# TEST ONLY (ninth round, 2026-11-15): THE WHOLE REGRESSION OF tools/own/reg_par8.sh, THE EIGHT LANES ONE AFTER THE OTHER (one emulator
# at a time: the user is playing). The same steps, the same logs and the same counting runs (local/sweep/b15/count-<prefix>.txt), so
# tools/own/reg_compare.py reads it as it reads reg_par8.sh's. Progress lines: local/reg-serial2.log. About four hours.
# usage: bash tools/own/reg_serial2.sh <ownPatchDirName> <sharedPatchDirName> <prefix> <countName>   (kits first: make_kits.sh <own>)
# The WHOLE regression (the same fourteen steps as reg_serial.sh / reg_b12.sh, each with the same script) ON EIGHT
# SANDBOXES AT ONCE, plus the thirteen counting runs (steps 1 to 3 once more with their fault line count).
# Written 2026-11-15 after the user said that several tests at once are welcome while he does not play.
# Kits first: bash tools/own/make_kits.sh <ownName>; the control folder patches/<shared>-nn must exist.
#   run-m    suite_v6.sh (own) -> suite_v5_short.sh (shared) -> the one-hero control      (mrun.sh is bound to run-m)
#   run-v3   batch_v7.sh (bound to run-v3)       -> counting runs, first seven
#   run-v3b  near_batch.sh (bound to run-v3b)
#   run-v3c  final_b9.sh a -> final_b9.sh b
#   run-x1   final_b10.sh  -> final_b11.sh
#   run-x2   final_b12.sh a -> final_b12.sh b    -> counting runs, last six
#   run-x3   final_b12.sh c -> Gummi routes 5 6 7 8
#   run-x4   Gummi routes 0 1 2 3 4
# Logs: as reg_b12.sh (local/m6-suite.log ... local/sweep/gummi-<prefix>-a.log); the counting runs' lines in
# local/sweep/b15/count-<prefix>.txt (names <cname>-*). Progress and the last line "ALL EIGHT THROUGH": local/reg-par8.log
# usage: bash tools/own/reg_par8.sh <ownPatchDirName> <sharedPatchDirName> <prefix> <countName>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
OWN=$1; SH=$2; X=$3; C=$4
cd "$P" || exit 1
R="$P/local/reg-serial2.log"; echo "regression (the eight lanes ONE AFTER THE OTHER) of $OWN / $SH started $(date +%H:%M:%S)" > "$R"
S="$P/tests/scripts/merge"; M="$P/tools/merge"; CL="$P/local/sweep/b15/count-$X.txt"
step() {  # step <number> <name> <command...>
  local n=$1 name=$2; shift 2
  echo "  step $n $name start $(date +%H:%M:%S)" >> "$R"
  "$@" > /dev/null 2>&1
  echo "  step $n $name done  $(date +%H:%M:%S)" >> "$R"
}
solo() {
  bash tools/merge/mrun.sh b12-solo-nn test-m-solo.iso 12000 4.0 "4480,4900,8000,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$P/patches/$SH-nn" > "$P/local/b12-solo-nn.log" 2>&1
  for f in 004480 004900 008000 011900; do
    x=$(sha1sum "$P/local/tests/b12-solo-nn/p1_f$f.png" 2>/dev/null | cut -c1-12); y=$(sha1sum "$P/local/tests/m5-h-solo/p1_f$f.png" 2>/dev/null | cut -c1-12)
    echo "    f$f new=$x v5=$y $([ -n "$x" ] && [ "$x" = "$y" ] && echo SAME || echo DIFFERENT)" >> "$P/local/b12-solo-nn.log"
  done
}
crun() {  # crun <sandbox> <port> <pine> <name> <command...>: one counting run and its fault line counts
  local rd=$1 pt=$2 pn=$3 n=$4; shift 4
  r=$(MRUN_DIR=$rd MRUN_PORT=$pt MRUN_PINE=$pn "$@" 2>&1 | head -1 | cut -c12-90)
  echo "$n: $r | p1 TLB misses $(grep -ac 'TLB Miss' "$P/local/$rd/p1/logs/emulog.txt") | p2 TLB misses $(grep -ac 'TLB Miss' "$P/local/$rd/p2/logs/emulog.txt" 2>/dev/null)" >> "$CL"
}
O="$P/patches/$OWN"; H="$P/patches/$SH"; NN="$P/patches/$SH-nn"
: > "$CL"
(
  step 1  suite_v6       bash tools/merge/suite_v6.sh "$O"
  step 2  suite_v5_short bash tools/merge/suite_v5_short.sh "$H"
  step 3  solo-nn        solo
  echo "run-m through $(date +%H:%M:%S)" >> "$R"
)
(
  step 4  batch_v7       bash tools/own/batch_v7.sh "$OWN"
  echo "  counting runs, first seven, start $(date +%H:%M:%S)" >> "$R"
  crun run-v3 30150 28061 $C-a-ctl          bash "$M/mrunx.sh" $C-a-ctl test-m-roam.iso 5600 1.0 "4650,5000,5300" 2 "$S/ctl_p1.txt" "$S/ctl_p2.txt" idle "$O"
  crun run-v3 30150 28061 $C-c-fight-idle   bash "$M/mrunx.sh" $C-c-fight-idle test-m-fight.iso 10400 2.0 "4700,7200,10300" 2 "$S/fight_idle_p1.txt" "$S/idle_p2.txt" idle "$O"
  crun run-v3 30150 28061 $C-d-roundtrip    bash "$M/mrunx.sh" $C-d-roundtrip test-m-roam.iso 7400 2.0 "4700,6200,7200" 2 "$S/rt_p1.txt" "$S/rt_p2.txt" idle "$O"
  crun run-v3 30150 28061 $C-d-door-p1alone bash "$M/mrunx.sh" $C-d-door-p1alone test-m-roam.iso 5400 1.0 "4480,4900,5350" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" idle "$O"
  crun run-v3 30150 28061 $C-e-newgame      bash "$M/mrunx.sh" $C-e-newgame kh2-coop-v2.iso 16000 2.0 "5180,10000,15900" 2 "$S/newgame_p1.txt" "$S/newgame_p2.txt" random "$O"
  crun run-v3 30150 28061 $C-i-attack       bash "$M/mrecrunx.sh" $C-i-attack test-m-fight.iso 5900 1.0 2 "$S/atk_p1.txt" "$S/atk_p2.txt" idle "$O" 4678 5878 "p2only:4700-5040,p1only:5100-5440,both:5500-5840" "4690,5050,5450,5850"
  crun run-v3 30150 28061 $C-l-sync-fight   bash "$M/mrunx.sh" $C-l-sync-fight test-m-fight.iso 7300 4.0 "4700,7200" 2 "$S/newgame_only.txt" "$S/wait_3700.txt" random "$O"
  echo "run-v3 through $(date +%H:%M:%S)" >> "$R"
)
(
  step 5  near_batch     bash tools/own/near_batch.sh "$OWN" "$X"
  echo "run-v3b through $(date +%H:%M:%S)" >> "$R"
)
(
  step 6  final_b9-a     bash tools/own/final_b9.sh "$OWN" run-v3c 30550 28063 a
  step 7  final_b9-b     bash tools/own/final_b9.sh "$OWN" run-v3c 30550 28063 b
  echo "run-v3c through $(date +%H:%M:%S)" >> "$R"
)
(
  step 8  final_b10      bash tools/own/final_b10.sh "$OWN" run-x1 30750 28064
  step 9  final_b11      bash tools/own/final_b11.sh "$OWN" run-x1 30750 28064
  echo "run-x1 through $(date +%H:%M:%S)" >> "$R"
)
(
  step 10 final_b12-a    bash tools/own/final_b12.sh "$OWN" run-x2 30950 28065 a
  step 11 final_b12-b    bash tools/own/final_b12.sh "$OWN" run-x2 30950 28065 b
  echo "  counting runs, last six, start $(date +%H:%M:%S)" >> "$R"
  crun run-x2 30950 28065 $C-l-sync-roam    bash "$M/mrunx.sh" $C-l-sync-roam test-m-roam.iso 34000 4.0 "4700,18000,33900" 2 "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random "$O"
  crun run-x2 30950 28065 $C-h-solo         bash "$M/mrunx.sh" $C-h-solo test-m-solo.iso 12000 4.0 "4480,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$O"
  crun run-x2 30950 28065 ${C}s-e-newgame   bash "$M/mrunx.sh" ${C}s-e-newgame kh2-coop-v2.iso 16000 2.0 "5180,10000,15900" 2 "$S/newgame_p1.txt" "$S/newgame_p2.txt" random "$H"
  crun run-x2 30950 28065 ${C}s-l-sync-roam bash "$M/mrunx.sh" ${C}s-l-sync-roam test-m-roam.iso 34000 4.0 "4700,18000,33900" 2 "$S/sync_roam_p1.txt" "$S/sync_roam_p2.txt" random "$H"
  crun run-x2 30950 28065 ${C}s-h-solo      bash "$M/mrunx.sh" ${C}s-h-solo test-m-solo.iso 12000 4.0 "4480,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$H"
  crun run-x2 30950 28065 $C-solo-nn        bash "$M/mrunx.sh" $C-solo-nn test-m-solo.iso 12000 4.0 "4480,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$NN"
  echo "run-x2 through $(date +%H:%M:%S)" >> "$R"
)
(
  step 12 final_b12-c    bash tools/own/final_b12.sh "$OWN" run-x3 31150 28066 c
  step 13 gummi-b        bash tools/own/gum_routes2.sh "$OWN" run-x3 31150 28066 "gummi-$X-b" 5 6 7 8
  echo "run-x3 through $(date +%H:%M:%S)" >> "$R"
)
(
  step 14 gummi-a        bash tools/own/gum_routes2.sh "$OWN" run-x4 31350 28067 "gummi-$X-a" 0 1 2 3 4
  echo "run-x4 through $(date +%H:%M:%S)" >> "$R"
)
echo "ALL EIGHT THROUGH (one after the other) $(date +%H:%M:%S)" >> "$R"
