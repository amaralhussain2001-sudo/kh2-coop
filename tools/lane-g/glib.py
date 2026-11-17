"""Lane G helpers: run a sandbox session (emulator copies local/run-g, port 28950, PINE 28071) and record chosen
memory ranges once per video frame through PINE (read-only).

    from glib import run, press, hold, NEWGAME
    rec = run("g-m1", iso, patch_dir, p1_lines, p2_lines, frames=6200, speed=2, ranges={...}, snaps=[...])
    rec.samples -> list of dicts {name: bytes}, each also has "vc" (the game's own pad-poll counter)
"""
import json
import pathlib
import socket
import struct
import subprocess
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
RUN_DIR, PORT, PINE = "run-g", "28950", 28071
ISO_CA5 = str(ROOT / "local" / "iso" / "test-b-ca5.iso")
ISO_ROAM3 = str(ROOT / "local" / "iso" / "test-b-roam3.iso")
ISO_ROAM = str(ROOT / "local" / "iso" / "test-b-roam.iso")
NEWGAME = ["3000 4 O", "3120 4 O", "3240 4 O", "3360 4 O", "3480 4 O", "3600 4 O"]

VC = 0x0034D4BC          # pad-1 poll counter: +1 per video frame (found by tools/lane-g/find_counter.py)
PAD1_RAW, PAD2_RAW = 0x0034D45C, 0x0034D5DC
LOG1, LOG2 = 0x0034D6C0, 0x0034D720
S = 0x01C5F530
SLOT1, SLOT_STEP = 0x01C6C750, 0x268


def press(button, start, end, every, length=4):
    return [f"{f} {length} {button}" for f in range(start, end, every)]


def hold(what, start, length):
    return [f"{start} {length} {what}"]


class Pine:
    def __init__(self, port, wait=90.0):
        t0 = time.time()
        while True:
            try:
                self.s = socket.create_connection(("127.0.0.1", port), timeout=10)
                return
            except OSError:
                if time.time() - t0 > wait:
                    raise
                time.sleep(0.2)

    def _rx(self, n):
        buf = bytearray()
        while len(buf) < n:
            c = self.s.recv(n - len(buf))
            if not c:
                raise ConnectionError("PINE closed")
            buf += c
        return bytes(buf)

    def read_many(self, ranges):
        """ranges: list of (addr, length). One request, so the values belong together as closely as PINE allows."""
        body = bytearray()
        plan = []
        for a, n in ranges:
            a0 = a & ~7
            k = (a + n - a0 + 7) // 8
            plan.append((a - a0, n, k))
            for i in range(k):
                body += b"\x03" + struct.pack("<I", a0 + 8 * i)
        self.s.sendall(struct.pack("<I", len(body) + 4) + bytes(body))
        size = struct.unpack("<I", self._rx(4))[0]
        rep = self._rx(size - 4)
        if rep[0] != 0:
            raise RuntimeError("PINE read refused")
        out, pos = [], 1
        for off, n, k in plan:
            out.append(rep[pos + off:pos + off + n])
            pos += 8 * k
        return out

    def r32(self, a):
        return struct.unpack("<I", self.read_many([(a, 4)])[0])[0]


class Rec:
    def __init__(self, name, out):
        self.name, self.out, self.samples, self.harness = name, out, [], ""

    @property
    def in_sync(self):
        return "never out of sync" in self.harness and "OUT OF SYNC" not in self.harness


