"""One-off: docs/STATE.md, what was learned about the hit-counter fight (lane S1 row TTR-10) after the lock-on fix."""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "### 9. The hit-counter fights (NOT solved)" in t:
    raise SystemExit("already there")
notes = r"""### 9. The hit-counter fights (NOT solved; what was tried on 2026-11-11)

- Disc `local\iso\test-s1-tt127.iso` (Old Mansion, the Dusk that cannot be damaged, lane S1 row TTR-10).
  Baselines on the final patch: player 1 attacking, the story scene plays by frame 8900 (h1-dusk-p1; the picture
  layout byte 0x000F6F00 is 0 there); only player 2 attacking, no scene in 9,000 and in 12,000 frames
  (g8-dusk-old1, h1-dusk-p2). The signal used: `tools\own\room_probe.py` (layout byte at the snapshot frames).
- The bit-coded search over the 119 loads of the engine's player pointer (`tools\own\dusk_bits.sh`, tests
  h2-plbit0..6) showed the scene in variants 0, 3 and 4. Read as one place that would be index 25 = the load at
  0x00189E40 in routine 0x00189E18. That routine offers a Reaction Command to the control object of the engine's
  player: through 0x001BD418 when the source object is that player, through 0x001BD3E0 when the source is
  anything else; on success it notes the command in the player object (+0x50C, flag 0x20000 at +0x160).
- Three tries, none let the story go on with only player 2 attacking: only that one load switched
  (`make_playerbits.py ... only 25`, test h4-site25); "the twin's own action counts as the player's" (hook
  0x00189E3C); "offer to the hero it belongs to, or to both heroes" (wrapper at 0x00189E18, the pointer
  0x0034E948 holding the twin for the second call; test h3-dusk-react). So more than one place is involved; the
  three variants share many indices.
- The wrapper is kept in `tools\merge\merge_v6.py` as the option `--react` (off; NOT in any build). Its
  routines sit at 0x000F4A00, where the test-only recorder `tools\own\make_diag_null.py` keeps its data: do not
  use the two together.
- Next ideas: a search over pairs (switch the indices of variants 3 and 4 that are not in variants 1, 2, 5, 6,
  then halve); or find the counter itself (the fight's script is in `local\analysis\h\ai`, the mission is
  TT14_MS109) and read what feeds it.
- Seen on the way: player 2's screen shows the "Reversal" prompt in that fight on the final patch (g8, frame
  7500), so enemy Reaction Commands do reach his control object in some cases already.

"""
marker = "### 7. Files\n"
assert t.count(marker) == 1
t = t.replace(marker, notes + marker)
old = """   two Nobody fights (NOT cured by the lock-on fix: test g8-dusk-old1, the story did not go on in 4,000 frames of
   player 2's attacks; the counter's place is still not located). Grandstander is DONE (part 8 of "Merge 6 and
   test build 4")."""
new = """   two Nobody fights (NOT cured by the lock-on fix; three more tries failed, see part 9 of "Merge 6 and test
   build 4" before going on). Grandstander is DONE (part 8)."""
assert t.count(old) == 1
t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("state updated")
