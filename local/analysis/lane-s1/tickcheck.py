import ctypes, os, sys, time, re
ctypes.windll.kernel32.GetTickCount64.restype = ctypes.c_uint64
d = sys.argv[1]
now_tick, now = ctypes.windll.kernel32.GetTickCount64(), time.time()
def tick_of(path):
    return now_tick - (now - os.path.getmtime(path)) * 1000
log = os.path.join(d, "p1.log")
last = [l for l in open(log, errors="replace").read().splitlines() if re.match(r"\d+ ", l)][-1]
print("last log line:", last[:80])
print("log file mtime as tick: %.0f" % tick_of(log))
for f in ("p1_f004600.png", "p1_f004800.png", "p1_f008950.png"):
    print(f, "mtime as tick: %.0f" % tick_of(os.path.join(d, f)))
rows = open(os.path.join(d, "rc.csv")).read().splitlines()
print("first sample tick", rows[1].split(",")[0], "last", rows[-1].split(",")[0])
for l in open(log, errors="replace").read().splitlines():
    if "stats: frame" in l:
        print(l[:40])
