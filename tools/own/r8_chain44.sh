#!/bin/bash
# TEST ONLY (eighth round, job 12): WHY DOES THE CANDIDATE v52 SHOW A SECOND GAME OVER IN THE REGRESSION'S "formdie"
# (both heroes held at 1 HP, the twin in a form, Continue at 9000) WHERE BUILD 12 HAS BOTH ALIVE AT 12500?
#   fdA  candidate v52 (kit test-own-v52-formdie), pictures every 300 frames after the Continue
#   fdB  v52 WITHOUT the thirtieth glue (enemy groups wake for player 2 too; kit test-own-v52-nosp-formdie)
#   fdC  build 12 (kit test-own-v33-formdie), the same pictures
# ONE RUN AT A TIME on sandbox run-v3c. Log: local/sweep/b15/chain44.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; B="$P/local/sweep/b15"
cd "$P" || exit 1
LOG="$B/chain44.txt"
echo "chain44 start $(date +%H:%M:%S)" >> "$LOG"
SN="8600,9400,9700,10000,10300,10600,10900,11200,11500,11800,12100,12500"
one() {  # name patchDir
  PROBE="$P/tools/own/drv_probe2.py" bash "$P/tools/own/dusk_one.sh" "$1" "$P/patches/$2" test-m-roam.iso 12600 "$SN" "$O/gocont2_p1.txt" "$O/formdie2_p2.txt" run-v3c 30550 28063 2>&1 | head -1 | cut -c1-105 >> "$LOG"
  cut -c1-150 "$P/local/tests/$1-probe.txt" >> "$LOG"
}
one fdA test-own-v52-formdie
one fdB test-own-v52-nosp-formdie
one fdC test-own-v33-formdie
echo "chain44 through $(date +%H:%M:%S)" >> "$LOG"
