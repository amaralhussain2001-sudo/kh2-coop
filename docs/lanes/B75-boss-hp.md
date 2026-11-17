# Lane B75: bosses get 75 % more HP when two heroes play

Written 2026-11-10. Task: "if two players, give the bosses 75 % hp more"; normal enemies stay as they are; the 75
must be ONE number that is easy to change after playing.
All tests SINGLE-PC (one or two linked emulator copies on this PC, sandbox copies `local\run-b75`, port 30250, PINE
28201), scripted buttons, game patch `patches\merged-v2`, discs built from the English build 3 candidate with the
"jump disc" method of lane B. Every test disc is deleted again; recipes are in `local\variants\b75-*`, logs and
screenshots in `local\tests\b75-*`.
Labels: **VERIFIED** (test id or file), **HYPOTHESIS**, **FROM MEMORY**.

## Summary

| Question | Answer |
|---|---|
| Where does boss HP come from? | One table in the battle data file `00battle.bin` (the enemy table, 229 entries). Each object's own AI script names the entry it uses. Real HP = table value x a percentage that depends on the battle level. VERIFIED by reading the game program and by measuring in the game. |
| What counts as a boss? | An entry is a boss entry when the AI script of an object that the game's own object list calls BOSS or L_BOSS (large boss) takes it. That gives **91 entries; 86 are raised, 5 are left alone on purpose** (the cage of a race mission, and four entries whose only placed users are allies). |
| How is the +75 % done? | **At disc-build time, in the data**: `tools\lane-b75\scale_boss_hp.py` writes a copy of `00battle.bin` in which the health values of the 86 entries are multiplied. Same file size, only those 16-bit numbers change, same input always gives the same output. No game code is needed for the HP itself. |
| Where is the one number? | `--percent 75` of `scale_boss_hp.py` (in the disc builder: `--boss-percent 75`). A single boss can get its own number in the list `tools\lane-b75\data\boss_entries.csv` (column `percent`). |
| **Important finding** | **The game's enemy HP gauge cannot show more than 3400 HP: above that the game freezes** as soon as the gauge is drawn. The strongest bosses of the original game sit at exactly 3400. VERIFIED by tests and by reading the routine. All story bosses stay under the limit with +75 %; **25 entries (the cups at high level, Sephiroth, the Final Mix silhouettes, the data rematches, Lingering Will, one value of the final dragon) would pass it.** |
| What was done about it? | Two ways, both built and tested. **(1) Safe default:** the tool raises such an entry only as far as 3400 HP allows ("gauge cap"). **(2) Full +75 % for everybody:** a small patch of the gauge (50 patch lines, lane's code cave) that shows a boss above 3400 HP in proportion; with it the tool is run with `--gauge-patch` and nothing is capped. I recommend (2); it needs the parent to add the lines to the game patch. |
| Tests | Three bosses: Shan-Yu (early story), Thresholder with Possessor (scripted HP phases, fight played to the bonus screen), Lingering Will (Final Mix, fixed level 99). HP is exactly x1.75, normal enemies and objects unchanged, percent-based phases keep their percentages, two linked copies stay in sync (data change and gauge patch). Details and what was NOT tested: section "Tests". |

## 1. Where boss HP comes from (engine facts)

Game program `SLPM_666.75` (file `local\iso-files\SLPM_666.75`). All addresses VERIFIED by disassembly unless marked.

- Enemy table: entry "enmp" of `00battle.bin` (21,076 bytes): header (version 2, count 229), then 229 entries of
  92 bytes: id, level, 32 health values (16-bit), max-damage and min-damage limits, 7 weakness values, experience,
  prize, bonus level. Ids run from 0 to 253 with gaps.
- The loader keeps the table pointer at `0x01D5BAAC`. `0x001DB5A8(id)` finds an entry (binary search; unknown id
  falls back to id 69).
- `0x001A0EE0(slot, entry)` fills a unit slot: level = the entry's own level if it is not 0 (`0x001C0C80`), else the
  current battle level (`0x001C0CC8`); for each of the 32 health values
  **HP = (HpMultiplier(level) x value + 99) / 100**, stored as (current, maximum, 0) at slot + 12 x index.
  The max-damage and min-damage limits are computed from the maximum HP, so they follow the change by themselves.
- HpMultiplier per level comes from the level table "lvpm" of the same file: 20 % at level 1, 100 % at level 50,
  150 % at level 80, 181 % at level 99.
- Unit slots: slot k at `0x01C6C750 - 0x268 x (k - 1)`; +0x264 points at the table entry the slot was filled from.
- **The number in the object list (for example Shan-Yu 5012) does NOT choose the entry.** Each object's AI script
  (inside `obj\<MODEL>.mdlx`) calls `trap_btlobj_set_sheet` (or `trap_btlobj_dup_sheet`) with the entry id. The id is
  a constant, a parameter of a set-up routine, or picked by the placement's argument (Axel: 78 or 148).
  `tools\lane-b75\scan_ai2.py` reads all 810 scripts: 277 set an entry, 274 are fully resolved
  (`local\analysis\lane-b75\scan\ai_ids.tsv`). Not resolved: three normal enemies (Creeper, Assassin, Dusk).
- Battle level of a fight: the room program's `BattleLevel N` command if it has one (cups, Sephiroth, silhouettes,
  data rematches), else the world's level. World level = sum of the rows of the table "btlv" whose story flag is set
  (checked against the known levels: Twilight Town 47, Hollow Bastion 45, The World That Never Was 50). Two rows
  (flags 15 and 17) would give every world level 99 / 60; HYPOTHESIS: they are never set in normal play.
  Nine entries carry their own fixed level 99 (data rematches, Lingering Will).
