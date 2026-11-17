"""Lane C: build the bench list from the game's own data (no emulator).

Inputs (all read-only):
  local/analysis/objentry.txt              object list (Kh2Tool objentry)
  local/analysis/lane-c/ard/*.txt          every room: scripts + spawn data (LaneC ard-full)
  local/analysis/lane-c/*.yml              memt, cmd, limt, sumn, fmlv tables (LaneC table)
  local/extract/kh2/msn/jp/*.bar           mission files
  local/extract/kh2/00place.bin            room name ids
  English pack msg/jp/sys.yml              English names for message ids
  local/analysis/lane-c/src/Constants.cs   world codes and names (OpenKH source)
Outputs:
  docs/lanes/C-bench-list.md
  local/analysis/lane-c/out/*.csv          full lists behind the tables

  python -I tools/lane-c/mine.py
"""
import collections
import csv
import math
import pathlib
import re
import struct

ROOT = pathlib.Path(__file__).resolve().parents[2]
AN = ROOT / "local" / "analysis"
LC = AN / "lane-c"
OUT = LC / "out"
OUT.mkdir(parents=True, exist_ok=True)
EX = ROOT / "local" / "extract" / "kh2"
PACK = next((ROOT / "local" / "downloads" / "languagepack-en" / "src").glob("languagepack-en-*"))
DOC = ROOT / "docs" / "lanes" / "C-bench-list.md"

PLAYER_PH, FRIEND1_PH, FRIEND2_PH = 0x0236, 0x0237, 0x0238

# ---------------------------------------------------------------- helpers


def hexid(n):
    return f"0x{n:02X}"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "/") for c in r) + " |")
    return "\n".join(out)


