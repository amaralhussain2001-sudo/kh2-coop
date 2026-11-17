"""One-off: docs/STATE.md after the fourth round (test build 9): the section PICK UP HERE is rewritten and the
round's validation part is added in front of "## Open items"."""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
a = t.index("## PICK UP HERE")
b = t.index("\n---\n", a)
if "after test build 9" in t[a:b]:
    raise SystemExit("already there")

PICK = """## PICK UP HERE (rewritten 2026-11-11 late, after test build 9)

Read this section first, then `..\\KH2-COOP-PLAN.md` (plan, rules, all user decisions; rows 10-27 are the newest)
and `REQUIREMENT-full-parity.md`. The rest of this file is the detailed record. Lane reports are in
`docs\\lanes\\`. The parity checklist is `docs\\PARITY-CHECKLIST.md`.

Where things stand:
- TWO builds, both on the disc `local\\iso\\kh2-coop-v4.iso` (SHA-1 97e37dd96ac1985946e80da502ba24d49a5ca3c7,
  UNCHANGED since build 8; builder `tools\\merge\\build_disc_v4.py`):
  * SHARED SCREEN = `patches\\merged-v6` (2,400 words, SHA-1 7f5971e375723435f10bc68d82424e775253788a; the same file
    as the validated test folder `patches\\test-v6-l`) = build 8's patch + FOUR GLUES of the fourth round:
    15 a hero's own motion offers its command to that hero (the boss move's follow-up command), 16 the script
    engine's two button tests on either controller (not seen in a game), 17 the helpers heal the other hero too,
    18 a Limit started by the second hero runs for him. Builder `tools\\merge\\merge_v6.py` (its header explains
    every glue). With `--no-reactown --no-mash --no-heal --no-limit2` it writes build 8's file word for word
    (SHA-1 567ffd92...). Experiments in the builder that are NOT in the build: `--react`, `--helper`,
    `--helper2`, `--evrc`.
  * OWN SCREENS = `patches\\merged-v6-own` (4,295 words, SHA-1 7ecdc1f05370bb691deddd4255ff4cb86e846b46; the same
    words as the validated test folder `patches\\test-own-v12`) = the above + two views + HUD per player + menu
    rows per player + boss moves keep two views + STEP 9: the command menu's FRAME AND PICTURE SHEET PER PLAYER
    (builder `tools\\own\\make_own.py`; `--no-looks` leaves step 9 out). Needs the emulator build
    `emulator-src\\builds\\view12` and `patches\\own-view\\SLPM-66675_F266B00B.view` (both unchanged).
- The test package in `dist\\` is BUILD 9 (package id 467514111169): own screens, the shared-screen patch inside
  as a fallback file, the disc patch `kh2-coop-v4.kh2patch` as in build 8 (both players make the "TEST v4"
  disc file once; check number 97e37dd9...). Friend kit SHA-1 922507f7d92edbd7e2046076516c6e6b4a68e493, KH2 patch
  file SHA-1 c7eb0b3b57ce8d350ffaf22c1e35317d37dcfe62. Rehearsed through the launchers (p11-rehearsal-b9: join
  code after 9 s, 9,000 frames, never out of sync, game file check = the v4 number on both, same memory card
  file; the host's pictures are byte for byte those of build 8's rehearsal). Copies deleted. The original disc
  file was only read (SHA-1 still 81c177a3...). No humans have played yet.
- TESTS MUST NOT DISTURB THE USER: every test emulator starts on a hidden Windows desktop
  (`tools\\quiet_launch.py`). Never use `--show` unless the user asks.
- FOUR sandboxes now: `local\\run-m` (the suites; port 29050, pine 28081), `local\\run-v3` (30150 / 28061),
  `local\\run-v3b` (30350 / 28062), `local\\run-v3c` (30550 / 28063; made in this round with
  `v3_session.py make 2 --run-dir run-v3c`). One run per sandbox at a time.
  `bash tools/own/dusk_one.sh <name> <patchDir> <iso> <frames> <snaps> <p1> <p2> <sandbox> <port> <pine>`.
- A stopped suite keeps running unless its shells and emulators are killed too:
  `powershell -File tools\\own\\stop_tests.ps1` (it now knows near_batch.sh and final_b8 / b9.sh as well).
- NEVER overwrite a patch folder OR A BATCH SCRIPT that a running batch reads (both happened once). Build into
  `patches\\test-*` first; edit a batch script only when nothing runs it.
- No lane (agent) is running. The user said: do NOT open extra lanes.

User answers and remarks:
- 2026-11-10 night: "why you stop continue until u finish for your question use the Recommended", then "continue
  until finish all the tasks". 2026-11-11: "why you stop not finish all the tasks?", "finish all the tasks then
  i'm going to test it one time after u finish everything", "continue until u finish the not done tasks". So:
  no stopping for A/B questions; the user tests ONCE at the end.
- 2026-11-11 late (the hand-over prompt of the fourth round): a job list in order (boss follow-up command, own
  menu frame, the end of Mail Delivery, forms / Game Over / shop / journal / healing, then the older items);
  after any patch change the suites, the package, the rehearsal, the notes; one report at the end.
- 2026-11-11 late, during the round: "run more then one tasks". Taken as: the main session runs several jobs
  at once (tests in the sandboxes in the background while other work goes on). No agents were opened.
- "is the money shared, but their skills different?": answered (one wallet, one item stock; level, skills,
  equipment the same for both); own skills / equipment stay a Phase 4 job unless the user asks (plan row 11).
- Taken as the recommended option without asking (plan rows 15-27): one Drive Form at a time; the twin's hits
  count for mission scripts; rules screens on either controller; skateboards; the nearer hero for things in a
  room; helpers split at 900 units and join at 550; a second board beside EVERY board; a boss move shows on the
  screen of the player whose hero is in it; and in the fourth round: the helpers heal both heroes; button-mash
  tests on either controller; a Limit belongs to the player who started it.

Next jobs, in order (section "Fourth round" has what was done and learned):
1. The two-human test (the user's, once, at the end) with build 9; read the logs they send back.
2. Left open by the fourth round:
   a. When one player's menu changes its look (he hops on or off a board) the other player's rows can blink for
      the length of the frame's opening animation: the "revealed" state and the group hide (0x0013D3F8, group 2)
      are still one for both players.
   b. The helpers' ITEM use for the other hero (healing item, MP item) is the same code pattern as Cure but was
      not seen in a test. The button-mash rule (sixteenth glue) was not seen in a game.
   c. Limits: Whirli-Goof, Comet and Trinity were played by player 2. Not tried: the guests' Limits, a Limit
      while the heroes are split, a Limit by player 2 while player 1 is in a form.
   d. Six fault lines at a Game Over + Continue on the roam test disc (pc 0x00170930 / 0x00170934, a record
      that is not found); the same on build 8. Not examined. The two bodies stand in a T-pose during the white
      fade of a Game Over.
3. Not seen in a game yet: the dark form (Anti Form); Summons; the six other "hits counted" missions; a second
   board in the other worlds' free roam (seen in tt07 only); the Moogle's workshop, the world map and the
   result screens of small games with player 2's controller.
4. Own screens, still open: a small orange glint beside player 2's gauge in the first town; the 2-3 step
   return of two views after a death or mission event; sound listener (HYPOTHESIS: player 1's camera); text
   boxes and the "Waiting" sign on both screens (kept on purpose).
5. Seen, not examined: the dim "Examine" banner on player 2's screen in Merlin's house (also without the kit:
   f1-journal; HYPOTHESIS: he stands beside the thing and does not face it, as with the dim "Shop").
6. Feasibility tests continue down `docs\\PARITY-CHECKLIST.md` in story order; boss moves written against "the
   player".
7. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission.
8. The PARK experiment (`tools\\own\\fork_views.py`); the null-read riddle (pc 0x0016E3C0 with the magic kit; the
   long roam run of `batch_v7.sh` shows 32 fault lines on build 9, 36 / 32 on builds 7 / 8).

How to repeat: patches `python -I tools\\merge\\merge_v4.py`, `merge_v5.py`, `merge_v6.py`, then
`python -I tools\\own\\make_own.py` (own screens; base = merged-v6); disc `python -I tools\\merge\\build_disc_v4.py
kh2-coop-v4.iso`; suites `bash tools/merge/suite_v6.sh <ownPatchDir>` and `bash tools/merge/suite_v5_short.sh
<sharedPatchDir>` (both on run-m, one after the other), `bash tools/own/batch_v7.sh <ownName>` (run-v3; needs
<ownName>-kit and -die2), `bash tools/own/near_batch.sh <ownName> <prefix>` (run-v3b), `bash tools/own/final_b9.sh
<ownName> <sandbox> <port> <pine> a|b` (needs the kits -forms, -formdie, -rec, -fheal, -limit, -mail: the
commands are in section "Fourth round", part 9); package `python -I tools\\package\\make_package_patch.py`,
`python -I tools\\package\\make_test_package.py --rebuild`, rehearsal copies `python -I
tools\\package\\make_rehearsal_copies.py`, rehearsal `python -I tools\\package\\rehearse.py <name> --game "Kingdom
Hearts II - Final Mix (2 Players TEST v4).iso" --layout 1 --screen 4:3 --frames 9000 --script-a
tests/scripts/merge/newgame_p1.txt --script-b tests/scripts/merge/newgame_p2.txt --snap "5180,6400,6912,8900"
--snapview` (then delete `local\\kit-test-t`); emulator `powershell -File emulator-src\\build.ps1`.

How a fault was found fastest in this round (use again): a small test-only RECORDER in the patch at the entry
of the routine everything must pass through (`tools\\own\\make_rec_offer.py`: ring of callers + the stack of the
first hit), read with a probe at the snapshot frames. It found in one run what four guessed places had missed.

Working habits that matter here: plain English, short sentences, lettered options with a recommendation (and
take the recommended one without waiting); every claim VERIFIED or HYPOTHESIS; never touch the original disc
file, `Desktop\\PS2-ONLINE`, `Desktop\\openkh` or `Desktop\\New folder\\digimon-online`; use absolute paths in
shell commands and never put paths with spaces into a word list; write script files instead of inline heredoc
Python when the text has quotes or backslashes; tests run on the hidden desktop; never overwrite a patch folder
or a batch script that a running suite is using. The emulator source carries the PCSX2 project's own rules for
AI help (`emulator-src\\pcsx2\\AGENTS.md`): nothing from this private copy may be posted to the PCSX2 project or
its GitHub by an agent.
"""

