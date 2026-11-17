"""Lane P: collect per-mission facts from the game data for the parity audit. Read-only on everything it reads.

Sources (all made earlier, none modified):
  local/extract/kh2/msn/jp/*.bar            mission files (header, on-screen meters, text ids)
  local/analysis/lane-c/out/*.csv           lane C's lists (missions, party per program, placements)
  local/analysis/lane-c/ard/*.txt           lane C's dump of every room (scripts and spawn data)
  local/analysis/objentry.txt               object list
  local/analysis/lane-p/msg/*.tsv           English text of the built disc, by message id
Output: local/analysis/lane-p/mission_facts.json and mission_facts.txt

  python -I tools/lane-p/audit_data.py
"""
import collections
import csv
import json
import pathlib
import re
import struct

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
EX = ROOT / "local" / "extract" / "kh2"
LC = ROOT / "local" / "analysis" / "lane-c"
OUT = ROOT / "local" / "analysis" / "lane-p"

# ---------------------------------------------------------------- text
msgs = {}        # id -> (file, text)
by_file = {}
for f in sorted((OUT / "msg").glob("*.tsv")):
    d = {}
    for line in f.read_text(encoding="utf-8").split("\n"):
        k, _, v = line.partition("\t")
        if k.isdigit():
            d[int(k)] = v
    by_file[f.stem] = d
    for k, v in d.items():
        msgs.setdefault(k, (f.stem, v))


def clean(s):
    s = re.sub(r"\{:[^}]*\}", " ", s)
    s = s.replace(" / ", " ")
    return re.sub(r"\s+", " ", s).strip()


def text(mid, world=None):
    if not mid:
        return ""
    if world and world in by_file and mid in by_file[world]:
        return clean(by_file[world][mid])
    if mid in msgs:
        return clean(msgs[mid][1])
    return ""


# ---------------------------------------------------------------- objects
objs = {}
for line in (ROOT / "local" / "analysis" / "objentry.txt").read_text(encoding="utf-8", errors="replace").split("\n"):
    m = re.match(r"0x([0-9A-F]+) type (\S+)\s+model (\S+)", line)
    if m:
        objs[int(m.group(1), 16)] = (m.group(2), m.group(3))

# ---------------------------------------------------------------- rooms (lane C dumps)
rooms = {}
for f in sorted((LC / "ard").glob("*.txt")):
    scripts = collections.defaultdict(dict)   # script name -> program id -> list of command lines
    spawns = collections.defaultdict(list)    # group name -> list of object ids
    cur_entry, cur_type, cur_prog = None, None, None
    for line in f.read_text(encoding="utf-8", errors="replace").split("\n"):
        m = re.match(r"==== entry (\S+) type (\S+)", line)
        if m:
            cur_entry, cur_type, cur_prog = m.group(1), m.group(2), None
            continue
        if cur_type == "AreaDataScript":
            m = re.match(r"Program 0x([0-9A-Fa-f]+)", line)
            if m:
                cur_prog = int(m.group(1), 16)
                scripts[cur_entry][cur_prog] = []
            elif cur_prog is not None and line.strip():
                scripts[cur_entry][cur_prog].append(line.strip())
        elif cur_type == "AreaDataSpawn":
            m = re.match(r"\s+ENT obj 0x([0-9A-Fa-f]+)", line)
            if m:
                spawns[cur_entry].append(int(m.group(1), 16))
    rooms[f.stem] = (scripts, spawns)

# ---------------------------------------------------------------- mission files
FLAG_BITS = [(0x1, "boss"), (0x2, "noDrive"), (0x4, "place"), (0x10, "showWeapon"), (0x20, "noLeave"), (0x40, "noPrize"),
             (0x80, "noPrizebox"), (0x100, "hideMap"), (0x200, "mickey"), (0x400, "noExp"), (0x800, "noMagic"),
             (0x1000, "retry"), (0x2000, "freeSummon"), (0x4000, "noSummon")]
OPS = {1: "CameraStart", 2: "CameraComplete", 3: "CameraFailed", 4: "Timer", 5: "Counter", 6: "Gauge", 7: "ComboCounter",
       8: "MissionScore", 9: "Watch", 10: "LimitCost", 11: "DriveRefillRatio", 12: "AddDrive", 13: "CameraPrize"}
msn = {}
for f in sorted((EX / "msn" / "jp").glob("*.bar")):
    b = f.read_bytes()
    n = struct.unpack_from("<I", b, 4)[0]
    ents = []
    for i in range(n):
        t, dup, nm, off, size = struct.unpack_from("<HH4sII", b, 16 + 16 * i)
        ents.append((t, nm.rstrip(b"\0").decode("ascii", "replace"), off, size))
    t, nm, off, size = ents[0]
    d = b[off:off + size]
    info = dict(entries=[e[1] + ":" + str(e[0]) for e in ents], ok=False, ops=[])
    if size >= 0x1C and struct.unpack_from("<H", d, 0)[0] == 2:
        magic, mid, flags, info_text, pause, _p, pause_text, help_seqd, bonus, anti, _p2 = struct.unpack_from("<HHHHBBHBBBB", d, 0)
        info.update(ok=True, id=mid, flags=flags, info_text=info_text, pause=pause, pause_text=pause_text, bonus=bonus, anti=anti,
                    head=d[:0x1C].hex())
        pos = 0x1C
        while pos + 4 <= len(d):
            op, cnt = struct.unpack_from("<hh", d, pos)
            if op <= 0 or op > 13 or cnt < 0:
                break
            params = list(struct.unpack_from("<%di" % cnt, d, pos + 4)) if cnt else []
            info["ops"].append((OPS[op], params))
            pos += 4 + 4 * cnt
    msn[f.stem] = info

