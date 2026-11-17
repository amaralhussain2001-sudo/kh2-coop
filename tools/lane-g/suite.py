"""Lane G: run the whole test set for one patch version and print a pass/fail style summary.

  python -I tools/lane-g/suite.py <tag> <patchDir> <kitPatchDir> <diePatchDir> [part ...]
parts: solo roam fight kit react room die friends ca5rand long     (default: all)
Needs the reference recordings g-ref1 and g-ref2 (one Sora, no twin, no patch): tools/lane-g/m_ref.py g-ref1 -
Results: local/tests/g-<tag>-<part>/ and local/analysis/g/suite-<tag>.txt
"""
import pathlib
import struct
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from glib import load, buttons, SLOT_STEP  # noqa: E402

tag, patch, kit, die = sys.argv[1:5]
parts = sys.argv[5:] or ["solo", "roam", "fight", "kit", "react", "room", "die", "friends", "ca5rand", "long"]
out_lines = []


def say(s):
    print(s, flush=True)
    out_lines.append(s)


def py(script, *args):
    r = subprocess.run([sys.executable, "-I", str(HERE / script), *args], capture_output=True, text=True)
    return r.stdout + r.stderr


def sync_line(name):
    h = (ROOT / "local" / "tests" / name / "harness.txt")
    t = h.read_text() if h.exists() else ""
    best = ""
    for line in t.splitlines():
        if "OUT OF SYNC" in line or "TIMED OUT" in line:
            return "PROBLEM: " + line[11:140]
        if "session closed" in line and "compared 0" not in line:
            best = line[11:110]
    return best or "(one copy: no digests)" if "session closed" in t else "NO SESSION END LINE"


def equiv(ref_start, name, blk, start, length, noy=False):
    o = py("an_equiv.py", "g-ref1", str(ref_start), name, blk, str(start), str(length), *(["--noy"] if noy else []))
    return "SAME" if "SAME BEHAVIOUR" in o else "DIFFERENT (" + o.strip().splitlines()[0][-40:] + ")"


