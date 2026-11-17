# Lane V2: a HUD for each player

Status 2026-11-10. Game: Kingdom Hearts II Final Mix, SLPM-66675, CRC F266B00B. Base: merged build v2
(`tools\merge\make_all.py --v2`), for two views plus lane V1's section (snapshot, see "Patches").
Evidence labels: VERIFIED (test folder under `local\tests\`, address, how) or HYPOTHESIS.

## 1. What is delivered, in short

| HUD part | One view (shared screen) | Two views (own screen) |
|---|---|---|
| Player 2's HP and MP | **Done.** Small gauge (face, HP ring, MP ring) for the twin, stacked on top of the friend gauges. | **Done.** Player 2's view has its own big gauge (HP, MP, Drive display) bottom right; each view also has the small gauge of the OTHER player. |
| "1P" / "2P" marker | **Done.** Over both heroes, in the game's own lettering. | **Done.** In both views, placed by each view's camera. |
| Command menu | Player 1's only (as before). | **Partly.** Each view shows its own player's menu (own cursor VERIFIED; sub-menus and shortcut list not tested apart). One menu object serves both players, see section 5. |
| Reaction Command prompt | Player 1's only. | **Done** as far as tested: the prompt appears only in the view of the hero who can use it. |
| Lock-on ring | Both rings (as before). | **Done.** Each view shows only its own player's ring, placed by that view's camera. |
| Marks on objects, numbers that pop up in the scene | As before. | **Done.** Shown in both views, placed by each view's camera. |
| Friend gauges, information texts (next level, munny), messages | As before. | **Done.** Shared: shown in both views. |
| Mission counters, timers, mini-map | As before. | Shared by the same rule; **not seen in a test** (no mission on the test discs). |
| START and the full-screen menus for player 2 | Not done. | Not done. What it takes: section 7. |
| Position and size after the view is stretched back | - | **Same as the one-player HUD** (measured, section 6). |

Layout 0 (one view) keeps the original single HUD plus the small gauge and the markers. One hero alone (no twin in
the room): the picture is byte-identical to merged build v2 (VERIFIED, section 8).

## 2. How the game draws its HUD (CRC F266B00B)

VERIFIED by reading the program (`local\analysis\v2\*.txt`, Ghidra copy `local\ghidra-v2`) and by memory dumps
(`tools\lane-v2\hudtasks.py`, dumps `local\analysis\v2\hudtasks_*.txt`).

- The field HUD is a "2D layer": manager 0 at 0x00347EA0 (manager n at 0x00347EA0 + n * 0x70; manager 1 is the
  layer of the full-screen menus). Current manager pointer: 0x00347F80.
  Manager: +0x00 its own task scheduler, +0x04 first object (next at object+4), +0x0C / +0x10 draw list (links at
  object+8), +0x14 owner (allocator: `(*[[owner]])(owner, size, 0)`), +0x20 world-to-screen matrix, +0x60 current object.
- Scene tasks of the HUD: priority 6010 `0x00139DE8` (select manager 0), **100000 `0x00139390` (run the HUD)**,
  103500 `0x001394C0` (remove dead objects). The HUD task builds the matrix from the CURRENT view's camera
  (`0x00139C90`), clears the draw list and runs the manager's scheduler (`0x001029E8`).
- Every HUD object has one task `0x00139200` in that scheduler: it calls the object's class method 1 (update) unless
  flag 0x20 is set, and appends the object to the draw list. The last task `0x00139308` calls class method 2 (draw)
  of every listed object without flags 0x02 / 0x40. So the HUD is drawn ONCE, after the scene, with player 1's data.
- Object: +0x00 class table, +0x0C flags (0x02 not drawn, 0x20 no update, 0x40 hidden, 0x100 paused, 0x800 has a
  parent), +0x10 group id, +0x14 its task. Group helpers: 0x001398D0 / 0x00139858 set / clear 0x02,
  0x00139B28 / 0x00139BA0 set / clear 0x100, 0x001399C0 / 0x00139948 hide / show.
- Classes (class table: update, draw): command menu display 0x00348590 (0x0013C938; pointer 0x003484A0; reads its
  control object from display+0x29C; groups 1, 2); **player gauge 0x0034A920** (0x3D00 bytes, constructor
  0x0031B130, set-up 0x001569D8, update 0x00157F08, refresh 0x00156E48, group 3); **friend gauge 0x0034A848**
  (0x15B0 bytes, constructor 0x0031B3B8, set-up 0x00154F30, update 0x001556F0, refresh 0x00155300, groups 4, 5);
  0x0034A820 (group 6); information bar 0x0034AF08 (group 0x12); marks over the scene 0x003486B0 + second part
  0x00347E18 (group 0x11; a pool of 9 at [0x003486A4], container [0x003486A0], taken with 0x0013E610(sequence));
  **number that pops up in the scene 0x0034AB80** (group 0xF; made by 0x0015B680); message queues 0x00347D70 / 0x0034A700.
- Gauges: root creation 0x0013D820 (pointers 0x003485E8..), tear-down 0x0013D9E0, "gauges off" 0x0013DB60
  (groups 3-6: flags 0x02 + 0x100), "gauges on" 0x0013DAF8. HUD party table 0x00348638 (3 objects + 3 flag words;
  slot 0 = player 1's hero), getter 0x0013DDA0. A gauge shows the unit slot of its character (object+0x48C:
  HP +0, max +4, MP +0x180, max +0x184).
- Objects fixed to a point of the scene (lock-on ring, reaction mark, pop-up number) keep the point at object+0x1A0;
  their update `0x001390F0` turns it into screen x / y / depth (object+0x170 / +0x174 / +0x1B0) with the manager's
  matrix (`0x0013A178`), calls class method 6 and takes one animation step (`0x00138840`).
- Lock-on: each hero has a lock-on object at hero+0xB40; its mark is at lock-on object+0x18 (0x0019D260).
- **What drew "1P" in lane K's demo picture** (`k-fight-ee0\p1_f005200.png`): VERIFIED it is the game's pop-up for
  experience points. 0x001B4198 (an enemy is defeated) computes the points and calls 0x0015B680(place, number):
  an object of class 0x0034AB80 with the digits of the number (sequences 6 + digit) and sequence 0x10, a small "P".
  For 1 point it reads "1P". It is not a player label. The markers of this lane reuse exactly this object
  (test v2-m3: numbers 1 and 2 give "1P" and "2P").

## 3. Two views: where the HUD has to be drawn

Lane V1's two-view mode draws the scene twice per step: first pass (scene tasks 6000-71000) with camera 2,
task 90000 (`0x00161A40` -> `0x0014E0D8`), second pass (90005-90110) with camera 1, task 90130 (`0x00161C70`) puts
the two view pictures on the screen. The HUD task at 100000 then drew ONE HUD across both halves.

VERIFIED (tests v2-p1-roam, v2-p3-poke, v2-p4-poke): running the HUD at the entry of task 90000 and again at the
entry of task 90130 puts one complete, full-size HUD into each view picture. **What is drawn at task 90000 lands in
player 1's picture (right half), what is drawn at task 90130 lands in player 2's picture (left half)** - the
opposite of the order of the two scene passes (found with different HP values for the two heroes; the reason was
not examined: HYPOTHESIS the 2D sprites travel in another draw list than the scene). Stable over consecutive
video frames (v2-p4-poke, frames 5000-5005).

Because each view picture is a complete 512 x 416 picture, the HUD in it has the original size and place by
construction; whatever lane V1 then does with the picture (squeeze to a half, show it full size, alternate
frames) is applied to scene and HUD together.

**Entry point for lane V1's other modes:** `pv_hud(a0)` in section "perview": "draw the complete field HUD of
player a0 (0 = player 1, 1 = player 2) into the picture that is being drawn now". The first call in a step updates
the shared HUD objects, later calls only draw them again; each call updates and draws that player's own objects
and places the scene marks with that player's camera (it sets the view index 0x0033CC40 to the player for the
duration). The two hooks in this patch are only the callers for today's side-by-side pipeline; for "full-size
views one after the other" or "alternate frames" call `pv_hud(player)` when that player's view is complete and
before the next view starts. Nothing in `pv_hud` knows about halves.

## 4. How each player's HUD is made (two views)

Every HUD object belongs to one of these kinds (by its group id, or by its update routine):

| Kind | Objects | Updated | Drawn |
|---|---|---|---|
| Player 1's own | group 3 (the game's player gauge), group 0x30 (small gauge of the twin) | in player 1's run | not in player 2's picture |
| Player 2's own | group 0x32 (second player gauge, bound to the twin), group 0x31 (small gauge of player 1's hero) | in player 2's run | only in player 2's picture |
| Command menu | groups 1, 2 | in every run, bound to that run's control object | every picture |
| Fixed to a point of the scene | update routine 0x001390F0, 0x0013E470 or 0x0015B578 | first run: normal; later runs: placed again only | every picture; the other player's lock-on ring is left out |
| Markers | group 0x35 | every run (placing only, no animation) | every picture |
| Shared (everything else) | friend gauges, information bar, messages, ... | first run of the step only | every picture |

In one view nothing changes: player 2's own objects are neither updated nor drawn, the rest runs as in the game.

- Player 2's big gauge is a second object of the game's player gauge class (same code, same layout file) with its
  own group. While it works, HUD party slot 0 answers "the twin" (`pv_party`), so it shows the twin's unit slot.
  It skips the game's "party changed" check (that check would use up player 1's change flags).
- The command menu display stays ONE object: before player 2's run display+0x29C is pointed at lane G's second
  control object S2 (0x000F1000, only if it is built: first word 0x00351260), after the run back to what it was.
- Lock-on rings: in a view picture the mark whose owner is the OTHER hero (hero+0xB40 -> +0x18, and its second
  part at mark+0x1C0) gets "not drawn".

## 5. Limits and open problems (two views)

1. **Command menu: one display object for two players.** VERIFIED: different cursor rows in the two views, stable
   over consecutive frames (v2-p5-roam, v2-f4-pv-roam). NOT tested: one player inside a sub-menu (Magic, Items,
   Drive) while the other is not, the L1 shortcut list, the open / close animations. HYPOTHESIS: when the two
   players' menus are in different states the menu's own animations restart in every run (they run twice per
   step anyway: at double speed). The clean fix is a second display object (constructor 0x0013B088, creation
   0x0013B348, module data around 0x003484A0); not done.
2. The menu's show / hide / fade state follows player 1's control object only (lane G's hooks at 0x001BDC64,
   0x001BDCA4, 0x001BDE30 skip S2; unchanged by this lane). If player 1's menu is hidden by the game, player 2's is too.
3. Player 2's big gauge shows the Drive display of the game's one Drive record (not examined further), and it does
   not get the game's "party changed" events (form change of the hero, etc.).
4. Hero and twin use the same face picture slot: HYPOTHESIS the face expression (normal / danger) of one gauge can
   show on the other. Not seen in the tests.
5. Scene tasks 91000-93000 (0x00160BD8, 0x001B9880, 0x001DE6D0, 0x001DDA78) still draw once over the finished
   two-view picture. Nothing wrong was seen in the test pictures; not examined.
6. In two-view steps the HUD is updated at priority 90000 / 90130 instead of 100000 (one step later relative to
   the four tasks above). No effect seen.
7. Three more update routines call the "fixed to a point" step (0x00229D68, 0x0022ACD0, 0x0022B5F0; not examined):
   objects of those classes are treated as shared, so in player 2's view they would sit at player 1's screen place.
8. Memory: the patch creates 2 small gauges, 1 player gauge and 2 markers per HUD (about 32 KB) from the HUD
   layer's allocator / the game's heap. No shortage seen in the tests; the limits were not measured.
9. Side-by-side fallback only: the HUD loses half of its horizontal sharpness like the scene (it is squeezed and
   stretched with the picture). Place and size are not affected (section 6).

## 6. Acceptance test: "each view must look like the one-player game"

Tool: `tools\lane-v2\hudmatch.ps1`. It stretches one half of a two-view picture back to full width and, for each
HUD rectangle, searches the shift (within 12 pixels) and the size factors (0.90 - 1.10) that agree best with the
one-view picture of the same moment (same buttons, same frame). "Same place and size" = best agreement at shift
0-2 pixels of the 1240 x 930 screenshot (1 screenshot pixel = 0.4 game pixel) and factor 1.00.

VERIFIED, final build (two-view run v2-f4-pv-roam against one-view run v2-f1-hud1-roam, same scripts
`tests\scripts\lane-v2\hud_p1.txt` / `hud_p2.txt`, two linked copies each; reports `v2-f4-pv-roam\match_*.txt`,
pictures `v2-f4-pv-roam\sheet_<frame>_<side>.png` = reference on top, stretched view below):

| Frame | View | Command menu (30,640 330x270) | Big gauge (880,690 360x220) | Small gauge (1090,600 130x120) |
|---|---|---|---|---|
| 4700 | player 1 (right half) | shift 1 / 0 px, factor 1.00 / 1.00: SAME | shift 1 / 0, 1.00 / 1.00: SAME | shift 1 / 0, 1.00 / 1.00: SAME |
| 4700 | player 2 (left half) | SAME (1 / 0, 1.00 / 1.00) | SAME (1 / 0, 1.00 / 1.00) | SAME (1 / 0, 1.00 / 1.00) |
| 5000 | player 1 | SAME (1 / 0, 1.00 / 1.00) | SAME (1 / 0, 1.00 / 1.00) | SAME (1 / 0, 1.00 / 1.00) |
| 5000 | player 2 (cursor on another row) | SAME (1 / 0, 1.00 / 1.00) | SAME (1 / 0, 1.00 / 1.00) | SAME (1 / 0, 1.00 / 1.00) |

The constant 1-pixel shift is 0.4 game pixel: the rounding of squeezing 512 columns into 256 and back. The same
numbers came out of the earlier pair v2-a1-two / v2-a1-ref. So for both players the menu sits bottom left and the
gauge bottom right at the original size; nothing is doubled; nothing lies across the two halves.

Controls (v2-a1): the two-view picture NOT stretched gives "DIFFERENT" for all three rectangles; the reference
against itself gives difference 0.00.

HUD parts that cannot match exactly, and why:
- The small gauge of the other player is an addition (the one-player HUD has no such gauge).
- The markers are an addition.
- Horizontal sharpness in the side-by-side fallback (see 5.9). Gone in a full-size view mode.
- Not compared because the test discs do not show them: mission counters, timers, mini-map, sub-menus.

## 7. START and the full-screen menus for player 2 (step 6: analysis only)

- VERIFIED (lane G, lane A): only controller 1's START opens the main menu; 43 places call the controller getter
  0x00167F18, all menu screens found pass index 0 (examples read here: 0x0027F9D8 list screen, 0x00284FD8).
- The place that tests START in the field was NOT found (`tools\lane-v2\padscan.py`: the only two START tests
  near a getter call are inside open menus). HYPOTHESIS: it goes through the pause routine with another getter.
- What it takes: (1) find that test and accept controller 2 as well, remembering who opened the menu;
  (2) while the menu is open, answer the getter calls that come from the menu code (0x0027xxxx-0x0029xxxx, by
  return address) with the opener's controller: about 20 instructions in one hook; (3) nothing for the content:
  items, munny and (by the user's decision) equipment and abilities are shared; (4) the picture: lane V1 already
  falls back to one view while a full-screen menu is open; the game is paused for both players.
  Estimate: small once (1) is found; not done in this lane.

## 8. Tests

All folders are under `local\tests\`. "2 copies" = two linked emulator copies (digests compared by the harness);
memory WRITES were used only in one-copy tests. Final builds = the patch folders of section 9 as they are now.

### 8.1 Final builds

| Test | Build, disc, what | Result |
|---|---|---|
| v2-f1-hud1-roam (2 copies) | `lane-v2-hud1`, test-m-roam, player 2 walks and moves the menu cursor | **In sync** (87 digests). `p1_f005000.png`: "1P" over player 1's hero, "2P" over the twin, small twin gauge above the player gauge. |
| v2-f2-hud1-hbf (2 copies) | `lane-v2-hud1`, Hollow Bastion fight with Donald and Goofy, random buttons on both pads, 9000 frames | **In sync** (140 digests). Gauge stacks above Goofy and Donald; an event removes and rebuilds the HUD without fault. |
| v2-f9-hud1-roam-long (2 copies) | `lane-v2-hud1`, test-m-roam, random buttons on both pads, 14000 frames | **In sync** (218 digests). |
| v2-f3-hud1-solo (1 copy) | `lane-v2-hud1`, disc without twin | Screenshots 4700 / 5000 / 5300 **byte-identical** to merged-v2 (v2-s1-merged-v2) and to the unpatched game (v2-s0-nopatch). 0 patch words changed in memory. |
| v2-f4-pv-roam (2 copies) | `lane-v2-perview`, test-m-roam, same scripts as f1 | **In sync** (87). Each half: own menu cursor, own big gauge, other player's small gauge, markers. Acceptance numbers in section 6. |
| v2-f5-pv-fight (2 copies) | `lane-v2-perview`, test-m-fight, both players lock on (R1) and attack | **In sync** (95). `p1_f005200.png`: one lock-on ring per view (different targets), markers placed per camera, player 2's cursor on row 2. |
| v2-f6-pv-hbf (2 copies) | `lane-v2-perview`, Hollow Bastion fight, random buttons, 9000 frames | **In sync** (140). Friend gauges and information texts in both views. |
| v2-f8-pv-roam-long (2 copies) | `lane-v2-perview`, test-m-roam, random buttons on both pads, 14000 frames | **In sync** (218). |
| v2-f7-pv-solo (1 copy) | `lane-v2-perview`, disc without twin | Screenshots **byte-identical** to merged-v2. 0 patch words changed in memory. |

Pace (the harness log prints the game's own frames per second every 10 s; at test speed 3 the original 30 per
second reads 89.9): one view (f2, f9): 89.9 in play. Two views (f6, f8): 89.9 in most samples, but one sample of
55.9 (f6, fight) and one of 75.0 (f8). **So in two views the game's own rate dipped at times.** Not separated:
how much is lane V1's second scene pass and how much the second HUD run (no run with lane V1's section alone was
made here). One view: no change against merged-v2 seen.

### 8.2 Earlier tests that carry a finding

| Test | What | Result |
|---|---|---|
| v2-party1 (1 copy, write) | twin put into HUD party slot 1 | the game's friend gauge shows the twin: the gauge code works for the twin's unit slot |
| v2-g1-roam (2 copies), v2-h1-hbf (2 copies, random, 9000) | `lane-v2-p2gauge` | in sync (81, 140 digests); gauge above the friend gauges; HUD tear-down in an event without fault |
| v2-g6-poke, v2-g2/g3-poke (1 copy, write) | twin HP 20 -> 7, MP 100 -> 40 | the small gauge's HP and MP arcs shrink, player 1's gauge does not change |
| v2-p1-roam (2 copies) | HUD run at tasks 90000 and 90130 | first proof: a complete full-size HUD in each view picture |
| v2-p3-poke, v2-p4-poke (1 copy, write) | twin HP 7, MP 40 in two views | which picture each run lands in (section 3); after the swap: left view = twin's values in the big gauge, right view = hero's; stable over frames 5000-5005 |
| v2-p5-roam (2 copies) | player 2 presses Down, Down, Up | `cropL.png` / `cropR.png`: the cursor moves only in the left (player 2) view; in sync |
| v2-p7-fight (2 copies) | both players lock on | one ring per view (before the rule both rings were in both views: v2-p6-fight) |
| v2-p8-hbf (2 copies, random) | two views with Donald and Goofy | in sync (140); `p1_f005200.png` both views complete; `p1_f005800.png` one view = one-view HUD |
| v2-a1-two / v2-a1-ref (2 copies each) | first acceptance comparison | same numbers as section 6; "Save" prompt only in the view of the hero on the save point (`sheet_5000_L.png`) |
| v2-m3-k1 / k8 / k24 (1 copy, write of the test knob) | marker after 1, 8, 24 animation steps | `v2-m3-sheet\crop.png`: "1P" / "2P" visible in all three; 1 step sits closest to the head (chosen) |
| v2-s0-nopatch (1 copy, no patch) | memory 0x000F7000-0x000F7FFF | all zero at frames 600, 3000, 4700, 5000, 5300 |
| v2-L*, v2-L2* | long random fight on test-m-fight | STALLED, also on merged-v2 alone: see section 10.1 |

### 8.3 Evidence per HUD part

| Part | State | Evidence | Where it is drawn / takes its data |
|---|---|---|---|
| Interim one-view gauge for player 2 | done | v2-f1, v2-f2, v2-f9, v2-g6-poke | friend gauge class 0x0034A848 with update `tg_update`; character through party getter slot 3 = [0x000F05CC]; unit slot via object+0x48C |
| 1P / 2P marker | done | v2-f1 `p1_f005000.png`, v2-f5 `p1_f005200.png`, v2-m3 | class 0x0034AB80 built as in 0x0015B680 (0x0015B368(obj, 0x10, [0x003486A0]+0x20, number)); point = hero+0x70 with y - 170; screen place by 0x0013A178 |
| HP / MP gauge per view | done | v2-p4-poke, v2-f4, v2-f6 | second object of class 0x0034A920 (set-up 0x001569D8 entered at 0x001569E8 with group base 0x2F, update entered at 0x00157F1C, refresh 0x00156E48 with party slot 0 = twin) |
| Drive gauge per view | partly | seen in every two-view picture ("DRIVE MAX 3" in both views) | part of the player gauge object (sub-updates 0x001578D8, 0x00157A00, 0x00157AE0, ...); which record the Drive value comes from was not examined |
| Command menu per view | partly | v2-p5-roam, v2-f4, v2-f5 (cursor); sub-menus not tested | display [0x003484A0] (class 0x00348590, update 0x0013C938, 9 item objects class 0x003485B0), control object at display+0x29C: S = 0x01C5F530, S2 = 0x000F1000 |
| Reaction Command prompt per view | done as far as tested | v2-a1-two `sheet_5000_L.png` / `sheet_5000_R.png`, v2-f4 | drawn by the command menu display from its control object (lane G: +0xA1E) |
| Lock-on ring per view | done | v2-p7-fight, v2-f5 | mark = [[hero+0xB40]+0x18], pool object class 0x003486B0 (sequences 1 / 5 / 0x17 / 0x1B, second part 0x14); target chooser marks 3 / 0x19 from 0x0011AC10 are not filtered |
| Marks on objects, pop-up numbers | done | v2-f5 (rings and markers per camera); pop-up numbers by the same rule, not seen in a picture | 0x0019D5F8 -> 0x0019D588 (reaction mark, sequence table 0x0036D3B4), 0x001B4198 -> 0x0015B680 (experience points) |
| Information texts, friend gauges | done (shared) | v2-p8-hbf `p1_f005200.png`, v2-f6 | information bar class 0x0034AF08 (group 0x12), message queues 0x00347D70 / 0x0034A700, number displays 0x00348658 / 0x00348678 |
| Mini-map, mission counters, timers | not tested | - | not located; shared by default (updated once, drawn in both views) |
| START and full-screen menus for player 2 | not started (analysis in section 7) | - | menu screens call 0x00167F18(0); examples 0x0027F9D8, 0x00284FD8 |

### 8.4 Safe to merge now, and next steps

**Safe to merge now for the first human test on the shared screen: `patches\lane-v2-hud1`** (merged-v2 + p2gauge
+ marker; 312 words in 0x000F7000-0x000F74FF, 7 hook words at 5 places, all inside the HUD's gauge routines; no
hook of merged-v2 or lane G is changed). Two-copy sync runs: v2-f1, v2-f2 (random, 9000 frames), v2-f9 (random,
14000 frames); one hero alone: picture identical to merged-v2. If the markers are not wanted: `lane-v2-p2gauge`.
To merge: add sections `p2gauge` and `marker` of `tools\lane-v2\make_v2.py` (they only need lane E's twin pointer
0x000F05CC).

`patches\lane-v2-perview` is a working state for own screens, not final: merge it only together with lane V1's
final mode.

Next steps for the per-view HUD (full-size views are the target):
1. When lane V1 delivers its mode: call `pv_hud(0)` when player 1's view is complete and `pv_hud(1)` when player
   2's is, and remove the two caller hooks at 0x00161A40 / 0x00161C70 if those tasks are no longer used. First
   check in which picture a HUD run lands in the new mode (the test of section 3: give the heroes different HP).
2. Rebuild with lane V1's current generator instead of the snapshot `v1_views.py`.
3. Command menu: test sub-menus, shortcut list and open / close animation with the two players in different
   states; if they disturb each other, make a second display object (section 5.1) and give S2 its own show /
   hide / fade (lane G's three hooks).
4. Measure the pace cost of the second HUD run alone (a run with lane V1's section only against `lane-v2-perview`).
5. Decide the Drive display for player 2 (section 5.3) and the face picture slot (5.4).
6. Check a mission with counter / timer and a room with a mini-map in two views; check the three unexamined
   "fixed to a point" classes (5.7) and the four scene tasks that draw after the two pictures (5.5).
7. START for player 2 (section 7).

## 9. Patches, files, hooks

Generator: `python -I tools\lane-v2\make_v2.py <outDir> [p2gauge] [marker] [views] [perview]` (imports
`tools\merge\make_all.py`; for `views` it imports `tools\lane-v2\v1_views.py`, a COPY of lane V1's
`tools\lane-v1\make_v1.py` taken 2026-11-10 16:23 - **the final merge must take lane V1's current file**).
Every output folder has `SLPM-66675_F266B00B.pnach` and `listing.txt` (every word with its meaning).

| Folder | Sections | Use |
|---|---|---|
| `patches\lane-v2-hud1` | merged-v2 + p2gauge + marker | **shared screen (first human test): gauge of player 2 and markers** |
| `patches\lane-v2-p2gauge` | merged-v2 + p2gauge | the gauge alone (fallback if the markers are not wanted) |
| `patches\lane-v2-perview` | merged-v2 + lane V1 views + p2gauge + marker + perview | own screens: a HUD per player |

Memory of this lane: 0x000F7000-0x000F7FFF. p2gauge 0x000F7000-0x000F721F, marker 0x000F7240-0x000F74FF, perview
0x000F7500-0x000F7B93, variables 0x000F7F00-0x000F7F33 (zero at boot, never written by the patch file; 0x000F7F30 is a test knob for the markers and must stay 0).
VERIFIED all zero in an unpatched run (v2-s0-nopatch, 5 checkpoints from boot to play) and unchanged by the game
while a patch runs (v2-s1-*, v2-f3, v2-f7: 0 words differ).

Hook sites (words changed in the game program). "o" = in `lane-v2-hud1`, "t" = in `lane-v2-perview`:

| Address | Was | Now | In | Purpose |
|---|---|---|---|---|
| 0x0013D9D8 | `j 0x0013DB60` | `j tg_create` (t: `j pv_create`) | o t | end of the HUD's gauge creation: make our gauges |
| 0x0013D9E0, E4 | `addiu sp,sp,-16` / `sd s0,0(sp)` | `j mk_destroy` (t: `j pv_destroy`) / `nop` | o t | HUD gauges destroyed: destroy ours first |
| 0x0013DBA8 | `j 0x00139B28` | `j mk_pause` (t: `j pv_pause`) | o t | tail of "gauges off": also our groups |
| 0x0013DB50 | `j 0x00139BA0` | `j mk_resume` (t: `j pv_resume`) | o t | tail of "gauges on": also our groups; makes the markers the first time |
| 0x0013DDA0, A4 | `addiu sp,sp,-16` / `daddu a1,a0,zero` | `j tg_party` (t: `j pv_party`) / `nop` | o t | HUD party getter: slot 3 = twin (t: slot 4 = hero, slot 0 = twin for player 2's gauge) |
| 0x00161A40, 44 | `addiu sp,sp,-16` / `sd ra,0(sp)` | `j pv_first` / `nop` | t | two-view task 90000: player 1's HUD |
| 0x00161C70, 74 | `addiu sp,sp,-16` / `sd ra,0(sp)` | `j pv_second` / `nop` | t | two-view task 90130: player 2's HUD (lane V1's hook at 0x00161C7C is untouched and still reached) |
| 0x00139390, 94 | `addiu sp,sp,-16` / `lui t7,0x34` | `j pv_mgr` / `nop` | t | HUD task: nothing to do when the HUD went into the view pictures |
| 0x001393D8 | `j 0x00139DC0` | `j pv_end` | t | HUD task removed: forget the HUD |
| 0x0013921C, 20 | `lw t7,12(s0)` / `andi t7,t7,0x20` | `jal pv_ufilter` / `nop` | t | which objects are updated in this run |
| 0x0013935C, 60 | `lw t7,12(a0)` / `andi t6,t7,0x40` | `jal pv_filter` / `daddu a1,s1,zero` | t | which objects are drawn into this picture |

Existing hooks of other lanes: none changed. Lane G's four menu hooks (0x0013B258, 0x001BDC64, 0x001BDCA4,
0x001BDE30) are left as they are; the per-view menu works by writing display+0x29C directly around player 2's run.
Lane V1's hooks are all kept.

Tools of this lane (`tools\lane-v2\`): `make_v2.py`, `v1_views.py` (copy), `vrun.sh` / `vrun_guard.sh` (test
runner; the guard stops a stalled session), `final_batch.sh`, `hudmatch.ps1` (section 6), `cave_v2.py` (memory
range check), `poke.py` (memory writes / reads at screenshot frames; writes only in ONE-copy tests),
`hudtasks.py`, `padscan.py`, `crop.ps1`, `disw.py`, `words.py`, `gh.sh`. Test scripts: `tests\scripts\lane-v2\`.
Discs of this lane were DELETED at the end (4.3 GB each). To rebuild one: `Kh2Tool inject` from
`local\iso\English text build3 (candidate).iso` with the room files of the recipe folder (the command line is in
`tools\merge\build_disc_m.py`): `test-v2-hbf.iso` = `local\variants\m-test-m-hbf\built` (Hollow Bastion fight with
Donald, Goofy and twins), `test-v2-solo.iso` = `local\variants\m-test-m-solo\built` (no twin).
Left on disk: the three patch folders, `tools\lane-v2\`, `tests\scripts\lane-v2\`, `local\analysis\v2\`,
`local\ghidra-v2`, `local\run-v2` (emulator copies, 338 MB), test folders `local\tests\v2-*`. No emulator of this
lane is running.

## 10. Found on the way (for other lanes)

1. **A session stalls on the merged build itself.** `test-m-fight.iso`, two copies, scripts
   `merge\fight_idle_p1.txt` / `merge\idle_p2.txt`, then random buttons, speed 3: both emulator copies stop
   computing (0 % CPU, no log line) shortly after frame 7150, in sync until then. Same with `patches\merged-v2`
   alone (v2-L2-merged-v2), with the gauge patch (v2-L2-lane-v2-p2gauge) and with a memory probe attached
   (v2-L-lane-v2-p2gauge). At frame 7000 player 1's hero is at critical HP. Not caused by this lane; not analysed.
2. **Player 1's lock-on can take the twin as its target.** v2-p7-fight / v2-f5-pv-fight: R1 at frame 4800 on the
   fight disc; in player 1's view the ring sits on the other Sora (frame 5080).
3. Lane V1's two views go back to one view during parts of the Hollow Bastion fight (v2-p8-hbf frame 5800);
   the HUD then is the one-view HUD, as intended.
