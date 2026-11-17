#!/bin/bash
# TEST ONLY (eighth round, register F4 and the Keyblade fault): THE TRUE ONE-HERO RUNS, on the jump disc WITHOUT the
# second hero (local/iso/test-s1-tt137solo.iso). That disc's jump record is NOT at 0x01C56310 (run kc1 stayed in the
# disc's own fight), so first:
#   jf    find the record's address (tools/own/jumpfind_probe.py) -> local/tests/t15-jfsolo-probe.txt
#   kc1b  the Keyblade change with ONE hero (the control of the fault)
#   s1p   the heap, the build with ONE hero: the Hydra, the 1000 Heartless, Shan-Yu
#   s1n   the heap, NO patch, one hero: the same three
# ONE RUN AT A TIME on sandbox run-m. Logs: local/sweep/b15/; progress local/sweep/b15/chain6.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"; S="$P/tests/scripts/merge"
cd "$P" || exit 1
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain6.txt"; }
LONG="5200,7000,9000,11000,13000,15000,17000,19000,21000,23900"
cat > "$L/list-h3.txt" <<'EOL'
he18 06 171 HE18_MS108 DEFAULT 171 171 171 0
hb17 04 66 HB17_MS405 NO_FRIEND 66 66 66 0
mu09 08 75 MU09_MS108 W_FRIEND 75 75 75 0
EOL
say "chain6 start"
# (put in front on 2026-11-14 00:36) kcvt: the Keyblade change with the freed-object recorder at 0x0017FE10 (make_rec_vt.py)
PROBE="$T/recbad_probe.py" SNAPS="5060,5540,5860,6200,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kcvt P1S="$O/keychg_p1.txt" P2S="$O/keychg_p2.txt" bash tools/own/sweep4.sh kcvt run-m 29050 28081 test-own-v33-menu-vt "$L/list-hb13.txt"
say "kcvt done"
PROBE="$T/jumpfind_probe.py" JUMP="02:89" bash tools/own/dusk_one.sh t15-jfsolo "$P/patches/test-own-v33" test-s1-tt137solo.iso 5000 "4700" "$S/newgame_only.txt" "$O/idle.txt" run-m 29050 28081 > "$B/jfsolo.log" 2>&1
REC=$(grep -o "record at [0-9A-F]*" "$P/local/tests/t15-jfsolo-probe.txt" | head -1 | awk '{print $3}')
say "jf done: record at ${REC:-NOT FOUND}"
[ -z "$REC" ] && { say "chain6 through (no record address: nothing more run)"; exit 1; }
export JUMPREC=$REC
ISO=test-s1-tt137solo.iso SNAPS="5060,5360,5540,5860,5960,6200,6600,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kc1b P1S="$O/keychg_p1.txt" P2S="$O/idle.txt" \
  bash tools/own/sweep5.sh kc1b run-m 29050 28081 test-own-v33-menu "$L/list-hb13.txt"
say "kc1b done"
ISO=test-s1-tt137solo.iso PROBE="$T/heap_probe.py" SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8s1p \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep5.sh s1p run-m 29050 28081 test-own-v33-snapB-god-heap "$L/list-h3.txt"
say "s1p done"
ISO=test-s1-tt137solo.iso PROBE="$T/heap_probe.py" SNAPS=$LONG FRAMES=24000 TOUT=1500 SWEEP_PROBE_WAIT=1500 LOGDIR=local/sweep/b15 TAG=r8s1n \
  P1S="$O/mashrc_long_p1.txt" P2S="$O/idle.txt" bash tools/own/sweep5.sh s1n run-m 29050 28081 test-empty-god-heap "$L/list-h3.txt"
say "s1n done"
say "chain6 through"
