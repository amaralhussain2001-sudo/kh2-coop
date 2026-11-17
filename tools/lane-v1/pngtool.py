"""Lane V1: compare screenshots without extra libraries (plain PNG reader / writer).

  python -I tools/lane-v1/pngtool.py cmp <a.png> <b.png> [--diff out.png] [--tol N]
      per-pixel comparison of two pictures of the same size: how many pixels differ (by more than N, default 0),
      largest and mean difference, the box that holds all differences; --diff writes a picture of the differences
      (white = equal, the darker the bigger the difference).
  python -I tools/lane-v1/pngtool.py half <in.png> <left|right> <out.png>
      one half of a side-by-side picture stretched back to full width (each column doubled).
  python -I tools/lane-v1/pngtool.py fit <full.png> <halfStretched.png>
      best horizontal / vertical shift (in screenshot pixels) that lines the second picture up with the first,
      and the mean difference at shift 0 and at the best shift (centre region, HUD corners left out).
  python -I tools/lane-v1/pngtool.py pair <a.png> <b.png> <out.png>
      a and b side by side, half size, for the document.
"""
import struct
import sys
import zlib


def load(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG: " + path
    pos, idat, w = 8, [], 0
    while pos < len(data):
        ln, kind = struct.unpack_from(">I4s", data, pos)
        body = data[pos + 8:pos + 8 + ln]
        if kind == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and ctype in (2, 6) and inter == 0, "only 8-bit RGB / RGBA, not interlaced"
            bpp = 3 if ctype == 2 else 4
        elif kind == b"IDAT":
            idat.append(body)
        pos += 12 + ln
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        prev = line
        if bpp == 4:
            rgb = bytearray(w * 3)
            rgb[0::3], rgb[1::3], rgb[2::3] = line[0::4], line[1::4], line[2::4]
            rows.append(rgb)
        else:
            rows.append(line)
    return w, h, rows


def save(path, w, h, rows):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
                           chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def cmp(a, b, tol=0, diff=None):
    wa, ha, ra = load(a)
    wb, hb, rb = load(b)
    if (wa, ha) != (wb, hb):
        print("sizes differ: %dx%d and %dx%d" % (wa, ha, wb, hb))
        return
    n = big = total = 0
    x0, y0, x1, y1 = wa, ha, -1, -1
    out = []
    for y in range(ha):
        la, lb = ra[y], rb[y]
        if la == lb:
            if diff:
                out.append(bytearray(b"\xff" * (wa * 3)))
            continue
        line = bytearray(b"\xff" * (wa * 3))
        for x in range(wa):
            i = 3 * x
            d = max(abs(la[i] - lb[i]), abs(la[i + 1] - lb[i + 1]), abs(la[i + 2] - lb[i + 2]))
            if d > tol:
                n += 1
                total += d
                big = max(big, d)
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
                v = max(0, 200 - 4 * d)
                line[i] = line[i + 1] = line[i + 2] = v
        out.append(line)
    px = wa * ha
    if n == 0:
        print("IDENTICAL: %d x %d, every pixel equal%s" % (wa, ha, "" if tol == 0 else " within %d" % tol))
    else:
        print("%d of %d pixels differ (%.3f %%), largest difference %d of 255, mean of the differing ones %.1f, box x %d..%d y %d..%d" % (
            n, px, 100.0 * n / px, big, total / n, x0, x1, y0, y1))
    if diff:
        save(diff, wa, ha, out)


def half(src, side, dst):
    w, h, rows = load(src)
    hw = w // 2
    off = 0 if side == "left" else hw
    out = []
    for r in rows:
        line = bytearray(w * 3)
        for x in range(hw):
            px = r[3 * (off + x):3 * (off + x) + 3]
            line[6 * x:6 * x + 3] = px
            line[6 * x + 3:6 * x + 6] = px
        out.append(line)
    save(dst, w, h, out)
    print("%s half of %s -> %s (%d x %d)" % (side, src, dst, w, h))


def fit(a, b):
    wa, ha, ra = load(a)
    wb, hb, rb = load(b)
    assert (wa, ha) == (wb, hb)
    xs = range(int(wa * 0.30), int(wa * 0.80), 7)
    ys = range(int(ha * 0.08), int(ha * 0.58), 7)

    def score(dx, dy):
        t = c = 0
        for y in ys:
            la, lb = ra[y], rb[y + dy]
            for x in xs:
                i, j = 3 * x, 3 * (x + dx)
                t += abs(la[i] - lb[j]) + abs(la[i + 1] - lb[j + 1]) + abs(la[i + 2] - lb[j + 2])
                c += 3
        return t / c
    best = min(((score(dx, dy), dx, dy) for dx in range(-12, 13) for dy in range(-8, 9)))
    print("mean difference at shift 0: %.2f of 255; best shift dx %d dy %d: %.2f" % (score(0, 0), best[1], best[2], best[0]))


def pair(a, b, dst):
    wa, ha, ra = load(a)
    wb, hb, rb = load(b)
    assert (wa, ha) == (wb, hb)
    hw, hh = wa // 2, ha // 2
    out = []
    for y in range(hh):
        line = bytearray((2 * hw + 4) * 3)
        for k, rows in enumerate((ra, rb)):
            r0, r1 = rows[2 * y], rows[2 * y + 1]
            base = k * (hw + 4) * 3
            for x in range(hw):
                i = 6 * x
                for c in range(3):
                    line[base + 3 * x + c] = (r0[i + c] + r0[i + 3 + c] + r1[i + c] + r1[i + 3 + c]) >> 2
        out.append(line)
    save(dst, 2 * hw + 4, hh, out)
    print("pair -> %s" % dst)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "cmp":
        tol = int(sys.argv[sys.argv.index("--tol") + 1]) if "--tol" in sys.argv else 0
        d = sys.argv[sys.argv.index("--diff") + 1] if "--diff" in sys.argv else None
        cmp(sys.argv[2], sys.argv[3], tol, d)
    elif cmd == "half":
        half(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "fit":
        fit(sys.argv[2], sys.argv[3])
    elif cmd == "pair":
        pair(sys.argv[2], sys.argv[3], sys.argv[4])
