#!/bin/bash
# TEST ONLY (tenth round, item 10, TAKE 5; PREPARED, run it only when lanes run-x3 .. run-x6 are free): THE FORTUNETELLER'S CLEAR SHOT
# WITH ONE HERO. Takes 3 / 4 (r10_chain58.sh, r10_chain59.sh) reached Agrabah with one hero but he never met a Fortuneteller that
# grabbed him: lbH's player 1 got there through fights and lock-on attacks with a second hero around. Now he WALKS first.
# The ORIGINAL GAME + god kit + capture recorder + Large Body kit + lbH's own jump (al00, map 2 / battle 2 / event 0) moved to the
# one-hero discs' jump record 0x01C562D0: patches/test-stock-god-cap-lb-al00solo, disc test-s1-tt137solo.iso. lbH's Fortuneteller
# (object 000B) grabbed player 1 near (0, -2870); the jump start is about (536, -2269), about 800 units away. The one-hero camera's
# direction at the start is not known (it differs from co-op), so the four lanes walk the four stick directions for 140 frames at 4850
# (after the Large Body's grab at the start, about 4720 .. 4816 in lbH), then press ONLY Triangle every 10 frames to 40,000.
# Probe tools/own/cap_log_probe5.py (= cap_log_probe3.py + "act" lines for a lone player 1: where he goes, and every capture: a
# Fortuneteller grab = "obj 000B"). Counted: "TLB Miss ... pc=0x16e1a4 ... [store]" in player 1's emulator log (lbH, two heroes,
# build 21: 26 after the Clear Shot; the original game's answer is the question). run_own2.sh is called directly to pass --timeout 2600.
#   wf1 x3 walkft_up_p1    wf2 x4 walkft_left_p1    wf3 x5 walkft_right_p1    wf4 x6 walkft_down_p1   (NOT fd1..: those names hold
#   the two-form door runs of r10_chain49.sh)
# Read: grep "obj 000B" local/tests/wfN-probe.txt; the "act" lines give his places; the chain prints the null-store counts.
P="/c/Users/PC FORCE/Desktop/New folder (3)"; O="$P/tests/scripts/own"; cd "$P" || exit 1
export FROM=4700 TO=39900 SWEEP_PROBE_WAIT=2700
SN="4840,4990,5200,6000,9000,12000,15000,18000,21000,24000,27000,30000,33000,36000,39900"
f() { n=$1; rm -rf "$P/local/tests/$n"; (python -I "$P/tools/own/cap_log_probe5.py" "$P/local/tests/$n" "$5" "$SN" "$P/local/tests/$n-probe.txt" > /dev/null 2>&1 &)
  OWN_RUN_DIR=$3 OWN_PORT=$4 bash "$P/tools/own/run_own2.sh" "$n" test-s1-tt137solo.iso 40000 4.0 "$SN" "$O/$2" "$O/idle.txt" idle 1 "$P/patches/test-stock-god-cap-lb-al00solo" --pine "$5" --timeout 2600 2>&1 | tail -1 | cut -c1-110
  sleep 8; echo "$n $3 null stores at 0x16e1a4: $(grep -c 'pc=0x16e1a4' "$P/local/$3/p1/logs/emulog.txt") | all fault lines $(grep -c 'pc=0x' "$P/local/$3/p1/logs/emulog.txt") | Fortuneteller grabs $(grep -c 'obj 000B' "$P/local/tests/$n-probe.txt" 2>/dev/null)"; }
f wf1 walkft_up_p1.txt run-x3 31150 28066 &
f wf2 walkft_left_p1.txt run-x4 31350 28067 &
f wf3 walkft_right_p1.txt run-x5 31550 28068 &
f wf4 walkft_down_p1.txt run-x6 31750 28069 &
wait
