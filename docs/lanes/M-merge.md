# Lane M: one merged build of lanes A, D, E, F (v1) and G (v2), tested together

Written 2026-11-10. Game program CRC F266B00B (Kingdom Hearts II Final Mix, SLPM-66675).
All tests SINGLE-PC, sandbox emulator copies `local\run-m` (port 29050, PINE 28081), scripted or random buttons,
no humans. "2 copies" = two linked emulator copies; every 2-copy run below ended "never out of sync".
Labels: VERIFIED (test id / address / how) or HYPOTHESIS. Test folders: `local\tests\m2-*`.

## Result

**Both merged builds work.** In one build: the twin is in every room (lane F), player 1's hero is and stays the
engine's player with the camera, HUD and exits, the twin is on controller 2 (lane E), each hero has its own HP
and MP (lane D), exits need both heroes (lane E), and in v2 each hero attacks, casts and uses commands from its own
controller with its own control object (lane G). One player object alone plays exactly as the unpatched game.

| Build | Patch file | Lines | SHA-1 |
|---|---|---|---|
| v1 = E (identity + exits, with lane A's base) + D + glue | `patches\merged-v1\SLPM-66675_F266B00B.pnach` | 329 | b3cc3b53d33ea5002f8f083ce514c783b4034d12 |
| **v2 = v1 + lane G, without lane A's base** (use this) | `patches\merged-v2\SLPM-66675_F266B00B.pnach` | 563 | 9168afbcfcf6cfc3303907c0aacfd26bd53254cf |

Each folder has `listing.txt`: every word the patch writes, with address, disassembly and meaning, the hook
sites with the original instruction, the variables and the reserved memory.

Discs (all built from `local\iso\English text build3 (candidate).iso`, twin record BEFORE the placeholder;
`Kingdom Hearts II - Final Mix (English text).iso` was not touched):

| Disc (`local\iso`) | What | SHA-1 |
|---|---|---|
| **kh2-coop-v1.iso** | twin everywhere, normal New Game start | a60c8ab94399f276725591bff1d97f6c8e5d6887 |
| test-m-roam.iso | same + lane B's jump: New Game starts at the save point in Merlin's house, Borough next door | 10d7eded7834897362791e9597c747857e2397a5 |
| test-m-fight.iso | same + lane B's jump: New Game starts in the Port Royal fight | 01179846f7e3f7ee74502f744ec4fbdcfd0ee5a8 |

Deleted after use (recipes in `local\variants\m-test-m-hbf`, `m-test-m-solo`): test-m-hbf.iso (Hollow Bastion
fight with Donald and Goofy, twins added) and test-m-solo.iso (free-roam jump WITHOUT twins).

## How to rebuild

```
python -I tools\merge\make_all.py                 -> patches\merged-v1   (byte-identical to the tested file)
python -I tools\merge\make_all.py --v2 --check    -> patches\merged-v2   (+ word-for-word check against lanes E, D, G)
python -I tools\merge\build_disc_m.py kh2-coop-v1.iso
python -I tools\merge\build_disc_m.py test-m-roam.iso  --overlay local\variants\b-roam\built\ard
python -I tools\merge\build_disc_m.py test-m-fight.iso --overlay local\variants\b-ca\b7\ard
python -I tools\merge\build_disc_m.py test-m-solo.iso  --no-twin --overlay local\variants\b-roam\built\ard
```
`make_all.py` has one clearly separated section per source lane (base, identity, exits, ownhp, commands, glue);
`--without NAME` leaves one out (used for the test variant `patches\merged-v1-noexit`).

## What was merged, and the check that nothing was changed by accident

| Section | From | In the merged file |
|---|---|---|
| identity, exits | lane E `patches\lane-e-x2` | routines and variables at lane E's addresses, text unchanged. v1: 169 of 171 words equal; the 2 different words are the two factory hooks, which now go through the glue. |
| ownhp | lane D `patches\lane-d-ownhp-v2` | routines D2, R, RM, W1, W2, D6 and their six hooks unchanged at lane D's addresses (100 of 129 words equal). Not taken: lane A's old order routine at 0x000F0000 (4 words), lane D's D1 at 0x000F0100-0x000F0158 (23 words, replaced by the glue routine `m_slot`), and the hook words at 0x00177E74 and 0x0017A000. |
| base | lane A, as kept by lane E | v1 only (routine 0x000F0020, hooks 0x00178898 / 0x001788A0). Left out of v2: lane G's design makes it unnecessary (`--keep-base` puts it back). |
| commands (v2) | lane G `patches\lane-g-cmd-v3-no-pad-rule` | **197 of 197 words equal**: routines 0x000F0800-0x000F0AD3 and all 16 hook words, built by lane G's own generator code (copy `tools\merge\g_cmd.py`). Nothing of lane G was dropped. |
| twin everywhere | lane F tool `local\build\lane-f\LaneF.dll twin-all`, run as it is | room data only, `--order before`. |
| English build 3 | main lane candidate | base of every disc above. |

## Clashes found and how they were resolved

1. **Who gets the fresh unit slot (the known clash).** Lane D decided "second hero" by "a player object already
   exists" (0x00352400 != 0). On the twin-everywhere disc the twin is built FIRST, and both heroes come from PLAYER
   placeholders, where lane E's rule makes the LATER one player 1's hero. Unmerged, the hero would have got the
   marked slot. **Resolution (glue routine `m_slot` at the slot request 0x00177E74, replaces lane D's D1):**
   it reads lane E's role of the object being built.
   - A twin built after the hero: fresh slot, marked, stats loaded (lane D's D1 path, unchanged).
   - Player 1's hero built while an earlier player object of the same character exists (that object becomes the
     twin): the EARLIER object's slot is marked and reloaded on the spot, then the hero asks the game for its slot
     in the normal way. Lane D's D2 makes searches skip marked slots, so the game makes a new, unmarked slot for
     the hero. "Sora's slot" is the hero's whatever the build order.
   - Not inside the player factory (some other code builds a player object): the game's own behaviour.
   VERIFIED in every twin test below: hero = plain slot, twin = MARKED slot, in Merlin's house, the Borough, the
   Port Royal fight, the Hollow Bastion fight with Donald and Goofy, and the Roxas start.
   Side effect to know: on these discs the twin holds the FIRST slot handed out (0x01C6C750, the community map's
   "Slot1") and the hero the second (0x01C6C4E8). The game finds the hero's slot by search, not by address, and
   the HUD followed the hero in every test; but tools or cheat lines that assume 0x01C6C750 = player 1 are wrong
   here.
2. **Hook word 0x0017A000** (lane A, lane E, lane D's copy of lane A, lane G's default variant) and
   **0x0016F0F4** (lane E): now `m_getpad` / `m_wrap` in the glue. They set a flag "the player factory is running"
   (0x000F0DF0) around lane E's own routines, which are called unchanged. `m_slot` needs that flag.
3. **Lane G + twin built first (v2).** Lane G gives a hero its control object when it ATTACHES, by its controller
   at that moment. A twin built first attaches as "controller 1" (to S) and only becomes the twin when the hero
   arrives. **Resolution (`m_wrap`, v2):** in that case the twin is attached once more (lane G's attach then gives
   it S2), then the hero once more, so the camera target, the trigger owner, the HUD owner and S end on the hero.
   VERIFIED: every v2 probe shows hero = S, twin = S2, S2.player = the twin, S2.pad = controller 2, menu on screen = S.
4. **Lane E's destructor rule + lane G (v2).** Lane E lets a twin die without the game's detach. With lane G the
   twin's own control object S2 has to be released. **Resolution (`m_dtor` at 0x00178294, then lane E's routine):**
   releases S2 with the game's routine 0x001D69D0; that routine also clears party slot 0 (the HUD owner), so the
   slot is given back to the hero (0x0013DDC0). Reached at every room change in which the twin is destroyed
   before the hero; no test separates the two destruction orders (HYPOTHESIS that both occur).
5. **Hook addresses used twice:** none besides the above. Lane D's six slot hooks, lane E's exit hooks and lane G's
   16 hooks do not overlap (the generator stops with "CLASH" if two sections write one address, and checks every
   hook's original instruction against the game program).
6. **Code-cave ranges:** A 0x000F0020-2F (v1), D 0x000F015C-02BB + flag 0x000F02F0, E 0x000F0300-058B + variables
   0x000F05C0-D7, G 0x000F0800-0AD3, glue 0x000F0C00-0x000F0DA7 (v2) + flag 0x000F0DF0. No overlap.
   **Lane G's S2 data block 0x000F1000-0x000F1AFF is reserved** (kept where lane G put it).
   VERIFIED unused by the game: in two unpatched runs (m2-x-nopatch-solo: boot, title, New Game, a room change,
   a fight, random play, 5 checkpoints; m2-x-nopatch-fight: twin disc, fight, random play, 4 checkpoints) the only
   4 KB blocks with data in 0x00080000-0x000FFFFF are 0x81000-0x93000 and 0x95000. This agrees with lane E's check.
   VERIFIED intact: during a random v2 fight all patch words in 0x000F0000-0x000F0FFF kept their values
   (m2-v2-x-intact, 4 checkpoints).
7. **Lane D's two save bytes** (0x0032D98E / 0x0032D98F): no other lane uses save data. They are written to the
   memory card with the save (cards of both copies byte-identical, save present).
8. **Lane E's destructor hooks against lane D's slot release:** no clash. The base destructor releases the slot
   in its base-class part (0x00175928), after lane E's two words; lane D does not hook the release.

## Test table

Probe = `tools\merge\mprobe.py` (reads roles, controllers, slots through PINE at screenshot frames; it is up to
about 60 frames late). Recorder = `tools\merge\mrec.py` (per-frame, uses the game's own frame counter).

### Merged build v1 (`patches\merged-v1`)

| # | Test | What | Result |
|---|---|---|---|
| a | m2-a-ctl2 (2 copies, test-m-roam) | P1 runs up, P2 runs right, P2 jumps, P1 jumps | **PASS.** Hero moved only in P1's window, twin only in P2's; each jumped only on its own Cross. (m2-a-ctl, same with crossing paths: the running hero pushed the standing twin 58 units; not a control leak.) |
| b | every probe of every twin test | engine player, last-built pointer, camera target, HUD owner | **PASS.** Always player 1's hero, also after room changes and after Continue. |
| c1 | m2-c-fight-idle (2 copies, test-m-fight) | both idle in the fight | **PASS.** Hero 20 -> 16 -> 8 -> 4 -> 2 HP, twin 20 -> 18 (one stray hit) and then unchanged. |
| c2 | m2-c-fight-redirect (ONE copy, test write) | the test keeps telling the engine the twin is its player | **PASS.** Twin 20 -> 3 -> 2 HP, hero stays 18. (The reverse direction needs this trick: see "still wrong" 1.) |
| c3 | m2-c-hp-door (ONE copy, test write, variant without the exit rule) | hero set to HP 7 / MP 60, twin to HP 13 / MP 40 away from the save point, then two room changes | **PASS.** Both keep their own values in the Borough and back in Merlin's house. (Standing on a save point refills the hero: the first attempt lost the written values that way.) |
| c4 | m2-c-hbf (2 copies, test-m-hbf) | fight with Donald and Goofy | **PASS.** Slots: 1 twin (marked), 2 hero, 3 Donald, 4 Goofy, 5+ enemies; no collision; hero 20 -> 11, Donald 18 -> 13 -> 17, twin 20. |
| d1 | m2-d-door-p2first (2 copies) | P2 walks into the door volume and waits; P1 walks in later | **PASS.** No room change while the twin is there alone (about 300 frames); change when the hero walks in; both arrive; roles, controllers and slots right; then each pad moves only its own hero. |
| d2 | m2-d-door-p1alone (2 copies) and control m2-h-solo-door | P1 walks into the door and pushes along it, the twin stays at the start | **PASS.** No room change. The SAME script on the disc without a twin changes the room at once, so it is the rule that stopped it, not the walk. |
| e | m2-e-newgame (2 copies, kh2-coop-v1.iso, 16,000 frames) | real New Game: opening skipped, two Roxas, tutorial boxes, each pad moves its own Roxas, then random buttons | **PASS.** Two Roxas (status id 14) at first control; hero plain slot / pad 1 / camera, twin marked slot / pad 2; the picture stays on player 1 (seen by eye, `sheet.png`). Random play stayed in the first area: the script gets no further than "approach the Armor Shop". |
| f | m2-f-save-continue + m2-f-continue (2 copies) | save to file 01, both out of the door; with the TEST-ONLY line "hero's HP held at 1": defeat, Continue | **PASS.** Save on both cards (byte-identical). Game Over, Continue with Circle, the room is rebuilt with the right roles, then each pad moves only its own hero (six move windows). |
| g | m2-g-sync-roam (34,000 frames), m2-g-sync-oneroom (34,000), m2-g-sync-fight (7,300) | random buttons on both pads after the scripted start | **PASS.** 531 / 531 / 114 digests, all screenshot pairs identical. The roam run has ONE room change (see "still wrong" 4). |
| h | m2-h-solo-door (2 copies, disc without twin) | one player object, patch on | **PASS.** Same pictures as the unpatched game (below). |

### Merged build v2 (`patches\merged-v2`)

| # | Test | What | Result |
|---|---|---|---|
| a, b | m2-v2-a-ctl (2 copies) | as v1 | **PASS.** Plus: hero's control object = S, twin's = S2, menu on screen = S. |
| d | m2-v2-d-roundtrip (2 copies) | out of Merlin's house, back in, out again; P2 steps 8 frames sideways into each door line first | **PASS.** Three room changes with both heroes; roles, slots and control objects right after each. |
| e | m2-v2-e-newgame (2 copies, kh2-coop-v1.iso, 16,000 frames) | as v1 | **PASS.** 250 digests, 7 of 7 screenshot pairs identical. |
| h | m2-v2-h-solo, m2-h-solo-door, m2-x-nopatch-solo | one player object: v2, v1, no patch, same buttons | **PASS.** Screenshots at frames 4480, 4900, 8000, 11900 are byte-identical in all three; S2 is never built. |
| i | m2-v2-i-attack (2 copies, test-m-fight, recorder) | only pad 2 presses Circle, then only pad 1, then both | **PASS.** Pad 2 only: twin attacking in 114 of 170 recorded frames, hero 0, enemy HP 60 -> 45. Pad 1 only: hero 93, twin 0, enemy HP 45 -> 22. Both: hero 120, twin 124, enemy HP 22 -> 6. |
| j | m2-v2-j-magic (2 copies, test-m-roam, TEST-ONLY skill kit) | P2 casts Fire three times (L1 + Circle), then P1 | **PASS.** Twin's MP 100 -> 88 -> 76 -> 64 while the hero stays 100; then hero's MP 100 -> 64 while the twin stays 64. |
| k | m2-v2-k-continue (2 copies, TEST-ONLY "HP held at 1"), m2-v2-d-roundtrip, m2-v2-h-solo | room change, Game Over + Continue, a disc without twin | **PASS.** After Continue: hero on S and pad 1, twin on S2 and pad 2, each pad moves its own hero. |
| l | m2-v2-l-sync-roam (34,000 frames), m2-v2-l-sync-fight (7,300) | random buttons on both pads | **PASS.** 531 / 114 digests, 8 of 8 and 4 of 4 screenshot pairs identical. |
| - | m2-v2-x-intact | patch words during a random fight | **PASS** (0 unexpected words at 4 checkpoints). |

Lane G's question "which hero's control object do game scripts reach": the engine's player pointer 0x0034E948 is
player 1's hero in every probe, and that hero's control object is S. So the 15 code sites that go through that
pointer land in S (player 1, on screen). VERIFIED for the pointers; no test ran an actual script command (HYPOTHESIS
for the effect).

Test-only patch variants (never part of the game patch): `patches\merged-v1-noexit` (without the exit rule, for
the one-copy HP test), `patches\merged-v1-test-die`, `patches\merged-v2-test-die` (one line: hero's HP held at 1),
`patches\merged-v2-test-kit` (lane G's skill lines).

## Still wrong or untested in the combined build

1. **Enemies attack only the engine's player (player 1's hero).** The twin is only hit by stray attacks
   (m2-c-fight-idle). Not changed by the merge.
2. **Either hero at 0 HP = the normal Game Over.** Hero case VERIFIED here (m2-f-continue, m2-v2-k-continue); twin
   case is lane D's finding, not repeated. "Down like Goofy" is Phase 2.
3. **Camera follows player 1 only**; the twin can walk out of the picture (m2-e-newgame sheet). No gauge and no
   menu on screen for player 2.
4. **Doors can be too narrow for the exit rule as it is.** The Borough's door back to Merlin's house is a box of
   100 x 180 units. The twin arrives 110 units beside the hero and, walking straight back, missed the box by 15
   units: both heroes pushed against the wall and nothing happened (m2-g-sync-roam, frames 5600-7300). With an
   8-frame sidestep it works (m2-v2-d-roundtrip). There is no "waiting for the other player" sign, and the heroes
   block each other. A human will meet this. Options: count the other hero as present within some distance of
   the volume, or place the arriving twin nearer the door line.
5. **Exit rule tested on one door pair only** (Merlin's house / Borough). Event triggers (kind 3) share the code;
   none was tested. Other trigger kinds still follow player 1 only (lane E).
6. **Not tested in the combined build:** Load Game with the twin's two save bytes, Drive Forms, Limits, Summons,
   items and Cure used on the other hero, Reaction Commands, lock-on (lane G tested it alone), other forms (lion,
   costumes), bosses, minigames, cutscenes that end in a fight, the 28 unproven twin spots, LAN / internet, humans.
7. **Player objects built outside the factory** (0x001B6850, HYPOTHESIS: Drive Form changes): `m_slot` gives them
   the game's own behaviour, so a form-changed twin would look up the hero's slot. Lane E and lane G do not cover
   this path either.
8. **Room nm07 (group b_99):** both heroes are real objects placed directly, not placeholders. Lane E's rule then
   makes the FIRST-built one player 1's hero, which on these discs is the copy lane F added on the side spot. One
   room; not tested.
9. **All variables and S2 rely on zero memory at boot** (not written by the patch file). Verified zero in the
   scenes listed; not for every world, movies, the Gummi Ship or a soft reset.
10. The first slot (0x01C6C750) belongs to the twin on these discs (clash 1). Lane G's test-only "HP held at 1"
    line and anything else written for the old layout must use the right slot.
11. The harness does not complain when `--patch-dir` points to a folder that does not exist: the run is then
    simply unpatched (this happened once here; that run was thrown away and repeated).

## Files of this lane

- `tools\merge\`: `make_all.py` (the generator), `g_cmd.py` + `g_asm.py` (copies of lane G's generator code),
  `asm.py`, `mips.py`, `pine.py`, `elfscan.py` (copies of lane E's helpers), `build_disc_m.py`, `mprobe.py`,
  `psum.py` (one line per probe), `mrec.py`, runners `mrun.sh`, `mrecrun.sh`, `mcave.sh`, script writers
  `make_scripts.py`, `make_scripts2.py`, test-only patch makers `make_testdie.py`, `make_testkit.py`.
- Button scripts: `tests\scripts\merge\`. One-off edit scripts and a copy of the tested v1 patch: `local\analysis\m\`.
- Patches: `patches\merged-v1`, `patches\merged-v2` (+ the four test-only variants named above).
- Discs: `local\iso\kh2-coop-v1.iso`, `test-m-roam.iso`, `test-m-fight.iso`; recipes and placement reports in
  `local\variants\m-*`.
- Emulator copies `local\run-m` (2) are left in place. No emulator of this lane is running.
- Not edited: other lanes' folders and patches, the shared tools, `docs\STATE.md`, the plan, the memory folder.
