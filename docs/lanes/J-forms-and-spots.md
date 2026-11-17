# Lane J: twin forms in the remaining worlds, the unproven spots, the old-layout entries, the special modes

Written 2026-11-10. Continues lane F ("twin in every room"). Room data only: no game-code patch of this lane.
All tests SINGLE-PC, sandbox emulator copies `local\run-j` and `local\run-j2`, scripted buttons, discs built from
the English copy build 2 with the "jump disc" method of lane B. Every test disc is deleted again; the recipes are in
`local\variants\j-*`, the screenshots and logs in `local\tests\j-*`.
Labels: **VERIFIED** (test id / file) or **HYPOTHESIS**.

## Summary

| Goal | Result |
|---|---|
| 1. Forms not yet seen | **All six work.** Halloween Town, Christmas Town, Space Paranoids, Timeless River, Atlantica, and Sora with Donald and Goofy in a normal world: the second placeholder gives a twin of the right form with its weapon. Both move on pad 1; with lane E's patch each pad moves its own hero (checked in Atlantica and Timeless River). |
| 2. The 28 unproven spots | **19 now have a better spot** in an override file (`tools\lane-j\data\overrides.csv`); 14 of them were also looked at in the game. **9 are in rooms that cannot be loaded** (no map file; the game hangs). 5 of the 19 could not be reached by a test disc and rest on the collision analysis only. |
| 3. The 6 old-layout entries | **Decoded.** al08 holds three direct placements of the Wisdom Form Sora object and one of Auron; po10 holds one PLAYER placeholder; the other three entries are trigger boxes. Both rooms have no map file and cannot be loaded, so nothing needs a twin there. |
| 4. Special modes (facts only) | 21 placements listed with mission and object. A second copy was tried in 6 of the 7 missions a test disc can reach: **no crash in any**; what appears differs per mode (table below). One mission (AL14_MS202) shows a black screen on a test disc with or without a twin, so it was not tested. |

## Goal 1: forms lane F had not tested

Method: lane F's second PLAYER placeholder in every room (`--order before`), New Game jumps to the room. Script
`tests\scripts\lane-j\j_probe.txt` (pad 1: run right at frame 5300, Cross at 5500, Circle x3 from 5700).

| World / form | Jump | Test | What the pictures show | Both move (pad 1)? | Odd things |
|---|---|---|---|---|---|
| Halloween Town costume | Type 2, NM 51 (nm00, mission NM00_MS101, Jack and Goofy present) | j-nm51 | VERIFIED: two Soras in the Halloween costume with pumpkin masks and Keyblades (clear in `p1_f005900.png`) | Yes, both run and swing (frames 5380-5900) | none |
| Christmas Town costume | Type 2, NM 53 (nm06, NM06_MS102) | j-nm53 | VERIFIED: two Soras in the Christmas costume (frames 4900-5290) | Yes | none |
| Space Paranoids (Tron suit) | Type 2, TR 54 (tr03, TR03_MS103, Tron and Goofy present) | j-tr54 | VERIFIED: two Soras in the Tron suit with Keyblades (`p1_f004900.png`) | Yes | none |
| Timeless River (old-cartoon look) | Type 2, WI 52 (wi02, WI02_MS103, Donald and Goofy present) | j-wi52 | VERIFIED: two old-cartoon Soras with Keyblades (`p1_f004900.png`) | Yes | none |
| Atlantica (swimming) | Type 1, LM area 2 entrance 0 (free swim, Sora alone) | j-lm02 | VERIFIED: two merman Soras side by side (`p1_f004700.png`) | Yes, both swim (5340-5900) | none; this placement was one of the 28 unproven ones |
| Sora in a normal world with Donald and Goofy | Type 2, HB 58 (hb09 mission, lane B's recipe) | j-hb58 | VERIFIED: two Soras, Donald and Goofy in the fight (frames 4700-4900) | Yes | none (lane B's notes on this mission still apply) |

Each pad its own hero in a changed form (lane E's patch `patches\lane-e-x2`, two linked copies, pad 1 runs right
from frame 5300, pad 2 runs away from frame 5000):

