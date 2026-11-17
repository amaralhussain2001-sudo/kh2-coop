"""Lane V2: print data words of the game program file.

  python -I tools/lane-v2/words.py <start_hex> <count> [<start_hex> <count> ...]
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from disw import loader  # noqa: E402


def main():
    word = loader()
    a = sys.argv[1:]
    for i in range(0, len(a), 2):
        start, n = int(a[i], 16), int(a[i + 1])
        row = []
        for k in range(n):
            w = word(start + 4 * k)
            row.append("????????" if w is None else "%08X" % w)
        print("%08X: %s" % (start, " ".join(row)))


if __name__ == "__main__":
    main()
