#!/bin/bash
# TAKE 3 (fb1 .. fb4): test-s1-al2solo starts al00 program 2 WITH its story scene (fa1 .. fa4 stayed in its party menu). Now lbH's own jump
# (make_jumpkit2.py 07 0 2 2 0 0 = map 2, battle 2, event 0) MOVED to the one-hero discs' record 0x01C562D0 (jumprec_probe.py jr1 / jr3), on
# test-s1-tt137solo: patches/test-stock-god-cap-lb-al00solo.
# TEST ONLY (tenth round, item 10, take 2; a fork's run, lanes run-x3 .. run-x6): fo1 .. fo4 (r10_chain55.sh) never reached Agrabah:
# the jump kit does not take on test-s1-tt137solo (the pictures show its own Twilight Town fight). NEW one-hero disc that starts IN
# al00 program 2: local/iso/test-s1-tt137solo.iso (`build_disc.py al2solo --jump "AL 2" --party DEFAULT --no-twin`). The ORIGINAL GAME
# + god kit + capture recorder + Large Body kit (patches/test-stock-god-cap-lb), 24,000 frames, probe cap_log_probe3.py (a Fortuneteller
# grab = captor obj 000B); count "TLB Miss ... pc=0x16e1a4 ... [store]" in player 1's emulator log (lbH, two heroes: 26).
#   fa1 x3 mashrc_long_p1   fa2 x4 tri_long_p1   fa3 x5 mashrc_long_p1_s7   fa4 x6 tri_long_p1_s7
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,23900"
f() { PROBE="$P/tools/own/cap_log_probe3.py" SWEEP_PROBE_WAIT=2400 bash tools/own/dusk_one.sh $1 "$P/patches/test-stock-god-cap-lb-al00solo" test-s1-tt137solo.iso 24000 "$SN" "$O/$2" "$O/idle.txt" $3 $4 $5; }
f fb1 mashrc_long_p1.txt run-x3 31150 28066 &
f fb2 tri_long_p1.txt run-x4 31350 28067 &
f fb3 mashrc_long_p1_s7.txt run-x5 31550 28068 &
f fb4 tri_long_p1_s7.txt run-x6 31750 28069 &
wait
for r in x3 x4 x5 x6; do echo "run-$r p1 null stores at 0x16e1a4: $(grep -c 'pc=0x16e1a4' "$P/local/run-$r/p1/logs/emulog.txt") | all fault lines $(grep -c 'pc=0x' "$P/local/run-$r/p1/logs/emulog.txt")"; done
