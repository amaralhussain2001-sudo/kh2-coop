"""Lane R: survey of every trigger volume (event activator) in the room data, to choose the "other hero is close
enough" distance for the exit rule from data.

  python -I tools/lane-r/survey.py <ardDir> <outTxt> <outCsv>

Kind = first byte of the spawn point (what the engine's area event does): 1 = jump to another room, 2 = spawn
objects, 3 = start an event, others see docs/lanes/R-exits.md. Volume option (kind 1 only): 0 = the jump volume,
1 / 2 = the approach volume (shows the destination's name or the "cannot go" message). Scales are HALF sizes.
"""
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "lane-e"))
from ard import bar_entries, spawn_points  # noqa: E402


def main():
    ard_dir, out_txt, out_csv = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
    rows = []
    bad = 0
    for f in sorted(ard_dir.glob("*.ard")):
        data = f.read_bytes()
        for typ, name, off, size in bar_entries(data):
            if typ != 12 or size == 0:
                continue
            try:
                sps = spawn_points(data[off:off + size])
            except Exception:  # noqa: BLE001
                bad += 1
                continue
            for i, sp in enumerate(sps):
                for a in sp["acts"]:
                    sx, sy, sz = a["scale"]
                    rows.append(dict(room=f.stem, group=name, sp=i, kind=sp["type"], doortype=sp["world"],
                                     place=sp["place"], door=sp["door"], shape=a["shape"], option=a["option"],
                                     x=a["pos"][0], y=a["pos"][1], z=a["pos"][2], sx=sx, sy=sy, sz=sz,
                                     n_ent=len(sp["ents"])))
    out = []
    out.append("volumes read: %d in %d rooms; spawn entries that could not be decoded: %d" % (
        len(rows), len({r["room"] for r in rows}), bad))
    kinds = {}
    for r in rows:
        kinds.setdefault(r["kind"], []).append(r)
    out.append("")
    out.append("volumes per kind (kind: volumes / spawn points / rooms):")
    for k in sorted(kinds):
        rs = kinds[k]
        out.append("  kind %2d: %5d / %5d / %3d" % (k, len(rs), len({(r["room"], r["group"], r["sp"]) for r in rs}),
                                                  len({r["room"] for r in rs})))

    def dist(title, rs, key):
        vals = sorted(key(r) for r in rs)
        if not vals:
            out.append("  %s: none" % title)
            return
        q = lambda p: vals[min(len(vals) - 1, int(p * len(vals)))]  # noqa: E731
        out.append("  %s: n=%d min %.0f  5%% %.0f  25%% %.0f  median %.0f  75%% %.0f  95%% %.0f  max %.0f" % (
            title, len(vals), vals[0], q(0.05), q(0.25), statistics.median(vals), q(0.75), q(0.95), vals[-1]))

    k1 = kinds.get(1, [])
    out.append("")
    out.append("KIND 1 (room exits)")
    for opt in (0, 1, 2):
        rs = [r for r in k1 if r["option"] == opt]
        out.append(" option %d: %d volumes; shapes %s; door types %s" % (
            opt, len(rs), sorted({r["shape"] for r in rs}), sorted({r["doortype"] for r in rs})))
        dist("smaller horizontal FULL size", rs, lambda r: 2 * min(abs(r["sx"]), abs(r["sz"])))
        dist("larger horizontal FULL size", rs, lambda r: 2 * max(abs(r["sx"]), abs(r["sz"])))
        dist("FULL height", rs, lambda r: 2 * abs(r["sy"]))
    jump = [r for r in k1 if r["option"] == 0]
    for lim in (100, 150, 200, 300, 400, 600):
        n = sum(1 for r in jump if 2 * min(abs(r["sx"]), abs(r["sz"])) <= lim)
        out.append("  jump volumes whose smaller horizontal size is <= %d: %d of %d" % (lim, n, len(jump)))
    for lim in (100, 150, 200, 300, 400, 600):
        n = sum(1 for r in jump if 2 * max(abs(r["sx"]), abs(r["sz"])) <= lim)
        out.append("  jump volumes whose LARGER horizontal size is <= %d: %d of %d" % (lim, n, len(jump)))
    by_type = {}
    for r in jump:
        by_type[r["doortype"]] = by_type.get(r["doortype"], 0) + 1
    out.append("  jump volumes per door type (0 = standing inside is enough, 1 / 2 = must walk into it): %s" % by_type)
    k3 = kinds.get(3, [])
    out.append("")
    out.append("KIND 3 (event triggers): %d volumes; shapes %s; options %s" % (
        len(k3), sorted({r["shape"] for r in k3}), sorted({r["option"] for r in k3})))
    dist("smaller horizontal FULL size", k3, lambda r: 2 * min(abs(r["sx"]), abs(r["sz"])))
    dist("larger horizontal FULL size", k3, lambda r: 2 * max(abs(r["sx"]), abs(r["sz"])))
    for k in sorted(kinds):
        if k in (1, 3):
            continue
        out.append("")
        out.append("KIND %d: %d volumes; shapes %s; options %s; spawn points with entities: %d" % (
            k, len(kinds[k]), sorted({r["shape"] for r in kinds[k]}), sorted({r["option"] for r in kinds[k]}),
            len({(r["room"], r["group"], r["sp"]) for r in kinds[k] if r["n_ent"]})))
        dist("smaller horizontal FULL size", kinds[k], lambda r: 2 * min(abs(r["sx"]), abs(r["sz"])))
    out.append("")
    out.append("the 15 narrowest jump volumes (room group: full size x * y * z, door type, shape):")
    for r in sorted(jump, key=lambda r: min(abs(r["sx"]), abs(r["sz"])))[:15]:
        out.append("  %s %s[%d]: %.0f * %.0f * %.0f  type %d shape %d  -> place %d door %d" % (
            r["room"], r["group"], r["sp"], 2 * abs(r["sx"]), 2 * abs(r["sy"]), 2 * abs(r["sz"]), r["doortype"],
            r["shape"], r["place"], r["door"]))
    out_txt.write_text("\n".join(out) + "\n", encoding="utf-8")
    cols = ["room", "group", "sp", "kind", "doortype", "place", "door", "shape", "option", "x", "y", "z", "sx", "sy",
            "sz", "n_ent"]
    with open(out_csv, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(("%.1f" % r[c]) if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
