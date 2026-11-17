"""One-off: the test package goes to BUILD 22 = build 21 + the glues 72 to 76 (docs/STATE.md, Tenth round, parts 119 to 124; the
user's answer F of 2026-11-16: "do 1 and 4 from propsals", then "try to close everything now so the next patch should contain
everything"):
  72 --drivesave   player 2's own Drive gauge and bars are kept in the save (a Load Game gives each hero his own again)
  73 --itemtarget  a target choice for Potions, Ethers and Elixirs: the item window "PARTY" shows both heroes
  74 --boxpick     player 2's hero picks up a dropped item box too (before: only player 1's could)
  75 --formroom    in a new room player 2's Drive Form files are asked for again (they are not left "to be thrown out")
  76 --setposguard trap_effect_set_pos writes nothing for an ended effect (the Fortuneteller's Clear Shot: 26 stores to 0)
(Glue 77 --gummiall is NOT in build 22: it faulted in its tests; the Gummi points of weapons other than cannons stay open.)
THE DISC FILE IS STILL "TEST v5"; only the patch files change: the package now takes patches/merged-v16-own (own
screens) and patches/merged-v16 (shared-screen fallback), written by
`tools/merge/merge_v7.py patches/merged-v16 --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2
--sidecar2 --twinmake --hudowner --ownabil --holdwatch --itemsync --ownitems --ownkey --bindname --holdpair
--ship2score --trickguard --holdshared --ownwallet --shoppad --ownbag --drivesave --itemtarget --boxpick --formroom
--setposguard` and
`tools/own/make_own.py patches/merged-v16-own --base merged-v16 --cannon2view`. Build 21's patches/merged-v15 /
merged-v15-own stay.
Edits: make_package_patch.py, make_test_package.py, the read-me and the two-PC start text.
  python -I tools/package/edit_package_v22.py          (run ONCE; it refuses a second run)
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "kit" / "1-READ-ME-FIRST (KH2 TEST).txt"
START = HERE / "kit" / "START-HERE (TWO PCs AT HOME).txt"


def edit(path, pairs):
    t = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if t.count(old) == 0 and t.count(new) >= 1:      # this pair is already in (a first run stopped half way)
            continue
        assert t.count(old) == 1, (path.name, t.count(old), old[:70])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8")
    print("edited", path.name)


if "TEST BUILD 22" in README.read_text(encoding="utf-8"):
    raise SystemExit("already build 22")     # (the read-me is the LAST file edited: the guard holds only after a full run)
for d in ("merged-v16", "merged-v16-own"):
    assert (HERE.parent.parent / "patches" / d / "SLPM-66675_F266B00B.pnach").exists(), "patches/%s is not there yet" % d

edit(HERE / "make_package_patch.py", [
    ("  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v15-own) + the official widescreen group",
     "  SLPM-66675_F266B00B.pnach          the own-screen build (patches/merged-v16-own) + the official widescreen group"),
    ("  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v15) + the same group",
     "  shared/SLPM-66675_F266B00B.pnach   the shared-screen fallback (patches/merged-v16) + the same group"),
    ('make("patches/merged-v15-own/" + NAME, "patches/test-package-v3/" + NAME,',
     'make("patches/merged-v16-own/" + NAME, "patches/test-package-v3/" + NAME,'),
    ('     "OWN SCREENS build (patches/merged-v15-own, tools/own/make_own.py --base merged-v15 --cannon2view)")',
     '     "OWN SCREENS build (patches/merged-v16-own, tools/own/make_own.py --base merged-v16 --cannon2view)")'),
    ('make("patches/merged-v15/" + NAME, "patches/test-package-v3/shared/" + NAME,',
     'make("patches/merged-v16/" + NAME, "patches/test-package-v3/shared/" + NAME,'),
])
edit(HERE / "make_test_package.py", [
    ('MERGED = ROOT / "patches" / "merged-v15-own" / "SLPM-66675_F266B00B.pnach"',
     'MERGED = ROOT / "patches" / "merged-v16-own" / "SLPM-66675_F266B00B.pnach"'),
    ('SHARED = ROOT / "patches" / "merged-v15" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen',
     'SHARED = ROOT / "patches" / "merged-v16" / "SLPM-66675_F266B00B.pnach"          # the fallback: one shared screen'),
    ('sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v15-own lines")',
     'sys.exit("the test package\'s KH2 patch does not start with exactly the merged-v16-own lines")'),
    ('sys.exit("the fallback patch does not start with exactly the merged-v15 lines")',
     'sys.exit("the fallback patch does not start with exactly the merged-v16 lines")'),
])
edit(START, [
    ("   BUILDS 13 TO 21 KEEP THAT DISC FILE; only small files changed.",
     "   BUILDS 13 TO 22 KEEP THAT DISC FILE; only small files changed."),
])
edit(README, [
    ("""NEW IN BUILD 21 (the disc file is still the same), four things:""",
     """NEW IN BUILD 22 (the disc file is still the same), five things:
(1) A TARGET CHOICE FOR POTIONS, HI-POTIONS, ETHERS AND ELIXIRS. When you use one from the command menu, the
    window "PARTY" now shows BOTH heroes: "Sora, Donald, Goofy, Sora" (or "Sora, Sora" when Donald and Goofy
    are not there). ON BOTH SCREENS THE FIRST "SORA" IS PLAYER 1'S HERO AND THE LAST "SORA" IS PLAYER 2'S HERO.
    So you can heal your partner while he stands. One rule: if you pick YOURSELF while your partner is DOWN, the
    item goes to your partner (as before). A shortcut item (L1) works as before: to your partner if he is down,
    else to you.
(2) PLAYER 2'S OWN DRIVE GAUGE IS KEPT IN THE SAVE. After Load Game each hero has his own Drive gauge again
    (before, both started with player 1's). A save from build 21 or older still gives both player 1's gauge.
(3) PLAYER 2 PICKS UP WHAT ENEMIES DROP. An item an enemy drops (a material, a fight item) could only be picked
    up by player 1's hero; now player 2's hero picks it up too. What either player picks up goes into BOTH bags,
    as from a chest.
(4) PLAYER 2'S DRIVE FORM AFTER A DOOR: his form's files are kept like player 1's (before, in a full room the
    game could have thrown them out while his form still used them; never seen, now prevented).
(5) THE FORTUNETELLER'S "CLEAR SHOT" (Agrabah): a small fault after it is guarded (the game wrote to an effect
    that had already ended).
    TESTED NOW, NOTHING TO CHANGE: the Data Xemnas fight's laser part (both heroes in it, each player's own
    Reflect, each press counts once); the toy cannon started at the elf by player 2 alone; the carpet escape
    entered with player 2 there first; the Large Body's "Full Swing" by player 2 (it is offered after a combo's
    last hit knocks a Large Body back: then stand at its front or back and press Triangle).
NEW IN BUILD 21 (the disc file is still the same), four things:"""),
    ("""  else (tested for HP and MP balls taken by player 2; Drive balls did not drop in the tests); munny goes into""",
     """  else (tested for HP, MP and Drive taken by player 2: the Drive test made the HP balls give Drive); munny goes into"""),
    ("""- Saving works (one shared save). The save holds player 1's Drive gauge; after loading, both heroes start with it.""",
     """- Saving works (one shared save). Since build 22 the save holds BOTH heroes' Drive gauges; after Load Game each
  hero has his own again (before: both started with player 1's)."""),
    ("""- A Potion heals the hero who is down; if nobody is down, the hero who used it. There is no choice on screen.""",
     """- Since build 22 you choose who gets a Potion, Hi-Potion, Ether or Elixir: the first "Sora" in the window is
  player 1's hero, the last "Sora" player 2's (if you pick yourself while your partner is down, he gets it).
  Shortcut items: the hero who is down, else the one who used it."""),
    ("""- Item drops (not the HP / MP / munny balls): a material the game gives goes into both bags (since build 21).
  Whether player 2 can pick up a dropped material himself is not tested yet (no material dropped in the tests).""",
     """- Item drops (not the HP / MP / munny balls): since build 22 either player's hero picks them up, and what is
  picked up goes into both bags (tested with a material dropped in Agrabah)."""),
    ("""  and the Samurai falls to his finish. Not met by any test script: the Large Body's green command ("Full
  Swing") for player 2.""",
     """  and the Samurai falls to his finish. THE LARGE BODY'S "FULL SWING" works for player 2 too (build 22's tests):
  it is offered only after a combo's last hit knocks a Large Body back; stand at its front or back, press Triangle."""),
    ("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 21 (OWN SCREENS)",
     "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 22 (OWN SCREENS)"),
])
print("package tooling and read-me are build 22 (disc v5, patches merged-v16 / merged-v16-own)")