- Scripts handle phases by percentage: `trap_sheet_hp_rate` (91 uses), minimum HP 0 or 1, refills "to maximum".
  The only absolute comparisons found are "HP < 2". So phases do not move when the maximum grows (measured on
  Shan-Yu, below). Lists: `local\analysis\lane-b75\scan\hp_script_calls.txt`, `hp_abs_thresholds.txt`.
- Entries with several health values (parts or second pools): 25 Storm Rider, 114 giant Sark, 138 Jafar, 172 final
  dragon, 200 Vexen, 244 Lingering Will. **All non-zero values of a chosen entry are multiplied.**

## 2. The HP gauge limit (found during the tests)

**What happens.** With the Scan ability the game draws the target's HP gauge (top right): one long bar and up to 16
small bars, 200 HP each = **3400 HP**. The routines that set the gauge loop over (HP - 1) / 200 small bars without
a bound (`0x00154B98` set, `0x00154C10` update after damage); the gauge object has exactly 16 small bars (array
at +2904, 816 bytes apart, the HP fields follow at +15552). The 17th walks into other data and the game stops.

- VERIFIED by test: Lingering Will disc with +75 % (5950 HP) and Scan froze at the first frame of the fight, twice
  (`b75-lw-s2`, `b75-lw-s3`: all screenshots identical). The control disc (3400 HP) with Scan runs (`b75-lw-c2`).
  On the control disc a test write of the maximum HP to 3600, 3800, 4000, 4600, 5200 or 5950 froze the game each
  time; rewriting 3400 did not (`b75-lw-g3400` ... `b75-lw-g5950`). Emulator log of the freeze: first fault at
  pc `0x00239C68` reading address `0x634` = animation 44 started on a sequence object without data; 44 is the
  animation both loops start for each small bar (`0x00154BE4`, `0x00154C88`).
- Without Scan the gauge is not drawn and nothing happens (`b75-lw-s1`: +75 % Lingering Will runs). A fresh test
  save has no Scan; that is why the first tests did not show it. In normal play the heroes have Scan early: the
  bonus table hands it out as a fight bonus (entry 178: character 14, ability 0x8A) and it is in starting ability
  sets of the player table
  (data read with `tools\lane-b75\find_scan_ability.py`); FROM MEMORY: Sora has it from the start of his story.
- The designers used the limit exactly: the table value 1878 at level 99 is 3400 HP, and seven original entries have
  1878 (Lingering Will, several data rematches, Lexaeus, Marluxia).

**Who would pass 3400 with +75 %.** `tools\lane-b75\fight_levels.py` joins every boss entry with the rooms and
programs that place it and their battle level (`local\analysis\lane-b75\scan\fight_levels.tsv`, short form
`tools\lane-b75\data\boss_levels.csv`). Result: **every story boss stays below** (largest: Prison Keeper 3010 at
the world's highest level). **25 entries pass it**: Sephiroth (level 80), the main value of the final dragon
(3500 at level 50), the bosses of the level-99 cup rounds (Hades, Cerberus, Pete, Hercules at level 80, Volcano and
Blizzard Lord), the five silhouette / data entries of Vexen, Lexaeus, Marluxia, Larxene, Zexion, Roxas, and the
nine fixed level-99 entries. They are marked **over** in the boss table.

**Way 1, the safe default: gauge cap.** Without `--gauge-patch` the tool raises a value only as far as its real HP
stays at or under 3400 at the highest level the entry is ever fought at. With 75 %: 61 entries get the full +75 %,
18 get less (+7 % ... +70 %), 6 get nothing because they are already at 3400 (Lexaeus, Marluxia, Xemnas data,
Axel data, Xaldin data, Saix data), and Lingering Will keeps its 3400 (only its second value grows). Weak point: an
entry shared by a story fight and a level-99 fight is capped for both (story Hades gets +25 %).

**Way 2, recommended: the gauge patch.** `tools\lane-b75\make_gauge_patch.py` writes 50 patch lines
(`tools\lane-b75\data\gauge_patch_lines.txt`). Three detours into the lane's code cave (`0x000F3800`-`0x000F38AF`,
one data word at `0x000F3FF0`):

| Hook | Routine | What the detour does |
|---|---|---|
| `0x00154450` | gauge start (gauge, HP, maximum) | keeps the real maximum in the data word; gives the gauge min(maximum, 3400) |
| `0x00154B98` | gauge set (gauge, HP) | if the real maximum is above 3400: shown HP = HP x 3400 / real maximum (rounded up); never more than 3400 |
| `0x00154C10` | gauge update after damage | the same |

For a target with 3400 HP or less nothing changes. Only the picture changes; the real HP in the unit slot is not
touched. There is one target gauge in the original game (pointer at `0x003485F8`), so one data word is enough.
The six replaced instructions are checked against the game program by the generator. No other lane's patch file
uses these addresses or the cave (searched `patches\*` on 2026-11-10).
With this patch in the game patch, build with `--gauge-patch`: all 86 entries get the full number.

## 3. Method: data at build time (a) against a runtime routine (b)

| | (a) data change at disc-build time (chosen) | (b) routine in the game patch |
|---|---|---|
| Where | `00battle.bin` on the disc, 86 entries | hook where a slot is filled (`0x001A0EE0`, or `0x001B3C00` / `0x001B3C58`), object type via (object+8)+4, in the cave |
| The one number | `--percent` at build time; rebuild the disc to change it (minutes) | one patch line; could change without a new disc |
| Sync | the same disc on both PCs = the same numbers; nothing runs differently | code runs the same on both PCs too, but it is more code in a place every enemy passes |
| "Only with two heroes" | the disc is the two-player disc; a one-player disc is built with 0 | could look at the twin pointer (`0x000F05CC`) at run time |
| Limits | 16-bit table values: largest after +75 % is 3500 of 32767; real HP is 32-bit | none from the table |
| Tested | yes (below) | not built |

