#!/bin/bash
# TEST ONLY: one test disc per skate mission on the v4 data (jump into the mission), one own-screen run each
# (player 1 closes the rules screen, player 2 rides forward), contact sheet. Log: local/v4-skate-tests.log
# usage: bash tools/boards/skate_tests.sh <ownPatchDir> <name:WORLD:LOCALSET> ...
P="/c/Users/PC FORCE/Desktop/New folder (3)"
PD=$1; shift
LOG="$P/local/v4-skate-tests.log"
for t in "$@"; do
  n=${t%%:*}; r=${t#*:}; w=${r%%:*}; ls=${r#*:}
  iso="test-v4-$n.iso"
  if [ ! -f "$P/local/iso/$iso" ]; then
    (cd "$P" && python -I tools/merge/build_disc_v4.py "$iso" --jump "$w $ls" > "local/v4-$n-build.log" 2>&1)
    tail -1 "$P/local/v4-$n-build.log" | cut -c1-120 >> "$LOG"
  fi
  PROBE="$P/tools/own/menu_probe.py" bash "$P/tools/own/dusk_one.sh" "u2-$n" "$PD" "$iso" 6400 "4900,5400,5900,6300" "$P/tests/scripts/own/rules_p1.txt" "$P/tests/scripts/own/mailride_p2.txt" run-v3b 30350 28062 2>&1 | head -1 | cut -c1-110 >> "$LOG"
  grep -o "frame [0-9]*\|S  player [0-9A-F]* attached [0-9A-F]* open menu [0-9A-F]* id [0-9]* | hero [0-9A-F]* board mode [0-9]\|S2 player [0-9A-F]* attached [0-9A-F]* open menu [0-9A-F]* id [0-9]* | hero [0-9A-F]* board mode [0-9]" "$P/local/tests/u2-$n-probe.txt" | tr '\n' ' ' | cut -c1-900 >> "$LOG"
  echo >> "$LOG"
  (cd "$P" && python tools/own/sheet.py "local/tests/u2-$n" 520 > /dev/null 2>&1)
done
echo "skate tests done" >> "$LOG"
