#!/bin/bash
# TEST ONLY (ninth round, jobs 5 and 6), two lanes:
#   run-x4: cnA = THE TOY CANNON WITH A VIEW FOR EACH PLAYER: nm10 63 on v103 + the own-screen option --cannon2view
#           (patches/test-own-v103c-snapB), 16,000 frames, the scripts that fire, reload and sweep the aim; probe sp_probe.py
#   run-m:  gsh1 = THE GUMMI FLIGHT, ONLY PLAYER 1 FIRES, with the log of every hit of a shot on an enemy
#           (patches/test-own-v103-gum0-gshot, probe gshot_probe.py), 14,000 frames;  gsh2 = ONLY PLAYER 2 FIRES
# Logs local/sweep/r9/cnA.log, chain20.txt; the hit logs local/tests/r9gsh1-probe.txt, r9gsh2-probe.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; S3="$P/tests/scripts/lane-s3"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain20.txt"; }
say "chain20 start"
(
  ISO=test-v5-tt137.iso PROBE="$T/sp_probe.py" SNAPS="5200,6000,6500,7000,7500,8000,9000,10000,11000,12000,13000,14000,15000,15900" FRAMES=16000 TOUT=1200 SWEEP_PROBE_WAIT=1200 LOGDIR=local/sweep/r9 TAG=r9cnA P1S="$O/cannon_p1.txt" P2S="$O/cannon_p2.txt" bash tools/own/sweep4.sh cnA run-x4 31350 28067 test-own-v103c-snapB "$L/list-nm63.txt"
  say "cnA done"
) &
(
  SN="8000,9000,10000,11000,12000,13000,13900"
  for r in "gsh1 gb_p1_fight.txt gb_p2_idle.txt" "gsh2 gb_p1_idle.txt gb_p2_fight.txt"; do
    set -- $r
    out=$(PROBE="$T/gshot_probe.py" FROM=6000 TO=13900 SWEEP_PROBE_WAIT=1200 bash "$T/dusk_one.sh" "r9$1" "patches/test-own-v103-gum0-gshot" test-s1-tt137.iso 14000 "$SN" "$S3/$2" "$S3/$3" run-m 29050 28081 2>&1 | head -n 1)
    say "$1 | $out | TLB misses $(grep -ac 'TLB Miss' "$P/local/run-m/p1/logs/emulog.txt")"
  done
) &
wait
say "chain20 through"
