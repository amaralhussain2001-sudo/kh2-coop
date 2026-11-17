"""One-off: docs/STATE.md, plan and memory after test build 7 (twelfth glue: the nearer hero is "the player" for
an object's own thinking)."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "after test build 7" in t:
    raise SystemExit("already there")


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:60])
    t = t.replace(old, new)


rep("## PICK UP HERE (rewritten 2026-11-11 evening, after test build 6)",
    "## PICK UP HERE (rewritten 2026-11-11 late evening, after test build 7)")
rep("rows 10-18 are the newest)", "rows 10-19 are the newest)")
rep("""  * SHARED SCREEN = `patches\\merged-v6` (SHA-1 7f7fd70c4a8f559754a8d57e9a72b870e84cb60d) = merged build 5 + ten
    glues (""", """  * SHARED SCREEN = `patches\\merged-v6` (SHA-1 ab2362a495a3374ef9a3f5cb6c7372fc1cb86b99) = merged build 5 + eleven
    glues (the nearer hero is "the player" for an object's own thinking; """)
rep("""  * OWN SCREENS = `patches\\merged-v6-own` (3,351 words, SHA-1 2124047f775090044e6d8b1c0761c44decb5fb46)""",
    """  * OWN SCREENS = `patches\\merged-v6-own` (3,413 words, SHA-1 2be381e83f0598b1a65c75cc89f41d01885a3c17)""")
rep("""- The test package in `dist\\` is BUILD 6 (package id c2689134df54)""",
    """- The test package in `dist\\` is BUILD 7 (package id 8d116c1087c7)""")
rep("""Friend kit SHA-1 63417814ebc26f02b24e2bf766698cce145a2599, KH2 patch file
  SHA-1 592ab5a565eee2b1fc73b99bdc9d3bbea711e5b5. Rehearsed through the launchers (p8-rehearsal-b6).""",
    """Friend kit SHA-1 0e1cde7a0344ca482a352e7b4d078d113ebc3e5c, KH2 patch file
  SHA-1 44b517763af99577766f312bbc9cd90057f11199. Rehearsed through the launchers (p9-rehearsal-b7).""")
a = t.index("   b. The bag ride, Twilight Thorn and the other carried-hero Reaction Commands (lane S1 section 3).")
b = t.index("3. Helpers with both heroes.")
t = t[:a] + r"""   b. The bag ride: DONE for either player (twelfth glue, part 8). Twilight Thorn: its commands go to the nearer
      hero and the fight runs; what a full version still lacks: both heroes in one scripted move, the camera of
      the other player during a move (both screens show the move's picture), a long two-human run.
""" + t[b:]
notes = r"""### 8. "The player" of an object's own thinking is the nearer hero (twelfth glue; test build 7)
- Found through the bag of the Seven Wonders (TT12_WORK_BOX, object F_TT110): its script asks
  trap_sysobj_player and offers "Jump" with trap_command_override; its handler (commands 507 / 508) works for
  any hero. The older `--react` experiment (offer to both) did not help (q2-bag-react).
- Glue `near_think` (0x000F5000, jump at the entry of 0x0016A950 "an object thinks": script and action list):
  for an object that is neither a hero nor a helper (class table 0x00345C08), the engine's player pointer holds
  the twin for the length of that call when the twin is nearer (flat distance, +0x70 / +0x78) or when player
  1's hero is down; never when the twin is down. Not sticky. Option `--no-nearest`.
- VERIFIED: q3-bag-near / r1-bag-p2 (only player 2 presses: he rides, gauge 100 -> 77 -> 30 -> 0, "Jump" in HIS
  menu), r1-bag-p1 (player 1 alone: as before); q4-thorn-near and r1-thorn-p2 (Twilight Thorn, 12,000 frames,
  in sync, no crash; "Reversal" on player 2's screen when he is nearer; the scripted moves play); the other
  special scenes on this build with `tools\own\near_batch.sh` (`local\r1-batch.log`): Dusk counter scene, Mail
  Delivery (both at menu 14), morale gauge (80.7 / 44.4 / 7.0 as before), Grandstander (hits 4, landing 1:
  r2-grand-near); save point: "Save" stays with the hero who stands on it (r3-save-near).
- Validation: `suite_v6.sh` 9 of 9 in sync, pairs identical, one-hero pictures as before
  (`local\m6-suite-n.log`); `suite_v5_short.sh` 3 of 3, one hero alone 4 of 4 the same as merged build 5
  (`local\m5s-suite-n.log`); `batch_v7.sh test-own-v6-near` 6 of 6 (`local\own-batch7-n.log`).
- Package: `edit_readme_v7.py`, `make_package_patch.py`, `make_test_package.py --rebuild` -> id 8d116c1087c7;
  rehearsal p9-rehearsal-b7 (join code after 7 s, 9,000 frames, never out of sync, v3 check number, same
  memory card file on both). Copies deleted. Disc unchanged since build 6 (v3).
- RISKS that only long play can show (HYPOTHESIS, not seen): a script that remembers "the player" and compares
  it later could hiccup when the nearer hero changes in between; scripted moves that run many steps. If a boss
  or a thing in a room acts oddly for two, test with `--no-nearest` first.
- Test discs added: `local\iso\test-s1-tt125.iso` (bag), `test-s1-tt157.iso` (Twilight Thorn),
  `test-v3-tt91.iso` (Mail Delivery on the v3 data). `tools\own\stop_tests.ps1` stops every running test.

"""
marker = "## Open items\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
p.write_text(t, encoding="utf-8")

q = ROOT / "KH2-COOP-PLAN.md"
s = q.read_text(encoding="utf-8")
if "| 19 | Things in a room and bosses |" not in s:
    lines = s.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("| 18 | Skateboards")]
    assert len(idx) == 1
    lines.insert(idx[0] + 1, "| 19 | Things in a room and bosses | **They deal with the NEARER hero** (2026-11-11, "
                 "taken as the recommended option): an object's own script sees the nearer hero as \"the player\", "
                 "a hero who is down is skipped. So either player can ride the bag, and a boss's Reaction Command "
                 "goes to the player who stands nearer. Helpers and the heroes themselves are not changed. |")
    q.write_text("\n".join(lines), encoding="utf-8")

BS = chr(92)
M = pathlib.Path("C:" + BS + "Users" + BS + "PC FORCE" + BS + ".claude" + BS + "projects" + BS
                 + "C--Users-PC-FORCE-Desktop-New-folder--3-" + BS + "memory")
m = M / "kh2-coop-ps2-project.md"
mt = m.read_text(encoding="utf-8")
if "8d116c1087c7" not in mt:
    mt = mt.rstrip("\n") + "\n\n" + (
        "Late evening of 2026-11-11: test package BUILD 7, id 8d116c1087c7 (disc v3 unchanged). New rule in the "
        "patch: for an object's own thinking \"the player\" is the NEARER hero (a downed hero is skipped). With it "
        "player 2 can ride the bag of the Seven Wonders and gets boss Reaction Commands (Twilight Thorn) when he is "
        "nearer. Validated by all suites and rehearsed. If a boss or room object acts oddly for two, the builder "
        "option `--no-nearest` takes the rule out.\n")
    m.write_text(mt, encoding="utf-8")
i = M / "MEMORY.md"
it = i.read_text(encoding="utf-8")
it = it.replace("builds (merged-v6, disc v3, test package 6, id c2689134df54)", "builds (merged-v6, disc v3, test package 7, id 8d116c1087c7)")
i.write_text(it, encoding="utf-8")
print("state, plan and memory updated")
