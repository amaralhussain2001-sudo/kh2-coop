# Lane S3: the Gummi Ship with two players (study)

Task: examine the Gummi Ship mode and answer, with evidence, what two simultaneous, directly controlled players
would look like there and whether it is feasible.

Status 2026-11-10: STUDY FINISHED. Nothing of this lane is in the merged build. The patches here are TEST ONLY.

Evidence labels: **VERIFIED** = seen in a test or read in the code/data of this disc. **HYPOTHESIS** = a reasoned
guess, not tested. **FROM MEMORY** = general knowledge of the game, not checked here.
All tests ran on ONE PC with scripted buttons (no human played). "2 copies" = two linked emulator copies in a
lockstep session, the host comparing a memory digest every 64 frames.

---

## 1. THE ANSWER

**Feasible: yes. The right form is a second, complete player ship flown by controller 2** (option (a)).
A test patch already does the core of it:

| What | Result | Label |
|---|---|---|
| A second full player-ship object is built at mission start, on controller 2 | works | VERIFIED (s3-e1, s3-e3) |
| Each pad moves only its own ship (own place on the flight path) | pad 1: ship 1 to (180,-140); pad 2: ship 2 to (-180,140) | VERIFIED (s3-e3) |
| Ship 2's shots destroy enemies and add to the score | score 2 -> 838, kills 0 -> 4, starting the moment pad 2 began to fire; pad 1 never fired | VERIFIED (s3-e3) |
| A whole mission with both ships weaving and firing ends normally | "Asteroid Sweep" level 1: score 73,500, 220 kills, medal value 2, back to the world map | VERIFIED (s3-e6b) |
| The two copies stay in sync | 156 / 203 / 468 / 624 digests compared in the 2-copy tests, never a difference | VERIFIED (all 2-copy tests) |

**What the test patch does NOT give yet** (each is real work, see section 7):

| Gap | Evidence | Label |
|---|---|---|
| Ship 2 takes no damage at all | ship 1's hull 177 -> 7, ship 2 stays 177, both apart (s3-e4) and at the same spot (s3-e5) | VERIFIED |
| The mission fails when ship 1 is destroyed, even with ship 2 at full hull | s3-e6: ship 1 hull 0, mission failed, ship 2 hull 177 | VERIFIED |
| Ship 2's "alive / finished / destroyed" state is copied from ship 1 in the test patch | by design of the test patch | VERIFIED |
| Score, kill count, medals, the one hull gauge on screen: one set, for ship 1 | one set of counters in the module | VERIFIED |
| View direction (L1/R1), lock-on, special weapons, pickups, Teeny Ships: built around ONE "player ship" pointer with 132 users in the code | static count in the module | VERIFIED (count), effects on ship 2 not tested |
| Enemies aim at ship 2? | not determined | - |
| World map and Gummi Menu / Garage: one cursor, controller 1 | section 6 | VERIFIED |

**How sure:** the principle is proven (own controller, own position, own working weapons, full mission, in sync).
The gaps are all of one kind: the module was written for exactly one player ship and keeps "the player ship" in
one global pointer. None of the gaps looks like a wall, but only the first four rows above have been measured;
the rest is HYPOTHESIS until tried.

**Cost (ESTIMATE):** a lane of its own, about the size of the twin's "own HP + own targeting" work in the field
mode. Almost nothing of the field-mode twin carries over (different code module, different object classes); only
the controller path and the test tools do. The Gummi Ship is roughly 9 routes x 3 levels of the same module, so
the work is in the module once, then test runs per route.

**Options (b) and (c) in one line each:** Teeny Ships as player 2's craft would be a lesser role (small helper
ships with no controller of their own, only present if the blueprint carries them): not recommended.
No other "real role" (gunner, view control) is better than a second ship, and each would break the rule that
player 2 gets an equivalent craft.

---

## 2. How the mode is built

All VERIFIED from the disc data (`local\extract\kh2`) and the code, unless marked.

- **A separate code module.** The Gummi flight is not part of the main program. It is `ovl_gumibattle.x` (444 KB,
  raw MIPS code) inside OVL.IMG, loaded at **0x01F18000** when a mission starts and removed afterwards. The Gummi
  Menu and Garage are a second module, `ovl_gumimenu.x`, loaded at the same address. Only one of them is in
  memory at a time. Test for "which one is loaded": the low 16 bits of the word at 0x01F18014
  (0x636A = flight, 0x62B0 = menu).
- **Game mode word** 0x0032BA24: 1 / 5 / 6 = field, **2 = Gummi flight**, 3 = Gummi Menu, 4 = other.
- **Gummi flight task** in the main program: record at 0x0032BA48 (start routine 0x00103F68 loads the module and
  gives it its own heap of 0xCE0000 bytes, end routine 0x00104018, state word at 0x0032BA64).
