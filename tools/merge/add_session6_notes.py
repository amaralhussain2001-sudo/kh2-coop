"""One-off: docs/STATE.md after test build 8 (third round: a second skateboard everywhere and the five skate
challenges = disc v4; one helper with each hero; a boss's scripted move keeps two views).

  python -I tools/merge/add_session6_notes.py <packageId> <friendKitSha1> <patchFileSha1> <rehearsalText>
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "after test build 8" in t:
    raise SystemExit("already there")
pkg, kit, pfile, rehearsal = sys.argv[1:5]


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)


a = t.index("## PICK UP HERE (rewritten 2026-11-11 late evening, after test build 7)")
b = t.index("How to repeat: patches `python -I tools\\merge\\merge_v4.py`")
PICK = r"""## PICK UP HERE (rewritten 2026-11-11, after test build 8)

Read this section first, then `..\KH2-COOP-PLAN.md` (plan, rules, all user decisions; rows 10-22 are the newest)
and `REQUIREMENT-full-parity.md`. The rest of this file is the detailed record. Lane reports are in
`docs\lanes\`. The parity checklist is `docs\PARITY-CHECKLIST.md`.

Where things stand:
- TWO builds, both on the NEW disc `local\iso\kh2-coop-v4.iso` (SHA-1 97e37dd96ac1985946e80da502ba24d49a5ca3c7
  = disc v3 + a second skateboard beside every skateboard of the game + the five skate challenges for two;
  builder `tools\merge\build_disc_v4.py`; v2 and v3 are still in `local\iso`):
  * SHARED SCREEN = `patches\merged-v6` (SHA-1 567ffd921a2056a223ab8fb146c4d304e3587595) = the patch of test build
    7 + the THIRTEENTH GLUE (one helper goes with each hero when the heroes split up). Builder
    `tools\merge\merge_v6.py` (its header explains every glue); with `--no-helpers` it writes the build 7 file
    again, word for word (SHA-1 ab2362a4...). Experiments in the builder that are NOT in the build: `--react`,
    `--helper`, `--helper2`, `--evrc`.
  * OWN SCREENS = `patches\merged-v6-own` (3,930 words, SHA-1 014f6dd05ab9d0ee39281f8dc5035a71bd8...; see the
    file) = the above + lane V1's two views + lane V2's HUD per player + the command menu's rows per player +
    STEP 8: a boss's scripted move keeps two views (builder `tools\own\make_own.py`; the camera task's part is
    in `tools\own\fork_views.py`, which writes `tools\own\views.py`). Needs the emulator build
    `emulator-src\builds\view12` and `patches\own-view\SLPM-66675_F266B00B.view` (unchanged).
- The test package in `dist\` is BUILD 8 (package id PKGID): own screens, the shared-screen patch inside as a
  fallback file, and a NEW disc patch `kh2-coop-v4.kh2patch` (both players must make the "TEST v4" disc file;
  check number 97e37dd9...). Friend kit SHA-1 KITSHA, KH2 patch file SHA-1 PFILE. REHEARSAL The disc patch was
  applied to the original image in a temporary file and gave the v4 check number
  (`tools\package\check_disc_patch.py`; the original is only read, its SHA-1 is still 81c177a3...). No humans
  have played yet.
- TESTS MUST NOT DISTURB THE USER: every test emulator starts on a hidden Windows desktop
  (`tools\quiet_launch.py`). Never use `--show` unless the user asks.
- A stopped suite keeps running unless its bash and emulator processes are killed too:
  `powershell -File tools\own\stop_tests.ps1`. One suite on `local\run-m` at a time; `local\run-v3` and
  `local\run-v3b` are two more sandboxes, so three things can run at once
  (`tools\own\dusk_one.sh <name> <patchDir> <iso> <frames> <snaps> <p1> <p2> run-m 29050 28081` uses run-m).
- NEVER overwrite a patch folder that a running batch reads (it happened on 2026-11-11 with `test-own-v8`; the
  batch had to be stopped and started again).
- No lane (agent) is running. The user said: do NOT open extra lanes.

User answers and remarks:
- 2026-11-10 night: "why you stop continue until u finish for your question use the Recommended", then "continue
  until finish all the tasks". 2026-11-11: "why you stop not finish all the tasks?", "finish all the tasks then
  i'm going to test it one time after u finish everything", then "continue until u finish the not done tasks"
  and "after u finish all the tasks then i'm going to test it (after all the tasks)". So: no stopping for A/B
  questions, no report that reads like an end while the list below has jobs that can be done; the user tests
  ONCE at the end.
- "is the money shared, but their skills different?": answered (one wallet, one item stock; level, skills,
  equipment the same for both); own skills / equipment stay a Phase 4 job unless the user asks (plan row 11).
- Taken as the recommended option without asking (plan rows 15-22): one Drive Form at a time; the twin's hits
  count for mission scripts; rules screens on either controller; skateboards; the nearer hero for things in a
  room; helpers split at 900 units and join at 550; a second board beside EVERY board; a boss move shows on the
  screen of the player whose hero is in it.

Next jobs, in order (section "Third round" has what was done and learned on 2026-11-11):
1. The two-human test (the user's, once, at the end) with the newest build; read the logs they send back.
2. Found in the third round and NOT solved:
   a. The follow-up command of a boss's scripted move ("Break Raid" in Twilight Thorn's throw) is put into
      player 1's menu and only player 1's Triangle starts it, also when the twin is the hero in the move (tests
      b5-thorn-nopress, b6-thorn-p1press, g7 / g9 / h1 / h2). Four places were tried and are NOT where it
      comes from: an object's thinking, the twin's own thinking, the callbacks of object scripts (0x0016CCE8),
      the event player's callback 0x00197D40 kind 1. Next idea: watch player 1's control object (0x01C5F530)
      for the word that changes when the row appears, then find the writer.
   b. Free roam, one player on a board and the other on foot: the walking player's command menu is drawn with
      the board menu's frame (broken look) until he hops on too or the rider gets off (tests j6, j8; the same
      in build 7). The frame is one thing for both players; own frame per player = own-screen work.
   c. Mail Delivery: the end of the job was not reached (random buttons got 4 of 5 letters in 60,000 frames;
      holding the counter at 4 or 5 by a test line does not end it).
3. Not seen in a game yet: Wisdom / Final Form and the dark form; a Game Over while the twin is in a form;
   Limits with a helper started by player 2; whom the helpers heal; the shop and the journal with two views;
   the six other "hits counted" missions; a second board in the other worlds' free roam (data checked by the
   tool's ground check only; seen in tt07).
4. Own screens, still open: a small orange glint beside player 2's gauge in the first town; the 2-3 step
   return of two views after a death or mission event; sound listener (HYPOTHESIS: player 1's camera); text
   boxes and the "Waiting" sign on both screens (kept on purpose).
5. Seen once, not examined: a Limit Form body in a T-pose for a moment (test k8-formdie frame 9400); the dim
   "Examine" banner on player 2's screen in Merlin's house.
6. Feasibility tests continue down `docs\PARITY-CHECKLIST.md` in story order; boss moves written against "the
   player"; button-mash moves of 7 object scripts read controller 1 only.
7. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission.
8. The PARK experiment (`tools\own\fork_views.py`); the null-read riddle (pc 0x0016E3C0 with the magic kit; the
   long roam run of `batch_v7.sh` shows its 36 fault lines on build 7 and build 8 alike).

""".replace("PKGID", pkg).replace("KITSHA", kit).replace("PFILE", pfile).replace("REHEARSAL", rehearsal)
t = t[:a] + PICK + t[b:]
rep("`python -I tools\\own\\make_own.py` (own screens; base = merged-v6); disc `python -I tools\\merge\\build_disc_v3.py\nkh2-coop-v3.iso`;",
    "`python -I tools\\own\\make_own.py` (own screens; base = merged-v6); disc `python -I tools\\merge\\build_disc_v4.py\nkh2-coop-v4.iso` (needs `local\\build\\boards\\Boards.dll`: `local\\dotnet\\dotnet.exe build tools\\boards\\Boards\\Boards.csproj -c Release -o local\\build\\boards`);")

NOTES = r"""## Third round (main session, evening and night of 2026-11-11; the user: "continue until u finish the not done tasks")

What was "not done" after build 7: Donald and Goofy stay with player 1; the skate challenges of the other
worlds have one board; untested things (forms other than Limit, letters by player 2, result screens, a board in
free roam); Twilight Thorn's moves show on both screens. Everything below was made and checked by scripts on
this PC; no humans have played.

### 1. Disc v4: a second skateboard beside EVERY skateboard, and the five skate challenges for two
- Found in the room files (`Kh2Tool ard-dump`, dumps in `local\analysis\ard-all`): the challenges (missions
  AL00 / CA02 / HB09 / NM09 / TT07 _SKATE_01) do not bring their own board. Their program spawns the player's
  placement (group s_99; lane F's twin is there already) and the room's own board comes from a map group (m_95;
  tt07: m_98). The script mounts "the first object with status 5067", like Mail Delivery. Every free-roam
  board is in a map group too (m_94 ... m_98), one per entrance: one board for two players.
- NEW TOOL `tools\boards\Boards` (C#, a copy of lane F's tool with one command, `clone-all`; build into
  `local\build\boards`): a CLONE of the object itself beside every placed object of the given kinds (same
  record, new position, new serial), with lane F's ground / wall check. Kinds: the seven skateboards (0x05AB
  Roxas, 0x081A Sora, 0x08C0-0x08C4 the worlds' own). Groups: every map group "m_*" and tt06 b_40 / b_43 (Mail
  Delivery). Result on the stock data: 147 second boards in 29 rooms (tt, hb, al, ca, nm, bb, dc, he, wi), 146
  with a checked spot (report `boards-report.csv` in the disc's work folder). Not cloned on purpose: the test
  missions' groups (s99_, s98_, skat: TEST_SKATEBOARD) and po01 b_89, mu11 s99_.
- `tools\boards\make_skate.py`: the eight mission scripts that mount the player (Mail Delivery x3 and the five
  challenges) get the same edit as build 6's Mail Delivery (the player's board by its serial; the second board
  and the twin by theirs; the edit code is `make_mail.py`'s). Serials come from the two reports.
- `tools\merge\build_disc_v4.py` = v3's builder with these two steps instead of `make_mail.py`'s (options
  `--no-boards`, and for test discs `--jump "WORLD LOCALSET"`, `--jump1 "WORLD AREA ENTRANCE"`, `--mod DIR`).
  `local\iso\kh2-coop-v4.iso`, SHA-1 97e37dd96ac1985946e80da502ba24d49a5ca3c7.
- VERIFIED on test discs `local\iso\test-v4-<name>.iso` (jump into the mission), own screens:
  * al109 "SB Sand Slider", ca88 "SB Time Attack": both on their own board, own board menus; a checkpoint
    player 2 rides through counts (u1-al-skate, u2-ca88).
  * tt187 "SB Street Rave", hb99 (hit combo), nm75 "SB Workshop Rave": both on boards (u2-...); with ONLY
    player 2 pressing (random buttons) the score rises: Street Rave 71 then 203 with "CLEAR!", combo record 151
    in Hollow Bastion, 695 points in Halloween Town (x2-...-p2; with only player 1: x2-...-p1). The "Quit /
    Retry" menu at the end was answered by player 2's controller (x2-tt187-p2).
  * After "Quit" on a test disc the game jumps to a room where no hero is built (player 0, twin 0, both runs
    the same): the test disc's story state, not the two-player part.
- Mail Delivery on the v4 data (`test-v4-tt91.iso`): both ride; a letter handed in by player 2 counts ("1/5" on
  both screens, y1-mail-p2); 60,000 frames of random buttons on both pads stayed in sync, 4 of 5 letters
  (y2-mail-long). The END of the job was not reached; a counter held at 4 or 5 by a test line does not end it.
- Free roam: two heroes hop on two boards, also two seconds apart (j4-skate-s2-v8, j8-skate-late; lane S1's old
  disc `test-s1-skate-s2`, rebuilt from its recipe). On the v4 data in Tram Common (mod
  `tools\lane-s1\mods\tt07-sora-boards`, `test-v4-tt07roam.iso`): both boards stand side by side; player 1
  hopped on ("Hop On", then the board menu), player 2's script did not reach the second board (j6). OPEN, seen
  there: while only one hero rides, the walking player's command menu is drawn with the board menu's frame.

### 2. Donald and Goofy: one helper goes with each hero when the heroes split up (thirteenth glue)
- HOW IT WAS FOUND. A quiet room with helpers was needed: `tools\lane-s1\mods\hb09-friends` (the Borough's free
  roam program 0 + "Party DEFAULT") + `build_disc.py hb9f --jump1 "HB 9 0" --party DEFAULT`
  -> `local\iso\test-s1-hb9f.iso` (Donald HP 18, Goofy HP 28, no enemies; test v1-hb9f).
  * The helpers' scripts (obj\P_EX020, P_EX030, decoded with `tools\own\extract_obj_ai.py` and Bdxio `-r -b`)
    only hold fight actions; following is in the program.
  * `tools\own\leader_probe.py` (where does memory hold the pointer to player 1's hero): nine places; holding
    each on the twin by a test line (`tools\own\make_pin.py`, conditional lines) moved no helper.
  * `tools\own\trail_probe.py` (where does memory keep spots the hero walked through): a ring of 32 spots at
    0x003A9040 = the leader's TRAIL. Its code is the "follow" system, 0x0010A000-0x0011C400. Three tasks run
    it every step (installed at 0x001123F0): 0x00111F50 (rebuilds the member table 0x00341708 = leader,
    helper, helper at 0x00111E50; THE LEADER IS THE ENGINE'S PLAYER, read at 0x00111E98; adds the leader's
    spot to the trail; sets the places beside the leader at 0x001118A8; runs each helper's follow object),
    0x001122A0 and 0x00112388.
  * Proof: with only the read at 0x00111E98 turned to the twin, both helpers walked to the twin
    (w-test-lead0). The bit search of 2026-11-11 (make_playerbits.py) never tried that read: it had index 0,
    and index 0 is in no variant. (A flaw of the search tool; keep in mind when a bit search finds nothing.)
- THE GLUE (`merge_v6.py`, HELP_SRC at 0x000F5280, data at 0x000F5800; option `--no-helpers`):
  * the three task routines are replaced by wrappers (the words that hand their addresses to the task list).
    Each wrapper runs the game's routine for player 1's hero and his helpers, then, when a helper goes with
    the twin, a second time with the twin as the leader and the follow system's leader memory swapped for a
    second copy (0x00341720-0x0034177F, 0x003417B0-0x003417DF, the trail 0x003A9040-0x003A924F);
  * the member table holds the true members again when a wrapper ends; the game's own rebuild (hooked at
    0x00111F74) sees only true changes, so the lists that follow the party (0x00135818) are told nothing new;
  * a helper decides where to walk in his own methods, outside those tasks (his follow object's states read
    "my place beside the leader" at 0x0010E464 by his index). So the same swap is done around a twin-led
    helper's thinking (the twelfth glue's hook, nr_help) and around four methods of the helper class (class
    table 0x00345C08, words +0x08, +0x0C, +0x14, +0x20). The pass word 0x000F5800 says "the twin's memory is
    in", so nothing swaps twice. (First version without this: the second copy was right, the helper stood
    still: tests h1 ... h4.)
  * who goes with whom (hp_assign, once a step): heroes less than 900 units apart: everybody with player 1's
    hero, as before. Farther apart: the pairing with the smaller sum of squared distances, one helper each,
    kept until the heroes are less than 550 apart again.
- VERIFIED: h5-split / k8-split (quiet room: the twin runs 1,100 away, Donald goes with him and stands 150
  from him, Goofy stays 158 from player 1; back together, both are with player 1 again; pictures: each screen
  shows its hero with his helper); h6-mu-split / k8-musplit (first morale mission: Goofy fights beside the
  twin 2,300 units from player 1, the guest stays with player 1; in sync, no fault lines); r8-morale (the
  mission is WON by frame 7000 where build 7 was still fighting at 8900).
- With `--no-helpers` the builder writes build 7's patch word for word; one hero alone: the suite's pictures
  are the same as before (part 6).
- NOT examined: whom the helpers heal; Limits; three heroes' worth of rules for a guest.

### 3. A boss's scripted move keeps two views (own screens, step 8)
- Before: while an event holds the camera (0x0033CC38) both screens showed one view. Twilight Thorn's moves
  are such events, 0.5 to 5 seconds each (20 seconds of game time for the longest), and the other hero can
  walk during them (z2-thorn-walk against z3-thorn-idle) without seeing himself.
- Found (`tools\own\event_probe.py`, tests z4-thorn-ev, e2-dusk-ev): the event object is at 0x0035037C. A
  scripted move's event was started by an OBJECT (event +8 = the boss, 0x0180xxxx-0x01BFxxxx); a story scene's
  by the mission (0x01D48DF4) or nobody. The hero who is in the move carries bit 0x4000 at object +0x160 (in
  every sample exactly one hero; the bit is also set while a hero does a Reaction Command without a hold).
  Event +0x44 is NOT a safe sign (story scenes have a value there too).
- NEW RULE (`tools\own\make_own.py` step 8, routines at 0x000F5C00, variable 0x000F5E80; the three calls in the
  camera task come from `tools\own\fork_views.py`; option `--no-bossviews` on both): hold + object-started
  event + exactly one hero with the bit -> two views stay. Player 1's hero in the move: his screen shows the
  move (the game's own), camera 2 goes on for the twin (its update runs with the hold lifted). The twin in the
  move: the move's picture (view 0's data, four blocks at 0x003A7B70 / 7D70 / 7F70 / 8090) is copied to view 1
  = player 2's screen and camera 1 goes on for player 1's hero. Anything else: one view, as before.
- VERIFIED: b3-thorn (33 of 33 hold snapshots in two views; pictures: player 1's moves on player 1's screen
  with player 2's own camera beside them, the twin's throw on player 2's screen with player 1's own camera);
  k8-thorn on the final patch; story scenes still one view (Dusk scene, mission start and end: r8-dusk, c8).
- OPEN (next jobs 2a): the move's follow-up command sits in player 1's menu whoever is in the move.

### 4. Drive Forms that use up a helper
- Valor Form for player 2 (uses Goofy): VERIFIED (f1-valor-p2, k8-valor: red outfit, Goofy leaves on both
  screens, FORM gauge and "Revert" on player 2's screen only; after Revert Goofy is back).
- Master Form for player 2 (uses both): VERIFIED (f5-master-p2k, k8-master). A freeze in the first tries (both
  players, also on build 7) came from the test kit: a fresh save has no Keyblade in that form's weapon place
  (save + 0x339C); `make_kit2.py --formkeys` writes one (0x32F4 Valor, 0x339C Master, 0x33D4 Final).
- Not tried: Wisdom, Final, the dark form.

### 5. Tried and taken out again (the record of what does NOT work)
- For the follow-up command (next jobs 2a) the twelfth glue got three additions and a fourteenth glue was
  made; none moved the command, so all four are out of the build (`edit_merge_v6_nearest4/5/6.py`,
  `edit_merge_v6_evrc.py`; the last one is still in the builder as the experiment `--evrc`).
- MY OWN FAULT on the way: `edit_merge_v6_nearest5.py` put a block into the fall-through path of the nearest
  hero routine, so the whole twelfth glue was dead in the candidate. Found by the regression batch (player 2
  could not ride the bag any more: r8-bag-p2, first run). Lesson: a new block goes after a routine's last
  jump, never before a label that is reached by falling through.
- A second slip: a small edit sent through the shell turned "\n" in a Python string into real line ends and
  broke `merge_v6.py` for a few minutes (repaired with the Edit tool). Script files with backslashes are
  written with the Write tool.

### 6. Validation of the final patches and test build 8
- Final test folders: `patches\test-v6-h` (shared) and `patches\test-own-v8` (+ `-kit`, `-die2`, `-forms`).
- `suite_v6.sh` on the own-screen patch: 9 of 9 in sync, every screenshot pair identical, one-hero pictures the
  same as merged build 5 (`local\m6-suite-b8.log`). `batch_v7.sh`: 6 of 6 (`local\own-batch7-b8.log`; the long
  roam run has the same 36 fault lines as on build 7). Special scenes `near_batch.sh` (`local\r8-batch-b8.log`):
  bag by player 1 and by player 2, Twilight Thorn (two views at every snapshot), Grandstander, Dusk counter
  scene, Mail Delivery, morale mission (won).
- The new things on the final patch: `tools\own\final_b8.sh` (logs `local\final-b8-a.log`, `-b.log`); the
  shared-screen patch: `suite_v5_short.sh` (`local\m5s-suite-b8.log`). FINALRESULTS
- Disc patch: `python -I tools\lane-t\make_disc_patch.py <original> local\iso\kh2-coop-v4.iso
  local\package\kh2-coop-v4.kh2patch` (SHA-1 009a04c2aa0992dc4e0d7bf609e453a89a1a4f6f, 119 runs, 14,139
  sectors); `check_disc_patch.py` gave the v4 number; the original's SHA-1 is unchanged.
- Package: `tools\package\edit_package_v8.py` (v4 names, read-me BUILD 8), `make_package_patch.py`,
  `make_test_package.py --rebuild` -> id PKGID. REHEARSAL

### 7. Tools and test discs added in this round
- `tools\boards\` (Boards clone tool, `make_skate.py`, `skate_tests.sh`, `score_tests.sh`),
  `tools\merge\build_disc_v4.py`, `tools\own\`: `leader_probe.py`, `trail_probe.py`, `watch_probe.py`,
  `hold_probe.py`, `event_probe.py`, `bm_probe.py`, `flag_probe.py`, `make_pin.py` (conditional test lines),
  `find_quiet.py`, `extract_obj_ai.py`, `disasm.py` (disassemble / data words / callers of a routine),
  `callers.py`, `modglobals.py` (the global data a range of the program uses), `leader_bits.sh`, `final_b8.sh`,
  `edit_boss_views.py`; `dusk_one.sh` takes `OWN_THEN=random`.
- Test discs kept in `local\iso\` (4.3 GB each; delete when not needed): test-s1-hb9f (quiet Borough with Donald
  and Goofy), test-s1-skate-s2 (two Sora boards beside the heroes), test-v4-al109 / tt187 / hb99 / nm75 / ca88
  (the five challenges), test-v4-tt91 (Mail Delivery), test-v4-tt07roam (free roam with boards).

""".replace("PKGID", pkg).replace("REHEARSAL", rehearsal)
final = (ROOT / "local" / "final-notes.txt")
NOTES = NOTES.replace("FINALRESULTS", final.read_text(encoding="utf-8").strip() if final.exists() else "")
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, NOTES + marker)
p.write_text(t, encoding="utf-8")

q = ROOT / "KH2-COOP-PLAN.md"
s = q.read_text(encoding="utf-8")
if "| 20 | Donald and Goofy |" not in s:
    lines = s.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("| 19 | Things in a room and bosses")]
    assert len(idx) == 1
    lines[idx[0] + 1:idx[0] + 1] = [
        "| 20 | Donald and Goofy | **One helper goes with each hero when the heroes are far apart** (the user's rule of "
        "2026-11-10, built 2026-11-11; numbers taken as the recommended option): closer than 900 units everybody "
        "follows player 1's hero as before; farther apart each hero gets the helper who is nearer to him; they are "
        "one group again when the heroes are closer than 550. |",
        "| 21 | Skateboards in free roam and the skate challenges | **A second board beside EVERY skateboard of the game** "
        "(2026-11-11, taken as the recommended option; new disc file v4): 147 places in 29 rooms. The five skate "
        "challenges put each player on a board; either player's tricks and checkpoints count. |",
        "| 22 | A boss's scripted move (it grabs a hero) | **The player whose hero is in the move sees the move; the other "
        "player keeps his own camera** (2026-11-11, taken as the recommended option). Story scenes stay one picture "
        "for both. |",
    ]
    q.write_text("\n".join(lines), encoding="utf-8")
print("state and plan updated")
