"""One-off: the user's memory folder after test build 5 (2026-11-11): the feedback note gets the two new quotes,
the project note gets the day's paragraph, the index line gets the new package id."""
import pathlib

BS = chr(92)
M = pathlib.Path("C:" + BS + "Users" + BS + "PC FORCE" + BS + ".claude" + BS + "projects" + BS
                 + "C--Users-PC-FORCE-Desktop-New-folder--3-" + BS + "memory")

p = M / "take-recommended-and-continue.md"
t = p.read_text(encoding="utf-8")
if "test it one time" not in t:
    old = 'Later that night, while I was working through the list, they wrote again: "continue until finish all the tasks".'
    assert t.count(old) == 1
    t = t.replace(old, old + ' On 2026-11-11 I ended a turn with a build report that read like an end although the job list '
                  'still had doable jobs; the user wrote "why you stop not finish all the tasks?" and then "finish all the '
                  'tasks then i\'m going to test it one time after u finish everything".')
    old = "**How to apply:** still write choices"
    assert t.count(old) == 1
    t = t.replace(old, "**How to apply:** a finished build is not a stopping point while the pick-up list has jobs I can do; "
                  "the user tests ONCE at the end, so I keep going down the list and only give short progress lines. "
                  "Still write choices")
    p.write_text(t, encoding="utf-8")

p = M / "kh2-coop-ps2-project.md"
t = p.read_text(encoding="utf-8")
if "8a2aa7970f68" not in t:
    t = t.rstrip("\n") + "\n\n" + (
        "Day of 2026-11-11 (main session, no lanes): the user asked why I stopped and said to finish all the tasks; "
        "they will test once at the end ([[take-recommended-and-continue]]). Done and verified by scripted tests: "
        "the hit counters of the \"cannot be hurt\" fights count player 2 (the mission files have their own scripts; "
        "decoder `tools" + BS + "lane-s1" + BS + "extract_msn_ai.py`); rules screens and the menu's first reveal on either "
        "controller; a fault of my own per-player menu rows (empty menu after a rules screen) fixed; Drive Forms for "
        "player 2 (own slot, own form number, own gauge and menu, through doors; one form at a time is the game's own "
        "lock and was kept). Built in but not seen in a game: mission-gauge prizes for player 2. Tried and left out: "
        "helpers following player 2 (builder option `--helper`). Test package BUILD 5, id 8a2aa7970f68 "
        "(`patches" + BS + "merged-v6` SHA-1 ba3d261e..., `merged-v6-own` f0c65c02...), rehearsed, disc unchanged (TEST v2). "
        "Open and next: Mail Delivery (needs a new disc v3: second board + mission script edit), the bag ride, "
        "Twilight Thorn, helpers. Everything is in `docs" + BS + "STATE.md` (PICK UP HERE and section "
        "\"Second round on merged build 6\") and plan rows 15-17.\n")
    p.write_text(t, encoding="utf-8")

p = M / "MEMORY.md"
t = p.read_text(encoding="utf-8")
old = "builds (merged-v6, test package 4, id 538e811e10f7)"
if old in t:
    t = t.replace(old, "builds (merged-v6, test package 5, id 8a2aa7970f68)")
    t = t.replace("no stopping for A/B questions; pick my recommendation, note it, keep working",
                  "no stopping for A/B questions or after a build; pick my recommendation, note it, keep working; user tests once at the end")
    p.write_text(t, encoding="utf-8")
print("memory updated")
