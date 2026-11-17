"""Lane V1: camera numbers from vprobe dump files (vprobe.py --dump).

  python -I tools/lane-v1/vcam.py <vprobe.txt.dump.txt> <cam: 1|2> [<file> <cam> ...]
For each dump line of each file: the camera's eye and aim point, its distance to its hero, its height above the hero,
the eye-to-aim distance, the camera's own floats +0x48..+0x5C (zoom / angles) and the first projection numbers of the
view block that belongs to this camera. cam 1 = the game's camera with the engine's player and view block 0;
cam 2 = player 2's camera with the twin and view block 1.
"""
import struct
import sys


def f(b, o, n=1):
    return struct.unpack_from("<%df" % n, b, o)


args = sys.argv[1:]
for path, cam in zip(args[0::2], args[1::2]):
    print("== %s, camera %s" % (path, cam))
    for line in open(path):
        p = line.split()
        want, got, layout = int(p[0]), int(p[1]), int(p[2])
        blocks = [bytes.fromhex(x) if x != "-" else b"" for x in p[3:]]
        c = blocks[0] if cam == "1" else blocks[1]
        view = blocks[2][0:0x90] if cam == "1" else blocks[2][0x90:0x120]
        hero = blocks[3] if cam == "1" else blocks[4]
        eye, aim = f(c, 0, 3), f(c, 0x20, 3)
        out = "frame %d layout %d | eye %8.1f %8.1f %8.1f | aim %8.1f %8.1f %8.1f | eye-aim %.2f" % (
            (got, layout) + eye + aim + (sum((a - b) ** 2 for a, b in zip(eye, aim)) ** 0.5,))
        if hero:
            pos = f(hero, 0x30, 3)
            out += " | hero %8.1f %8.1f %8.1f | eye-hero %.2f | eye height over hero %.2f" % (
                pos + (sum((a - b) ** 2 for a, b in zip(eye, pos)) ** 0.5, -(eye[1] - pos[1])))
        out += " | cam +48: " + " ".join("%.3f" % x for x in f(c, 0x48, 6))
        out += " | view: " + " ".join("%.4f" % x for x in f(view, 0x40, 8))
        print(out)
