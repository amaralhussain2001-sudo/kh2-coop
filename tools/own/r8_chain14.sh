#!/bin/bash
# TEST ONLY (eighth round, register G5, second try): the Large Body by player 2. In run lb player 1's Triangle
# started Auron's Limit, which cleared the room before player 2 met the Large Body. Now player 1 only starts the
# game and stands still, the heroes are NOT strong (HP held only), player 2 presses Circle / Triangle / R1.
# ONE RUN on sandbox run-m. Log: local/sweep/b15/lb2.log, pictures local/tests/r8lb2-HE05_MS102-111
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"
cd "$P" || exit 1
SNAPS="5200,5300,5400,5500,5600,5700,5800,5900,6000,6200,6400,6700,7000,7500,8000,8900" LOGDIR=local/sweep/b15 TAG=r8lb2 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" \
  bash tools/own/sweep4.sh lb2 run-m 29050 28081 test-own-v33-snapB-god "$L/list-he05.txt"
# sam2: the Bailey fight with its own program (map = battle = event = 52: the heroes stand in group b_40 with 12 Dusks and
# 5 of object 0x0136). Run sam used battle program 91, which has no heroes. Player 1 idle, HP held, not strong.
echo "hb08 04 52 HB08_MS102 NO_FRIEND 52 52 52 0" > "$L/list-hb08b.txt"
SNAPS="5200,5300,5400,5500,5600,5700,5800,5900,6000,6200,6400,6700,7000,7500,8000,8900" LOGDIR=local/sweep/b15 TAG=r8sam2 P1S="$O/ctl_p1.txt" P2S="$O/mashrc_long_p2.txt" bash tools/own/sweep4.sh sam2 run-m 29050 28081 test-own-v33-snapB-god "$L/list-hb08b.txt"
# (added 2026-11-14 00:48) kcfix2: the Keyblade change with the fix, the menu left closed afterwards: both heroes attack with the new Keyblade
SNAPS="5540,5860,6050,6070,6100,6130,6200,6600,7000,7400" FRAMES=7500 LOGDIR=local/sweep/b15 TAG=r8kcfix2 P1S="$O/keychg2_p1.txt" P2S="$O/keychg_p2.txt" bash tools/own/sweep4.sh kcfix2 run-m 29050 28081 test-own-v36-menu "$L/list-hb13.txt"
# (added 2026-11-14 00:50) gh3: a GUEST heals player 2. Cerberus's room (party = Auron alone): Auron carries two Potions (block save + 0x2940),
# player 2's HP is set to 3 at 6000. In run gh2 Goofy was the one who used an item at once; here only the guest can.
echo "he07 06 114 HE07_MS103 W_FRIEND_ONLY 114 114 114 0" > "$L/list-he07.txt"
PROBE="$P/tools/own/heal_poll_probe.py" FROM=5950 TO=6600 WATCH=0032E4A4:4 SNAPS="5990,6020,6060,6100,6300,6600" FRAMES=6700 LOGDIR=local/sweep/b15 TAG=r8gh3 P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" bash tools/own/sweep4.sh gh3 run-m 29050 28081 test-own-v33-snapB-strong-auron-low "$L/list-he07.txt"
# (added 2026-11-14 00:52) ffd2: Final Form through the west door of Merlin's House (the path from run ex13), then jump and glide
bash tools/own/dusk_one.sh t15-finaldoor2 "$P/patches/test-own-v33-forms" test-s1-hb13s.iso 7400 "4690,5000,5250,5450,5700,5900,6100,6230,6260,6450,6630,6660,6900,7100,7350" "$O/finaldoor2_p1.txt" "$O/finaldoor2_p2.txt" run-m 29050 28081 > "$B/finaldoor2.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/finaldoor2.log"
echo "chain14 through $(date +%H:%M:%S)" >> "$B/chain14.txt"
