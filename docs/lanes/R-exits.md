# Lane R: exits and story triggers for two heroes ("at the exit together"), the waiting sign

Written 2026-11-10. Game program CRC F266B00B. Base: merged build v2 (`patches\merged-v2`).
All tests SINGLE-PC, sandbox emulator copies `local\run-r` (port 29550, PINE 28131), two linked copies, scripted or
random buttons, no humans. Every run below ended "never out of sync".
Labels: VERIFIED (test id / address / how) or HYPOTHESIS. Test folders: `local\tests\r-*`.

## Result per problem

| Problem | Result |
|---|---|
| 1. Narrow doors | **DONE.** New rule: one hero in the exit's jump volume, the other in the same volume OR within 300 units of the first. The narrow Borough door that failed in the merged build now works without a sidestep. |
| 2. Waiting sign | **DONE.** "Waiting for the other player." in the game's own wall-message window, for exits and story triggers, for either hero. The text is in the patch; no disc change. |
| 3. Other triggers | **DONE for story triggers (one tested); the other kinds are listed with a recommendation.** Extra: an option that lets enemy spawn zones react to either hero (tested, off by default). |
| 4. Arrival | **DONE for the doors tested.** No bounce back in three door pairs; both heroes arrive clear of the door. Doors that need no walking-in (29 in the game) are not tested. |
| 5. Lane E's open point | **DECIDED and built:** the second offer stays (either hero may be the one in the door), but the room jump and the event start now always run with player 1's hero as the engine's player. |

Delivered patch: **`patches\lane-r-x3\SLPM-66675_F266B00B.pnach`** (698 lines, SHA-1
1af004465a86c9ac9aeb72282d911ac8b89274b6) with `listing.txt`, made by `python -I tools\lane-r\make_r.py`.
It is merged-v2 with lane E's section "exits" taken out and this lane's section "exits-r" put in; the generator
checks that all 470 other words of merged-v2 are unchanged.
Variants of the same generator: `patches\lane-r-x3-spawn` (`--either-spawn`, see problem 3),
`patches\lane-r-x3-nowalk` (`--no-either-walk`, control for test r-05c).

## The rule

For the engine's area events of kind 1 (room exit) and kind 3 (start an event):

1. **Both at the exit.** A room exit's JUMP volume and an event trigger count as entered when one hero is inside
   AND the other hero is inside the same volume OR within **300 game units** (3-D distance) of the first.
