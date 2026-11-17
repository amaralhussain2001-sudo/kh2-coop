# Lane B: fights test-bed, the twin in a fight, sync in real play, pictures per second

Written 2026-11-10. All tests: SINGLE-PC, sandbox emulator copies `local\run-b` and `local\run-b2`, English disc copy
build 2 (SHA-1 de0ed50c...) as the base of every variant, scripted or random buttons, no humans.
Labels: VERIFIED (test id / address) or HYPOTHESIS. Test folders: `local\tests\b-*`.

## 1. A quick way into fights: DONE

### Method (chosen): "jump discs" (room-script edits), tests only
The first room of a New Game (`ard/tt01.ard`, script `evt`, Program 0x34) normally plays the opening movie and then
jumps on. A test disc replaces that one program with a jump to the room we want. Built with the shared pipeline:
a tiny OpenKH-style mod (`mod.yml` + script text) -> `Kh2Tool patch` -> optional `Kh2Tool ard-add` (add an object) or
`tools\lane-b\move_entity.py` (move an object) -> `Kh2Tool inject` from the English copy. About 15 s per variant.
Recipes (mod files and built room files) are kept in `local\variants\b-*`.

VERIFIED facts behind it:
- New Game chain of the stock game: tt01 program 0x34 (movie) -> tt01 0x38 -> tt02 0x3F -> tt07 0x6A -> tt07 0x5F
  (first control). Test b-trace01 (PINE watch of 0x0032BAE0..E8).
- A "Type 2" jump with `LocalSet N` runs program N (N >= 51, unique per world) in map / btl / evt of the room that
  owns it. Worked for HB 58 (-> hb09) and CA 55 (-> ca02). Tests b-fight01, b-ca7-idle.
- A "Type 1" jump with `LocalSet 0` uses the programs stored in the save. On a fresh save: Merlin's house (hb13)
  loads map 1 / btl 0 / evt 0, the Borough (hb09) loads map 1 / btl 1 / evt 0. Tests b-roam01, b-exit01.
- A fresh New Game save is fight-ready: Sora level 1, HP 20, Kingdom Key. Donald and Goofy are present only when the
  program says `Party DEFAULT`; in free roam on a fresh save Sora is alone.

### The test discs
| Disc (local\iso) | What New Game gives | Control at | Notes |
|---|---|---|---|
| test-b-ca5.iso (kept) | Port Royal fight "Defeat all of the Heartless!" (ca02 program 0x37), Sora alone, **twin beside him** | frame ~4650 | Clean fight: no helpers, normal Game Over. Script `tests\scripts\b_newgame.txt` |
| test-b-ca7 (recipe) | Same fight, no twin (control) | ~4650 | `local\variants\b-ca\b7` |
| test-b-ca6 (recipe) | Same fight, original Sora 2,500 units away, twin among the enemies | ~4650 | `local\variants\b-ca\b6` |
| test-b-roam.iso (kept) | Sora alone on the save point in Merlin's house (hb13). West door -> Borough (hb09) free roam with Heartless | ~4450 | Save script `b_save.txt`, exit script `b_exit.txt` |
| test-b-roam3.iso (kept) | Same, **with a twin**: 150 units nearer the door in Merlin's house, 200 units beside Sora at the Borough entrance | ~4450 | `local\variants\b-roam3` |
| test-b-fight1 / 3 (recipes) | Hollow Bastion Borough mission "Defeat the Heartless!" (hb09 program 0x3A) with Donald and Goofy / without them and with a twin | ~4500 | Two traps, see below |
Rebuild a recipe: `dotnet Kh2Tool.dll inject "<English copy>" local\iso\test-b-X.iso local\variants\<recipe folder> report.txt`.

Traps found in the Hollow Bastion fight (VERIFIED):
- The town's defense system (light pillars, object F_HB020 in group b_10) hits enemies for 3 and kills them with no
  button pressed; the player still gets the experience (b-twin06, b-death01). Bad for "who did the damage" tests.
- Mission HB09_MS901 never kills Sora: when HP is at or below about 30 % (6 of 20) the fight stops and the story
  cutscene with Pooh's book plays. Setting HP to 1 by hand ended the fight at once (b-death03, also b-twin05/07).