def write_csv(name, header, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def yaml_blocks(path):
    """Very small reader for the flat list-of-maps YAML written by LaneC (scalars and simple lists)."""
    text = path.read_text(encoding="utf-8")
    items = []
    for blk in re.split(r"(?m)^- ", text)[1:]:
        d = {}
        key = None
        for line in blk.split("\n"):
            m = re.match(r"\s*([A-Za-z0-9]+):\s*(.*)$", line)
            if m:
                key = m.group(1)
                d[key] = m.group(2)
                continue
            m = re.match(r"\s*-\s*(.*)$", line)
            if m and key:
                if not isinstance(d.get(key), list):
                    d[key] = []
                d[key].append(m.group(1))
        items.append(d)
    return items


# ---------------------------------------------------------------- worlds, texts, places

const = (LC / "src" / "Constants.cs").read_text(encoding="utf-8")
codes = re.findall(r'"([a-z]{2})"', re.search(r"WorldIds = new string\[WorldCount\]\s*\{(.*?)\};", const, re.S).group(1))
wnames = re.findall(r'"([^"]+)"', re.search(r"WorldNames = new string\[WorldCount\]\s*\{(.*?)\};", const, re.S).group(1))
WORLD_NAME = dict(zip(codes, wnames))
WORLD_ID = {c: i for i, c in enumerate(codes)}

sys_text = {}
raw = (PACK / "msg" / "jp" / "sys.yml").read_text(encoding="utf-8-sig")
for blk in re.split(r"(?m)^- id: ", raw)[1:]:
    lines = blk.split("\n")
    try:
        mid = int(lines[0].strip(), 0)
    except ValueError:
        continue
    val = ""
    for i, line in enumerate(lines[1:], 1):
        m = re.match(r"\s*en:\s*(.*)$", line)
        if m:
            val = m.group(1).strip()
            if val in (">-", "|-", ">", "|"):
                val = " ".join(x.strip() for x in lines[i + 1:] if x.strip())
            break
    val = val.strip("'\"")
    val = re.sub(r"\{:[^}]*\}", "", val).strip()
    sys_text[mid] = val


def msg_name(message_id):
    if message_id & 0x8000:
        return sys_text.get(message_id & 0x7FFF, "")
    return ""


# Room names. The place table gives, per room, a message id and the developers' Japanese name. The id is only
# right for some rooms (for tt05 and later it points at item texts, in the Japanese original too), so the room is
# matched through its Japanese name: find the system message with that same Japanese text and take the English
# text of the same message id.
import difflib

sys_jp = {}
for line in (LC / "sys_jp_original.tsv").read_text(encoding="utf-8").splitlines():
    k, _, v = line.partition("\t")
    sys_jp[int(k)] = v


def norm_jp(s):
    return s.replace("：", ":").replace(" ", "").replace("　", "").strip()


jp_index = {}
for k in sorted(sys_jp):
    jp_index.setdefault(norm_jp(sys_jp[k]), k)

place_name = {}
place_dev = {}
place_how = collections.Counter()
pb = (EX / "00place.bin").read_bytes()
for i in range(struct.unpack_from("<I", pb, 4)[0]):
    _t, _d, nm, off, size = struct.unpack_from("<HH4sII", pb, 16 + 16 * i)
    w = nm.rstrip(b"\0").decode()
    if size < 4:
        continue
    d = pb[off:off + size]
    count = struct.unpack_from("<H", d, 2)[0] // 4
    for r in range(count):
        mid, so = struct.unpack_from("<HH", d, 4 * r)
        dev = norm_jp(d[4 * r + so:].split(b"\0")[0].decode("shift_jis", "replace"))
        place_dev[(w, r)] = dev
        key = mid & 0x7FFF
        name = ""
        if mid & 0x8000 and key in sys_jp and difflib.SequenceMatcher(None, norm_jp(sys_jp[key]), dev).ratio() > 0.7:
            name = sys_text.get(key, "")
            place_how["by id"] += 1
        elif dev in jp_index:
            name = sys_text.get(jp_index[dev], "")
            place_how["by Japanese name"] += 1
        else:
            # same text written with a variant character (same length, almost equal)
            close = [k for k in difflib.get_close_matches(dev, list(jp_index), n=3, cutoff=0.85) if len(k) == len(dev)]
            if close and len(dev) >= 4:
                name = sys_text.get(jp_index[close[0]], "")
                place_how["by Japanese name"] += 1
            else:
                place_how["no match"] += 1
        place_name[(w, r)] = re.sub(r"\s+", " ", name).replace("´", "'").strip()


def rl(room):
    """room id with its English name in brackets when one is known"""
    n = room_label(room)
    return f"{room} ({n})" if n else room


def room_label(room):
    w, n = room[:2], room[2:]
    try:
        return place_name.get((w, int(n)), "")
    except ValueError:
        return ""


# ---------------------------------------------------------------- objects

objs = {}
for line in (AN / "objentry.txt").read_text(encoding="utf-8").splitlines():
    m = re.match(r"^0x([0-9A-F]+) type (\S+)\s+model (\S+)\s+anim (.*?)\s*flags 0x([0-9A-F]+) status (\d+) moveset (\d+) form (\S+)", line)
    if m:
        objs[int(m.group(1), 16)] = dict(type=m.group(2), model=m.group(3), anim=m.group(4).strip(), flags=int(m.group(5), 16),
                                         status=int(m.group(6)), moveset=int(m.group(7)), form=m.group(8))


def oname(i):
    return objs[i]["model"] if i in objs else f"?{i:#x}"


player_objs = {i: o for i, o in objs.items() if o["type"] == "PLAYER"}

# ---------------------------------------------------------------- rooms

rooms = {}
for f in sorted((LC / "ard").glob("*.txt")):
    room = f.stem
    entries = []
    cur = None
    prog = None
    sp = None
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.startswith("==== entry "):
            m = re.match(r"==== entry (.*?) type (\S+) index (\d+) size (\d+)$", line)
            cur = dict(name=m.group(1), type=m.group(2), size=int(m.group(4)), programs=[], sps=[], bad=False)
            entries.append(cur)
            prog = None
            sp = None
            continue
        if cur is None:
            continue
        if "(cannot decode" in line:
            cur["bad"] = True
            continue
        if cur["type"] == "AreaDataScript":
            s = line.strip()
            if s.startswith("Program "):
                prog = dict(id=int(s.split()[1], 16), cmds=[])
                cur["programs"].append(prog)
            elif s and prog is not None:
                prog["cmds"].append(s)
        elif cur["type"] == "AreaDataSpawn":
            s = line.strip()
            if s.startswith("SP "):
                t = s.split()
                sp = dict(index=int(t[1]), type=int(t[3]), flag=int(t[5]), id=int(t[7]), place=int(t[10]), door=int(t[12]),
                          world=int(t[14]), ents=[], acts=[], walk=int(t[22]), ret=int(t[24]), sig=int(t[26]))
                cur["sps"].append(sp)
            elif s.startswith("ENT ") and sp is not None:
                t = s.split()
                sp["ents"].append(dict(obj=int(t[2], 16), x=float(t[4]), y=float(t[5]), z=float(t[6]), type=int(t[8]),
                                       arg=int(t[10]), serial=int(t[12]), rc=int(t[18]), cmd=int(t[22])))
            elif s.startswith("ACT ") and sp is not None:
                t = s.split()
                sp["acts"].append(dict(shape=int(t[2]), option=int(t[4]), flags=int(t[14], 16), type=int(t[16])))
    rooms[room] = entries

ROOMS = sorted(rooms)
WORLDS = sorted({r[:2] for r in ROOMS}, key=lambda c: WORLD_ID.get(c, 99))

# ---------------------------------------------------------------- 1. party settings

party_counts = collections.Counter()
party_kind = collections.Counter()
party_rows = []          # room, kind, program, party, mission
mission_uses = []        # room, kind, program, mission id, mission name, party
setmember = []
setpartymenu = collections.Counter()
cmd_words = collections.Counter()
programs_total = 0
programs_with_party = 0
for room in ROOMS:
    for e in rooms[room]:
        if e["type"] != "AreaDataScript":
            continue
        for p in e["programs"]:
            programs_total += 1
            party = None
            missions = []          # a program can name several missions (inside "If Entrance n" blocks)
            spawns = []
            for c in p["cmds"]:
                w = c.split()[0]
                cmd_words[w] += 1
                if w == "Party":
                    party = c.split()[1]
                elif w == "Mission":
                    m = re.match(r'Mission (0x[0-9A-Fa-f]+) "([^"]*)"', c)
                    if m and (int(m.group(1), 16), m.group(2)) not in missions:
                        missions.append((int(m.group(1), 16), m.group(2)))
                elif w in ("Spawn", "SpawnAlt"):
                    spawns += re.findall(r'"([^"]*)"', c)
                elif w == "SetMember":
                    setmember.append((room, e["name"], p["id"], c.split()[1]))
                elif w == "SetPartyMenu":
                    setpartymenu[c.split()[1]] += 1
            p["party"] = party
            p["spawns"] = spawns
            p["missions"] = [n for _i, n in missions]
            mtxt = ""
            if missions:
                mtxt = missions[0][1] if len(missions) == 1 else f"{missions[0][1]} +{len(missions) - 1} more"
            if party:
                programs_with_party += 1
                party_counts[party] += 1
                party_kind[(e["name"], party)] += 1
                party_rows.append((room, e["name"], p["id"], party, mtxt))
            for mid, mname in missions:
                mission_uses.append((room, e["name"], p["id"], mid, mname, party or ""))

write_csv("party_programs.csv", ["room", "room_name", "script", "program", "party", "mission"],
          [(r, room_label(r), k, hexid(p), pa, m) for r, k, p, pa, m in party_rows])

solo_by_room = collections.defaultdict(list)
for r, k, p, pa, m in party_rows:
    if pa == "NO_FRIEND":
        solo_by_room[r].append((p, m))

# ---------------------------------------------------------------- 2. player / friend placeholders

# One row per PLAYER placeholder entity ("a placement"). One spawn point can hold several placements, one per
# entrance number (the entity's spawn argument); the friend placeholders that belong to it carry the same argument.
spawn_rows = []   # room, group, sp index, same-arg player count, n_f1, n_f2, others, type, arg, d1, d2
dists = []
group_player = collections.defaultdict(lambda: [0, 0])   # (room, group) -> [placements, placements with a friend]
sp_with_player = 0
for room in ROOMS:
    for e in rooms[room]:
        if e["type"] != "AreaDataSpawn":
            continue
        for sp in e["sps"]:
            pl = [x for x in sp["ents"] if x["obj"] == PLAYER_PH]
            if not pl:
                continue
            sp_with_player += 1
            others = sum(1 for x in sp["ents"] if x["obj"] not in (PLAYER_PH, FRIEND1_PH, FRIEND2_PH))
            for p0 in pl:
                same = [x for x in pl if x["type"] == p0["type"] and x["arg"] == p0["arg"]]
                f1 = [x for x in sp["ents"] if x["obj"] == FRIEND1_PH and x["type"] == p0["type"] and x["arg"] == p0["arg"]]
                f2 = [x for x in sp["ents"] if x["obj"] == FRIEND2_PH and x["type"] == p0["type"] and x["arg"] == p0["arg"]]

                def dist(a, b):
                    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["z"] - b["z"]) ** 2)
                d1 = dist(p0, f1[0]) if f1 else None
                d2 = dist(p0, f2[0]) if f2 else None
                for d in (d1, d2):
                    if d is not None:
                        dists.append(d)
                spawn_rows.append((room, e["name"], sp["index"], len(same), len(f1), len(f2), others, p0["type"], p0["arg"],
                                   "" if d1 is None else round(d1), "" if d2 is None else round(d2)))
                g = group_player[(room, e["name"])]
                g[0] += 1
                g[1] += 1 if (f1 or f2) else 0
write_csv("player_placements.csv",
          ["room", "room_name", "group", "spawnpoint", "players_with_same_argument", "friend1", "friend2", "other_entities",
           "spawn_type", "spawn_arg", "dist_friend1", "dist_friend2"],
          [(r, room_label(r)) + tuple(rest) for r, *rest in spawn_rows])

rooms_with_player_ph = {r[0] for r in spawn_rows}
no_friend_sp = [r for r in spawn_rows if r[4] == 0 and r[5] == 0]
one_friend_sp = [r for r in spawn_rows if (r[4] == 0) != (r[5] == 0)]
multi_player_sp = [r for r in spawn_rows if r[3] > 1]
dists.sort()

