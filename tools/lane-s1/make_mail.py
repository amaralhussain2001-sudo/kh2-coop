"""Mail Delivery for two (lane S1 row TTR-03): the data part.

  python -I tools/lane-s1/make_mail.py ard <outDir>
      writes <outDir>/tt06.ard = the stock room file with a SECOND skateboard in the two Mail Delivery groups:
      b_40 (Roxas's board 0x05AB; missions TT06_WORK_LETTER, TT06_LETTER_01) and b_43 (Sora's board 0x081A;
      TT06_LETTER_02), 110 units to the side of the first, where lane F's tool puts the twin ("right 110").
      Prints the two new serial numbers (70 and 242 with the stock file).

  python -I tools/lane-s1/make_mail.py msn <builtDir> <report.csv> <board2 serial b_40> <board2 serial b_43>
      writes <builtDir>/msn/jp/TT06_WORK_LETTER.bar, TT06_LETTER_01.bar, TT06_LETTER_02.bar: the English mission
      files with a changed script. The stock script puts the player on the board at the start
      (trap_obj_reaction_callback(board, player, 327, board), board = first object with status 5067). The changed
      script does the same for the second board and the twin, both found by their spawn serial numbers
      (trap_obj_search_by_serial). The twin's serial is read from lane F's report (rows tt06,b_40 / tt06,b_43).

The script texts come from OpenKH's Bdxio (decode, edit, encode; run only). The encoder writes some unused bits
of instruction words as 0 where the game's own compiler left other values; the decoded text is the same.
Nothing is written outside the given folders.
"""
import csv
import pathlib
import struct
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DOTNET = ROOT / "local" / "dotnet" / "dotnet.exe"
KH2TOOL = ROOT / "local" / "build" / "Kh2Tool" / "Kh2Tool.dll"
BDXIO = r"C:\Users\PC FORCE\Desktop\openkh\Apps\OpenKh.Command.Bdxio.exe"
STOCK_ARD = ROOT / "local" / "extract" / "kh2" / "ard" / "tt06.ard"
ENGLISH_MSN = ROOT / "local" / "english" / "built3" / "msn" / "jp"
MISSIONS = (("TT06_WORK_LETTER", "b_40"), ("TT06_LETTER_01", "b_40"), ("TT06_LETTER_02", "b_43"))
BOARD1 = {"b_40": 69, "b_43": 241}        # serial numbers of the stock boards in the two groups
TYPE_BDX = 3


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: %s\n%s\n%s" % (" ".join(map(str, cmd)), r.stdout, r.stderr))
    return r.stdout


