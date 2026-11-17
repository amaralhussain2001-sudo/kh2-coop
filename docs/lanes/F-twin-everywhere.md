# Lane F: the twin in every room and every player form

Written 2026-11-10. All tests SINGLE-PC, sandbox emulator copies `local\run-f`, scripted or random buttons.
Base disc: English-text copy build 2 (SHA-1 de0ed50c...). Labels: VERIFIED (test id / file) or HYPOTHESIS.

## Result

**WORKS, with data only (no game code changed, no patch, no hook site).**

- A second PLAYER placeholder (object 0x0236) in a spawn group makes the game build a second player character
  **of whatever form is current**: Roxas, Sora, lion Sora. VERIFIED (f-e1-2placeholders, f-ca-fight2, f-lk-02).
- The tool `tools\lane-f\LaneF` adds that second placeholder beside every placeholder of every room, at a spot
  checked against the room's own collision data. One command builds a disc.
- Kept disc: **`local\iso\test-f-twin-everywhere.iso`**, SHA-1 `fade6744fffbdf607c1a143a6b6c1326906147bc`
  (normal New Game start; built twice, byte-identical).
- With lane A's pad patch on top, two linked copies stay in sync, each controller drives its own hero, and both
  heroes are there after every room change. VERIFIED (f-roam-pad2b, f-final-sync3).

## Numbers (file `local\variants\f-twin-everywhere\report.csv`, one line per placement)

| What | Count |
|---|---|
| Room files read / changed | 289 / 284 |
| Twin placements made | 1,250 (1,249 placeholders + 1 real Sora object, see below) |
| Spot proven by the room's collision data | 1,222 |
| Spot NOT proven ("unchecked") | 28 in 22 rooms |
| Twin distance from the player | 71 to 110 units, median 110 |
| Chosen spot | right 979, left 130, ahead right 45, ahead left 12, ahead 5, between the two friends 20, between player and a friend 19, behind right 8, behind 4 (the 28 unchecked use the best guess) |

Unchecked placements (the twin could stand badly there; needs eyes on it):
- 9: no map file for the room (hb28, hb29, hb30, hb31, hb35, hb36, hb37, hb39, hb40).
- 15: no ground found under the player's own spot (al13, eh23 x3, eh25, hb21, lm00, lm02 x4, lm03, lm04, mu08, tr08).
  The four Atlantica rooms are swimming rooms, so that is expected there.
- 4: ground found but no spot passed (nm08 x2, tt07 group b_44, tt36).

**Not handled (listed so nothing is silently missing):**
- 21 placements of special-mode player objects placed directly by room data, in 6 rooms: carpet (al05, al14: 14),
  AL14_PLAYER (al14: 1), light cycle (tr02: 2), PO06_PLAYER (po06: 2), sidecar (eh22: 1), F_NM180 (nm10: 1).
  These are minigame / vehicle modes: a Phase 3 decision each.
- 6 spawn entries in an older data layout, left untouched: al08 (m_00, m_10, m_11, m_20), po10 (m_00, m_10).
  po10 m_00 contains a player placeholder. HYPOTHESIS: both rooms are leftovers (no in-game room name).
- 5 rooms have no placeholder at all (al08, al14, es01, po10, wm00; from lane C).

## How it works

### The fact it rests on
The PLAYER placeholder is resolved by the game to the current player object (the party table picks it per world
and story state). Every placeholder that is spawned makes its own player object. The stock data never has two in
play at once, so the stock game always has one.
- FRIEND placeholders (0x0237, 0x0238) work the same way: in the Pride Lands test they became bird Donald and
  turtle Goofy; under `Party NO_FRIEND` they make nothing. VERIFIED (f-lk-02, f-all-tt07).
- A real player object placed directly is used as it is, without the world's costume: nm07 program 0x47 (group
  b_99, lane C's lead) shows Sora in his normal clothes in Christmas Town, and he is the engine's player (camera,
  HUD, commands). VERIFIED (f-nm07-b99). The tool gives this one placement a twin of the same object
  (option `--also 54`, on by default). VERIFIED (f-nm07-b99-twin: two Soras).

