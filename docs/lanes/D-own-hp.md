# Lane D: own HP and MP for each hero

Written 2026-11-10. Disc: English-text copy build 2 and test discs made from it (game program unchanged,
CRC F266B00B). All tests SINGLE-PC, sandbox emulator copies `local\run-d`, scripted or random buttons, no humans.
Labels: VERIFIED (test id / address) or HYPOTHESIS. Test folders `local\tests\d-*`, logs `local\analysis\d\`.

## Result

**WORKS.** With the patch below each hero has its own HP and MP. Damage and healing on one do not change the
other, the two keep their own values through a room change and through "Continue", their stats and level stay
equal (also at the moment of a level-up), nothing collides with Donald, Goofy or enemies, lane A's controller
separation still works, and two linked copies stay in sync.

Not solved here (by design, Phase 2 / other lanes): a hero at 0 HP still gives the normal Game Over, whichever
hero it is. The one HUD gauge shows the hero the camera follows. Enemies only attack the hero the engine
calls "the player" (the one built last).

## The patch

- File: `patches\lane-d-ownhp-v2\SLPM-66675_F266B00B.pnach` (SHA-1 26cbcf3b...; 11 lines of lane A v3 copied
  unchanged + 111 code words + 7 hooks). Disassembly of every word: `patches\lane-d-ownhp-v2\listing.txt`.
- Generator: `python -I tools\lane-d\make_ownhp2.py <outDir>` (options `nobase` = without lane A's lines, both
  heroes on pad 1, experiments only; `nosib` = without routine D6).
- Code cave used: 0x000F0100-0x000F02BB, one work flag at 0x000F02F0 (lane D's range 0x000F0100-0x000F02FF).
- Two bytes of the save data are used: 0x0032D98E (save + 0x1E5E) = second hero's current HP,
  0x0032D98F (save + 0x1E5F) = second hero's current MP + 1 (0 = nothing stored).

| Routine | Hook site (old instruction) | What it does |
|---|---|---|
| D1 0x000F0100 | 0x00177E74 `jal 0x001A15D0` in the player base constructor 0x00177DC8 | If a player object already exists (0x00352400 != 0: the same test lane A uses for "second hero") the new object gets a fresh unit slot from the game's own routine 0x001A1728 instead of the shared one. The slot is marked (bit 31 of slot+0x250) and its stats are loaded once more. First hero: unchanged, jumps to 0x001A15D0. |
| D2 0x000F015C | 0x001A1518 `bne t7,s1,0x001A14C4` in the find-slot-by-id loop of 0x001A1490 | A marked slot is never returned by a search by id, so every "Sora's slot" lookup in the game still gets player 1's. |
| R 0x000F017C | 0x001A1238 `lbu t7,4(s1)` in 0x001A11E0 (load stats from the character record) | Marked slot: current HP comes from 0x0032D98E (if not 0) instead of the record. |
| RM 0x000F019C | 0x001A1248 `lbu t6,6(s1)` in 0x001A11E0 | Marked slot: current MP comes from 0x0032D98F - 1 (if the byte is not 0). |
| W1 0x000F01C4 | 0x001A1854 `sb t7,4(t6)` in 0x001A1840 (write the slot back into the record) | Marked slot: current HP goes to 0x0032D98E, not into player 1's record. |
| W2 0x000F01E4 | 0x001A1870 `sb t7,6(t5)` in 0x001A1840 | Marked slot: current MP + 1 goes to 0x0032D98F (0 if the HP just stored is 0). |
| D6 0x000F0210 | 0x001A1438 `j 0x001C3060` (tail of 0x001A11E0) | After a hero slot (status id 1 or 14) reloaded its stats, every other slot in use with the same id is written back and reloaded too. A flag at 0x000F02F0 stops the nested call from looping. |

None of these sites is touched by lane A's patch (0x0017A000, 0x00178898, 0x001788A0). Sites other lanes may also
want: the base constructor 0x00177DC8 (I changed only the one call at 0x00177E74) and 0x001A11E0 / 0x001A1840
(slot load / write-back).

Design in one paragraph: the second hero's slot keeps pointing at player 1's character record, so max HP, max
MP, strength, magic, defence, AP, abilities, equipment and level are read from the same place and are always
equal. Only the two "current" values are kept apart: they live in the slot while a room is loaded and in two
save-data bytes between rooms.

## Tests

| Test | Setup | Result |
|---|---|---|
| d-base | Port Royal fight, twin among the enemies, player 1 far away (lane B recipe b6); lane A patch only; both idle | Baseline: one slot (0x01C6C750, id 1, reference count 2, owner = twin), HP 20 -> 0 |
| d-v1 | same with patch v1 (D1 + D2) | VERIFIED: slot 1 (player 1) stays 20/20; the twin has slot 2 (id 1, marked), HP 20 -> 0 |
| d-v1-ca5-idle | both Soras side by side (test-b-ca5), idle | VERIFIED: only the twin loses HP (20 -> 0); player 1, 150 units away, stays 20/20 |
| d-v1-p1dies | reverse layout (recipe `local\variants\d-ca8`: player 1 among the enemies, twin 2,500 units away), idle, 94 s | Nobody loses HP. The enemies do nothing to player 1 while the engine's "player" (the twin) is far away |
| d-x1-target | ONE copy, side by side; after both exist, PINE keeps writing player 1's object into 0x00352400 and 0x0034E948 | VERIFIED: the enemies now hit player 1: slot 1 20 -> 0 while the twin's slot stays 20/20. (This is the "reverse" test.) |
| d-v1-atk | v1 without lane A's lines (pad 1 drives both), twin fights | VERIFIED: the twin's damage and HP-orb healing change only its slot (e.g. 14 -> 19); player 1, hit by stray attacks, goes 20 -> 17 -> 14 -> 12 and is not healed by the twin's orbs |
| d-v1-roomchg | ONE copy, free-roam disc with twin; HP set to 7 / 13 by PINE, then through the door | PROBLEM with v1: after the door both have 7 (they share the record). This is why v2 exists |
| d-v2-roomchg | same with v2; HP 7 MP 100 / HP 13 MP 40 | VERIFIED: after the door player 1 has 7 / 100, the twin 13 / 40; then the twin heals 13 -> 15 from orbs, player 1 stays 7 |
| d-v2-atk | ONE copy, v2, total experience (0x0032F210) set to 300 once, then the twin kills an enemy | VERIFIED: level 1 -> 5; both slots' stats change at the same moment (5,7,2,2 -> 7,7,5,6); the twin keeps its HP 12 through the reload, player 1 keeps 20 |
| d-v2-hbf | Hollow Bastion fight with Donald, Goofy and a twin (recipe `local\variants\d-hbfriends`), delivered patch | VERIFIED: slots 1 player 1, 2 Donald (id 2), 3 Goofy (id 3), 4 twin (id 1, marked), 5+ enemies. Twin 20 -> 6, Donald 18 -> 3 -> 18, Goofy 28 -> 23, player 1 20. The mission's cutscene then plays normally |
| d-v2-continue3 | ONE copy, free-roam disc; in the Borough player 1 set to 11 HP, twin to 1 HP; twin is defeated; Continue | VERIFIED: Game Over, Continue works; afterwards player 1 20/20 and twin 20/20 (the game restores its save data, including our two bytes, to the values at room entry). No crash |
| d-sep | lane A's "who controls whom" test with the delivered patch | VERIFIED: object 1 moves/jumps only for pad 1, twin only for pad 2, in sync |
| d-sync1-ca5 | TWO linked copies, Port Royal fight with twin, random buttons on both pads, 7,300 frames | VERIFIED: 114 digests, never out of sync, 5 of 5 screenshot pairs identical; at the end slot 1 HP 20, slot 2 HP 17 |
| d-sync2-roam | TWO linked copies, free roam with twin, both walk out of the door, then random on both pads, 30,000 frames | VERIFIED: 468 digests, never out of sync, 6 of 6 screenshot pairs identical; room change done; twin HP moves (12-16) while player 1 stays 20 |
| d-stock-check | no patch at all, free-roam disc: New Game, save, room changes, random play, 9,000 frames | VERIFIED: 0x0032D98E/8F stay 0; memory 0x000F0000-0x000F0BFF is all zero at two points |
| d-v2-continue, d-v2-continue2 | attempts at the Continue test | NO RESULT: the script did not leave the room / the town's defense system killed the enemies before a defeat |

Not tested: MP being spent by real magic (level-1 Sora has none; MP separation is shown only by a written value
surviving a room change), Cure / Potion on one hero, save to memory card and load with the two bytes, Drive Forms,
other player forms (Roxas, lion, ...), LAN or internet, humans.

## What happens at 0 HP (with the patch)

- VERIFIED (d-v1-twindies): the twin (the hero the camera follows) reaches 0: defeat animation, then the normal
  Game Over screen (Continue / Load Game), although player 1 still has 20/20.
- VERIFIED (d-x1-target): player 1 (the hero the camera does not follow) reaches 0: the same Game Over screen.
- No crash in either case. After Continue both heroes are back with their room-entry HP (d-v2-continue3).
- What "down like Goofy" (Phase 2) needs: HP changes are applied through the owner object's virtual function
  (0x001A1950 calls the function at class table + 0x78; for the player class 0x00352410 that is 0x0017A480).
  Defeat and Game Over are decided inside the player class, per object. That code has to be changed so that a
  hero at 0 HP goes down instead, and Game Over starts only when both are down. Not investigated further.

## What was found (CRC F266B00B)

### Unit slots
| Thing | Address / value | Status |
|---|---|---|
| Slot pool | 0x01C62FB8, 64 slots of 0x268 bytes; free-index stack 0x01C6C9B8, free count 0x01C6CAB8 | VERIFIED (code 0x001A0E78 / 0x001A17C8, live reads) |
| Order | slots are handed out from the top: first 0x01C6C750, then 0x01C6C4E8, 0x01C6C280, 0x01C6C018 ... | VERIFIED |
| Fields | +0x000 HP, +0x004 max HP, +0x180 MP, +0x184 max MP, +0x188/18A/18C/18E four stats (16-bit), +0x1B0.. Drive state, +0x244 character record, +0x248 form data, +0x250 flags (the game uses bits 0-2; bit 31 is our mark), +0x254 status id (1 Sora, 14 Roxas, 2 Donald, 3 Goofy, -1 enemies), +0x258 reference count, +0x25C owner object, +0x260 party save block (0x0032E020, heroes only), +0x264 another pointer | VERIFIED (0x001A0D48, 0x001A11E0, 0x001A1840, live reads) |
| Allocate / initialise / release | 0x001A0E78 / 0x001A0D48 / 0x001A17C8 | VERIFIED statically |
| Find by id, else make new (ids 1-15 only) | 0x001A1490 | VERIFIED |
| "Get my slot" used by player objects | 0x001A15D0(statusId, formArg): find-or-share, then load stats | VERIFIED |
| "Always a fresh slot" | 0x001A1728(statusId, formArg), 3 callers in the game (0x00267368, 0x00291BF8, 0x00291E24) | VERIFIED statically; used by D1 |
| Load stats from record / write back / both | 0x001A11E0 / 0x001A1840 / 0x001A1460 | VERIFIED |
| Next slot in use | 0x0031F168(pool, previous) | VERIFIED statically; used by D6 |
| Where a player object asks | base constructor 0x00177DC8 at 0x00177E74; status id = 16-bit value at (object+8)+0x4C (the object list's status column); the result goes to object+0x48C and slot+0x25C | VERIFIED |
| Second asking site | constructor 0x00177F50 at 0x00177FFC (one user: 0x002D0290) | VERIFIED statically, NOT hooked, not tested |

### Character records and level-up
| Thing | Address / value | Status |
|---|---|---|
| Sora's record | 0x0032E020 (0x114 bytes); Donald 0x0032E134; Goofy 0x0032E248 | VERIFIED (slot+0x244 live) |
| Record bytes | +4 current HP, +5 max HP, +6 current MP, +7 max MP, +0xC / +0xD two gauges, +0xF level | VERIFIED (0x001A11E0 / 0x001A1840, live) |
| Total experience | 0x0032F210 | VERIFIED (d-v2-atk: writing 300 gave level 5 at the next kill) |
| Level-up loop | 0x001B71E8(statusId, record, object): raises the level, then reloads the slot of the object passed (0x001A1460) | VERIFIED statically; with D6 both heroes' slots reload (d-v2-atk) |
| Other reloads | by object: 0x001D7000 (uses the object in 0x0034E948), 0x001D5D80; by id: ten callers of 0x001A1658 | VERIFIED statically |
| The two save bytes | save + 0x1E5E / + 0x1E5F. The community GoA mod lists them as unused bytes it re-uses ("HT Post-Story Save" / "HT Progress") | Zero in an unpatched game (d-stock-check); "never used by the game" is HYPOTHESIS |

## For the other lanes (outside lane D, noted only)

- **Whom the enemies attack.** Side by side and idle, only the hero built last is attacked (d-v1-ca5-idle).
  After writing player 1's object into BOTH 0x00352400 and 0x0034E948 the enemies attacked player 1 instead
  (d-x1-target, one copy, PINE). Which of the two pointers decides it was not separated.
- **The HUD gauge** shows the HP of the hero the camera follows (the twin's): danger-red face while player 1
  was full (d-v1). There is no gauge for the other hero.
- **Room change and the "second hero" rule:** across Merlin's house -> Borough the second-built object got the
  marked slot again and player 1 the unmarked one (d-v2-roomchg, d-sync2-roam), so 0x00352400 was 0 when the
  first object of the new room was built.

## Stretch: a gauge for player 2 (not concluded)

- In the fight with Donald and Goofy their two small gauges are drawn; nothing is drawn for a second hero.
- The community "Gauge1" (0x01D48FA4, step 0x34) and "Point1" (0x01D48EFC, step 0x38) blocks hold no pointers
  to unit slots (d-gauge1 dump). Besides each object's own pointer and one pointer inside each slot, only the
  twin's slot had a third pointer to it, at 0x01B47BA0 (a heap object, address valid for that scene only).
- Writing player 1's slot address there did not visibly change the gauge (d-gauge3; thumbnails only, not a
  clean test). HYPOTHESIS: the gauge reads the camera hero's slot through the player object each frame.

## Open problems

1. **Game Over rule.** Either hero at 0 HP ends the fight (see above). Phase 2.
2. **Drive state is still shared between rooms.** Slot+0x1B0..+0x1BB (Drive gauge, bars, form data) are written
   through slot+0x260 into the shared save block by both slots; the last writer wins at a room change. The two
   gauges at record +0xC / +0xD are shared the same way. Left alone on purpose (Drive Forms are a later phase).
3. **The "second hero" test** is lane A's (0x00352400 != 0 when the object is built). Any case where a new
   player object is built while another exists is treated as a second hero and gets a fresh slot: a Drive Form
   change may do that. Not tested. The second asking site (0x00177FFC) is not hooked.
4. **The two save bytes** are assumed unused by the game. They are saved to the memory card with the rest.
   Loading a save made without the patch gives 0 / 0, which means "use player 1's values". Save / load with the
   patch was not run.
5. **A hero that was down** restarts from player 1's HP and MP in the next room (stored HP 0 means "none").
6. **MP** separation was not exercised by real magic.
7. **Code cave memory** 0x000F0100-0x000F02FF was zero in an unpatched game at two points of one test only.
8. **D6 treats every slot with the same hero id as a sibling**, also the fresh slots the game itself makes with
   0x001A1728 in three special places (not identified, not tested).
9. **Stats are equal by construction** (same record). If player 2 is to get its own Keyblade and abilities
   (plan Phase 4), the second hero needs its own record; the mark bit and D2 stay useful, R/W1/W2/D6 would change.

## How to repeat

```
python -I tools\kh2_session.py make 2 --run-dir run-d
python -I tools\lane-d\make_ownhp2.py patches\lane-d-ownhp-v2
bash tools/lane-d/drun.sh d-v2-hbf test-d-hbf.iso "<abs path>/patches/lane-d-ownhp-v2" 9000 "4600,5500,6500,7500,8900" 80 "<abs path>/tests/scripts/b_newgame.txt"
python -I tools\lane-a\sep_run.py d-sep <abs path>\patches\lane-d-ownhp-v2 run-d 28650 28041 <abs path>\local\iso\test-t1.iso
```
Test discs of this lane were deleted (4.3 GB each); rebuild with
`dotnet local\build\Kh2Tool\Kh2Tool.dll inject "<English copy>" local\iso\test-d-X.iso <recipe folder> report.txt`:
test-d-ca6 = `local\variants\b-ca\b6`, test-d-ca8 = `local\variants\d-ca8`, test-d-hbf = `local\variants\d-hbfriends`.
Two-copy sync tests (scripts in `tests\scripts\lane-d\`, P = absolute project path):
```
python -I tools\kh2_session.py run d-sync1-ca5 --iso P\local\iso\test-b-ca5.iso --players 2 --slots 0,1 --frames 7300 --speed 4
   --script P\tests\scripts\lane-d\d_newgame_short.txt --script2 P\tests\scripts\lane-d\d_p2_wait.txt --then random --bot random
   --fresh-card --run-dir run-d --port 28650 --patch-dir P\patches\lane-d-ownhp-v2 --peek 0032BAE0,01C6C750,01C6C4E8,0032D98C,01C61958
