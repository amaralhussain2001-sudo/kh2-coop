"""One-off: record the night session 2026-11-10 / 11 in docs/STATE.md (merged build 6, own-screen build with menu
rows per player, test build 4). Run once, AFTER the final validation: python -I tools/merge/add_session4_notes.py
<results file>   (a text file whose lines go into the "Final validation" block)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "## Merge 6 and test build 4" in t:
    raise SystemExit("already there")
facts = dict(l.split("=", 1) for l in pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if "=" in l and not l.startswith(" "))
results = "\n".join(l[2:] for l in pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.startswith("  "))


def rep(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("expected one place for %r (found %d)" % (old[:60], t.count(old)))
    t = t.replace(old, new)


start = t.index("## PICK UP HERE")
end = t.index("\n---\n", start)
pick = """## PICK UP HERE (rewritten 2026-11-11, after merged build 6 and test build 4)

Read this section first, then `..\\KH2-COOP-PLAN.md` (plan, rules, all user decisions; rows 10-13 are new) and
`REQUIREMENT-full-parity.md`. The rest of this file is the detailed record. Lane reports are in `docs\\lanes\\`.
The parity checklist is `docs\\PARITY-CHECKLIST.md`.

Where things stand:
- TWO builds, both on disc `local\\iso\\kh2-coop-v2.iso` (SHA-1 12edc56fdb0baac302c373e554185921242e6533, unchanged):
  * SHARED SCREEN = merged build 6: `patches\\merged-v6` (%(V6_WORDS)s words, SHA-1 %(V6_SHA)s) = merged build 5
    + own Drive values for the second hero + text boxes, START and the main menu on either controller + prizes
    for the second hero. Builder `tools\\merge\\merge_v6.py`. Section "Merge 6 and test build 4".
  * OWN SCREENS = `patches\\merged-v6-own` (%(OWN_WORDS)s words, SHA-1 %(OWN_SHA)s) = merged build 6 + lane V1's
    two views + lane V2's HUD per player + glue, now with THE COMMAND MENU'S ROWS PER PLAYER (builder
    `tools\\own\\make_own.py`, step 7). Needs the emulator build `emulator-src\\builds\\view12` and the settings file
    `patches\\own-view\\SLPM-66675_F266B00B.view` (both unchanged).
- The test package in `dist\\` is BUILD 4 (package id %(PKG_ID)s): own screens, with the shared-screen patch
  inside as a fallback file. %(PKG_NOTE)s No humans have played yet. The disc file did not change (TEST v2).
- TESTS MUST NOT DISTURB THE USER: every test emulator starts on a hidden Windows desktop
  (`tools\\quiet_launch.py`). Never use `--show` unless the user asks.
- A stopped suite keeps running unless its bash and emulator processes are killed too. After TaskStop, kill
  `suite_*.sh`, `mrun.sh`, `batch_v6.sh`, `run_own*.sh`, `kh2_session.py`, `v3_session.py` and the `local\\run-*`
  emulators (PowerShell, by command line; a script started with a relative path has no project path in its
  command line). One suite on `local\\run-m` at a time; `local\\run-v3` and `local\\run-v3b` are two more sandboxes
  (`tools\\own\\run_own2.sh` takes OWN_RUN_DIR / OWN_PORT), so three things can run at once.
- No lane (agent) is running. The user said: do NOT open extra lanes.

User answers and remarks of 2026-11-10 night:
- "why you stop continue until u finish for your question use the Recommended", later "continue until finish
  all the tasks": no stopping for A/B questions; take the recommended option, note it, go on down the list.
- Taken that way: the Magic-list fault fixed now; own Drive gauge for each hero; either player closes text boxes
  and opens / works the main menu; both heroes pick up prizes (plan rows 10, 12, 13).
- "is the money shared, but their skills different?": answered: one wallet and one item stock; level, skills and
  equipment are the same for both today; own skills / equipment stay a Phase 4 job unless the user asks sooner
  (plan row 11). The user has not answered that offer.

