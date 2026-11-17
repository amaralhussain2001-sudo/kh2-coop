# Lane V1: two views (an own screen for each player) on the merged build

Status 2026-11-10: DELIVERED for single-PC tests. Every result below is SINGLE-PC (two linked emulator copies on
one machine, scripted or random buttons). Words used: VERIFIED = measured, with the test name; HYPOTHESIS = not
measured. Player 2's finished picture was checked with a test build that leaves it on the display; no emulator
that picks it up at the marker exists yet (that is lane V3's part).

## THE CONTRACT (for lanes V2 and V3)

### The view layout byte

| Thing | Value |
|---|---|
| **View layout byte** | **0x000F6F00** (one byte in the emulated PS2's main memory), written at the end of every game step, just before the step's picture is put on the display. It describes that picture. |
| 0 | ONE full view. Every PC shows the display as it is. |
| 1 | TWO views SIDE BY SIDE in one picture: left half = player 2, right half = player 1. Only the fall-back patch `patches\lane-v1-two-views-sbs` produces this. Details at the end of this section. |
| **2** | **TWO FULL-SIZE PICTURES, ONE AFTER THE OTHER, WITH A MARKER BETWEEN THEM. This is what the delivered patch `patches\lane-v1-two-views` produces.** |
| 3 | Alternate video frames. NOT BUILT (reasons in "Layout 3"). |

### Layout 2: exactly what happens, and what lane V3's emulator must do

At the end of every step with two views, right after the game's own wait for the video frame, the game sends
these three things to the graphics chip in one go (no video frame boundary can fall between them):

1. The game's own display copy (draw buffer page 216 -> display buffer page 0): the display buffer now holds
   **PLAYER 2's finished picture** (player 2's camera, the whole 3D picture and everything 2D).
2. **THE MARKER**: one write to the graphics chip's LABEL register that changes nothing (its mask is 0).
   On the wire (GIF path 3, its own transfer): GIF tag `00008001 10000000 0000000E 00000000`, then the data
   quadword `56310002 00000000 00000062 00000000` = register 0x62 (LABEL), ID = **0x56310002**, ID mask = 0.
   The packet sits at 0x000F6AC0 (chain tag) / 0x000F6AD0 (data).
3. The display copy again, this time reading the second buffer (page 112): the display buffer now holds
   **PLAYER 1's finished picture**. This is what stays on the display until the next step.

What each emulator does while the byte is 2:
- **Player 1's PC** (controller in PS2 port 1): nothing special. It shows the display at each video frame, as today.
- **Player 2's PC**: when the marker passes through the emulator's GIF handling (the LABEL write with exactly
  ID 0x56310002 and mask 0), show (or keep a copy of) the display buffer as it is at that point of the
  graphics stream, and do not show the regular video frames. If no marker has arrived for a few video frames
  (the game went to a menu or a film), go back to showing the display normally; when the byte is 0, always
  show the display normally.
- Both pictures are complete 512 x 448 display pictures made by the game's own display copy, so the scaling to
  the window is the same as for the normal game. Nothing is squeezed or cut.
- Both PCs compute and draw exactly the same things; only what each window shows differs.

An emulator that knows nothing about this shows player 1's picture, which is the normal one-player picture.

### For lane V2 (HUD per player) in layout 2

| Address | Size | Meaning |
|---|---|---|
| 0x000F6F02 | byte | **2D target mask, written by lane V2**: 0 = what is drawn goes into both pictures (default), 1 = into player 1's picture only, 2 = into player 2's picture only. Set it before the draw calls and back to 0 after. |
| 0x000F6F03 | byte | 1 while the "both pictures" part of the step is open (from the scene task at priority 90130 to the end of the step). The mask only works then. |

- From priority 90130 on, every packet chain the game sends on the drawing channel (through the game's
  "send packet chain" routine 0x002F3918: HUD, text, marks, 2D effects) is sent twice: first into player 1's
  picture (second buffer, graphics memory page 112), then, as the game sent it, into player 2's picture
  (draw buffer, page 216). So the game's normal HUD appears, the same, on both pictures. Making it differ per
  player (own HP gauge, own command menu, own lock-on ring) is lane V2's work, with the mask byte.
- Positions computed from a camera after priority 90130 use view 0 (player 1's camera) unless you choose
  view 1 yourself (0x001069F8). View 1's block is at 0x003A8000, view 0's at 0x003A7F70. So the lock-on ring
  and other marks tied to 3D points are, as delivered, right on player 1's picture and wrong on player 2's.
- During that part of the step the HUD's depth buffer is at page 320 (cleared to "far" at 90130), because the
  game's depth buffer pages (112-215) hold player 1's picture. The redirection finds frame, texture and depth
  settings only where the game writes them as "address + data" entries (how all packets seen so far do it).
- Draw calls made before priority 90000 land in player 1's 3D picture only, between 90005 and 90130 in
  player 2's only.

### Other addresses of this lane (read-only for other lanes; all zero at boot)

| Address | Size | Meaning |
|---|---|---|
| 0x000F6F01 | byte | layout of the picture being built in the current step |
| 0x000F6F04 | word | 1 while the two-view render tasks installed in the scene are ours |
| 0x000F6F08 | word | switch request waiting for the end of the step (1 = to two views, 2 = to one view) |
| 0x000F6F0C | word | not 0 while player 2's camera is swapped into the game's camera memory |
| 0x000F6F10-0x000F6F1F | | work values of the packet redirection |
| 0x000F6E00 | 0xF0 bytes | player 2's camera object while it is not swapped in (layout of 0x00348710) |
| 0x000F6C00 | 0x120 bytes | player 2's copy of the camera module's variables 0x0034A970-0x0034AA8F |
| 0x000F6D20 | 0xE0 bytes | work list of the packet redirection |

### Layout 1 (fall-back patch only)

One picture, two halves: LEFT half x 0..255 = player 2, RIGHT half x 256..511 = player 1, each a complete
512 x 416 view drawn at half width (horizontal scale 0.5, vertical scale 1.0); the HUD is drawn once over the
whole picture. The emulator shows its own half stretched by 2 horizontally. Tested as `lane-v1-b`
(same words as `lane-v1-two-views-sbs`): v1-e-roam, v1-f-lock, v1-d-menu, v1-c-hbf, all in sync.

## What was built

Patch `patches\lane-v1-two-views\SLPM-66675_F266B00B.pnach` = every word of merged build v2 + sections
"views" (598 words at 0x000F6000-0x000F6957) and "views-data" (108 words of constant graphics packets at
0x000F6A00-0x000F6BAF); `listing.txt` beside it explains every word. Generator: `python -I tools\lane-v1\make_v1.py`
(options: `sbs` = layout 1 patch, `showp2` = TEST ONLY, the display keeps player 2's picture, `noviews` = merged-v2
only). Lane K's demo cave 0x000F0E00-0x000F0FFF is not used. No hook of merged-v2 is changed; lane G's second
control object S2 and lane D's unit slot are used as they are.

How it works, in the order of a step:
1. **Cameras.** The camera task (hook 0x00140CC8) updates the game's camera for player 1, then swaps player 2's
   camera (object and the camera module's variables) into the same memory, updates it for the twin with view
   index 1, and swaps back. So player 2 has a camera of the game's own kind, with the game's own code. The same
   swap wraps the four places where a lock-on manager talks to the camera when it is S2's manager, and the
   camera code's eight controller reads return controller 2 while player 2's camera is in place.
2. **Two 3D pictures.** The game's own two-view render tasks (made for its event cross-fades) draw view 0 and
   view 1 at full size 512 x 416 into the draw buffer, one after the other. After the first (player 1's) the
   game's own capture reads it back to main memory (0x00457580).
3. **2D into both** (layout 2). At priority 90130 player 1's 3D picture is loaded into the pages of the depth
   buffer, the HUD's depth moves to page 320, and from then on every drawing packet is sent twice (see above).
   The copy for player 1 goes first and leaves depth alone, so depth tricks between HUD parts (the HP ring is
   cut with one) come out the same in both pictures.
4. **End of step**: display copy, marker, display copy (see the contract).
5. **Movement.** "Stick -> world direction" (hook 0x0017837C) uses view 1 for the twin's stick, view 0 otherwise.

Why the pictures cannot both sit in graphics memory in a simpler way (VERIFIED by the first two attempts,
v1-h-full first run and v1-h-tex): the graphics memory is full (display 0-111, depth 112-215, draw buffer
216-319, texture work area 320-423, HUD textures 424-511). A copy kept at page 320 during the second 3D pass is
overwritten by textures; a second buffer at page 320 during the 2D part gets HUD effect textures written into
its corner; a second buffer in the depth pages with depth simply switched off turns the HP ring into a full
circle. The delivered arrangement (picture in the depth pages, HUD depth at page 320) showed none of these.

## Acceptance test: is each player's picture the same as the one-player game?

Same disc, same inputs, same frame; (a) merged base in one view, (b) the delivered patch.

| Question | Result |
|---|---|
| Player 1: framing, zoom, viewpoint | **VERIFIED identical.** v1-h-one (a) against v1-h-full (b), Merlin's house, player 1 walks and turns the camera: at frames 4950 and 5100, 97.0 % of all screenshot pixels are exactly equal and every differing pixel belongs to three animated particle effects (save point glow, the sparkle on "MAX", a treasure sparkle). Scenery, both heroes, command menu, HP ring, portrait: pixel-identical. Pictures: `docs\lanes\V1-pictures\p1-oneview-vs-twoview-4950.png` (left a, right b), `p1-difference-4950.png` (white = equal). |
| Are the particle differences caused by two views? | **No (VERIFIED):** the same effects differ in the same way between the merged base and the delivered patch on a disc with ONE hero, where the patch never leaves one view (v1-i-solo against v1-j-solo-two: 2.5 % of pixels at frame 5100, only those effects). HYPOTHESIS for the cause: the particle code reads a hardware timer, and any change of code timing moves it. |
| Player 1: camera numbers | **VERIFIED identical.** At a settled frame the camera object is byte-identical to the one-hero run except its target pointer, and view block 0 is byte-identical (all 0x90 bytes): v1-i-p2 against v1-i-solo, frame 4600. |
| Player 2: field of view, distance, height | **VERIFIED the same kind of camera:** field of view 1.047 rad (60 degrees) in both cameras and in the one-hero run; follow distance 600 in all three; aim point 170 above the hero's feet in both. Same stick moves on pad 2 (two views) and on pad 1 (one hero alone) give the same framing of the hero: `p2-solo-vs-twoview-5100.png` (left: one hero alone; right: player 2's picture; the room looks shifted because the twin stands 110 units beside the hero's start point). |
| Resolution | Layout 2: each picture is a full 512 x 448 display picture; horizontal scale 1.0; vertical 448/416, the game's own display stretch, as in the one-player game. Layout 1: horizontal 0.5, vertical 1.0, per half. |
| What is NOT the same | (1) Player 1's 3D picture passes through main memory at the PS2's own 512 x 416. With the emulator at native resolution that is exact; with the emulator's internal resolution raised, player 1's 3D stays at native sharpness while player 2's is drawn at the raised resolution. To make them equal: run at native internal resolution, or accept it; there is no free graphics memory to avoid the round trip. (2) Player 2's 3D world is one step (1/30 s) fresher than in the one-player game; player 1's has the original delay. (3) The HUD on player 2's picture is player 1's HUD until lane V2 changes it. (4) Particles: see above. |

## Fall back to one view: each case

| Case | Result |
|---|---|
| Room or moment without a twin | **PASS.** Layout 0 on the one-hero disc for the whole run (v1-j-solo-two); 0 until the twin exists and two steps after it is removed (all runs). |
| Cutscene / event camera | **PASS.** v1-k-hbf: mission intro 4426-4664 and mission end 6036-8710 in one full view (layout 0 two frames after the event takes the camera), two views again in the next room at 9558. Same in v1-r-long. |
| Full-screen menus | **PASS** for the main menu (START) and the save menu: byte 0 while open, 2 again two steps after closing; the menu is complete (v1-j-menu, `p1_f004800.png`). Its dim background is the last game picture. Shop and journal: NOT TESTED (HYPOTHESIS: same mechanism, the scene's draw tasks do not run). |
| Room loading / room change | **PASS** one way, three times: New Game jump, Hollow Bastion -> 100 Acre Wood after the mission (v1-k-hbf, v1-r-long), Twilight Town start (v1-q-coop). A round trip A -> B -> A: **NOT TESTED** (no ready script that walks both heroes through a door). |
| Game Over | **PASS.** v1-o-die (test line: first hit lethal): death event in one view, Game Over screen complete, byte 0. "Continue" back into play: NOT TESTED. |
| The game's own cross-fades | **NOT TESTED:** none occurred in any run (flags 0x0034C770/71 stayed 0). Built: ours is taken down first (hook 0x00161E38) and anything that removes the two-view tasks cleans up (hook 0x001623B0). |
| Glitches seen at the switches | Two views come back for 2 or 3 steps between the end of a death or mission event and the twin's removal (v1-k-hbf 6290-6296, v1-o-die 5262-5266). Cosmetic. |

## Cameras

- **Lock-on per player: PASS** (v1-j-lock, v1-f-lock): pad 2's R1 puts only player 2's camera into lock-on
  mode (type 0 -> 2), pad 1's R1 only player 1's; letting go likewise. In merged-v2 player 2's lock-on moved
  camera 1; that is gone, also in one view.
- **Each right stick turns its own camera: PASS** (v1-e-roam, v1-n-move).
- **Player 2 walks by camera 2: PASS** (v1-n-move): cameras turned 120 degrees opposite ways, both push the
  stick up: player 1 moved (+33.0, -55.4), player 2 (-33.3, -52.5): mirror images, each along its own view.
- **Event and special cameras.** While an event holds the camera (0x0033CC38 not 0) there is one view. Camera
  kinds set by scripts act on player 1's camera only; player 2's camera starts as a copy of player 1's (so it
  begins with the same kind, seen with kind 5 in 100 Acre Wood) and afterwards only changes through player
  2's own lock-on. First-person view and other kinds for player 2: NOT TESTED.

## Costs and limits

- **Pace at 100 % emulated CPU: held at 30 pictures per second** in every place measured (7 different pictures
  in 12 consecutive video frames, the same count as one view): Hollow Bastion fight with four fighters and
  enemies (v1-k-hbf, frames 5000-5011), Port Royal fight (v1-k-pr, 5200-5211), Twilight Town outdoors
  (v1-q-coop, 10000-10011). Slower emulated CPU settings were NOT measured for layout 2 (lane K measured the
  two 3D passes alone: held down to 60 %).
- **Sync:** every two-copy run stayed in sync; longest v1-r-long, 30,000 frames, 468 digests, seeded random
  buttons and both right sticks on both pads, fight, pauses, cutscene, room change; screenshot pairs identical.
- **One player alone:** the picture is the merged base's except the timer-driven particles (see above), so
  "byte-identical" as worded is NOT met; layout stays 0 and no two-view code runs.
- **Culling, shadows, effects:** each pass uses its own view for the world, the characters and the effects (the
  task list sets the other index for effects because the world list is drawn one pass late); scenery,
  characters, enemies, hit effects and shadows looked right in both pictures in three rooms. Not measured
  beyond the pixel comparison above.
- **Sound: NOT EXAMINED.** HYPOTHESIS: the listener stays with player 1's camera.
- **Known limits of the 2D doubling:** at most 27 redirected settings per packet chain and 600 chain tags;
  a HUD part that tests depth could be hidden where a 2D effect's texture was just loaded at page 320 (not
  seen); HUD parts that read the screen as a texture get their own picture.

## Layout 3 (alternate video frames): not built

Possible, but worse: the display would flip between the two players' pictures 30 times a second for anything
that is not a V3 emulator; and both pictures need their own video frame, so a step whose work takes longer
than one video frame would last three frames instead of two (20 pictures per second), where layout 2 holds 30.

## More room

0x000F6000-0x000F6FFF stays all zero without any patch: **VERIFIED**, 0 non-zero bytes in every sample (every
50 frames): v1-p-cave-coop (kh2-coop-v1.iso: boot, title, New Game opening, 9,000 frames) and v1-p-cave-hbf
(boot, New Game, fight, cutscene, room change, 9,000 frames).

## Hooks (22 words; none of them is a merged-v2 hook)

| Address | Was | Now | Purpose |
|---|---|---|---|
| 0x00140CC8, 0x00140CCC | camera task body | `j v_camtask`, nop | both cameras; decision one view / two views |
| 0x001403D4, 0x00140778, 0x0014E940, 0x001585F8, 0x00158DDC, 0x001590E8, 0x001594A0, 0x0015A5E4 | `jal 0x00167F18` | `jal v_pad` | camera code reads controller 2 for player 2's camera |
| 0x0019CA04, 0x0019CB00, 0x0019CC58, 0x0019D09C | lock-on manager -> camera calls | `jal` wrappers | player 2's lock-on acts on player 2's camera |
| 0x0017837C | `jal 0x00106A60` | `jal v_view` | the twin's stick is turned by camera 2 |
| 0x00161C7C | `j 0x00161AA8` | `j v_compose` | priority 90130: open the "both pictures" part (layout 1: draw the halves) |
| 0x002F3918, 0x002F391C | entry of "send packet chain" | `j v_dma`, nop | 2D into both pictures (not in the layout 1 patch) |
| 0x0014CFC0 | `j 0x0014E5F0` | `j v_send` | layout byte; display copy, marker, display copy |
| 0x001623B0, 0x001623B4 | entry of "remove two-view tasks" | `j v_dualoff`, nop | clean up when ours are removed |
| 0x00161E38 | `jal 0x001619E8` | `jal v_fade0` | the game's own cross-fade: ours down first |

## Tests (results in `local\tests\<name>\`)

| Test | What | Result |
|---|---|---|
| v1-h-one / v1-h-full | acceptance, player 1 | see above |
| v1-i-p2 (showp2 build) / v1-i-solo / v1-j-solo-two | acceptance, player 2; one hero alone | see above |
| v1-n-move | movement by own camera | PASS |
| v1-j-lock | lock-on per view, layout 2 | PASS |
| v1-j-menu | menus | PASS |
| v1-k-hbf | Hollow Bastion fight, events, room change, random buttons, 12,000 frames | PASS, 187 digests |
| v1-k-pr | Port Royal fight | PASS, 87 digests |
| v1-o-die | Game Over | PASS, 140 digests |
| v1-q-coop | New Game on kh2-coop-v1.iso, two Roxas, Twilight Town outdoors, 16,000 frames | PASS, 250 digests |
| v1-r-long | long random run with right sticks, 30,000 frames | PASS, 468 digests |
| v1-p-cave-coop, v1-p-cave-hbf | memory range zero without patch | PASS |

The runs named above used `patches\lane-v1-c` and `lane-v1-c-showp2`, whose patch words are identical to the
delivered `lane-v1-two-views` and `lane-v1-two-views-showp2` (compared line by line); v1-q-coop and v1-r-long
ran with the delivered folder.

## How to repeat

```
python -I tools\lane-v1\make_v1.py                         (delivered patch)
python -I tools\lane-v1\make_v1.py <outDir> sbs | showp2   (layout 1 patch | test build)
bash tools/lane-v1/vrun.sh <name> <disc> <frames> <speed> <snapFrames> 2 <p1script|-> <p2script|-> idle|random <patchDir|->
python -I tools\lane-v1\vsum.py local\tests\<name>\vprobe.txt       (layout byte and switches over time)
python -I tools\lane-v1\pngtool.py cmp a.png b.png --diff d.png     (pixel comparison)
```
Scripts: `tests\scripts\lane-v1\`. The two test discs of this lane (Hollow Bastion fight with friends and twin,
one hero alone) were deleted after use; they are the recipes `local\variants\m-test-m-hbf\built` and
`local\variants\m-test-m-solo\built` written onto the English text build 3 candidate with Kh2Tool inject.

## What remains

1. Lane V3: show the display at the marker on player 2's PC (nothing of layout 2 has run with such an emulator).
2. Lane V2: per-player HUD with the mask byte; lock-on ring and 3D-tied marks for player 2.
3. Not tested: the game's own cross-fade during two views, a room round trip, Continue after Game Over, shop
   and journal, other camera kinds for player 2, slower emulated CPU, sound, two real PCs.
4. The 2-3 step return of two views after a death or mission event.
