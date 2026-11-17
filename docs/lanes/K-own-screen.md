# Lane K: can each player have an own screen? (study, plan Phase 1C)

Written 2026-11-10. Disc base: English-text copy build 2 (game program unchanged, CRC F266B00B). All tests
SINGLE-PC, sandbox emulator copies `local\run-k`, scripted or random buttons, no humans. Base patch: lane E
(`lane-e-x2`: player 1's hero is the engine's player on controller 1, the twin on controller 2).
Labels: VERIFIED (test id / address / how) or HYPOTHESIS. Test folders: `local\tests\k-*`.

## The answer

**Yes, but.** The game can draw a full view for each hero in every game step, and it does so with its own code.

- **What each player would see:** a full picture from a camera that follows their own hero and turns with their
  own right stick, **30 different pictures per second, the same as the original game in play** (VERIFIED for the
  drawing, tests k-rate1 and k-fight-ee0; the "show only my view" part on each PC is not built).
- **How:** the game has a built-in two-view render mode. It uses it for camera cross-fades: the scene is drawn
  twice in one step, once per view, into two pictures that are then put on the screen. The demo switches that mode
  on for good and gives view 2 a second camera. Nothing differs between the two PCs inside the game, so it stays
  in sync (VERIFIED, 30,000 frames with a room change and random buttons, test k-sync1).
- **Cost in emulated PS2 power:** none seen. The game kept its pace of 30 steps per second with two views at the
  normal 100 % emulated CPU, in a room, outdoors and in a fight, and also with the emulated CPU slowed down
  (see "Pace and emulated CPU").
- **The buts:**
  1. **The HUD is drawn once, over the finished picture.** In the demo the two views are side by side and the one
     HUD lies across both. Each player needs their own HUD drawn for their own view. Not done; this is the biggest
     remaining job and it overlaps with player 2's own command menu (lane G).
  2. **The demo shows both views side by side in one picture.** It does NOT yet put view 1 on one video frame and
     view 2 on the next. Showing a player only their own view (a crop of their half, or alternate frames) is the
     emulator-side job outside this lane, plus the HUD job above.
  3. Only the normal follow camera was given a second instance. Lock-on camera, event cameras, the game's own
     cross-fades and cutscenes are not handled (list below).
- **Not production code.** The demo patch is an experiment that fills the lane's code cave completely.

## Evidence by question

### 1. How the game paces a step in 30 mode

VERIFIED by decompiling (`local\analysis\k\timing.txt`, `tasks.txt`) and by the runtime task lists
(`local\analysis\k\tasks_play.txt`, `tasks_twoview.txt`, read through PINE with `tools\lane-k\tasks.py`):

| Thing | Address | What it does |
|---|---|---|
| Main loop | 0x00101F3C-0x00101F60 | runs every task of the scene's list once (0x001029E8), then yields to the outer list (0x00102448) |
| Outer task list | pointer 0x0032B91C | 10 tasks; the game scene is one of them (priority 130000, coroutine 0x00101EA8) |
| Scene task list | scene object 0x0032B968, list of scenes at 0x0038AA40 | 39 tasks in play (one-view mode), in priority order |
| Camera task | priority 26000, 0x00140CC8 | calls the camera update 0x00140B68(camera 0x00348710, 0) |
| Draw tasks (one-view mode, flag value 3) | priorities 6000, 6001, 30000, 41000, 43000, 49999, 50000, 60001, 65000, 71000 | installed by 0x001618F0; 49999 / 50000 (0x00161880, 0x001618A0) draw the scene |
| End-of-step task | outer priority 800000, 0x0014CF88 | waits for the video frames (0x0014D060), then sends the finished draw list to the graphics chip (0x0014E5F0) |
| Wait | 0x0014D060 | waits one video frame (0x0014D478), then `flag` more; step length `dt` = number of video frames passed x game speed |
| Flag | 0x00349E1C (1 in play) | video frames to wait beyond the first; set by 0x0014CE30 |
| Step length, game speed | 0x00349E10, 0x00349E0C; raw 0x00349E14 | 2.0 in play in 30 mode |
| Video-frame interrupt | 0x0014CF18 | counts frames (0x00349E04, 0x00349E08) and wakes the waiting task |

