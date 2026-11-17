#!/bin/bash
# TEST ONLY (2026-11-13): does a Drive Form gain EXP from player 2's hits? (second try: the first form in the kit's Drive
# menu is LIMIT FORM, so all five form records are read: save + 0x32F4 Valor, 0x332C Wisdom, 0x3364 Limit, 0x339C Master,
# 0x33D4 Final; 8 bytes each). Fight disc test-m-fight, kit -forms; after sp_chain_dt.sh, sandbox run-m.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; S="$P/tests/scripts/merge"
cd "$P" || exit 1
while ! grep -q "dark thorn controls done" local/sweep/b13c/hy-done.txt 2>/dev/null; do powershell -NoProfile -Command "Start-Sleep -Seconds 15" > /dev/null; done
SN="4690,4900,5200,5500,5800,6100,6400,6900"
for who in p2 p1; do
  if [ $who = p2 ]; then A="$S/newgame_only.txt"; B="$O/valor_fight_p2.txt"; else A="$O/valor_fight_p1.txt"; B="$O/idle.txt"; fi
  RANGES="0032EE24:8,0032EE5C:8,0032EE94:8,0032EECC:8,0032EF04:8" PROBE="$P/tools/own/memdump_probe.py" bash tools/own/dusk_one.sh "t13-form-$who" "$P/patches/test-own-v33-forms" test-m-fight.iso 7000 "$SN" "$A" "$B" run-m 29050 28081 > "local/sweep/b13/form-$who.log" 2>&1
  echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "local/sweep/b13/form-$who.log"
done