(a) is simpler and touches no game code. The project always plays with two heroes, so a run-time switch is not
needed. The gauge limit is the same problem for both ways.

Commands:

```
python -I tools/lane-b75/scale_boss_hp.py local/extract/kh2/00battle.bin <build folder>/00battle.bin --percent 75 [--gauge-patch] [--report FILE]
python -I tools/lane-b75/build_disc_b75.py <name> --boss-percent 75 [--gauge-patch] [--jump "WORLD LOCALSET"] [--rooms a,b]
```

- new value = round(old x (100 + percent) / 100) for every non-zero health value of a listed entry.
- `--percent 0` gives a file byte-identical to the original (VERIFIED, `cmp`).
- The tool refuses a value above 32767 and checks that only health bytes of the table changed.
- +75 % with `--gauge-patch`: 86 entries changed, 191 bytes, SHA-1 `f7b67bcca2ce57d614a8d43b2c6cd4ebb106b7bd`.
  +75 % with the gauge cap (default): 80 entries changed, 177 bytes, SHA-1 `08f63e80b0c3b339d3899814bd9b722fcb83b9bc`.
  Original file: `dbd3203924dea93f1a48135add326dfcb8e06898`. Each built twice with the same result.

## 4. Boss list

Rule: see Summary. The list file is `tools\lane-b75\data\boss_entries.csv` (made by `make_boss_list.py`; columns:
entry id, percent, decision, names, objects, health, note). Names are community names (project khbr, used as a
reading aid; its boss entry numbers agree with mine for 86 models) or my own where it has none.
"Highest level" is the highest battle level of any placement of that entry: for story fights this is the world's
level at the end of the story, so the first-visit fight has less HP than shown. "Real HP" is for the largest value.
**over** = above the gauge limit of 3400 (fine with the gauge patch; capped without it, last column).

