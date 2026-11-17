"""Lane P: build docs/PARITY-CHECKLIST.md and docs/PARITY-CHECKLIST.csv from rows.py and the collected data facts.

  python -I tools/lane-p/build_checklist.py
"""
import collections
import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import rows as RW  # noqa: E402

AN = ROOT / "local" / "analysis" / "lane-p"
facts = json.loads((AN / "mission_facts.json").read_text(encoding="utf-8"))
all_missions = [r["mission"] for r in csv.DictReader(open(ROOT / "local" / "analysis" / "lane-c" / "out" / "missions.csv", encoding="utf-8"))]

JNAME = {"BASE": "works with the base (to confirm)", "OBJECT": "needs a second special object", "ADAPT": "needs real adaptation", "UNKNOWN": "not known"}
EVTXT = {"V": "VERIFIED: wording restates the game data named in the data-facts column.",
         "V+M": "Data facts VERIFIED (mission file, room scripts, spawn data, text). Description beyond them: FROM MEMORY, TO CONFIRM IN PLAY.",
         "M": "FROM MEMORY, TO CONFIRM IN PLAY (the data gives only what the data-facts column shows)."}


def data_facts(names):
    out = []
    for n in names:
        o = facts.get(n)
        if not o:
            out.append(f"{n}: no entry in the mission list")
            continue
        parts = []
        txt = o["info_text"]
        if o["pause_text"] and o["pause_text"] != o["info_text"]:
            txt = (txt + " / " if txt else "") + o["pause_text"]
        parts.append(f'text "{txt}"' if txt else "no objective text" if o["has_file"] else "no mission file")
        if o["flags"]:
            parts.append("flags " + o["flags"])
        if o["party"]:
            parts.append("party " + o["party"])
        if o["meters"]:
            parts.append("meters " + o["meters"])
        ob = o["objects"]
        boss = sorted(list(ob.get("BOSS", {})) + list(ob.get("L_BOSS", {})))
        if boss:
            parts.append("boss objects " + ", ".join(boss))
        ply = [k for k in sorted(ob.get("PLAYER", {})) if k != "PLAYER"]
        if ply:
            parts.append("player object placed directly: " + ", ".join(ply))
        helpers = sorted(list(ob.get("BTLNPC", {})) + [k for k in ob.get("MINIGAME", {}) if "PRIZE" not in k and "_F_" not in k])
        if helpers:
            parts.append("helper / minigame objects " + ", ".join(helpers[:8]))
        if o["room_names"]:
            parts.append("rooms " + "; ".join(o["room_names"]))
        out.append(f"{n} [{o['id'] or 'no id'}]: " + "; ".join(parts))
    return " || ".join(out)


rows = []
for r in RW.ROWS:
    d = dict(RW.DEF[r["kind"]])
    d.update(r)
    d["facts"] = data_facts(d["missions"]) if d["missions"] else "No mission file: facts are in the row itself (object list, party table, room data, text files)."
    d.setdefault("note", "")
    rows.append(d)

# ---------------------------------------------------------------- coverage
used = collections.Counter(m for d in rows for m in d["missions"])
missing = [m for m in all_missions if m not in used]
extra = [m for m in used if m not in all_missions]
dupes = [m for m, n in used.items() if n > 1]
print("rows:", len(rows), "| missions in the data:", len(all_missions), "| covered:", len(all_missions) - len(missing))
print("missing:", missing)
print("not in the data:", extra, "| used twice:", dupes)

# ---------------------------------------------------------------- CSV
cols = ["id", "world", "sequence", "mission_files", "original_mechanic", "p1_can", "p2_must", "separate_object_vehicle_state_interaction",
        "adaptation", "verify_with_two_human_players", "judgment", "evidence", "data_facts", "phase", "feasibility_test", "note",
        "checked_with_two_players", "date_checked"]
