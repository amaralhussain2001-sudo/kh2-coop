"""One-off (ninth round, STATE parts 110 to 115): tools/own/row9_report.py is brought up to TEST BUILD 21 (the user's items 1 to 4 of
2026-11-15 evening: a boss's grab takes only the hero it aims at; only the last Xemnas's laser dome takes both, each player
with his own Reflect; glue 68 left out; Shan-Yu's stray calls 0; the Samurai duel verified; the Large Body and the end of the
Riku part with one hero held not verified). The PLAYED column reads the runs of build 21's candidates (tags rs4 = the 40
fights on v128, h11 = the ten boss rooms on v124). Then the report is made again by hand:
  python -I tools/own/edit_row9_build21.py
  python -I tools/own/row9_report.py --xig=local/sweep/b15/row9-xig.txt --lux=local/sweep/b15/row9-lux.txt"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
p = ROOT / "tools" / "own" / "row9_report.py"
s = p.read_text(encoding="utf-8")
if "SINGLE =" in s:
    raise SystemExit("already there")


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)


B21 = (" BUILD 21 (the user's item 4 of 2026-11-15: a single-target attack takes only the targeted player): THE GRAB TAKES "
       "ONLY THE HERO IT AIMS AT, the other hero stays free and fights (the ten boss rooms on v122 / v124, runs h10 / h11, "
       "and the 40 fights on v128, run rs4: no pair).")
for key in ('"B_BB110": ("PAIR", "', '"B_HE020": ("PAIR", "', '"B_LK110": ("PAIR", "', '"B_HE100": ("PAIR", "', '"B_EX390": ("PAIR", "'):
    i = s.index(key)
    j = s.index('"),\n', i)
    s = s[:i] + key.replace('("PAIR"', '("SINGLE"') + s[i + len(key):j] + B21 + s[j:]

key = '"B_EX170_LAST": ("PAIR", "'
i = s.index(key)
j = s.index('"),\n', i)
s = s[:j] + (" BUILD 21: HIS OPENING MOVE AND THE RIKU PART TAKE ONE HERO (the one the script names); the held hero's "
             "player steers Riku with his own stick (run xsB on v122) and his green commands reach the boss (run rkE on v127); "
             "THE END OF THE RIKU PART WITH ONE HERO HELD WAS NOT SEEN IN A TEST (it needs Riku steered to Xemnas: runs xsA, "
             "xsP, xsV, rkA .. rkE; for the user's playthrough). THE LASER DOME STAYS THE ONE SHARED MOVE: both heroes stand "
             "in it, each player has his own Reflect in his own menu (glue 65 co_two), a press of either player is sent in "
             "player 1's hero's name so that every piece of the dome runs on the hero its lasers aim at (hs_rc), the count "
             "goes up once a press and the dome ends once (runs xt2 .. xt6 on v128: player 2 alone 41 reflects, player 1 "
             "alone 30, both 55; no step with two; STATE parts 111, 113).") + s[j:]

rep("""Written 2026-11-14 for job 10 of the job list ("build it or write the per-fight report"); brought up to test build
20 on 2026-11-15 (the ninth round: both heroes inside the same hold).""",
    """Written 2026-11-14 for job 10 of the job list ("build it or write the per-fight report"); brought up to test build