| entry | boss | objects | table health now | table health +75 % | highest level | real HP there now | real HP there +75 % | with the gauge cap instead |
|---|---|---|---|---|---|---|---|---|
| 15 | Lock | N_NM050_BTL N_NM050_BTL_TOY | 200 | 350 | 41 | 172 | 301 | same |
| 16 | Shock | N_NM060_BTL N_NM060_BTL_TOY | 200 | 350 | 41 | 172 | 301 | same |
| 17 | Barrel | N_NM070_BTL N_NM070_BTL_TOY | 200 | 350 | 41 | 172 | 301 | same |
| 18 | Hades (story) | B_HE030 B_HE030_HE05 B_HE030_PART | 1500 | 2625 | 99 | 2715 | 4752 **over** | 1878 (HP 3400, +25 %) |
| 19 | Cerberus (story) | B_HE020 | 1000 | 1750 | 99 | 1810 | 3168 | same |
| 20 | Hydra | B_HE100 | 1050 | 1838 | 39 | 861 | 1508 | same |
| 22 | Dark Thorn | B_BB110 | 1000 | 1750 | 36 | 770 | 1348 | same |
| 23 | Shadow Stalker | B_BB120 | 450 | 788 | 36 | 347 | 607 | same |
| 24 | Possessor (inside Thresholder) | B_BB130 | 250 | 438 | 36 | 193 | 338 | same |
| 25 | Storm Rider | B_MU120 | 1600 100 100 | 2800 175 175 | 35 | 1216 | 2128 | same |
| 26 | Pete at Olympus (two missions) | N_EX760_BTL_HERCULES N_EX760_BTL_MEGARA | 600 | 1050 | 39 | 492 | 861 | same |
| 71 | Shan-Yu | B_MU100 | 1300 | 2275 | 35 | 988 | 1729 | same |
| 72 | Shan-Yu's falcon | B_MU110 | 300 | 525 | 35 | 228 | 399 | same |
| 73 | Beast (as opponent) | P_BB000_BTL | 400 | 700 | 36 | 308 | 539 | same |
| 74 | Thresholder | B_BB100 | 350 | 613 | 36 | 270 | 473 | same |
| 75 | Oogie Boogie | B_NM000 | 650 | 1138 | 41 | 559 | 979 | same |
| 78 | Axel (boss fight) | B_EX110 B_EX110_FRIEND B_EX110_SKIRMISH | 1500 | 2625 | 47 | 1425 | 2494 | same |
| 79 | the cage (Timeless River) | F_WI380 F_WI380_RTN | 700 | unchanged | 34 | 518 | unchanged | unchanged |
| 86 | Twilight Thorn | B_EX100 | 1500 | 2625 | 47 | 1425 | 2494 | same |
| 87 | Xaldin | B_EX130 | 1500 | 2625 | 36 | 1155 | 2022 | same |
| 88 | Demyx; Demyx OC | B_EX120 B_EX120_HB | 1500 | 2625 | 45 | 1380 | 2415 | same |
| 89 | Luxord | B_EX150 | 1500 | 2625 | 50 | 1500 | 2625 | same |
| 90 | Xemnas (two fights) | B_EX170 B_EX170_LAST | 1500 | 2625 | 50 | 1500 | 2625 | same |
| 91 | the three hyenas (one entry) | B_LK100 B_LK100_00 B_LK100_10 B_LK100_20 | 500 | 875 | 43 | 445 | 779 | same |
| 94 | Scar | B_LK110 | 1500 | 2625 | 43 | 1335 | 2337 | same |
| 95 | Groundshaker | B_LK120 | 1600 | 2800 | 43 | 1424 | 2492 | same |
| 99 | Barbossa | B_CA010 | 1200 | 2100 | 37 | 948 | 1659 | same |
| 100 | Sark | N_TR010_BTL | 500 | 875 | 45 | 460 | 805 | same |
| 102 | part of the Hydra fight | B_HE110 | 160 | 280 | 39 | 132 | 230 | same |
| 106 | Hostile Program | B_TR000 | 1500 | 2625 | 45 | 1380 | 2415 | same |
| 113 | Pete of the past | N_WI010_BTL N_WI010_BTL_VS | 250 | 438 | 34 | 185 | 325 | same |
| 114 | Giant Sark | N_TR010_BTL_L | 250 50 50 | 438 88 88 | 45 | 230 | 403 | same |
| 115 | field object, Sark / MCP fight | F_TR050 | 160 | 280 | 45 | 148 | 258 | same |
| 119 | Prison Keeper | B_NM100 N_NM070_BTL_2 | 2000 | 3500 | 41 | 1720 | 3010 | same |
| 120 | The Experiment | B_NM110 | 1500 | 2625 | 41 | 1290 | 2258 | same |
| 122 | Volcano Lord (story) | B_AL100_1ST B_AL100_FIRE | 800 | 1400 | 99 | 1448 | 2534 | same |
| 123 | Blizzard Lord (story) | B_AL100_2ND B_AL100_ICE | 800 | 1400 | 99 | 1448 | 2534 | same |
| 124 | Grim Reaper (first fight) | B_CA050 | 1000 | 1750 | 37 | 790 | 1383 | same |
| 127 | Pete (cage chase, Timeless River) | N_EX760_BTL_WILLY | 250 | 438 | 34 | 185 | 325 | same |
| 128 | Pete (Timeless River, final) | N_EX760_BTL | 1600 | 2800 | 34 | 1184 | 2072 | same |
| 130 | Riku (Land of Dragons) | N_EX940_BTL | 1000 | 1750 | 35 | 760 | 1330 | same |
| 131 | Leon (ally version only) | N_HB530_BOSS N_HB530_BTL | 150 | unchanged | 45 | 138 | unchanged | unchanged |
| 133 | Xigbar | B_EX140 | 1300 | 2275 | 50 | 1300 | 2275 | same |
| 134 | Saix | B_EX160 | 1500 | 2625 | 50 | 1500 | 2625 | same |
| 138 | Jafar | B_AL020 | 1000 110 60 60 | 1750 193 105 105 | 40 | 840 | 1470 | same |
| 139 | Tifa (ally version only) | N_HB570_BOSS N_HB570_BTL | 500 | unchanged | 45 | 460 | unchanged | unchanged |
| 140 | Sephiroth | N_HB590_BTL N_HB630 | 2000 | 3500 | 80 | 3000 | 5250 **over** | 2266 (HP 3399, +13 %) |
| 141 | MCP | B_TR020 | 1000 | 1750 | 45 | 920 | 1610 | same |
| 142 | Cloud (ally version only) | N_HB550_BOSS N_HB550_BTL | 1000 | unchanged | 45 | 920 | unchanged | unchanged |
| 143 | Yuffie (ally version only) | N_HB580_BOSS N_HB580_BTL | 500 | unchanged | 45 | 460 | unchanged | unchanged |
| 148 | Axel (first skirmish) | B_EX110 B_EX110_SKIRMISH | 500 | 875 | 47 | 475 | 832 | same |
| 153 | field object, final Xemnas area | F_EH100 | 1000 | 1750 | 50 | 1000 | 1750 | same |
| 154 | Grim Reaper (second fight) | B_CA050 | 1000 | 1750 | 37 | 790 | 1383 | same |
| 160 | Armored Xemnas | B_EX260 | 1000 | 1750 | 50 | 1000 | 1750 | same |
| 172 | final dragon (Xemnas) | B_EX330 | 2000 600 1200 1200 1000 1000 | 3500 1050 2100 2100 1750 1750 | 50 | 2000 | 3500 **over** | 3400 1050 2100 2100 1750 1750 (HP 3400, +70 %) |
| 177 | Hades (cups) | B_HE030_CLSM | 1500 | 2625 | 99 | 2715 | 4752 **over** | 1878 (HP 3400, +25 %) |
| 178 | Hercules | N_HE010_BTL_CLSM | 1500 | 2625 | 80 | 2250 | 3938 **over** | 2266 (HP 3399, +51 %) |
| 179 | Pete (cups) | N_EX760_BTL_CLSM | 1600 | 2800 | 99 | 2896 | 5068 **over** | 1878 (HP 3400, +17 %) |
| 180 | Leon | N_HB530_BTL2 | 700 | 1225 | 99 | 1267 | 2218 | same |
| 181 | Cloud | N_HB550_BTL2 | 800 | 1400 | 99 | 1448 | 2534 | same |
| 182 | Tifa | N_HB570_BTL2 | 600 | 1050 | 99 | 1086 | 1901 | same |
| 183 | Yuffie | N_HB580_BTL2 | 500 | 875 | 99 | 905 | 1584 | same |
| 184 | Leon | N_HB530_BTL2 | 700 | 1225 | 99 | 1267 | 2218 | same |
| 185 | Cloud | N_HB550_BTL2 | 800 | 1400 | 99 | 1448 | 2534 | same |
| 186 | Tifa | N_HB570_BTL2 | 600 | 1050 | 99 | 1086 | 1901 | same |
| 187 | Yuffie | N_HB580_BTL2 | 500 | 875 | 99 | 905 | 1584 | same |
| 188 | Leon | N_HB530_BTL2 | 700 | 1225 | 99 | 1267 | 2218 | same |
| 189 | Cloud | N_HB550_BTL2 | 400 | 700 | 99 | 724 | 1267 | same |
| 190 | Tifa | N_HB570_BTL2 | 300 | 525 | 99 | 543 | 951 | same |
| 191 | Yuffie | N_HB580_BTL2 | 500 | 875 | 99 | 905 | 1584 | same |
| 192 | Leon | N_HB530_BTL2 | 350 | 613 | 99 | 634 | 1110 | same |
| 195 | Yuffie | N_HB580_BTL2 | 250 | 438 | 99 | 453 | 793 | same |
| 196 | Hades (final fight / cups) | B_HE030 | 1500 | 2625 | 99 | 2715 | 4752 **over** | 1878 (HP 3400, +25 %) |
| 197 | Volcano Lord (cups) | B_AL100_1ST B_AL100_FIRE | 1200 | 2100 | 99 | 2172 | 3801 **over** | 1878 (HP 3400, +56 %) |
| 198 | Blizzard Lord (cups) | B_AL100_2ND B_AL100_ICE | 1200 | 2100 | 99 | 2172 | 3801 **over** | 1878 (HP 3400, +56 %) |
| 199 | Cerberus (cups) | B_HE020 | 1500 | 2625 | 99 | 2715 | 4752 **over** | 1878 (HP 3400, +25 %) |
| 200 | Vexen (silhouette and data) | N_CM040_BTL | 1500 100 | 2625 175 | 99 | 2715 | 4752 **over** | 1878 175 (HP 3400, +25 %) |
| 213 | Roxas (story / Final Mix fight) | B_EX390 | 1300 | 2275 | 99 | 2353 | 4118 **over** | 1878 (HP 3400, +44 %) |
| 214 | Lexaeus (silhouette and data) | N_CM020_BTL | 1878 | 3287 | 99 | 3400 | 5950 **over** | 1878 (HP 3400, +0 %) |
| 215 | Marluxia (silhouette and data) | N_CM000_BTL | 1878 | 3287 | 99 | 3400 | 5950 **over** | 1878 (HP 3400, +0 %) |
| 216 | Larxene (silhouette and data) | B_EX400 | 1500 | 2625 | 99 | 2715 | 4752 **over** | 1878 (HP 3400, +25 %) |
| 217 | Zexion (silhouette and data) | B_EX370 | 1200 | 2100 | 99 | 2172 | 3801 **over** | 1878 (HP 3400, +56 %) |
| 239 | Xemnas, both forms (data rematch) | B_EX170_LAST_LV99 B_EX170_LV99 | 1878 | 3287 | 99 fixed | 3400 | 5950 **over** | 1878 (HP 3400, +0 %) |
| 240 | Demyx (Data) | B_EX120_HB_LV99 | 1500 | 2625 | 99 fixed | 2715 | 4752 **over** | 1878 (HP 3400, +25 %) |
| 242 | Roxas (data rematch) | B_EX390 | 1750 | 3063 | 99 fixed | 3168 | 5545 **over** | 1878 (HP 3400, +7 %) |
| 243 | Luxord (Data) | B_EX150_LV99 | 1500 | 2625 | 99 fixed | 2715 | 4752 **over** | 1878 (HP 3400, +25 %) |
| 244 | Lingering Will (Terra) | B_EX420 | 1878 50 | 3287 88 | 99 fixed | 3400 | 5950 **over** | 1878 88 (HP 3400, +0 %) |
| 245 | Axel (Data) | B_EX110_LV99 | 1878 | 3287 | 99 fixed | 3400 | 5950 **over** | 1878 (HP 3400, +0 %) |
| 246 | Xaldin (Data) | B_EX130_LV99 | 1878 | 3287 | 99 fixed | 3400 | 5950 **over** | 1878 (HP 3400, +0 %) |
| 252 | Xigbar (Data) | B_EX140_LV99 | 1600 | 2800 | 99 fixed | 2896 | 5068 **over** | 1878 (HP 3400, +17 %) |
| 253 | Saix (Data) | B_EX160_LV99 | 1878 | 3287 | 99 fixed | 3400 | 5950 **over** | 1878 (HP 3400, +0 %) |

