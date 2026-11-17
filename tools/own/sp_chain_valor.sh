#!/bin/bash
# TEST ONLY (2026-11-13): does a Drive Form gain EXP from player 2's hits? Fight disc test-m-fight, kit -forms, sandbox
# run-v3c. Probe: the Valor and Wisdom records (save + 0x32F4 / + 0x332C, first 8 bytes) at each picture.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"
cd "$P" || exit 1
SN="4690,4900,5200,5500,5800,6100,6400,6900"
for who in p2 p1; do
  if [ $who = p2 ]; then A="$S/newgame_only.txt"; B="$O/valor_fight_p2.txt"; else A="$O/valor_fight_p1.txt"; B="$O/idle.txt"; fi
  RANGES="0032EE24:8,0032EE5C:8" PROBE="$P/tools/own/memdump_probe.py" bash tools/own/dusk_one.sh "t13-valorf-$who" "$P/patches/test-own-v33-forms" test-m-fight.iso 7000 "$SN" "$A" "$B" run-v3c 30550 28063 > "local/sweep/b13/valorf-$who.log" 2>&1
  echo "TLB misses $(grep -c 'TLB Miss' local/run-v3c/p1/logs/emulog.txt)" >> "local/sweep/b13/valorf-$who.log"
done
