"""Lane K: print both camera blocks and both heroes' positions of a running sandbox emulator (read-only, PINE).

Waits for each frame's screenshot in <test-out-dir>, then reads. One output line group per frame.
  python -I tools/lane-k/camprobe.py <test-out-dir> <port> <frame,frame,...> [--raw]
Camera block: eye at +0x00 (x, y, z, w), second point at +0x10, look-at at +0x20, mode +0x40, target +0x44.
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

out_dir = pathlib.Path(sys.argv[1])
port = int(sys.argv[2])
frames = [int(x) for x in sys.argv[3].split(",") if x]
raw = "--raw" in sys.argv
CAM1, CAM2 = 0x00348710, 0x000F0F10
p = None
t0 = time.time()


def vec(b, o):
    return "(%8.1f %8.1f %8.1f)" % struct.unpack_from("<3f", b, o)


for f in frames:
    shot = out_dir / f"p1_f{f:06d}.png"
    while not shot.exists():
        if time.time() - t0 > 900:
            sys.exit("timeout waiting for " + shot.name)
        time.sleep(0.03)
    if p is None:
        p = Pine(port)
    hero = p.r32(0x0034E948)
    twin = p.r32(0x000F05CC)
    line = [f"frame {f}: view index {p.r32(0x0033CC40)} two-view flag {p.r8(0x0033CC44)} step flag {p.r32(0x00349E1C)}"]
    for name, obj in (("hero", hero), ("twin", twin)):
        if obj:
            line.append(f"  {name} 0x{obj:08X} pos {vec(p.read(obj + 0x70, 12), 0)}")
    for name, a in (("cam1", CAM1), ("cam2", CAM2)):
        b = p.read(a, 0xF0)
        mode, tgt = struct.unpack_from("<II", b, 0x40)
        line.append(f"  {name} eye {vec(b, 0)} at {vec(b, 0x20)} p10 {vec(b, 0x10)} mode {mode} target 0x{tgt:08X}"
                    f" a0 {struct.unpack_from('<f', b, 0xA0)[0]:.3f} a4 {struct.unpack_from('<f', b, 0xA4)[0]:.3f}"
                    f" 30/34 {struct.unpack_from('<f', b, 0x30)[0]:.3f} {struct.unpack_from('<f', b, 0x34)[0]:.3f}")
        if raw:
            for o in range(0, 0xF0, 16):
                line.append("      +%02X  " % o + " ".join("%08X" % x for x in struct.unpack_from("<4I", b, o))
                            + "   " + " ".join("%9.2f" % x for x in struct.unpack_from("<4f", b, o)))
    print(chr(10).join(line), flush=True)