### Doubtful cases, with a recommendation each

| Case | What the data says | Recommendation |
|---|---|---|
| Entry 79, the cage in "Break the cage before Pete escapes!" (WI02_MS103) | the object is typed BOSS, the mission is a race against a gauge | **left unchanged** (percent 0 in the list). Pete in that chase (127) is raised; hitting him is not the goal. |
| Entries 131, 139, 142, 143 | used by BOSS-typed objects that are placed in no room, and by the ally versions of Leon, Tifa, Cloud, Yuffie (Hollow Bastion battle) | **left unchanged**: raising them would only make the allies tougher. Their cup versions (180-195) are separate entries and are raised. |
| 15, 16, 17 Lock, Shock, Barrel | shared with the toy versions of "Make some presents!", whose scripts never read HP (minimum HP 1) | raise; no effect on the present game. |
| 78 Axel | shared with the ally Axel (B_EX110_FRIEND) | raise; the ally also gets +75 % HP, harmless. |
| 113 Pete of the past | shared with a non-boss version (N_WI010_BTL) | raise. |
| 115 (F_TR050, Sark / MCP fight) and 153 (F_EH100, final Xemnas area) | field objects that the object list types BOSS; 160 and 1000 HP | raised by the rule. If that part of the fight feels too long, write 0 in their row. Not looked at in play. |
| 172 final dragon | six values; its script reads only the five part values; the main value 2000 becomes 3500 at level 50 = over the gauge limit | all raised; with the gauge cap the main value is 3400. Which value the gauge shows was not checked in play. |
| 200 Vexen, 244 Lingering Will | a second value (100 / 50). Lingering Will's second pool was seen in the test: it is hit only when the main HP is at 1 and it refills to its maximum | raised with the rest. |
| Cup opponents that name entries 193 and 194 (N_HB550_BTL2, N_HB570_BTL2) | these ids are not in the table; the game falls back to entry 69 (100), which is not a boss entry | unchanged; an oddity of the original. |
| Story fights against objects NOT typed BOSS | Seifer (135, 155), Hayner (150), Setzer (158), Vivi (157, 162) in the Struggle; Shadow Roxas (145); the Illuminator in the Barbossa fight (98); Bulky Vendor (4); the Mushroom XIII (205, 207, 210, 247-251) | **not raised.** The Struggle is a points contest, the mushrooms are counting games, the vendor loses HP by itself. If the user wants Seifer or Shadow Roxas tougher, add a row to the list. |
| Allies and escorts | Hercules (29), Megara (30), Queen Minnie (112), the gate of Hollow Bastion (146), King Mickey (147) | not raised (they are not bosses). |
| Entries shared by a story fight and a level-99 fight | Hades 18 (story and cup object), Cerberus 19 / 199, Volcano and Blizzard Lord 122 / 123 / 197 / 198, Vexen, Lexaeus, Marluxia, Larxene, Zexion (silhouette and data rematch), Roxas 213 | matters only without the gauge patch: the cap of the level-99 fight then also limits the lower fight. Which of two entries a shared object picks in which room was not resolved per room. |
| Fights where the second hero is missing or the mode is special | (other lanes) | the HP is raised on the disc in every case; a boss fought by one hero alone would be 75 % longer. To be judged with the parity work. |

