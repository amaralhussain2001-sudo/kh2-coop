"""One-off: record the second half of the 2026-11-10 evening session in docs/STATE.md
(merged build 5, own-screen build, emulator build view12, hidden test desktop, test package build 3).

  python -I tools/merge/add_session2_notes.py "<one line about the own-screen suite result>"
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "## Own screens joined" in t:
    raise SystemExit("already there")
suite_line = sys.argv[1] if len(sys.argv) > 1 else "NOT RUN TO THE END (see local\\m6-suite.log)"

start = t.index("## PICK UP HERE")
end = t.index("---\n\nUpdated 2026-11-10. Read with")
pickup = r"""## PICK UP HERE (rewritten 2026-11-10 late evening, after the own-screen build)

Read this section first, then `..\KH2-COOP-PLAN.md` (plan, rules, all user decisions) and
`REQUIREMENT-full-parity.md`. The rest of this file is the detailed record. Lane reports are in `docs\lanes\`.
The parity checklist is `docs\PARITY-CHECKLIST.md`.

Where things stand:
- TWO builds, both on disc `local\iso\kh2-coop-v2.iso` (SHA-1 12edc56fdb0baac302c373e554185921242e6533: English
  build 3, twin in every room, bosses +75 % HP, Pete at Olympus +40 %):
  * SHARED SCREEN = merged build 5: `patches\merged-v5` (1,438 words, SHA-1
    ac7470c63594e8126aaff0c41bfb62110bcf198c). Section "Merge 4" + "Merge 5".
  * OWN SCREENS = `patches\merged-v6-own` (2,683 words, SHA-1 59f86b04e7b55d4cbd4fb9b215e7bf2e8d7adb5a) = merged
    build 5 + lane V1's two views + lane V2's HUD per player + glue. Needs the emulator build
    `emulator-src\builds\view12` and the settings file `patches\own-view\SLPM-66675_F266B00B.view`.
    Section "Own screens joined".
- The test package in `dist\` is BUILD 3 = OWN SCREENS (package id 35228b5c127c), with the shared-screen patch
  inside as a fallback file. Rehearsed through the launchers. The user has the steps. No humans have played yet.
- TESTS MUST NOT DISTURB THE USER: every test emulator starts on a hidden Windows desktop
  (`tools\quiet_launch.py`; section "Hidden test desktop"). Never use `--show` unless the user asks.
- A stopped suite keeps running in the background unless its bash and emulator processes are killed too (it
  happened once and two suites disturbed each other). After TaskStop, kill `suite_*.sh`, `mrun.sh`,
  `kh2_session.py` and the `local\run-*` emulators, and run only one suite on `local\run-m` at a time.
- No lane (agent) is running. The user said: do NOT open extra lanes.

User answers and remarks of 2026-11-10 (evening):
- Boss HP limit = A (gauge patch); Pete in the cave = +40 %. DONE (merge 4).
- No "1P / 2P" signs over the heroes' heads (a marker on a map would be fine). DONE (merge 4).
- "The camera shows the main person in both clients" = own screens wanted now. DONE as test build 3.
- "The Drive bar, each person will have his own?" ASKED BACK, NOT ANSWERED: (A) own Drive bar for each hero
  (recommended) or (B) one shared bar. Today: one Drive value for both; nothing built for either.
- "Each time you open something the focus goes from Black Desert into yours": DONE, hidden test desktop.

Next jobs, in order:
1. Wait for the first two-human test of build 3 (own screens); read the logs they send back.
2. Own screens, still open: text boxes and the "Waiting for the other player." sign are on both screens;
   player 2's command menu sub-menus (Magic, Items) and the L1 shortcut list untested; the menu's open and close
   movements run twice per step; a small orange glint beside player 2's gauge in the first town; shop, journal,
   Continue after Game Over, the game's own cross-fades, a room round trip and 16:9 untested with two views; the
   2-3 step return of two views after a death or mission event; pace in busy fights (the world is drawn twice and
   player 1's picture still passes through main memory); sound listener stays with player 1's camera
   (HYPOTHESIS); START and the full-screen menus for player 2.
3. Still missing for "player 2 exactly like player 1": helpers go with both heroes; HP orbs for the twin; START
   and menus for player 2; boss moves written against "the player"; Twilight Thorn and the other carried-hero
   Reaction Commands (the user wants BOTH heroes in the move); the Drive bar (question above).
4. Feasibility tests continue down `docs\PARITY-CHECKLIST.md` in story order (done so far: Twilight Town
   prologue, Gummi Ship study, special-mode "second copy" checks).
5. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission. Every mission test
   disc starts with a shortcut jump, and there Continue crashes also in the UNMODIFIED game (section "Merge 4").
6. The PARK experiment (keep player 1's picture inside the graphics chip: no trip through main memory, so a
   faster step and no picture-quality rule from the two-view code): the words of the command menu disappear
   when the display buffer's memory is used for it; cause not found (`tools\own\fork_views.py`, its header).

How to repeat: patch `python -I tools\merge\merge_v4.py`, `merge_v5.py`, then `python -I tools\own\make_own.py`
(own screens; `--plain` = without the emulator markers); disc `python -I tools\merge\build_disc_v2.py
kh2-coop-v2.iso`; suites `bash tools/merge/suite_v5.sh` (shared) and `suite_v6.sh` (own screens; logs
`local\m5-suite.log`, `local\m6-suite.log`); own-screen pictures `python -I tools\lane-v3\v3_session.py run ...
--exe1/--exe2 emulator-src\builds\view12\pcsx2-qtx64.exe --view-file patches\own-view\... --snapview1 1
--snapview2 1`; package `python -I tools\package\make_package_patch.py`, `python -I
tools\package\make_test_package.py --rebuild`, rehearsal `python -I tools\package\rehearse.py ... --snapview`
(two copies of the test folder with the disc in `local\kit-test-t\A` and `B`); emulator `powershell -File
emulator-src\build.ps1` (source change recorded in `emulator-src\patches\ownview-view12.patch`).

Working habits that matter here: plain English, short sentences, lettered options with a recommendation; every
claim VERIFIED or HYPOTHESIS; never touch the original disc file, `Desktop\PS2-ONLINE`, `Desktop\openkh` or
`Desktop\New folder\digimon-online`; use absolute paths in shell commands; write script files instead of inline
heredoc Python when the text has quotes or backslashes (inline heredocs broke three times); tests run on the hidden
desktop. The emulator source carries the PCSX2 project's own rules for AI help (`emulator-src\pcsx2\AGENTS.md`):
nothing from this private copy may be posted to the PCSX2 project or its GitHub by an agent.

"""
t = t[:start] + pickup + t[end:]

notes = r"""## Merge 5 (main session, 2026-11-10 evening): player 2's gauge rings hide with player 1's

- What the user had seen: in the first town the game shows player 1's gauge as a face only, player 2's small
  gauge kept its rings.
- How the game does it. VERIFIED by reading the program and by a read-only memory probe (`tools\merge\
  gauge_probe.py`, tests g1-town / g1-roam): the player gauge hides its parts when its hero's unit slot has bit 1
  (value 2) in the flag word at slot+0x250 (code around 0x001567B0). The word is 7 in the first town and 1 in a
  normal room; the twin's slot carries the same bits (plus lane D's bit 31).
- Which parts of the small gauge. VERIFIED by hiding each part in turn in one-copy tests (`tools\merge\
  gauge_parts_test.py`, g2-parts, g4-parts-town): gauge+0x6CC = HP ring, +0x868 = MP ring, +0x394 = the dark ring
  under them, +0x40 = the face (flag word at part+12, 0x40 = hidden).
- Patch: `tools\merge\merge_v5.py` -> `patches\merged-v5` (1,438 words, SHA-1
  ac7470c63594e8126aaff0c41bfb62110bcf198c) = merged-v4 + 35 glue words at 0x000F3440-0x000F34CB; the only
  changed word is lane V2's class table entry 0x000F7004 (update method -> the glue, which calls lane V2's update
  first and then sets or clears the hidden flag of the three ring parts from PLAYER 1's hero's slot flag).
- VERIFIED: first town: the small gauge is the face only (`local\tests\g3-compare\crop.png`); a normal room:
  picture byte-identical to merged build 4. Suite `tools\merge\suite_v5.sh` (`local\m5-suite.log`): ALL NINE runs
  never out of sync, every screenshot pair identical, attack windows 146/0, 130/0, 113/137, one player alone
  byte-identical to builds 2-4.
- A first run of this suite was spoiled: an earlier suite that I had stopped with TaskStop was still running in
  the background and the two fought over `local\run-m`. Rule now in the pick-up section.

## Own screens joined (main session, 2026-11-10 evening): `patches\merged-v6-own` + emulator build view12

- Tool `tools\own\make_own.py`: word-level join of (merged-v2 + lane V1's views + lane V2's p2gauge and perview
  sections, built by the lanes' own generators) with everything the merged build added since (lanes R, H, N, B75,
  the glue routines). It checks that no address is written by two sides. Result `patches\merged-v6-own`, 2,683
  words, SHA-1 59f86b04e7b55d4cbd4fb9b215e7bf2e8d7adb5a, with `listing.txt`. No 1P/2P markers.
- Lane V2's per-view HUD worked on lane V1's FINAL full-size pipeline as it was: player 1's HUD is drawn at the
  two-view task of priority 90000 (before player 1's picture is captured), player 2's at 90130 (before the 2D
  part opens). Nothing had to be re-aimed.
- VERIFIED with two linked copies, own-view emulator on both, snapshots of what each PC shows (`--snapview`):
  | Test | Result |
  |---|---|
  | o20-roam / o1-roam | each PC shows its own hero behind its own camera; own command menu cursor (player 2 moved it down twice: only in player 2's picture); "Save" prompt only for the hero on the save point; own big gauge + the other player's small gauge; 85 digests, never out of sync |
  | o21-menu, o30-menu (4x) | START: both PCs show the complete pause menu; own views come back after it closes. Lane V3's "frozen view, no menu" fault did NOT appear in the joined build |
  | o22-fight, o31-fight (4x) | Port Royal fight: own lock-on ring per picture, own menu, both cameras; in sync |
  | o23-newgame, o32-newgame (4x), o24-pg-town | New Game on kh2-coop-v2.iso: two Roxas, each PC its own; all gauges are faces only in the first town (see the ring rules below); 140 digests |
  | o25-4x / o26-keep-1x / o26-keep-4x | sharpness, see "keep" below |
- Ring rule for own screens (glue in `make_own.py`): the small gauge of player 1's hero in player 2's picture
  uses merged build 5's routine; player 2's own BIG gauge (a second player gauge object, built before it has its
  hero, so the game's own rule misses it) gets the 13 parts hidden that differ between the first town and a
  normal room in player 1's gauge (offsets in the tool). Left over: a small orange glint beside player 2's gauge
  in the first town.
- PLAYER 1's SHARPNESS ("keep"). VERIFIED fault first (o25-4x): at 4x player 1's 3D picture was blocky (it
  passes through main memory at the PS2's own 512 x 416), player 2's sharp. FIX, emulator side, game flow
  unchanged: `tools\own\fork_views.py` makes `tools\own\views.py` (lane V1's generator + two LABEL register
  writes: 0x56310003 before the game's capture, 0x56310004 after its loader); emulator build view12 keeps a copy
  of the draw buffer at its own resolution at the first and puts it into the frame buffer at page 112 at the
  second (`GSTextureCache::KeepViewTarget / PasteViewTarget`; settings `KeepSaveId`, `KeepRestoreId`,
  `KeepRestoreBlock` in the .view file). VERIFIED: at 4x player 1's picture is as sharp as player 2's
  (`local\tests\o26-cmp\crop.png`); at 1x it differs from the plain arrangement in 0.89 % of the pixels by 1
  colour step at most; in sync at 1x and 4x. An emulator without the change ignores the two writes.
- Emulator build view12: `emulator-src\builds\view12\pcsx2-qtx64.exe` (SHA-256 5a6ca0356a424c04...), source
  change `emulator-src\patches\ownview-view12.patch` (lane V3's view10 change + one marker id per player
  `Marker1Id`..`Marker4Id`, `MarkerAllId`, and keep/paste; made by `tools\own\emu_keep_edit.py` and hand edits).
  Settings file to ship: `patches\own-view\SLPM-66675_F266B00B.view`.
- BOTH PCs MUST USE THE SAME PICTURE QUALITY (upscale) with this game: the game reads pictures back into main
  memory, so different values give a false "OUT OF SYNC" (lane V3, VERIFIED there). The package starts at 4x and
  its read-me says so. With own screens this matters in every step, not only after a pause screen.
- Combined suite on the own-screen build (`tools\merge\suite_v6.sh`, the package's own emulator exe, so the game
  draws two views but every copy shows player 1's): SUITE_RESULT
- THE PARK EXPERIMENT (not used). Idea: keep player 1's picture inside the graphics chip (copy draw buffer ->
  display pages at 90000 and back to page 112 at 90130 or at the end) instead of the trip through main memory;
  both PCs then show a copy taken at their own marker. It ran in sync and both pictures were right EXCEPT that
  the words of the command menu (Attack, ?, Save) were missing in both. Found (tests o3-o18): only the executed
  copy into the display pages removes them (same packet with TRXDIR = 3: words there; top half only or bottom
  half only: gone; the copy back alone: harmless); the same on the software renderer, so it is the game, not the
  emulator. HYPOTHESIS: the game needs the display buffer's memory for its text. Options "park" / "late" of
  `tools\own\views.py` keep the code.

## Hidden test desktop (2026-11-10, user request)

- The user was playing another game and every test emulator window took the keyboard focus for a moment.
- `tools\quiet_launch.py` starts a process on a separate Windows desktop object ("kh2-test-desktop"): its windows
  are not on the user's screen, not in the task bar and cannot become the active window. Used by
  `tools\kh2_session.py`, `tools\lane-v3\v3_session.py` (unless `--show`) and `tools\package\rehearse.py`;
  `KH2_TEST_DESKTOP=0` switches it off. The lanes' own copies of the session tool in `tools\lane-*` are NOT
  changed (they are not used any more).
- VERIFIED (o27-quiet against o26-keep-1x): same run on the hidden desktop: exit 0, in sync, both pictures
  byte-identical; Direct3D 12 works there. The suite, the own-screen tests and the launcher rehearsal ran that way.

## Test package build 3 = own screens (2026-11-10 late evening)

- `python -I tools\package\make_package_patch.py` then `make_test_package.py --rebuild`: package id
  35228b5c127c; emulator exe = view12; `emulator\patches` holds the own-screen patch (merged-v6-own lines + the
  official widescreen group, SHA-1 afe5a6c59193b752160ae91c2e994b730dacf209), the .view file and the Digimon
  patch; folder `SHARED-SCREEN-FALLBACK` holds merged build 5 the same way, with a read-me; Picture quality
  starts at 4x; disc maker and disc unchanged since build 2 (kh2-coop-v2.kh2patch, disc name "... TEST v2").
  Friend kit `dist\KH2-TEST-FRIEND-KIT.zip` SHA-1 03d6d55bfb1586e96669d83e4d60f6659e0d2a41 (22.5 MB, 16 entries,
  no disc image, BIOS or memory card). The launcher is byte-identical to lane T's (SHA-1 4ac5b5b7...).
  (The rehearsal below ran on the build before the last read-me line was added, id 447275fa7e70; program files,
  patch files and emulator are the same.)
- VERIFIED (p3-rehearsal-own, hidden desktop): two copies of the package with the tested disc, joined through
  their launchers with a join code, 9,000 frames, 140 digests, never out of sync; the host's log says "this PC
  shows the final picture", the friend's "this PC shows the copy taken at the marker"; pictures: the host sees
  his Roxas, the friend sees his (`local\tests\p3-rehearsal-own\cmp\sheet.png`); memory cards identical after.
- The real package was only read (still id 9e49d3f8243e).

"""
notes = notes.replace("SUITE_RESULT", suite_line)
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
p.write_text(t, encoding="utf-8")
print("state updated")
