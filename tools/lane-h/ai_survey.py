"""Lane H: decode the AI script of every object model and count the engine calls that concern "the player" and targets.

  python -I tools/lane-h/ai_survey.py decode     unpack + decode every obj/*.mdlx that holds an AI script (slow, once)
  python -I tools/lane-h/ai_survey.py report     write local/analysis/h/ai_survey.csv and print a summary

Uses the user's OpenKH tools (Bar unpack, Bdxio decode), read-only on the extracted game data.
"""
import collections
import csv
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
APPS = pathlib.Path(r"C:\Users\PC FORCE\Desktop\openkh\Apps")
OBJ = ROOT / "local" / "extract" / "kh2" / "obj"
OUT = ROOT / "local" / "analysis" / "h" / "ai"
TRAPS = ["trap_sysobj_player", "trap_target_search", "trap_btlobj_target", "trap_enemy_get_attacker",
         "trap_sysobj_party", "trap_friend_set_target", "trap_target_seracher_search", "trap_target_set_obj",
         "trap_sysobj_is_player", "trap_obj_is_player", "trap_player_", "trap_camera_", "trap_target_searcher_search"]


def decode():
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(OBJ.glob("*.mdlx"))
    done = 0
    for i, f in enumerate(files):
        txt = OUT / (f.stem + ".txt")
        if txt.exists():
            continue
        lst = subprocess.run([str(APPS / "OpenKh.Command.Bar.exe"), "list", str(f)], capture_output=True, text=True).stdout
        if ", Bdx," not in lst:
            continue
        tmp = OUT / "_tmp" / f.stem
        tmp.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(APPS / "OpenKh.Command.Bar.exe"), "unpack", str(f), "-o", str(tmp), "-s"], capture_output=True)
        bdx = next(iter(tmp.glob("*.bdx")), None)
        if bdx is None:
            continue
        subprocess.run([str(APPS / "OpenKh.Command.Bdxio.exe"), "decode", str(bdx), str(txt), "-r"], capture_output=True)
        done += 1
        if done % 50 == 0:
            print("decoded", done, "at", f.name, flush=True)
    print("decoded now:", done, "total texts:", len(list(OUT.glob("*.txt"))))


def modes(text):
    """Search modes passed to the shared wrapper around trap_target_search: 'push N' right before 'jal x, <label>'."""
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if "trap_target_search" in l]
    found = set()
    for i in idx:
        label = None
        for j in range(i, max(0, i - 14), -1):
            m = re.match(r"(L\d+):", lines[j])
            if m:
                label = m.group(1)
                break
        if not label:
            continue
        for j, l in enumerate(lines):
            if re.search(r"jal \d+, %s\b" % label, l) and j > 0:
                m = re.match(r"\s*push (\d+)\s*$", lines[j - 1])
                found.add(m.group(1) if m else "?")
    return found


def report():
    types = {}
    for line in (ROOT / "local" / "analysis" / "objentry.txt").read_text().splitlines():
        m = re.match(r"0x([0-9A-F]+) type (\S+)\s+model (\S+)", line)
        if m:
            types.setdefault(m.group(3), m.group(2))
    rows = []
    for f in sorted(OUT.glob("*.txt")):
        text = f.read_text(errors="replace")
        names = collections.Counter(re.findall(r"trap_[a-z_0-9]+", text))
        row = {"model": f.stem, "type": types.get(f.stem, "?"), "lines": text.count("\n"),
               "player": names.get("trap_sysobj_player", 0), "search": names.get("trap_target_search", 0),
               "modes": " ".join(sorted(modes(text))), "attacker": names.get("trap_enemy_get_attacker", 0),
               "other": " ".join(sorted(n for n in names if ("player" in n or "party" in n or "friend" in n) and n != "trap_sysobj_player"))}
        rows.append(row)
    with open(ROOT / "local" / "analysis" / "h" / "ai_survey.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    by = collections.defaultdict(list)
    for r in rows:
        by[r["type"]].append(r)
    print("AI scripts decoded:", len(rows))
    for t, rs in sorted(by.items(), key=lambda x: -len(x[1])):
        print("  %-10s %4d scripts | use target search %4d | call 'get the player' %4d (calls in total %d) | use 'last attacker' %d" % (
            t, len(rs), sum(1 for r in rs if r["search"]), sum(1 for r in rs if r["player"]), sum(r["player"] for r in rs),
            sum(1 for r in rs if r["attacker"])))
    md = collections.Counter()
    for r in rows:
        for m in r["modes"].split():
            md[m] += 1
    print("search modes passed by scripts (scripts using each):", dict(md))
    oth = collections.Counter()
    for r in rows:
        for n in r["other"].split():
            oth[n] += 1
    print("other player/party/friend calls (scripts using each):", dict(oth.most_common(30)))
    heavy = sorted((r for r in rows if r["type"] in ("BOSS", "L_BOSS", "ZAKO", "L_ZAKO")), key=lambda r: -r["player"])[:25]
    print("enemy and boss scripts that call 'get the player' most:", ", ".join("%s(%s) %d" % (r["model"], r["type"], r["player"]) for r in heavy))


if __name__ == "__main__":
    {"decode": decode, "report": report}[sys.argv[1]]()
