"""Lane A: run one 'who controls whom' test and report how each player object reacted to each controller.

Both controllers press the same menu buttons to reach play (so the test works even when menus are switched to
controller 2). Then: P1 holds stick right 6300-6390, P2 holds stick up 6500-6590, P2 presses Cross 6700,
P1 presses Cross 6900. Positions of the two player objects are read through PINE (read-only).

  python -I tools/lane-a/sep_run.py <name> <patchDir|-> <runDir> <port> <pinePort> [iso]
"""
import pathlib
import struct
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
name, patch, run_dir, port, pine = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
iso = sys.argv[6] if len(sys.argv) > 6 else str(ROOT / "local" / "iso" / "test-a-t1.iso")
OBJ1, TWIN = 0x01A90B70, 0x01AAB360   # position vectors of the two player objects in the t1 scene (VERIFIED a-in1)
out = ROOT / "local" / "tests" / name
frames = [6290, 6400, 6480, 6600, 6690, 6716, 6800, 6916, 7000]

reach = ["3000 4 O", "3120 4 O", "3240 4 O", "3360 4 O", "3480 4 O", "3600 4 O", "4200 4 START", "4230 4 DOWN",
         "4260 4 O", "4680 4 START", "4710 4 DOWN", "4740 4 O", "5200 4 O", "5350 4 O", "5500 4 O", "5650 4 O",
         "5800 4 O", "5950 4 O"]
sdir = ROOT / "tests" / "scripts" / "lane-a"
(sdir / "sepb_p1.txt").write_text("\n".join(reach + ["6300 90 LX=255", "6900 4 X", "7050 1 "]) + "\n")
(sdir / "sepb_p2.txt").write_text("\n".join(reach + ["6500 90 LY=0", "6700 4 X", "7050 1 "]) + "\n")

if out.exists():
    for f in out.iterdir():
        f.unlink()
cmd = [sys.executable, "-I", str(ROOT / "tools" / "kh2_session.py"), "run", name, "--run-dir", run_dir, "--port", port,
       "--iso", iso, "--players", "2", "--slots", "0,1", "--frames", "7050", "--speed", "2",
       "--snap", ",".join(map(str, frames)), "--script", str(sdir / "sepb_p1.txt"), "--script2", str(sdir / "sepb_p2.txt"),
       "--then", "idle", "--fresh-card", "--pine", pine, "--timeout", "300", "--tail", "1"]
if patch != "-":
    cmd += ["--patch-dir", patch]
h = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
time.sleep(3)
p = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "lane-a" / "pine_ranges.py"), str(out), pine,
                    ",".join(map(str, frames)), f"{OBJ1:08X}:10,{TWIN:08X}:10", "--timeout", "280"],
                   capture_output=True, text=True)
hout = h.communicate()[0]


def pos(f, a):
    fn = out / f"mem_f{f:06d}_{a:08X}.bin"
    return struct.unpack("<4f", fn.read_bytes()) if fn.exists() else None


res = {}
ok = all(pos(f, OBJ1) for f in frames)
if not ok:
    print(f"{name}: NO DATA (did not reach play?)  {p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ''}")
    sys.exit(0)
for label, a in (("obj1", OBJ1), ("twin", TWIN)):
    def d(f0, f1):
        p0, p1 = pos(f0, a), pos(f1, a)
        return abs(p1[0] - p0[0]) + abs(p1[2] - p0[2])
    moved_p1 = d(6290, 6400) > 5      # during P1 stick window
    moved_p2 = d(6480, 6600) > 5      # during P2 stick window
    jump_p2 = abs(pos(6716, a)[1] - pos(6690, a)[1]) > 2
    jump_p1 = abs(pos(6916, a)[1] - pos(6800, a)[1]) > 2
    res[label] = (moved_p1, moved_p2, jump_p1, jump_p2)
sync = "never out of sync" in hout
print(f"{name}: obj1 move[P1={res['obj1'][0]:d} P2={res['obj1'][1]:d}] jump[P1={res['obj1'][2]:d} P2={res['obj1'][3]:d}]   "
      f"twin move[P1={res['twin'][0]:d} P2={res['twin'][1]:d}] jump[P1={res['twin'][2]:d} P2={res['twin'][3]:d}]   in-sync={sync}")
