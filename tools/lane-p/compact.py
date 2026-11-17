"""Print the mission facts one line per mission for chosen worlds.  python -I tools/lane-p/compact.py al bb ..."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
facts = json.loads((ROOT / "local" / "analysis" / "lane-p" / "mission_facts.json").read_text(encoding="utf-8"))
out = []
for w in sys.argv[1:]:
    for name in sorted(facts):
        o = facts[name]
        if o["world"] != w:
            continue
        ob = o["objects"]
        boss = ",".join(sorted(list(ob.get("BOSS", {})) + list(ob.get("L_BOSS", {}))))
        ply = ",".join(k for k in sorted(ob.get("PLAYER", {})) if k != "PLAYER")
        nply = ob.get("PLAYER", {}).get("PLAYER", 0)
        fr = "+".join(sorted(ob.get("FRIEND", {})))
        other = ",".join(sorted(list(ob.get("MINIGAME", {})) + list(ob.get("BTLNPC", {}))))
        zako = sum(ob.get("ZAKO", {}).values()) + sum(ob.get("L_ZAKO", {}).values())
        txt = o["info_text"]
        if o["pause_text"] and o["pause_text"] != o["info_text"]:
            txt = (txt + " // " if txt else "") + o["pause_text"][:170]
        rooms = ";".join(o["room_names"])
        out.append(f"{name}|{o['flags'].replace('showWeapon,','').replace('noPrizebox','').replace('hideMap','').replace(',,',',').strip(',')}|{o['party']}|{o['meters']}|{rooms}|{txt}|B:{boss}|P:{ply} ph{nply}|F:{fr}|O:{other}|z{zako}")
(ROOT / "local" / "analysis" / "lane-p" / "compact.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print(len(out))
