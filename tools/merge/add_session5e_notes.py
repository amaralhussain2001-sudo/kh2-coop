"""One-off: docs/STATE.md, plan and memory after test build 6 (Mail Delivery for two, disc v3)."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "after test build 6" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)


rep("## PICK UP HERE (rewritten 2026-11-11 afternoon, after test build 5)",
    "## PICK UP HERE (rewritten 2026-11-11 evening, after test build 6)")
rep("`..\\KH2-COOP-PLAN.md` (plan, rules, all user decisions; rows 10-17 are the newest)",
    "`..\\KH2-COOP-PLAN.md` (plan, rules, all user decisions; rows 10-18 are the newest)")
a = t.index("- TWO builds, both on disc `local\\iso\\kh2-coop-v2.iso`")
b = t.index("- TESTS MUST NOT DISTURB THE USER")
t = t[:a] + r"""- TWO builds, both on the NEW disc `local\iso\kh2-coop-v3.iso` (SHA-1 23504a4bacc419144d68578192b8848519eda3ec
  = disc v2 + Mail Delivery for two; builder `tools\merge\build_disc_v3.py`; v2 is still in `local\iso`):
  * SHARED SCREEN = `patches\merged-v6` (SHA-1 7f7fd70c4a8f559754a8d57e9a72b870e84cb60d) = merged build 5 + ten
    glues (own Drive values; text boxes, START, main menu, rules screens and the menu's reveal on either
    controller; prizes; lock-on target; hits counted by mission scripts; mission-gauge prizes; Drive Forms for the
    second hero; the skateboard's commands on the rider's own control object). Builder
    `tools\merge\merge_v6.py` (its header explains every glue). Two experiments are in the builder but NOT in
    the build: `--react`, `--helper`.
  * OWN SCREENS = `patches\merged-v6-own` (3,351 words, SHA-1 2124047f775090044e6d8b1c0761c44decb5fb46) = the
    above + lane V1's two views + lane V2's HUD per player + the command menu's rows per player (builder
    `tools\own\make_own.py`). Needs the emulator build `emulator-src\builds\view12` and
    `patches\own-view\SLPM-66675_F266B00B.view` (unchanged).
