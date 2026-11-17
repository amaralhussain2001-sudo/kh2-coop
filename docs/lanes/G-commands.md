# Lane G: each hero attacks and uses commands from its own controller

Written 2026-11-10. Game program CRC F266B00B (Kingdom Hearts II Final Mix, SLPM-66675), English-text copy build 2.
All tests: SINGLE-PC, two linked sandbox emulator copies (`local\run-g`, port 28950, PINE 28071) unless a line says
"one copy", scripted or random buttons, no humans. Labels: VERIFIED (test id / address) or HYPOTHESIS.

## Result

**WORKS.** With the patch `patches\lane-g-cmd-v3\SLPM-66675_F266B00B.pnach` the hero on controller 2 has its own
command controller. Attack, combos, jump, guard, dodge, magic through the shortcut buttons, Reaction Commands,
lock-on, menu cursor and shortcut mode all come from that hero's own controller and no longer touch the other
hero's. The on-screen command menu stays player 1's. Sessions stay in sync, and one player alone plays exactly as
without the patch.

Not solved here (other lanes or later work): HP and MP are still shared; player 2 has no menu on screen; things the
game addresses to "the player" (the last-built hero) land in that hero's command controller (see Open problems).

## 1. Measurements before the fix (step 1)

Discs: `test-b-ca5.iso` (Port Royal fight, Sora + twin) and `test-b-roam3.iso` (Merlin's house, Sora + twin, no
enemies). Reference: `test-b-roam.iso`, ONE Sora, no patch (tests g-ref1, g-ref2). Tool: `tools\lane-g\an_equiv.py`
compares, frame by frame from a button press, a hero's position change and action fields with the lone Sora of
the reference pressing the same buttons.

How to read a hero's state (VERIFIED by the pictures and by the reference run): object+0x154 = current action:
0 none, 2 run, 3 / 4 / 5 jump, fall, land, 0x97-0x9A ground attacks, 0xB5-0xB7 air attacks, 0xAD guard,
0xD1 dodge roll, 0xC9 high jump, 0xCA aerial dodge, 0x38 / 0x3B / 0x3E casting Fire / Blizzard / Thunder,
6 / 0xB / 0xD reactions to being hit (the last names are HYPOTHESIS). object+0xA0C is a serial number shared by
all attackers, not a per-hero counter.

| Question | Lane A patch `pad` (S->player stays the last-built hero) | Lane A patch `padplayer` (S->player = the hero being updated) |
|---|---|---|
| Player 2 presses Circle, player 1 idle (fight) | Only hero 2 swings: 137 of 180 recorded frames in an attack action, hero 1 none; enemy HP falls (g-m1-pad) | Same (g-m1-padplayer) |
| Player 1 presses Circle, player 2 idle (fight) | Only hero 1 swings (130 of 180), but its first press was ignored | Only hero 1 swings (157 of 180), first press accepted |
| Both press | Each swings; hero 1 lost half its presses (59 of 170 frames) | Both swing (120 and 133 of 170) |
| Is hero 1 exactly like a lone Sora? (quiet room, g-m2-*) | **No.** 5 of 6 comparisons differ: about 50 frames after the first press of a ground combo an extra attack starts, the jump landing drifts, the air combo differs | **Yes**, 6 of 6: ground combo, jump, air combo, alone, both at once and interleaved |
| Is hero 2 exactly like a lone Sora? | Yes | Yes |
| D-pad DOWN / UP on pad 2 | Moves the ONE menu cursor (S+0x90 0 -> 1 -> 0), which is the cursor on screen | Same |
| L1 (shortcut mode) | One flag in the one control object; the screen shows the shortcut list only for pad 1's L1 | Same |
| START | Only pad 1 opens the main menu; pad 2's START does nothing (not this lane: the pause code reads controller 1) | Same |

What this showed (VERIFIED):
- The combo itself lives in the player object, so two heroes can keep their own combos.
- A press becomes a "command request" inside the control object S (S+0x04.., written by 0x001BD918 through
  0x0017BFA0, cleared at the start of every update by 0x0017BF40) and the same hero reads it later in the same
  update, through its own pointer. That is why even the shared S gave each hero its own attack.
