"""Make the English text name the buttons of the JAPANESE disc (Circle = confirm/attack, Cross = cancel/jump).

The English pack's text comes from the US game, where Circle and Cross are the other way round, so lines such as
"Jump with (Circle)" are wrong on this disc. The game's controls are NOT changed; only the two icons in the text
are exchanged. The downloaded pack is never modified: a fixed copy is written to <dst>.

  python -I tools/fix_buttons.py <packDir> <dstDir>
"""
import pathlib
import shutil
import sys

PAIRS = [("{:icon button-circle}", "{:icon button-cross}"), ("{:unk16 05}", "{:unk16 06}")]
# The pack's own Japan-specific line is already right for this disc: leave it alone.
ALREADY_RIGHT = "{:icon button-circle}: Save   {:icon button-cross}: End Game"


def swap(line):
    for a, b in PAIRS:
        line = line.replace(a, "\0A\0").replace(b, a).replace("\0A\0", b)
    return line


def main():
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    total = 0
    for yml in sorted((dst / "msg").rglob("*.yml")):
        rel = yml.relative_to(dst).as_posix()
        if rel == "msg/sys.yml":
            continue  # US system text, not used for the Japanese disc
        raw = yml.read_bytes()
        text = raw.decode("utf-8")
        out, changed = [], 0
        for line in text.split("\n"):
            new = line if (rel == "msg/jp/sys.yml" and ALREADY_RIGHT in line) else swap(line)
            changed += new != line
            out.append(new)
        if changed:
            yml.write_bytes("\n".join(out).encode("utf-8"))
        total += changed
        print(f"{rel}: {changed} line(s) changed")
    print("total lines changed:", total)


if __name__ == "__main__":
    main()