## 5. Timed and special fights

Source: lane P's mission facts joined with the boss entries (`local\analysis\lane-b75\scan\boss_missions.tsv`:
113 missions hold a raised object, 63 of them have a timer, counter or gauge). Judged from the data and FROM MEMORY
of the game; **none of these was played in this lane**, so every line is a HYPOTHESIS until played.

General point: two heroes hit. If both players fight, a boss with +75 % falls in about the time the original boss
needs against one hero, so a clock that was fair stays about as fair. It gets worse than the original only when
one player is down or much weaker (up to 1.75 x the time).

| Mission | What is special | Raised entries | Does +75 % change the chance to win? | Recommendation |
|---|---|---|---|---|
| HE08_MS107 "Defeat Pete before the cave collapses!" | **90 s limit on the boss himself** | 26 Pete | **Yes, directly.** | **Smaller number: 40** (write 40 in row 26). The same entry is used in the Megara mission. |
| HE08_MS106 "Defeat the enemies while defending Megara!" | Megara's gauge falls while enemies live | 26 Pete | Yes, a longer fight gives more hits on her. | covered by the 40 above. |
| MU09_MS108 "Defeat Shan-Yu while guarding the gates!" | gate gauge; the mission fails when it is empty. VERIFIED in my test: left alone, the gate was lost after about 36 s | 71 Shan-Yu, 72 falcon | Yes, longer fight = more gate damage. | keep 75 and play it; candidate for 50. One player can guard the gate. |
| LK02_MS102 "Fight the hyenas while protecting Pumbaa and Timon!" | protect gauge | 91 hyenas (also their later fight LK05_MS201) | Yes, mildly. | keep 75; candidate for 50. |
| EH14_MS103 Luxord (and data rematch) | time gauges instead of a normal fight | 89, 243 | Unclear: if his gauge follows his HP by percent, the fight is 75 % longer while the player's time runs. | keep 75 and play it early; candidate for 40. |
| HB04_MS403 / HE17_MS105 Demyx | "defeat 10 water forms in 60 s" phases; the forms are normal enemies and are NOT raised | 88, 240 | The timed part itself is unchanged; a longer fight has more such phases. | keep 75. |
| Cups with Cerberus Cup rules: HE_COL_2_10, HE_COL_6_10 (Cerberus), Hades Paradox rounds 31-40 | a time limit for the whole cup (120-200 s, 180-200 s, 600-660 s) | 19 / 199 Cerberus and the round bosses | Yes for the boss rounds; normal rounds unchanged. | keep 75; candidate for 40 on 199 after playing. |
| Cups with Titan Cup rules (HE_COLOSSEUM_3 / _7, Hades Paradox rounds 11-20) | points are lost when hit; no clock | 178 Hercules and others | Mildly (more time to lose points). | keep 75. |
| HE_COL_4_2, 4_3, 4_6, 4_7, 4_8 (rounds of cup 4 with a clock or points) | Hades stands in the object list of every round of that cup; he is fought in round 10 only | 177 | No for these rounds (he is not the target). | keep 75. |
| HE06_MS101, HE19_MS204 Hades | the mission files hold a 180 s timer, a counter and a gauge with flags 0 | 18, 196 | FROM MEMORY there is no visible time limit; the first meeting ends by itself. | keep 75; look at it when playing. |
| EH15_MS104 Saix | his berserk gauge | 134, 253 | No clock. | keep 75. |
| TR04_MS104 Hostile Program | cluster gauge for the freeze command | 106 | No clock. | keep 75. |
| HB32_FM_VEX / HB33_FM_VEX Vexen | data gauge and counter for the clone | 200 | No clock; a longer fight makes more clones. | keep 75. |
| HB33_FM_LEX Lexaeus | power counters | 214 | No clock. | keep 75. |
| CA01_MS204 Grim Reaper (second fight) | medallion counters; he can be hurt only while all medallions are in the chest | 124 / 154 | No clock; more rounds of collecting. | keep 75. |
| EH22_MS111 final dragon | part of the long final sequence, one gauge | 172 | Longer part fights. | keep 75; belongs to the parity check of that sequence. |
| WI02_MS103 cage chase | race against a gauge | cage 79 unchanged; Pete 127 raised | No (the cage is the target). | as built. |
| NM10_MS201 Lock, Shock, Barrel / NM10_MS203 presents | boxes and counters | 15-17 | No clock in MS201; MS203 never reads HP. | keep 75. |