# How each party value goes together with the player placements the same program spawns.
party_vs_place = collections.defaultdict(lambda: [0, 0, 0, 0])   # party -> [programs, with friends, player only, no player group]
for room in ROOMS:
    for e in rooms[room]:
        if e["type"] != "AreaDataScript":
            continue
        for p in e["programs"]:
            if not p.get("party"):
                continue
            row = party_vs_place[p["party"]]
            row[0] += 1
            gs = [group_player[(room, g)] for g in p["spawns"] if (room, g) in group_player]
            if not gs:
                row[3] += 1
            elif any(g[1] for g in gs):
                row[1] += 1
            else:
                row[2] += 1


def pct(v, q):
    return v[min(len(v) - 1, int(len(v) * q))] if v else 0


# ---------------------------------------------------------------- 3. other player objects

direct_player = collections.defaultdict(list)   # obj -> [(room, group)]
friend_direct = collections.Counter()
rc_entities = 0
rc_values = collections.Counter()
rc_types = collections.Counter()
ent_total = 0
act_total = 0
act_types = collections.Counter()
sp_total = 0
sp_tele = 0
walk_total = ret_total = sig_total = 0
groups_total = 0
for room in ROOMS:
    for e in rooms[room]:
        if e["type"] != "AreaDataSpawn":
            continue
        groups_total += 1
        for sp in e["sps"]:
            sp_total += 1
            if sp["place"] or sp["door"] or sp["world"]:
                sp_tele += 1
            walk_total += sp["walk"]
            ret_total += sp["ret"]
            sig_total += sp["sig"]
            for a in sp["acts"]:
                act_total += 1
                act_types[a["type"]] += 1
            for x in sp["ents"]:
                ent_total += 1
                if x["rc"]:
                    rc_entities += 1
                    rc_values[x["rc"]] += 1
                    rc_types[objs[x["obj"]]["type"] if x["obj"] in objs else "?"] += 1
                o = objs.get(x["obj"])
                if o and o["type"] == "PLAYER" and x["obj"] != PLAYER_PH:
                    direct_player[x["obj"]].append((room, e["name"]))
                if o and o["type"] == "FRIEND" and x["obj"] not in (FRIEND1_PH, FRIEND2_PH):
                    friend_direct[x["obj"]] += 1
write_csv("direct_player_objects.csv", ["object", "model", "room", "room_name", "group"],
          [(f"0x{o:04X}", oname(o), r, room_label(r), g) for o, lst in sorted(direct_player.items()) for r, g in lst])

MEMBERS = ["Sora", "Donald", "Goofy", "WorldCharacter", "FormValor", "FormWisdom", "FormLimit", "FormTrinity(Master)", "FormFinal",
           "Antiform", "Mickey", "SoraHighPoly", "FormValorHighPoly", "FormWisdomHighPoly", "FormLimitHighPoly",
           "FormTrinityHighPoly", "FormFinalHighPoly", "AntiformHighPoly"]
memt_text = (LC / "memt.yml").read_text(encoding="utf-8")
memt_entries = []
body, _, tail = memt_text.partition("MemberIndexCollection:")
for blk in re.split(r"(?m)^- WorldId: ", body)[1:]:
    lines = blk.split("\n")
    d = dict(world=int(lines[0]))
    members = []
    in_members = False
    for line in lines[1:]:
        m = re.match(r"\s*([A-Za-z]+):\s*(-?\d+)?$", line)
        if m and m.group(1) != "Members":
            d[m.group(1)] = int(m.group(2) or 0)
            in_members = False
        elif m:
            in_members = True
        else:
            m = re.match(r"\s*-\s*(-?\d+)$", line)
            if m and in_members:
                members.append(int(m.group(1)) & 0xFFFF)
    d["members"] = members
    for key in ("PlayerSize", "FriendSize"):
        m = re.search(key + r":\s*(-?\d+)", blk)
        d[key] = int(m.group(1)) if m else 0
    memt_entries.append(d)
memt_index = []
for blk in re.split(r"(?m)^- Player: ", tail)[1:]:
    vals = [int(blk.split("\n")[0])] + [int(x) for x in re.findall(r":\s*(\d+)", blk)]
    memt_index.append(vals[:4])

# ---------------------------------------------------------------- 4. missions

FLAG_BITS = [(0x1, "boss"), (0x2, "noDrive"), (0x4, "place"), (0x10, "showWeapon"), (0x20, "noLeave"), (0x40, "noPrize"),
             (0x80, "noPrizebox"), (0x100, "hideMap"), (0x200, "mickey"), (0x400, "noExp"), (0x800, "noMagic"),
             (0x1000, "retry"), (0x2000, "freeSummon"), (0x4000, "noSummon")]
OPS = {1: "CameraStart", 2: "CameraComplete", 3: "CameraFailed", 4: "Timer", 5: "Counter", 6: "Gauge", 7: "ComboCounter",
       8: "MissionScore", 9: "Watch", 10: "LimitCost", 11: "DriveRefillRatio", 12: "AddDrive", 13: "CameraPrize"}
NAME_TOKENS = ["SKATE", "GIMMICK", "KINOKO", "TRAP", "MEDAL", "COLOSSEUM", "COL_", "WORK", "BAGGAGE", "LETTER", "PERFORM", "CLEAN",
               "POSTER", "WORM", "CONFINE", "_FM_", "NAZO", "SWITCH", "SHIP_BATTLE", "WORLDMAP", "AXEL", "_FREE", "_RE"]

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
    info = dict(file=f.stem, entry=nm, entries=len(ents), ok=False, ops=collections.Counter(), drive_ratio=None, limit_cost=None)
    if size >= 0x1C and struct.unpack_from("<H", d, 0)[0] == 2:
        magic, mid, flags, info_text, pause, _p, pause_text, help_seqd, bonus, anti, _p2 = struct.unpack_from("<HHHHBBHBBBB", d, 0)
        info.update(ok=True, id=mid, flags=flags, pause=pause, bonus=bonus, anti=anti)
        pos = 0x1C
        while pos + 4 <= len(d):
            op, cnt = struct.unpack_from("<hh", d, pos)
            if op <= 0 or op > 13 or cnt < 0:
                break
            params = d[pos + 4:pos + 4 + 4 * cnt]
            info["ops"][OPS[op]] += 1
            if op == 11 and len(params) >= 4:
                info["drive_ratio"] = round(struct.unpack_from("<f", params, 0)[0], 3)
            if op == 10 and len(params) >= 4:
                info["limit_cost"] = struct.unpack_from("<i", params, 0)[0]
            pos += 4 + 4 * cnt
    info["has_boss_script"] = any(x[1] == "ms_b" for x in ents)
    msn[f.stem] = info

uses_by_mission = collections.defaultdict(list)
for room, kind, prog, mid, name, party in mission_uses:
    uses_by_mission[name].append((room, kind, prog, mid, party))


def flag_names(fl):
    return ",".join(n for b, n in FLAG_BITS if fl & b)


def name_flags(name):
    hits = set()
    for tok in ("SKATE", "GIMMICK", "KINOKO", "TRAP", "MEDAL", "COLOSSEUM", "WORK", "BAGGAGE", "LETTER", "PERFORM", "CLEAN",
                "POSTER", "WORM", "CONFINE", "NAZO", "SWITCH", "SHIP_BATTLE", "WORLDMAP", "AXEL"):
        if tok in name:
            hits.add(tok)
    if "_COL_" in name:
        hits.add("COLOSSEUM")
    if "_FM_" in name:
        hits.add("FM")
    if "_FREE" in name:
        hits.add("FREE")
    if name.endswith("_RE"):
        hits.add("RE")
    return sorted(hits)