# ---------------------------------------------------------------- lane C lists
mission_rows = list(csv.DictReader(open(LC / "out" / "missions.csv", encoding="utf-8")))
prog_rows = list(csv.DictReader(open(LC / "out" / "party_programs.csv", encoding="utf-8")))
uses = collections.defaultdict(list)
room_names = {}
for r in prog_rows:
    room_names[r["room"]] = r["room_name"]
    if r["mission"]:
        for name in re.split(r"\s*\+\d+ more", r["mission"]):
            if name:
                uses[name.strip()].append((r["room"], r["script"], int(r["program"], 16), r["party"]))
# a program can name several missions; find them again in the dumps
for room, (scripts, spawns) in rooms.items():
    for sname, progs in scripts.items():
        for pid, lines in progs.items():
            for c in lines:
                m = re.match(r'Mission (0x[0-9A-Fa-f]+) "([^"]*)"', c)
                if m:
                    party = next((x.split()[1] for x in lines if x.startswith("Party ")), "")
                    tup = (room, sname, pid, party)
                    if tup not in uses[m.group(2)]:
                        uses[m.group(2)].append(tup)

facts = {}
for mr in mission_rows:
    name = mr["mission"]
    info = msn.get(name, {})
    world = mr["world"]
    o = dict(mission=name, world=world, id=mr["id"], has_file=mr["has_file"] == "True", flags=mr["flags"], meters=mr["meters"],
             name_flags=mr["name_flags"], party=mr["party_values"], pause_menu=mr["pause_menu"])
    o["info_text"] = text(info.get("info_text"), world) if info.get("ok") else ""
    o["pause_text"] = text(info.get("pause_text"), world) if info.get("ok") else ""
    o["info_id"] = info.get("info_text", 0) if info.get("ok") else 0
    o["pause_id"] = info.get("pause_text", 0) if info.get("ok") else 0
    o["ops"] = info.get("ops", [])
    o["entries"] = info.get("entries", [])
    # texts named by the meter op-codes (first parameter is often a message id)
    mt = []
    for op, params in o["ops"]:
        for p in params[:6]:
            t = text(p, world) if 0 < p < 0x10000 else ""
            if t and len(t) < 80:
                mt.append(f"{op}: {t}")
    o["meter_texts"] = sorted(set(mt))
    rooms_used, objs_by_type, special = [], collections.defaultdict(collections.Counter), []
    for room, sname, pid, party in sorted(set(uses.get(name, []))):
        rooms_used.append(f"{room}:{sname}:0x{pid:02X}")
        scripts, spawns = rooms.get(room, ({}, {}))
        lines = scripts.get(sname, {}).get(pid, [])
        for c in lines:
            m = re.match(r'Spawn(?:Alt)? "([^"]*)"', c)
            if m:
                for oid in spawns.get(m.group(1), []):
                    typ, model = objs.get(oid, ("?", f"0x{oid:04X}"))
                    objs_by_type[typ][model] += 1
    o["programs"] = rooms_used
    o["room_names"] = sorted({f"{r.split(':')[0]} {room_names.get(r.split(':')[0], '')}".strip() for r in rooms_used})
    o["objects"] = {t: dict(c) for t, c in objs_by_type.items()}
    facts[name] = o

(OUT / "mission_facts.json").write_text(json.dumps(facts, indent=1), encoding="utf-8")
lines = []
for name in sorted(facts):
    o = facts[name]
    lines.append(f"## {name} [{o['id']}] flags={o['flags']} meters={o['meters']} party={o['party']} name={o['name_flags']}")
    lines.append(f"   rooms: {'; '.join(o['room_names'])} | programs: {' '.join(o['programs'])}")
    lines.append(f"   info({o['info_id']}): {o['info_text']}")
    lines.append(f"   pause({o['pause_id']}): {o['pause_text'][:300]}")
    if o["meter_texts"]:
        lines.append("   meter texts: " + " | ".join(o["meter_texts"]))
    for t in ("BOSS", "L_BOSS", "PLAYER", "FRIEND", "MINIGAME", "BTLNPC", "ZAKO", "L_ZAKO", "F_OBJ", "G_OBJ", "NPC", "RTN"):
        if t in o["objects"]:
            c = o["objects"][t]
            lines.append(f"   {t}: " + ", ".join(f"{k}x{v}" if v > 1 else k for k, v in sorted(c.items())[:14]))
    lines.append("   file entries: " + " ".join(o["entries"]))
(OUT / "mission_facts.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("missions:", len(facts), "with info text:", sum(1 for o in facts.values() if o["info_text"]),
      "with pause text:", sum(1 for o in facts.values() if o["pause_text"]))