Trap of every jump disc that starts INSIDE a mission (test-b-ca*, test-b-fight*), VERIFIED:
- After Game Over, choosing **Continue** crashes the game: the screen goes white, no more frames, and the emulator log
  fills with "TLB Miss, pc=0x168af4 addr=0x2000000.." (reading past the end of memory). Seen with and without a twin,
  in one-copy and two-copy sessions (b-go-continue, b-sync02-twin, b-sync02b-twin, b-sync03-ctl).
  HYPOTHESIS: the game has no valid retry point because New Game jumped straight into the mission. It is a test-disc
  artifact: on test-b-roam (save, walk through a door, get defeated in the next room) Continue works and the fight
  resumes with full HP (b-go-roam). "Load Game" just opens the load screen (b-go-load).
- So: on mission jump discs stop random-button tests before Sora dies (about frame 7,800 with no helpers), or use
  the free-roam discs for long tests.

### Ways not used
- GoA ROM Edition mod: not built. Its start needs its Lua script (it re-points a jump in memory; without Lua the game
  is sent to a dead end on purpose, see the script's NewGame function), and the jump-disc method made it unnecessary.
- Memory pokes by .pnach: possible (the emulator supports button-conditional codes, `Patch.cpp` D-type; pad 2 raw
  buttons at 0x0034D5DC), not needed.
- Scripted walk through the real opening: not needed.

## 2. The twin in a fight (both Soras still on pad 1)

Twin = object 0x54 (P_EX100, Sora) added to the fight's spawn group next to the player placeholder (0x236).

| Question | Answer | Evidence |
|---|---|---|
| Does it appear, armed? | Yes: a second Sora with Keyblade, moves and attacks with pad 1 like the first | b-twin01, b-ca5-idle screenshots |
| Own HP? | **No. Both Soras use the same HP record (unit slot 1).** Each object holds a pointer to its unit slot 0x41C bytes after its first position copy; both point to 0x01C6C750 | b-twin04 dump, `obj_compare.py` |
| Do enemies target and hit it? | Yes. With the original Sora 2,500+ units away and untouched, the shared HP still fell 20 -> 1 while enemy HP stayed full | b-ca6-idle; b-twin06 (positions: original never moved, twin knocked around) |
| Do its attacks hit? | Yes. Enemies lose HP and die from second 40 on while the original Sora is still 1,300-2,000 units away | b-ca6-atk + b-ca6-pos, control b-ca6-idle |
| Rewards | Experience, munny and item drops are collected ("GET! Dark Shard") | b-roamtwin02, b-ca6-atk |
| Camera | Follows the **twin** (the player object created last), not the original | b-twin05/06: camera on the Sora among the enemies |
| HUD | One HUD only: command menu, one Sora gauge showing the shared HP, Reaction Commands (Cyclone, Save, Examine) appear | same screenshots |
| Room exits | Triggered by the **twin**, not by the original: original at the door = nothing; twin at the door = room change | b-roamtwin01 (no change), b-roamtwin02 (change) |
| Is the far Sora pulled back? | No. The original stood 2,700 units away for 20 s without being moved | b-twin06 |
| HP reaches 0 | Normal Game Over screen ("Continue / Load Game"), same as without a twin | b-ca5-idle vs b-ca7-idle |
| Cutscene starts | Plays normally with the story's own actors; the twin is not in it; the jump after it works | b-twin01, b-twin07 |
| Room change | The twin exists only in rooms whose spawn data lists it. With the twin added at the next room's entrance, both Soras arrive | b-roamtwin02 |

Other VERIFIED details:
- Unit slots: slot 1 at 0x01C6C750 (HP at +0, max HP at +4), next slots 0x268 bytes LOWER: slot 2 0x01C6C4E8
  (Donald 18/18), slot 3 0x01C6C280 (Goofy 28/28), then enemies (10 = Shadow, 20 = Soldier). With no friends the
  enemies start at slot 2. (b-twin04)
- Character objects found by position: e.g. Sora first position copy 0x01A96BD0, more copies at +0x4D0 and later.
  Addresses change per room and per disc variant but repeat exactly between runs of the same test.
- Pressing attack makes the far-away Sora walk toward the enemies at about 100 units per second (b-ca6-pos).
- The slot shows 40/40 for about 3 s after the room loads, then the game sets 20/20: write test values after that.

Meaning for the plan (HYPOTHESIS until built): the engine treats the last-created player object as "the player"
(camera, exits, HUD). For two real players this is good news and a to-do list: enemies, damage, rewards and Game
Over already work for both; own HP needs a second unit slot; camera, exits and HUD need work for the other Sora.

Not tested: magic, items, Drive, Limits, lock-on, using Reaction Commands, chests, "Continue" after Game Over,
who the enemies prefer when both Soras are close, and anything with the twin on its own controller (lane A).

## 3. Sync in real play (two linked copies, 127.0.0.1)

| ID | Content | Result |
|---|---|---|
| b-sync01 | test-b-roam, no twin. Pad 1: New Game, save to file 01 (frame ~5040), walk out the west door, then random buttons; pad 2 random. 34,000 frames at 4x | **Never out of sync** (531 digests). 8 screenshot pairs identical. Rooms: Merlin's house -> Borough -> Merlin's house -> Borough (3 changes). Fight seen: battle flag 1, HP 20 -> 13. Both memory cards contain the save and are byte-identical (SHA-1 4b44974e...) |
| b-sync04-twinfight | test-b-ca5 (**twin** in the Port Royal fight), random buttons on both pads from frame 3,600, 7,800 frames | **Never out of sync** (121 digests), 5 of 5 screenshot pairs identical, HP 20 -> 3 during the fight |
| b-sync05-twinroam | test-b-roam3 (**twin** in free roam). Pad 1: save, walk out the door (the twin triggers it), then random; pad 2 random. 34,000 frames | **Never out of sync** (531 digests), 9 of 9 screenshot pairs identical, Merlin's house -> Borough, damage taken in the Borough |
| b-sync02-twin, b-sync02b-twin, b-sync03-ctl | test-b-ca5 / ca7 for 16,000 frames | In sync up to the last digest (111 at frame ~7,140), then both copies stopped at the same frame (~9,200): random buttons picked "Continue" after Game Over, which crashes on these discs (see section 1). Not a sync failure: the control without a twin stopped the same way |

Not covered: internet or LAN (all on one PC), humans, cutscene skipping by both players, Drive Forms, other worlds.

## 4. Pictures per second (method of test fps01: 12 consecutive frames, count different pictures)

| Where | Different pictures in 12 frames | Per second |
|---|---|---|
| Hollow Bastion Borough fight, 3 samples (b-fps-fight) | 7, 7, 7 | 30 |
| Port Royal fight, 2 samples (b-fps-ca) | 7, 7 | 30 |
| Merlin's house, running, 2 samples (b-fps-house) | 6, 6 | 30 |
| (main lane: Market Street 30; title and menus 60) | | |

Also VERIFIED (b-rate01, normal speed): while Sora runs, his position in memory changes every 33.4 ms (115 of 115
gaps). So in play the game also THINKS 30 times per second, it does not only draw 30.
HYPOTHESIS: a community "60 fps" patch exists for this game (a PCSX2 forum thread with that name came up in the
first web search); not looked at.

## 5. Things the main lane should know

1. Save dialog text: saving to an empty file asks "Delete selected file?" (default No), then shows "Deleting previous
   data..." and "Saving data..". The game does save (file 01 appears; the card has the BISLPM-66675 folder).
   The wording looks like mismatched text numbers in the pack's Japan-specific system text. A player could be scared
   off or misled. Tests b-save01, b-save02.
2. Room title cards are pictures with Japanese and English together ("住宅街 -BOROUGH-"); they are not part of the
   text patch and stay as on the original disc.
3. PINE accepts one client at a time; a second connection times out.
4. Fresh-card save flow in buttons (Japanese layout): Triangle, Circle (Save), Circle (Slot 1), Circle (file),
   Left, Circle (Yes). Leave the menu with Cross.
5. Merlin's house from the save point: up = +z, left = -x; the west door is at about (-600, 0, -575).

## 6. Files of this lane

- Tools `tools\lane-b\`: pine.py (PINE client, watch / dump), track.py (follow player objects), list_units.py,
  obj_compare.py, find_objs.py, sethp.py (ONE-copy tests only: memory write), pollrate.py, ardsum.py,
  find_fights.py (563 enemy programs listed from all 289 rooms), move_entity.py.
- Scripts `tests\scripts\b_*.txt`.
- Room dumps `local\analysis-b\ard\*.txt`.
- Discs kept: `local\iso\test-b-ca5.iso`, `local\iso\test-b-roam.iso`, `local\iso\test-b-roam3.iso` (4.3 GB each).
  Others deleted, recipes kept in `local\variants\b-*`.
- Emulator copies: `local\run-b` (2 copies), `local\run-b2` (1 copy).