mission_rows = []
all_mission_names = sorted(set(msn) | set(uses_by_mission))
for name in all_mission_names:
    info = msn.get(name)
    uses = uses_by_mission.get(name, [])
    rooms_used = sorted({u[0] for u in uses})
    if rooms_used:
        world = rooms_used[0][:2]
    else:
        world = name[:2].lower() if name[:2].lower() in WORLD_ID else "??"
    parties = sorted({u[4] for u in uses if u[4]})
    meters = ""
    fl = ""
    if info and info["ok"]:
        meters = ",".join(f"{k}x{v}" if v > 1 else k for k, v in sorted(info["ops"].items())
                          if k in ("Timer", "Counter", "Gauge", "ComboCounter", "Watch", "MissionScore", "LimitCost", "DriveRefillRatio", "AddDrive"))
        fl = flag_names(info["flags"])
    mission_rows.append(dict(name=name, world=world, id=(hexid(info["id"]) if info and info["ok"] else ""), file=bool(info),
                             rooms=rooms_used, programs=len(uses), parties=parties, flags=fl, meters=meters,
                             nameflags=name_flags(name), pause=(info["pause"] if info and info["ok"] else ""),
                             drive_ratio=(info["drive_ratio"] if info else None), ok=bool(info and info["ok"]),
                             anti=(info["anti"] if info and info["ok"] else "")))
write_csv("missions.csv", ["mission", "world", "id", "has_file", "rooms", "programs", "party_values", "flags", "meters", "name_flags",
                           "pause_menu", "antiform_multiplier", "drive_refill_ratio"],
          [(m["name"], m["world"], m["id"], m["file"], " ".join(m["rooms"]), m["programs"], " ".join(m["parties"]), m["flags"],
            m["meters"], " ".join(m["nameflags"]), m["pause"], m["anti"], m["drive_ratio"]) for m in mission_rows])

# ---------------------------------------------------------------- 5. forms, limits, summons

cmds = yaml_blocks(LC / "cmd.yml")
CMD_FLAGS = [(0x1, "Cursor"), (0x2, "Land"), (0x4, "Force"), (0x8, "Combo"), (0x10, "Battle"), (0x20, "Secure"), (0x40, "Require"),
             (0x80, "NoCombo"), (0x100, "Drive"), (0x200, "Short"), (0x400, "DisableSora"), (0x800, "DisableRoxas"),
             (0x1000, "DisableLionSora"), (0x2000, "DisableLimitForm"), (0x8000, "DisableSkateboard"), (0x10000, "InBattleOnly")]
cmd_by_id = {int(c["Id"]): c for c in cmds}


def cmd_name(cid):
    c = cmd_by_id.get(cid)
    return msg_name(int(c["MessageId"])) if c else ""


def cmd_flags(c):
    v = int(c["Flags"])
    return ",".join(n for b, n in CMD_FLAGS if v & b)


limt = yaml_blocks(LC / "limt.yml")
sumn = yaml_blocks(LC / "sumn.yml")
fmlv = yaml_blocks(LC / "fmlv.yml")
forms_in_fmlv = collections.Counter(x["FinalMixForm"] for x in fmlv)

flag_disable_counts = collections.Counter()
for c in cmds:
    v = int(c["Flags"])
    for b, n in CMD_FLAGS:
        if n.startswith("Disable") and v & b:
            flag_disable_counts[n] += 1

# ---------------------------------------------------------------- write the document

L = []
A = L.append
solo_rooms = sorted(solo_by_room)
markers = sorted(i for i, o in player_objs.items() if (o["flags"] & 1 and o["status"] == 0))
no_stats = sorted(i for i, o in player_objs.items() if i not in markers and o["status"] == 0)
special_forms = sorted(i for i in player_objs if i not in markers and i not in no_stats)
flagged_missions = [m for m in mission_rows if m["nameflags"]]
metered = [m for m in mission_rows if m["meters"]]
nodrive = [m for m in mission_rows if "noDrive" in m["flags"]]
mickey = [m for m in mission_rows if "mickey" in m["flags"].split(",")]

A("# Lane C: the bench list")
A("")
A("Every place in the game's own data where a twin of the player character needs special care.")
A("Made on 2026-11-10 from the extracted original Japanese disc (SLPM-66675), without running the emulator.")
A("")
A("## Summary")
A("")
A(f"- **Rooms:** {len(ROOMS)} room files in {len(WORLDS)} worlds; {programs_total} script programs, {groups_total} spawn groups, "
  f"{ent_total} placed entities.")
A(f"- **Solo places:** {party_counts['NO_FRIEND']} script programs in {len(solo_rooms)} rooms set `Party NO_FRIEND` "
  f"(the player is alone). {programs_with_party} programs set a party value at all; the other "
  f"{programs_total - programs_with_party} do not mention the party.")
A(f"- **Where the player is placed:** {len(spawn_rows)} player placements (PLAYER placeholder, object 0x0236) in "
  f"{len(rooms_with_player_ph)} rooms. {len(no_friend_sp)} of them have no friend placeholder beside them, "
  f"{len(one_friend_sp)} have only one. The data never places two players at once.")
A(f"- **Special player forms:** {len(player_objs)} objects are of type PLAYER: {len(special_forms)} real ones (characters, "
  f"Drive Forms, vehicles and special modes), {len(no_stats)} without player stats and {len(markers)} markers. The party table "
  f"(MEMT) has {len(memt_entries)} rows that choose the player object per world; {len(direct_player)} player objects are also "
  "placed directly by room data.")
A(f"- **Missions:** {len(msn)} mission files, {len(uses_by_mission)} mission names used by room scripts. "
  f"{len(flagged_missions)} are flagged as minigame or special mode by name; {len(metered)} carry a timer, counter or gauge; "
  f"{len(nodrive)} switch Drive off; {len(mickey)} allow the Mickey rescue.")
A("")
A("### What stands out for the twin")
A("")
tt_solo = sum(len(solo_by_room[r]) for r in solo_rooms if r[:2] == "tt")
all_solo_worlds = []
for w in WORLDS:
    sr = [s for s in spawn_rows if s[0][:2] == w]
    if sr and all(s[4] == 0 and s[5] == 0 for s in sr):
        all_solo_worlds.append(f"{w} {WORLD_NAME.get(w, '')} ({len(sr)})")
A(f"1. **The data never puts two players in a room.** Every placement is one PLAYER placeholder, usually with two friend "
  f"placeholders about {round(pct(dists, 0.5))} units away (median). The twin always needs our own placement rule; the friend "
  "spacing is a ready model for it.")
A(f"2. **Solo play is concentrated in Twilight Town:** {tt_solo} of the {party_counts['NO_FRIEND']} `NO_FRIEND` programs are "
  f"there ({sum(1 for r in solo_rooms if r[:2] == 'tt')} rooms). The other worlds have "
  f"{party_counts['NO_FRIEND'] - tt_solo} between them.")
A("3. **Whole worlds have no friend placeholders at all:** " + ", ".join(all_solo_worlds)
  + " (number of placements in brackets). In those worlds nothing in the data ever stands beside the player.")