- **Own object table.** The flight does not use the field mode's object list. It has `50gumientry.bin`
  (277 entries: 128 ship blocks G_BL*, enemies G_EX2xx / G_EX3xx, bosses, menu objects).
- **Mission data** in `gumibattle\` (108 files): 9 route maps gm00..gm08, each with three scripts
  (`a` / `b` / `c` `.gbx`; HYPOTHESIS: mission levels 1 / 2 / 3), plus tables `playerparam.bin`, `enemyparam.bin`,
  `missileparam.bin`, `lockonparam.bin`, `tinyset.bin` (Teeny Ships), `planset.bin` (blueprints), `rank.bin`,
  `treasure.bin`, `item.bin`, `systemparam.bin`, `abilityparam.bin`.
- **The player ship** is one object of 0x1440 bytes, built by the constructor 0x01F1E4A8(object, controller,
  position, rotation), called from 0x01F21C4C..0x01F21CD4. Fields found:

  | Offset | Meaning | Label |
  |---|---|---|
  | +0x4A4 | pointer to the controller this ship reads | VERIFIED |
  | +0x4AC | hull HP (float, 177 at the start with the default ship) | VERIFIED |
  | +0x50C | state: 1 = flying in, 2 = under control, 3 = mission done, 4 = destroyed | VERIFIED |
  | +0xA0 | world position (follows the flight path) | VERIFIED |

- **The ship does not own its position.** It flies on a fixed path ("rail"). One shared flight-controller object
  at 0x01F7DE60 holds the player's offset from the path (+0x80, address 0x01F7DEE0), the view direction turned
  with L1/R1 (+0x94) and flags (+0x9C). The stick moves this ONE offset; the ship is drawn at path + offset.
- **"The player ship" is one global pointer**, 0x01F7DE44, used at 132 places in the module (among them
  targeting, HUD, camera, Teeny Ships and the fire handler; the places were counted, not all read).
- **Counters:** score 0x01F8039C, kills 0x01F80856 (16 bit), medal value 0x01F803C0.
- **Teeny Ships:** objects of 0x4E0 bytes, built by 0x01F27740(object, position, rotation, index 0 / 1), only when
  the blueprint has them. They have no controller pointer. They read the player ship's status and fire when it
  fires.

How a mission is started (VERIFIED by following the code and by test s3-launch01):
route symbol on the world map -> 0x002C5418(route 0..8) -> thread 0x002C53C8 -> Gummi Menu module
(Start / Gummi Editor / World Map, then Gummiship Select) -> Gummi flight task -> back to the world map.

---

## 3. How to reach it for tests

A fresh save shows no Gummi routes on the world map (tried map programs 0 and 1: tests s3-wm03-prog0/-prog1;
only Twilight Town and Hollow Bastion show, VERIFIED). Routes need story flags. So the tests use a shortcut:

1. **Disc** `local\iso\test-s3-wm.iso` (deleted at the end of the lane; recipe kept in `local\variants\s3-wm`):
   New Game jumps straight to the world map (world WM, area 0). Built with `Kh2Tool patch` + `inject` from the
   English text build.
2. **Launcher patch** (part of every `patches\lane-s3-*` test patch except `-wmprog1` and `-count`): when the
   world-map cursor is built (0x002C5F08), it calls 0x002C5418 once with route 0. TEST ONLY: it starts the route
   by itself.
3. **Buttons:** New Game with Circle x6 (frames 3000-3600), then Circle at 5000, 5300, ... 7100 walks through the
   Gummi Menu (Start, ship select, confirm).

Timeline (VERIFIED, s3-gm01 and later): flight module loaded at about frame 6100, ship under control from about
frame 7540. The Gummi Menu module is loaded about 1800-1900 frames before the flight module (from the probe
times). Route 0 is "Asteroid Sweep" (name read in the screenshots of s3-e6b).

Repeat the two-ship demo:

```
python -I tools\lane-s3\make_s3.py lane-s3-e3-ship2own launch route=0 delay=1 ovl:ship2 ovl:ship2own
python -I tools\kh2_session.py run s3-e3 --iso local\iso\test-s3-wm.iso --players 2 --slots 0,1 --frames 10000
   --speed 2 --script tests\scripts\lane-s3\gb_p1.txt --script2 tests\scripts\lane-s3\gb_p2.txt --then idle
   --patch-dir patches\lane-s3-e3-ship2own --fresh-card --run-dir run-s3 --port 29850 --pine 28161