for part in parts:
    name = f"g-{tag}-{part}"
    if part == "solo":
        py("m_ref.py", name, patch)
        o = py("an_same.py", "g-ref2", name, "obj1", "S", "S2", "slots", "log1")
        ident = [l.split()[0] for l in o.splitlines() if "IDENTICAL" in l]
        zero = "all zero" in o
        say(f"solo    one Sora, patch on, against no patch: identical blocks {ident}; second control object memory untouched: {zero}")
    elif part == "roam":
        py("m_roam.py", name, patch)
        # windows start 2 frames after the first press (the frame the action begins), so the state left over from
        # the previous action is not compared
        res = {
            "hero1 ground combo": equiv(4702, name, "obj1", 4702, 104), "hero2 ground combo": equiv(4702, name, "twin", 4902, 104),
            "both at once h1": equiv(4702, name, "obj1", 5102, 104), "both at once h2": equiv(4702, name, "twin", 5102, 104),
            "interleaved h1": equiv(4702, name, "obj1", 5302, 104), "interleaved h2": equiv(4702, name, "twin", 5314, 104),
            "jump h1": equiv(5502, name, "obj1", 5502, 54), "jump h2": equiv(5502, name, "twin", 5562, 54),
            "both jump h1": equiv(5502, name, "obj1", 5622, 54), "both jump h2": equiv(5502, name, "twin", 5622, 54),
            "air combo h1": equiv(5702, name, "obj1", 5702, 94, True), "air combo h2": equiv(5702, name, "twin", 5802, 94, True),
        }
        bad = {k: v for k, v in res.items() if v != "SAME"}
        r = load(name)
        cur = {}
        for s in r.samples:
            fr = s["vc"] + 152
            for lab, f in (("after P1 DOWN", 5915), ("after P2 DOWN", 5975)):
                if abs(fr - f) <= 1:
                    cur[lab] = (struct.unpack_from("<I", s["S"], 0x90)[0], struct.unpack_from("<I", s["S2"], 0x90)[0])
        say(f"roam    {len(res) - len(bad)}/{len(res)} action comparisons equal to the lone-Sora reference {bad if bad else ''}; cursors (P1 menu, P2 menu) {cur}; {sync_line(name)}")
    elif part == "fight":
        py("m_attack.py", name, patch)
        o = py("an_fight.py", name)
        for l in o.splitlines()[1:]:
            say("fight   " + l.strip()[:175])
        say("fight   " + sync_line(name))
    elif part == "kit":
        py("m_kit.py", name, kit)
        r = load(name)
        names = {0xAD: "guard", 0xD1: "dodge", 0x38: "Fire", 0x3B: "Blizzard", 0x3E: "Thunder", 0xC9: "highjump", 0xCA: "airdodge"}
        wrong, seen = 0, {"obj1": [], "twin": []}
        for who in seen:
            prev = None
            for s in r.samples:
                a = struct.unpack_from("<I", s[who], 0x154)[0]
                if a != prev and a in names:
                    own, other = (buttons(s["pad1"]), buttons(s["pad2"])) if who == "obj1" else (buttons(s["pad2"]), buttons(s["pad1"]))
                    seen[who].append(names[a])
                    wrong += (not own) or bool(other)
                prev = a
        mp = [struct.unpack_from("<I", s["slots"], 0x268 + 0x180)[0] for s in r.samples]
        say(f"kit     hero1 {seen['obj1']}  hero2 {seen['twin']}  actions started by the wrong pad: {wrong}; shared MP {mp[0]} -> {mp[-1]}; {sync_line(name)}")
    elif part == "react":
        py("m_react.py", name, patch, "12", "p2")
        r = load(name)
        pre = next(s for s in r.samples if s["vc"] + 152 >= 4890)
        offered = (struct.unpack_from("<H", pre["S"], 0xA1E)[0], struct.unpack_from("<H", pre["S2"], 0xA1E)[0])
        shot = ROOT / "local" / "tests" / name / "p1_f004915.png"
        import hashlib
        h = hashlib.sha1(shot.read_bytes()).hexdigest()[:10] if shot.exists() else "missing"
        say(f"react   reaction offered before Triangle (hero1, hero2) = {tuple(hex(x) for x in offered)} (0x37 = Save); picture after pad 2's Triangle {h} "
            f"({'SAVE menu, same picture as the checked run' if h == '391681fef6' else 'CHECK BY EYE'}); {sync_line(name)}")
    elif part in ("room", "long"):
        py("m_room.py", name, patch, *(["34000"] if part == "long" else []))
        o = py("an_long.py", name, "4760" if part == "room" else "6400")
        keep = [l.strip() for l in o.splitlines() if l.strip().startswith(("frame", "obj1", "twin", "S:", "S2:", "spare", "from frame"))]
        for l in keep:
            say(f"{part:7s} " + l[:190])
        say(f"{part:7s} " + sync_line(name))
    elif part == "die":
        py("m_die.py", name, die)
        o = py("an_long.py", name, "5000")
        n_att = sum(1 for l in o.splitlines() if "S attached True   S2 attached True" in l)
        n_det = sum(1 for l in o.splitlines() if "S attached False  S2 attached False" in l)
        say(f"die     both control objects attached {n_att} times and released {n_det} times (Game Over / Continue cycles); {sync_line(name)}")
    elif part == "friends":
        py("m_friends.py", name, patch)
        o = py("an_fight.py", name, "--c", "152", "--windows", "4700-5060,5100-5460")
        for l in o.splitlines()[1:]:
            say("friends " + l.strip()[:175])
        o = py("an_long.py", name, "4690")
        for l in o.splitlines():
            if l.strip().startswith("frame"):
                say("friends " + l.strip()[:150])
        say("friends " + sync_line(name))
    elif part == "ca5rand":
        py("m_ca5rand.py", name, patch)
        o = py("an_long.py", name, "4690")
        keep = [l.strip() for l in o.splitlines() if l.strip().startswith(("obj1", "twin", "from frame"))]
        for l in keep:
            say("ca5rand " + l[:190])
        say("ca5rand " + sync_line(name))
(ROOT / "local" / "analysis" / "g" / f"suite-{tag}.txt").write_text("\n".join(out_lines) + "\n")