A("4. **One room uses the real Sora object as the placement:** nm07, group `b_99` (section 3d). A cheap test there shows "
  "how the engine treats a real player object in room data.")
A("5. **The party table carries two size fields per world** (section 3b), possibly memory budgets for player and friends.")
A("6. **Which friends a Drive Form or Summon uses up is not in the data tables** (section 5). It has to be found in the "
  "game program.")
A(f"7. **{len(mickey)} missions allow the Mickey rescue:** " + ", ".join(m["name"] for m in mickey)
  + ". The flag's meaning (\"Mickey spawnable\") is from the OpenKH format notes. HYPOTHESIS: these are the fights where "
  "the game already lets somebody else take over when Sora falls, a ready pattern for \"player 2 saves player 1\".")
A("")
A("Labels: **VERIFIED** = read directly from the file named. **HYPOTHESIS** = my reading of what the data means; "
  "not tested in the game.")
A("")
A("Full lists behind every table: `local\\analysis\\lane-c\\out\\*.csv`. Script: `tools\\lane-c\\mine.py`. "
  "Tool that reads the game files: `tools\\lane-c\\LaneC` (uses the OpenKH libraries).")
A("")

# worlds overview
A("## 0. Worlds overview")
A("")
A("VERIFIED: room files `ard\\*.ard`; world names from the OpenKH source (`Constants.cs`). Room names: the game's place table "
  "(`00place.bin`) gives each room a Japanese name; the system message with that Japanese text was found and the English "
  "text of the same message id is shown. "
  f"{sum(1 for r in ROOMS if room_label(r))} of {len(ROOMS)} rooms get a name this way; the rest are left blank "
  "(rooms past the end of the place table, or rooms whose table name is only a working title).")
A("")
rows = []
for w in WORLDS:
    rs = [r for r in ROOMS if r[:2] == w]
    rows.append((w, WORLD_NAME.get(w, "?"), len(rs), sum(1 for r in rs if r in solo_by_room),
                 sum(len(solo_by_room[r]) for r in rs), sum(1 for s in spawn_rows if s[0][:2] == w),
                 sum(1 for s in no_friend_sp if s[0][:2] == w), sum(1 for m in mission_rows if m["world"] == w)))
A(md_table(["World", "Name", "Rooms", "Rooms with a solo program", "Solo programs", "Player placements",
            "...without friend placeholders", "Missions"], rows))
A("")

# 1 party
A("## 1. Where the game changes the party")
A("")
A("VERIFIED: `Party` commands in the room scripts (`ard\\*.ard`). The six names are the ones the OpenKH script decompiler prints; "
  "a seventh, `DONALD_ONLY`, exists in its list but is never used on this disc.")
A("")
meaning = {"NO_FRIEND": "the player is alone", "DEFAULT": "normal party", "W_FRIEND": "the world's guest can be in the party",
           "W_FRIEND_IN": "the guest is put in the party", "W_FRIEND_FIX": "the guest is in the party and cannot be taken out",
           "W_FRIEND_ONLY": "only the guest fights beside the player"}
rows = []
for k, v in party_counts.most_common():
    kinds = ", ".join(f"{kk} {vv}" for (kk, pp), vv in sorted(party_kind.items()) if pp == k)
    rows.append((f"`{k}`", v, kinds, meaning.get(k, "?")))
A(md_table(["Party value", "Programs", "In which script", "Meaning (HYPOTHESIS, from the name)"], rows))
A("")
A("What this means for a twin: in every `NO_FRIEND` program the original game has one fighter on screen, so the twin has to "
  "be added there by our own rule; nothing in the data places a second character.")
A("")
A("### 1a. Solo programs (`Party NO_FRIEND`) per world")
A("")
A("Program ids are the numbers the room scripts are selected by (the three event ids in memory). "
  "A mission name is shown when the same program starts one.")
A("")
for w in WORLDS:
    rs = [r for r in solo_rooms if r[:2] == w]
    if not rs:
        continue
    A(f"**{w} {WORLD_NAME.get(w, '')}** ({sum(len(solo_by_room[r]) for r in rs)} programs in {len(rs)} rooms)")
    A("")
    rows = []
    for r in rs:
        items = sorted(solo_by_room[r])
        txt = ", ".join(hexid(p) + (f" ({m})" if m else "") for p, m in items)
        rows.append((r, room_label(r), len(items), txt))
    A(md_table(["Room", "Name", "Count", "Programs (mission)"], rows))
    A("")

A("### 1b. The rarer party values")
A("")
for val in ("W_FRIEND_ONLY", "W_FRIEND_FIX", "W_FRIEND_IN"):
    items = [(r, p, m) for r, k, p, pa, m in party_rows if pa == val]
    by_room = collections.defaultdict(list)
    for r, p, m in items:
        by_room[r].append(hexid(p) + (f" ({m})" if m else ""))
    A(f"`{val}` ({len(items)} programs): " + "; ".join(f"{rl(r)}: {', '.join(v)}" for r, v in sorted(by_room.items())))
    A("")
A("### 1c. Other party-related commands")
A("")
sm = collections.Counter(v for _r, _k, _p, v in setmember)
A(f"- VERIFIED: `SetMember` appears {len(setmember)} times in event scripts, with values "
  + ", ".join(f"{k} ({v}x)" for k, v in sorted(sm.items())) + ". The party table has exactly "
  f"{len(memt_index)} line-ups (section 3c), numbered 0 to {len(memt_index) - 1}. HYPOTHESIS: `SetMember n` selects line-up n.")
sm_rooms = collections.defaultdict(set)
for r, _k, _p, v in setmember:
    sm_rooms[v].add(r)
for v in sorted(sm_rooms):
    A(f"  - `SetMember {v}`: " + ", ".join(sorted(sm_rooms[v])))
A(f"- VERIFIED: `SetPartyMenu` appears {sum(setpartymenu.values())} times: "
  + ", ".join(f"value {k} {v}x" for k, v in sorted(setpartymenu.items()))
  + ". HYPOTHESIS: it controls whether the party can be changed in the menu.")
A("")

# 2 placeholders
A("## 2. Where the game places the player and the friends")
A("")
A("VERIFIED: spawn data in `ard\\*.ard`. The player is placed by a placeholder entity, object 0x0236 (model name `PLAYER`); "
  "the two friends by 0x0237 (`FRIEND_1`) and 0x0238 (`FRIEND_2`). The twin test in `docs\\STATE.md` used exactly such a "
  "spawn point (room tt07, group `b_40`).")
A("")
A(f"- {len(spawn_rows)} player placements (PLAYER placeholder entities) exist, in {sp_with_player} spawn points, in "
  f"{len(group_player)} spawn groups, in {len(rooms_with_player_ph)} of {len(ROOMS)} rooms.")
A("- One spawn point often holds several placements, one per way into the room: each placeholder carries an argument "
  "number, and the friend placeholders that belong to it carry the same number (example: room al15, group `m_00`, "
  "arguments 99 and 21). The counts below match friends to the player by that number.")
both = [r for r in spawn_rows if r[4] and r[5]]
A(f"- {len(both)} placements have both friend placeholders, {len(one_friend_sp)} have one, {len(no_friend_sp)} have none.")
if multi_player_sp:
    A(f"- {len(multi_player_sp)} placements share spawn point, type and argument with another PLAYER placeholder: "
      + ", ".join(sorted({f"{r[0]}:{r[1]}[{r[2]}] arg {r[8]}" for r in multi_player_sp})[:20]) + ".")
