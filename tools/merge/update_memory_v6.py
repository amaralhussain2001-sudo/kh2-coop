"""One-off: bring the assistant's project memory up to date after the night session 2026-11-10 / 11."""
import pathlib

MEM = pathlib.Path.home() / ".claude" / "projects" / "C--Users-PC-FORCE-Desktop-New-folder--3-" / "memory"
p = MEM / "kh2-coop-ps2-project.md"
t = p.read_text(encoding="utf-8")
marker = "TO RESUME after a cleared chat:"
assert t.count(marker) == 1
if "Night of 2026-11-10 to 11" in t:
    raise SystemExit("already there")
start = t.index(marker)
end = t.index("\n", start)
BS = chr(92)
root = "C:" + BS + "Users" + BS + "PC FORCE" + BS + "Desktop" + BS + "New folder (3)"
new = (
    "Night of 2026-11-10 to 11 (main session, no lanes): the user said to stop asking and take my recommended "
    "options ([[take-recommended-and-continue]]), then asked \"is the money shared, but their skills different?\" "
    "(answered: one wallet and item stock; level, skills and equipment the same for both; own skills/equipment "
    "offered as a later job, the user has not answered). Built and tested: shared-screen patch `patches" + BS + "merged-v6` "
    "(tool `tools" + BS + "merge" + BS + "merge_v6.py`) = build 5 + own Drive gauge values for player 2 across rooms "
    "+ text boxes, START, main menu and save menu on either controller + player 2's hero picks up what enemies drop; "
    "own-screen patch `patches" + BS + "merged-v6-own` (tool `tools" + BS + "own" + BS + "make_own.py`) = that + the "
    "command menu's lists shown only on the screen of the player who opened them. Test package build 4 in `dist" + BS + "` "
    "(disc file unchanged, TEST v2). Still nobody has played it; the first two-human test is the user's to do. "
    "Drive bar decision: own gauge per hero (taken as the recommended option, plan row 10).\n\n"
    "TO RESUME after a cleared chat: read the \"PICK UP HERE\" section at the top of `" + root + BS + "docs" + BS + "STATE.md` "
    "first (current builds, next jobs in order), then `KH2-COOP-PLAN.md`."
)
t = t[:start] + new + t[end:]
p.write_text(t, encoding="utf-8")

q = MEM / "take-recommended-and-continue.md"
s = q.read_text(encoding="utf-8")
old2 = 'Earlier the same day they had already said "do everything as your recommendations" for a batch of design decisions.'
assert s.count(old2) == 1
s = s.replace(old2, old2 + ' Later that night, while I was working through the list, they wrote again: "continue until finish all the tasks".')
q.write_text(s, encoding="utf-8")

m = MEM / "MEMORY.md"
x = m.read_text(encoding="utf-8")
old3 = [l for l in x.splitlines() if l.startswith("- [KH2 co-op on PS2-ONLINE]")]
assert len(old3) == 1
x = x.replace(old3[0], "- [KH2 co-op on PS2-ONLINE](kh2-coop-ps2-project.md) — PS2 route, own screens per player, decisions log, builds (merged-v6, test package 4) and where the resume notes live")
m.write_text(x, encoding="utf-8")
print("memory updated")
