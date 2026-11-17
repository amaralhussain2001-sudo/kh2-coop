"""Does picture B show the same framing as picture A? (zoom, aspect, shift), and how sharp is each?

Both pictures are given as .raw files of the SAME size (made by png2raw.ps1). Method: edge profiles.
  - horizontal: for every column, the sum of |difference between neighbouring pixels along the row| over the rows
    of the test band -> one number per column. Picture B's profile is matched to A's with a scale and a shift.
  - vertical: the same with rows.
The best scale and shift (highest correlation) are reported per axis. scale 1.000 and shift 0 = same framing;
scale_x / scale_y = 1.000 = same aspect (a circle in A is a circle in B).
Only a band of the picture is used (default: columns 4-96 %, rows 6-58 %) to stay clear of the HUD.
Sharpness: mean edge strength per pixel in the same band (higher = sharper), for A and B.

  python -I tools/lane-v3/register.py <A.raw> <B.raw> [--band x0 x1 y0 y1]
"""
import struct
import sys


def load(path):
    b = open(path, "rb").read()
    w, h = struct.unpack("<ii", b[:8])
    px = b[8:]
    gray = [0.0] * (w * h)
    for i in range(w * h):
        o = i * 4
        gray[i] = 0.114 * px[o] + 0.587 * px[o + 1] + 0.299 * px[o + 2]
    return w, h, gray


def profiles(w, h, g, band):
    x0, x1, y0, y1 = int(w * band[0]), int(w * band[1]), int(h * band[2]), int(h * band[3])
    col = [0.0] * w
    row = [0.0] * h
    for y in range(y0, y1):
        base = y * w
        for x in range(1, w - 1):
            d = abs(g[base + x + 1] - g[base + x - 1])
            col[x] += d
    for y in range(1, h - 1):
        s = 0.0
        base = y * w
        for x in range(x0, x1):
            s += abs(g[base + w + x] - g[base - w + x])
        row[y] = s
    sharp = sum(col[x0:x1]) / max(1, (x1 - x0) * (y1 - y0))
    return col, row, sharp, (x0, x1, y0, y1)


def sample(p, x):
    if x < 0 or x >= len(p) - 1:
        return None
    i = int(x)
    f = x - i
    return p[i] * (1 - f) + p[i + 1] * f


def best(pa, pb, lo, hi):
    """Find scale s and shift t so that pb(c + (x - c) * s + t) matches pa(x) for x in lo..hi (c = centre)."""
    n = len(pa)
    c = n / 2.0
    xs = list(range(lo, hi))
    a = [pa[x] for x in xs]
    ma = sum(a) / len(a)
    va = sum((v - ma) ** 2 for v in a) or 1e-9
    top = (-2.0, 1.0, 0.0)
    for si in range(-100, 101):
        s = 1.0 + si * 0.002
        for ti in range(-60, 61):
            t = ti * 0.5
            b = []
            ok = True
            for x in xs:
                v = sample(pb, c + (x - c) * s + t)
                if v is None:
                    ok = False
                    break
                b.append(v)
            if not ok:
                continue
            mb = sum(b) / len(b)
            vb = sum((v - mb) ** 2 for v in b) or 1e-9
            cc = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a))) / (va * vb) ** 0.5
            if cc > top[0]:
                top = (cc, s, t)
    return top


def main():
    band = [0.04, 0.96, 0.06, 0.58]
    if "--band" in sys.argv:
        i = sys.argv.index("--band")
        band = [float(v) for v in sys.argv[i + 1:i + 5]]
    wa, ha, ga = load(sys.argv[1])
    wb, hb, gb = load(sys.argv[2])
    if (wa, ha) != (wb, hb):
        sys.exit(f"sizes differ: {wa}x{ha} vs {wb}x{hb}")
    ca, ra, sa, box = profiles(wa, ha, ga, band)
    cb, rb, sb, _ = profiles(wb, hb, gb, band)
    cx = best(ca, cb, box[0] + 8, box[1] - 8)
    cy = best(ra, rb, box[2] + 8, box[3] - 8)
    # plain picture difference in the band (0 = identical, 255 = opposite)
    diff = 0.0
    cnt = 0
    for y in range(box[2], box[3]):
        for x in range(box[0], box[1]):
            diff += abs(ga[y * wa + x] - gb[y * wa + x])
            cnt += 1
    print(f"size {wa}x{ha}, band columns {box[0]}-{box[1]}, rows {box[2]}-{box[3]}")
    print(f"horizontal: scale {cx[1]:.3f}, shift {cx[2]:+.1f} px ({100.0 * cx[2] / wa:+.2f} % of width), match {cx[0]:.3f}")
    print(f"vertical:   scale {cy[1]:.3f}, shift {cy[2]:+.1f} px ({100.0 * cy[2] / ha:+.2f} % of height), match {cy[0]:.3f}")
    print(f"aspect (horizontal scale / vertical scale): {cx[1] / cy[1]:.3f}")
    print(f"mean brightness difference in the band: {diff / cnt:.2f} of 255")
    print(f"sharpness (mean horizontal edge strength): A {sa:.2f}, B {sb:.2f}, B/A {sb / sa:.2f}")


if __name__ == "__main__":
    main()
