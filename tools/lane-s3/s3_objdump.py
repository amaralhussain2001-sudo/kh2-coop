"""Lane S3: save the two Gummi ship objects (and the shared flight-controller object) at intervals, through PINE.

  python -I tools/lane-s3/s3_objdump.py <port> <seconds> <interval> <outDir>
Writes <outDir>/t<NNN>_ship1.bin, _ship2.bin (0x1440 bytes each), _rail.bin (0x200 bytes at 0x01F7DE60) and an index
file with the time, score and kill count of each sample. Read-only.

  python -I tools/lane-s3/s3_objdump.py diff <outDir>
Lists the fields of ship 1 whose value changed between samples (as int and float), with ship 2's value beside them.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])


def capture():
    from pine import Pine
    port, secs, step = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    out = pathlib.Path(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    p = Pine(port, wait=180)
    t0 = time.time()
    n = 0
    idx = []
    while time.time() - t0 < secs:
        try:
            if p.r32(0x01F18014) & 0xFFFF == 0x636A:
                s1, s2 = p.r32(0x000F5F80), p.r32(0x000F5F84)
                g = p.r32(0x01F7DE44)
                if s1 == 0:
                    s1 = g
                if 0x00100000 <= s1 < 0x02000000 and p.r32(s1 + 0x50C) == 2:
                    (out / ("t%03d_ship1.bin" % n)).write_bytes(p.read(s1, 0x1440))
                    if 0x00100000 <= s2 < 0x02000000:
                        (out / ("t%03d_ship2.bin" % n)).write_bytes(p.read(s2, 0x1440))
                    (out / ("t%03d_rail.bin" % n)).write_bytes(p.read(0x01F7DE60, 0x200))
                    idx.append("%03d %.1f score %d kills %d ship1 %08X ship2 %08X" % (n, time.time() - t0, p.r32(0x01F8039C),
                                                                                     p.r16(0x01F80856), s1, s2))
                    n += 1
        except Exception as e:  # noqa: BLE001
            idx.append("read failed %.1f %s" % (time.time() - t0, e))
            time.sleep(0.5)
        time.sleep(step)
    (out / "index.txt").write_text("\n".join(idx) + "\n")
    print("samples:", n)


def diff():
    d = pathlib.Path(sys.argv[2])
    files = sorted(d.glob("t*_ship1.bin"))
    s1 = [f.read_bytes() for f in files]
    s2 = []
    for f in files:
        g = d / f.name.replace("ship1", "ship2")
        s2.append(g.read_bytes() if g.exists() else None)
    n = len(s1)
    print("samples", n)
    for off in range(0, 0x1440, 4):
        vals = [struct.unpack_from("<I", b, off)[0] for b in s1]
        if len(set(vals)) < 2:
            continue
        fl = [struct.unpack_from("<f", b, off)[0] for b in s1]
        v2 = [struct.unpack_from("<I", b, off)[0] if b else None for b in s2]
        f2 = [struct.unpack_from("<f", b, off)[0] if b else None for b in s2]
        # keep fields that look like small counters or plain floats and do not change in every sample
        changes = sum(1 for i in range(1, n) if vals[i] != vals[i - 1])
        isf = all(abs(x) < 1e6 and (abs(x) > 1e-3 or x == 0) for x in fl)
        isi = all(v < 100000 for v in vals)
        if not (isf or isi):
            continue
        pick = [0, n // 4, n // 2, 3 * n // 4, n - 1]

        def show(i):
            if isi:
                return "%d/%s" % (vals[i], v2[i] if v2[i] is not None else "-")
            return "%.1f/%s" % (fl[i], ("%.1f" % f2[i]) if f2[i] is not None and abs(f2[i]) < 1e6 else "-")
        print("+%04X changes %2d  ship1/ship2: %s" % (off, changes, "  ".join(show(i) for i in pick)))


if __name__ == "__main__":
    if sys.argv[1] == "diff":
        diff()
    else:
        capture()
