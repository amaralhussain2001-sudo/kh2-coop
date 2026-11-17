"""Make the disc patch for the test package: only the sectors that differ between the original disc image and the
two-player disc image. Both inputs are opened read-only.

  python -I tools/lane-t/make_disc_patch.py <original.iso> <two-player.iso> <out.kh2patch>

Patch file layout (little endian):
  8 bytes  magic "KH2SECT1"
  u32      sector size (2048)
  u64      size of the original file      20 bytes  SHA-1 of the original file
  u64      size of the result file        20 bytes  SHA-1 of the result file
  u32      number of runs
  per run: u32 first sector, u32 number of sectors, then that many sectors of data
"""
import hashlib
import struct
import sys

SECTOR = 2048
CHUNK = SECTOR * 4096  # 8 MB


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 24)
            if not b:
                break
            h.update(b)
    return h.digest()


def main():
    src, dst, out = sys.argv[1], sys.argv[2], sys.argv[3]
    import os
    ssize, dsize = os.path.getsize(src), os.path.getsize(dst)
    if ssize % SECTOR or dsize % SECTOR:
        sys.exit("file sizes are not a whole number of sectors")
    runs = []  # (first sector, bytes)
    cur_start, cur = None, bytearray()
    with open(src, "rb") as fs, open(dst, "rb") as fd:
        sector = 0
        total = dsize // SECTOR
        while sector < total:
            b = fd.read(CHUNK)
            a = fs.read(len(b))
            n = len(b) // SECTOR
            if a == b:
                if cur_start is not None:
                    runs.append((cur_start, bytes(cur)))
                    cur_start, cur = None, bytearray()
                sector += n
                continue
            for i in range(n):
                sa = a[i * SECTOR:(i + 1) * SECTOR]
                sb = b[i * SECTOR:(i + 1) * SECTOR]
                if sa != sb:  # also true where the original is shorter
                    if cur_start is None:
                        cur_start = sector + i
                    cur += sb
                elif cur_start is not None:
                    runs.append((cur_start, bytes(cur)))
                    cur_start, cur = None, bytearray()
            sector += n
        if cur_start is not None:
            runs.append((cur_start, bytes(cur)))
    s1, d1 = sha1_of(src), sha1_of(dst)
    with open(out, "wb") as o:
        o.write(b"KH2SECT1")
        o.write(struct.pack("<I", SECTOR))
        o.write(struct.pack("<Q", ssize) + s1)
        o.write(struct.pack("<Q", dsize) + d1)
        o.write(struct.pack("<I", len(runs)))
        for start, data in runs:
            o.write(struct.pack("<II", start, len(data) // SECTOR))
            o.write(data)
    changed = sum(len(d) for _, d in runs) // SECTOR
    psha = sha1_of(out).hex()
    print(f"original  {ssize} bytes sha1 {s1.hex()}")
    print(f"result    {dsize} bytes sha1 {d1.hex()}")
    print(f"runs {len(runs)}, changed sectors {changed} ({changed * SECTOR} bytes)")
    print(f"patch     {os.path.getsize(out)} bytes sha1 {psha}")


if __name__ == "__main__":
    main()