- With `pad`, S asked "may this player do that?" about the wrong hero (0x001BD918 calls 0x001B8F10 with S->player),
  which explains hero 1's lost presses and odd combo.
- Everything else in S was shared: cursor, open sub-menus, shortcut mode, Reaction Command, lock-on manager.

## 2. The design: a second control object (S2)

VERIFIED facts that make it possible:
- The game program addresses S (0x01C5F530, 0xB00 bytes, class table 0x00351260) directly in only a few places:
  the player base constructors (0x00177E14, 0x00177F9C: object+0xB3C = S, +0xB44 = S, +0xB40 = S+0xAC0), the attach
  routine (0x001781CC), two reset wrappers (0x00179BC8, 0x00179BE8) and S's own static constructor (0x0017A7E0).
  Every other use goes through the player object's pointers or through the pointer 0x003527E0
  ("current control object", used only by the global "commands off / on" routines 0x001D6C58 / 0x001D6C88).
- S is built by: base constructor 0x001BCF80, class table 0x00351260, three list inits (0x00190128 at +0xA68,
  +0xA7C, +0xA90), lock-on manager constructor 0x0019C920 at +0xAC0, +0xAF0 = 0. The same calls work on a second
  block of memory.
- A room load resets S with 0x001D68F8; the next hero that attaches (0x001D6938) is a "first attach" and sets
  S->player and S->pad from the hero (pad = object+0xB38).

The patch therefore gives the hero whose own controller (object+0xB38) is logical controller 2 (0x0034D720) a
second control object **S2**, built once with the game's own routines:
- S: player 1's hero, controller 1, the command menu on screen. Unchanged behaviour.
- S2: player 2's hero, controller 2, its own cursor, sub-menus, shortcut mode, command request, Reaction Command
  and lock-on manager. Not drawn.
- Lane A's per-update hook (0x00178898 / 0x001788A0 with the routine at 0x000F0020) is no longer needed: with one
  control object per hero, the original code is right again. Keeping it next to this patch is harmless
  (it rewrites the same values; test g-v3b-*).

Memory used: routines 0x000F0800-0x000F0AD3 (inside lane G's area), and **S2's data at 0x000F1000-0x000F1AFF**.
The data block is OUTSIDE the routine area given to this lane, because 0xB00 bytes do not fit in it. It must be
zero at start (it is: checked in every recorded run) and nothing else may use it. The main lane should either
reserve it or give another address (one constant, `S2`, in `tools\lane-g\make_cmd.py`).

## 3. The patch

File: `patches\lane-g-cmd-v3\SLPM-66675_F266B00B.pnach`, made by `python -I tools\lane-g\make_cmd.py <outDir>`.
Options: `--no-pad-rule` leaves out lane A's controller rule (for merging with lane E, which owns that hook; folder
`patches\lane-g-cmd-v3-no-pad-rule`), `--no-hud-pin` leaves out the four on-screen-menu hooks.
Full listing with every instruction and comment: `patches\lane-g-cmd-v3\listing.txt`.

### Hook sites (what the main lane needs for merging)

