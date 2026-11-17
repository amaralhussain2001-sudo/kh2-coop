#!/bin/bash
# TEST ONLY (ninth round, the user's items 1, 2 and 3 of 2026-11-15 evening), candidate v124. Eight lanes at once:
#   xsQ run-m   the last Xemnas's dome (HP 40, capture log): player 1 mashrc_long, player 2 the same FIVE FRAMES LATER
#               -> reflect callbacks sent by both players
#   syE run-v3  Shan-Yu, strong kit, probe sy_count_probe.py (the boss's push count): ONLY player 1 presses
#   syF run-v3b the same, both press in the same frames
#   syG run-v3c the same, player 2 five frames later
#   lbA run-x1  Agrabah city al00, battle program 2 (Large Bodies, no Auron), recorder make_rec_rc.py for source object 0x0001:
#               player 1 idle (ctl_p1), player 2 only Triangle (tri_long_p2)
#   lbB run-x2  the same room, capture log: player 1 walks away (walk_p1), player 2 mashrc_long
#   smA run-x3  Twilight Town tt19, battle program 7 (Samurai), capture log: player 1 idle, player 2 mashrc_long
#   smB run-x4  eh12, battle program 2 (Samurai), capture log: player 1 idle, player 2 mashrc_long
# usage: r9_chain55.sh [ownTag]   (default test-own-v124)
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/r9"; T="$P/tools/own"
cd "$P" || exit 1
X=${1:-test-own-v124}
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain55.txt"; }
say "chain55 start ($X)"
SN="5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,15900"
SYN="5240,5400,5600,6000,6400,7000,7500,8000,9000,10000,11000,11900"
one() {  # one <name> <sandbox> <port> <pine> <kit> <probe> <frames> <snaps> <list> <p1> <p2>
  ISO=${ISO:-test-s1-tt137.iso} PROBE="$T/$6" FROM=4700 TO=$(( $7 - 100 )) SNAPS="$8" FRAMES=$7 TOUT=1800 SWEEP_PROBE_WAIT=1800 LOGDIR=local/sweep/r9 TAG=r9$1 P1S="$O/${10}" P2S="$O/${11}" bash tools/own/sweep4.sh $1 $2 $3 $4 "$5" "$9"
  say "$1 done"
}
ISO=test-v5-tt137.iso one xsQ run-m 29050 28081 $X-snapB-god-cap-xe0028 cap_log_probe2.py 16000 "$SN" "$B/list-eh20.txt" mashrc_long_p1.txt mashrc_long_p2_off5.txt &
one syE run-v3 30150 28061 $X-snapB-god-strong sy_count_probe.py 12000 "$SYN" "$L/list-sy.txt" mashrc_long_p1.txt idle.txt &
one syF run-v3b 30350 28062 $X-snapB-god-strong sy_count_probe.py 12000 "$SYN" "$L/list-sy.txt" mashrc_long_p1.txt mashrc_long_p2.txt &
one syG run-v3c 30550 28063 $X-snapB-god-strong sy_count_probe.py 12000 "$SYN" "$L/list-sy.txt" mashrc_long_p1.txt mashrc_long_p2_off5.txt &
one lbA run-x1 30750 28064 $X-snapB-god-rclb rc_probe.py 16000 "$SN" "$B/list-al00lb.txt" ctl_p1.txt tri_long_p2.txt &
one lbB run-x2 30950 28065 $X-snapB-god-cap cap_log_probe2.py 16000 "$SN" "$B/list-al00lb.txt" walk_p1.txt mashrc_long_p2.txt &
one smA run-x3 31150 28066 $X-snapB-god-cap cap_log_probe2.py 16000 "$SN" "$B/list-tt19sam.txt" ctl_p1.txt mashrc_long_p2.txt &
one smB run-x4 31350 28067 $X-snapB-god-cap cap_log_probe2.py 16000 "$SN" "$B/list-eh12sam.txt" ctl_p1.txt mashrc_long_p2.txt &
wait
say "chain55 through"