python -I tools\lane-s3\s3_ships.py 28161 48          (alongside: prints both ships' pad, state, offset, score)
```

---

## 4. The controller

- The flight asks the main program for a controller with GetLogicalController(index) at 0x00167F18
  (pad 1 = index 0 = 0x0034D6C0, pad 2 = index 1 = 0x0034D720). The flight module has 6 such call sites; all pass
  index 0. VERIFIED (static).
- The call that matters is 0x01F21C48: its result is handed to the ship constructor, which stores it at
  ship + 0x4A4. The ship's own routines (move, fire, view) read the pad through that pointer. VERIFIED.
- **Test s3-e0:** one changed instruction (0x01F21C4C: index 1 instead of 0). The ship then obeys pad 2 only;
  the probe shows ship + 0x4A4 = 0x0034D720 in every sample. 2 copies, 156 digests, in sync. VERIFIED.
- So logical controller 2 can drive a player ship with no other change. The pad path of the merged build already
  delivers player 2's buttons to 0x0034D720 in this mode.

---

## 5. Experiments

Patches are in `patches\lane-s3-<name>\`, logs in `local\analysis\lane-s3\`, pictures in `local\tests\<id>\`.

| Id | Copies | What was tried | Result | Label |
|---|---|---|---|---|
| s3-wm01, s3-wm02 | 1 | World map from a new save; move the cursor with the stick | World map reached; one cursor object (0x03A1, 0xBE0 bytes) moving about 29 units per frame; "Land" prompt on a world | VERIFIED |
| s3-wm03-prog0 / -prog1 | 1 | World-map programs 0 and 1; fly to where route symbols should be | No route symbols on a fresh save in either program | VERIFIED (negative) |
| s3-count01 | 1 | Count calls of the 6 world-map controller fetch sites | Only 0x002C5F08 runs, once, when the cursor is built; none runs per frame (the cursor keeps the pointer) | VERIFIED |
| s3-launch01 | 1 | Launcher patch: call 0x002C5418(0) from the cursor's construction | Gummi Menu opens for route 0 | VERIFIED |
| s3-gm01 | 1 | Circle through the Gummi Menu | Flight module loads, mode 2, ship under control | VERIFIED |
| s3-e0 | 2 | Ship constructor gets controller 2 instead of 1 | Ship obeys pad 2 only; 156 digests in sync | VERIFIED |
| s3-e1 | 2 | Build a second player ship (same constructor, controller 2) right after the first | Second ship exists and is drawn, but is not "live": its state never advances, and both ships sit at the same place; 156 digests in sync | VERIFIED (partial failure, explained by section 2) |
| s3-e2 | 2 | Make ship 2 live: copy ship 1's state into it each step; fire routine also for ship 2 | Ship 2 is live, but BOTH pads move the SAME shared offset, so the ships cannot separate; 156 digests in sync | VERIFIED (partial failure) |
| **s3-e3** | 2 | Give ship 2 its own offset: exchange the shared offset with ship 2's private copy around ship 2's update | **Works.** Pad 1 right+up: ship 1 to (180,-140). Pad 2 left+down: ship 2 to (-180,140). Ships visibly apart (`local\tests\s3-e3\sheet.png`). Pad 2 fires alone: score 2 -> 838, kills 0 -> 4. 156 digests in sync | VERIFIED |
| s3-e4 | 2 | Nobody fires; ship 2 held to the left, ship 1 in the middle; dump both ship objects every 1.5 s | Hull HP found at +0x4AC. Ship 1: 177 -> 7. Ship 2: 177 all the time. 203 digests in sync | VERIFIED |
| s3-e5 | 2 | Same, both ships at the same spot | Same result: ship 1 177 -> 7, ship 2 177. So ship 2 is not hit even where ship 1 is hit | VERIFIED |
| s3-e6 | 2 | Whole mission, both pads HOLD Circle and weave | Holding the button did not keep firing: score 0. Ship 1's hull reached 0 (state 4), mission failed, ship 2 at 177. 468 digests in sync | VERIFIED (the hold-to-fire reason is HYPOTHESIS: fire is on press; a setting routine 0x01F21258 was not examined) |
| **s3-e6b** | 2 | Whole mission, both pads TAP Circle (5 frames every 10) and weave, 40,000 frames at speed 4 | **Mission completed:** score 73,500, kills 220, medal value 2, ship state 3, task ends, mode back to 1, world map shows the "Asteroid Sweep" panel. Ship 1 hull ends at 70, ship 2 at 177. 624 digests in sync; screenshots of both copies identical at 5 points; unused part of the cave all zero in 674 checks | VERIFIED |

Side observations (VERIFIED in the logs, cause HYPOTHESIS):
- In s3-e3, after the stick was released, ship 1's vertical offset drifted back from -140 to -40, ship 2's stayed
  at 140. Something outside the ship update also adjusts the shared offset (path limits or re-centring). A full
  version must give ship 2 the same treatment.
- Both ships have the same hull value (177): ship 2 is built from the same selected blueprint as ship 1.
- Not run: `ovl:pad1` (all 6 fetch sites to controller 2). s3-e0 made it unnecessary.

---

## 6. World map and Gummi Menu / Garage (facts only)

- **World map** (`ard\wm00.ard`): map programs 0x00-0x0D and 0x19, all `Mission 0xC "WORLDMAP"`. Arrival points
  `m_00` / `m_01` with the cursor WM_CURSOR (0x03A1); world symbols in `m_50`; nine route symbols WM_GUMI_01
  (0x03AE, argument 1..9) in `m_51`. VERIFIED.
- **One cursor ship**, built at 0x002C5F08 with GetLogicalController(0); it stores the pad pointer. Controller 2
  does nothing there. VERIFIED (s3-count01, s3-wm02).
- **Gummi Menu / Editor** (`ovl_gumimenu.x`): 35 controller fetch sites; 29 confirmed as index 0, 6 not decided by
  the simple pattern search. A single-cursor menu. VERIFIED (static only).
- Both are menu-like, one-cursor screens, the same kind as the pause menu. What player 2 should do there is a
  design decision for the plan, not examined here.

---

## 7. Options compared, and what a full version needs

### Options

| Option | What player 2 gets | Evidence | Verdict |
|---|---|---|---|
| **(a) second player ship** | The same craft as player 1: own stick, own position, own guns | Demonstrated (s3-e3, s3-e6b) | **Recommended.** The only option that meets "equivalent, independently controlled vehicle" |
| (b) Teeny Ships as player 2's craft | Two small helper ships | Not tested. They exist only when the blueprint carries them, have no controller pointer, and copy the player ship's fire | Lesser role, needs new control code anyway, and takes the helpers away from player 1. Not recommended |
| (c) other roles (gunner, view/turn control, lock-on operator) | A share of ONE ship | Not tested. View direction is one shared value (+0x94) | Not "a craft of his own". Not recommended |

### What a full version of (a) needs

In rough order. Sizes are ESTIMATES (S = hours of work with tests, M = a session or two, L = several sessions).

| # | Work item | Why | Size | Label |
|---|---|---|---|---|
| 1 | Install the changes from the main program when the module has been loaded (at the task start 0x00103F68), instead of per-frame guarded writes | The test patch writes into the module once per frame while its signature matches. That worked in all 7 two-ship runs, but leaves a window between loading and the first write | S | HYPOTHESIS (risk), fix is routine |
| 2 | Ship 2 can be hit and has its own hull | Today it is never damaged | M-L | cause HYPOTHESIS: hit handling goes through the one "player ship" pointer |
| 3 | Own state for ship 2 (flying in / control / done / destroyed) instead of the copy | Needed for 2 and 4 | M | - |
| 4 | Fail rule for two ships: fail only when both are destroyed; a destroyed ship comes back or waits | Today: ship 1 destroyed = failed | M | design decision needed |
| 5 | Enemies and their shots aim at either ship | Not determined today | M | - |
| 6 | Path limits / re-centring applied to ship 2's offset | Observed drift difference in s3-e3 | S | HYPOTHESIS |
| 7 | Lock-on and special weapons for ship 2 | Not tested; lock-on has its own table (`lockonparam.bin`) and uses the global pointer | M | - |
| 8 | Pickups (items, orbs, medals) collected by ship 2 | Not tested | S-M | - |
| 9 | View: both ships must stay in the one picture; L1/R1 turn is one shared value | In the tests the offsets stopped at about +-180 / +-140 and both ships were in the picture (HYPOTHESIS: these are the path's limits). Who turns the view is a design decision | S-M | VERIFIED (seen in s3-e3), rest open |
| 10 | HUD: second hull gauge, a mark to tell the two ships apart (same model today) | One gauge today | M | - |
| 11 | Teeny Ships: stay with ship 1, or one each | Design decision | S-M | - |
| 12 | Own blueprint for player 2 (today: the same ship twice) | Constructor reads the selected blueprint | M | HYPOTHESIS |
| 13 | Clear this lane's ship pointers when the mission ends; second and later missions in one session | The test patch leaves stale pointers; only one mission per run was tested | S | VERIFIED (stale pointers) |
| 14 | Test every route and level: 9 routes x 3 levels, bosses, route-specific events | Only route 0 level 1 was run | L (test time) | - |
| 15 | World map and Gummi Menu: decide player 2's role | Section 6 | design | - |

Items 1-6 make the mode honest for two players (both can be hurt, both matter). Items 7-12 bring player 2 up to
"similar to player 1 exactly". Item 14 is the bulk of the test time.

---

## 8. The test patch (for whoever continues)

`patches\lane-s3-e3-ship2own\SLPM-66675_F266B00B.pnach` = merged build v2 + this lane. **TEST ONLY** (it starts
route 0 by itself on the world map). Generator: `tools\lane-s3\make_s3.py`.

| Hook | Where | What |
|---|---|---|
| 0x002C5F08 (main program) | world-map cursor construction | launcher: once, call 0x002C5418(route) |
| 0x01F21CD4 (flight module, was `jal 0x01F20DD8`) | right after ship 1 is built | allocate 0x1440 bytes (module allocator 0x01F19160), GetLogicalController(1), constructor 0x01F1E4A8 with the same position and rotation; then put ship 1 back into 0x01F7DE44 |
| 0x01F81068 (flight module, class table entry of the player-ship update, was 0x01F219A8) | every step, every player ship | for ship 2: copy ship 1's state, exchange the shared offset 0x01F7DEE0 with ship 2's own copy, run the game's update, exchange back |
| 0x01F2191C (flight module, end of the fire handler) | when the player ship's fire routine has run | if ship 2 is under control: run the same two routines for ship 2 (0x01F1ED28, 0x01F1EE00) |

Module hooks are written only while the flight module is loaded (guard: 16-bit value 0x636A at 0x01F18014).

Cave use (lane range 0x000F5000-0x000F5FFF): routines 0x000F5000-0x47, 0x000F5100-0x15F, 0x000F5300-0x403.
Variables: 0x000F5F40 / 44 launcher counter / latch, 0x000F5F80 / 84 ship 1 / ship 2 pointers, 0x000F5F88 ship-2
update count, 0x000F5FA0 ship 2's offset (16 bytes), 0x000F5FB0 saved offset of ship 1 (16 bytes).
Cave check: 0x000F5410-0x000F5EFF stayed all zero through boot, world map, Gummi Menu, the whole flight and the
return (674 checks, s3-e6b). A check without any patch inside the Gummi mode was not possible (the launcher that
gets there lives in the cave).

Other test patches: `lane-s3-wmprog1`, `lane-s3-count`, `lane-s3-launch0`, `lane-s3-e0-mainpad1`,
`lane-s3-e1-ship2`, `lane-s3-e2-ship2live`.

---

## 9. Limits of this study

- One PC, scripted buttons, emulator at speed 2 or 4. No human has flown the two ships. No test over a real
  network (only button presses travel, and the digests matched, so nothing mode-specific is expected: HYPOTHESIS).
- Only route 0 ("Asteroid Sweep"), level 1, default ship, one mission per run.
- Not determined: why ship 2 is not hit; whether enemies aim at it; what pad 2's L1/R1, lock-on and special
  weapon buttons do through ship 2's update; pickups; behaviour with Teeny Ships on the blueprint; bosses.
- The 132 users of the "player ship" pointer were counted, not read one by one.
- 6 of the 35 controller fetch sites of the Gummi Menu module were not resolved.
- Speed / frame time with two ships was not measured.

---

## 10. Files of this lane

| Path | What |
|---|---|
| `tools\lane-s3\make_s3.py` | test-patch generator (modes `count`, `launch`, `ovl:mainpad1`, `ovl:ship2`, `ovl:ship2live`, `ovl:ship2own`) |
| `tools\lane-s3\ovl.py` | reader for the raw code modules (calls, disassembly, references) |
| `tools\lane-s3\pine.py`, `wm_probe.py`, `s3_ships.py`, `s3_objdump.py`, `s3_flow.py` | read-only probes through PINE |
| `tools\lane-s3\gh.sh`, `tools\lane-s3\ghidra\*.java` | Ghidra headless on the lane's own project `local\ghidra-s3` (flight module imported at 0x01F18000, 2164 functions) |
| `tests\scripts\lane-s3\*.txt` | button scripts |
| `patches\lane-s3-*` | test patches |
| `local\analysis\lane-s3\` | module copies, data listings, Ghidra dumps, probe and harness logs, object dumps |
| `local\tests\s3-*` | screenshots (`sheet.png` in s3-e3 and s3-e6b) |
| `local\variants\s3-wm` | recipe of the test disc |

Left on disk: `local\run-s3` (emulator copies of this lane) and `local\ghidra-s3`. The test disc was deleted.
