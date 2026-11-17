"""Watch the unit slots (HP records) of a running sandbox emulator through PINE and log every change.

  python -I tools/lane-b75/slots_watch.py <port> <seconds> <out.tsv> [--set ENTRY:HP:AFTER[:PART]] ...

For each slot in use it reads: current and maximum HP (and the first three part values), and the enemy-table
entry the slot was filled from (slot+0x264 points at the entry; its first 16 bits are the entry id).
VERIFIED layout: slot k at 0x01C6C750 - 0x268*(k-1); 32 x (current, maximum, 0) at +0x000 (routine 0x001A0EE0).

--set ENTRY:HP:AFTER[:PART]  ONE-COPY TESTS ONLY (a memory write): AFTER seconds after a slot with that entry id
                             is first seen in a battle, write HP as its current HP (PART = which health value, default 0).
--keep-heroes                ONE-COPY TESTS ONLY: at every poll write the heroes' and friends' HP back to their maximum
                             (slots with a character status id), so a scripted test is not ended by a defeat.
"""
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0].rsplit("/", 1)[0] + "/lane-b")
from pine import Pine  # noqa: E402

SLOT1, STEP = 0x01C6C750, 0x268
NOW, BTL = 0x0032BAE0, 0x01C61958
port, secs, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
sets = []
argv = sys.argv[4:]
for i, a in enumerate(argv):
    if a == "--setmax":      # ONE-COPY ONLY: ENTRY:VALUE:AFTER -> write maximum HP and current HP of the main value
        p = argv[i + 1].split(":")
        sets.append({"entry": int(p[0]), "hp": int(p[1]), "after": float(p[2]), "part": 0, "seen": None, "done": False,
                     "max": True})
    if a == "--set":
        p = argv[i + 1].split(":")
        sets.append({"entry": int(p[0]), "hp": int(p[1]), "after": float(p[2]), "part": int(p[3]) if len(p) > 3 else 0,
                     "seen": None, "done": False})

keep = "--keep-heroes" in argv
boost = int(argv[argv.index("--boost-heroes") + 1]) if "--boost-heroes" in argv else 0   # ONE-COPY ONLY: heroes' HP and max HP
keep_entries = {int(argv[i + 1]) for i, x in enumerate(argv) if x == "--keep"}   # ONE-COPY ONLY: hold these entries at max HP
p = Pine(port, wait=120)
t0 = time.time()
last = None
f = open(out, "w", encoding="utf-8")
f.write("seconds\troom\tbattle\tslots (k:entry hp/max [parts])\n")
while time.time() - t0 < secs:
    try:
        now, btl = p.r16(NOW), p.r8(BTL)
        row = []
        for k in range(1, 15):
            base = SLOT1 - STEP * (k - 1)
            raw = p.read(base, 40)
            hp, mx = struct.unpack_from("<ii", raw, 0)
            if mx <= 0 and hp <= 0:
                continue
            parts = [struct.unpack_from("<ii", raw, 12 * j) for j in (1, 2)]
            ent = p.r32(base + 0x264)
            eid = p.r16(ent) if 0x00100000 <= ent < 0x02000000 else -1
            st = struct.unpack("<i", p.read(base + 0x254, 4))[0]
            if boost and eid < 0 and st > 0 and mx > 0 and (mx < boost or hp < boost):
                p.w32(base + 4, boost)
                p.w32(base, boost)
                hp = mx = boost
            if keep and eid < 0 and st > 0 and mx > 0 and hp < mx:
                p.w32(base, mx)
                hp = mx
            if eid in keep_entries and mx > 0 and hp < mx:
                p.w32(base, mx)
                hp = mx
            row.append((k, eid, st, hp, mx, parts))
            for s in sets:
                if eid == s["entry"] and btl and not s["done"]:
                    if s["seen"] is None:
                        s["seen"] = time.time()
                    elif time.time() - s["seen"] >= s["after"]:
                        if s.get("max"):
                            p.w32(base + 4, s["hp"])
                        p.w32(base + 12 * s["part"], s["hp"])
                        s["done"] = True
                        f.flush()
                        f.write("%.1f\tWRITE: slot %d (entry %d) health value %d set to %d\n" % (time.time() - t0, k, eid, s["part"], s["hp"]))
        cur = (now, btl, tuple((k, eid, hp, mx, tuple(parts)) for k, eid, st, hp, mx, parts in row))
        if cur != last:
            last = cur
            txt = "  ".join("%d:%s %d/%d%s" % (k, ("e%d" % eid) if eid >= 0 else ("s%d" % st), hp, mx,
                            (" [" + " ".join("%d/%d" % q for q in parts if q[1] > 0) + "]") if any(q[1] > 0 for q in parts) else "")
                            for k, eid, st, hp, mx, parts in row)
            f.write("%.1f\t%04X\t%d\t%s\n" % (time.time() - t0, now, btl, txt))
            f.flush()
    except Exception as ex:  # noqa: BLE001
        if time.time() - t0 > 20 and "closed" in str(ex).lower():
            break
        time.sleep(0.2)
        try:
            p = Pine(port, wait=5)
        except Exception:  # noqa: BLE001
            if time.time() - t0 > 30:
                break
    time.sleep(0.25)
f.close()
print("log:", out)