def make_ard(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "tt06.step1.ard"
    out = out_dir / "tt06.ard"
    a = run([str(DOTNET), str(KH2TOOL), "ard-add", str(STOCK_ARD), str(tmp), "b_40", "0", "3", "05AB", "-110", "0", "0"])
    b = run([str(DOTNET), str(KH2TOOL), "ard-add", str(tmp), str(out), "b_43", "0", "3", "081A", "-110", "0", "0"])
    tmp.unlink()
    print(a.strip())
    print(b.strip())


def bar_entries(blob):
    assert blob[:3] == b"BAR"
    count = struct.unpack_from("<i", blob, 4)[0]
    return [list(struct.unpack_from("<HH4sII", blob, 16 + 16 * i)) for i in range(count)]


def bar_replace(blob, index, data):
    """The BAR file with entry <index>'s data replaced. Later data moves by a multiple of 16 bytes, so every
    entry keeps its alignment; entries that share an offset keep sharing it."""
    ents = bar_entries(blob)
    off, size = ents[index][3], ents[index][4]
    later = sorted({e[3] for e in ents if e[3] > off})
    end = later[0] if later else len(blob)
    room = end - off
    grow = 0 if len(data) <= room else ((len(data) - room + 15) // 16) * 16
    out = bytearray(blob[:off]) + data + bytes(room + grow - len(data)) + blob[end:]
    for i, e in enumerate(ents):
        if e[3] == off and e[4] == size:
            e[4] = len(data)
        elif e[3] > off:
            e[3] += grow
        struct.pack_into("<HH4sII", out, 16 + 16 * i, *e)
    return bytes(out)


def edit_script(text, board_serial, twin_serial, board1_serial):
    lines = text.split("\n")
    # The player's board by its serial number: the stock search "first object with status 5067" finds the NEW
    # board, and both riders would end on one board (seen in test n4-mail-dbg).
    part = [i for i, l in enumerate(lines) if l.strip() == "push 5067"]
    assert len(part) == 1 and "trap_obj_search_by_part" in lines[part[0] + 1], "expected one search for the board"
    lines[part[0]] = " push %d" % board1_serial
    lines[part[0] + 1] = " syscall 1, 143 ; trap_obj_search_by_serial (2 in, 0 out)"
    at =[i for i, l in enumerate(lines) if "trap_obj_reaction_callback" in l]
    assert len(at) == 1, "expected one mount call"
    ret = next(i for i in range(at[0], len(lines)) if lines[i].strip() == "ret")
    add = [
        " push.sp 32",
        " push %d" % board_serial,
        " syscall 1, 143 ; trap_obj_search_by_serial (2 in, 0 out)",
        " push.sp 32",
        " push.d.pop 4",
        " syscall 1, 94 ; trap_sysobj_is_exist (1 in, 1 out)",
        " beqz LTWINEND",
        " push.sp 48",
        " push %d" % twin_serial,
        " syscall 1, 143 ; trap_obj_search_by_serial (2 in, 0 out)",
        " push.sp 48",
        " push.d.pop 4",
        " syscall 1, 94 ; trap_sysobj_is_exist (1 in, 1 out)",
        " beqz LTWINEND",
        " push.sp 32",
        " push.sp 48",
        " push 327",
        " push.sp 32",
        " syscall 1, 325 ; trap_obj_reaction_callback (4 in, 0 out)",
        "LTWINEND:",
    ]
    return "\n".join(lines[:ret] + add + lines[ret:])


def make_msn(built, report, serial_b40, serial_b43):
    twin = {}
    with open(report, newline="") as f:
        for row in csv.DictReader(f):
            if row["room"] == "tt06" and row["group"] in ("b_40", "b_43"):
                twin[row["group"]] = int(row["new_serial"])
    assert set(twin) == {"b_40", "b_43"}, "the report has no twin for the Mail Delivery groups: %r" % twin
    board = {"b_40": serial_b40, "b_43": serial_b43}
    out = built / "msn" / "jp"
    out.mkdir(parents=True, exist_ok=True)
    work = built.parent / "mail-work"
    work.mkdir(exist_ok=True)
    for name, group in MISSIONS:
        blob = (ENGLISH_MSN / (name + ".bar")).read_bytes()
        ents = bar_entries(blob)
        idx = [i for i, e in enumerate(ents) if e[0] == TYPE_BDX]
        assert len(idx) == 1
        e = ents[idx[0]]
        (work / (name + ".bdx")).write_bytes(blob[e[3]:e[3] + e[4]])
        run([BDXIO, "decode", str(work / (name + ".bdx")), str(work / (name + ".txt"))])
        text = (work / (name + ".txt")).read_text(encoding="utf-8")
        (work / (name + ".new.txt")).write_text(edit_script(text, board[group], twin[group], BOARD1[group]), encoding="utf-8")
        run([BDXIO, "encode", str(work / (name + ".new.txt")), str(work / (name + ".new.bdx"))])
        new = bar_replace(blob, idx[0], (work / (name + ".new.bdx")).read_bytes())
        (out / (name + ".bar")).write_bytes(new)
        print("%s: script %d -> %d bytes, file %d -> %d bytes; second board serial %d, twin serial %d" % (
            name, e[4], len((work / (name + ".new.bdx")).read_bytes()), len(blob), len(new), board[group], twin[group]))


if __name__ == "__main__":
    if sys.argv[1] == "ard":
        make_ard(pathlib.Path(sys.argv[2]).resolve())
    elif sys.argv[1] == "msn":
        make_msn(pathlib.Path(sys.argv[2]).resolve(), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    else:
        raise SystemExit(__doc__)