VALID = """### 9. Validation of the final patches and test build 9
- Final test folders: `patches\\test-v6-l` (shared) and `patches\\test-own-v12` (+ kits, made like this:
  `make_kit2.py test-own-v12 test-own-v12-kit --magic`, `-die2 --die=both`, `-forms --magic --forms=56 --limit
  --drive=5 --formkeys`, `-formdie` = the forms kit + `--die=both`; `make_rec_offer.py test-own-v12
  test-own-v12-rec 299`; `make_mailpins.py test-own-v12 test-own-v12-mail`; `make_healkit.py test-own-v12
  test-own-v12-fheal p2 4900 3 --p1slot=01C6C750 --p2slot=01C6C018`; `-limit` = three ability lines, part 7).
  Earlier candidates of the round: v9 (glue 15), v10 (+ step 9), v11 (+ glues 16, 17); a full regression of v10
  was clean too.
- `suite_v6.sh` on the own-screen patch: 9 of 9 in sync (87 / 162 / 115 / 84 / 249 / 92 / 531 / 114 / 187
  digests), every screenshot pair identical, one-hero pictures the same as in the validation of build 8
  (`local\\m6-suite-b9.log`). `suite_v5_short.sh` on the shared patch: 3 of 3, one hero alone 4 of 4 pictures
  the same as merged build 5 (`local\\m5s-suite-b9.log`). `batch_v7.sh`: 6 of 6 (`local\\own-batch7-b9.log`; the
  long roam run has 32 of the known fault lines). `near_batch.sh` (`local\\s9-batch.log`): 7 of 7, line for line
  the results of build 8 (bag by either player, Twilight Thorn, Grandstander, Dusk counter scene, Mail
  Delivery, morale mission).
- `tools\\own\\final_b9.sh` = build 8's final checks + this round's (logs `local\\final-b9-a.log`, `-b.log`):
  part a 12 of 12 (helper split, Valor, Master, the boss fight with 18 of 18 hold snapshots in two views, the
  morale split, the follow-up command with nobody pressing and with player 2 pressing, Wisdom, Final, the Game
  Over in a form, Donald's Cure for the twin, the Limit by player 2); part b 10 of 10 (the five challenges and
  Mail Delivery on boards, the late hop-on, one rider / one walker and getting off, the END of Mail Delivery,
  New Game on the full v4 disc). All in sync; fault lines only the six known ones of the Game Over run.
- The final folders were written by the builders after the regression: `patches\\merged-v6` has the SHA-1 of
  `test-v6-l`; `patches\\merged-v6-own` has the same patch words as `test-own-v12` (the files differ in the
  comment line that names the base folder).
- Package: `tools\\package\\edit_package_v9.py` (read-me BUILD 9; the disc file and its patch are build 8's),
  `make_package_patch.py`, `make_test_package.py --rebuild` -> id 467514111169. Rehearsed through the launchers
  (p11-rehearsal-b9: join code after 9 s, 9,000 frames, 140 digests, never out of sync, game file check = the
  v4 number on both, both memory card files the same). Copies deleted.

### 10. Tools and test discs added in this round
- `tools\\own\\`: `make_rec_offer.py` + `offer_probe.py` (recorder of command offers), `sheet_probe.py` (the
  menu's sheet, frame and look words; also counts non-zero words in four cave areas), `posfind_probe.py`
  (where memory holds a hero's position), `make_mailpins.py` + `mail_probe.py` (the end of Mail Delivery),
  `make_healkit.py` + `heal_probe.py` (whom the helpers heal; HP / MP / action of heroes and helpers),
  `make_mash.py` (button scripts), `strrefs.py` (a text in the program and the code that uses it),
  `final_b9.sh`; `tools\\package\\edit_package_v9.py`; `tools\\merge\\add_session7_notes.py`;
  room mod `tools\\lane-s1\\mods\\hb10-shops`.
- Button scripts `tests\\scripts\\own\\`: wisdom_p2, final_p2, formdie2_p2, journal_p2, shop_*_p2, limit_p1,
  limit_p2, limit2_p2, limit3_p2, skateoff_p1 / _p2, mailend_p1 / _p2, mailend2_p1 / _p2.
- Test discs added to `local\\iso\\` (4.3 GB each; delete when not needed): test-s1-hb10s (Marketplace with
  helpers and shops), test-g-friends (the old fight with Donald, Goofy and a twin, rebuilt from
  `local\\variants\\g-friends`).
- Memory used by this round: routines 0x000F3B00-0x000F3EE7 and data 0x000F3900-0x000F3A9F (own screens, step
  9); 0x000F5B80-0x000F5BAB (glue 15); 0x000F7C00-0x000F7D1B (glue 17), 0x000F7E00-0x000F7E4F (glue 18);
  test-only recorder 0x000F1C00-0x000F1FFF. All were zero in a run before (probe e2-sheet).

"""
t = t[:a] + PICK + t[b:]
k = t.index("## Open items")
t = t[:k] + VALID + t[k:]
t = t.replace("WORKING NOTES, written while the round runs (the summary at the top is rewritten when the round ends).\n", "")
p.write_text(t, encoding="utf-8")
print("STATE.md: PICK UP HERE rewritten, validation part added")