### Placement rule (deterministic)
For each placeholder the tool tries spots in this order and takes the first that passes every check:
right 110, left 110, ahead-right 110, ahead-left 110, between the two friend placeholders, between the player and
a friend, then ahead / behind-right / behind-left / behind at 110, then the same ring at 80.
Checks:
1. at least 60 units from the player and from the friends' spots;
2. not inside a trigger zone (exit, event) that the player's own spot is outside of;
3. not within 50 units of any other placed thing in the room file (people, chests, props, enemies);
4. ground under the spot, reachable from the player's spot without a step of more than 45 units per sixth of the
   way, total height difference at most 120, no wall between the two spots at two heights, and 40 units of free
   ground around the spot. Ground and walls come from the room's collision data (`map\jp\<room>.map`).
The twin copies the player's record (type, entrance number, all other fields) with a new serial number that is
not used anywhere else in that room file. The bytes are spliced in directly; nothing else in the spawn data is
re-written.

Facing: a placeholder with rotation RotY faces (sin RotY, 0, -cos RotY). VERIFIED by data (the friends' centre
lies on the opposite side in 884 of 940 placements, `LaneF stats`) and by sight (f-final-start: "left/right" puts
the twin beside the player; a spot on the friends' side hid the player from the camera in f-all-tt07).

## Creation order (for lane E)

- **Build order = record order inside the spawn group.** VERIFIED: with the twin's record AFTER the player's
  (f-roam-rt2 .. rt5) the hero on the stock spot is the lower-address object (0x01A7C1E0) and does NOT trigger the
  door; with the twin's record BEFORE the player's (f-roam-rt6) the hero on the stock spot is the higher-address
  object (0x01A965F0), has the camera and triggers the doors.
- The engine's "player" (camera, HUD, exits) is the object built LAST (same as lanes A and B found).
- The kept disc uses **`--order before`**: record order is twin, player, friend 1, friend 2. So:
  - object built 1st = the twin, on the side spot;
  - object built 2nd = the hero on the designer's spot = the engine's player. Stock walking scripts, camera and
    exits behave as in the stock game for this hero.
- With lane A's patch as it is (first built -> controller 1, later -> controller 2) this means: **pad 1 drives the
  twin, pad 2 drives the engine's player.** VERIFIED (f-roam-pad2b: pad 2 walked the hero that owns the doors).
  `--order after` gives the opposite pairing (pad 1 on the stock spot, camera and exits on the pad 2 hero).
  Which pairing is wanted is lane E's call; the tool does both.
- The same order repeats in every room: pad 2 kept driving the door-owning hero across three room changes
  (f-roam-pad2b). This also answers lane A's open point 4 for this case.
- Twin and player are both placed at the entrance on every room change, wherever the other hero was standing.

## Tests

| ID | Disc / setup | Result |
|---|---|---|
| f-e1-2placeholders | tt07 b_40 with a second placeholder added by hand | VERIFIED: two Roxas, both run and jump (pad 1) |
| f-final-start, f-final-start3 | kept disc, normal New Game | VERIFIED: two Roxas side by side at first control (frame ~5150), both run and jump |
| f-final-scenes | kept disc, opening in-engine scenes not skipped (tt01 program 0x38, tt02 0x3F) | VERIFIED: scenes play normally, one Roxas (the story actor), no twin in the picture |
| f-roam-rt6 | all rooms + lane B's free-roam jump, order before, pad 1 drives both, positions tracked through PINE | VERIFIED: Merlin's house -> Borough -> Merlin's house -> Borough; two player objects and two Soras in the picture after each change |
| f-roam-pad2b | same disc (final placement rule), 2 linked copies, lane A patch: pad 1 only starts the game, pad 2 walks | VERIFIED: three room changes, both Soras after each, never out of sync (109 digests), 7 of 7 screenshot pairs identical |
| f-ca-fight2 | all rooms + lane B's Port Royal fight jump (no hand-made twin) | VERIFIED: two Soras with Keyblades side by side, fight runs (HP 20 -> 18) |
| f-lk-02 (also f-lk-01) | all rooms + jump to Pride Lands mission LK05_MS101 (recipe `local\variants\f-lk-mod`) | VERIFIED: two LION Soras, bird Donald, turtle Goofy, three large Heartless. In f-lk-01 the level-1 heroes were defeated (normal Game Over; Continue not pressed) |
| f-nm07-b99 / f-nm07-b99-twin | jump to nm07 program 0x47 (recipe `local\variants\f-nm-mod`) | VERIFIED: see "real player object placed directly" above |
| f-final-sync3 (also f-final-sync, -sync2 on earlier builds) | kept disc, 2 linked copies, lane A patch, random buttons on BOTH pads, 24,000 frames | VERIFIED: never out of sync (375 digests), 5 of 5 screenshot pairs identical |
| f-roam-rt2 .. rt5 | order after | The twin owns camera and exits; my walking script did not bring it to the door (the other hero stood in the doorway). Not a fault of the method; it is why the kept disc uses order before |

Not tested: Halloween / Christmas costumes through a placeholder, Tron, Timeless River (same mechanism, so
HYPOTHESIS that they work), minigames, Drive Forms, Limits, summons, save and load, a long playthrough, any of the
28 unchecked placements, and rooms where a second hero may break a one-on-one setup (Struggle fights, bosses).

## Memory

- No sign of trouble in any test, including the heavy ones: two lion Soras + Donald + Goofy + three large
  Heartless (f-lk-01: ran until Game Over), and two Soras + Jack + Goofy + the boss of nm07 (f-nm07-b99-twin).
- The two player objects sit about 107,500 bytes apart in memory in every room looked at (tt07: 0x01A90B00 and
  0x01AAB2F0, lane A; hb13: 0x01A7C1E0 and 0x01A965F0; hb09: 0x01A8FBA0 and 0x01AA9FB0). HYPOTHESIS: a second
  player object of the same form costs about 0.1 MB, i.e. the model and motion files are loaded once and shared.
- Free memory was NOT measured, and nothing was tested with a Drive Form (a different model per hero).

## Open problems

1. Who is "the player" (camera, HUD, exits) and which pad he gets: lane E. Facts above; both orders are available.
2. The 28 unchecked placements and the 21 special-mode placements listed under Numbers.
3. The ground check uses every collision triangle of the room. It does not know about barriers that are switched
   on per story state, moving platforms or scenery objects without collision data.
4. The twin is added in EVERY placement, also in minigames, one-on-one fights and forced events. Whether each of
   those should have a twin is a Phase 3 decision; the tool can leave rooms out (`--rooms` lists the rooms to DO).
5. A hero who is somewhere else in the room is put back at the entrance on a room change (both always arrive).
6. The kept disc is built from English build 2. If the English copy changes, rebuild (one command, about 20 s).

## How to use

```
python -I tools\lane-f\build_disc.py twin-everywhere --order before
    -> local\iso\test-f-twin-everywhere.iso, report in local\variants\f-twin-everywhere\report.csv

python -I tools\lane-f\build_disc.py <name> --order before --overlay <folder with test jump *.ard files>
    -> local\iso\test-f-<name>.iso   (twin everywhere on top of a lane-B style jump recipe, e.g.
       local\variants\b-roam\built\ard, local\variants\b-ca\b7\ard, local\variants\f-lk-mod\built\ard)

options: --order after|before   --rooms tt07,ca02 (only these rooms)   --also 54|- (real objects that also get a twin)
         --no-disc (room files and report only)
local\dotnet\dotnet.exe local\build\lane-f\LaneF.dll stats local\extract\kh2\ard     (facing statistics)
```
The original disc and the English copy are only read. The same inputs give the same bytes.

## Files of this lane

- `tools\lane-f\LaneF\` (C#, uses the OpenKH libraries to open room and map files; built to `local\build\lane-f`),
  `tools\lane-f\build_disc.py`.
- Test scripts `tests\scripts\f_*.txt`.
- Jump recipes made here: `local\variants\f-lk-mod` (Pride Lands), `local\variants\f-nm-mod` (nm07 program 0x47).
- Reports: `local\variants\f-twin-everywhere\` (report.csv, twin-all.txt, inject-report.txt, built room files).
- Test folders `local\tests\f-*`. Emulator copies `local\run-f`. Other test discs of this lane are deleted.
- No patch file and no hook site: lane F changes room data only.