20 on 2026-11-15 (the ninth round: both heroes inside the same hold) and to TEST BUILD 21 on 2026-11-15 night (the
user's items 1 to 4: a boss's grab takes only the hero it aims at; only the last Xemnas's laser dome takes both).""")

rep("""- The mirror hero of a pair has no hooked script of his own (the boss's script hooks one piece onto one hero);
  where that piece reads a controller, it reads the named hero's. BUILD 20 (glue 68, `merge_v7.py --holdpads`):
  WHILE BOTH HEROES OF A PAIR ARE HELD, BOTH CONTROLLERS COUNT (the buttons of either, without START, and the
  moving stick), so both players press in a hold, and in the last Xemnas's "Riku frees Sora" part both
  players steer Riku (part 100).""",
    """- The mirror hero of a pair has no hooked script of his own (the boss's script hooks one piece onto one hero);
  where that piece reads a controller, it reads the named hero's. Build 20 (glue 68, `--holdpads`) made the two
  controllers one while both heroes were held. BUILD 21 LEAVES GLUE 68 OUT: each player keeps his own controller,
  one press never counts twice.
BUILD 21 (THE USER'S ITEM 4 OF 2026-11-15: "For single-target attacks, prefer capturing only the targeted player. For
genuinely shared boss mechanics, both players should participate meaningfully."): `tools\\own\\cap_kinds.py` sorted
every boss capture of the 40 fights and the ten boss rooms: all are SINGLE-TARGET (the boss's script takes one
victim with a move) except the last Xemnas's LASER DOME (move 0x106: the game itself captures the player and Riku).
Glue 65's fifth form (`--holdshared`) makes a pair only there; every other grab takes the hero the script names, as
the game; the stray-capture cure and the nets stay. In the dome each player has his own Reflect (co_two), a press of
player 2's hero is sent in player 1's hero's name (hs_rc: the dome's pieces run on the hero its lasers aim at), the
dome is never "a hero's own move" (hs_hf). Shan-Yu's clash keeps glue 50; its push count goes up once a push
(STATE part 112).""")

rep("""PAIR = build 20 puts both heroes inside the same hold; seen in test runs.""",
    """PAIR = build 20 puts both heroes inside the same hold; seen in test runs (build 21: only the last Xemnas's laser dome).
SINGLE = build 21: the boss's grab takes only the hero it aims at, the other stays free; seen in test runs.""")
rep("""PLAYED = played on purpose with two heroes on
build 20's candidate""", """PLAYED = played on purpose with two heroes on
build 21's candidate""")
rep('''"ON BUILD 20's CANDIDATE, PLAYED ON PURPOSE WITH TWO HEROES: "''', '''"ON BUILD 21's CANDIDATES (v128 / v124), PLAYED ON PURPOSE WITH TWO HEROES: "''')
rep('''    played = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "own" / "row9_rs2.py"), "--json"],''',
    '''    played = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "own" / "row9_rs2.py"), "--json", "--tags=rs4,h11"],''')
rep('''    order = ["OK", "PAIR", "FIXED", "OWN", "PLAYED", "RUN", "OPEN", "SWEEP", "NO ROOM"]''',
    '''    order = ["OK", "PAIR", "SINGLE", "FIXED", "OWN", "PLAYED", "RUN", "OPEN", "SWEEP", "NO ROOM"]''')
rep("""- The stray calls in one clash of six at Shan-Yu when BOTH players press: still there in build 14 (run cap12),
  cause not found. The clash ends right all the same.""",
    """- (Closed 2026-11-15 night: Shan-Yu's stray calls. Since build 16 both heroes are in the clash; runs syC / syD on
  v124: 0 captures outside a hero's own clash; the push count goes up once a push, runs syE2 / syG2. STATE part 112.)""")
rep("""- How it feels when both players steer the one Riku (the last Xemnas's hold) is for the user's test.""",
    """- The last Xemnas's "Riku frees Sora" part with ONE hero held (build 21): the held hero's player steers Riku; the
  part's END was not seen in a test (Riku must be steered to Xemnas). For the user's playthrough.""")
rep("""- The Large Body's command and the Samurai duel (enemy moves of the same kind): NOT MET in five test runs each
  (STATE part 39). They need a human.""",
    """- The Samurai duel by player 2: VERIFIED in build 21's tests (Twilight Town tt19, runs smA / smC / smD: "Duel
  Stance" and "The End" in his own menu, the Samurai cut down; STATE part 114).
- The Large Body's command "Full Swing": NOT MET in a test (he05 in the eighth round; Agrabah al00 in the ninth, four
  runs of 11,000 frames: never offered). UNVERIFIED, for the user's playthrough.""")
p.write_text(s, encoding="utf-8", newline="\n")
print("report source: build 21")
