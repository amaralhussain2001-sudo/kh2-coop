"""One-off: point the pick-up list of docs/STATE.md at the started Grandstander work."""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "STATE.md"
t = p.read_text(encoding="utf-8")
old = """4. Prologue jobs that need real work (lane S1): Mail Delivery (second board), Grandstander (ball rule), the bag
   ride, the hit counters of two Nobody fights."""
new = """4. Prologue jobs that need real work (lane S1): Grandstander (ball rule; STARTED: disc rebuilt, stall shown on
   the final build, first reading of the ball's script; see the end of "Merge 6 and test build 4", part 6),
   Mail Delivery (second board), the bag ride, the hit counters of two Nobody fights."""
assert t.count(old) == 1
p.write_text(t.replace(old, new), encoding="utf-8")
print("ok")
