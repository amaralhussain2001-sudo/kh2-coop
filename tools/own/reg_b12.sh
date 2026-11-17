#!/bin/bash
# The WHOLE regression of test build 12 on the four sandboxes (seventh round). Everything named in docs/STATE.md
# "How to repeat" plus this round's own checks. Kits first: bash tools/own/make_kits.sh <ownName>.
#   run-m    suite_v6.sh (own)  ->  suite_v5_short.sh (shared)  ->  the one-hero control (<shared>-nn, log
#            local/b12-solo-nn.log)  ->  final_b12.sh a  ->  Gummi routes 5 6 7 8
#   run-v3   batch_v7.sh        ->  final_b12.sh b               ->  Gummi routes 0 1 2 3 4
#   run-v3b  near_batch.sh <own> <prefix>  ->  final_b10.sh  ->  final_b11.sh
#   run-v3c  final_b9.sh a  ->  final_b9.sh b  ->  final_b12.sh c
# Logs: local/m6-suite.log, local/m5s-suite.log, local/own-batch7.log, local/<prefix>-batch.log,
# local/final-b9-a.log, -b.log, local/final-b10.log, local/final-b11.log, local/final-b12-a.log, -b.log, -c.log,
# local/sweep/gummi-<prefix>-a.log, -b.log. The last line of local/reg-b12.log says when all four are through.
# usage: bash tools/own/reg_b12.sh <ownPatchDirName> <sharedPatchDirName> <prefix>
P="/c/Users/PC FORCE/Desktop/New folder (3)"
OWN=$1; SH=$2; X=$3
cd "$P" || exit 1
R="$P/local/reg-b12.log"; echo "regression of $OWN / $SH started $(date +%H:%M:%S)" > "$R"
(
  bash tools/merge/suite_v6.sh "$P/patches/$OWN" > /dev/null 2>&1
  bash tools/merge/suite_v5_short.sh "$P/patches/$SH" > /dev/null 2>&1
  # the one-hero run again on the shared patch built with --no-notwin (folder <shared>-nn): with the twenty-eighth
  # glue player 2's random buttons move the lone hero after frame 5400, so the suites' one-hero pictures at 8000
  # and 11900 differ from merged build 5's; without the glue all four must be the same again
  S="$P/tests/scripts/merge"
  bash tools/merge/mrun.sh b12-solo-nn test-m-solo.iso 12000 4.0 "4480,4900,8000,11900" 2 "$S/door_p1alone_p1.txt" "$S/idle_p2.txt" random "$P/patches/$SH-nn" > "$P/local/b12-solo-nn.log" 2>&1
  for f in 004480 004900 008000 011900; do
    x=$(sha1sum "$P/local/tests/b12-solo-nn/p1_f$f.png" 2>/dev/null | cut -c1-12); y=$(sha1sum "$P/local/tests/m5-h-solo/p1_f$f.png" 2>/dev/null | cut -c1-12)
    echo "    f$f new=$x v5=$y $([ -n "$x" ] && [ "$x" = "$y" ] && echo SAME || echo DIFFERENT)" >> "$P/local/b12-solo-nn.log"
  done
  bash tools/own/final_b12.sh "$OWN" run-m 29050 28081 a > /dev/null 2>&1
  bash tools/own/gum_routes2.sh "$OWN" run-m 29050 28081 "gummi-$X-b" 5 6 7 8 > /dev/null 2>&1
  echo "run-m through $(date +%H:%M:%S)" >> "$R"
) &
(
  bash tools/own/batch_v7.sh "$OWN" > /dev/null 2>&1
  bash tools/own/final_b12.sh "$OWN" run-v3 30150 28061 b > /dev/null 2>&1
  bash tools/own/gum_routes2.sh "$OWN" run-v3 30150 28061 "gummi-$X-a" 0 1 2 3 4 > /dev/null 2>&1
  echo "run-v3 through $(date +%H:%M:%S)" >> "$R"
) &
(
  bash tools/own/near_batch.sh "$OWN" "$X" > /dev/null 2>&1
  bash tools/own/final_b10.sh "$OWN" run-v3b 30350 28062 > /dev/null 2>&1
  bash tools/own/final_b11.sh "$OWN" run-v3b 30350 28062 > /dev/null 2>&1
  echo "run-v3b through $(date +%H:%M:%S)" >> "$R"
) &
(
  bash tools/own/final_b9.sh "$OWN" run-v3c 30550 28063 a > /dev/null 2>&1
  bash tools/own/final_b9.sh "$OWN" run-v3c 30550 28063 b > /dev/null 2>&1
  bash tools/own/final_b12.sh "$OWN" run-v3c 30550 28063 c > /dev/null 2>&1
  echo "run-v3c through $(date +%H:%M:%S)" >> "$R"
) &
wait
echo "ALL FOUR THROUGH $(date +%H:%M:%S)" >> "$R"