def find_players(p):
    """Player-type objects = objects whose unit-slot pointer (object+0x48C) is unit slot 1. Returns object bases,
    lowest address first (the first-built object has the lower address in every scene seen so far)."""
    res = []
    for start in range(0x01800000, 0x01C00000, 0x40000):
        ram = p.read_many([(start, 0x40000)])[0]
        words = struct.unpack("<%dI" % (len(ram) // 4), ram)
        for i, w in enumerate(words):
            if w != SLOT1:
                continue
            base = start + i * 4 - 0x48C
            if base < start:
                continue
            off = base - start + 0x70
            x, y, z, wv = struct.unpack_from("<4f", ram, off)
            if all(abs(v) < 30000 for v in (x, y, z)) and abs(wv - 1.0) < 0.01:
                res.append(base)
    return sorted(res)


def run(name, iso, patch_dir, p1, p2, frames, speed=2, ranges=None, snaps=(), players=2, then="idle", bot="none",
        start_vc=0, timeout=420, full_at=(), extra=(), auto_objs=False, follow=None, script_end=None):
    """ranges: dict name -> (addr, length). Recording starts when the pad counter passes start_vc.
    full_at: list of pad-counter values at which the whole 32 MB is saved as ram_vc<value>.bin."""
    out = ROOT / "local" / "tests" / name
    out.mkdir(parents=True, exist_ok=True)
    for f in out.iterdir():
        try:
            f.unlink()
        except OSError:
            pass
    sdir = ROOT / "tests" / "scripts" / "lane-g"
    sdir.mkdir(parents=True, exist_ok=True)
    s1, s2 = sdir / f"{name}_p1.txt", sdir / f"{name}_p2.txt"
    # the last line fixes where the script ends; "then random" starts after it
    end = script_end or frames
    s1.write_text("\n".join(list(p1) + [f"{end} 1 "]) + "\n")
    s2.write_text("\n".join(list(p2) + [f"{end} 1 "]) + "\n")
    cmd = [sys.executable, "-I", str(ROOT / "tools" / "kh2_session.py"), "run", name, "--run-dir", RUN_DIR, "--port", PORT,
           "--iso", iso, "--players", str(players), "--slots", "0,1", "--frames", str(frames), "--speed", str(speed),
           "--script", str(s1), "--then", then, "--bot", bot, "--fresh-card", "--pine", str(PINE),
           "--timeout", str(timeout), "--tail", "3"]
    if players > 1:
        cmd += ["--script2", str(s2)]
    if snaps:
        cmd += ["--snap", ",".join(str(x) for x in snaps)]
    if patch_dir:
        cmd += ["--patch-dir", str(patch_dir)]
    cmd += list(extra)
    rec = Rec(name, out)
    h = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    names = ["vc"] + list((ranges or {}).keys())
    rl = [(VC, 4)] + [tuple(v) for v in (ranges or {}).values()]
    todo_full = sorted(full_at)

    def sampler():
        try:
            p = Pine(PINE)
        except OSError:
            return
        last = -1
        if auto_objs:
            # wait until play has started, then find the player objects (they point to unit slot 1)
            while h.poll() is None:
                try:
                    if p.r32(VC) >= start_vc and p.r32(SLOT1) != 0:
                        break
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(0.02)
            try:
                bases = find_players(p)
            except Exception:  # noqa: BLE001
                bases = []
            rec.players = bases
            for i, b in enumerate(bases[:2]):
                names.append("obj1" if i == 0 else "twin")
                rl.append((b, 0xB80))
        while h.poll() is None:
            try:
                vals = p.read_many(rl)
            except Exception:  # noqa: BLE001
                time.sleep(0.05)
                continue
            vc = struct.unpack("<I", vals[0])[0]
            if vc == last or vc < start_vc:
                time.sleep(0.001)
                continue
            last = vc
            d = dict(zip(names, vals))
            d["vc"] = vc
            if follow:
                # objects reached through a pointer inside an already recorded block (their address changes per room)
                want = []
                for fname, (blk, off) in follow.items():
                    ptr = struct.unpack_from("<I", d[blk], off)[0]
                    if 0x01000000 <= ptr < 0x01FFF000:
                        want.append((fname, ptr))
                try:
                    got = p.read_many([(ptr, 0xB80) for _, ptr in want]) if want else []
                except Exception:  # noqa: BLE001
                    got = []
                for fname in follow:
                    d[fname] = bytes(0xB80)
                    d[fname + "@"] = 0
                for (fname, ptr), data in zip(want, got):
                    d[fname] = data
                    d[fname + "@"] = ptr
            rec.samples.append(d)
            if todo_full and vc >= todo_full[0]:
                tgt = todo_full.pop(0)
                try:
                    data = b"".join(p.read_many([(a, 0x40000)])[0] for a in range(0, 0x02000000, 0x40000))
                    (out / f"ram_vc{tgt}.bin").write_bytes(data)
                except Exception:  # noqa: BLE001
                    pass

    t = threading.Thread(target=sampler, daemon=True)
    t.start()
    rec.harness = h.communicate()[0]
    t.join(timeout=5)
    (out / "harness.txt").write_text(rec.harness)
    with open(out / "samples.bin", "wb") as f:
        fnames = list(follow or {})
        meta = {"names": names + fnames + [x + "@" for x in fnames],
                "lens": [n for _, n in rl] + [0xB80] * len(fnames) + [4] * len(fnames),
                "addrs": [a for a, _ in rl], "count": len(rec.samples)}
        f.write(json.dumps(meta).encode() + b"\n")
        for s in rec.samples:
            for nme, (_, ln) in zip(names, rl):
                v = s[nme]
                f.write(struct.pack("<I", v) if nme == "vc" else v)
            for nme in fnames:
                f.write(s.get(nme, bytes(0xB80)))
            for nme in fnames:
                f.write(struct.pack("<I", s.get(nme + "@", 0)))
    return rec


def load(name):
    out = ROOT / "local" / "tests" / name
    rec = Rec(name, out)
    with open(out / "samples.bin", "rb") as f:
        meta = json.loads(f.readline())
        for _ in range(meta["count"]):
            d = {}
            for nme, ln in zip(meta["names"], meta["lens"]):
                b = f.read(ln)
                d[nme] = struct.unpack("<I", b)[0] if (nme == "vc" or nme.endswith("@")) else b
            rec.samples.append(d)
    rec.meta = meta
    hp = out / "harness.txt"
    rec.harness = hp.read_text() if hp.exists() else ""
    return rec


def u32(b, off=0):
    return struct.unpack_from("<I", b, off)[0]


def f32(b, off=0):
    return struct.unpack_from("<f", b, off)[0]


def buttons(raw):
    """raw pad word (pressed = 0) -> names of held buttons"""
    v = (~struct.unpack_from("<H", raw, 0)[0]) & 0xFFFF
    names = {0x0001: "SELECT", 0x0008: "START", 0x0010: "UP", 0x0020: "RIGHT", 0x0040: "DOWN", 0x0080: "LEFT",
             0x0100: "L2", 0x0200: "R2", 0x0400: "L1", 0x0800: "R1", 0x1000: "TRI", 0x2000: "O", 0x4000: "X",
             0x8000: "SQ", 0x0002: "L3", 0x0004: "R3"}
    return "+".join(n for bit, n in sorted(names.items()) if v & bit)
