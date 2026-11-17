"""Give bosses more HP: write a copy of the game's battle data file (00battle.bin) in which the health values of
the boss entries of the enemy table are multiplied. Lane B75.

  python -I tools/lane-b75/scale_boss_hp.py <original 00battle.bin> <out 00battle.bin> [--percent 75]
         [--gauge-patch] [--gauge-limit 3400] [--list tools/lane-b75/data/boss_entries.csv]
         [--levels tools/lane-b75/data/boss_levels.csv] [--report FILE]

THE ONE NUMBER is --percent (default 75 = "75 % more HP"). The list says which entries are bosses; a row may
carry its own percent (0 = leave this boss as in the original; any other number = use that for this entry).
Every non-zero health value of a chosen entry is multiplied (main HP and part HP): new = round(old * (100 + p) / 100).

THE HP GAUGE LIMIT (VERIFIED, docs/lanes/B75-boss-hp.md): the game's enemy HP gauge freezes the game when a
target has more than 3400 HP. Real HP = table value x the level's multiplier, and the strongest bosses of the
original already sit at exactly 3400. So:
  without --gauge-patch (the safe default): a value is raised only as far as its real HP stays within the limit
      at the highest level that entry is ever fought at (levels file); such entries are marked CAPPED in the report.
  with --gauge-patch: no cap. Use this ONLY when the game patch contains the lane's HP gauge lines
      (tools/lane-b75/data/gauge_patch_lines.txt), which let the gauge show any HP in proportion.

Only those 16-bit values change. The file keeps its size and every other byte, so nothing moves in memory, and
the same inputs always give the same output (needed so two PCs get byte-identical discs).
"""
import argparse
import csv
import hashlib
import os
import pathlib
import struct
import sys

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
import bar  # noqa: E402
from enmp_lib import parse, ENTRY  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--percent", type=int, default=75)
    ap.add_argument("--list", default=str(HERE / "data" / "boss_entries.csv"))
    ap.add_argument("--levels", default=str(HERE / "data" / "boss_levels.csv"))
    ap.add_argument("--gauge-patch", action="store_true",
                    help="the game patch contains the HP gauge lines: do not cap at the gauge limit")
    ap.add_argument("--gauge-limit", type=int, default=3400)
    ap.add_argument("--report", default="")
    a = ap.parse_args()
    if os.path.abspath(a.src) == os.path.abspath(a.dst):
        sys.exit("source and destination must be different files")
    if not -50 <= a.percent <= 400:
        sys.exit("percent out of range")

    blob = bytearray(open(a.src, "rb").read())
    ent = bar.find(bytes(blob), "enmp", bar.TYPE_LIST)
    table = bytes(blob[ent["offset"]:ent["offset"] + ent["size"]])
    ver, entries = parse(table)
    by_id = {e["id"]: e for e in entries}
    # level table of the same file: 99 rows of 12 bytes, HP multiplier (percent) first (checked against lane C's dump)
    lv = bar.find(bytes(blob), "lvpm", bar.TYPE_LIST)
    mult = [struct.unpack_from("<H", blob, lv["offset"] + 12 * i)[0] for i in range(lv["size"] // 12)]
    assert len(mult) == 99 and mult[0] == 20 and mult[49] == 100, "unexpected level table"

    plan = {}
    for row in csv.DictReader(open(a.list, encoding="utf-8", newline="")):
        eid = int(row["entry_id"])
        p = row["percent"].strip()
        pct = a.percent if p == "" else int(p)
        if eid not in by_id:
            sys.exit(f"entry {eid} of the list is not in the table")
        plan[eid] = (pct, row["names"] or row["objects"].split("[")[0])
    levels = {}
    if not a.gauge_patch:
        for row in csv.DictReader(open(a.levels, encoding="utf-8", newline="")):
            levels[int(row["entry_id"])] = int(row["highest_level"])

    lines, changed, capped, biggest, biggest_real = [], 0, 0, 0, 0
    for eid in sorted(plan):
        pct, name = plan[eid]
        e = by_id[eid]
        if pct == 0:
            lines.append(f"{eid}\t0\tunchanged\t\t{name}")
            continue
        level = e["level"] or levels.get(eid, 0) or 99        # unknown level: assume the worst case
        m = mult[level - 1]
        cap = (100 * a.gauge_limit) // m                         # largest table value whose real HP fits the gauge
        new, was_capped = [], False
        for h in e["health"]:
            v = (h * (100 + pct) + 50) // 100 if h > 0 else h
            if not a.gauge_patch and h > 0 and v > max(h, cap):
                v = max(h, cap)
                was_capped = True
            if v > 32767:
                sys.exit(f"entry {eid}: {h} x {100 + pct} % = {v} does not fit the table's 16-bit value")
            new.append(v)
            biggest = max(biggest, v)
            if not a.gauge_patch:
                biggest_real = max(biggest_real, (m * v + 99) // 100)
        off = ent["offset"] + e["offset"] + 4
        for i, v in enumerate(new):
            blob[off + 2 * i:off + 2 * i + 2] = int(v).to_bytes(2, "little", signed=True)
        changed += new != list(e["health"])
        capped += was_capped
        old_s = " ".join(str(h) for h in e["health"] if h)
        new_s = " ".join(str(v) for v in new if v)
        got = ""
        if was_capped:
            top = max(e["health"])
            got = "CAPPED at level %d: +%d %% instead of +%d %%" % (level, round(100 * max(new) / top) - 100, pct)
        lines.append(f"{eid}\t{pct}\t{old_s} -> {new_s}\t{got}\t{name}")

    os.makedirs(os.path.dirname(os.path.abspath(a.dst)), exist_ok=True)
    open(a.dst, "wb").write(blob)
    # safety: only health values of listed entries may differ
    src = open(a.src, "rb").read()
    diff = [i for i in range(len(src)) if src[i] != blob[i]]
    lo, hi = ent["offset"] + 8, ent["offset"] + ent["size"]
    assert len(src) == len(blob) and all(lo <= i < hi and 4 <= (i - lo) % ENTRY < 68 for i in diff)
    sha = hashlib.sha1(bytes(blob)).hexdigest()
    mode = ("NO gauge cap (needs the HP gauge patch lines in the game patch)" if a.gauge_patch else
            f"gauge cap {a.gauge_limit} HP: {capped} entries capped, largest real HP {biggest_real}")
    head = (f"boss HP: +{a.percent} % (list {os.path.basename(a.list)}); {mode}; entries changed {changed}, "
            f"left unchanged {len(plan) - changed}; largest health value now {biggest}; bytes changed {len(diff)}; "
            f"sha1 {sha}")
    print(head)
    if a.report:
        open(a.report, "w", encoding="utf-8").write(head + "\nentry\tpercent\thealth\tgauge cap\tname\n" + "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
