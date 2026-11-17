"""Lane E: read the "who is the player" state from a running sandbox emulator through PINE (read-only).

Waits for the session screenshot of each frame, then prints: the engine's player pointers, camera target, party
table, command controller owner, this lane's variables, and every player object found in memory with its position
and controller.

  python -I tools/lane-e/probe.py <test-out-dir> <pinePort> <frame,frame,...> [--timeout 600] [--cave]
--cave  also print whether 0x000F0000-0x000F0FFF holds anything besides the patch words (see cavecheck.py)
"""
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pine import Pine  # noqa: E402

PLAYER_VTABLES = {0x00352410: "player", 0x0034E958: "base"}
PADS = {0x0034D6C0: "pad1", 0x0034D720: "pad2", 0: "none"}


def find_players(p):
    """Player objects: heap blocks whose first word is the main player class table and whose +0xB44 is S."""
    ram = p.read(0x01000000, 0x01000000)
    res = []
    pos = 0
    key = struct.pack("<I", 0x00352410)
    while True:
        i = ram.find(key, pos)
        if i < 0:
            break
        pos = i + 4
        if i % 4 or i + 0xB80 > len(ram):
            continue
        if struct.unpack_from("<I", ram, i + 0xB44)[0] != 0x01C5F530:
            continue
        res.append((0x01000000 + i, ram[i:i + 0xB80]))
    return res


def snapshot(p):
    g = {
        "g_player": p.r32(0x0034E948), "g_saved": p.r32(0x0034E94C), "last": p.r32(0x00352400),
        "cam": p.r32(0x00348754), "party0": p.r32(0x00348638), "party1": p.r32(0x0034863C), "party2": p.r32(0x00348640),
        "S.player": p.r32(0x01C5FF10), "S.pad": p.r32(0x01C5FF14), "S.owner": p.r32(0x01C60024),
        "room": p.r32(0x0032BAE0), "ev": p.r32(0x0032BAE4), "hp": p.r32(0x01C6C750),
        "v_flag": p.r32(0x000F05C0), "v_isp1": p.r32(0x000F05C4), "v_old": p.r32(0x000F05C8), "v_twin": p.r32(0x000F05CC),
    }
    objs = []
    for addr, blob in find_players(p):
        x, y, z = struct.unpack_from("<3f", blob, 0x70)
        pad = struct.unpack_from("<I", blob, 0xB38)[0]
        slot = struct.unpack_from("<I", blob, 0x48C)[0]
        cid = struct.unpack_from("<I", blob, 0xB50)[0]
        objs.append((addr, x, y, z, pad, slot, cid))
    return g, objs


def show(tag, g, objs):
    def role(a):
        return "0" if a == 0 else "%07X" % a
    print("%s room %04X ev %08X hp %d | player %s saved %s last %s cam %s party0 %s S.player %s S.owner %s S.pad %s | twin %s" % (
        tag, g["room"] & 0xFFFF, g["ev"], g["hp"], role(g["g_player"]), role(g["g_saved"]), role(g["last"]), role(g["cam"]),
        role(g["party0"]), role(g["S.player"]), role(g["S.owner"]), PADS.get(g["S.pad"], hex(g["S.pad"])), role(g["v_twin"])))
    for addr, x, y, z, pad, slot, cid in objs:
        marks = []
        if addr == g["g_player"]:
            marks.append("ENGINE-PLAYER")
        if addr == g["cam"]:
            marks.append("CAMERA")
        if addr == g["v_twin"]:
            marks.append("twin")
        print("     obj %07X pos (%8.1f %7.1f %8.1f) %s slot %07X char %d  %s" % (
            addr, x, y, z, PADS.get(pad, hex(pad)), slot, cid, " ".join(marks)))
    sys.stdout.flush()


def main():
    outdir = pathlib.Path(sys.argv[1])
    port = int(sys.argv[2])
    frames = [int(x) for x in sys.argv[3].split(",") if x]
    timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600
    t0 = time.time()
    p = None
    for f in frames:
        shot = outdir / ("p1_f%06d.png" % f)
        while not shot.exists():
            if time.time() - t0 > timeout:
                sys.exit("timeout waiting for " + shot.name)
            time.sleep(0.02)
        try:
            if p is None:
                p = Pine(port, wait=20)
            g, objs = snapshot(p)
            show("f%06d" % f, g, objs)
        except Exception as e:  # noqa: BLE001
            print("f%06d read failed: %s" % (f, e))
            p = None


if __name__ == "__main__":
    main()