with open(ROOT / "docs" / "PARITY-CHECKLIST.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for d in rows:
        w.writerow([d["id"], d["group"], d["title"], " ".join(d["missions"]), d["mech"], d["p1"], d["p2"], d["sep"], d["adapt"], d["verify"],
                    JNAME[d["judg"]], EVTXT[d["ev"]], d["facts"], d["phase"], d["test"], d["note"], "", ""])

# ---------------------------------------------------------------- command table
OWN = {}


def own(names, who):
    for n in names.split("|"):
        OWN[n.strip()] = who


own("Talk", "people in the field")
own("Examine|Examine The Book|Examine The Wall|Examine The Table|Investigate|Touch It|Look Up", "objects in the field")
own("Open|Open The Door", "chests and doors")
own("Save", "save points")
own("Shop|Synthesize", "shops and the Moogle")
own("Enter The Book|Leave The Book|Read The Book", "Pooh's book")
own("Depart|Warp|Proceed|Land", "exits, warps and the world map")
own("Access Computer|Enter Password|Access|Turn On", "computer terminals")
own("Reversal", "Dusk; also boss duels")
own("Full Swing", "Large Body type Heartless")
own("Snag|Sparkle Ray", "Surveillance Robot")
own("Cyclone", "Soldier")
own("Bat Cry", "Hook Bat")
own("Lance Tug", "Lance Soldier")
own("Rising Sun", "Armored Knight")
own("Dodge Roll", "Minute Bomb")
own("Bolt Reversal", "Bolt Tower")
own("Air Twister", "Air Pirate")
own("Rapid Blow", "Aerial Knocker")
own("Clear Shot", "Fortuneteller")
own("Shift Shot", "Silver Rock")
own("Root Ravager", "Creeper Plant")
own("Heal Stomp", "Crescendo")
own("Tornado Ride", "Tornado Step")
own("Quick Blade", "Magnum Loader")
own("Speed Trap|Aero Blade", "Rapid Thruster")
own("Rodeo|Grand Cross", "Living Bone")
own("Capsule Prize|Rare Capsule|Limited Capsule|Prime Capsule", "Bulky Vendor")
own("Duel Stance|The End", "Samurai; Roxas")
own("Learn|Jump", "Dragoon; Xaldin")
own("Fail-Safe", "Assassin")
own("Berserk|Eclipse|Magna Storm", "Berserker; Saix")
own("Warp Snipe", "Sniper; Xigbar")
own("Begin Game|Stop Dice", "Gambler; Luxord")
own("Key Counter|Lunarsault|Break Raid", "Twilight Thorn")
own("Evade|Jump!|Dog Paddle", "Cerberus")
own("Vanquish|Urninator|Pegasus Run|Phil One-Two", "Hydra")
own("Pinball", "Pete")
own("Release", "Thresholder and Possessor; gargoyles")
own("Step Vault|Catch|Pendulum Round|Slingshot", "Dark Thorn")
own("Wake Up!|Get Up!|Charge", "the Beast fight with Cogsworth; also the MCP")
own("Press|Takedown", "Shan-Yu")
own("Slide|Vertigo Toss", "Storm Rider")
own("Fore!", "Oogie Boogie")
own("Inside Combo", "Prison Keeper")
own("Capture", "Lock, Shock and Barrel")
own("Hinder|Loot Launch", "Grim Reaper")
own("Firagun|Blizzagun", "Volcanic Lord and Blizzard Lord")
own("Roll Up|Spin Burst", "Jafar (genie form)")
own("Freeze", "Space Paranoids: monitors and the Hostile Program")
own("Delete|Needle Dive", "the MCP fight")
own("Zone Guard|Disc Strike", "Sark")
own("Wild Dance|Show Stealer", "Demyx")
own("Facedown|Clash|Break Through|Finish|Riding Shot|Meteor Rain|Slicer|Sky Scraper|Stunt Dodge|Reflect", "the Xemnas fights")
own("Block", "Sephiroth")
own("Heelflip|Pop-Jump|360° Spin|Method Grab|Air Walk|Handstand|Grind|Hop On|Get Off", "the skateboard")
own("Musical", "Atlantica's musical")
own("Go, Abu!|Set the jewel!", "Abu in the Cave of Wonders")
own("Call Over|Faith", "Queen Minnie's escort")
own("Post", "job: Poster Duty")
own("Deliver", "job: Mail Delivery")
own("Light", "lanterns in Beast's Castle")
own("Push", "the wardrobe in Beast's Castle")
own("Struggle", "Struggle matches")
own("Enter Tournament|Go To The Tournament|Train|Learn The Rules", "Olympus: cups and training")
own("Twin Howl|Stalwart Fang|Outcry|Last Howl", "Limit with Beast")
own("Bushido|Shooting Star|Banishing Blade|Spiral", "Limit with Auron")
own("Red Rocket|Flametongue|Heat Lance|Red Meteor", "Limit with Mulan")
own("Whirli-Goof|Whirli-Goofra|Whirli-Goofga|Knocksmash|Duo Raid|Cosmo Boost", "Limits with Goofy")
own("Comet|Comet Rain|Duck Flare|Rocket Flare|Megaduck Flare", "Limits with Donald")
own("Speedster|Quickplay|Trickster", "Limit with Aladdin")
own("Bluff|Slasher|Jackknife|Final Trap", "Limit with Jack Sparrow")
own("Wildcat|High Fang|X-Claw|Proud Roar", "Limit with Simba")
own("Dance Call|Downbeat|Synchronization|Finale", "Limit with Jack Skellington")
own("Setup|Cluster Code|Burst Pulse|Reprogram", "Limit with Tron")
own("Session|Last Saber|Dark Cannon|{XIII} Blades|Master Hearts|All's End", "Limit with Riku")
own("Trinity|Break|Ultima|Major Drive|Begin Combo", "Trinity Limit")
own("Never Land|The Flying Boy|Tiny Fairy|Journey's End", "summon: Peter Pan")
own("Ohana!|Ukulele|Blast", "summon: Stitch")
own("FPS Mode|Balls|Firecracker|End", "summon: Chicken Little")
own("Sonic|Rave|Strike|Judgment|Arcana|Bash|Ragnarok|Impact|Valor Genie|Wisdom Genie|Master Genie|Final Genie", "summon: Genie")
own("Sonic Blade|Ars Arcanum|Strike Raid|Raid|Giga Impact|Mega Impact", "Limit Form")

cmd_rows = list(csv.DictReader(open(AN / "commands.tsv", encoding="utf-8"), delimiter="\t"))
names = collections.OrderedDict()
for c in cmd_rows:
    if c["icon"] != "Null":
        continue
    n = (c["name"] or "").replace("´", "'").strip()
    if n in ("", "-"):
        continue
    names.setdefault(n, []).append(c["id"])
known = [(n, ids, OWN[n]) for n, ids in names.items() if n in OWN]
unknown = [(n, ids) for n, ids in names.items() if n not in OWN]
blank = sum(1 for c in cmd_rows if c["icon"] == "Null" and (c["name"] or "-") == "-")

# ---------------------------------------------------------------- markdown
cnt = collections.Counter(d["judg"] for d in rows)
A = []
w = A.append


def cell(s):
    return str(s).replace("|", "/").replace("\n", " ")


w("# Parity checklist: every world, mission, minigame, special sequence and boss, for two players")
w("")
w("Written 2026-11-10 by lane P for the user's requirement `docs/REQUIREMENT-full-parity.md` (plan section 4B, Phase 3A).")
w("This is the audit that comes BEFORE any special sequence is implemented. It does not design solutions and does not")
w("promise that anything is possible. The same rows are in `docs/PARITY-CHECKLIST.csv`, with two empty columns to tick")
w("later (`checked_with_two_players`, `date_checked`) and one more column, `data_facts`, holding what the game data")
w("says about every mission file of the row.")
w("")
w("**How to read the labels**")
w("")
w("- **Judgment** (a first sorting, not a result): **BASE** = nothing in the data says more than the base is needed")
w("  (the twin from a second PLAYER placeholder, own controller, own HP and MP, own commands, exits for two), to be")
w("  confirmed; **OBJECT** = needs a second special object, vehicle or character state; **ADAPT** = the sequence")
w("  itself was built for one and must be adapted; **UNKNOWN** = not known.")
w("- **Ev** (evidence): **V** = the wording only restates game data; **V+M** = the data facts are VERIFIED, the")
w("  description beyond them is FROM MEMORY, TO CONFIRM IN PLAY; **M** = FROM MEMORY, TO CONFIRM IN PLAY.")
w("  Data means: the 303 mission files and their objective texts, the room scripts and spawn data of all 289 rooms,")
w("  the object list, the party table, the command table and the English text (lane C's lists and")
w("  `local/analysis/lane-p/`).")
w("- **Phase** = the plan phase that should own the row.")
w("- 'Base open items' used in many rows (from lanes D, E, G): enemies attack only the hero the engine holds as its")
w("  player; either hero at 0 HP gives Game Over; no prompt, menu or gauge is drawn for player 2; START and all menus")
w("  listen to controller 1; items, Drive, Limits and Summons through player 2 are untested.")
w("")
w("## 1. Summary")
w("")
w(f"- **Rows: {len(rows)}.** They cover all {len(all_missions)} mission names in the game data ({len(all_missions) - len(missing)} placed in a row"
  + (f", {len(missing)} missing: {', '.join(missing)}" if missing else "") + "), plus the sequences that have no mission")
w("  file (Gummi routes, the world map, lion and merman movement, the wood, puzzle pieces) and 14 game-wide mechanics.")
for j in ("BASE", "OBJECT", "ADAPT", "UNKNOWN"):
    w(f"- **{j}** ({JNAME[j]}): **{cnt[j]}** rows.")
w("")
w("**Special modes that need a second vehicle or object** (OBJECT rows):")
w("")
for d in rows:
    if d["judg"] == "OBJECT":
        w(f"- {d['id']} {d['title']}")
w("")
w("In short: a second **Magic Carpet** (two rows here, and the carpet escape run under ADAPT; lane J found that")
w("copying the carpet-Sora object gives a second Sora but not a second carpet), a second **Light Cycle** (a copy does")
w("appear, lane J), a second **toy cannon** for Gift Wrapping (a copy does appear, lane J), and a second")
w("**skateboard** (six rows; the board object is not identified yet).")
w("")
w("Special player objects found in the data (VERIFIED: object list, party table, room data; lanes C and J):")
w("")
w("- placed directly in room data: P_EX100_AL_CARPET (rooms al05 and al14, 14 placements), AL14_PLAYER (al14),")
w("  P_EX100_TR_LIGHTCYCLE (tr02, 2), P_EX100_SIDECAR (eh22), PO06_PLAYER (po06, 2), F_NM180 the toy cannon (nm10),")
w("  and once the real Sora object (nm07): 21 special-mode placements in 6 rooms;")
w("- stand-ins of another object type in two Pooh games: PO07_PLAYER (po07) and PO08_PLAYER (po08);")
w("- never placed in room data, so created by the fight itself: M_EX950_CARD and M_EX950_DICE (Luxord);")
w("- chosen by the party table per world: Roxas (P_EX110, P_EX110_BTLF, P_EX120), the lion P_LK100, the merman")
w("  P_LM100, the costumes P_EX100_NM / P_EX100_XM, the Tron suit P_EX100_TR, Timeless River P_EX100_WI, every Drive")
w("  Form of each of those, and King Mickey (P_EX200, P_EX220).")
w("")
w("**Sequences that must themselves be adapted for two** (ADAPT rows):")
w("")
for d in rows:
    if d["judg"] == "ADAPT":
        w(f"- {d['id']} {d['title']}")
w("")
w("**Not known** (UNKNOWN rows):")
w("")
for d in rows:
    if d["judg"] == "UNKNOWN":
        w(f"- {d['id']} {d['title']}")
w("")
w("**The biggest unknowns**")
w("")
w("1. **The Gummi Ship mode.** Nothing about it has been examined: how it reads the controller, its camera, its")
w("   scoring. It has escort 'Teeny Ships', a possible second ship, but that is only a lead.")
w("2. **Script-module minigames.** Five sequences have their own script module (`minigame/al_14.bar`, `eh_22.bar`,")
w("   `po_06.bar`, `po_07.bar`, `po_08.bar`): the carpet escape, the dragon shooter and three Pooh games. Each is")
w("   built around one special player object. Lane J: a second flyer appears in po06; in the dragon shooter the")
w("   second Sora has no vehicle; the carpet escape could not even be started on a test disc.")
w("3. **Reaction Commands that carry the hero** (Twilight Thorn, Cerberus, Hydra, Dark Thorn, Storm Rider,")
w("   Groundshaker, the first Xemnas fight, the building chase, the bag on Sunset Hill). Not known whether two heroes")
w("   can be attached at once.")
w("4. **Per-Sora boss states**: Luxord's time gauges and card/dice forms, Marluxia's count, Vexen's data copy,")
w("   Zexion's book, Roxas taking the Keyblade, the final Xemnas rescue, the Lingering Will's seals.")
w("5. **Score rules for two**: Struggle orbs, the Titan Cup point pool, skateboard and job scores, the musical.")
w("6. **Drive Forms, Limits and Summons for two heroes** (two friends to fuse with; which friends a form uses is not")
w("   in the data tables).")
w("7. **Nothing in any special mode is tested beyond 'does a second copy appear'** (lane J). Independent control,")
w("   scoring, win and lose rules and enemy targeting in those modes are all open.")
w("")
w("## 2. Recommended order of the feasibility tests")
w("")
w("Story order; inside a world the cheapest test first. Each is a short experiment in the style of the twin test:")
w("build a jump disc, run it with the merged patch, look, write down. None of them is a promise.")
w("")
ORDER = [
    ("Base, before everything", "Merged build (lane M): own controller, own HP, own commands, exits, twin everywhere, all in one test run. GW-07 (magic drains own MP), GW-01 (P2 uses one enemy Reaction Command), GW-10 (only P2 falls)."),
    ("Twilight Town, Roxas", "TTR-09 Struggle: only pad 2 collects orbs, read both counters (also answers TTS-06). Then the job counters TTR-04 to TTR-08 the same way. Then TTR-03 / TTS-07 skateboard: both press Hop On at one board; find the board object and place a second. Then TTR-13 the bag and TTR-15 Twilight Thorn: both pads press Triangle in the same window."),
    ("Hollow Bastion", "HB-05 Demyx and HB-07 the 1000 Heartless: does the kill counter count P2's kills? HB-08 Sephiroth: does his single-target attack ever pick the twin?"),
    ("Land of Dragons, Beast's Castle", "MU-09 Storm Rider and BB-07 Dark Thorn: the first 'carried by a Reaction Command' tests with a party present. BB-09 Xaldin: does P2 get an own Learn stock?"),
    ("Olympus", "HE-01 Cerberus (Auron only) and HE-06 Hydra (Pegasus ride). Then HEC-03 Titan Cup: let each hero be hit once and read the point pool; HEC-02 Cerberus Cup: Drive 'alone' for each hero (needs GW-04 first)."),
    ("Disney Castle, Timeless River, Port Royal", "DC-01: P2 calls Minnie. CA-08: watch one ship ambush with two heroes to learn what it is."),
    ("Agrabah", "AL-06: repeat lane J's carpet test with the helper object copied too, to find what makes a carpet; only then AL-08. AL-07 needs a start played in from the story, because a jump disc shows a black screen (lane J)."),
    ("Halloween Town", "NM-07 Gift Wrapping: lane J's two-cannon disc with the merged patch: does the second cannon aim and fire on pad 2?"),
    ("Pride Lands", "LK-05 Groundshaker: both lions press the climb command."),
    ("Space Paranoids", "TR-03 Light Cycle: lane J's two-cycle disc with the merged patch: does each cycle follow its own controller? TR-08: can both hold Delete?"),
    ("The World That Never Was", "EH-03 Luxord: watch the two time gauges when each hero is hit; let each be turned into a die. EH-01 Roxas: P2 answers the duel command. EH-09 the dragon: find what makes the bike. EH-11: let Xemnas catch each hero in turn."),
    ("100 Acre Wood", "PO-01: lane J's two-flyer disc with the merged patch (own controller?). Then PO-02 and PO-03 with a second PO07_PLAYER / PO08_PLAYER placed. PO-05: just watch it with a twin."),
    ("Atlantica", "LM-01: in one song press only on pad 2: does the game accept it at all?"),
    ("Gummi Ship", "GM-01: find where the Gummi mode reads the controller (the method lane A used for the player), then try giving a Teeny Ship to pad 2. This is a study of its own."),
    ("Game-wide, in parallel", "GW-04 Drive Forms: each pad selects Valor in turn with Donald and Goofy present; then GW-05 one Limit per player, GW-06 one summon per player."),
    ("Final Mix extras, last", "FM-06 Marluxia (whose count falls), FM-02 Vexen (whose data fills the gauge), FM-04 Zexion (who is trapped), FM-08 the Lingering Will; the mushrooms' counters with the job-counter result in hand."),
]
for i, (where, what) in enumerate(ORDER, 1):
    w(f"{i}. **{where}.** {what}")
w("")
w("## 3. The checklist, world by world")
w("")
HEAD = ["ID", "Sequence (mission files)", "Original mechanic", "What P1 can do", "What P2 must be able to do",
        "Separate object, vehicle, state or interaction", "Adaptation needed", "Check with two human players", "Judgment", "Ev", "Phase", "Feasibility test"]
groups = collections.OrderedDict()
for d in rows:
    groups.setdefault(d["group"], []).append(d)


def table(ds):
    w("| " + " | ".join(HEAD) + " |")
    w("|" + "---|" * len(HEAD))
    for d in ds:
        ms = d["missions"]
        mtxt = (" (" + ", ".join(ms[:6]) + (f" and {len(ms) - 6} more" if len(ms) > 6 else "") + ")") if ms else ""
        w("| " + " | ".join(cell(x) for x in [d["id"], d["title"] + mtxt, d["mech"], d["p1"], d["p2"], d["sep"],
                                                d["adapt"] + (" " + d["note"] if d["note"] else ""), d["verify"], d["judg"], d["ev"], d["phase"], d["test"]]) + " |")
    w("")


def texts(ds):
    lines = []
    for d in ds:
        for m in d["missions"]:
            o = facts.get(m)
            if not o:
                continue
            t = o["info_text"] or o["pause_text"]
            extra = []
            ob = o["objects"]
            boss = sorted(list(ob.get("BOSS", {})) + list(ob.get("L_BOSS", {})))
            if boss:
                extra.append("boss objects " + ", ".join(boss[:6]) + (" ..." if len(boss) > 6 else ""))
            ply = [k for k in sorted(ob.get("PLAYER", {})) if k != "PLAYER"]
            if ply:
                extra.append("player object " + ", ".join(ply))
            if o["party"]:
                extra.append("party " + o["party"])
            if o["meters"]:
                extra.append("meters " + o["meters"])
            if t or extra:
                lines.append(f"- {d['id']} `{m}`: " + (f"\"{t[:150]}\"" if t else "no objective text") + ("; " + "; ".join(extra) if extra else ""))
    if lines:
        w("Game data for these rows (VERIFIED: objective text from the mission file, objects from the room data):")
        w("")
        for line in lines:
            w(line)
        w("")


for g, ds in groups.items():
    if g.startswith("19.") or g.startswith("20."):
        continue
    w(f"### {g}")
    w("")
    table(ds)
    texts(ds)

w("## 4. Game-wide mechanics")
w("")
table(groups[RW.G19])
w("Game data behind these rows (VERIFIED, lane C and `local/analysis/lane-p/extras.txt`): 328 chest placements, 157")
w("puzzle pieces, 16 save points, 52 world points, 23 shop points; 751 commands in the command table (9 with the Form")
w("icon, 19 Magic, 8 Item, 6 Summon, 2 Limit, 13 Friend); the limit table has 25 rows; four summons; 11 missions carry")
w("the Mickey flag (AL03_MS103, BB05_MS104A, BB05_MS104B, BB11_MS102, BB15_MS203, CA18_MS202, EH24_MS110, HE07_MS103,")
w("HE18_MS108, MU08_MS204, MU09_MS108); 14 missions switch Drive off; 3 switch summons off.")
w("")
w("## 5. Every Reaction Command and context command in the command table")
w("")
w(f"VERIFIED from the command table (`03system.bin`, table `cmd`) and the English text: {sum(len(v) for v in names.values())} commands")
w(f"without a menu icon carry {len(names)} different names ({blank} more have no name). These are the Triangle commands and the")
w("steps of Limits and summon attacks. **Who offers each command is NOT in this table**: it is decided by each enemy's")
w("or object's own script. The 'offered by' column below is FROM MEMORY, TO CONFIRM IN PLAY, and is filled only where")
w("the owner is well known. For two players the rule is the same for all of them: player 2 must be able to trigger")
w("each one (row GW-01), and the ones that carry the hero need the tests of section 2.")
w("")
w("| Command (ids in the table) | Offered by (FROM MEMORY) |")
w("|---|---|")
by_owner = collections.OrderedDict()
for n, ids, who in known:
    by_owner.setdefault(who, []).append(f"{n} ({ids[0]}{'+' + str(len(ids) - 1) if len(ids) > 1 else ''})")
for who, lst in by_owner.items():
    w(f"| {cell(', '.join(lst))} | {cell(who)} |")
w("")
w(f"Names whose owner is not identified here ({len(unknown)}), listed so that none is left out:")
w("")
w(", ".join(f"{n} ({ids[0]}{'+' + str(len(ids) - 1) if len(ids) > 1 else ''})" for n, ids in unknown) + ".")
w("")
w("## 6. Mission names and files the game does not seem to use")
w("")
table(groups[RW.G20])
w("VERIFIED by lane C: these names either have no mission file or no room script names them. Lane J also decoded the")
w("six old-layout spawn entries of rooms al08 and po10: both rooms have no map file and hang the game when entered, so")
w("they are development leftovers and need no row.")
w("")
w("## 7. What could not be determined from the data")
w("")
for line in [
    "**What most sequences are like to play.** The mission files give an objective sentence, flags, counters and the objects in the room. How a sequence feels, which Reaction Commands it uses and what a boss does are FROM MEMORY in this document, and every such row is marked V+M or M.",
    "**Who offers which Reaction Command** (section 5): decided by enemy and object scripts, which were not read.",
    "**Which mission file is which Atlantica song**, and which mushroom file is which number: read from names and list order only.",
    "**Which friends a Drive Form or a summon uses up**: not in the command, limit, summon or form tables (lane C).",
    "**What makes the Magic Carpet and the flying bike**: copying the player object does not bring a second vehicle (lane J).",
    "**The skateboard object**: the tricks are commands in the table, but the board itself was not identified in the object list.",
    "**The Gummi Ship mode**: only its file names, route names and menu text were read.",
    "**Story order and story state.** The data lists every program that exists, not when the story uses it. Jump discs give a fresh level-1 save, so second visits and late-game states were not seen (lanes B and J).",
    "**Whether each mission's counter counts player 2's actions**: no test yet; this is why score rows carry a test.",
    "**HB13_MS902, SHIP_BATTLE, PO01 (The Hunny Pot)**: the data does not say enough to describe them.",
    "**Sequences without any mission file** that only a playthrough will show (scripted walks, forced events between fights, tutorials given by text boxes alone).",
]:
    w(f"- {line}")
w("")
w("## 8. Where the data came from")
w("")
w("- Mission files, room scripts, spawn data, object list, party table, command, limit and summon tables: lane C's")
w("  lists (`local/analysis/lane-c/`) and `docs/lanes/C-bench-list.md`.")
w("- Objective texts, boss and helper objects per mission, command names, journal lists of minigames and missions,")
w("  Gummi route names: `tools/lane-p/audit_data.py`, `extras.py` and the files in `local/analysis/lane-p/`")
w("  (`mission_facts.json`, `commands.tsv`, `jm_missions.txt`, `extras.txt`, `msg/*.tsv`).")
w("- What is already proven about the twin: lane reports A, B, D, E, F, G, J and K in `docs/lanes/`.")
w("- Rebuild this document: `python -I tools/lane-p/audit_data.py` then `python -I tools/lane-p/build_checklist.py`")
w("  (the hand-written part is `tools/lane-p/rows.py`).")
w("")
(ROOT / "docs" / "PARITY-CHECKLIST.md").write_text("\n".join(A), encoding="utf-8")
print("judgments:", dict(cnt))
print("commands with an owner:", len(known), "| without:", len(unknown))
print("md bytes:", len("\n".join(A).encode("utf-8")))
