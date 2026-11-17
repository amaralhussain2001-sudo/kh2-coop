#!/bin/bash
# TEST ONLY (eighth round, job 12): THE REST OF THE WHOLE REGRESSION OF v89, IN PARALLEL LANES. The serial runner
# (r8_chain108.sh -> reg_serial.sh test-own-v89 test-v14-a b18) was stopped by hand on 2026-11-15 00:02 while its
# step 8 (final_b10.sh on run-v3b) was running; that step's own script goes on by itself. The user said at 23:50
# that several tests at once are welcome, so the six steps that were left run here side by side, EACH WITH THE
# SAME SCRIPT, THE SAME ARGUMENTS AND THE SAME SANDBOX as in reg_serial.sh:
#   run-v3b  (after step 8's script has ended)  step 9  final_b11.sh
#   run-m    step 10 final_b12.sh a   ->  step 13 the Gummi routes 5 6 7 8
#   run-v3   step 11 final_b12.sh b   ->  step 14 the Gummi routes 0 1 2 3 4
#   run-v3c  step 12 final_b12.sh c
# Progress: local/reg-serial.log (the same file) and local/sweep/b15/chain118.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
OWN=test-own-v89; X=b18
cd "$P" || exit 1
R="$P/local/reg-serial.log"; B="$P/local/sweep/b15"
echo "  (the serial runner was stopped at 00:02 during step 8; steps 9 to 14 run in parallel lanes, r8_chain118.sh) $(date +%H:%M:%S)" >> "$R"
echo "chain118 start $(date +%H:%M:%S)" >> "$B/chain118.txt"
step() {  # step <number> <name> <command...>
  local n=$1 name=$2; shift 2
  echo "  step $n $name start $(date +%H:%M:%S)" >> "$R"
  "$@" > /dev/null 2>&1
  echo "  step $n $name done  $(date +%H:%M:%S)" >> "$R"
}
(
  while powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'final_b10.sh' } | ForEach-Object { \$_.ProcessId }" 2>/dev/null | grep -q "[0-9]"; do sleep 5; done
  echo "  step 8 final_b10 done  $(date +%H:%M:%S) (its own script ended)" >> "$R"
  step 9  final_b11      bash tools/own/final_b11.sh "$OWN" run-v3b 30350 28062
  echo "lane run-v3b through $(date +%H:%M:%S)" >> "$B/chain118.txt"
) &
(
  step 10 final_b12-a    bash tools/own/final_b12.sh "$OWN" run-m 29050 28081 a
  step 13 gummi-b        bash tools/own/gum_routes2.sh "$OWN" run-m 29050 28081 "gummi-$X-b" 5 6 7 8
  echo "lane run-m through $(date +%H:%M:%S)" >> "$B/chain118.txt"
) &
(
  step 11 final_b12-b    bash tools/own/final_b12.sh "$OWN" run-v3 30150 28061 b
  step 14 gummi-a        bash tools/own/gum_routes2.sh "$OWN" run-v3 30150 28061 "gummi-$X-a" 0 1 2 3 4
  echo "lane run-v3 through $(date +%H:%M:%S)" >> "$B/chain118.txt"
) &
(
  step 12 final_b12-c    bash tools/own/final_b12.sh "$OWN" run-v3c 30550 28063 c
  echo "lane run-v3c through $(date +%H:%M:%S)" >> "$B/chain118.txt"
) &
wait
echo "SERIAL REGRESSION THROUGH (its last six steps in parallel lanes) $(date +%H:%M:%S)" >> "$R"
echo "chain118 through $(date +%H:%M:%S)" >> "$B/chain118.txt"