| Address | Was | Now | Purpose |
|---|---|---|---|
| 0x001781C4, 0x001781C8 | `lui a0,0x1C6` / `ld ra,8(sp)` (tail of the player's attach routine 0x001781A8) | `j attach` / `a1 = object` | A hero on controller 2 gets object+0xB3C = +0xB44 = S2, +0xB40 = S2+0xAC0 and attaches to S2; any other hero attaches to S as before |
| 0x001D6A10 | `lui t7,0x35` (end of detach 0x001D69D0, which set 0x003527E0 = 0) | `j detach_tail` | After any detach: 0x003527E0 = S if S still has a hero, else 0 |
| 0x00179BFC | `j 0x001D68F8` (room reset wrapper) | `j reset` | Room load resets S, then S2 if it exists |
| 0x00179BDC | `j 0x001D68E0` (start-up reset wrapper) | `j ginit` | Same for the start-up reset |
| 0x001D6C58, 0x001D6C5C | start of global "commands off" | `j disable` / `nop` | Applies to S and to S2 |
| 0x001D6C88, 0x001D6C8C | start of global "commands on" | `j enable` / `nop` | Applies to S and to S2 |
| 0x00174400, 0x00174404 | script command "player commands on" (table entry 0x0034E770); acted only on the last-built hero's control object | `j enable` / `nop` | Applies to S and to S2 |
| 0x0013B258, 0x0013B25C | `jr ra` / `sw a1,0x29C(a0)`: on-screen menu "use this control object" | `j setdisp` / `nop` | If S2 asks, S is shown instead (menu stays player 1's) |
| 0x001BDC64 | `jal 0x0013B2F8` (control object shows the menu) | `jal hudshow` | Skipped for S2 |
| 0x001BDCA4 | `jal 0x0013B320` (control object hides the menu) | `jal hudhide` | Skipped for S2 |
| 0x001BDE30 | `jal 0x0013B2B8` (control object sets the menu's fade value) | `jal hudfade` | Skipped for S2 |
| 0x0017A000 (+ 0x000F0000-0x000F000F) | lane A's controller rule, unchanged | | Only with the default options; lane E owns it |
| 0x00178898, 0x001788A0 | lane A's per-update hook | **not patched** (original code) | |

Routines (all in 0x000F0800-0x000F0AD3): `ensure` (build S2 once; its first word is 0 until then), `fixcur`,
`attach`, `detach_tail`, `reset`, `ginit`, `disable`, `enable`, `setdisp`, `hudshow`, `hudhide`, `hudfade`.

Versions: v1 = second control object (attach, detach, room reset, global off / on). v2 = v1 + start-up reset +
script command "player commands on". v3 = v2 + the four on-screen-menu hooks. v1 and v2 folders are kept for the
record; v3 is the one to use.

## 4. Tests

Recorded once per video frame through PINE (read-only): both heroes (0xB80 bytes each), S and S2 (0xB00 bytes
each), both pads, unit slots. Session frame = the game's pad counter (0x0034D4BC, +1 per video frame) + 152.

All lines below are for patch v3 (`suite.py v3 ...`, summary `local\analysis\g\suite-v3-part1.txt` and
`suite-v3-part2.txt`); v1 and v2 gave the same results in the same tests (`g-v1-*`, `g-v2-*`).

| Test (folder `local\tests\`) | What it does | Result |
|---|---|---|
| g-v3-solo (one copy) | ONE Sora, no twin (`test-b-roam.iso`), patch on, same buttons as the no-patch run g-ref2: ground combos, jump, air combo, D-pad, Triangle, L1, START | VERIFIED: hero object, S, unit slots and controller data byte-identical to the no-patch run in all 945 recorded frames; S2's memory stays all zero (never built) |
| g-v3-roam | Quiet room, Sora + twin. Each pad alone, both at once, and interleaved: ground combo, jump, air combo. Then D-pad, L1, START from each pad | VERIFIED: 12 of 12 comparisons "same as the lone Sora" for both heroes. Cursor: pad 1 DOWN moves only S's (1, 0), pad 2 DOWN only S2's (0, 1). L1 sets shortcut mode only in the own control object. Picture: cursor and shortcut list follow pad 1 only. In sync (102 digests) |
| g-v3-fight | Port Royal fight (`test-b-ca5.iso`). Frames 4700-5000 only pad 2 presses Circle, 5100-5400 only pad 1, 5500-5800 both | VERIFIED: pad 2 window: hero 2 in attack actions in 137 of 180 recorded frames, hero 1 in 0; enemy HP 10,10,10,10,10,10 -> 5,3,8,5,10,0. Pad 1 window: hero 1 142 of 180, hero 2 0; enemy HP falls further. Both: 137 and 122 of 170. In sync (100 digests) |
| g-v1-fight (lock-on part) | Same run, R1 from each pad | VERIFIED: before R1 each control object has its own nearest target (S 0x01AFB950, S2 0x01B005C0). Pad 2's R1 locks only S2's manager (state 1 -> 2), pad 1's R1 only S's. Two lock-on rings are on screen |
| g-v3-kit | Quiet room with the TEST-ONLY skill kit: Square, stick + Square, L1 + Circle / Triangle / Square, Cross twice, from each pad | VERIFIED: hero 1 and hero 2 each do guard, dodge roll, Fire, Blizzard, Thunder, high jump, aerial dodge; actions started by the wrong pad: 0. MP is shared: 100 -> 10. Each pad opens and closes the Magic list of its own control object (S2's unseen). In sync (100 digests) |
| g-v3-react | Hero 1 stands on the save point; pad 2 walks hero 2 onto it and presses Triangle | VERIFIED: "Save" (command 0x37) is offered to both control objects; pad 2's Triangle opens the SAVE menu (picture p1_f004915.png). The save menu itself is then operated by pad 1. In sync (82 digests) |
| g-v3-room | Pad 2 walks the twin out of Merlin's house; in the Borough each pad moves, jumps, attacks, moves its cursor | VERIFIED: both control objects are released at the room change and attach to the new heroes (S: hero 1 + controller 1, S2: hero 2 + controller 2); every action goes to the right hero. In sync (99 digests) |
| g-v3-die | Free roam with twin, TEST-ONLY line "HP held at 1": Game Over, pad 1 chooses Continue, several times | VERIFIED: 6 attach / 6 release cycles of both control objects, play continues after each Continue. In sync (206 digests), pictures of the two copies identical |
| g-v3-friends | Hollow Bastion fight with Donald, Goofy AND a twin (`test-g-friends`), then random buttons; the mission ends in its cutscene and jumps to another world | VERIFIED: pad 1 window: hero 1 105 of 180 frames attacking, hero 2 0; pad 2 window: hero 2 100, hero 1 0. Cutscene: both released; next room has no twin: S attached, S2 stays unused, play goes on. In sync (187 digests, 12,000 frames) |
| g-v3-ca5rand | Port Royal fight, RANDOM buttons on both pads, frames 4690-7800 | VERIFIED: never out of sync (121 digests); both heroes move, jump, attack |
| g-v3-long | Free roam with twin, room change, then RANDOM buttons on both pads until frame 34,000 | VERIFIED: never out of sync (531 digests). Both heroes fight all over the Borough; both control objects use cursor rows 0-3, shortcut mode and lock-on states 0 / 1 / 2 |
| g-v3b-solo / -roam / -fight | v3 with lane A's per-update hook left in (as lanes D and E still have it) | VERIFIED: same results as v3 (identical / 12 of 12 / same fight numbers), in sync |
| pictures | Every screenshot of g-v3-roam, -fight, -kit against the same test under v2 | VERIFIED: 60 of 60 byte-identical (the on-screen-menu hooks change nothing in these scenes) |

The two control objects were switched on and off together in every recorded sample of every run
(S+0x20 bit 0, S+0xA18 bit 0, S+0xAF0, compared with S2's).

Not shown by any test: that S2 would take over the on-screen menu without the v3 hooks. In all scenes hero 1 is
updated after hero 2, so S always won. The hooks are a safeguard for when the build order of the heroes changes
(HYPOTHESIS that it would matter then; the mechanism in section 5 is VERIFIED from the code).

Success test of the directive: player 1 idle while player 2 mashes Circle = only the twin swings and enemies lose
HP (g-v3-fight, first window); the reverse (second window); both at once (third window, and g-v3-roam where each
hero's combo equals the lone Sora's frame for frame); two-copy random session in sync (g-v3-ca5rand, g-v3-long).

## 5. What a drawn menu for player 2 needs

VERIFIED:
- The command menu on screen is ONE display object: pointer at 0x003484A0, 0x2B8 bytes, built by 0x0013B348,
  drawn by 0x0013C938. It reads everything (open menus at +0x9E8 / +0x8C0, cursor, Reaction Command at +0xA1E) from
  the control object whose address is stored at **display+0x29C**.
- display+0x29C is set by 0x0013B258, called when a control object is switched on (0x001D6AE0 -> 0x0013B348).
  Without the v3 hooks the last control object switched on would win.
- So showing player 2's menu is a matter of pointing display+0x29C at S2. The data is already complete in S2:
  in the tests player 2 moved a cursor, opened the Magic list and closed it without seeing it.

Two ways, both untested (HYPOTHESIS):
1. Own screens (plan Phase 1C / 2B): before player 2's picture is drawn, set display+0x29C = S2, before player 1's
   back to S. One display object is enough. To check: the display object keeps animation state (cursor slide,
   opening animation) that would be shared between the two views.
2. Shared screen: a second display object for S2 at another place on the screen. Needs the display's constructor
   (0x0013B088), its layout data and its draw call to be used twice; more work.
Lock-on rings are already drawn for both heroes (seen in test g-v1-fight, frames 6110-6290).

## 6. Open problems

1. **S2's data block is outside this lane's routine area** (0x000F1000-0x000F1AFF). See section 2.
2. **"The player" in script commands.** 15 places reach a control object through the last-built-hero pointer
   0x0034E948 (script-command routines 0x00174374-0x001744F8 from the table at 0x0034E7xx, 0x00198920 / 0x00198994,
   0x002BFA6C-0x002BFB60, 0x002EB354). Before this patch they all landed in the one S. Now they land in the control
   object of whichever hero was built last (today the twin, so S2, which is not on screen). Only "player commands
   on" (0x00174400) is redirected to both. When lane E makes hero 1 "the player", these go to S again. Until then a
   Reaction Command handed out by an event script would be offered to player 2 only. Not seen in the tests
   (Save and Examine come from the per-hero scan and were offered to the right hero), but not ruled out.
3. **Player 2 sees nothing of its own menu**: no cursor, no shortcut list, no Reaction Command prompt. The menu
   sounds of player 2's cursor are heard.
4. **Shared HP and MP** (lane D): magic cast by either hero takes MP from the same bar (test kit: 100 -> 10).
5. **Not tested through S2:** items, Drive Forms, Limits, Summons, party commands, the second menu page, form
   changes and the special player objects (they use the same base constructor, so the attach hook should cover
   them: HYPOTHESIS), event scripts that switch commands off and on (the hooks are in place; the two control
   objects' on / off state was equal in every recorded sample).
6. **START / pause, the main menu, the save menu** still listen to controller 1 only (not this lane). Player 2 can
   open the save menu with a Reaction Command, but only player 1 can operate or close it.
7. **Low memory.** 0x000F0C00-0x000F0FFF and 0x000F1B00-0x000F1FFF stayed zero in every recorded run, so nothing
   else seems to use this region in the scenes tested. Not checked: other worlds, movies, the title demo loop.
8. Tests are scripted or random buttons on one PC. No human has played it yet.

## 7. How to repeat

```
python -I tools\kh2_session.py make 2 --run-dir run-g
python -I tools\lane-g\make_cmd.py patches\lane-g-cmd-v3
python -I tools\lane-g\make_kit.py patches\lane-g-cmd-v3 patches\lane-g-test-kit-v3      (test only: skills)
python -I tools\lane-g\make_die.py patches\lane-g-cmd-v3 patches\lane-g-test-die-v3      (test only: HP held at 1)
python -I tools\lane-g\m_ref.py g-ref1 -          (reference: one Sora, no patch; also g-ref2)
python -I tools\lane-g\suite.py v3 patches\lane-g-cmd-v3 patches\lane-g-test-kit-v3 patches\lane-g-test-die-v3
```
The suite prints one summary per test and writes `local\analysis\g\suite-v3.txt`.

## 8. Files of this lane

- `tools\lane-g\`: `make_cmd.py` (the patch), `asm.py` (small assembler with labels), `glib.py` (run a session and
  record memory once per frame), measurements `m_attack.py`, `m_roam.py`, `m_ref.py`, `m_room.py`, `m_kit.py`,
  `m_react.py`, `m_die.py`, `m_friends.py`, `m_ca5rand.py`, analysis `an_equiv.py`, `an_same.py`, `an_fight.py`,
  `an_long.py`, `an_timeline.py`, `an_fields.py`, `suite.py`, test-only patch makers `make_kit.py`, `make_die.py`,
  helpers `find_counter.py`, `cmd_names.py`, `gh.sh`.
- Patches: `patches\lane-g-cmd-v3` (use this), `-v3-no-pad-rule`, `-v1`, `-v2`; test-only folders
  `lane-g-test-kit-v*`, `lane-g-test-die-v*`, `lane-g-test-v3-plus-hookB`, `lane-g-base-pad`, `lane-g-base-padplayer`.
- Test disc of this lane: `test-g-friends` (Hollow Bastion fight with Donald, Goofy and a twin). The 4.3 GB disc
  file was deleted after the tests; the recipe is kept in `local\variants\g-friends`. Rebuild:
  `local\dotnet\dotnet.exe local\build\Kh2Tool\Kh2Tool.dll inject "local\iso\Kingdom Hearts II - Final Mix (English text).iso" local\iso\test-g-friends.iso local\variants\g-friends\built report.txt`
  (needed for the `friends` part of the suite).
- Decompiled text and tables: `local\analysis\g\` (`s1.txt`-`s6.txt`, `hud1.txt`, `hud2.txt`, `cmd_names.txt` = the
  game's 751 commands with English names).
- Ghidra project copy: `local\ghidra-g`. Emulator copies: `local\run-g`.

## 9. Addresses found (CRC F266B00B)

| Thing | Address | Status |
|---|---|---|
| Control object S | 0x01C5F530, 0xB00 bytes, class table 0x00351260, static constructor 0x0017A7E0 | VERIFIED |
| S+0x04.. | command request for this update | VERIFIED (code) |
| S+0x20 | flags: bit 0 = commands off, 0x02 = shortcut mode (L1 held), 0x40 = this object has shown the menu | VERIFIED (records + code) |
| S+0x24 + n*0x74 | 19 menus; cursor of a menu at +0x6C (root menu cursor = S+0x90) | VERIFIED |
| S+0x8C0, S+0x9E8 | pointer to the top of the open-menu stack, the stack (4 entries) | VERIFIED |
| S+0x9E0, S+0x9E4 | player object, logical controller | VERIFIED |
| S+0xA1E, S+0xA21 | Reaction Command offered (command number), its state (0 = usable, 5 = none) | VERIFIED for Save (0x37) |
| S+0xA30..0xA3C | stick copy read by the hero's movement code | VERIFIED (lane A) |
| S+0xAA4 | menu page (0 or 6) | VERIFIED (code) |
| S+0xAC0 | lock-on manager: +0 state (0 none, 1 nearest target, 2 locked), +4 target object, +0x28 owner | VERIFIED |
| S+0xAF0, +0xAF4, +0xAF8 | flags, attached hero, start-up countdown | VERIFIED |
| Player object +0xB38 / +0xB3C, +0xB44 / +0xB40 | own controller / control object / lock-on manager | VERIFIED |
| Attach, detach | 0x001D6938 (from 0x001781A8), 0x001D69D0 (from 0x001781E8) | VERIFIED |
| Control object update | 0x001D6BA0 -> 0x001BD6A8, called by player method 0x00178888 through object+0xB3C | VERIFIED |
| Room reset, start-up reset | 0x001D68F8 (wrapper 0x00179BE8, called by the room-load routine 0x00169210), 0x001D68E0 (wrapper 0x00179BC8) | VERIFIED |
| Global commands off / on | 0x001D6C58 / 0x001D6C88, pointer 0x003527E0 | VERIFIED |
| Script command table | 0x0034E700.. pairs (routine, argument info) | VERIFIED |
| On-screen command menu | display pointer 0x003484A0; its control object at +0x29C (setter 0x0013B258); show 0x0013B2F8, hide 0x0013B320, fade value 0x0013B2B8, draw 0x0013C938 | VERIFIED |
| Frame counter | 0x0034D4BC (+1 per video frame) | VERIFIED |
| Save data used by the test kit | abilities save+0x2544 (16-bit, 0x8000 = equipped), magic levels save+0x3594..0x3597, shortcuts save+0x36F8 (4 command numbers); save = 0x0032BB30 | VERIFIED on screen (Magic list, shortcut list, guard, dodge, high jump, aerial dodge) |
| Command numbers | Attack 0x01, Potion 0x17, Guard 0x23, Fire 0x31, Thunder 0x32, Blizzard 0x33, Cure 0x34, Save 0x37 | VERIFIED (CMD table + English text) |
