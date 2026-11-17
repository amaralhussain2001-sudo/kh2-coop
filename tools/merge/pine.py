"""Small PINE client for the sandbox emulator (PCSX2's memory interface on 127.0.0.1:<port>).

Library use:  from pine import Pine;  p = Pine(28031);  p.r32(addr);  p.w8(addr, v);  p.read(addr, n)
Command line:
  python -I tools/lane-b/pine.py watch <port> <seconds> <hexaddr:size,...>     print the values whenever they change
  python -I tools/lane-b/pine.py dump  <port> <hexaddr> <length> <outfile>      save a memory range
Writes exist (w8/w16/w32) but must only be used in ONE-copy tests: a write on one PC of a linked pair breaks sync.
"""
import socket
import struct
import sys
import time


class Pine:
    def __init__(self, port, wait=60.0):
        t0 = time.time()
        while True:
            try:
                self.s = socket.create_connection(("127.0.0.1", port), timeout=10)
                break
            except OSError:
                if time.time() - t0 > wait:
                    raise
                time.sleep(0.2)

    def _rx(self, n):
        buf = bytearray()
        while len(buf) < n:
            c = self.s.recv(n - len(buf))
            if not c:
                raise ConnectionError("PINE closed")
            buf += c
        return bytes(buf)

    def _call(self, body):
        self.s.sendall(struct.pack("<I", len(body) + 4) + body)
        size = struct.unpack("<I", self._rx(4))[0]
        rep = self._rx(size - 4)
        if rep[0] != 0:
            raise RuntimeError("PINE call failed")
        return rep[1:]

    def r8(self, a):
        return self._call(b"\x00" + struct.pack("<I", a))[0]

    def r16(self, a):
        return struct.unpack("<H", self._call(b"\x01" + struct.pack("<I", a))[:2])[0]

    def r32(self, a):
        return struct.unpack("<I", self._call(b"\x02" + struct.pack("<I", a))[:4])[0]

    def rf(self, a):
        return struct.unpack("<f", self._call(b"\x02" + struct.pack("<I", a))[:4])[0]

    def w8(self, a, v):
        self._call(b"\x04" + struct.pack("<IB", a, v & 0xFF))

    def w16(self, a, v):
        self._call(b"\x05" + struct.pack("<IH", a, v & 0xFFFF))

    def w32(self, a, v):
        self._call(b"\x06" + struct.pack("<II", a, v & 0xFFFFFFFF))

    def wf(self, a, v):
        self._call(b"\x06" + struct.pack("<If", a, v))

    def read(self, a, n):
        out = bytearray()
        end = a + n
        cur = a & ~7
        while cur < end:
            k = min(40000, (end - cur + 7) // 8)
            body = b"".join(b"\x03" + struct.pack("<I", cur + 8 * i) for i in range(k))
            out += self._call(body)[:8 * k]
            cur += 8 * k
        off = a - (a & ~7)
        return bytes(out[off:off + n])

    def try_status(self):
        try:
            return self._call(b"\x0f")
        except Exception:  # noqa: BLE001
            return None


def main():
    cmd = sys.argv[1]
    port = int(sys.argv[2])
    if cmd == "watch":
        secs = float(sys.argv[3])
        specs = []
        for item in sys.argv[4].split(","):
            a, _, sz = item.partition(":")
            specs.append((int(a, 16), int(sz or "4")))
        p = Pine(port)
        last = None
        t0 = time.time()
        while time.time() - t0 < secs:
            try:
                vals = tuple({1: p.r8, 2: p.r16, 4: p.r32}[sz](a) for a, sz in specs)
            except Exception:  # noqa: BLE001
                time.sleep(0.05)
                continue
            if vals != last:
                print(f"{time.time() - t0:7.2f}s " + " ".join(f"{a:08X}={v:0{sz * 2}X}" for (a, sz), v in zip(specs, vals)), flush=True)
                last = vals
            time.sleep(0.02)
    elif cmd == "dump":
        p = Pine(port)
        data = p.read(int(sys.argv[3], 16), int(sys.argv[4], 0))
        open(sys.argv[5], "wb").write(data)
        print("saved", len(data))


if __name__ == "__main__":
    main()
