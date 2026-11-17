"""Make the English memory-card messages say what the PS2 game really does.

The English pack takes these lines from the later HD version, which has no memory cards: for example the PS2
question "the memory card is not formatted, format it?" became "Delete selected file?". This script rewrites those
messages in a COPY of the pack (the one made by fix_buttons.py) as faithful translations of the original Japanese
text of this disc (compared by message number in local/analysis/main/memcard_msgs.txt). Nothing in the game's
behaviour changes.

  python -I tools/fix_memcard_text.py <fixedPackDir>
"""
import pathlib
import sys

SLOT = "MEMORY CARD in slot {:unk0d }"
KEEP = ["Do not remove the memory card", "or the controller."]
NEED = ["155 KB or more is needed to save", "KINGDOM HEARTS II FINAL MIX data."]

# message id -> text lines (the header line with the INFORMATION / QUESTION icon is kept from the pack)
TEXT = {
    2697: ["Checking " + SLOT + "."] + KEEP,
    2699: ["Failed to save to", SLOT + "."],
    2700: ["Failed to load the file list from", SLOT + "."],
    2701: ["Failed to load from", SLOT + "."],
    2703: ["Formatting " + SLOT + "."] + KEEP,
    2704: ["Saving to " + SLOT + "."] + KEEP,
    2705: ["Loading from " + SLOT + "."] + KEEP,
    2706: ["Overwriting the save data on", SLOT + "."] + KEEP,
    2707: ["Deleting old data on", SLOT + "."] + KEEP,
    2708: ["Failed to check", SLOT + "."],
    2709: ["Failed to format", SLOT + "."],
    2710: ["Failed to delete old data on", SLOT + "."],
    2726: [SLOT, "is not formatted.", "Format it?"],
    2734: [SLOT, "is corrupted."],
    14284: ["Checking the MEMORY CARDS", "in slots 1 and 2."] + KEEP,
    14285: ["Not enough free space on", SLOT + "."] + NEED + ["Start the game anyway?"],
    14286: ["No memory card (PS2) is inserted."] + NEED + ["Start the game anyway?"],
    14298: ["Not enough free space on the", "MEMORY CARDS in slots 1 and 2."] + NEED + ["Start the game anyway?"],
    14426: ["Save data to slot {:unk0d }."],
    14427: ["Load data from slot {:unk0d }."],
    14429: ["No memory card (PS2)", "in slot {:unk0d }."],
    18120: ["Not enough free space on", SLOT + "."] + NEED,
}


def main():
    yml = pathlib.Path(sys.argv[1]) / "msg" / "jp" / "sys.yml"
    lines = yml.read_bytes().decode("utf-8").split("\n")
    starts = [i for i, l in enumerate(lines) if l.startswith("- id: ")]
    starts.append(len(lines))
    out, done = [], set()
    out += lines[:starts[0]]
    for a, b in zip(starts, starts[1:]):
        block = lines[a:b]
        try:
            mid = int(block[0][6:].strip())
        except ValueError:
            out += block
            continue
        if mid not in TEXT:
            out += block
            continue
        header = next((l for l in block[1:] if "{:icon " in l and "{:reset}" in l), None)
        new = [block[0], "  en: >-"]
        if header is not None:
            new += [header, "", ""]
        for k, text in enumerate(TEXT[mid]):
            if k:
                new.append("")
            new.append("    " + text)
        # keep a trailing empty line if the file ends inside this block
        if b == len(lines) and block and block[-1] == "":
            new.append("")
        out += new
        done.add(mid)
    yml.write_bytes("\n".join(out).encode("utf-8"))
    missing = sorted(set(TEXT) - done)
    print(f"rewritten: {len(done)} messages; not found: {missing}")


if __name__ == "__main__":
    main()
