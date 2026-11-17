"""One-off: docs/STATE.md after the lock-on fix (fifth glue of merged build 6) and the rebuilt package.
  python -I tools/merge/add_session4b_notes.py "<suite result line>" "<short shared result line>"
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "### 8. The second hero's attack uses his own lock-on target" in t:
    raise SystemExit("already there")
suite_line, short_line = sys.argv[1], sys.argv[2]


def rep(old, new, count=1):
    global t
    if t.count(old) != count:
        raise SystemExit("expected %d place(s) for %r (found %d)" % (count, old[:60], t.count(old)))
    t = t.replace(old, new)


rep("`patches\\merged-v6` (1,564 words, SHA-1 5310545bb25a56accafc13d23b1b799186edc4ea) = merged build 5\n"
    "    + own Drive values for the second hero + text boxes, START and the main menu on either controller + prizes\n"
    "    for the second hero.",
    "`patches\\merged-v6` (1,572 words, SHA-1 ea3e4de39130afda4cca315ad801562f50531710) = merged build 5\n"
    "    + own Drive values for the second hero + text boxes, START and the main menu on either controller + prizes\n"
    "    for the second hero + the second hero's attack uses his own lock-on target.")
rep("`patches\\merged-v6-own` (3,067 words, SHA-1 2f4dd968234a2d5744dc2741849f8b75cc42ed08)",
    "`patches\\merged-v6-own` (3,075 words, SHA-1 d23e0077d818db521513fd4d8fb5765c395a76b7)")
rep("is BUILD 4 (package id 172b2f8e8001)", "is BUILD 4 (package id 538e811e10f7)")
rep("Friend kit SHA-1 6e3b0391d0a26dcde779172de1cfc0e97254c482, KH2 patch file SHA-1 c4d8766f0fd801dcbf486c1cf4a4bc9b8ae5f55f. Rehearsed through the launchers (p5-rehearsal-b4).",
    "Friend kit SHA-1 1f5fa5497a833a2ebcd8646d46bfd913f26dfdde, KH2 patch file SHA-1 b168b7430a0caa08e46e8a0d36a20106d8a5adba. Rehearsed through the launchers (p6-rehearsal-b4).")
rep("""4. Prologue jobs that need real work (lane S1): Grandstander (ball rule; STARTED: disc rebuilt, stall shown on
   the final build, first reading of the ball's script; see the end of "Merge 6 and test build 4", part 6),
   Mail Delivery (second board), the bag ride, the hit counters of two Nobody fights.""",
    """4. Prologue jobs that need real work (lane S1): Mail Delivery (second board), the bag ride, the hit counters of
   two Nobody fights (NOT cured by the lock-on fix: test g8-dusk-old1, the story did not go on in 4,000 frames of
   player 2's attacks; the counter's place is still not located). Grandstander is DONE (part 8 of "Merge 6 and
   test build 4").""")
rep("- Taken that way: the Magic-list fault fixed now; own Drive gauge for each hero; either player closes text boxes\n"
    "  and opens / works the main menu; both heroes pick up prizes (plan rows 10, 12, 13).",
    "- Taken that way: the Magic-list fault fixed now; own Drive gauge for each hero; either player closes text boxes\n"
    "  and opens / works the main menu; both heroes pick up prizes; player 2's attacks use his own target (plan rows\n"
    "  10, 12, 13).")

notes = r"""### 8. The second hero's attack uses his own lock-on target (merged build 6, fifth glue; found through Grandstander)

- Fault (lane S1 row TTR-05; VERIFIED again on the final build, test g1-grand-base): in the Grandstander job
  player 2's swings sent the ball away, the screen stayed at 0 HIT and REST 5/5, and the job stalled.
- What the probe showed (`tools\own\near_probe.py`, test g3-grand-near): the ball is the object of class
  0x00350910 with script F_TT020; the script's own record of it (work word 0 -> record; +16 landings, +20 hits)
  stayed 0 / 0 while player 2 swung, so the swings never arrived as "damage". The script itself does not look at
  who hit.
- Test g4-grand-twinplayer (test-only patch `tools\own\make_twinplayer_test.py`: the engine's player pointer
  0x0034E948 = the twin): now hits 2, 4, then one landing. So the rule hangs on "the player".
- Search (`tools\own\make_playerbits.py`, tests g5-plbit0..6): each of the 119 loads of that pointer got an index;
  variant b lets the loads with bit b set see the twin (through the never-addressed word 0x0034E954, kept by a
  small test routine). Hits arrived in variants 3 and 4 only = index 24 = the load at 0x001874C0.
- The place: routine 0x001874A0(attacking hero, distance), called from the attack motion's event handler at
  0x0018958C when the hero has flag 2 at object+0x588. It asks routine 0x00187300 whether the attacker is at, or
  within the distance of, the target held by the lock-on manager of THE ENGINE'S PLAYER (player+0xB40, record
  +4). Player 1 stood far away with no target, so player 2's swing "had no target".
- Glue: hook 0x001874BC -> `lock_own` (0x000F48C0): when the attacker is the twin, his own object is used (so
  his own lock-on manager, lane G's second control object). One hero alone and player 1's attacks: unchanged.
- Result (test g6-grand-lock, player 2 alone swings): "2 HIT", "4 HIT, MAX HIT 4", landing, REST 4/5, the ball
  comes back beside player 1's hero; the script's record shows hits 1, 2, 4 and landing 1. Control g7-grand-p1
  (player 1 alone, final patch): MAX HIT 4, REST 4/5 as before.
- This is not only the ball: in every fight player 2's attack motions now test against HIS target, not player
  1's. The suite's attack windows (m6-i-attack) are in part 6.
- NOT changed: the sister routine 0x00187420 (called from 0x00189AB8; index 23 of the search, no effect on the
  ball). NOT cured: the hit counters of the two "cannot be damaged" Nobody fights (test g8-dusk-old1).
- Test discs kept: `local\iso\test-s1-tt90.iso`, `test-s1-tt90g.iso`, `test-s1-tt127.iso` (rebuilt with
  `tools\lane-s1\build_disc.py`; delete when not needed, 4.3 GB each).
- Validation of the final patches (six changes): %(SUITE)s
  %(SHORT)s
  Own-screen batch `batch_v6.sh`: 6 of 6 in sync (`own-batch.log`). Rehearsal p6-rehearsal-b4 (package
  538e811e10f7 through both launchers): join code after 8 s, 9,000 frames, 140 digests, never out of sync, own
  picture on each PC, memory cards byte-identical. The rehearsal copies were deleted again.

""".replace("%(SUITE)s", suite_line).replace("%(SHORT)s", short_line)
marker = "### 7. Files\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
p.write_text(t, encoding="utf-8")
print("state updated")