| Test | Result |
|---|---|
| j-sep-lm02 (Atlantica) | VERIFIED: at frames 5060-5100 one merman swims away while the other stays; from 5340 the camera's merman swims right alone. Session closed in sync. |
| j-sep-wi52 (Timeless River) | VERIFIED: same pattern with the two old-cartoon Soras. Session closed in sync. |

Not tested in this lane: Drive Forms, Limits, Pride Lands again (lane F did it), Roxas again (lane F did it).

## Goal 2: the 28 placements lane F could not prove

### What was wrong with the first analysis, and what lane J's analysis adds
1. **Heroes that do not stand on room ground.** In 15 placements there is no floor in the collision data under the
   player's spot. Seen in the game, three different things hide behind that: the hero stands on a platform that is
   an object (al13, eh25, eh23), the hero drops in from above (hb21: spawn at height 800, both heroes are on the floor
   at height 0 a moment later, test j-trk-hb21), or the hero swims (Atlantica). Lane J's rule for these: first the
   spots between the designer-made friend places (they are on the same unseen platform), then a spot beside the
   player with a free straight line and free space around it.
2. **Walls the game switches on and off.** In tt07 group b_44 and tt36 entrance 1 every spot failed because of
   walls that belong to switchable collision groups. VERIFIED from the data: the room's collision meshes carry a
   group number (tt07: 1-7 and 61-63; tt36: 1, 2, 20; file `local\analysis\lane-j\meshgroups.csv`), and the map
   scripts' `MapVisibility` values use exactly those bit numbers (tt07 programs differ in bits 1-7 and 60-63; the
   only tt36 program with bit 20 is 0x9F). HYPOTHESIS: collision group g is switched on by bit g of that value.
   With the groups of the program that really uses the placement, both placements get a spot beside the player.
   VERIFIED in the game for the result (tests j-trk-tt99, j-trk-tt36: twin stands on that spot); the hypothesis
   itself is not proven.
3. **A wider ring of spots** (16 directions, 5 distances) found ground spots for the two nm08 placements.

### The 28, one by one