2. **Either hero may be the one inside** (lane E's second offer, kept).
3. **Either hero may walk in.** 421 of the 450 jump volumes belong to doors that want the hero to walk into
   them. Once both heroes are at the exit, that question is asked for the hero in the volume first and, if the
   answer is no, for the other hero. So the one standing in the doorway leaves as soon as the other runs up.
4. **Approach volumes are untouched.** A door's second, bigger volume only shows the destination's name (or the
   game's own "cannot go" message). It works for each hero alone, as in the one-player game.
5. **The jump and the event start run with player 1's hero as the engine's player**, whoever triggered them.
6. **The sign.** While one hero is in a usable jump volume or event trigger and the other is too far, the game's
   wall-message window shows "Waiting for the other player.". It is not shown for a door the game would ignore
   anyway (forced battle) or one the story keeps closed (the game shows its own message there).
7. No twin in the room: nothing changes.

### Why 300 units (from the room data, `tools\lane-r\survey.py`, output `local\analysis\r\survey.txt`)

VERIFIED from all 289 room files (6,572 trigger volumes; boxes are rotated, the first size is the depth through
the door):
- 450 jump volumes. Depth: 100 for a third of them, 200 at the median, 300 at the 95th percentile. Width: 15 are
  150 or less, 74 are 200 or less, 147 are 300 or less; median 500.
- 451 approach volumes (the game's own idea of "near this door"): smaller side 400 at the 5th percentile, 700 at
  the median.
- The twin is placed 71-110 units from the hero (lane F); the heroes push each other when they collide.
So with "both inside the same volume" two heroes cannot both fit in a third of the doors, front to back.
**300** = the 95th percentile of the jump volume's depth = about three times the twin's placement offset = less
than what the game itself treats as "near the door" for 95 % of the doors. In play it is about 0.6 s of running.
The value is one option of the generator (`--dist N`).

## How it works (all addresses for CRC F266B00B)

Found by decompiling (lane E's files plus `local\analysis\r\msg1.txt`, `msg2.txt`) and disassembly
(`tools\lane-r\dis.py`):

| Thing | Address | What |
|---|---|---|
| Door handler | 0x0019A480 | volume option = u16 at (volume+0x6C)+2: 0 = jump volume, 1 / 2 = approach volume. Door type = byte at data+0x1E: 0 = standing inside is enough, 1 / 2 = must walk in. |
| "Walking into this door?" | 0x001DB198 (call at 0x0019A57C) | a pure query on the engine's player (0x001DB200, 0x001DB250) |
| Room jump | 0x0019A610 (call at 0x0019A590) | writes the destination to 0x0032BB00 and asks for the room change |
| Approach handler | 0x0019A6C0 | if the engine's player faces the door: shows the destination's name (0x0015B1B0), or, if the story keeps the door closed, the wall message |
| "Door closed by the story?" | 0x00196768(world, room) | non-zero = closed |
| Battle mode | 0x001917B0 (word 0x01C61958) | 2 = forced battle: doors that must be walked into are ignored |
| **Wall-message window** | 0x0015B268(f12 = time, a0 = text) | the game's own call is at 0x0019A7F4 with time = the float at 0x0036D340 (6.0). Window object pointer 0x0034AA9C, "open" counter 0x0034AA98. Calling it every frame keeps it open; it closes by itself. |
| Text | any pointer to encoded text | the sign's 30 bytes sit in the patch (0x000F3360); encoded with `local\build\lane-r\LaneR.dll msg-encode` (OpenKH's international table) |

### Hook sites

| Address | Original | Now | Purpose | Compared with merged-v2 |
|---|---|---|---|---|
| 0x0019A168 | `jalr v0` | `jal 0x000F3000` (r_inside) | volume test: the rule above, and the sign | same word as lane E's hook, new target |
| 0x00182D04 | `jal 0x00182980` | `jal 0x000F327C` (r_offer) | second offer with the twin as the offered hero (lane E's routine, text unchanged) | same word as lane E's hook, new target |
| 0x0019A57C | `jal 0x001DB198` | `jal 0x000F31E4` (r_walk) | "walking in?" may be answered by either hero | **new hook** |
| 0x0019A590 | `jal 0x0019A610` | `jal 0x000F3258` (r_jump) | the jump runs with player 1's hero as the engine's player | **new hook** |

Cave: 0x000F3000-0x000F337F (224 words): r_inside 0x000F3000, r_sign 0x000F3140, r_walk 0x000F31E4,
r_jump 0x000F3258, r_offer 0x000F327C, distance constant 0x000F335C, sign text 0x000F3360.
Lane E's exit routines at 0x000F0420-0x000F058B are no longer written (that memory is free again).
Variables used (lane E's, same meaning): twin pointer 0x000F05CC (read only), second-offer flag 0x000F05D0,
player 1's hero during the second offer 0x000F05D4.

### The engine's player during the second offer (problem 5)

Lane E's x2 pointed the engine's player (0x0034E948) at the twin for the whole second offer, including a room
jump or an event start. Its x1 avoided that but then only player 1 could be the one in the door, which is exactly
what fails when player 2 stands in a narrow doorway. This lane keeps the second offer and narrows the swap:
- the twin is the engine's player only for the queries of the second offer (inside tests, walking-in, the
  destination-name display);
- `r_jump` puts player 1's hero back before the room jump starts; `r_inside` does the same before an event starts;
- the walking-in query for "the other hero" swaps and restores around that one call.
VERIFIED (r-10-gsample): with the twin standing alone in a door volume, 38,902 fast samples over 9 s show the
twin as engine player in 245 (0.63 %), never more than 2 samples in a row. So the pointer is never left on the
twin; a probe can still catch the instant (two probes of this lane show "Pt" for the twin for that reason).

## Tests

| ID | Disc | What | Result |
|---|---|---|---|
| r-01-p1alone | test-m-roam | P1 walks into Merlin's west door alone (twin 430 units away) and stays | VERIFIED: no room change; **sign shown** from the moment P1 is in the jump volume (`sheet.png`); 84 digests |
| r-02-narrow | test-m-roam | P2 into the door alone; P1 follows; in the Borough both walk straight back (lane M's failing case); out again | VERIFIED: P2 alone = no change + **sign** (`p1_f004890.png`); both = change; **the narrow door back (100 x 180) works without a sidestep**; three room changes; after each arrival both stand 300-450 frames without bouncing back; 115 digests |
| r-03-event (+ r-x-ttev1) | kh2-coop-v1 (real New Game, two Roxas) | story trigger of the first town (room tt07, group a10_, kind 3, cylinder radius 450): P1 runs in alone; P2 joins later | VERIFIED: P1 inside (403 from the centre) for 370 frames: **no event, sign shown**; when P2 is 293 units from P1 **the event starts** (the game's tutorial box) and the sign goes; 118 digests |
| r-04-hb9-market | test-r-hb9e0 | Borough -> next area (room 0A04) and back, twice | VERIFIED: change when P2 is in the door and P1 near (second offer path); back and forth again with both walking; no bounce after arrival; 114 digests |
| r-05-eitherwalk | test-m-roam | P1 stands still in the door volume; P2 runs up but stops outside it | VERIFIED: room changes while P2 is still on the way (either hero may walk in) |
| r-05c-nowalk | test-m-roam, variant without rule 3 | same buttons | VERIFIED control: P2 ends 279 units from P1, **no room change, no sign** (both at the exit, nobody walking into it) |
| r-06-hb9-bailey | test-r-hb9e1 | Borough's other door -> room 0804 and back, twice; P1 first alone in the door (twin 787 away) | VERIFIED: alone = no change + **sign** (`p1_f005080.png`); change when P2 comes back; round trip twice; no bounce; 114 digests |
| r-08-solo-patch / -nopatch | test-r-solo (no twin) | one player: out of the west door, then idle | VERIFIED: 5 of 5 screenshots byte-identical with and without the patch; the room changes as in the stock game |
| r-09-sync-roam | test-m-roam | scripted round trip, then random buttons on both pads, 34,000 frames | VERIFIED: **never out of sync, 531 digests**, 8 of 8 screenshot pairs identical; three room changes, then a fight in the Borough |
| r-10-gsample | test-m-roam | see "engine's player" above | VERIFIED transient |
| r-11-spawn-x3 / -x3-spawn | test-r-hb9e2 | P2 walks alone into an enemy spawn zone, P1 stays outside | default patch: no enemies, battle flag 0. With `--either-spawn`: **enemies spawn** (battle flag 1; they then attack player 1's hero, HP 20 -> 16, the known targeting gap); both in sync, 84 digests |
| r-12-cave-newgame, r-12-cave-solo | NO patch | real New Game with two Roxas, 9,000 frames, 6 checkpoints; one player with a door and fights, 12,000 frames, 5 checkpoints | VERIFIED: 0x000F3000-0x000F37FF all zero every time; the only 4 KB blocks with data in 0x00080000-0x000FFFFF are 0x81000-0x93000 and 0x95000 (same as lanes E and M) |
| r-12-cave-patched | test-m-roam, patch on | round trip, random buttons, 16,000 frames, 6 checkpoints | VERIFIED: 0 of 512 cave words differ from the patch file; 249 digests |
| r-07-atlantica | test-r-lm2e1 | meant as a door test in the swimming form | NOT A TEST: a "Type 1" jump to Atlantica room 2 entrance 1 gives a picture without characters. Dropped. |
| r-x-ttdirs, r-x-ttwest | kh2-coop-v1 | navigation trials | Holding a diagonal stick makes the hero run in a circle (the camera turns); the west exit of the first town was not reached. |

Doors covered: Merlin's house west door (jump volume 100 x 150), Borough -> Merlin's house (100 x 180),
Borough -> room 0A04 and its door back (100 x 1000 each), Borough -> room 0804 and its door back (100 x 800).
Six doors in four rooms, two of them narrow, all in Hollow Bastion; plus one story trigger in Twilight Town.

## Problem 3: the other trigger kinds (VERIFIED from the room data, `local\analysis\r\kinds.txt`, and the code)

| Kind | In the data | What the code does | Follows | Recommendation |
|---|---|---|---|---|
| 1 | 450 jump + 458 approach volumes, 213 rooms | room exit | both heroes (this lane) | done |
| 3 | 147 volumes, 62 rooms | start an event (0x0019AF98) | both heroes (this lane) | done; test more kinds of event (cutscene, boss) in play |
| 2 | 1,841 volumes, 139 rooms; the entities are enemies | spawn the group when the hero enters the zone (0x0019A808) | player 1 only | **Either hero.** Built as an option and tested (r-11): when player 1's hero is not inside, the twin's position is tested on the same offer (no second offer, so the spawn timers do not run twice). Switch it on together with lane H's work: until enemies choose between the heroes, an ambush set off by player 2 attacks player 1. |
| 6 | 2,709 small volumes (median 85 units), 101 rooms; the entities are townspeople and helper stand-ins (RTN) | makes those characters react when the hero is close (0x0019B500) | player 1 only | Either hero later, low priority. HYPOTHESIS that it is only "notice the hero"; the Talk command itself was not examined. |
| 10 | 69 volumes in 10 rooms (tt04-tt07, tt09, tt37, al00, hb09, nm09, he15) | writes a zone number into the engine's player (object+0xB4C) | player 1 only | **Per hero**, when the skateboard is done: these are the skateboard rooms (HYPOTHESIS that the number is for that). The twin's number is never set today. |
| 4 | 113 volumes, 27 rooms | loops over a list of objects itself and gives each a zone number (0x0019B180) | not the hero in particular | leave |
| 8 | 42 volumes, 1 room (eh17) | switches map parts on and off (0x0019B5D8) | player 1 only | **Stay with the hero the picture follows** (player 1 on the shared screen; per view with own screens): it is about what is drawn. |
| 7, 9 | 64 + 21 volumes, 1 room (tr02, the Light Cycle room) | special to that room (0x0019B4D0, 0x0019B668) | player 1 only | decide with the Light Cycle work |
| 5 | 25 spawn points, none with a volume | never offered | - | nothing to do |

## Problem 4: arrival

VERIFIED in three door pairs (r-02, r-04, r-06): after every room change both heroes stand where they were
placed for 300-450 frames with no room change, and walking on works. Why it holds: the game's arrival spots are
outside the jump volumes, lane F / J place the twin outside trigger volumes, and 421 of 450 jump volumes need a
hero to walk into them.
Not tested: the 29 jump volumes that need no walking-in (for example Atlantica's). There the new rule fires as
soon as one hero is inside and the other within 300 units, which is the rule, but nobody has looked at an
arrival next to such a door.

## Open problems and notes for the merge

1. **Not tested in play:** a door the story keeps closed, and a door during a forced battle. The sign's two
   conditions copy the game's own code at 0x0019A4C0-0x0019A530 (HYPOTHESIS that they behave the same).
2. **One story trigger tested**, and it opens a tutorial box, not a cutscene or a boss fight. Boss rooms are
   entered through ordinary exits, so the exit rule covers them; not tested as such.
3. **All six doors are in Hollow Bastion**, all with Sora. Other worlds, other forms, a door of type 0: not tested.
4. **The sign and the destination label can show together** (the label "???" sits under the sign when the hero
   also faces the door). The sign appears only in the jump volume or the trigger, not in the approach volume.
5. **The sign's text is encoded for the English build's letter table** and lives in the patch. If the text table
   of the disc changes, encode it again (`LaneR.dll msg-encode "..."`, then `make_r.py --text-hex`).
6. **Either hero may walk in** makes a door fire when the hero in the doorway stands still and the other runs
   toward the door from up to 300 units away. That is intended; a human test should confirm it feels right.
7. **New hook words 0x0019A57C and 0x0019A590** inside the door handler: no other section of merged-v2 uses them
   (the generator stops on a clash). Lanes H and N were running in parallel and are not checked against.
8. **`--either-spawn`** is off in the delivered patch (see kind 2 above).
9. The second offer runs the area-event code twice per frame for exits and event triggers only; no change of
   pace was seen (r-09 held full speed).
10. Variables rely on zero memory at boot, as in merged-v2. This lane adds no variable of its own.
11. Probe note: `tools\merge\mprobe.py` can show the twin as engine player ("Pt") when it reads in the middle of
    the second offer. It is not a fault (r-10-gsample).
12. Not tested: LAN / internet, humans, Drive Forms, cutscene skipping by both players.

## How to repeat

```
python -I tools\kh2_session.py make 2 --run-dir run-r
python -I tools\lane-r\make_r.py                               -> patches\lane-r-x3
python -I tools\lane-r\make_r.py patches\lane-r-x3-spawn --either-spawn
bash tools/lane-r/rrun.sh r-02-narrow test-m-roam.iso 7400 2 "4600,4890,5150,5590,5680,5760,5900,6450,6600,6700,7000,7300" 2 tests/scripts/merge/sync_roam_p1.txt tests/scripts/merge/sync_roam_p2.txt idle default
python -I tools\merge\psum.py local\tests\r-02-narrow          (one line per probe: room, positions, roles)
python -I tools\lane-r\build_disc_r.py hb9e1 --jump1 "HB 9 1" --overlay local\variants\r-overlay-roam   (test disc in front of a door)
```

## Files of this lane

- `tools\lane-r\`: `make_r.py` (patch generator, imports `tools\merge\make_all.py` without editing it),
  `survey.py` (trigger volumes), `kinds.py` (area-event kinds), `dis.py` (disassembly), `gsample.py`,
  `cave_r.py`, `rrun.sh` (test runner, copy of the merge lane's), `build_disc_r.py` (copy of lane J's, base =
  English build 3), `gh.sh` + `ghidra\LaneRDump.java` (project copy `local\ghidra-r`), `LaneR\` (text encoder,
  built to `local\build\lane-r`).
- Button scripts `tests\scripts\lane-r\`. Analysis output `local\analysis\r\`.
- Patches `patches\lane-r-x3` (delivered), `lane-r-x3-spawn`, `lane-r-x3-nowalk`.
- Test discs: all deleted (`test-r-hb9e0`, `-hb9e1`, `-hb9e2`, `-solo`, `-lm2e1`); recipes in
  `local\variants\r-*`, rebuild with `build_disc_r.py`. Emulator copies `local\run-r` are left in place.
- Not edited: other lanes' folders and patches, the shared tools, `docs\STATE.md`, the plan, the requirement and
  checklist files, the memory folder. No emulator of this lane is running.
