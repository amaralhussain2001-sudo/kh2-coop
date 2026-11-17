"""Lane V1: follow the two-view state of a running sandbox emulator, read-only (PINE).

  python -I tools/lane-v1/vprobe.py <port> <endFrame> <outFile> [--cave] [--full]

Polls as fast as PINE allows. Frame = the game's pad counter (0x0034D4BC) + 152 (lane G's finding).
Writes one line to <outFile> whenever the state tuple changes:
  frame | layout shown / pending | ours | request | game two-view flag | view index | camera hold | room |
  fade flags | step flag | camera 1 type,target | camera 2 target | engine player | twin
--full   also one line per polled frame with camera eyes and hero positions (bigger file: <outFile>.full.csv)
--cave   at the end, count non-zero bytes in 0x000F6000-0x000F6FFF (meant for runs WITHOUT the patch)
--dump f1,f2,...  at the first poll at or after each of these frames (and with player 2's camera NOT swapped in)
         write raw memory to <outFile>.dump.txt: camera 0x00348710, player 2's camera 0x000F6E00, the view table
         0x003A7F70 (two blocks of 0x90), and 0x100 bytes of the engine player object and of the twin from +0x40
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

port, end_f, out = int(sys.argv[1]), int(sys.argv[2]), pathlib.Path(sys.argv[3])
full = "--full" in sys.argv
cave = "--cave" in sys.argv
dump_at = []
if "--dump" in sys.argv:
    dump_at = sorted(int(x) for x in sys.argv[sys.argv.index("--dump") + 1].split(","))
dlines = []
p = Pine(port, wait=120)


def frame():
    return p.r32(0x0034D4BC) + 152


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def f3(b, o):
    return "%.0f %.0f %.0f" % struct.unpack_from("<3f", b, o)


lines, flines = [], []
last, last_f = None, -1
t0 = time.time()
max_cave = 0
while True:
    try:
        f = frame()
    except Exception:  # noqa: BLE001
        time.sleep(0.05)
        if time.time() - t0 > 900:
            break
        continue
    if f >= end_f:
        break
    if f == last_f:
        time.sleep(0.002)
        continue
    last_f = f
    try:
        v = p.read(0x000F6F00, 0x10)
        g = p.read(0x0033CC38, 0x10)
        cam1 = p.read(0x00348710, 0x50)
        cam2 = p.read(0x000F6E00, 0x50)
        fade = p.read(0x0034C768, 0x14)
        room = p.r32(0x0032BAE0) & 0xFFFF
        step = p.r32(0x00349E1C) & 0xFF
        eng = p.r32(0x0034E948)
        twin = p.r32(0x000F05CC)
    except Exception:  # noqa: BLE001
        continue
    state = (v[0], v[1], u32(v, 4), u32(v, 8), g[0xC], u32(g, 8), u32(g, 0), room,
             fade[8], fade[9], fade[10], u32(fade, 0xC) != 0, u32(fade, 0x10) != 0, step,
             u32(cam1, 0x40), u32(cam1, 0x44), u32(cam2, 0x44), eng, twin, u32(cam2, 0x40), cam2[0x3B], cam1[0x3B])
    if dump_at and f >= dump_at[0] and u32(v, 0xC) == 0:
        try:
            blocks = [p.read(0x00348710, 0xF0), p.read(0x000F6E00, 0xF0), p.read(0x003A7F70, 0x120)]
            for obj in (eng, twin):
                blocks.append(p.read(obj + 0x40, 0x100) if 0x00100000 <= obj < 0x02000000 else b"")
            if frame() == f and (p.r32(0x000F6F0C) == 0):
                dlines.append("%d %d %d %s" % (dump_at.pop(0), f, v[0], " ".join(b.hex() or "-" for b in blocks)))
        except Exception:  # noqa: BLE001
            pass
    if state != last:
        last = state
        lines.append("%6d | lay %d/%d | ours %d | req %d | dual %d | view %d | hold %d | room %04X | fade %d %d sw%d t%d c%d | step %d | cam1 type %d tgt %07X | cam2 tgt %07X | eng %07X | twin %07X | c2type %d lock2 %d lock1 %d" % (
            (f,) + tuple(int(x) for x in state)))
    if full:
        pos = []
        for obj in (eng, twin):
            if 0x00100000 <= obj < 0x02000000:
                try:
                    pos.append(f3(p.read(obj + 0x70, 12), 0))
                except Exception:  # noqa: BLE001
                    pos.append("?")
            else:
                pos.append("-")
        flines.append("%d,%d,%d,%s,%s,%s,%s,%s,%s" % (f, v[0], u32(v, 4), f3(cam1, 0), f3(cam1, 0x20), f3(cam2, 0), f3(cam2, 0x20), pos[0], pos[1]))
    if cave and f % 50 == 0:
        try:
            blk = p.read(0x000F6000, 0x1000)
            max_cave = max(max_cave, sum(1 for b in blk if b))
        except Exception:  # noqa: BLE001
            pass
if cave:
    lines.append("cave 0x000F6000-0x000F6FFF: most non-zero bytes seen in any sample = %d" % max_cave)
out.write_text("\n".join(lines) + "\n")
if dlines:
    pathlib.Path(str(out) + ".dump.txt").write_text("\n".join(dlines) + "\n")
if full:
    pathlib.Path(str(out) + ".full.csv").write_text("frame,layout,ours,cam1eye,cam1look,cam2eye,cam2look,hero,twin\n" + "\n".join(flines) + "\n")
print("%d state changes, last frame %d -> %s" % (len(lines), last_f, out))
