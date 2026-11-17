import pathlib
f = pathlib.Path(r"C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-s1/s1rcsum.py")
s = f.read_text()
a = "    prev = None\n    n = 0\n"
b = ("    # The session log's clock runs a few seconds ahead of the probe's clock. The probe's first sample is taken\n"
     "    # right after the screenshot of its start frame appears, so that pair fixes the difference (a few frames off).\n"
     "    start = int(sys.argv[sys.argv.index(\"--start\") + 1]) if \"--start\" in sys.argv else 4600\n"
     "    first = int(rows[1].split(\",\")[0])\n"
     "    off = 0\n"
     "    for i in range(len(anc) - 1):\n"
     "        (t0, f0), (t1, f1) = anc[i], anc[i + 1]\n"
     "        if f0 <= start <= f1 and f1 > f0:\n"
     "            off = int(t0 + (start - f0) * (t1 - t0) / (f1 - f0)) - first\n"
     "    prev = None\n    n = 0\n")
assert s.count(a) == 1
s = s.replace(a, b)
a2 = "        fr = to_frame(anc, int(d[\"tick\"]))\n"
assert s.count(a2) == 1
s = s.replace(a2, "        fr = to_frame(anc, int(d[\"tick\"]) + off)\n")
s = s.replace("  python -I tools/lane-s1/s1rcsum.py <test-name> [--all] [--from F] [--to F]",
              "  python -I tools/lane-s1/s1rcsum.py <test-name> [--all] [--from F] [--to F] [--start 4600]")
f.write_text(s)
print("ok")
