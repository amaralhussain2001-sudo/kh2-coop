"""One-off: the test package goes to BUILD 32 = build 31 + the eighty-fifth glue --sound2 (docs/STATE.md part 148: every 3D sound is
heard from the NEARER of the two cameras). patches/merged-v24 = merge_v7.py with build 31's options + --sound2, merged-v24-own =
make_own.py --base merged-v24 --cannon2view. The disc file, the emulator (builds/card1) and the launcher do not change.
START-HERE is not edited any more (since 2026-11-18 the kit's START-HERE has no build line; update_desktop_folder.py writes it).
  python -I tools/package/edit_package_v32.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"

NEW32 = """NEW IN BUILD 32 (the disc file, the emulator and the launcher are the same as in build 31), one change in the patch file:
(1) SOUND FROM THE NEARER HERO. Until build 31 every sound was heard from player 1's camera: when player 2 fought far
    away, his own fight sounded faint on both PCs (or not at all when very far). Now every sound that comes from one
    spot in the room (hits, enemies, attacks, footsteps, ...) is as loud as it is for the camera that is NEARER to it,
    and comes from that camera's left or right. So each player hears his own fight at full strength, wherever the
    other one is. Both PCs still play the same sound (that is how the online play works): player 1 also hears player
    2's fight loudly when player 2 is far away. Music, voices of the story and menu sounds do not change. Sounds that
    belong to a whole area (a river, a waterfall) are only partly better for now (their spot is still chosen from
    player 1's camera).
    Tested on one PC: Agrabah fight, player 1 standing, player 2 fighting about 1,900 steps away: his sounds went from
    25-56 % of full volume (build 31) to about 97 %; sounds near player 1 stayed as before; never out of sync.
"""


def edit(path, pairs):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8-sig").replace("\r\n", "\n")
    for old, new in pairs:
        if t.count(old) == 0 and t.count(new) >= 1:      # this pair is already in (a first run stopped half way)
            continue
        assert t.count(old) == 1, (str(path), t.count(old), old[:70])
        t = t.replace(old, new)
    out = t.replace("\n", "\r\n") if crlf else t
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    print("edited", path)


if "TEST BUILD 32" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 32")     # (the kit read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v24", "merged-v24-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("(patches/merged-v23-own) + the official widescreen group", "(patches/merged-v24-own) + the official widescreen group"),
    ("(patches/merged-v23) + the same group", "(patches/merged-v24) + the same group"),
    ('make("patches/merged-v23-own/" + NAME,', 'make("patches/merged-v24-own/" + NAME,'),
    ('"OWN SCREENS build (patches/merged-v23-own, tools/own/make_own.py --base merged-v23 --cannon2view)")',
     '"OWN SCREENS build (patches/merged-v24-own, tools/own/make_own.py --base merged-v24 --cannon2view)")'),
    ('make("patches/merged-v23/" + NAME,', 'make("patches/merged-v24/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v23-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v24-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v23" / "SLPM-66675_F266B00B.pnach"',
     'SHARED = ROOT / "patches" / "merged-v24" / "SLPM-66675_F266B00B.pnach"'),
    ("does not start with exactly the merged-v23-own lines", "does not start with exactly the merged-v24-own lines"),
    ("does not start with exactly the merged-v23 lines", "does not start with exactly the merged-v24 lines"),
])
edit(README, [
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 31 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 32 (OWN SCREENS)"),
    ("NEW IN BUILD 31 (the disc file, the emulator and the launcher are the same as in build 30), one change in the patch file:\n",
     NEW32 + "NEW IN BUILD 31 (the disc file, the emulator and the launcher are the same as in build 30), one change in the patch file:\n"),
    ("- Known small thing: the sound is one sound for both PCs. You hear the game from player 1's camera.\n",
     "- The sound is one sound for both PCs. Since build 32 every sound is heard from the camera NEARER to it, so\n"
     "  each player hears his own fight at full strength (before: always from player 1's camera).\n"),
])
