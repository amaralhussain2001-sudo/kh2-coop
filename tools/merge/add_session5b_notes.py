"""One-off: docs/STATE.md after test build 5: the PICK UP HERE head is rewritten, the validation part is added to
"Second round on merged build 6", plan rows 15-17 are added.
  python -I tools/merge/add_session5b_notes.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "after test build 5" in t:
    raise SystemExit("already there")
a = t.index("## PICK UP HERE")
b = t.index("How to repeat: patches")
head = r"""## PICK UP HERE (rewritten 2026-11-11 afternoon, after test build 5)

Read this section first, then `..\KH2-COOP-PLAN.md` (plan, rules, all user decisions; rows 10-17 are the newest)
and `REQUIREMENT-full-parity.md`. The rest of this file is the detailed record. Lane reports are in
`docs\lanes\`. The parity checklist is `docs\PARITY-CHECKLIST.md`.

Where things stand:
- TWO builds, both on disc `local\iso\kh2-coop-v2.iso` (SHA-1 12edc56fdb0baac302c373e554185921242e6533, unchanged):
  * SHARED SCREEN = merged build 6, second round: `patches\merged-v6` (1,808 words, SHA-1
    ba3d261e31188342649cea5ac20c58ef9f0b0e11) = merged build 5 + nine glues (own Drive values; text boxes, START,
    main menu, rules screens and the menu's reveal on either controller; prizes; lock-on target; hits counted by
    mission scripts; mission-gauge prizes; Drive Forms for the second hero). Builder `tools\merge\merge_v6.py`
    (its header explains every glue). Two experiments are in the builder but NOT in the build: `--react`,
    `--helper`.
  * OWN SCREENS = `patches\merged-v6-own` (3,315 words, SHA-1 f0c65c02962313b4cbbb4f2a1d51760ca90aab20) = the
    above + lane V1's two views + lane V2's HUD per player + the command menu's rows per player (builder
    `tools\own\make_own.py`, step 7, now with the menu's "revealed" state common to both players). Needs the
    emulator build `emulator-src\builds\view12` and `patches\own-view\SLPM-66675_F266B00B.view` (unchanged).
- The test package in `dist\` is BUILD 5 (package id 8a2aa7970f68): own screens, with the shared-screen patch
  inside as a fallback file. Friend kit SHA-1 195064cf6a6c84bf01e55b556ce673cf2e6d7ecb, KH2 patch file SHA-1
  e4ab5613507798bdd7887409059eb320fc170f8b. Rehearsed through the launchers (p7-rehearsal-b5). No humans have
  played yet. The disc file did not change (TEST v2).
- TESTS MUST NOT DISTURB THE USER: every test emulator starts on a hidden Windows desktop
  (`tools\quiet_launch.py`). Never use `--show` unless the user asks.
- A stopped suite keeps running unless its bash and emulator processes are killed too. After TaskStop, kill
  `suite_*.sh`, `mrun.sh`, `batch_v*.sh`, `run_own*.sh`, `dusk_one.sh`, `kh2_session.py`, `v3_session.py` and the
  `local\run-*` emulators (PowerShell, by command line). One suite on `local\run-m` at a time; `local\run-v3`
  and `local\run-v3b` are two more sandboxes, so three things can run at once.
- No lane (agent) is running. The user said: do NOT open extra lanes.

User answers and remarks:
- 2026-11-10 night: "why you stop continue until u finish for your question use the Recommended", then "continue
  until finish all the tasks". 2026-11-11: "why you stop not finish all the tasks?" and "finish all the tasks
  then i'm going to test it one time after u finish everything". So: no stopping for A/B questions, no report
  that reads like an end while the list below has jobs that can be done; the user tests ONCE at the end.
- "is the money shared, but their skills different?": answered (one wallet, one item stock; level, skills,
  equipment the same for both); own skills / equipment stay a Phase 4 job unless the user asks (plan row 11).
- Taken as the recommended option without asking (plan rows 15-17): one Drive Form at a time (the game's own
  lock); the twin's hits count as the player's for mission scripts; rules screens on either controller.

Next jobs, in order (section "Second round on merged build 6" has what was done and learned on 2026-11-11):
1. The two-human test (the user's, once, at the end) with the newest build; read the logs they send back.
2. Prologue jobs that need real work (lane S1):
   a. Mail Delivery. Plan worked out, not started: the mission's script (`msn\jp\TT06_WORK_LETTER.bar`, text in
      `local\analysis\lane-s1\msn\TT06_WORK_LETTER_0.txt`) mounts the player with
      trap_obj_reaction_callback(board, player, 327, board) (board = first object with status 5067). A second
      board in the mission's group (data; lane S1's recipe `local\variants\s1-mail-src`) and the same call for
      the twin are needed. Cleanest: edit the script (search both by spawn serial, trap_obj_search_by_entry) and
      re-encode it with Bdxio; that is a NEW DISC (v3) for both players. Also TT06_LETTER_01 / _02 and the
      skate missions of other worlds.
   b. The bag ride, Twilight Thorn and the other carried-hero Reaction Commands (lane S1 section 3).
3. Helpers with both heroes. Two tries failed (builder option `--helper`, header TENTH GLUE): in a fight the
   helpers are not led by the engine's player pointer. Next: a quiet room with the heroes apart (a jump disc
   with `--party DEFAULT`), `tools\own\party_probe.py`, then the bit search again.
4. Not seen in a game yet: mission-gauge prizes for the second hero (eighth glue; disc
   `local\iso\test-s1-mu68.iso` starts in the first morale mission, but the script-driven twin walked away from
   the fight); the six other "hits counted" missions; result screens of jobs with only controller 2; Drive
   Forms other than Limit; a Game Over while the twin is in a form; the shop and the journal with two views.
5. Own screens, still open: a small orange glint beside player 2's gauge in the first town; the 2-3 step
   return of two views after a death or mission event; sound listener (HYPOTHESIS: player 1's camera); text
   boxes and the "Waiting" sign on both screens (kept on purpose).
6. Seen once, not examined: a Limit Form body in a T-pose for a moment (test k8-formdie frame 9400, both heroes
   at 1 HP, form clock at its end); the dim "Examine" banner on player 2's screen in Merlin's house.
7. Feasibility tests continue down `docs\PARITY-CHECKLIST.md` in story order; boss moves written against "the
   player"; button-mash moves of 7 object scripts read controller 1 only.
8. Never run on a real path: Continue after a Game Over or a failed mission INSIDE a mission.
9. The PARK experiment (`tools\own\fork_views.py`); the null-read riddle (pc 0x0016E3C0 with the magic kit).

"""
t = t[:a] + head + t[b:]

val = r"""### 6. Validation of the final patches and test build 5 (2026-11-11)
- The test folders `patches\test-v6-e` / `test-own-v6-e` are word for word what the builders write into
  `patches\merged-v6` / `merged-v6-own` (checked: same SHA-1 for the shared file; the own-screen files differ
  only in the comment line that names the base folder).
- Own-screen suite `suite_v6.sh`: 9 of 9 in sync, every screenshot pair of the same view identical; the
  one-hero run's pictures have the same check sums as in the validation of build 4 (`local\m6-suite-e.log`).
- Shared-screen `suite_v5_short.sh`: 3 of 3 in sync; one hero alone: 4 of 4 pictures the same as merged build 5
  (`local\m5s-suite-e.log`).
- Own-screen batch `batch_v7.sh test-own-v6-e`: 6 of 6 in sync (`local\own-batch7.log`); menu lists per player
  as before (y4v-menu).
- More form tests on the final patch: k7-formend (player 2's form runs out by itself after about 80 s: normal
  body again, still the second hero, two views), k8-formdie (both at 1 HP in the Borough with the twin in a
  form: no Game Over happened in that run; all normal at the end).
- Package: `python -I tools\package\edit_readme_v5.py`, `make_package_patch.py`, `make_test_package.py --rebuild`
  -> id 8a2aa7970f68. Rehearsal p7-rehearsal-b5 through both launchers: join code after 8 s, 9,000 frames, 140
  digests, never out of sync, own picture on each PC, both memory cards the same file. Copies deleted again.
- Test discs kept in `local\iso\`: test-s1-tt84 (Struggle), tt90, tt90g (Grandstander), tt127 (Old Mansion
  Dusk), mu68 (first morale mission). 4.3 GB each; delete when not needed.

"""
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, val + marker)
p.write_text(t, encoding="utf-8")

q = ROOT / "KH2-COOP-PLAN.md"
s = q.read_text(encoding="utf-8")
if "| 15 | Drive Forms with two heroes |" not in s:
    lines = s.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("| 14 | Player 2's attack target")]
    assert len(idx) == 1
    rows = [
        "| 15 | Drive Forms with two heroes | **Each player can use Drive; one form at a time** (2026-11-11, taken as "
        "the recommended option). Only the hero who chose it changes; he has his own form gauge, his own menu and "
        "keeps the form through a door. While one hero is in a form the other's Drive row is dim: that is the "
        "game's own lock, kept because a form uses up Donald or Goofy. Tested with Limit Form. |",
        "| 16 | Counters of mission scripts | **A hit by the second hero counts as a hit by the player** in the mission "
        "scripts' damage event (2026-11-11). Fixes the two \"cannot be hurt\" fights of the prologue and six later "
        "missions with the same script. |",
        "| 17 | Full screens of the small games | **Rules screens and the Game Over menu work on either controller**; "
        "the first button press of EITHER player brings the command menu up (2026-11-11). Result screens: not "
        "found to need a button yet. |",
    ]
    for k, r in enumerate(rows):
        lines.insert(idx[0] + 1 + k, r)
    q.write_text("\n".join(lines), encoding="utf-8")
print("state and plan updated")
