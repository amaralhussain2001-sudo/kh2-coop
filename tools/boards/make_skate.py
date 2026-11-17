"""Skateboards for two: the mission scripts (disc v4).

  python -I tools/boards/make_skate.py <builtDir> <twinReport.csv> <cloneReport.csv>

Writes <builtDir>/msn/jp/<mission>.bar for the eight missions that put the player on a skateboard at their start
(three Mail Delivery missions of tt06, the five skate challenges AL00 / CA02 / HB09 / NM09 / TT07 _SKATE_01).
The stock script does trap_obj_reaction_callback(board, player, 327, board) with board = the first object with
status 5067. The changed script takes the player's board by its serial number and then does the same call for
the SECOND board and the twin, both found by their serial numbers:
  - the second board: tools/boards/Boards clone-all wrote it beside the first (cloneReport: room, group, serial,
    new_serial);
  - the twin: lane F's tool wrote him beside the player placement (twinReport: room, group, new_serial).
The script edit itself is tools/lane-s1/make_mail.py's (edit_script, bar_replace); the mission files are the
English ones. Nothing is written outside <builtDir> and its sibling folder skate-work.
"""
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "lane-s1"))
import make_mail as mm  # noqa: E402

# mission, room, group that holds the board, group that holds the player placement (and so the twin)
MISSIONS = (
    ("TT06_WORK_LETTER", "tt06", "b_40", "b_40"),
    ("TT06_LETTER_01", "tt06", "b_40", "b_40"),
    ("TT06_LETTER_02", "tt06", "b_43", "b_43"),
    ("AL00_SKATE_01", "al00", "m_95", "s_99"),
    ("CA02_SKATE_01", "ca02", "m_95", "s_99"),
    ("HB09_SKATE_01", "hb09", "m_95", "s_99"),
    ("NM09_SKATE_01", "nm09", "m_95", "s_99"),
    ("TT07_SKATE_01", "tt07", "m_98", "s_99"),
)


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main(built, twin_report, clone_report):
    twins = rows(twin_report)
    clones = rows(clone_report)
    out = built / "msn" / "jp"
    out.mkdir(parents=True, exist_ok=True)
    work = built.parent / "skate-work"
    work.mkdir(exist_ok=True)
    for name, room, bgroup, pgroup in MISSIONS:
        b = [r for r in clones if r["room"] == room and r["group"] == bgroup]
        assert len(b) == 1, "expected one board in %s %s, found %d" % (room, bgroup, len(b))
        board1, board2 = int(b[0]["serial"]), int(b[0]["new_serial"])
        t = sorted({int(r["new_serial"]) for r in twins if r["room"] == room and r["group"] == pgroup})
        assert len(t) == 1, "expected one twin in %s %s, found %r" % (room, pgroup, t)
        blob = (mm.ENGLISH_MSN / (name + ".bar")).read_bytes()
        ents = mm.bar_entries(blob)
        idx = [i for i, e in enumerate(ents) if e[0] == mm.TYPE_BDX]
        assert len(idx) == 1
        e = ents[idx[0]]
        (work / (name + ".bdx")).write_bytes(blob[e[3]:e[3] + e[4]])
        mm.run([mm.BDXIO, "decode", str(work / (name + ".bdx")), str(work / (name + ".txt"))])
        text = (work / (name + ".txt")).read_text(encoding="utf-8")
        (work / (name + ".new.txt")).write_text(mm.edit_script(text, board2, t[0], board1), encoding="utf-8")
        mm.run([mm.BDXIO, "encode", str(work / (name + ".new.txt")), str(work / (name + ".new.bdx"))])
        newbdx = (work / (name + ".new.bdx")).read_bytes()
        new = mm.bar_replace(blob, idx[0], newbdx)
        (out / (name + ".bar")).write_bytes(new)
        print("%s: script %d -> %d bytes, file %d -> %d bytes; board %d, second board %d, twin %d" % (
            name, e[4], len(newbdx), len(blob), len(new), board1, board2, t[0]))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(pathlib.Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3])
