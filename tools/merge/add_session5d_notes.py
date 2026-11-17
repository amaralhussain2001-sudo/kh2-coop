"""One-off: docs/STATE.md, what the quiet-room try for the helpers showed (test m1-hb13dg)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
if "m1-hb13dg" in t:
    raise SystemExit("already there")
a = t.index("3. Helpers with both heroes. Two tries failed")
b = t.index("4. Not seen in a game yet:", a)
t = t[:a] + r"""3. Helpers with both heroes. Two tries failed (builder option `--helper`, header TENTH GLUE): in a fight the
   helpers are not led by the engine's player pointer (bit search l4-helpbit0..6 on the morale mission: in no
   variant did a helper go to the twin, 2,000 units away). A quiet-room disc made with
   `build_disc.py hb13dg --jump1 "HB 13 0" --party DEFAULT` has NO helpers (test m1-hb13dg: party places 1 and 2
   empty; the fresh save's party is the hero alone there), so it was deleted. Next: a room whose program brings
   helpers without enemies (a Pride Lands or Timeless River program after its fight, or a mission disc whose
   enemies are removed by an override), `tools\own\party_probe.py`, and other "leader" sources than the engine's
   player pointer: the party table's place 0 (0x00348638, read through 0x0013DDA0) and the helper scripts'
   own data.
""" + t[b:]
p.write_text(t, encoding="utf-8")
print("state updated")
