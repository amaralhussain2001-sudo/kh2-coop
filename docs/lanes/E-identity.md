# Lane E: who is "the player" (identity), the camera owner, and exits that need both heroes

Written 2026-11-10. Disc base: English-text copy build 2 (game program unchanged, CRC F266B00B).
All tests SINGLE-PC, sandbox emulator copies `local\run-e`, scripted or random buttons, no humans.
Labels: VERIFIED (test id / address / how) or HYPOTHESIS. Test folders: `local\tests\e-*`.

## Result per goal

| Goal | Result |
|---|---|
| 1. Identity | **DONE.** Player 1's hero (made from the PLAYER placeholder 0x236) is and stays the engine's "player" whatever the creation order; the twin is always on controller 2. Holds after room changes, after the skipped opening cutscenes, and after Continue. |
| 2. Camera | **DONE for "follows player 1"**, by giving the game's own registration back to player 1's hero (no forced heap values). The same step fixes the HUD owner and the exit owner. **Stretch (keep both heroes in the picture): NOT done.** |
| 3. Exits | **DONE for room exits; the same code covers event triggers but no event trigger was tested.** A room exit fires only when both heroes are in the same trigger volume. Either hero may be the one who walks in last. Both arrive in the next room when its data has a twin. |
| 4. Code-cave memory | **DONE for the scenes tested.** 0x000F0000-0x000F0FFF stays all zero in the unpatched game through boot, the opening movie, New Game, a save, four room changes and a fight. The nearest memory the system uses ends at 0x00095FFF. |

