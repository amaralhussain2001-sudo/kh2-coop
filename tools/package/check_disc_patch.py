"""Check a .kh2patch file the way the kit's disc maker uses it: apply it to the original disc image (read only)
into a temporary file, compare the result's SHA-1 with the one in the patch, delete the temporary file.
  python -I tools/package/check_disc_patch.py <original.iso> <patch.kh2patch> <tempFile>
"""
import hashlib
import shutil
import struct
import sys

src, patch, tmp = sys.argv[1:4]
with open(patch, "rb") as f:
    assert f.read(8) == b"KH2SECT1"
    sector = struct.unpack("<I", f.read(4))[0]
    osize, = struct.unpack("<Q", f.read(8)); osha = f.read(20)
    rsize, = struct.unpack("<Q", f.read(8)); rsha = f.read(20)
    runs, = struct.unpack("<I", f.read(4))
    shutil.copyfile(src, tmp)
    with open(tmp, "r+b") as o:
        for _ in range(runs):
            first, count = struct.unpack("<II", f.read(8))
            o.seek(first * sector)
            o.write(f.read(count * sector))
        o.truncate(rsize)
h = hashlib.sha1()
with open(tmp, "rb") as o:
    while True:
        b = o.read(1 << 24)
        if not b:
            break
        h.update(b)
import os
os.remove(tmp)
print("result sha1", h.hexdigest(), "expected", rsha.hex(), "OK" if h.digest() == rsha else "MISMATCH")
