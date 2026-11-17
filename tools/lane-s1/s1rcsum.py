"""Lane S1: turn a test's rc.csv (made by s1rc.py) into a readable timeline.

  python -I tools/lane-s1/s1rcsum.py <test-name> [--all] [--from F] [--to F] [--start 4600]

Frame numbers are estimated from the time stamps of the session log's "stats: frame N" lines (straight line
between two of them, so they can be a few frames off). One line is printed whenever something discrete changes:
a hero's action number, a control object's Reaction Command bytes or flags, an HP value, one of the engine's
"player" / camera pointers; plus each hero's position at that moment. --all prints every sample.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def anchors(test):
    out = []
    f = ROOT / "local" / "tests" / test / "p1.log"
    for line in f.read_text(errors="replace").splitlines():
        m = re.match(r"(\d+) .*?(?:stats: frame|test end at frame|session closed at frame) (\d+)", line)
        if m:
            out.append((int(m.group(1)), int(m.group(2))))
    return sorted(set(out))


def to_frame(anc, t):
    if len(anc) < 2:
        return -1
    for i in range(len(anc) - 1):
        if t <= anc[i + 1][0] or i == len(anc) - 2:
            (t0, f0), (t1, f1) = anc[i], anc[i + 1]
            return int(round(f0 + (t - t0) * (f1 - f0) / max(1, t1 - t0)))
    return -1


def rc(hexs):
    b = bytes.fromhex(hexs)
    return "%02X/%d" % (b[6], b[9])      # +0xA1E command number, +0xA21 state


def main():
    test = sys.argv[1]
    every = "--all" in sys.argv
    lo = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
    hi = int(sys.argv[sys.argv.index("--to") + 1]) if "--to" in sys.argv else 10 ** 9
    anc = anchors(test)
    rows = (ROOT / "local" / "tests" / test / "rc.csv").read_text().splitlines()
    head = rows[0].split(",")
    # The session log's clock runs a few seconds ahead of the probe's clock. The probe's first sample is taken
    # right after the screenshot of its start frame appears, so that pair fixes the difference (a few frames off).
    start = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 4600
    first = int(rows[1].split(",")[0])
    off = 0
    for i in range(len(anc) - 1):
        (t0, f0), (t1, f1) = anc[i], anc[i + 1]
        if f0 <= start <= f1 and f1 > f0:
            off = int(t0 + (start - f0) * (t1 - t0) / (f1 - f0)) - first
    prev = None
    n = 0
    print("== %s: %d samples; columns: frame | engine player / camera = which hero | hero: act HP pos RC(cmd/state) "
          "| twin: act HP pos RC | other slots' HP" % (test, len(rows) - 1))
    for line in rows[1:]:
        d = dict(zip(head, line.split(",")))
        fr = to_frame(anc, int(d["tick"]) + off)
        if not lo <= fr <= hi:
            continue
        who = {d["Hobj"]: "hero", d["Tobj"]: "twin"}
        key = (d["player"], d["last"], d["cam"], d["Hact"], d["Tact"], rc(d["Src"]), rc(d["S2rc"]), d["Sflags"],
               d["S2flags"], d["slot3hp"], d["slot4hp"], d["slot5hp"], d["Hhp"], d["Thp"])
        if every or key != prev:
            print("f%5d | player %s last %s cam %s | H act %3s HP %2s (%6.0f %6.0f %6.0f) RC %s fl %s | "
                  "T act %3s HP %2s (%6.0f %6.0f %6.0f) RC %s fl %s | %s %s %s" % (
                      fr, who.get(d["player"], d["player"]), who.get(d["last"], d["last"]), who.get(d["cam"], d["cam"]),
                      d["Hact"], d["Hhp"], float(d["Hx"]), float(d["Hy"]), float(d["Hz"]), rc(d["Src"]), d["Sflags"],
                      d["Tact"], d["Thp"], float(d["Tx"]), float(d["Ty"]), float(d["Tz"]), rc(d["S2rc"]), d["S2flags"],
                      d["slot3hp"], d["slot4hp"], d["slot5hp"]))
            n += 1
        prev = key
    print("   %d lines; frame anchors: %s" % (n, " ".join("%d@%d" % (f, t % 1000000) for t, f in anc[:12])))


if __name__ == "__main__":
    main()