python -I tools\kh2_session.py run d-sync2-roam --iso P\local\iso\test-b-roam3.iso --players 2 --slots 0,1 --frames 30000 --speed 4
   --script P\tests\scripts\lane-d\d_roam_p1.txt --script2 P\tests\scripts\lane-d\d_roam_p2.txt --then random --bot random
   --fresh-card --run-dir run-d --port 28650 --patch-dir P\patches\lane-d-ownhp-v2
```
On the Port Royal disc stop before a hero can be defeated (Continue crashes on mission jump discs, lane B).

## Files of this lane

- `tools\lane-d\`: make_ownhp2.py (delivered patch), make_ownhp.py (v1), slots.py (watch the slot pool, read-only),
  poke_watch.py and gauge_poke.py (ONE-copy experiments, they write memory), drun.sh (run + watch), scan_off.py
  (find uses of a structure offset), gh.sh (Ghidra dump from the copy `local\ghidra-d`).
- `patches\lane-d-ownhp-v2\` (delivered), `patches\lane-d-ownhp-v1\` (first stage, kept for reference),
  `local\patches-d\` (experiment variants without lane A's lines).
- `local\analysis\d\`: decompiled routines (slot1-4.txt, basector.txt, refresh.txt, hpfuncs.txt, ctor2.txt) and
  the slot / poke logs of every test.
- Emulator copies `local\run-d` (2) left in place for re-runs.
