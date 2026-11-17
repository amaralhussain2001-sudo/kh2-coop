#!/bin/bash
# The WHOLE regression (the same chains as reg_b12.sh) ONE RUN AT A TIME: for a session where the user wants a
# single test on screen (KH2_TEST_SHOW=1 bash tools/own/reg_serial.sh ...). About two and a half hours.
# Logs as in reg_b12.sh; progress lines in local/reg-serial.log.
# usage: bash tools/own/reg_serial.sh <ownPatchDirName> <sharedPatchDirName> <prefix> [firstStep]
#   firstStep (1..12) lets a stopped regression go on where it was.
P="/c/Users/PC FORCE/Desktop/New folder (3)"
OWN=$1; SH=$2; X=$3; FROM=${4:-1}
cd "$P" || exit 1
R="$P/local/reg-serial.log"; echo "serial regression of $OWN / $SH from step $FROM started $(date +%H:%M:%S)" >> "$R"
S="$P/tests/scripts/merge"
step() {  # step <number> <name> <command...>
  local n=$1 name=$2; shift 2
  [ "$n" -lt "$FROM" ] && return
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
step 1  suite_v6       bash tools/merge/suite_v6.sh "$P/patches/$OWN"
step 2  suite_v5_short bash tools/merge/suite_v5_short.sh "$P/patches/$SH"
step 3  solo-nn        solo
step 4  batch_v7       bash tools/own/batch_v7.sh "$OWN"
step 5  near_batch     bash tools/own/near_batch.sh "$OWN" "$X"
step 6  final_b9-a     bash tools/own/final_b9.sh "$OWN" run-v3c 30550 28063 a
step 7  final_b9-b     bash tools/own/final_b9.sh "$OWN" run-v3c 30550 28063 b
step 8  final_b10      bash tools/own/final_b10.sh "$OWN" run-v3b 30350 28062
step 9  final_b11      bash tools/own/final_b11.sh "$OWN" run-v3b 30350 28062
step 10 final_b12-a    bash tools/own/final_b12.sh "$OWN" run-m 29050 28081 a
step 11 final_b12-b    bash tools/own/final_b12.sh "$OWN" run-v3 30150 28061 b
step 12 final_b12-c    bash tools/own/final_b12.sh "$OWN" run-v3c 30550 28063 c
step 13 gummi-b        bash tools/own/gum_routes2.sh "$OWN" run-m 29050 28081 "gummi-$X-b" 5 6 7 8
step 14 gummi-a        bash tools/own/gum_routes2.sh "$OWN" run-v3 30150 28061 "gummi-$X-a" 0 1 2 3 4
echo "SERIAL REGRESSION THROUGH $(date +%H:%M:%S)" >> "$R"