Next jobs, in order:
1. The first two-human test (the user's to do) with build 4; read the logs they send back.
2. Own screens, still open:
   a. text boxes and the "Waiting for the other player." sign are on both screens (kept on purpose: both players
      should see them; change only if the user asks);
   b. the menu's show / hide / fade follows player 1's control object only (lane V2 limit 2): on a shortcut-start
      fight disc both screens show an empty menu plate until player 1's first button press (seen in v3-orbs);
   c. a small orange glint beside player 2's gauge in the first town; the 2-3 step return of two views after a
      death or mission event;
   d. untested with two views: shop, journal pages, the game's own cross-fades; sound listener (HYPOTHESIS: stays
      with player 1's camera); the shop and the main menu's pages on controller 2.
3. Still missing for "player 2 exactly like player 1": helpers go with both heroes; item drops for the second
   hero (second pickup routine 0x001A5990, HYPOTHESIS); boss moves written against "the player"; Twilight Thorn
   and the other carried-hero Reaction Commands; rules / result screens of the small games on controller 2 (the
   script engine's button tests 0x0016DB98 / 0x0016DBE0 read controller 1; not changed, not needed for tutorial
   boxes); Drive Forms for the second hero (never tested; the own-Drive glue was tested without a form).
4. Prologue jobs that need real work (lane S1): Mail Delivery (second board), Grandstander (ball rule), the bag
   ride, the hit counters of two Nobody fights.
5. Feasibility tests continue down `docs\\PARITY-CHECKLIST.md` in story order.
6. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission (see "Merge 4" and
   the retry-record note there).
7. The PARK experiment (`tools\\own\\fork_views.py`, its header).
8. Open riddle: with the test kit (magic for a fresh save) the emulator log shows null reads at pc 0x0016E3C0
   (script routine 0x0016E378 asks the position of an effect object, class 0x00352B48, whose +0x1C is empty):
   24-32 lines per 34,000 random frames with ANY of our patches, old or new; none in the unmodified game with the
   same kit and buttons. No crash, no desync. Cause not found (recorder: `tools\\own\\make_diag_null.py`).

How to repeat: patches `python -I tools\\merge\\merge_v4.py`, `merge_v5.py`, `merge_v6.py`, then
`python -I tools\\own\\make_own.py` (own screens; base = merged-v6); disc `python -I tools\\merge\\build_disc_v2.py
kh2-coop-v2.iso`; suites `bash tools/merge/suite_v5.sh <patches\\merged-v6>` (shared) and `suite_v6.sh` (own
screens), own-screen batch `bash tools/own/batch_v6.sh` (log `local\\own-batch.log`); one own-screen run
`bash tools/own/run_own.sh <name> <iso> <frames> <speed> <snaps> <p1script> <p2script> <then> <upscale> [patchDir]`;
package `python -I tools\\package\\make_package_patch.py`, `python -I tools\\package\\make_test_package.py --rebuild`,
rehearsal copies `python -I tools\\package\\make_rehearsal_copies.py`, rehearsal `python -I
tools\\package\\rehearse.py ... --snapview`; emulator `powershell -File emulator-src\\build.ps1`.

Working habits that matter here: plain English, short sentences, lettered options with a recommendation (and
take the recommended one without waiting); every claim VERIFIED or HYPOTHESIS; never touch the original disc
file, `Desktop\\PS2-ONLINE`, `Desktop\\openkh` or `Desktop\\New folder\\digimon-online`; use absolute paths in
shell commands; write script files instead of inline heredoc Python when the text has quotes or backslashes;
tests run on the hidden desktop; never overwrite a patch folder that a running suite is using (build into a
`patches\\test-*` folder first). The emulator source carries the PCSX2 project's own rules for AI help
(`emulator-src\\pcsx2\\AGENTS.md`): nothing from this private copy may be posted to the PCSX2 project or its
GitHub by an agent.
""" % facts
t = t[:start] + pick + t[end:]

notes = r"""## Merge 6 and test build 4 (main session, night of 2026-11-10 to 11)

All tests on the hidden desktop, two linked copies, scripted or random buttons, own-view emulator (view12) for
the own-screen runs. Probes read memory only.

### 1. The command menu's rows per player (own-screen build only; `tools\own\make_own.py`, step 7)

- Fault (VERIFIED before, test u4-menu): a list opened by one player (Magic) showed on the other screen too.
- Cause (VERIFIED by reading the display's update 0x0013C938 and by the probe `tools\own\rows_probe.py`): the
  one display object keeps its rows in a table at display+0x18 (4 levels x 9 pointers; row class 0x003485B0,
  taken from a pool of 36 at [0x00348058], free list at pool+0x6E40, count +0x6ED0). Every update builds the rows
  its control object (display+0x29C) wants (factory 0x0013B5D0) and marks the others dead (0x0013B838; flag bit 0,
  the manager's sweep 0x001393F8 gives them back). Lane V2 points the display at player 2's control object for
  his HUD run, so each run killed the other player's rows and made its own again, in every step; the dying rows
  were still drawn.
- Fix: player 2 has his own copy of display+0x18..+0x103 (rows, level words, menu id, Reaction Command state),
  swapped into the display around his HUD run (`own_hud` in place of lane V2's `pv_hud`); the rows the display
  holds after his run get a mark (flag bit 30); marked rows are updated and drawn in player 2's picture only,
  unmarked rows not in his (`own_ufilter`, `own_filter` in front of lane V2's two filters). Hooks: 0x0013B128
  (display forgets its rows), 0x0013D4C8 (display removes all rows), 0x0013B498 (display ends).
- A second set of pools for player 2: one root menu alone takes 9 rows (VERIFIED: 18 of 36 used by two idle
  menus, 23 with one list open), so two players' lists can want more than 36. The game's pool routine now runs
  twice per display (hook 0x0013B394 on `jal 0x0013AD20`; freed twice at 0x0013B474), a new row comes from the
  pool of the player whose menu is being built (hook 0x0013ACC0) and goes back to the pool it came from (hook
  0x0013AB28, by address). VERIFIED (u8c-rows, u9-rt): 27 rows left in each pool with two root menus, 22 with a
  list open, 27 again after closing; pools are made anew in every room and nothing leaks over three room changes.
- Memory: routines 0x000F4000-0x000F43FF, variables 0x000F4400 (display that the copy belongs to), 0x000F4404 (1
  while player 2's state is inside the display), 0x000F4410 (the copy, 0xEC bytes), 0x000F4500/04/08 (player 2's
  pools). 0x000F4000-0x000F4FFF was lane S1's range and was never used.
- Results: u8-rows / x4-menu: each screen shows only its own Magic list and its own L1 shortcut list; the
  Reaction Command banner is steady per player. w1-anim: the list's open and close movement is the same, frame
  by frame over 13 frames, as in the shared-screen build (the "too fast" fault is gone).
- Seen and left: with the test kit player 2's banner shows a dim "Examine" in Merlin's house (his control object
  has command 0x1E in state 5; without the kit it has command 0). HYPOTHESIS: the game's own state for that
  spot with the kit's settings; not seen without the kit.
- "The Reaction Command changed" (display+0xFE, set through the one display pointer by either control object)
  is copied into player 2's state at the start of player 1's run, so both menus get it.

### 2. Own Drive values for the second hero (merged build 6)

- VERIFIED first (v1-drvgain, Drive set to 0 by a test line): inside a room each hero's unit slot has its own
  Drive values (slot+0x1B0 gauge, +0x1B1 bars, +0x1B2 max bars, +0x1B4 / +0x1B8 timers); player 2's hits filled
  only the twin's gauge (0 -> 8 while the hero stayed 0), player 1's only the hero's; each HUD gauge shows its own
  character's slot (gauge+0x34 -> +0x48C).
- What was shared: both slots save the 12 bytes into the save data (party block 0x0032E020 + 0x1038 =
  0x0032F058; routine 0x001A1840) and load them from there (0x001A11E0): after a room change both had the
  values of whoever was written last.
- Glue: load hook 0x001A12B4, save hook 0x001A18C0 (+ 0x001A18C4), refill hook 0x001ADBEC (the game's one "full
  Drive" routine 0x001ADBC0 refills the twin too). The twin's 12 bytes live at 0x000F47D0, "what player 1 wrote
  last" at 0x000F47C4, a valid flag at 0x000F47C0. If the save data holds anything else than what player 1 wrote
  last (loaded save, New Game, the story), both heroes take the save data's values. Max bars always come from
  the save data (common).
- Tests: v2-drvA (the twin's slot held at 55 / 1 bar by test lines): across three doors the save data kept
  player 1's 100 / 3 and the twin's copy held 55 / 1. v2-drvB (the copy held at 55 / 1): after the first door the
  twin's slot had 55 / 1, the hero's 100 / 3. Both 115 digests, in sync.
- NOT tested: a real gain carried through a door in one run, the refill hook, saving and loading, Drive Forms.

### 3. Text boxes, START and the main menu on either controller (merged build 6)

- Method: lane A's list of the 43 calls of the controller getter (0x00167F18); six patch variants, variant b
  switches every call whose index has bit b set to controller 2 (`tools\own\make_padbits.py`); the variants in
  which player 2's button works spell the index.
- Text boxes: call 0x001ACBD4 (the message window's update 0x001ACBC0). Tests y2-bit0..5 on the real New Game:
  the "Move the left stick" box closed on player 2's Circle exactly in variants 0-3 (index 15).
- START (open the main menu): call 0x00138538 (tests y4-startbit0..5: variant 1 only, index 2).
- The main menu's cursor: call 0x002893A0 (tests y5-menubit0..5: variants 0, 2, 3, 4, index 29). The menu pages
  add controller 1's buttons to a common record through 0x00287F90 (49 callers, getter call at 0x00287FA0).
- Glue: those four calls get a scratch record (0x000F4800, 0x60 bytes) from `pad_both` (0x000F4740): the four
  button words of both controllers OR-ed, the stick part from controller 1 or, when its stick is at rest, from
  controller 2.
- Tests on the final patch: y3-box-p2 (only player 2 presses Circle on the real New Game: the boxes close and
  play goes on), y6-start-p2 (player 2 opens the main menu with START, moves the cursor twice, closes it with
  START), z2-newgame-start (player 1's START scene skips: four pictures identical to the build before),
  y7-save-p2 (player 1 opens the save menu with Triangle on the save point; player 2's Down moves its cursor
  Save -> World Map -> Save and his Cross closes it), y8-skip-p2 (player 2 alone skips the opening movie and
  the first scene with START, Down, Circle: the picture at frame 5180 is the same as when player 1 does it).
- NOT changed: the script engine's two button tests (0x0016DB98 "held", 0x0016DBE0 "pressed", table entries
  0x0034DB30 / 0x0034DB38) read controller 1; a first try on them did not close the tutorial box
  (`tools\merge\make_padboth_test.py`, y1-box-both). HYPOTHESIS: rules and result screens of the small games use
  them. The shop and the pages inside the main menu (Status, Journal, Config) on controller 2: NOT tested.
- My own slip, for the record: I read the menu search the wrong way round twice (first "0x002B0960", then "the
  menu already listens to controller 2") before the pictures showed which variants had moved the cursor.

### 4. Prizes for the second hero (merged build 6)

- Fault (VERIFIED, v3-orbs: heroes made strong by a test line): enemies killed by player 2 dropped balls that
  lay beside his hero for 300 frames; the munny counter (0x0032DF70) stayed 0 until player 1's hero came near.
- Cause: the prize's update (0x001A5140) asks "party member N" for N = 0, 1, 2 (0x00176B20: the engine's
  player, then two friends) whether the prize is in reach (0x001C7950 -> 0x001A4FF8, radius widened by the asked
  character's slot+0x1C4); the one in reach gets it (0x001A5380: the prize flies to him, 0x001A52A8 gives HP by
  his own method, MP, Drive to his slot, munny to the wallet).
- Glue: the loop runs to N = 3 (word at 0x001A5258) and the call at 0x001A51F8 goes through `prize_cand`
  (0x000F4840): N = 3 is the other hero; every other prize (bit 6 of its address) asks the twin at N = 0 and
  player 1's hero at N = 3, so neither wins every prize when both stand in reach.
- Test v4-orbs: munny rose 0 -> 1 during player 2's own attack window with player 1 idle, 5 at the end (2
  before the change). HP by a ball on the twin: same routine, NOT seen in a test (he was never hurt).
- NOT changed: a second pickup routine 0x001A5990 (from 0x001C7ED4, 0x001D29C0) asks only the engine's player.
  HYPOTHESIS: item drops.

### 5. Null reads with the test kit (open)

- The emulator log counts "TLB Miss, pc=0x16e3c0 addr=0x0 [load]": script routine 0x0016E378 (table entry
  0x0034DA58) asks 0x001DC5F8 for an object's body pointer (object+0x1C) and reads through a null. The object
  (recorder `tools\own\make_diag_null.py`, test z1-diag) is a small heap object of class 0x00352B48 (constructors
  0x001DC1F8 / 0x001DC278, list head 0x00352AE0), not a hero.
- Counts over the same 34,000 random frames on the roam disc with the kit: old own-screen patch 24, new 24-32;
  random fight 12,000 frames: old 0, new 4; unmodified game + kit, one hero: 0. So it comes with our two-hero
  patches and the kit's magic, it is not new, and it never broke a run (all in sync, no crash).

### 6. Final validation

%(RESULTS)s

### 7. Files

- Builders: `tools\merge\merge_v6.py` (options `--no-drive`, `--no-box`, `--no-start`, `--no-prize`),
  `tools\own\make_own.py` (step 7 `add_menu_rows`; `--no-rows`; `--base`).
- Probes and helpers: `tools\own\findglobal.py`, `rows_probe.py`, `drive_probe.py`, `make_padbits.py`,
  `make_diag_null.py`, `diag_null_probe.py`, `run_own2.sh`, `batch_v6.sh`; `tools\merge\make_padboth_test.py`;
  `tools\package\make_rehearsal_copies.py`, `edit_readme_v4.py`; `tools\merge\add_plan_rows_v6.py`.
- Test scripts: `tests\scripts\own\box_*.txt`, `box2_*.txt`, `start_*.txt`, `start2_*.txt`, `menu2_*.txt`.
- Test-only patch folders (none is for play): `patches\test-own-rows*`, `test-own-drv0`, `test-own-v6*`,
  `test-v6-*`, `test-padbit0..5`, `test-own-padboth`, `test-kit-only`, and the older `test-own-kit`,
  `test-own-die2`.

""".replace("%(RESULTS)s", results)
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
p.write_text(t, encoding="utf-8")
print("state updated")