else:
    A("- No spawn point has two PLAYER placeholders with the same type and argument. So the data never places two "
      "players at once; a twin always needs our own placement rule.")
tcount = collections.Counter((r[7]) for r in spawn_rows)
A("- Spawn type of the player placeholder: " + ", ".join(f"type {k}: {v}" for k, v in sorted(tcount.items()))
  + ". HYPOTHESIS: type 1 with an argument is \"arrive through entrance number N\"; type 0 is a fixed start position "
  "for a fight or an event.")
if dists:
    A(f"- Distance between the player placeholder and a friend placeholder (ground plane, game units, {len(dists)} pairs): "
      f"smallest {round(dists[0])}, median {round(pct(dists, 0.5))}, 90 % below {round(pct(dists, 0.9))}, largest {round(dists[-1])}. "
      "Lane A's twin was placed 150 units beside the player. HYPOTHESIS: the friend placeholders' spacing is a safe model for "
      "placing the twin.")
no_ph_rooms = [r for r in ROOMS if r not in rooms_with_player_ph]
A(f"- {len(no_ph_rooms)} rooms have no PLAYER placeholder at all: " + ", ".join(f"{r}" for r in no_ph_rooms)
  + ". HYPOTHESIS: these are cutscene-only rooms, menus or rooms where the player object is placed another way.")
A("")
A("### 2a. Per world")
A("")
rows = []
for w in WORLDS:
    sr = [s for s in spawn_rows if s[0][:2] == w]
    if not sr:
        continue
    rows.append((w, WORLD_NAME.get(w, ""), len({s[0] for s in sr}), len(sr), sum(1 for s in sr if s[4] and s[5]),
                 sum(1 for s in sr if (s[4] == 0) != (s[5] == 0)), sum(1 for s in sr if s[4] == 0 and s[5] == 0)))
A(md_table(["World", "Name", "Rooms", "Player placements", "With both friends", "With one friend", "With no friend"], rows))
A("")
A("### 2b. How the party value and the placements go together")
A("")
A("VERIFIED: for every script program that sets a party value, the spawn groups that same program loads were checked for "
  "player placements.")
A("")
rows = []
for k, v in sorted(party_vs_place.items(), key=lambda kv: -kv[1][0]):
    rows.append((f"`{k}`", v[0], v[1], v[2], v[3]))
A(md_table(["Party value", "Programs", "...that load a player placement with friend placeholders",
            "...that load a player placement without friends", "...that load no player placement"], rows))
A("")
A("Reading (HYPOTHESIS): a program that loads no player placement keeps the party where the room's entrance placement "
  "(map script) put it.")
A("")
A("### 2c. Player placements with no friend placeholder")
A("")
A("These are the places where the twin has no existing pattern to copy. Written as room (name): group x count. "
  "Full rows: `player_placements.csv`.")
A("")
for w in WORLDS:
    sr = [s for s in no_friend_sp if s[0][:2] == w]
    if not sr:
        continue
    by_room = collections.defaultdict(collections.Counter)
    for s in sr:
        by_room[s[0]][s[1]] += 1
    A(f"**{w} {WORLD_NAME.get(w, '')}** ({len(sr)} placements in {len(by_room)} rooms): "
      + "; ".join(f"{rl(r)}: " + ", ".join(g + (f" x{c}" if c > 1 else "") for g, c in sorted(v.items()))
                  for r, v in sorted(by_room.items())))
    A("")

# 3 player objects
A("## 3. When the player is a different object")
A("")
A("### 3a. All PLAYER-type objects")
A("")
A("VERIFIED: `00objentry.bin` (dump: `local\\analysis\\objentry.txt`). \"Uses\" = how many times a room's spawn data names the "
  "object directly; most player objects are never named in room data because the party table (3b) chooses them.")
A("")
rows = []
for i in sorted(player_objs):
    o = player_objs[i]
    kind = ("marker / placeholder" if i in markers else "special object, no player stats" if i in no_stats
            else "player character, form or vehicle")
    rows.append((f"0x{i:04X}", o["model"], o["anim"], o["form"], o["status"], o["moveset"], kind, len(direct_player.get(i, []))))
A(md_table(["Id", "Model", "Animation set", "Form field", "Status", "Move set", "Kind (HYPOTHESIS)", "Uses in rooms"], rows))
A("")
A("### 3b. The party table: which object is the player, per world")
A("")
A("VERIFIED: `03system.bin`, table `memt` (Final Mix layout, 18 members per row). A row applies to a world, optionally only when "
  "a story flag is set (or not set) or in one area. Empty cells are 0 in the data. HYPOTHESIS: a 0 means \"keep the default "
  "row's value\". Row 0 has world id 0 and is the only row with every member filled. HYPOTHESIS: it is the default for all "
  "worlds. High-poly cutscene models (members 12 to 18) are left out here; they are in `memt.yml`.")
A("")
rows = []
for idx, e in enumerate(memt_entries):
    wcode = codes[e["world"]] if 0 <= e["world"] < len(codes) else str(e["world"])
    m = e["members"]

    def cell(k):
        return oname(m[k]) if k < len(m) and m[k] else ""
    rows.append((idx, "all (default)" if idx == 0 else wcode, e.get("CheckStoryFlag", 0) or "",
                 e.get("CheckStoryFlagNegation", 0) or "", e.get("CheckArea", 0) or "",
                 cell(0), cell(1), cell(2), cell(3), cell(4), cell(5), cell(6), cell(7), cell(8), cell(9), cell(10),
                 e.get("PlayerSize", 0) or "", e.get("FriendSize", 0) or ""))
A(md_table(["Row", "World", "Flag set", "Flag not set", "Area", "Player", "Friend 1", "Friend 2", "World guest", "Valor", "Wisdom",
            "Limit", "Master", "Final", "Anti", "Mickey", "PlayerSize", "FriendSize"], rows))
A("")
sizes = sorted({(e.get("PlayerSize", 0), e.get("FriendSize", 0)) for e in memt_entries if e.get("PlayerSize", 0) or e.get("FriendSize", 0)})
A("The last two columns are fields the table calls `PlayerSize` and `FriendSize` (VERIFIED values: "
  + "; ".join(f"{a:,} / {b:,}" for a, b in sizes)
  + "). HYPOTHESIS: they are memory budgets in bytes for the player's and the friends' data in that world. If so, they are "
  "the first numbers to look at for \"does a second player fit in memory\".")
A("")
A("Reading it for the twin (HYPOTHESIS): the twin must be \"the same object the Player column gives for this world and story "
  "point\", and when a Drive Form is used, the object in that form's column.")
A("")
A("### 3c. Party line-ups in the same table")
A("")
A("VERIFIED: `memt`, second part (member index collection). Numbers are positions in the 18-member row (0 = Sora ... 3 = world "
  "guest); 18 is past the end. HYPOTHESIS: 18 means \"nobody\"; values 67 and 131 are 3 plus a flag bit (64, 128).")
