"""Read and write the enemy parameter table (ENMP) of 00battle.bin. Lane B75.

Layout (VERIFIED against OpenKH's Battle/Enmp.cs and the 21,076-byte table of this disc):
  header: int32 version (2), int32 count
  entry, 92 bytes: u16 id, u16 level, s16 health[32], u16 maxDamage, u16 minDamage,
                   u16 x7 weaknesses (physical, fire, ice, thunder, dark, light, general),
                   u16 experience, u16 prize, u16 bonusLevel
"""
import struct

ENTRY = 92


def parse(blob):
    ver, count = struct.unpack_from("<ii", blob, 0)
    out = []
    for i in range(count):
        off = 8 + i * ENTRY
        eid, level = struct.unpack_from("<HH", blob, off)
        health = list(struct.unpack_from("<32h", blob, off + 4))
        rest = list(struct.unpack_from("<12H", blob, off + 68))
        out.append({"index": i, "offset": off, "id": eid, "level": level, "health": health,
                    "maxDamage": rest[0], "minDamage": rest[1], "weak": rest[2:9],
                    "exp": rest[9], "prize": rest[10], "bonus": rest[11]})
    return ver, out


def set_health(blob, entry, values):
    """Return a new blob with the 32 health values of one entry replaced."""
    b = bytearray(blob)
    struct.pack_into("<32h", b, entry["offset"] + 4, *values)
    return bytes(b)
