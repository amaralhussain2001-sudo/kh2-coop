"""Lane S1: dense, read-only timeline of the two heroes while a boss runs scripted Reaction Command moves.

  python -I tools/lane-s1/s1rc.py <test-out-dir> <pinePort> <startFrame> <endFrame> [--redirect] [--timeout 600]

Waits for the session screenshot of <startFrame>, then samples as fast as PINE answers until the screenshot of
<endFrame> exists (both frames must be in the run's --snap list). Every sample is ONE PINE message, so its values
belong together. Written to <dir>/rc.csv (one line per sample, time = Windows tick count in ms, the clock the
session log uses, so tools/lane-s1/s1rcsum.py can turn it into frame numbers):
  the engine's "player" pointers (0x0034E948, 0x00352400), the camera target (0x00348754), lane E's twin pointer,
  the hero attached to each control object (S = player 1, S2 = player 2), each control object's flags and its
  Reaction Command bytes (lane G: +0xA1E command number, +0xA21 state, 0 = usable, 5 = none),
  both heroes' position, action number and HP, the HP of the next three unit slots (boss and helpers).
When a hero's action number changes, the two hero objects (0xB80 bytes each) and the first 0x1000 bytes of the
boss object are saved to <dir>/rcdump/ (at most 80 sets) for looking up pointers later.

--redirect  ONE-COPY TESTS ONLY (it writes): after every sample write the twin's address into 0x00352400 and
            0x0034E948 (lane M's test trick: the engine then takes the twin for its player). Never on a linked pair.
"""
import ctypes
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

S, S2 = 0x01C5F530, 0x000F1000
SLOT_TWIN, SLOT_HERO, STEP = 0x01C6C750, 0x01C6C4E8, 0x268
G_PLAYER, G_LAST, G_CAM, G_TWIN = 0x0034E948, 0x00352400, 0x00348754, 0x000F05CC

ctypes.windll.kernel32.GetTickCount64.restype = ctypes.c_uint64


def tick():
    return ctypes.windll.kernel32.GetTickCount64()


def multi(p, reads):
    """reads: list of (addr, n) with n = 4 or a multiple of 8 (addr 8-aligned for the latter). One message."""
    body = bytearray()
    for a, n in reads:
        if n == 4:
            body += b"\x02" + struct.pack("<I", a)
        else:
            for i in range(n // 8):
                body += b"\x03" + struct.pack("<I", a + 8 * i)
    rep = p._call(bytes(body))
    out, pos = [], 0
    for a, n in reads:
        out.append(rep[pos:pos + n])
        pos += n
    return out


def ok(a):
    return 0x00100000 <= a < 0x02000000 and a % 4 == 0


def main():
    outdir = pathlib.Path(sys.argv[1])
    port = int(sys.argv[2])
    f0, f1 = int(sys.argv[3]), int(sys.argv[4])
    redirect = "--redirect" in sys.argv
    timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600.0
    start, stop = outdir / ("p1_f%06d.png" % f0), outdir / ("p1_f%06d.png" % f1)
    t0 = time.time()
    while not start.exists():
        if time.time() - t0 > timeout:
            print("timeout waiting for", start.name)
            return
        time.sleep(0.01)
    p = Pine(port, wait=20)
    dumpdir = outdir / "rcdump"
    dumpdir.mkdir(exist_ok=True)
    csv = open(outdir / "rc.csv", "w", encoding="utf-8")
    csv.write("tick,player,last,cam,twinptr,Hobj,Tobj,Sflags,S2flags,Src,S2rc,slot3hp,slot4hp,slot5hp,"
              "Hx,Hy,Hz,Hact,Hhp,Tx,Ty,Tz,Tact,Thp\n")
    hobj = tobj = 0
    last_acts = (None, None)
    n = dumps = writes = 0
    while not stop.exists() and time.time() - t0 < timeout:
        reads = [(G_PLAYER, 4), (G_LAST, 4), (G_CAM, 4), (G_TWIN, 4), (S + 0x9E0, 4), (S2 + 0x9E0, 4),
                 (S + 0x20, 4), (S2 + 0x20, 4), (S + 0xA18, 16), (S2 + 0xA18, 16),
                 (SLOT_HERO - STEP, 4), (SLOT_HERO - 2 * STEP, 4), (SLOT_HERO - 3 * STEP, 4),
                 (SLOT_HERO, 4), (SLOT_TWIN, 4)]
        for o in (hobj, tobj):
            if ok(o):
                reads += [(o + 0x70, 16), (o + 0x154, 4)]
        try:
            r = multi(p, reads)
        except Exception as e:  # noqa: BLE001
            print("read failed:", repr(e))
            break
        t = tick()
        u = [struct.unpack("<I", x)[0] for x in r[:8]]
        src, s2rc = r[8], r[9]
        s3, s4, s5, hhp, thp = [struct.unpack("<i", x)[0] for x in r[10:15]]
        k = 15
        vals = []
        for o in (hobj, tobj):
            if ok(o):
                x, y, z = struct.unpack_from("<3f", r[k], 0)
                act = struct.unpack("<I", r[k + 1])[0]
                k += 2
            else:
                x = y = z = 0.0
                act = 0xFFFFFFFF
            vals.append((x, y, z, act))
        csv.write("%d,%X,%X,%X,%X,%X,%X,%X,%X,%s,%s,%d,%d,%d,%.1f,%.1f,%.1f,%X,%d,%.1f,%.1f,%.1f,%X,%d\n" % (
            t, u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7], src.hex(), s2rc.hex(), s3, s4, s5,
            vals[0][0], vals[0][1], vals[0][2], vals[0][3], hhp, vals[1][0], vals[1][1], vals[1][2], vals[1][3], thp))
        acts = (vals[0][3], vals[1][3])
        if acts != last_acts and ok(hobj) and ok(tobj) and dumps < 80:
            try:
                boss = p.r32(SLOT_HERO - STEP + 0x25C)
                blob = p.read(hobj, 0xB80) + p.read(tobj, 0xB80) + (p.read(boss & ~7, 0x1000) if ok(boss) else b"")
                (dumpdir / ("%d_H%X_T%X_B%X_a%X_%X.bin" % (t, hobj, tobj, boss, acts[0], acts[1]))).write_bytes(blob)
                dumps += 1
            except Exception as e:  # noqa: BLE001
                print("dump failed:", repr(e))
        last_acts = acts
        hobj, tobj = u[4], u[5]
        if redirect and ok(u[3]):
            p.w32(G_LAST, u[3])
            p.w32(G_PLAYER, u[3])
            writes += 1
        n += 1
        if n % 50 == 0:
            csv.flush()
        time.sleep(0.002)
    csv.close()
    print("samples %d, dumps %d, redirect writes %d" % (n, dumps, writes))


if __name__ == "__main__":
    main()