A("")
A(md_table(["Line-up", "Player", "Friend 1", "Friend 2", "World guest slot"], [(i,) + tuple(v) for i, v in enumerate(memt_index)]))
A("")
A("### 3d. Player objects named directly in room data")
A("")
if direct_player:
    rows = []
    for o in sorted(direct_player):
        lst = direct_player[o]
        by_room = collections.defaultdict(list)
        for r, g in lst:
            by_room[r].append(g)
        ms = set()
        for r, g in lst:
            for e in rooms[r]:
                if e["type"] == "AreaDataScript":
                    for p in e["programs"]:
                        if g in p.get("spawns", []):
                            ms.update(p.get("missions", []))
        rows.append((f"0x{o:04X}", oname(o), len(lst),
                     "; ".join(f"{rl(r)}: {', '.join(sorted(set(g)))}" for r, g in sorted(by_room.items())),
                     ", ".join(sorted(ms)) or "-"))
    A("VERIFIED: spawn entities in `ard\\*.ard` whose object is of type PLAYER (other than the 0x0236 placeholder), and the "
      "missions named by the script programs that load those groups.")
    A("")
    A(md_table(["Id", "Model", "Entities", "Room: spawn groups", "Missions of the programs that load them"], rows))
    A("")
    A("Worth a test by the other lanes: **nm07, group `b_99`** (loaded by battle program 0x47, mission `NM07_MS204`, "
      "`Party W_FRIEND`). VERIFIED: this group holds the real Sora object 0x0054 together with the two friend placeholders "
      "and four boss objects, and no PLAYER placeholder. So the game's own data uses a real PLAYER-type object where "
      "every other room uses the placeholder. HYPOTHESIS: either the engine treats it as the player's start position, or a "
      "second Sora appears in that fight; which one it is tells how the engine decides between \"this is the player\" and "
      "\"spawn another one\".")
    A("")
    A("The vehicle and special-mode objects (carpet, light cycle, sidecar, `PO06_PLAYER`, `AL14_PLAYER`) are placed the "
      "same direct way, each in its own minigame room. A twin there needs a second copy of that object.")
else:
    A("VERIFIED: no room places a real PLAYER-type object directly; only the placeholder is used.")
A("")
A(f"Also VERIFIED: {sum(friend_direct.values())} spawn entities name a real FRIEND-type object directly "
  f"({len(friend_direct)} different objects), besides the two friend placeholders.")
A("")

# 4 missions
A("## 4. Missions")
A("")
A(f"VERIFIED: `msn\\jp\\*.bar` ({len(msn)} files; header and op-codes read as described in the OpenKH format notes) and the "
  f"`Mission` commands in the room scripts ({cmd_words['Mission']} commands, {len(uses_by_mission)} different names).")
A("")
only_file = [m["name"] for m in mission_rows if m["file"] and not m["programs"]]
only_ard = [m["name"] for m in mission_rows if not m["file"]]
bad_hdr = [m["name"] for m in mission_rows if m["file"] and not m["ok"]]
A(f"- Mission files that no room script names: {len(only_file)}" + (": " + ", ".join(only_file) if only_file else "") + ".")
A(f"- Mission names in room scripts with no file: {len(only_ard)}" + (": " + ", ".join(only_ard) if only_ard else "") + ".")
if bad_hdr:
    A(f"- Files whose header could not be read: {len(bad_hdr)}: " + ", ".join(bad_hdr) + ".")
id_ok = id_bad = 0
for name, uses in uses_by_mission.items():
    info = msn.get(name)
    if info and info["ok"]:
        for u in uses:
            if u[3] == info["id"]:
                id_ok += 1
            else:
                id_bad += 1
A(f"- Cross-check: the id written in the room script equals the id in the mission file's header in {id_ok} of "
  f"{id_ok + id_bad} uses.")
A("- Name flags are read from the file name only. KINOKO is the Japanese word for mushroom; FM marks names containing "
  "`_FM_`; FREE and RE mark `_FREE` and `_RE` variants; COLOSSEUM also covers `HE_COL_` names.")
A("")
A("Columns: **Flags** are the mission header bits (boss, noDrive = Drive switched off, noLeave, mickey = Mickey rescue allowed, "
  "noExp, noMagic, retry, freeSummon, noSummon, place, showWeapon, noPrize, noPrizebox, hideMap). **Meters** are on-screen "
  "counters the mission defines. **Name flag** = the name looks like a minigame or special mode "
  "(this is only a reading of the name: HYPOTHESIS). **Party** = party value set by the programs that start it.")
A("")
tok_counts = collections.Counter(t for m in mission_rows for t in m["nameflags"])
A("Name flags used: " + ", ".join(f"{k} ({v})" for k, v in tok_counts.most_common()) + ".")
A("")
order = WORLDS + [w for w in sorted({m["world"] for m in mission_rows}) if w not in WORLDS]
for w in order:
    ms = [m for m in mission_rows if m["world"] == w]
    if not ms:
        continue
    A(f"**{w} {WORLD_NAME.get(w, '(world not determined)')}** ({len(ms)} missions, {sum(1 for m in ms if m['nameflags'])} flagged by name)")
    A("")
    rows = []
    for m in ms:
        rows.append((m["name"], m["id"], " ".join(m["rooms"]) or "-", m["programs"], " ".join(m["parties"]) or "-", m["flags"] or "-",
                     m["meters"] or "-", " ".join(m["nameflags"]) or "-"))
    A(md_table(["Mission", "Id", "Rooms", "Programs", "Party", "Flags", "Meters", "Name flag"], rows))
    A("")

# 5 forms limits summons
A("## 5. Drive Forms, Limits and Summons")
A("")
A("### 5a. Drive Forms")
A("")
A("VERIFIED: `03system.bin`, table `cmd` (command list), entries with the Form icon; names looked up by message id in the "
  "English pack. `Argument` is the form number.")
A("")
rows = []
for c in cmds:
    if c.get("CmdIcon") == "Form":
        rows.append((c["Id"], msg_name(int(c["MessageId"])) or "?", c["Argument"], c["Cost"], cmd_flags(c), c["DisableForm"]))
A(md_table(["Command id", "Name", "Argument", "Cost", "Flags", "DisableForm mask"], rows))
A("")
A("- **Could not be read from the data:** which friends a form uses up. No field of the command table names Donald or Goofy, "
  "and `fmlv` (form levels) only lists experience and abilities per form "
  f"(rows per form: {', '.join(f'{k} {v}' for k, v in sorted(forms_in_fmlv.items()))}). "
  "HYPOTHESIS: the friend requirement is in the game program, not in these tables. Lanes that test Drive Forms must find it there.")
A(f"- VERIFIED: the party table (3b) gives a separate object for every form in every world row, so a twin in a form needs "
  "that object too (memory: see the plan's risk about two forms at once).")
A(f"- VERIFIED: {len(nodrive)} missions have the \"Drive disabled\" bit: " + ", ".join(m["name"] for m in nodrive) + ".")
dr = [m for m in mission_rows if m["drive_ratio"] is not None]
A(f"- VERIFIED: {len(dr)} missions set a Drive refill ratio: " + ", ".join(f"{m['name']} ({m['drive_ratio']})" for m in dr)
  + ". The OpenKH notes say this op-code also decides whether Sora can use the other forms when alone (not checked here).")