- The test package in `dist\` is BUILD 6 (package id c2689134df54): own screens, the shared-screen patch inside
  as a fallback file, and a NEW disc patch `kh2-coop-v3.kh2patch` (both players must make the "TEST v3" disc
  file; check number 23504a4b...). Friend kit SHA-1 63417814ebc26f02b24e2bf766698cce145a2599, KH2 patch file
  SHA-1 592ab5a565eee2b1fc73b99bdc9d3bbea711e5b5. Rehearsed through the launchers (p8-rehearsal-b6). The disc
  patch was applied to the original image in a temporary file and gave the v3 check number
  (`tools\package\check_disc_patch.py`). No humans have played yet.
""" + t[b:]
a = t.index("2. Prologue jobs that need real work (lane S1):")
b = t.index("3. Helpers with both heroes.")
t = t[:a] + r"""2. Prologue jobs that need real work (lane S1):
   a. Mail Delivery: both ride now (section "Second round", part 7). Not tested: letters handed in by player 2,
      the end of the job (both get off), TT06_LETTER_01 / _02 in a game (same script edit, built), a board in
      free roam with own screens. The five skate-challenge missions of other worlds (AL00, CA02, HB09, NM09,
      TT07 SKATE_01) use the same forced mount and still have ONE board: same recipe (`make_mail.py`).
   b. The bag ride, Twilight Thorn and the other carried-hero Reaction Commands (lane S1 section 3).
""" + t[b:]

notes = r"""### 7. Mail Delivery for two: disc v3, eleventh glue, test build 6 (2026-11-11 evening)
- The mission script (`tt06_work_lette` in `msn\jp\TT06_WORK_LETTER.bar`, the same in TT06_LETTER_01 / _02)
  mounts the player at the start: trap_obj_reaction_callback(board, player, 327, board), board = the first
  object with status 5067. The board's own script (F_TT010, trigger REACTION_CALLBACK, command 327) works for
  any hero.
- DATA (`tools\lane-s1\make_mail.py`, run by `tools\merge\build_disc_v3.py`): a second board in the two Mail
  Delivery groups of tt06 (b_40: 0x05AB serial 70; b_43: 0x081A serial 242; 110 units beside the first, where
  the twin stands), and the three mission scripts edited as text with OpenKH's Bdxio (decode, edit, encode;
  the English mission files are the base): the player's board is taken by its serial (69 / 241), then the second
  board and the twin (serials from lane F's report: 278 / 281) are found with trap_obj_search_by_serial and get
  the same call. The encoder writes some unused instruction bits as 0; the decoded text is the same and the
  game runs it.
- First try, wrong: with the stock search the NEW board was found first, both riders were put on it (recorder
  test n4-mail-dbg, `tools\own\make_dbg_board.py`; object list n5-mail-near).
- CODE (eleventh glue, `sk_ride`, `sk_who`, `sk_off` at 0x000F4F00, variable 0x000F47F0): the board commands
  (control object menu 14) were opened and closed on the engine's player's control object only
  (0x00198860 / 0x00198970, loads at 0x00198910 / 0x00198990). Now on the rider's own. Needed in free roam too.
- VERIFIED (disc `local\iso\test-v3-tt91.iso`, jump into the job): n6-mail-ok (both on their own board, both
  control objects at menu 14, "Heelflip / Get Off / Jump" on both screens), n7-mail-ride (player 2 closes the
  rules screen, rides down the street on controller 2, his view follows; player 1 stays).
- Validation of the final patches: `suite_v6.sh` 9 of 9 in sync, pairs identical, one-hero pictures as before
  (`local\m6-suite-g.log`); `suite_v5_short.sh` 3 of 3, one hero alone 4 of 4 the same as merged build 5
  (`local\m5s-suite-g.log`); `batch_v7.sh test-own-v6-g` 6 of 6 (`local\own-batch7-g.log`); New Game on the
  full v3 disc in sync (o1-newgame-v3). The suites' own discs are v2-era test discs.
- Package: `tools\package\edit_package_v6.py` (v3 names, read-me BUILD 6), disc patch
  `python -I tools\lane-t\make_disc_patch.py <original> local\iso\kh2-coop-v3.iso
  local\package\kh2-coop-v3.kh2patch` (the original is only read; its SHA-1 is still 81c177a3...),
  `make_package_patch.py`, `make_test_package.py --rebuild` -> id c2689134df54; rehearsal p8-rehearsal-b6 (join
  code after 7 s, 9,000 frames, never out of sync, game file check = the v3 number, same memory card file on
  both). Copies deleted again.

"""
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
rep("disc `python -I tools\\merge\\build_disc_v2.py\nkh2-coop-v2.iso`", "disc `python -I tools\\merge\\build_disc_v3.py\nkh2-coop-v3.iso`")
p.write_text(t, encoding="utf-8")

q = ROOT / "KH2-COOP-PLAN.md"
s = q.read_text(encoding="utf-8")
if "| 18 | Skateboards |" not in s:
    lines = s.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("| 17 | Full screens of the small games")]
    assert len(idx) == 1
    lines.insert(idx[0] + 1, "| 18 | Skateboards | **Each player has his own board and his own board commands** "
                 "(2026-11-11). Mail Delivery starts both heroes on a board each; this needed a new disc file "
                 "(TEST v3: a second board in the job's room data and a changed mission script). The skate "
                 "challenges of other worlds still have one board. |")
    q.write_text("\n".join(lines), encoding="utf-8")

BS = chr(92)
M = pathlib.Path("C:" + BS + "Users" + BS + "PC FORCE" + BS + ".claude" + BS + "projects" + BS
                 + "C--Users-PC-FORCE-Desktop-New-folder--3-" + BS + "memory")
m = M / "kh2-coop-ps2-project.md"
mt = m.read_text(encoding="utf-8")
if "c2689134df54" not in mt:
    mt = mt.rstrip("\n") + "\n\n" + (
        "Evening of 2026-11-11: Mail Delivery for two works (each hero on his own skateboard with his own board "
        "menu). It needed a NEW DISC, v3 (`local" + BS + "iso" + BS + "kh2-coop-v3.iso`, SHA-1 23504a4b..., builder "
        "`tools" + BS + "merge" + BS + "build_disc_v3.py`: second board in the room data + mission scripts edited with "
        "OpenKH's Bdxio) and one more code glue. Test package BUILD 6, id c2689134df54, with the disc patch "
        "`kh2-coop-v3.kh2patch`: both players must make the \"TEST v3\" disc file. Validated and rehearsed. "
        "Still open: the bag ride, Twilight Thorn, helpers with both heroes, the skate challenges of other worlds.\n")
    m.write_text(mt, encoding="utf-8")
i = M / "MEMORY.md"
it = i.read_text(encoding="utf-8")
it = it.replace("builds (merged-v6, test package 5, id 8a2aa7970f68)", "builds (merged-v6, disc v3, test package 6, id c2689134df54)")
i.write_text(it, encoding="utf-8")
print("state, plan and memory updated")