So in 30 mode the game **computes one step, draws the scene once, and waits two video frames**. It does not draw
the same scene twice. The second video frame shows the same picture again (VERIFIED earlier by test fps01:
consecutive screenshots come in identical pairs).

### 2. The camera, and keeping it twice

VERIFIED (`local\analysis\k\cam.txt`, `cam2.txt`, memory reads with `tools\lane-k\camprobe.py`):

- The game's camera is ONE object at 0x00348710, 0xF0 bytes long (the next variable starts at 0x00348800):
  look-at point at +0x00, eye at +0x10, a third point at +0x20, angles at +0x30 / +0x34, flags +0x38..+0x3B,
  type +0x40 (0 = normal follow camera, up to 10), target object +0x44, and the follow / smoothing state behind.
- Its update routine 0x00140B68 takes the camera object as a parameter, and so do the routines below it. So the
  game's own code can run a SECOND camera object. The demo keeps one at 0x000F0F10 and calls the same update for it.
- The follow camera asks for controller 0 at one place (0x001403D4). The demo answers "controller = current view
  index", so camera 1 turns with pad 1 and camera 2 with pad 2.
- The camera update ends by writing the result into a "view" block (0x00106A18 / 0x00106A60, eye and matrices).
  There are blocks for view 0 and view 1; the current one is chosen by the view index 0x0033CC40 (0x001069F8).
  The demo updates camera 2 with view index 1.
- VERIFIED behaviour (tests k-dual2, k-dual3): camera 2 follows the twin exactly as camera 1 follows player 1's
  hero in the same situation (same eye positions for the same walk), and each camera turns only with its own
  player's right stick.

Other camera types read controller 0 at seven more places (0x00140778, 0x0014E940, 0x001585F8, 0x00158DDC,
0x001590E8, 0x001594A0, 0x0015A5E4); not touched. Some camera code asks for "the camera" or its type through
0x00140DF0 / 0x00140DC0 (20 and 12 callers) and gets camera 1; not examined one by one.

### 3. The demo: two views drawn in every step

The key finding (VERIFIED, `local\analysis\k\views.txt`, `dual.txt`): **the engine already has a two-view render
mode.** 0x001620A8 installs a second list of draw tasks (flag value 5) that draws the scene twice in one step:
first pass at priorities 6000-71000, a buffer switch at 90000, second pass at 90005-90110, and at 90130 a task
(0x00161C70 -> 0x00161AA8) that puts the two pictures on the screen as two sprites with blend weights
(0x0034C76C, 0x0034C768). The game uses it for camera cross-fades (0x00161F48, reached from six places through
0x00162058) and removes it when the fade ends (0x00161C88 / 0x00161D48 -> 0x001623B0, 0x001618F0).
The two pictures are 512 wide, 24-bit, and 416 lines are used (program data 0x0036B478, 0x0036B480).