A("- VERIFIED: command flags exist that switch a command off for one kind of player: "
  + ", ".join(f"{k} on {v} commands" for k, v in sorted(flag_disable_counts.items()))
  + ". So Roxas, lion Sora, Limit Form and the skateboard already have their own allowed command sets in data; "
  "a twin of those inherits the same limits.")
A("")
A("### 5b. Limits")
A("")
A("VERIFIED: `00battle.bin`, table `limt`. `Character` is who the limit belongs to and `Summon` the partner the table names "
  "(the field names are OpenKH's). World 13 rows are the Timeless River versions.")
A("")
rows = []
for x in limt:
    rows.append((x["Id"], x["Character"], x["Summon"], x["Group"], x["FileName"], x["Command"], cmd_name(int(x["Command"])) or "?",
                 x["World"]))
A(md_table(["Id", "Character", "Partner field", "Group", "File", "Command", "Command name", "World"], rows))
A("")
A("HYPOTHESIS: every limit pairs exactly two named characters (Sora plus one partner; Trinity names Donald and has group 3). "
  "With two players, the data gives no rule for which player is the \"Sora\" of a limit; that is our design choice "
  "(the user decided: either player can start one).")
lc = [m for m in mission_rows if "LimitCost" in m["meters"]]
A(f"VERIFIED: {len(lc)} missions set their own limit cost: " + ", ".join(m["name"] for m in lc) + ".")
A("")
A("### 5c. Summons")
A("")
A("VERIFIED: `00battle.bin`, table `sumn`, and the Summon-icon commands in `cmd`.")
A("")
rows = []
for x in sumn:
    e1, e2 = int(x["Entity1"]), int(x["Entity2"])
    rows.append((x["Command"], cmd_name(int(x["Command"])) or "?", x["Item"], oname(e1) if e1 else "-", oname(e2) if e2 else "-",
                 x["LimitCommand"], cmd_name(int(x["LimitCommand"])) or "?"))
A(md_table(["Command", "Name", "Item", "Entity 1", "Entity 2", "Limit command", "Limit name"], rows))
A("")
fs = [m for m in mission_rows if "freeSummon" in m["flags"]]
ns = [m for m in mission_rows if "noSummon" in m["flags"].split(",")]
A(f"VERIFIED: {len(ns)} missions have \"Summon disabled\"; {len(fs)} have \"free summon (summon alone)\""
  + (": " + ", ".join(m["name"] for m in fs) if fs else "") + ".")
A("**Could not be read:** which friends a summon replaces. HYPOTHESIS: also in the game program.")
A("")
A("### 5d. Friend commands")
A("")
rows = [(c["Id"], msg_name(int(c["MessageId"])) or "?", c["Argument"], cmd_flags(c)) for c in cmds if c.get("CmdIcon") == "Friend"]
A("VERIFIED: commands with the Friend icon in `cmd` (the party-swap menu).")
A("")
A(md_table(["Command id", "Name", "Argument", "Flags"], rows))
A("")

# 6 other
A("## 6. Other data that singles out \"the player\"")
A("")
A("Counts only; each is something a second player has to share or trigger too.")
A("")
rows = [
    ("Entities with a non-zero `ReactionCommand` field", rc_entities,
     f"{len(rc_values)} different values; by object type: " + ", ".join(f"{k} {v}" for k, v in rc_types.most_common()),
     "HYPOTHESIS: an individual id (which talk text, which chest), i.e. the things a player presses Triangle on; "
     "player 2 must be able to use them too"),
    ("Event activators (trigger volumes)", act_total,
     ", ".join(f"type {k}: {v}" for k, v in act_types.most_common(2))
     + f", {len(act_types) - 2} other types: {act_total - sum(v for _k, v in act_types.most_common(2))}",
     "room exits, event starts: the \"both players at the exit\" rule lives here"),
    ("Spawn points with a teleport target", sp_tele, f"of {sp_total} spawn points", "where a room change sends the party"),
    ("`SetJump` commands", cmd_words["SetJump"], "event scripts", "scripted room changes after events"),
    ("`SetEvent` commands", cmd_words["SetEvent"], "event scripts", "cutscene starts; the twin must be hidden or placed"),
    ("`Mission` commands", cmd_words["Mission"], "battle scripts", "mission rules apply to both players"),
    ("`Capacity` commands", cmd_words["Capacity"], "", "HYPOTHESIS: memory budget for a room; a twin adds load"),
    ("`Camera` commands", cmd_words["Camera"], "", "fixed or special cameras"),
    ("`BarrierFlag` commands", cmd_words["BarrierFlag"], "", "HYPOTHESIS: battle walls that lock the room"),
    ("`MsgWall` commands", cmd_words["MsgWall"], "", "invisible walls with a message"),
    ("`SetInventory` commands", cmd_words["SetInventory"], "", "items given or taken by script"),
    ("`SetMenuFlag` commands", cmd_words["SetMenuFlag"], "", "menu parts switched on or off"),
    ("Walk paths / return parameters / signals", f"{walk_total} / {ret_total} / {sig_total}", "spawn data", "enemy and NPC behaviour hooks"),
]
A(md_table(["What", "Count", "Detail", "Why it matters for two players"], rows))
A("")
A("VERIFIED counts from `ard\\*.ard`; the \"why\" column is my reading (HYPOTHESIS) unless marked otherwise.")
A("")

# 7 limits
A("## 7. What this list cannot tell")
A("")
bad = [(r, e["name"]) for r in ROOMS for e in rooms[r] if e["bad"]]
A(f"- {len(bad)} script or spawn entries could not be decoded by the OpenKH reader and are not counted: "
  + ", ".join(f"{r}:{n}" for r, n in bad) + ".")
A("- Which program runs when: the scripts are selected by story progress in memory. This list shows every program that "
  "exists, not the order the story uses them.")
A("- Anything decided inside the game program instead of data: who a Drive Form or Summon uses up, how enemies choose a "
  "target, what the camera follows. Those belong to lanes A and B.")
A("- Meanings marked HYPOTHESIS come from field and command names, not from tests.")
A("- Text for room names and commands comes from the English pack; the ids come from the Japanese disc.")
A("")

DOC.parent.mkdir(parents=True, exist_ok=True)
DOC.write_text("\n".join(L) + "\n", encoding="utf-8")

print("rooms", len(ROOMS), "worlds", len(WORLDS), "programs", programs_total, "with party", programs_with_party)
print("party", dict(party_counts))
print("solo rooms", len(solo_rooms), "solo programs", party_counts["NO_FRIEND"])
print("player spawn points", len(spawn_rows), "rooms", len(rooms_with_player_ph), "no friend", len(no_friend_sp), "one friend",
      len(one_friend_sp), "multi player", len(multi_player_sp))
print("player objects", len(player_objs), "forms/characters", len(special_forms), "markers", len(markers), "memt rows", len(memt_entries))
print("missions files", len(msn), "names in ard", len(uses_by_mission), "flagged by name", len(flagged_missions), "metered", len(metered),
      "noDrive", len(nodrive), "mickey", len(mickey), "bad headers", len(bad_hdr))
print("direct player objs", {hex(k): len(v) for k, v in direct_player.items()})
print("room names:", dict(place_how), "rooms without a name:", [r for r in ROOMS if not room_label(r)])
print("doc", DOC, DOC.stat().st_size, "bytes")
