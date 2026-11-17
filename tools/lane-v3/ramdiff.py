"""Exact comparison of the main memory of two linked copies at the same session frame.

Needs the DumpFrames session key of the lane V3 emulator build (files p1_ram_f<frame>.bin / p2_ram_f<frame>.bin).

  python -I tools/lane-v3/ramdiff.py <test-out-dir> <frame> [<frame> ...] [--keep]
Prints the differing ranges (gaps up to 256 bytes joined) and deletes the dumps unless --keep is given.
"""
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
keep = "--keep" in sys.argv
for arg in sys.argv[2:]:
    if arg.startswith("--"):
        continue
    f = int(arg)
    pa, pb = d / f"p1_ram_f{f:06d}.bin", d / f"p2_ram_f{f:06d}.bin"
    if not pa.exists() or not pb.exists():
        print(f"frame {f}: dump missing")
        continue
    a, b = pa.read_bytes(), pb.read_bytes()
    n = len(a)
    x = (int.from_bytes(a, "little") ^ int.from_bytes(b, "little")).to_bytes(n, "little")
    ranges, words = [], 0
    for i in range(0, n, 4):
        if x[i:i + 4] != b"\0\0\0\0":
            words += 1
            if ranges and i - ranges[-1][1] <= 256:
                ranges[-1][1] = i + 4
                ranges[-1][2] += 1
            else:
                ranges.append([i, i + 4, 1])
    lines = [f"frame {f}: {words} words differ in {len(ranges)} range(s)"]
    for r in sorted(ranges, key=lambda r: -r[2])[:25]:
        lines.append(f"  0x{r[0]:08X}-0x{r[1]:08X}  {r[2]} words differ of {(r[1] - r[0]) // 4}  ({r[1] - r[0]} bytes)")
    (d / f"ramdiff_f{f:06d}.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if not keep:
        pa.unlink()
        pb.unlink()