What the demo patch does (`patches\lane-k-dual-sbs-move`):
1. The camera task updates camera 1 as before. If a twin exists (lane E's pointer 0x000F05CC) and the two-view
   mode is off (0x0033CC44 = 0), it removes the one-view draw tasks (0x001619E8), installs the two-view ones
   (0x001620A8), and starts camera 2 as a copy of camera 1 with the twin as target (0x0013F558).
2. Every step it updates camera 2 for view 1 (twin as target, controller 2).
3. The two pictures are placed side by side (each squeezed to half width) with full weight, instead of blended.
4. The twin's left stick is turned by camera 2's view (question 4).

Results:

| Test | What | Result |
|---|---|---|
| k-dual1 | Merlin's house, 2 linked copies; P2 walks away, P1 turns camera 1, P2 turns camera 2 | VERIFIED by eye (`local\tests\k-dual1\sheet.png`, `p1_f005300.png`): the picture holds two different views of the room; the right half follows P1's hero and turns with pad 1, the left half follows the twin and turns with pad 2. In sync (84 digests) |
| k-dual2 | same, with memory reads | VERIFIED: camera 1 target = hero, camera 2 target = twin; look-at points equal the heroes' positions; `local\analysis\k\k-dual2-cams.txt` |
| k-rate1 | both cameras turning; 12 consecutive video frames; each half hashed separately (`tools\lane-k\halfhash.ps1`) | VERIFIED: **7 different left halves and 7 different right halves in 12 frames**, both changing in the same frames: each view is redrawn in every step, 30 times per second. In sync (85 digests) |
| k-fight-ee0 / ee1 / ee2 | Port Royal fight with twin and enemies, emulated CPU 100 % / 130 % / 180 % | VERIFIED: 7 different pictures in 12 consecutive frames in all three (pace held); both views show the fight, enemies, hit effects (`local\tests\k-fight-ee0\p1_f005200.png`); in sync; screenshot pairs identical |
| k-sync1 | door disc: both heroes through the door (room change), then random buttons on both pads, 30,000 frames | VERIFIED: **never out of sync, 468 digests**, 8 of 8 screenshot pairs identical. After the room change the two-view mode is on again and camera 2 follows the new twin object (`local\analysis\k\k-sync1-cams.txt`, `local\tests\k-sync1\sheet.png`) |

What the demo does NOT show: view 1 on one video frame and view 2 on the next. Both views are in every picture,
side by side. Alternating them needs a second "put on screen" inside one step (the draw list is sent to the
graphics chip once per step, by the end-of-step task), or the emulator can simply show each PC its half.
The fallback asked for in the brief (alternating views in the 60 mode, or 15 per view) was not needed and not built.

### 4. Movement relative to the right camera

VERIFIED: the stick is turned into a world direction by 0x00178330, which takes the matrix of the CURRENT view
(call of 0x00106A60 at 0x0017837C). It has three callers: 0x001784E8 (normal movement, player object in s0),
0x001785F4 (player object in s1), 0x001796FC (player object not kept).

| Test | Patch | Result |
|---|---|---|
| k-move1 | two views, no movement change | FAILED as expected: P2 turns camera 2, pushes up: the twin moves along camera 1's forward (cosine 1.00 with camera 1, -0.49 with camera 2) |
| k-move2 | + movement hooks | VERIFIED: the twin moves along camera 2's forward (cosine 1.00 with camera 2, -0.47 with camera 1) |
| k-move3 | same patch, P1 turns camera 1 and pushes up | VERIFIED: player 1's hero moves along camera 1's forward (cosine 1.00 with camera 1) |

The third caller (0x001796FC) is not hooked: whatever uses it would move the twin relative to camera 1.
Attacks, dodges and anything else that aims by camera were not tested.

### 5. What breaks, and what was not looked at

Seen (VERIFIED by eye on the screenshots named above):
1. **HUD:** command menu, HP / MP / Drive gauges and messages are drawn once, after the two pictures are on the
   screen, at full-screen positions. In the side-by-side demo they lie across both halves. They show player 1's data.
2. **Marks over the scene** (the lock-on target ring, the green HP orbs' icons) are drawn the same way: once, at
   full-screen positions, not once per view (`k-fight-ee0\p1_f005200.png`).
3. A small "1P" label appeared in that fight picture between the halves. Origin unknown (HYPOTHESIS: a label of
   the game for the player when hidden behind scenery).
4. The main menu (START) opens and closes normally over the two-view picture (k-rate1, frames 5340 and 5450).
5. Each view is drawn at the game's full size but shown squeezed to half width in the side-by-side picture.

No fault seen, but only checked by eye in three places (Merlin's house, the Borough outdoors, the Port Royal
fight): scenery, characters, enemies, hit effects, light rings of the save point and shadows appear in both views,
also when the cameras look in opposite directions. So culling works per view there.

NOT examined:
- Effects that use the previous picture (blur, heat haze, Drive Form effects), magic, summons, big bosses.
- Sound: which camera is the "ear". Area triggers, ambush spawns and enemy wake-up: they follow player 1 (lane E).
- **The game's own cross-fades while the two-view mode is permanently on.** HYPOTHESIS: the game would install
  its two-view task list a second time (0x00161E40) and draw four times until the fade ends. Not tested.
- **Cutscenes and rooms without a twin after the mode was switched on:** the demo never switches back to one
  view; view 2 would keep its last camera. Not tested (no room in the code cave for it).
- Lock-on camera and the other camera types for camera 2; the pause screen of the game (only the menu was seen).
- Memory: camera 2 is 0xF0 bytes in the cave. The two-view mode uses the buffers the game itself uses for
  cross-fades, so no extra video memory is taken (VERIFIED only in the sense that the game's own mode is used).

### Pace and emulated CPU

Method: 12 consecutive video frames, count different pictures (7 = the original 30 steps per second).

| Scene | Views | Emulated CPU | Different pictures in 12 frames |
|---|---|---|---|
| Merlin's house (k-rate1) | two | 100 % | 7 |
| Port Royal fight (k-fight-ee0, ee1, ee2) | two | 100 %, 130 %, 180 % | 7, 7, 7 |
| Port Royal fight (k-load-dual-1, -2) | two | 75 %, 60 % | 6, 6 (pace held: 6 or 7 both mean 30 per second) |
| Port Royal fight (k-load-dual-3) | two | 50 % | 5 (pace slips: some steps take three video frames) |
| Port Royal fight (k-load-base-3, control) | one | 50 % | 6 (pace held) |

So two views per step fit into the two video frames a step already has, without any faster emulated CPU: in this
fight the pace held down to 60 % of the normal emulated CPU and only slipped at 50 %, where one view still held.
Two views do cost more than one, but there is room. Heavier scenes (big bosses, many effects) were not measured.
All these runs stayed in sync.

### 6. Sync

Every two-copy run stayed in sync: k-dual1 (84 digests), k-rate1 (85), k-fight-ee0/1/2, k-move1/2/3 and the long
run k-sync1 (468 digests, room change, random buttons on both pads, 8 identical screenshot pairs).
The only values written from outside the game are constants in the patch file, the same on every PC.

## The demo patch

Not production code. Files: `patches\lane-k-dual-sbs-move\SLPM-66675_F266B00B.pnach` (full demo),
`patches\lane-k-dual-sbs` (without the movement hooks), `patches\lane-k-base` (lane E's lines only; equal to
`lane-e-x2` line for line). Generator: `python -I tools\lane-k\make_k.py <outDir> dual sbs move`
(options in its header: `stack` = one view above the other, `alpha=A,B` = blended, `nocam2`, `nostick`).

Hook sites added by this lane (lane E's and lane A's are unchanged):

| Address | Original | Now | Purpose |
|---|---|---|---|
| 0x00140CC8, 0x00140CCC | `addiu sp,sp,-16` / `lui a0,0x35` | `j 0x000F0E00` / `nop` | camera task: camera 1, switch to two views when a twin exists, camera 2 |
| 0x001403D4 | `jal 0x00167F18` (controller 0) | `jal 0x000F0EB0` | follow camera's controller = current view index |
| 0x001784E8 | `jal 0x00178330` | `jal 0x000F0EC4` | stick to direction: note whether the mover (s0) is the twin |
| 0x001785F4 | `jal 0x00178330` | `jal 0x000F0EBC` | same, mover in s1 |
| 0x0017837C | `jal 0x00106A60` | `jal 0x000F0EE0` | inside that routine: the twin gets view 1's block (0x003A8000) |
| 0x00161B38, 0x00161BB4 | `addiu a1,zero,512` | `addiu a1,zero,256` | the two view pictures at half width |
| 0x004F3E78 (16-bit, written every video frame) | 0 | 256 | second picture starts at x = 256 |
| 0x0034C76C, 0x0034C768 (bytes, every video frame) | fade weights | 128, 128 | both pictures at full weight |

Which build each test used: k-dual1, k-dual2, k-dual3, k-fight-ee0/1/2 and k-move1 ran with the first build of the
demo (camera 2 at 0x000F0F00, a flag byte instead of the view index for the camera's controller, no movement
hooks). k-move2, k-move3, k-rate1, k-sync1 and k-load-* ran with the final build described here.

Code cave, all inside 0x000F0E00-0x000F0FFF: routines 0x000F0E00-0x000F0F03 (65 instructions), one flag byte
0x000F0F08, camera 2 at 0x000F0F10-0x000F0FFF. The cave is full: a real version needs more room (about as much
again for switching back to one view, the other camera types and the third movement caller).
The flag byte and camera 2 rely on that memory being zero at start (lane E checked the range).
A listing of the routines is printed by the generator's source (`K_CODE` in `make_k.py`, with comments).

## What a full version would still need

1. **Own HUD per view.** Draw the HUD once for each view, each with its own player's data. This is the largest
   open piece and is shared with lane G's "second command menu".
2. **Show each PC its own view** (emulator side, outside the game, so it cannot break sync). Two ways:
   show a crop of the PC's half of the side-by-side picture, stretched (the views are squeezed 2:1, so a higher
   internal resolution setting is wanted), or have the game put view 1 and view 2 on alternate video frames and
   show every second frame. The second way needs a second "send to the graphics chip" inside one step.
3. Switch back to one view when there is no twin (cutscenes, rooms without one) and stay out of the way of the
   game's own cross-fades.
4. Camera 2 for the other camera types (lock-on first), the seven other controller reads, the third movement
   caller, and aiming of attacks.
5. Marks over the scene (lock-on ring and similar) per view.
6. A check of sound, effects that reuse the previous picture, Drive Forms, bosses, and heavy scenes for pace.

## How to repeat

```
python -I tools\kh2_session.py make 2 --run-dir run-k
python -I tools\lane-k\make_k.py patches\lane-k-dual-sbs-move dual sbs move
python -I tools\kh2_session.py run k-dual1 --run-dir run-k --port 29250 --iso local\iso\test-b-roam3.iso ^
   --players 2 --slots 0,1 --frames 5400 --speed 2 --snap 4500,4900,5045,5245,5300 ^
   --script tests\scripts\lane-k\a_p1.txt --script2 tests\scripts\lane-k\a_p2.txt --then idle ^
   --fresh-card --pine 28101 --patch-dir patches\lane-k-dual-sbs-move
python -I tools\lane-k\camprobe.py local\tests\k-dual1 28101 4500,4900,5045,5245,5300      (while it runs)
powershell -File tools\lane-k\halfhash.ps1 -Dir local\tests\k-rate1 -Pattern "p1_f0050*.png"
```

## Files of this lane

- `tools\lane-k\`: `make_k.py` (demo patch generator), `tasks.py` (task lists), `camprobe.py` (cameras and
  heroes), `movecheck.py` (movement direction against each camera), `halfhash.ps1` (each half of a screenshot),
  `gh.sh` + `ghidra\LaneKDump.java` (decompile from the project copy `local\ghidra-k`), copies of lane E's
  generator (`make_e.py`, `e_exit.py`, `asm.py`) and of the scan / PINE tools.
- `tests\scripts\lane-k\*.txt`. Decompiled text, task lists and probe outputs: `local\analysis\k\`.
- Patches: `patches\lane-k-dual-sbs-move`, `patches\lane-k-dual-sbs`, `patches\lane-k-base`.
- No disc was made by this lane (it used `test-b-roam3.iso`, `test-b-ca5.iso` and `test-e-door.iso` read-only).
- Emulator copies `local\run-k` (2 copies) are left in place.