How to give one boss a smaller number: open `tools\lane-b75\data\boss_entries.csv`, write the number in the column
`percent` of its row (empty = the build's number, 0 = unchanged), rebuild the disc.

## 6. Tests

Method: jump disc to the fight, fresh save (battle level 1, HpMultiplier 20 %; Lingering Will has fixed level 99).
`tools\lane-b75\slots_watch.py` reads the unit slots through PINE (entry id, HP, maximum, parts).
**Test-only helpers, never part of the game:** (1) memory writes of the watcher on ONE-COPY runs (heroes' HP kept
high so a scripted run is not ended by a defeat; boss HP written low to reach the end or a phase);
(2) the patch line that gives the fresh save the Scan ability (`patches\lane-b75-test-scan`).

### HP, normal enemies, phases

| Boss | Disc / test | Result |
|---|---|---|
| Shan-Yu (early story), jump MU 75, room 0908 | control `b75-shanyu-c1`, +75 % `b75-shanyu-s1` | VERIFIED: Shan-Yu (entry 71) 260/260 -> 455/455, falcon (72) 60/60 -> 105/105 = exactly x1.75. Normal enemies (entry 61) 20/20 on both discs; the gate object (entry 109) 20/20 on both. |
| Shan-Yu, scripted HP floor | `b75-shanyu-c2`, `b75-shanyu-s5` | VERIFIED: after a test write to 44 % the script put the HP back to 129/260 on the control and 225/455 on +75 % = 49.5 % both. The floor is a percentage. |
| Shan-Yu, fight to the end | `b75-shanyu-s2` ... `s5` | NOT DONE: a button script cannot defend the gate; the gate gauge empties after about 36 s and the mission fails (on both discs alike). |
| Thresholder + Possessor (scripted phases), jump BB 72, room 0B05 | control `b75-thresh-c1`, +75 % `b75-thresh-s1` | VERIFIED: Thresholder (74) 70/70 -> 123/123, Possessor (24) 50/50 -> 88/88 (rounded up from 122.6 and 87.6). |
| Thresholder, whole fight on the +75 % disc | `b75-thresh-s2` (one copy, hero HP kept high, test writes Thresholder -> 12, Possessor -> 6) | VERIFIED: Thresholder held at 1 HP, Possessor comes out and is hit (88 -> 43), goes back in, Thresholder is refilled to 123/123, second round, Possessor to 0, then the bonus screen "GET BONUS!" (`local\tests\b75-thresh-s2-sel\sheet.png`). |
| Lingering Will (Final Mix, fixed level 99), jump DC 73, room 070C | control `b75-lw-c2`, +75 % `b75-lw-s1` | VERIFIED: 3400/3400 (second value 91) -> 5950/5950 (second value 160). The fight runs on the +75 % disc without Scan. |
| Lingering Will to the end | `b75-lw-gp3`, `b75-lw-gp6` (+75 %, gauge patch, test write to 3 HP) | NOT REACHED: his low-HP phases start ("Commands have been locked!"), HP stays at 1 and the scripted level-1 hero cannot land the last blow in 13,000 frames. Not compared with the control disc at 1 HP. |

### The gauge

| Test | Result |
|---|---|
| `b75-lw-s2`, `b75-lw-s3`: +75 % Lingering Will, Scan, no gauge patch | VERIFIED FAILURE: freeze at the start of the fight, both times. |
| `b75-lw-g3400` / `g3600` / `g3800` / `g4000` / `g4600` / `g5200` / `g5950`: control disc, Scan, test write of the maximum HP | VERIFIED: 3400 runs; every value above freezes. |
| `b75-lw-gp1`: +75 % Lingering Will, Scan, **gauge patch** | VERIFIED: runs (14 different screenshots, no fault in the emulator log); the gauge shows the long bar and 16 small bars for 5950 HP (`sheet.png`). |
| `b75-lw-gp2`: the same, test writes of the boss HP to 2975, 500, 3 | VERIFIED: half = 8 small bars and half a long bar; 500 = 1 small bar and a part; 3 = empty with a sliver (`sheet.png`). |
| `b75-lw-gp4`: control disc, gauge patch, test write of the maximum to 5950 | VERIFIED: no freeze (the same write froze without the patch). |
| `b75-lw-gp5` against `b75-lw-c3`: control disc with and without the gauge patch, same script | VERIFIED: 9 of 14 screenshots byte-identical; in the other 5 every differing pixel is in the lower HUD strip (y >= 680: the heroes' HP, which the test tool rewrites at its own pace), none in the enemy gauge (`tools\lane-b75\img_diff.py`). |

### Two linked copies

| Test | Result |
|---|---|
| `b75-thresh-sync`: +75 % Thresholder disc, random buttons on both pads, 7,600 frames | VERIFIED: 118 digests compared, never out of sync; 4 of 4 screenshot pairs identical. |
| `b75-threshbig-sync2`: test disc where Thresholder alone has 51 x HP (3570 at level 1), gauge patch + Scan line on both copies, both pads lock on and attack, 7,600 frames | VERIFIED: 118 digests, never out of sync; 7 of 7 screenshot pairs identical; the cave's data word reads 3570 on both copies; the gauge is drawn and drains (`p2_f006400.png`). |
| `b75-threshbig-sync`: the same disc with random buttons | in sync, but nobody locked on, so the gauge was not drawn; counts only as a second run of the data. |

### Failures and things seen that are not from this lane's change

- **Lingering Will jump disc without the test tool's HP help: crash at about frame 5000.** First fault pc
  `0x001AEBF0` (reads address 0), then "Jump to unaligned address", emulator paused. Seen in two linked copies with
  the gauge patch (`b75-lw-gsync`, `b75-lw-gsync2`), in two linked copies on the CONTROL disc without it
  (`b75-lw-csync`), and in ONE copy on the control disc with the plain `patches\merged-v2` (`b75-lw-c-noboost`).
  So it does not come from the boss HP or the gauge patch. HYPOTHESIS: a fresh-save hero (or the twin) is defeated
  by the level-99 boss's first hit; all runs that kept the heroes' HP high passed that point. Not looked into
  further (other lanes' ground). Log kept: `local\tests\b75-lw-gsync\p1_emulog_crash.txt`.
- Early test scripts that pressed START in a fight paused the game; a hero's defeat followed by the scripted
  Circle chose Continue and stalled (the known rule for mission jump discs). Both were mistakes of the test, fixed
  in `make_fight_script.py` and with the hero HP help.

### Not tested

- Real play on two PCs; any fight at its real level (all tests are at battle level 1 except Lingering Will).
- The cups, Sephiroth, the silhouettes and data rematches other than Lingering Will; the final dragon.
- Every timed mission of section 5.
- The gauge picture of a +75 % boss that stays under 3400 HP was not photographed on its own (the fresh test save
  has no Scan). For the gauge this is an ordinary case of the original game: it only receives HP and maximum.
- The gauge patch together with other lanes' HUD work (per-player HUD): no overlap of addresses found today, but
  not run together.
- Whether the two story flags that would lift every world to level 60 / 99 are ever set.

## 7. For the merge

1. **Data (needed in every case):** run `scale_boss_hp.py` on the original `00battle.bin` and put the result as
   `00battle.bin` in the disc build folder (the shared inject step writes it in place; file size unchanged).
   The builder `tools\lane-b75\build_disc_b75.py` shows the order: jump recipe (tests only) -> twin placement ->
   boss HP -> inject.
2. **Gauge (recommended):** append the 50 `patch=` lines of `tools\lane-b75\data\gauge_patch_lines.txt` to the game
   patch (SHA-1 of the lines file `4282e01ab916fdd3e74c852fbfd2f74cb5c5f8a9`; cave `0x000F3800`-`0x000F38AF`, word
   `0x000F3FF0`; hooks at `0x00154450`, `0x00154B98`, `0x00154C10`, two instructions each). Then build with
   `--gauge-patch`. `patches\lane-b75-gauge` is `merged-v2` plus these lines, as used in the tests.
3. **Without the gauge lines** build WITHOUT `--gauge-patch` (the default): safe, but 25 entries get less than the
   number. Never ship an uncapped battle file with a game patch that lacks the gauge lines: the level-99 fights
   would freeze.
4. If the number changes later: only step 1 is repeated (`--percent N`); the cap is recomputed by the tool.

## 8. Files

| File | What |
|---|---|
| `tools\lane-b75\scale_boss_hp.py` | THE tool: battle file with raised boss HP (one number, gauge cap or `--gauge-patch`) |
| `tools\lane-b75\data\boss_entries.csv` | the boss list (91 rows; per-row percent) |
| `tools\lane-b75\data\boss_levels.csv` | highest battle level per boss entry (for the cap), made by `fight_levels.py` |
| `tools\lane-b75\make_gauge_patch.py`, `data\gauge_patch_lines.txt` | the gauge patch lines and their generator |
| `tools\lane-b75\build_disc_b75.py` | test disc builder (jump, twins, boss HP, inject) |
| `tools\lane-b75\enmp_lib.py`, `bar.py`, `extract_ai.py`, `scan_ai2.py`, `classify.py`, `make_boss_list.py`, `boss_missions.py`, `placements.py`, `fight_levels.py`, `make_doc_tables.py` | analysis: table reader, AI script scan, list makers |
| `tools\lane-b75\slots_watch.py`, `run_gauge.sh`, `make_fight_script.py`, `img_diff.py`, `find_*.py`, `lvpm_check.py` | test and search helpers |
| `patches\lane-b75-gauge` | `merged-v2` + gauge lines (candidate) |
| `patches\lane-b75-gauge-scan`, `patches\lane-b75-test-scan` | TEST ONLY: with the Scan line for a fresh save |
| `local\analysis\lane-b75\` | dumps and scan results (`scan\ai_ids.tsv`, `scan\fight_levels.tsv`, `scan\boss_missions.tsv`, `out75cap\report.txt`, `out75full\report.txt`, 810 decoded AI scripts in `ai\`) |
| `local\tests\b75-*`, `local\variants\b75-*` | test logs, screenshots, disc recipes (the discs themselves are deleted) |
