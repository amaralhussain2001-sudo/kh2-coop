"""One-off: read-me of TEST build 4, after the lock-on fix (Grandstander works with player 2's hits)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
t = p.read_text(encoding="utf-8")
old = """- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: Mail Delivery
  (only player 1 gets the skateboard), Grandstander (the job stalls if player 2 hits the ball), the bag job,
  and the counter of two "hit them N times" fights does not count player 2's hits. If a job cannot be finished,
  let player 1 do it alone and tell me which one it was."""
new = """- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: Mail Delivery
  (only player 1 gets the skateboard), the bag job, and the counter of two "hit them N times" fights does not
  count player 2's hits. If a job cannot be finished, let player 1 do it alone and tell me which one it was.
  Grandstander (keep the ball in the air) now counts player 2's hits too; after a miss the ball comes back
  beside player 1's hero."""
if t.count(old) != 1:
    raise SystemExit("text not found (%d)" % t.count(old))
t = t.replace(old, new)
old2 = """- Each hero is moved by its own controller: run, jump, attack and combos, guard, dodge, magic through the L1
  shortcuts, own lock-on target. Each hero walks by its own camera."""
if t.count(old2) == 1:
    t = t.replace(old2, old2 + """
  Each hero's attacks go for his own target (in build 3 player 2's swings used player 1's target).""")
p.write_text(t, encoding="utf-8")
print("read-me updated")
