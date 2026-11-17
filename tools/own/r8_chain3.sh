#!/bin/bash
# TEST ONLY (eighth round): the smaller tests of register G5, ONE RUN AT A TIME on sandbox run-m.
# Start it with KH2_TEST_SHOW=1 to see the windows.
#   lm2 / lm1   hurt during a Limit (plan row 41): player 2 does the Limit, then the control with player 1
#   sc / scc    Second Chance and Once More in Data Roxas (level 99 against level 1), then the control without
#   eth         player 2 uses Ether / Elixir / Megalixir by shortcut
#   ffd         player 2 in Final Form through a door, then jump and glide
#   gh          a guest's Potion for player 2 (Mulan carries two Potions, player 2's HP is set to 3 at 6000)
#   swap        party swap from player 2's command menu
#   lb / sam    the Large Body (Auron's fight room) and the Bailey fight's Nobodies: both players press Circle
#               and Triangle (Reaction Commands) with strong heroes
# Logs: local/sweep/b15/. Progress: local/sweep/b15/chain3.txt
P="/c/Users/PC FORCE/Desktop/New folder (3)"
O="$P/tests/scripts/own"; L="$P/local/sweep"; B="$L/b15"; T="$P/tools/own"
cd "$P" || exit 1
mkdir -p "$B"
say() { echo "$1 $(date +%H:%M:%S)" >> "$B/chain3.txt"; }
run() {  # run <worker> <kit> <listFile>   (the rest comes from the environment)
  LOGDIR=local/sweep/b15 bash tools/own/sweep4.sh "$1" run-m 29050 28081 "$2" "$3"
  say "$1 done"
}
say "chain3 start"
bash tools/own/r8_chain9.sh     # (put in front on 2026-11-14 00:10: the Keyblade-change fault)
echo "hb17 04 66 HB17_MS405 NO_FRIEND 66 66 66 0" > "$L/list-hb17.txt"
echo "eh21 12 99 EH21_MS101 NO_FRIEND 99 99 99 0" > "$L/list-dr.txt"
echo "mu08 08 79 MU08_MS204 W_FRIEND 79 79 79 0" > "$L/list-mu08.txt"
echo "he05 06 111 HE05_MS102 W_FRIEND_FIX 111 111 111 0" > "$L/list-he05.txt"
echo "hb08 04 91 HB08_MS102 NO_FRIEND 52 91 0 0" > "$L/list-hb08.txt"
LIM="5200,5500,5800,6200,6800,7100,7900,8300,8900"
PROBE="$T/hurt_probe.py" SNAPS=$LIM TAG=r8lm2 P1S="$O/mash_new40_p1.txt" P2S="$O/lim_jump_p2.txt" run lm2 test-own-v33-snapB-god-limit-hurt "$L/list-hb17.txt"
PROBE="$T/hurt_probe.py" SNAPS=$LIM TAG=r8lm1 P1S="$O/lim_jump_p1.txt" P2S="$O/mash_long_p2.txt" run lm1 test-own-v33-snapB-god-limit-hurt "$L/list-hb17.txt"
PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 TAG=r8sc P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" run sc test-own-v33-snapB-sc "$L/list-dr.txt"
PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7400 SNAPS="5200,6000,7000,7400" FRAMES=7500 TAG=r8scc P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" run scc test-own-v33-snapB "$L/list-dr.txt"
PROBE="$T/hp_poll_probe.py" FROM=4600 TO=7900 WATCH=0032F0B0:8 SNAPS="4690,5100,5290,5450,5990,6150,6690,6850,7400,7900" FRAMES=8000 TAG=r8eth \
  P1S="$O/mash_new40_p1.txt" P2S="$O/ether_p2.txt" run eth test-own-v33-snapB-eth "$L/list-hb17.txt"
bash tools/own/dusk_one.sh t15-finaldoor "$P/patches/test-own-v33-forms" test-s1-hb13s.iso 7200 "4690,5000,5250,5450,5800,6030,6060,6230,6430,6460,6900,7150" "$O/finaldoor_p1.txt" "$O/finaldoor_p2.txt" run-m 29050 28081 > "$B/finaldoor.log" 2>&1
echo "TLB misses $(grep -c 'TLB Miss' local/run-m/p1/logs/emulog.txt)" >> "$B/finaldoor.log"
say "ffd done"
PROBE="$T/hp_poll_probe.py" FROM=5900 TO=8900 WATCH=0032E5B8:4,0032E594:4 SNAPS="5200,5990,6100,6300,6600,7000,8000,8900" TAG=r8gh \
  P1S="$O/mash_new40_p1.txt" P2S="$O/mash_long_p2.txt" run gh test-own-v33-snapB-strong-mulan-low "$L/list-mu08.txt"
SNAPS="5390,5430,5500,5560,5630,5700,5900,6500,6560,6610,6680,6750,7400,8800" TAG=r8swap P1S="$O/mash_new40_p1.txt" P2S="$O/swap_p2.txt" run swap test-own-v33-snapB-god "$L/list-mu08.txt"
RC="5200,5400,5600,5800,6000,6200,6400,6700,7000,7500,8000,8900"
SNAPS=$RC TAG=r8lb P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" run lb test-own-v33-snapB-god-strong "$L/list-he05.txt"
SNAPS=$RC TAG=r8sam P1S="$O/mashrc_long_p1.txt" P2S="$O/mashrc_long_p2.txt" run sam test-own-v33-snapB-god-strong "$L/list-hb08.txt"
say "chain3 through"