"Seen" = looked at in a test with the override file in use (pictures, or the two player objects' positions read
through PINE with lane B's `track.py`).

| # | Room, group, placement | Lane F's reason | Lane J spot (override) | Seen? |
|---|---|---|---|---|
| 1 | al13 m_00, entrance 4 | no ground under the player | right 110, same height | VERIFIED j-look-al13: two Soras, Aladdin and Goofy on a small platform (the platform is an object, 1000 above the collision floor) |
| 2 | eh23 m_00, entrance 0 | no ground | between the two friends | VERIFIED j-look-eh23: two Soras (frames 5715, 5900) |
| 3 | eh23 b_99 (EH23_MS112) | no ground | right 110 | VERIFIED j-look-eh73: two Soras side by side with Riku |
| 4 | eh23 b_97 (program 0x51) | no ground | right 110 | VERIFIED j-trk-eh81: two player objects 120 apart, followed for 12 s |
| 5 | eh25 b_40 (EH25_MS109) | no ground | between the two friends | VERIFIED j-look-eh70: two Soras with Riku and Goofy |
| 6 | hb21 m_00, entrance 0 (Cavern of Remembrance: Depths) | no ground | between the player and a friend | VERIFIED j-trk-hb21: two player objects on the floor, 80 apart, both walk. (The first try, j-look-hb21, used a spot on the friends' line at the player's height and showed only one Sora in the pictures: that spot is not used.) |
| 7-15 | hb28, hb29, hb30, hb31, hb35, hb36, hb37, hb39, hb40 (m_00) | no map file | none | **Rooms cannot be loaded.** VERIFIED: 320-byte room files with one program and one placement, no map file on the disc, no room script jumps to them; a jump to hb28 hangs the game (j-look-hb28: frames stop, emulator killed after 400 s). HYPOTHESIS for the other eight (same data, not each tried) |
| 16 | lm00 m_00, entrance 0 | no ground (swimming) | right 110 | VERIFIED j-trk-lm00: two player objects side by side, both swim |
| 17 | lm02 m_00, entrance 0 | no ground (swimming) | right 110 | VERIFIED j-lm02, j-sep-lm02 |
| 18 | lm02 b_40 (LM02_MS101) | no ground (swimming) | behind left 110 | VERIFIED j-trk-lm52: two player objects about 120 apart |
| 19 | lm02 e_50, entrance 50 | no ground (swimming) | behind 80 | not seen (event entrance; analysis only) |
| 20 | lm02 e_50, entrance 20 | no ground (swimming) | right 110 | not seen (event entrance; analysis only) |
| 21 | lm03 m_00, entrance 0 | no ground (swimming) | right 110 | VERIFIED j-trk-lm03 |
| 22 | lm04 m_00, entrance 0 | no ground (swimming) | right 110 | VERIFIED j-trk-lm04 |
| 23 | mu08 b_61 (MU08_MS204, Storm Rider) | no ground | right 110, same height | VERIFIED j-trk-mu79: both objects ride at height 1300-1650, both come down to the ground, both walk; shared HP 20 -> 14 |
| 24 | nm08 e_50, entrance 51 | no spot passed | ahead right 80 | not seen: a jump to this entrance on a fresh save shows the room without any hero (j-trk-nm8a). Analysis only |
| 25 | nm08 e_50, entrance 54 | no spot passed | behind right 110 | not seen (j-trk-nm8b, same). Analysis only |
| 26 | tr08 m_00, entrance 2 (Central Computer Mesa) | no ground | between the two friends | not seen: the jump shows a fixed camera on the tower and no hero (j-look-tr08). Analysis only |
| 27 | tt07 b_44 (TT07_MS105, lock-on lesson) | no spot passed (switchable walls) | right 110 | VERIFIED j-trk-tt99: two Roxas side by side in every picture, two player objects 120 apart. (With lane F's guess the twin stood in line with the camera and hid the hero: j-look-tt99.) |
| 28 | tt36 m_00, entrance 1 (Tunnelway) | no spot passed (switchable walls) | right 110 | VERIFIED j-trk-tt36: two player objects side by side, both walk. (Lane F's guess also worked but hid one hero from the camera: j-look-tt36.) |

Count: 19 with an override (14 seen, 5 analysis only: #19, 20, 24, 25, 26), 9 in rooms that cannot be loaded.

### The override file
- File: **`tools\lane-j\data\overrides.csv`** (19 lines; made by `tools\lane-j\make_overrides.py` from the analysis
  result `local\analysis\lane-j\study.csv` plus the two hand-checked lines in `tools\lane-j\data\manual_overrides.csv`).
- Format: `room,group,spawnpoint,spawn_type,spawn_arg,player_x,player_y,player_z,twin_x,twin_y,twin_z,status,note`.
  The first eight columns are the same as in the placement report and identify one placement.
- Read by lane J's copy of the tool (`tools\lane-j\LaneJ`, built to `local\build\lane-j`): `twin-all` takes it as
  a last argument; `tools\lane-j\build_disc.py <name> --override tools\lane-j\data\overrides.csv`.
  `tools\lane-f` is not changed.
- VERIFIED: with the override file, lane J's tool writes room files byte-identical to lane F's kept result in 271
  of 284 rooms; the 13 that differ are exactly the rooms with an override (al13, eh23, eh25, hb21, lm00, lm02, lm03,
  lm04, mu08, nm08, tr08, tt07, tt36). Report: `local\variants\j-final-check\report.csv` (1,222 proven by lane F's
  rule, 19 overrides, 9 in rooms that cannot be loaded).
- Status words in the file are the analysis result ("proven-ground", "proven-drop", "proven-free-space",
  "proven-designer-spot", "proven-ground-with-switched-walls"). "proven-drop" only means "free line, free space and a
  floor further below"; what really happens there (platform, drop or swimming) is in the table above.

### Still needs a human look
- The five analysis-only placements: lm02 entrances 50 and 20, nm08 entrances 51 and 54, tr08 entrance 2. They need
  the real story state (an event or a save), which a jump disc does not give.
- The hypothesis "collision group g = bit g of MapVisibility". If it holds, lane F's ground check could use it for
  every room (today it treats every switchable wall as always there, which only makes it stricter).

## Goal 3: the six spawn entries in the older layout (rooms al08, po10)

VERIFIED by decoding the bytes (`tools\lane-j\old_layout.py`, output `local\analysis\lane-j\old_layout.txt`; every
file parses to its last byte):

| Entry | Size | What it is |
|---|---|---|
| al08 m_00 | 808 | three blocks, each with ONE placement of object 0x0056 (P_EX100_MAGF, Wisdom Form Sora, a PLAYER-type object placed directly), at (-3000, -200, -3400), (0, -11500, 4300), (-3800, -200, -3800) |
| al08 m_20 | 272 | one placement of object 0x0065 (P_HE000, a FRIEND-type object: Auron) at (-3000, -200, -3400) |
| al08 m_10, m_11 | 92 each | two boxes each (position, size, rotation): exits or triggers, no objects |
| po10 m_00 | 272 | one placement of the PLAYER placeholder 0x0236 at (-2350, -38.8, -30) |
| po10 m_10 | 92 | two boxes, no objects |

Layout: a placement list is `count`, then per block a 12-byte header and 0x100-byte records (object id, x, y, z,
rotation, then flags); a box list is `count`, then 44 bytes per box.

Do they matter? No. VERIFIED: neither room has a map file, their scripts only have program 0 (po10 also 0x1A), no
room script jumps to them, and a jump to either hangs the game like hb28 (j-look-al08, j-look-po10: no frame after
the jump, emulator killed after 150 s). HYPOTHESIS: leftovers from development. No twin is needed and the tool
rightly leaves them untouched.

## Goal 4: the 21 special-mode placements (facts only, no design)

VERIFIED from the room data (`local\analysis\lane-j\special_modes.txt`):

| Room | Object placed directly | Groups (placements) | Mission(s) and party setting |
|---|---|---|---|
| po06 A Windsday Tale | 0x035B PO06_PLAYER | b_40 (1); m_00 (1) | b_40: PO06_MS100. m_00: PO06_MS101, PO06_MS101_FREE. No party line |
| nm10 Toy Factory: The Wrapping Room | 0x03C8 F_NM180 (the toy cannon) | m_50 (1) | map programs 0x3F, 0x46, 0x48; missions NM10_MS203 and NM10_MS203_FREE (W_FRIEND) |
| al05 Above Agrabah | 0x04FF P_EX100_AL_CARPET | b_60 (1) | AL05_MS203 (W_FRIEND) |
| al14 Sandswept Ruins | 0x04FF P_EX100_AL_CARPET | m_00 (2, entrances 0 and 1); b_61, b_64, b_67, b_68, b_69 (1 each); e_50 .. e_55 (1 each): 13 in all | b_61 AL14_MS201A, b_64 AL14_MS201B, b_67/b_68/b_69 AL14_MS_P (all W_FRIEND); the e_ groups are event entrances 50-55 |
| al14 Sandswept Ruins | 0x05E9 AL14_PLAYER | b_70 (1) | AL14_MS202 and AL14_MS202_FREE (W_FRIEND) |
| tr02 Game Grid | 0x05F5 P_EX100_TR_LIGHTCYCLE | b_99 (1); b_97 (1) | b_99: TR02_MS102A (NO_FRIEND, and W_FRIEND_FIX in program 0x49). b_97: TR02_MS102B, TR02_MS102_FREE |
| eh22 | 0x0840 P_EX100_SIDECAR | b_40 (1) | EH22_MS111 and TEST_EH22_MS111 (NO_FRIEND) |

2 + 1 + 1 + 13 + 1 + 2 + 1 = 21. None of these groups also holds a PLAYER placeholder.

What happens with a second copy of the special object beside the first (the tool's `--also <object>` option, one
room at a time; pad 1 drives everything; about 30 s of play each):

| Test | Mission reached | What appears | Crash? |
|---|---|---|---|
| j-sp-po54 (PO 54) | PO06_MS100 | VERIFIED: two flying Soras side by side; both fly on together; a swing is seen at frame 5715 | no |
| j-sp-nm63 (NM 63) | NM10_MS203 (Gift Wrapping) | VERIFIED: a second cannon stands to the right of the first; the game counts down and runs. Whether the second cannon fires was not checked | no |
| j-sp-al62 (AL 62) | AL05_MS203 (fight above Agrabah) | VERIFIED: a second Sora, but only ONE carpet in the picture; the second Sora moves in the air without a carpet of his own and drifts away from the first (gone from the picture by frame 6100) | no |
| j-sp-al86 (AL 86) | AL14_MS201A | VERIFIED: same as above: two Soras, one carpet; enemies are fought and defeated | no |
| j-sp-tr61 (TR 61) | TR02_MS102A (Light Cycle) | VERIFIED: two light cycles with riders side by side after the instruction screen | no |
| j-sp-eh72 (EH 72) | EH22_MS111 | VERIFIED: a second Sora near the first, without a vehicle of his own (frames 4800-5380), not in the later pictures | no |
| j-sp-al106 (AL 106) | AL14_MS202 | NOT TESTED: the screen stays black and the game draws nothing, with the twin and also without it (control j-ctl-al106). A jump disc cannot start this mission |

Not tried: the other placements of the same objects (po06 m_00, tr02 b_97, the other al14 groups), and what each
second object does on its own controller. Each of the 21 is a decision for the user later.

## Tools and files of this lane

- `tools\lane-j\LaneJ\` (copy of lane F's tool plus: override file for `twin-all`; `study` = the closer analysis of
  unproven placements; `why` = why each spot fails for one placement; `spotmask` = one placement under one
  MapVisibility value; `meshgroups` = switch numbers of every room's collision meshes; `rawspawn` = dump spawn
  entries that are not in the usual layout). Built to `local\build\lane-j`.
- `tools\lane-j\build_disc.py` (jump recipe + twins + overrides + extra room files in one command),
  `run_form.py` (build, run, contact sheet, delete the disc), `track_run.py` (same with the player objects'
  positions read through PINE), `batch.py` (a list of such tests), `make_overrides.py`, `old_layout.py`.
- Data: `tools\lane-j\data\overrides.csv`, `manual_overrides.csv`.
- Analysis output: `local\analysis\lane-j\` (study.csv, study-noswitch.csv, meshgroups.csv, old_layout.txt,
  special_modes.txt, oldspawn\*.bin).
- Scripts: `tests\scripts\lane-j\`. Test folders `local\tests\j-*` (39). Recipes `local\variants\j-*` (the built room
  files were deleted except in `j-final-check`; every recipe rebuilds with one command).
- Emulator copies `local\run-j` (port 29150, PINE 28091) and `local\run-j2` (port 29170, PINE 28092; a second set
  so two batches could run at once). No test disc of this lane is left in `local\iso`. No emulator left running.
- Nothing outside lane J's folders and this document was written; `tools\lane-f`, the shared tools, STATE.md, the
  plan and the memory folder are untouched. No commits.

How to repeat one test, for example Halloween Town:
```
python -I tools\lane-j\run_form.py nm51 tests\scripts\lane-j\j_probe.txt 6100 4500,4900,5290,5715,5900 -- --jump "NM 51" --override tools\lane-j\data\overrides.csv
```

## Open points

1. Five placements rest on analysis only (see "Still needs a human look").
2. The collision-group hypothesis is supported by two rooms' data and two game tests, not proven in general.
3. Special modes: a second vehicle exists only for the light cycle and the cannon; for the carpet, the glider and
   PO06_PLAYER the second hero has no vehicle or shares the picture oddly. Nothing was designed here.
4. A jump disc gives a fresh level-1 save. Story-state placements (event entrances, later visits) were not seen.
5. Placement always puts both heroes at the entrance. Twins in minigames and one-on-one fights are still added
   everywhere by default (lane F's open point 4).
