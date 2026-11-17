"""Merged build 3 = merged-v2 + lane R (exit polish) + lane H (enemy targeting) + lane N (down and rescue)
+ one glue routine: no room exit or story trigger while a hero is down.

Word-level merge of the lanes' delivered patch files (each of them is "merged-v2 plus or replacing some words"):
  base   patches/merged-v2
  R      patches/lane-r-x3          (replaces lane E's exit words, adds its own)
  H      patches/lane-h-target-v1   (adds words only)
  N      patches/lane-n-down-v2     (adds words only)
  V2     patches/lane-v2-hud1       (adds words only: player 2's gauge on the one-view HUD and the 1P/2P markers)
For every address the tool checks that at most ONE lane differs from the base; otherwise it stops.

  python -I tools/merge/merge_v3.py [outDir] [--no-glue] [--report]

Writes <outDir>/SLPM-66675_F266B00B.pnach and <outDir>/listing.txt. Default outDir: patches/merged-v3.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
NAME = "SLPM-66675_F266B00B.pnach"
LINE = re.compile(r"^patch=(\d),EE,([0-9A-Fa-f]{8}),(\w+),([0-9A-Fa-f]{8})\s*(?://.*)?$")


def load(folder):
    """-> (ordered list of keys, dict key -> (raw line, value)); key = (place, kind, address)."""
    order, words = [], {}
    for raw in (ROOT / "patches" / folder / NAME).read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        key = (m.group(1), m.group(3).lower(), int(m.group(2), 16))
        if key in words:
            raise SystemExit(f"{folder}: address written twice: {m.group(2)}")
        order.append(key)
        words[key] = int(m.group(4), 16)
    return order, words


def main():
    skips = {sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--skip"}
    args = [a for a in sys.argv[1:] if not a.startswith("--") and a not in skips]
    out = ROOT / (args[0] if args else "patches/merged-v3")
    glue_on = "--no-glue" not in sys.argv
    base_o, base = load("merged-v2")
    lanes = {"R": load("lane-r-x3"), "H": load("lane-h-target-v1"), "N": load("lane-n-down-v2"),
             "V2": load("lane-v2-hud1")}
    for skip in [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--skip"]:
        lanes.pop(skip)   # test variants only, e.g. --skip N to let lane N's generator add a test build of N

    merged = dict(base)
    origin = {k: "merged-v2" for k in base}
    order = list(base_o)
    changed_by = {}
    for name, (lo, lw) in lanes.items():
        removed = [k for k in base if k not in lw]
        for k in removed:
            changed_by.setdefault(k, []).append((name, None))
        for k in lo:
            v = lw[k]
            if k in base and base[k] == v:
                continue
            changed_by.setdefault(k, []).append((name, v))
    clashes = {k: v for k, v in changed_by.items() if len({n for n, _ in v}) > 1}
    if clashes:
        for k, v in sorted(clashes.items(), key=lambda x: x[0][2]):
            print("CLASH at %08X:" % k[2], v)
        raise SystemExit("two lanes change the same address; resolve by hand")
    for k, v in changed_by.items():
        name, val = v[0]
        if val is None:
            merged.pop(k, None)
            origin.pop(k, None)
            if k in order:
                order.remove(k)
        else:
            if k not in merged:
                order.append(k)
            merged[k] = val
            origin[k] = "lane " + name

    glue_words = []
    if glue_on:
        # Lane R's hook at 0x0019A168 is "jal <R routine>" (it replaced the game's "jalr v0", the volume test of
        # exits and story triggers). The glue goes in front of it: if lane N says a hero is down
        # (0x000F2FC8 = player 1's hero, 0x000F2FCC = the twin), answer "nobody is inside" (v0 = 0) without
        # running the test; otherwise continue into lane R's routine with the same return address.
        import mips
        from asm import assemble
        hook = ("1", "word", 0x0019A168)
        if hook not in merged:
            raise SystemExit("lane R's hook word at 0x0019A168 not found")
        w = merged[hook]
        if (w >> 26) != 3:
            raise SystemExit("0x0019A168 is not a jal: %08X" % w)
        r_entry = (w & 0x03FFFFFF) << 2
        glue_at = 0x000F3400
        src = """
            lui   t8, 0x000F
            lw    t9, 0x2FC8(t8)
            lw    t8, 0x2FCC(t8)
            or    t9, t9, t8
            bne   t9, zero, down
            nop
            j     R_ENTRY
            nop
        down:
            jr    ra
            addu  v0, zero, zero
        """
        code, _labels = assemble(glue_at, src, {"R_ENTRY": r_entry})
        code = [w if isinstance(w, int) else w[1] for w in code]
        for i, word in enumerate(code):
            k = ("1", "word", glue_at + 4 * i)
            if k in merged:
                raise SystemExit("glue address already used: %08X" % k[2])
            merged[k] = word
            origin[k] = "glue (no exit while a hero is down)"
            order.append(k)
            glue_words.append(k)
        merged[hook] = (3 << 26) | (glue_at >> 2)
        origin[hook] = "glue (was lane R: jal %08X)" % r_entry

    out.mkdir(parents=True, exist_ok=True)
    head = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, MERGED BUILD 3: merged-v2 + exits (lane R) + enemy targeting (lane H)",
        "comment=+ down and rescue (lane N) + gauge and markers for player 2 (lane V2) + glue.",
        "comment=Every PC in an online game must have this same file.",
    ]
    body = ["patch=%s,EE,%08X,%s,%08X" % (k[0], k[2], k[1], merged[k]) for k in order]
    (out / NAME).write_text("\n".join(head + body) + "\n", encoding="utf-8")
    listing = ["%08X %08X  %s" % (k[2], merged[k], origin[k]) for k in sorted(order, key=lambda x: x[2])]
    (out / "listing.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")
    counts = {}
    for k in order:
        counts[origin[k].split(" (")[0]] = counts.get(origin[k].split(" (")[0], 0) + 1
    print("merged words:", len(order), counts)
    print("written:", out / NAME)


if __name__ == "__main__":
    main()