Delivered patch: `patches\lane-e-x2\SLPM-66675_F266B00B.pnach` (171 lines), made by
`python -I tools\lane-e\make_e.py patches\lane-e-x2 exit`.
Other builds of the same generator: `patches\lane-e-id1` (identity only), `patches\lane-e-x1` (exit rule where
player 1 must be the one walking in), `patches\lane-e-x2pp` (as x2 with lane A's "padplayer" base).

## What was found (all for CRC F266B00B)

### Why the last-built player object was "the player"
VERIFIED by decompiling (`local\analysis\e\player_core.txt`, `attach_cam.txt`, `attach2.txt`):

| Thing | Address | What it does |
|---|---|---|
| Engine's player pointer | 0x0034E948 | Read at 120 places (everything that asks "where is the player"). Set by the base constructor 0x00177DC8, cleared by the base destructor 0x00178280. |
| Saved player pointer | 0x0034E94C | Used by 0x00179E48 / 0x00179EB8, which park the player and bring it back (not exercised here). |
| Attach routine | 0x001781A8(player) | Called at the end of every player constructor. Calls 0x00178100 (camera), 0x00182F28 (trigger owner), then 0x001D6938 (command controller S). |
| Camera target | 0x00348754 | Set by 0x00140D38(player, mode), called from 0x00178100. This is the pointer lane A had to force by hand. |
| Trigger owner | 0x0034ED04 | Set by 0x00182F28(player). Its position is what room exits and area triggers are tested against. |
| Party table | 0x00348638 (3 pointers + 3 flag words) | Slot 0 = player, slots 1-2 = friends. Set by 0x0013DDC0(slot, object), read by 0x0013DDA0(slot). The player gauge of the HUD (method 0x00156E48) reads slot 0 every time. |
| Command controller S | S+0x9E0 = player, S+0xAF4 = attached player, S+0xAE8 | Set by 0x001D6938(S, player). |
| Unit slot back pointer | slot+0x25C | Set by the constructor (slot = object+0x48C). |
| Last built of the main class | 0x00352400 | Set by 0x001D0980, cleared by 0x001D0CE8. |
| Detach | 0x001781E8(player) | Called by the destructor: clears the camera target, the trigger owner, party slot 0 and S's attachment. |

So every constructor registers its object as the camera target, HUD owner, exit owner and engine player. The
second-built object simply overwrote the first.

### How a player object is created
VERIFIED (`spawn_core.txt`, disassembly):
- 0x0016F000(objectId, params) creates any object. For the PLAYER placeholder 0x236 it takes its own path
  (0x0016F0A8-0x0016F0E4: looks up the current player object and form), for a directly placed PLAYER-type object it
  comes from the type switch. Both end at the single call of the player factory, `jal 0x00179FD0` at 0x0016F0F4.
- The factory asks for the controller first (`jal 0x00167F18` at 0x0017A000, lane A's hook site), then builds the object.
- 0x001B6850 builds a player object directly through the constructor, copying the controller from an existing object
  (not through the factory; HYPOTHESIS: form changes). Not exercised.

### How exits and area triggers work
VERIFIED (`exit4.txt`, `exit5.txt`, `exit6.txt`, `act1.txt`, room data dumped with `tools\lane-e\ard.py`):
- Room data: a spawn point with "teleport" fields (place, door) and EventActivators = trigger volumes. Merlin's
  house west door (group `m_10`): a box at (-645, -100, -550) half-size (50, 110, 75) with option 0, and an
  elliptic cylinder at (-800, -195, -550) radii (400, 250), half-height 205, with option 1.
- Every frame the task 0x00182C60 takes the position of the trigger owner 0x0034ED04 (through 0x0016C028) and
  offers it to each area event of the room: table 0x01C60588, 12 bytes per entry, count 0x0034ED00, call
  `jal 0x00182980` at 0x00182D04.
- 0x0019A048 walks the area event's volumes and calls each volume's "is this point inside" method (object vtable +8,
  `jalr v0` at 0x0019A168). Box test 0x001DB298, cylinder test 0x001DB368; the sizes are half-sizes.
- If inside, 0x0019A1A0 runs the area event by kind (first byte of its data): 1 = jump to another room (0x0019A480),
  2 = spawn objects, 3 = start an event (0x0019AF98), 4, 6, 7, 8, 9, 10 = other things (map parts, zone ids ...).
- A door (kind 1) does two things: volume option 1 or 2 = when the engine's player faces the door, start loading
  the next room (0x0019A6C0); option 0 = jump (0x0019A610 writes the destination to 0x0032BB00 and calls
  0x00104F58), but only if 0x001DB198 agrees, which looks at the engine's player (0x0034E948) walking into it.
  VERIFIED by test e-door-id1: standing in the volumes does nothing; walking into the door changes the room.

## The patch

Built on lane A's base (kept unchanged): before a player object runs the command controller's update,
S->pad = that object's own controller (routine 0x000F0020, hooks 0x00178898 / 0x001788A0).
Lane A's routine at 0x000F0000 ("second built = controller 2") is NOT used any more; this lane owns the
controller rule now.

### Hook sites (for merging with lanes D and G)

| Address | Original | Now | Purpose |
|---|---|---|---|
| 0x0016F0B0 | `jal 0x001D1438` | `jal 0x000F0300` (e_mark) | Placeholder path of the object creator: remember "this player object comes from the PLAYER placeholder". Then continues into the original routine. |
| 0x0016F0F4 | `jal 0x00179FD0` | `jal 0x000F033C` (e_wrap) | The only call of the player factory: after the object is built, apply the identity rule. |
| 0x0017A000 | `jal 0x00167F18` | `jal 0x000F0310` (e_getpad) | Factory's controller request: index 0 for player 1's hero, 1 for a twin. (Lane A hooked the same word.) |
| 0x0017828C | `sw zero,0x0034E948` | `nop` | Base destructor: the clearing moved into e_dtor so it can be skipped for a twin. |
| 0x00178294 | `jal 0x001781E8` | `jal 0x000F03C8` (e_dtor) | Base destructor: a dying twin does not unregister player 1's hero. |
| 0x00178898 | `daddu a0,t7,zero` | `nop` | lane A base |
| 0x001788A0 | `j 0x001D6BA0` | `j 0x000F0020` | lane A base |
| 0x00182D04 | `jal 0x00182980` | `jal 0x000F04AC` (e_offer) | Area-event loop: second offer with the twin as the walking hero (exit rule). Not in `lane-e-x1`. |
| 0x0019A168 | `jalr v0` | `jal 0x000F0420` (e_inside) | Volume test: for exits and event triggers the other hero must be inside the same volume (exit rule). |

Code cave used: routines 0x000F0300-0x000F040B (identity), 0x000F0420-0x000F058B (exits); variables
0x000F05C0 (placeholder flag), 0x000F05C4 (role of the object being built), 0x000F05C8 (engine player before the
build), 0x000F05CC (**pointer to the twin object, 0 if none**: other lanes may read it), 0x000F05D0 (second-offer
flag), 0x000F05D4 (player 1's hero during the second offer). Everything is inside 0x000F0300-0x000F05FF.
The variables are not written by the patch file; they rely on that memory being zero at start (VERIFIED zero, see
goal 4).

### What each routine does (the commented source is in `tools\lane-e\make_e.py` and `tools\lane-e\e_exit.py`)

**e_mark (0x000F0300, 4 instructions).** Sets the placeholder flag to 1, then jumps on into the game's routine
that the hooked call wanted (0x001D1438).

**e_getpad (0x000F0310, 11 instructions).** Reads and clears the placeholder flag; reads the engine's player
pointer and remembers it; "is player 1's hero" = flag set OR no engine player yet; remembers that; continues into
the game's controller getter with index 0 (player 1's hero) or 1 (twin).

**e_wrap (0x000F033C, 35 instructions).** Calls the real factory. Then:
- If the new object is a twin: stores it at 0x000F05CC; writes the old hero back to 0x0034E948 and 0x00352400 and
  to its unit slot's back pointer; calls the game's own attach routine 0x001781A8 for the old hero (camera target,
  trigger owner, party slot 0, command controller).
- If the new object is player 1's hero and another player object already existed (a twin built first): that older
  object becomes the twin (stored at 0x000F05CC) and its controller pointer (object+0xB38) is set to controller 2.
- Returns the new object as the factory did.

**e_dtor (0x000F03C8, 17 instructions).** If the dying object is the twin, clears 0x000F05CC. If the dying object is
the engine's player, or there is none: does what the game did (clear 0x0034E948, detach). Otherwise (a twin dies
while player 1's hero lives): leaves the registration alone, writes the hero back to 0x00352400 and only clears the
dying object's own S pointer (object+0xB3C), which is what detach would do to it.

**e_inside (0x000F0420, 35 instructions).** Runs the volume's own test for the walking hero. If inside and the area
event is kind 1 or 3 and a twin exists: runs the same test for the other hero (position through the game's
0x0016C028) and returns that. Other kinds: unchanged on the first offer, never on the second offer.

**e_offer (0x000F04AC, 56 instructions).** Makes the game's offer for player 1's hero as before. Then, only for
entries that are switched on and of kind 1 or 3 and only if a twin exists: sets the engine's player pointer to the
twin, offers the area event again with the twin's position, puts the engine's player pointer back, and keeps the
"inside / approaching" flag bits the first offer had set (area event +4, bits 0x18).

## Tests

All with two linked copies unless noted; every run "never out of sync" (digest counts from player 1's log).

| ID | Disc / patch | What | Result |
|---|---|---|---|
| e-noid | test-b-roam3, lane A's order rule | baseline | VERIFIED: engine player, camera, party slot 0, S owner = the twin (built second), which is on pad 2 |
| e-id1 | test-b-roam3, identity | P1 runs, P2 runs and jumps | VERIFIED: all those pointers = the placeholder hero, pad 1; twin on pad 2; each pad moves only its own hero; the picture stays on P1 while the twin walks away (`local\tests\e-id1\sheet.png`, seen by eye); 87 digests |
| e-p1alone-id1 / -x1 | test-b-roam3 | P1 walks to the west door alone | id1: room changes (P1 is the exit owner now) and both heroes arrive with the right roles. x1: **no room change** for the rest of the run (about 13 s of game time); 87 digests each |
| e-p2alone-x2 | test-b-roam3, full patch | twin walks into the door and keeps pushing for 400 frames, P1 far away | VERIFIED: **no room change**; 87 digests |
| e-door-id1 | test-e-door, identity (control) | P1 starts in the exit volumes facing the door | VERIFIED: nothing until P1 walks into the door, then the room changes |
| e-door2-x1 | test-e-door, exit rule "P1 walks in" | P1 pushes into the door alone, twin arrives, P1 pushes again | VERIFIED: no change, no change, **change on P1's second push**; both arrive; afterwards pad 1 moves P1, pad 2 moves the twin; 103 digests |
| e-door-x2 | test-e-door, full patch | P1 pushes into the door and waits, then the twin walks in | VERIFIED: no change while alone; **change when the twin walks in**; both arrive, controllers right; 103 digests |
| e-order-x2 | test-e-order (twin record BEFORE the placeholder in both rooms), full patch | same steps as e-door-x2 | VERIFIED: the first-built object is switched to pad 2 and marked twin; the placeholder hero is the engine player and camera target in both rooms; exit and arrival as above; 103 digests |
| e-t1-x2 | test-t1 (Roxas twin, scene reached through the skipped opening scenes), full patch | lane A's who-moves-whom script | VERIFIED: placeholder Roxas = engine player, pad 1; twin pad 2; each moved and jumped only with its own pad; 110 digests |
| e-cont1-id1 | test-e-door, identity, ONE copy (HP written to 1 by the test) | defeated in the Borough, Continue | VERIFIED: after Continue the room is rebuilt with the placeholder hero as engine player on pad 1 and the twin on pad 2; pad 1 moves P1 |
| e-sync-x2 | test-e-door, full patch | door steps, then random buttons on both pads, 30,000 frames | VERIFIED: **never out of sync, 468 digests**, 4 of 4 screenshot pairs identical; patch words intact at 13 checkpoints |
| e-ca5-x2 | test-b-ca5 (fight with twin), full patch | random buttons on both pads until defeat | VERIFIED: roles right in the fight room; 120 digests |
| e-solo-x2 | test-b-roam (no twin), full patch | save, walk out the door alone | VERIFIED: works as the unpatched game (room changes); 109 digests |
| e-opening-x2 | English copy (no twin), full patch | real opening to the first town | VERIFIED: normal; one Roxas on pad 1; 112 digests |
| e-cave-nopatch | test-b-roam, NO patch | boot, New Game, save, 4 room changes, a fight, random buttons, 19,000 frames, 13 checkpoints | VERIFIED: 0x000F0000-0x000F0FFF all zero every time; data in 0x00080000-0x000FFFFF only in 0x00081000-0x00095FFF |
| e-cave-opening | English copy, NO patch, one copy | boot, title, opening movie (paused/resumed), 7 checkpoints | VERIFIED: all zero |
| e-both-x1, e-both-id1 | test-b-roam3 | first attempt at the both-heroes test | No room change in either: player 1's path was blocked by the twin standing in the doorway and never reached the door (the identity-only control failed the same way). Navigation problem of the test, kept for the record; replaced by the test-e-door disc. |

Test disc made by this lane: `local\iso\test-e-door.iso` (recipe `local\variants\e-door`): test-b-roam3 with
player 1 starting at (-470, 0, -550) facing the west door of Merlin's house and the twin at (-250, -1, -560).
`test-e-order.iso` was deleted; recipe in `local\variants\e-order` (rebuild with `Kh2Tool inject`).

## Open problems and things the main lane should know

1. **Camera stretch not done.** The camera follows player 1's hero only; the twin can walk out of the picture.
   Where to start: camera state block 0x00348710 (target object at +0x44, getter 0x00140DF0), setter 0x00140D38.
2. **No on-screen sign "waiting for the other player".** With the rule on, one hero pushing into a door alone
   simply gets no reaction.
3. **The exit rule is tested on one door only** (Merlin's house to the Borough). Event triggers (kind 3) go through
   the same code but none was tested. Kinds 2, 4, 6-10 (ambush spawns, map parts, zone ids) still follow player
   1's hero only: the twin walking ahead alone does not trigger them. HYPOTHESIS: acceptable while the heroes stay
   together, to revisit with own screens.
4. **Boss rooms** are entered through ordinary room exits, so they fall under the rule; not tested as such.
5. **Second offer swaps the engine's player pointer for a moment** (inside one call, on both PCs alike). In sync in
   every test, but anything the door code remembers about "the player" during that call would be the twin.
   Nothing wrong was seen in 30,000 frames; use `lane-e-x1` if a problem shows up (then player 1 must walk in last).
6. **Paths that build or swap player objects without the factory are not covered:** 0x001B6850 (HYPOTHESIS: Drive
   Form change) and the park/restore pair 0x00179E48 / 0x00179EB8. A twin that changes form would be built through
   0x001B6850, register itself as the engine's player, and nothing would give the role back.
7. **Attacks, seen while testing (lane G's subject):** with this patch S->player is player 1's hero all the time
   (before, it was the last attached object). In the fight disc, when only pad 2 pressed attack the twin attacked
   and player 1's hero moved as well; when only pad 1 pressed attack only player 1's hero moved (tests e-atk-x2,
   e-atk-x2pp, positions only, not analysed further).
8. **Both heroes still share unit slot 1** (lane D). e_wrap rewrites the back pointer of the hero's own slot only,
   so it stays correct when the twin gets its own slot.
9. **The variables are not initialised by the patch file.** Fine as long as that memory is zero at boot (VERIFIED
   in the scenes above; not checked for every world, a soft reset, or the Gummi Ship).
10. **Probe timing:** `probe.py` reads when a screenshot file appears, which is up to about 60 frames after the
    named frame at 2x speed. Positions in the logs are "at or shortly after" the frame.
11. Player-player collision: the heroes block each other (the twin standing in a doorway kept player 1 out).

## How to repeat

```
python -I tools\kh2_session.py make 2 --run-dir run-e
python -I tools\lane-e\make_e.py patches\lane-e-x2 exit
python -I tools\kh2_session.py run e-door-x2 --run-dir run-e --port 28750 --iso local\iso\test-e-door.iso ^
   --players 2 --slots 0,1 --frames 6600 --speed 2 --snap 4600,4800,5190,5260,5450,5990,6350 ^
   --script tests\scripts\lane-e\door_p1.txt --script2 tests\scripts\lane-e\door_p2.txt --then idle ^
   --fresh-card --pine 28051 --patch-dir patches\lane-e-x2
python -I tools\lane-e\probe.py local\tests\e-door-x2 28051 4600,4800,5190,5260,5450,5990,6350     (while it runs)
python -I tools\lane-e\cavecheck.py <test folder> 28051 <frames> [--pnach <file>] [--wide]          (while it runs)
```

## Files of this lane

- `tools\lane-e\`: `make_e.py` (patch generator), `e_exit.py` (exit rule), `asm.py` (small assembler with labels),
  `probe.py` (who is the player: pointers, objects, controllers), `cavecheck.py`, `ard.py` (room data dump with
  trigger volumes), `ard_edit.py` (move / swap entities), `findimm.py`, `sethp_at.py` (one-copy tests only),
  `gh.sh` + `ghidra\LaneEDump.java` (decompile from the project copy `local\ghidra-e`), copies of lane A / B tools.
- `tests\scripts\lane-e\*.txt`. Decompiled text and harness outputs: `local\analysis\e\`.
- Patches: `patches\lane-e-x2` (delivered), `lane-e-x1`, `lane-e-id1`, `lane-e-x2pp`.
- Emulator copies `local\run-e` (2 copies) are left in place for re-runs.
