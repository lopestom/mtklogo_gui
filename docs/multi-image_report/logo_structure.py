#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logo_structure.py - Structural report of a MediaTek logo.bin file.

Replicate in Python the reading of the mtklogo source code (cyberknight777/arlept):
  header.rs (MTK 512 B header), logo.rs (offsets table + blobs + cert)
  and Profile::guess_format (matching slots with profiles from mtklogo.yaml).

Uso:
  python3 logo_structure.py logo.bin
  python3 logo_structure.py logo.bin --yaml mtklogo.yaml
  python3 logo_structure.py logo.bin --yaml mtklogo.yaml --export out_png/
  python3 logo_structure.py logo.bin --compare outher_logo.bin
  python3 logo_structure.py logo.bin --json > report.json

Standard library only. Optional: PyYAML (profiles) and Pillow (contact sheet).
Read-only: the logo.bin file is never modified.
"""
import argparse
import collections
import hashlib
import json
import os
import struct
import sys
import zlib

VERSION = "1.2"
MAGIC = 0x88168858
MAGIC_EXT = 0x89168958
MAGIC_BYTES = struct.pack(">I", MAGIC)
HDR = 512
LABELS = (b"RECOVERY", b"ROOTFS", b"KERNEL", b"LOGO")

# mode -> (bytes per pixel, description of the byte order in memory)
MODES = {
    "rgbabe": (4, "R,G,B,A"),
    "rgbale": (4, "A,B,G,R"),
    "bgrabe": (4, "B,G,R,A"),
    "bgrale": (4, "A,R,G,B"),
    "rgb565be": (2, "RGB565 big-endian"),
    "rgb565le": (2, "RGB565 little-endian"),
}

# Actual/common full-screen resolutions seen on MTK devices (width x height, portrait).
COMMON = [
    (480, 800), (480, 854), (540, 960), (600, 1024), (720, 1280), (720, 1440), (720, 1520),
    (720, 1600), (720, 1604), (720, 1612), (720, 1640), (720, 1650), (768, 1024), (800, 1280),
    (800, 1340), (1080, 1920), (1080, 2160), (1080, 2280), (1080, 2340), (1080, 2400),
    (1080, 2408), (1080, 2412), (1080, 2460), (1200, 1920), (1200, 2000), (1218, 2160),
    (1220, 2712), (1260, 2800), (1264, 2780), (1440, 2560), (1440, 3200), (1536, 2048),
    (1600, 2560), (1600, 2880),
]

OID_NAMES = {
    "2.5.4.3": "CN", "2.5.4.6": "C", "2.5.4.7": "L", "2.5.4.8": "ST",
    "2.5.4.10": "O", "2.5.4.11": "OU",
    "1.2.840.113549.1.1.4": "md5WithRSAEncryption",
    "1.2.840.113549.1.1.5": "sha1WithRSAEncryption",
    "1.2.840.113549.1.1.11": "sha256WithRSAEncryption",
    "1.2.840.113549.1.1.12": "sha384WithRSAEncryption",
    "1.2.840.113549.1.1.13": "sha512WithRSAEncryption",
}


class LogoError(Exception):
    pass


def n(x):
    """Integer with a thousands separator following the format used in some countries."""
    return f"{x:,}".replace(",", ".")


# --------------------------------------------------------------------------- MTK header
def parse_mtk_header(buf, off=0):
    """Decodes a 512-byte MTK header (header.rs). Raises LogoError if invalid."""
    h = buf[off:off + HDR]
    if len(h) < HDR:
        raise LogoError("file smaller than an MTK header (512 B)")
    if struct.unpack(">I", h[:4])[0] != MAGIC:
        raise LogoError("magic 0x88168858 missing")
    u = lambda o: struct.unpack("<I", h[o:o + 4])[0]
    name = h[8:40]
    ext = struct.unpack(">I", h[0x30:0x34])[0] == MAGIC_EXT
    d = {
        "offset": off, "dsize": u(4), "name": name.rstrip(b"\0").decode("latin1"),
        "addr": u(0x28), "mode": u(0x2C), "extended": ext,
        "legacy_logo": name.startswith(b"LOGO"),
    }
    if ext:
        for key, o in (("hdr_size", 0x34), ("hdr_ver", 0x38), ("img_type", 0x3C),
                       ("img_list_end", 0x40), ("align_size", 0x44), ("dsize_ext", 0x48),
                       ("addr_ext", 0x4C), ("scrambled", 0x50)):
            d[key] = u(o)
        res = h[0x54:HDR]
        d["reserved_all_ff"] = set(res) == {0xFF}
    else:
        d["align_size"] = 0
        d["reserved_all_ff"] = set(h[0x28:HDR]) == {0xFF}
    return d


# --------------------------------------------------------------------------- Minimum DER (certificates)
def _tlv(b, o):
    tag = b[o]
    l = b[o + 1]
    if l & 0x80:
        k = l & 0x7F
        length = int.from_bytes(b[o + 2:o + 2 + k], "big")
        hdr = 2 + k
    else:
        length, hdr = l, 2
    if o + hdr + length > len(b):
        raise ValueError("Truncated DER")
    return tag, hdr, length


def _children(b, o):
    tag, hdr, length = _tlv(b, o)
    p, end, out = o + hdr, o + hdr + length, []
    while p < end:
        t, h, l = _tlv(b, p)
        out.append((t, p, h, l))
        p += h + l
    return out


def _oid(b, p, h, l):
    v = b[p + h:p + h + l]
    parts = [v[0] // 40, v[0] % 40]
    acc = 0
    for c in v[1:]:
        acc = (acc << 7) | (c & 0x7F)
        if not c & 0x80:
            parts.append(acc)
            acc = 0
    return ".".join(map(str, parts))


def _name(b, p):
    out = []
    for _, sp, _, _ in _children(b, p):               # SET
        for _, qp, _, _ in _children(b, sp):          # SEQUENCE
            ch = _children(b, qp)
            oid = _oid(b, ch[0][1], ch[0][2], ch[0][3])
            val = b[ch[1][1] + ch[1][2]:ch[1][1] + ch[1][2] + ch[1][3]].decode("utf-8", "replace")
            out.append(f"{OID_NAMES.get(oid, oid)}={val}")
    return ", ".join(out)


def _time(b, p, h, l):
    s = b[p + h:p + h + l].decode("ascii", "replace")
    if len(s) >= 13 and s[0].isdigit() and len(s) == 13:     # UTCTime YYMMDDHHMMSSZ
        yy = int(s[:2])
        y = 2000 + yy if yy < 50 else 1900 + yy
        return f"{y}-{s[2:4]}-{s[4:6]}"
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"                      # GeneralizedTime


def parse_cert(der):
    """Summary of the first X.509 certificate in the payload; None if it is not valid DER."""
    try:
        top = _children(der, 0)
        tbs = _children(der, top[0][1])
        i = 1 if tbs[0][0] == 0xA0 else 0                     # skip [0] version
        sraw = der[tbs[i][1] + tbs[i][2]:tbs[i][1] + tbs[i][2] + tbs[i][3]]
        serial = (sraw[1:] if len(sraw) > 1 and sraw[0] == 0 else sraw).hex().upper()
        sig = _children(der, tbs[i + 1][1])[0]
        sigalg = OID_NAMES.get(_oid(der, sig[1], sig[2], sig[3]), "?")
        issuer = _name(der, tbs[i + 2][1])
        val = _children(der, tbs[i + 3][1])
        spki = _children(der, tbs[i + 5][1])
        bits = der[spki[1][1] + spki[1][2] + 1:spki[1][1] + spki[1][2] + spki[1][3]]
        rsa = _children(bits, 0)
        mod = bits[rsa[0][1] + rsa[0][2]:rsa[0][1] + rsa[0][2] + rsa[0][3]]
        return {
            "serial": serial, "sigalg": sigalg, "issuer": issuer,
            "not_before": _time(der, val[0][1], val[0][2], val[0][3]),
            "not_after": _time(der, val[1][1], val[1][2], val[1][3]),
            "rsa_bits": int.from_bytes(mod, "big").bit_length(),
        }
    except Exception:
        return None


# --------------------------------------------------------------------------- main analysis
def parse_logo_image(buf, m, ch, check_levels, cache, warn):
    """Table + slots for a 'logo*' image whose MTK header begins with 'm'."""
    p = m + HDR
    name = ch["name"]
    img = {"name": name, "offset": m, "header": ch, "slots": [], "fatal": False}
    if p + 8 > len(buf):
        img["fatal"] = True
        img["table"] = {"count": 0, "block_size": 0, "table_bytes": 0, "offsets": [], "min_offset": 0,
                        "issues": ["truncated file: missing offset table"], "cert_inner_len": 0}
        return img
    count, bs = struct.unpack("<II", buf[p:p + 8])
    table_bytes = 8 + 4 * count
    t = {"count": count, "block_size": bs, "table_bytes": table_bytes}
    img["table"] = t
    if table_bytes > ch["dsize"] or p + table_bytes > len(buf):
        t.update(offsets=[], min_offset=(2 + count) * 4, cert_inner_len=0,
                 issues=[f"table declares {count} entries, incompatible with dsize/file"])
        img["fatal"] = True
        return img
    offs = list(struct.unpack(f"<{count}I", buf[p + 8:p + 8 + 4 * count]))
    t["offsets"] = offs
    min_off = (2 + count) * 4
    issues = []
    if bs > ch["dsize"]:
        issues.append(f"block_size {bs} > dsize {ch['dsize']}")
    prev = 0
    for i, o in enumerate(offs):
        if o < min_off:
            issues.append(f"offset[{i}]={o} below minimum {min_off}")
        if o > bs:
            issues.append(f"offset[{i}]={o} above block_size")
        if o < prev:
            issues.append(f"offset[{i}] non-monotonic ({o} < {prev})")
        prev = max(prev, o)
    if p + bs > len(buf):
        issues.append(f"block_size exceeds the file size (missing {p + bs - len(buf)} B)")
    t["min_offset"], t["issues"] = min_off, issues
    t["cert_inner_len"] = ch["dsize"] - bs
    if issues:
        img["fatal"] = True
        return img
    ends = offs[1:] + [bs]
    for i, (o, e) in enumerate(zip(offs, ends)):
        blob = buf[p + o:p + e]
        s = {"img": name, "id": i, "comp": len(blob), "zhdr": blob[:2].hex(),
             "md5": hashlib.md5(blob).hexdigest()}
        try:
            d = zlib.decompressobj()
            raw = d.decompress(blob)
            if d.unused_data or not d.eof:
                raise zlib.error("extra data or incomplete flow")
            s["zlib"] = True
        except zlib.error:
            raw, s["zlib"] = blob, False
            warn(f"{name} slot {i}: not a valid zlib stream (treated as raw)")
        s["raw"] = len(raw)
        s["_blob"] = blob          # only the compressed version remains in memory; the raw data is recalculated on demand
        s["level"] = None
        if check_levels and s["zlib"]:
            key = s["md5"]
            if key not in cache:
                cands = {3: (9, 8, 7), 2: (6,), 1: (5, 4, 3, 2), 0: (1,)}[blob[1] >> 6]
                cache[key] = next((lv for lv in cands if zlib.compress(raw, lv) == blob), 0)
            s["level"] = cache[key] or None
        img["slots"].append(s)
    return img


def analyze(path, check_levels=True):
    """Iterates through ALL MTK images in the container (logo1, logo2, cert1, cert2, ...)."""
    buf = open(path, "rb").read()
    r = {"path": path, "file_size": len(buf), "warnings": [], "levels_checked": bool(check_levels)}
    warn = r["warnings"].append

    hdr = parse_mtk_header(buf)
    r["header"] = hdr
    if not hdr["name"].upper().startswith("LOGO"):
        raise LogoError(f"the header type is '{hdr['name']}', no 'logo'")
    if not hdr["extended"]:
        warn("legacy header (without ext_magic 0x89168958); missing extended fields")

    images, certs, regions, cache = [], [], [], {}
    pos = 0
    while pos < len(buf):
        m = buf.find(MAGIC_BYTES, pos)
        if m < 0:
            break
        if m > pos:
            regions.append(_gap(buf, pos, m))
        try:
            ch = parse_mtk_header(buf, m)
        except LogoError:
            regions.append(_gap(buf, m, min(m + 4, len(buf)), force="unidentified data"))
            pos = m + 4
            continue
        pend = m + HDR + ch["dsize"]
        if pend > len(buf):
            warn(f"header '{ch['name']}' @0x{m:X} declares payload beyond the end of the file")
            pend = len(buf)
        if ch["name"].lower().startswith("logo"):
            img = parse_logo_image(buf, m, ch, check_levels, cache, warn)
            images.append(img)
            t, p = img["table"], m + HDR
            regions.append((f"{ch['name']}: MTK header ", m, p, ""))
            regions.append((f"{ch['name']}: offset table", p, p + t["table_bytes"], f"{t['count']} entries"))
            if t["offsets"] and not img["fatal"]:
                regions.append((f"{ch['name']}: blobs zlib", p + t["offsets"][0], p + t["block_size"], f"{t['count']} slots"))
                if t["cert_inner_len"]:
                    regions.append((f"{ch['name']}: internal cert (dsize-block_size)", p + t["block_size"], pend, ""))
            else:
                regions.append((f"{ch['name']}: invalid payload", p + t["table_bytes"], pend, ""))
            if img["fatal"]:
                warn(f"{ch['name']}: invalid table: " + "; ".join(t["issues"]))
        else:
            payload = buf[m + HDR:pend]
            ch["payload_len"] = len(payload)
            ch["sha256"] = hashlib.sha256(payload).hexdigest()
            ch["x509"] = parse_cert(payload)
            certs.append(ch)
            regions.append((f"{ch['name']} (header + payload)", m, pend, f"{HDR} + {n(ch['dsize'])} B"))
        pos = pend
    if pos < len(buf):
        regions.append(_gap(buf, pos, len(buf)))

    r["images"], r["certs"], r["regions"] = images, certs, regions
    if not images or images[0]["fatal"]:
        r["fatal"] = True
        r["table"] = images[0]["table"] if images else {"issues": ["no logo image found"],
                                                        "count": 0, "block_size": 0, "table_bytes": 0,
                                                        "offsets": [], "min_offset": 0, "cert_inner_len": 0}
        return r
    r["table"] = images[0]["table"]
    r["fatal"] = False
    first = images[0]
    hidden = [im for im in images[1:] if not im["fatal"]]
    r["engine_view"] = {"slots_seen": first["table"]["count"],
                        "cert_bytes": len(buf) - (HDR + first["table"]["block_size"]),
                        "hidden_images": [im["name"] for im in hidden],
                        "hidden_slots": sum(im["table"]["count"] for im in hidden)}
    if hidden:
        warn(f"the mtklogo/GUI reads only the 1st image ({first['name']}: {first['table']['count']} slot(s)); "
             f"{', '.join(im['name'] for im in hidden)} ({r['engine_view']['hidden_slots']} slots) "
             f"converted into 'cert' and not extracted. Use --split.")
    if any(x[0] == "unidentified data" or x[3] == "unidentified data" for x in regions):
        warn("There is data following the blobs that is neither MTK-certified nor zeros")

    # global slots (global IDs; each slot stores the image and the local ID)
    slots = [s for im in images if not im["fatal"] for s in im["slots"]]
    for g, s in enumerate(slots):
        s["gid"] = g
    r["slots"] = slots
    r["comp_total"] = sum(s["comp"] for s in slots)
    r["raw_total"] = sum(s["raw"] for s in slots)
    groups = collections.OrderedDict()
    for s in slots:
        groups.setdefault(s["raw"], []).append(s["gid"])
    r["groups"] = [{"raw": k, "ids": v} for k, v in groups.items()]
    dup = collections.defaultdict(list)
    for s in slots:
        dup[s["md5"]].append(s["gid"])
    r["duplicates"] = [[slots[g]["img"] + ":" + str(slots[g]["id"]) for g in v]
                       for v in dup.values() if len(v) > 1]

    r["mtkimg_size_check"] = (hdr["dsize"] + HDR == len(buf))
    r["end_aligned_4k"] = len(buf) % 4096 == 0

    #  Simple proof: does the payload hash appear within any certificate?
    hit = []
    for im in images:
        if im["fatal"]:
            continue
        m, bs = im["offset"], im["table"]["block_size"]
        probes = {"table+blobs": buf[m + HDR:m + HDR + bs], "header+table+blobs": buf[m:m + HDR + bs]}
        for pn, data in probes.items():
            for hn in ("sha256", "sha1", "md5"):
                dg = hashlib.new(hn, data).digest()
                for c in certs:
                    if dg in buf[c["offset"] + HDR:c["offset"] + HDR + c["dsize"]]:
                        hit.append(f"{hn}({im['name']}:{pn}) inside of {c['name']}")
    r["cert_hash_hits"] = hit

    # ---- color model (alpha channel) by the largest group of 4 B/pixel
    r["alpha"] = _detect_alpha(slots)
    return r


def raw_of(slot):
    """Uncompressed bytes from a slot (or the blob itself, if it is not zlib)."""
    return zlib.decompress(slot["_blob"]) if slot["zlib"] else slot["_blob"]


def _gap(buf, a, b, force=None):
    seg = buf[a:b]
    if force:
        return (force, a, b, force)
    if not any(seg):
        return ("padding (zeros)", a, b, "")
    return ("unidentified data", a, b, "unidentified data")


def _detect_alpha(slots):
    big = max(slots, key=lambda s: s["raw"])
    data = raw_of(big)
    if len(data) % 4:
        return {"bpp": 2, "text": "size not a multiple of 4: likely 16 bpp (RGB565)", "pos": None}
    cnt = len(data) // 4
    if data[3::4].count(255) == cnt:
        return {"bpp": 4, "pos": 3, "text": "32 bpp, alfa = 0xFF at the 4th byte (bgrabe ou rgbabe)"}
    if data[0::4].count(255) == cnt:
        return {"bpp": 4, "pos": 0, "text": "32 bpp, alfa = 0xFF at the 1st byte (rgbale ou bgrale)"}
    return {"bpp": 4, "pos": None, "text": "without constant alpha: 16 bpp (RGB565) or 32 bpp with variable alpha"}


# --------------------------------------------------------------------------- profiles (mtklogo.yaml)
def find_yaml(explicit):
    cands = [explicit] if explicit else [
        "mtklogo.yaml", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mtklogo.yaml"),
        os.path.expanduser("~/.config/mtklogo.yaml"), "/etc/mtklogo.yaml", "~/mtklogo-gui/mtklogo.yaml"]
    return next((c for c in cands if c and os.path.isfile(c)), None)


def load_profiles(path):
    try:
        import yaml
    except ImportError:
        return None, "Missing PyYAML (pip install pyyaml); profile ranking ignored"
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return d.get("profiles", []), None


def guess(profile, size):
    """Equivalent to Profile::guess_format: integer division and first format with w*h equal."""
    bpp = MODES[profile["color_model"]][0]
    px = size // bpp
    return next((f for f in profile["formats"] if f["w"] * f["h"] == px), None)


def rank_profiles(r, profiles):
    sizes = [s["raw"] for s in r["slots"]]
    rows = []
    for p in profiles:
        if p.get("color_model") not in MODES:
            continue
        matched = sum(1 for z in sizes if guess(p, z))
        rows.append({"name": p["name"], "mode": p["color_model"], "matched": matched, "profile": p})
    # Tie-breaker: profiles usually have the full-screen name (e.g., 720x1612); prefer that one.
    big = max(sizes)

    def name_hit(row):
        f = guess(row["profile"], big)
        names = [row["name"]] + list(row["profile"].get("alias") or [])
        return 0 if f and f"{f['w']}x{f['h']}" in names else 1

    rows.sort(key=lambda x: (-x["matched"], name_hit(x), x["name"]))
    return rows


def ambiguities(r, rows, best):
    """Pixel counts of the winning profile that appear with different dimensions on other profiles."""
    out = []
    for g in r["groups"]:
        f = guess(best["profile"], g["raw"])
        if not f:
            continue
        alt = set()
        for row in rows:
            if row is best:
                continue
            f2 = guess(row["profile"], g["raw"])
            if f2 and (f2["w"], f2["h"]) != (f["w"], f["h"]):
                alt.add(f"{f2['w']}x{f2['h']}")
        if alt:
            out.append((g["raw"], f"{f['w']}x{f['h']}", sorted(alt)[:4]))
    return out


# --------------------------------------------------------------------------- dimension inference
def factor_pairs(px):
    out = []
    i = 1
    while i * i <= px:
        if px % i == 0:
            out.append((i, px // i))
            if i != px // i:
                out.append((px // i, i))
        i += 1
    return out


def smooth_rank(raw, bpp, alpha_pos, px, max_px=150_000, top=3):
    """Scores candidate widths based on continuity between neighboring lines (lower = better)."""
    if bpp != 4 or px > max_px:
        return []
    ch = (0, 1, 2) if alpha_pos == 3 else (1, 2, 3)
    lum = [raw[i + ch[0]] + raw[i + ch[1]] + raw[i + ch[2]] for i in range(0, px * 4, 4)]
    res = []
    for w, h in factor_pairs(px):
        if w < 8 or h < 8:
            continue
        dv = sum(abs(lum[i + w] - lum[i]) for i in range(px - w))
        dh = sum(abs(lum[i + 1] - lum[i]) for i in range(px - 1) if (i + 1) % w)
        res.append(((dv / (px - w)) / ((dh / max(1, px - px // w)) + 1e-9), w, h))
    res.sort()
    return [(w, h, round(sc, 2)) for sc, w, h in res[:top]]


def infer_groups(r):
    a = r["alpha"]
    out = {}
    for g in r["groups"]:
        size, bpp = g["raw"], a["bpp"]
        info = {"known": [], "heuristic": [], "line": None}
        if size % bpp == 0:
            px = size // bpp
            for w, h in COMMON:
                if w * h == px:
                    info["known"].append(f"{w}x{h}")
            data = raw_of(r["slots"][g["ids"][0]]) if size <= 600_000 else b""
            info["heuristic"] = smooth_rank(data, bpp, a["pos"], px)
            if px <= 1024:
                info["line"] = f"{px}x1"
        out[size] = info
    # strip: a few rows with the same width as an already inferred image (e.g., a 363x3 load row))
    widths = sorted({i["heuristic"][0][0] for i in out.values() if i["heuristic"] and i["heuristic"][0][0] >= 32})
    for g in r["groups"]:
        if g["raw"] % a["bpp"] == 0 and g["raw"] // a["bpp"] <= 20000:
            px = g["raw"] // a["bpp"]
            for w in widths:
                if px % w == 0 and 1 <= px // w <= 8:
                    out[g["raw"]]["strip"] = f"{w}x{px // w}"
                    break
    return out


# --------------------------------------------------------------------------- PNG export
def to_rgba(data, mode, w, h):
    px = w * h
    if mode in ("rgb565be", "rgb565le"):
        import array
        a = array.array("H")
        a.frombytes(data[:px * 2])
        if (mode == "rgb565be") == (sys.byteorder == "little"):
            a.byteswap()
        out = bytearray(px * 4)
        for i, v in enumerate(a):
            r5, g6, b5 = (v >> 11) & 31, (v >> 5) & 63, v & 31
            out[4 * i:4 * i + 4] = bytes(((r5 << 3) | (r5 >> 2), (g6 << 2) | (g6 >> 4),
                                           (b5 << 3) | (b5 >> 2), 255))
        return bytes(out)
    order = {"rgbabe": (0, 1, 2, 3), "rgbale": (3, 2, 1, 0),
             "bgrabe": (2, 1, 0, 3), "bgrale": (1, 2, 3, 0)}[mode]    # byte index for R,G,B,A
    out = bytearray(px * 4)
    for k in range(4):
        out[k::4] = data[order[k]:px * 4:4]
    return bytes(out)


def write_png(path, rgba, w, h):
    def chunk(tag, body):
        c = struct.pack(">I", len(body)) + tag + body
        return c + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
    stride = w * 4
    raw = b"".join(b"\x00" + rgba[y * stride:(y + 1) * stride] for y in range(h))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def export(r, outdir, mode, dims_for, opaque):
    os.makedirs(outdir, exist_ok=True)
    bpp = MODES[mode][0]
    done, thumbs = [], []
    multi = len({s["img"] for s in r["slots"]}) > 1
    pre = (lambda s: s["img"] + "_") if multi else (lambda s: "")
    for s in r["slots"]:
        d = dims_for(s["raw"])
        if d and s["raw"] % bpp == 0 and d[0] * d[1] * bpp == s["raw"]:
            w, h = d
            rgba = to_rgba(raw_of(s), mode, w, h)
            if opaque:
                b = bytearray(rgba)
                b[3::4] = b"\xff" * (w * h)
                rgba = bytes(b)
            fn = os.path.join(outdir, f"{pre(s)}{s['id']:02d}_{w}x{h}.png")
            write_png(fn, rgba, w, h)
            done.append((s["id"], fn, w, h))
            thumbs.append((pre(s) + str(s["id"]), fn, w, h))
        else:
            fn = os.path.join(outdir, f"{pre(s)}{s['id']:02d}_raw_{s['raw']}.bin")
            open(fn, "wb").write(raw_of(s))
            done.append((s["id"], fn, None, None))
    try:
        from PIL import Image, ImageDraw
        cols, cw, ch = 10, 150, 150
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cw, max(1, rows) * ch), (36, 36, 36))
        dr = ImageDraw.Draw(sheet)
        for k, (i, fn, w, h) in enumerate(thumbs):
            im = Image.open(fn).convert("RGB")
            if h == 1:
                im = im.resize((w, 10))
            im.thumbnail((cw - 10, ch - 26))
            x, y = (k % cols) * cw + 5, (k // cols) * ch + 4
            sheet.paste(im, (x, y))
            dr.text((x, y + ch - 22), f"{i} {w}x{h}", fill=(220, 220, 220))
        sheet.save(os.path.join(outdir, "_contact_sheet.png"))
    except ImportError:
        pass
    return done


# --------------------------------------------------------------------------- text report
def fmt_ids(r, gids, limit=8):
    """Global IDs -> 'logo1:0 | logo2:3..12' (consecutive strips per image)."""
    by = collections.OrderedDict()
    for g in gids:
        s = r["slots"][g]
        by.setdefault(s["img"], []).append(s["id"])
    parts = []
    for im, ids in by.items():
        runs, a, b = [], ids[0], ids[0]
        for x in ids[1:]:
            if x == b + 1:
                b = x
            else:
                runs.append((a, b)); a = b = x
        runs.append((a, b))
        txt = ",".join(f"{x}" if x == y else f"{x}..{y}" for x, y in runs)
        parts.append((im + ":" if len(by) > 1 or len(r["images"]) > 1 else "") + txt)
    out = " | ".join(parts)
    return out if len(out) <= 40 else out[:37] + "..."


def bar(title):
    print(f"\n== {title} " + "=" * max(3, 66 - len(title)))


def hx(v):
    return f"0x{v:08X}"


def report(r, rows=None, yaml_note=None, top=7):
    h, t = r["header"], r.get("table")
    print(f"logo_structure {VERSION} - {r['path']}")
    print(f"file size: {n(r['file_size'])} B (0x{r['file_size']:X})")

    bar("MTK Header (512 B)")
    print(f"magic        0x88168858 OK")
    print(f"tipo         '{h['name']}' ({'Legacy LOGO' if h['legacy_logo'] else 'tiny logo'})")
    print(f"dsize        {n(h['dsize'])} (0x{h['dsize']:X})")
    print(f"addr / mode  {hx(h['addr'])} / {hx(h['mode'])}")
    if h["extended"]:
        print("extended    yes (ext_magic 0x89168958)")
        print(f"hdr_size={h['hdr_size']} hdr_ver={h['hdr_ver']} img_type={h['img_type']} "
              f"img_list_end={h['img_list_end']} align_size={h['align_size']}")
        print(f"dsize_ext={h['dsize_ext']} addr_ext={hx(h['addr_ext'])} scrambled={hx(h['scrambled'])}")
    else:
        print("extended    no (legacy_logo)")
    print(f"reserved    {'todo 0xFF' if h['reserved_all_ff'] else 'contains data (preserved in the repack)'}")

    imgs = r.get("images", [])
    if len(imgs) > 1:
        bar(f"Container with {len(imgs)} logo images")
        for im in imgs:
            ih, it = im["header"], im["table"]
            print(f"  {ih['name']:<6} @0x{im['offset']:X}  dsize={n(ih['dsize'])}  slots={it['count']}  "
                  f"img_type={hx(ih.get('img_type', 0))}  img_list_end={ih.get('img_list_end', '-')}"
                  + ("  [INVALID TABLE]" if im["fatal"] else ""))
        print("  (each image has its own table of offsets and its certificates; the last cert2 with img_list_end=1 close the list)")

    for im in imgs:
        t = im["table"]
        bar(f"Offset table ({im['name']})" if len(imgs) > 1 else "Offset table")
        print(f"logo_count={t['count']}  block_size={n(t['block_size'])}  table={t['table_bytes']} B")
        if t["issues"]:
            for x in t["issues"]:
                print(f"  ! {x}")
            print("Invalid structure in this image file.")
            if im is imgs[0]:
                return
            continue
        print(f"offsets[0]={t['offsets'][0]} (minimum {t['min_offset']}) "
              f"{'OK' if t['offsets'][0] == t['min_offset'] else 'different from the minimum'}; "
              "monotonic and within block_size: OK")
        print(f"internal cert (dsize - block_size) = {t['cert_inner_len']} B")

    bar("Map of regions")
    for name, a, b, note in r["regions"]:
        print(f"  0x{a:06X}-0x{b:06X}  {n(b - a):>10} B  {name}" + (f"  [{note}]" if note and note != name else ""))
    print(f"  end of file aligned to 4 KiB: {'yes' if r['end_aligned_4k'] else 'no'}"
          f"   |  check dsize+512 == size: {'OK' if r['mtkimg_size_check'] else 'not valid (certs/multiple image files)'}")

    ev = r.get("engine_view")
    if ev and ev["hidden_images"]:
        bar("mtklogo view / GUI (LogoImage::read)")
        print(f"The engine reads ONE table ({ev['slots_seen']} slot(s)) and keeps everything else as 'cert' ({n(ev['cert_bytes'])} B).")
        print(f"Images that it does NOT extract: {', '.join(ev['hidden_images'])} ({ev['hidden_slots']} slots).")
        print("Solution: --split DIR generates one file per image; open each one in the GUI and use --join to repack.")

    if r["certs"]:
        bar("Certificates")
        for c in r["certs"]:
            print(f"{c['name']}: @0x{c['offset']:X}, payload {n(c['dsize'])} B, img_type={hx(c.get('img_type', 0))}, "
                  f"img_list_end={c.get('img_list_end', '-')}, sha256={c['sha256'][:16]}...")
            x = c["x509"]
            if x:
                print(f"   X.509: {x['sigalg']}, RSA {x['rsa_bits']} bits, emissor [{x['issuer']}], "
                      f"validity {x['not_before']} a {x['not_after']}, serial {x['serial']}")
            else:
                print("   payload is not a readable X.509 DER.")
        print("   payload hash inside the certs: " +
              ("; ".join(r["cert_hash_hits"]) if r["cert_hash_hits"] else "not found (simple test, inconclusive)"))

    bar("Slots")
    lv = collections.Counter(s["level"] for s in r["slots"] if s["zlib"])
    zh = collections.Counter(s["zhdr"] for s in r["slots"])
    print(f"{len(r['slots'])} slots; zlib: {dict(zh)}; "
          f"compressed {n(r['comp_total'])} B / raw_total {n(r['raw_total'])} B "
          f"({100 * r['comp_total'] / max(1, r['raw_total']):.1f}%)")
    reproduced = sum(c for k, c in lv.items() if k)
    if r["levels_checked"]:
        print(f"byte-for-byte reproducible by zlib: {reproduced}/{len(r['slots'])}"
              + (f" (level {', '.join(str(k) for k in lv if k)})" if reproduced else ""))
    else:
        print("zlib reproduction: unverified (--no-recompress)")
    if r["duplicates"]:
        print(f"identical blobs: {r['duplicates']}")
    inf = infer_groups(r)
    print("\n  raw bytes  qty  slots                                    dimension")
    for g in r["groups"]:
        ids = g["ids"]
        txt = fmt_ids(r, ids)
        dim = ""
        if rows:
            f = guess(rows[0]["profile"], g["raw"])
            if f:
                dim = f"{f['w']}x{f['h']}" + (f" ({f['t']})" if f.get("t") else "")
            else:
                i = inf[g["raw"]]
                dim = "NO PROFILE (.z)"
                if i["heuristic"]:
                    dim += "; heuristic: " + ", ".join(f"{w}x{hh}" for w, hh, _ in i["heuristic"][:3])
                if i.get("strip"):
                    dim += f"; or strip {i['strip']}"
                elif i["line"]:
                    dim += f"; or line {i['line']}"
        else:
            i = inf[g["raw"]]
            dim = ", ".join(i["known"]) or ""
            if not dim and i["heuristic"]:
                dim = "heuristic: " + ", ".join(f"{w}x{hh}" for w, hh, _ in i["heuristic"])
            if i.get("strip") and not i["known"]:
                dim = (dim + "; or " if dim else "") + f"strip {i['strip']}"
            elif i["line"] and not i["known"]:
                dim = (dim + "; or " if dim else "") + f"line {i['line']}"
        print(f"  {g['raw']:>12}  {len(ids):>3}  {txt:<40} {dim}")

    bar("Color model")
    print(r["alpha"]["text"])
    print("BGR vs. RGB cannot be detected automatically: use --export and check the colors.")

    if rows:
        bar(f"mtklogo.yaml profiles (best {top})")
        for row in rows[:top]:
            tag = "  <-- best" if row is rows[0] else ""
            print(f"  {row['matched']:>2}/{len(r['slots'])}  {row['name']} ({row['mode']}){tag}")
        best = rows[0]
        und = [s["gid"] for s in r["slots"] if not guess(best["profile"], s["raw"])]
        if und:
            print(f"unformatted slots in the profile '{best['name']}' (staying .z): {len(und)}: {fmt_ids(r, und)}")
        else:
            print(f"profile '{best['name']}' covers all slots.")
        amb = ambiguities(r, rows, best)
        if amb:
            print("ambiguities (same pixel count but a different dimension in another profile):")
            for size, ok, alt in amb:
                print(f"  {n(size)} B: chosen {ok}; too {', '.join(alt)}")
        if len(rows) > 1 and rows[1]["matched"] == rows[0]["matched"]:
            print("Attention: a tie at the top; matching slots does not confirm the correct dimension — check visually.")
    elif yaml_note:
        print(f"\n(note) {yaml_note}")

    if r["warnings"]:
        bar("Warnings")
        for w in r["warnings"]:
            print(f"  ! {w}")


def _tail_pad(r):
    last = r["regions"][-1]
    return (n(last[2] - last[1]) + " B") if last[0].startswith("preench") else "0 B"


def compare(a, b):
    bar("Comparison")
    sig = lambda r: [(s["img"], [g["raw"] for g in r["groups"]].index(s["raw"])) for s in r["slots"]]
    rows = [
        ("file", a["path"], b["path"]),
        ("size", n(a["file_size"]), n(b["file_size"])),
        ("logo images", ",".join(i["name"] for i in a["images"]), ",".join(i["name"] for i in b["images"])),
        ("slots", len(a["slots"]), len(b["slots"])),
        ("distinct sizes", " ".join(n(g["raw"]) for g in a["groups"]),
         " ".join(n(g["raw"]) for g in b["groups"])),
        ("final filling", _tail_pad(a), _tail_pad(b)),
    ]
    for ca in a["certs"]:
        cb = next((c for c in b["certs"] if c["name"] == ca["name"]), None)
        rows.append((ca["name"] + " sha256", ca["sha256"][:16], cb["sha256"][:16] if cb else "-"))
    w = max(len(str(x[0])) for x in rows)
    for k, x, y in rows:
        print(f"  {k:<{w}}  A: {x}\n  {'':<{w}}  B: {y}")
    same = len(a["slots"]) == len(b["slots"]) and sig(a) == sig(b)
    print(f"slot map (grouped by size): {'IDENTICAL (same template)' if same else 'different'}")
    for ca in a["certs"]:
        cb = next((c for c in b["certs"] if c["name"] == ca["name"]), None)
        if cb:
            print(f"{ca['name']}: {'identical' if ca['sha256'] == cb['sha256'] else 'different'}")


def split_container(r, buf, outdir):
    """Save each image (along with the certificates that accompany it) as a separate file."""
    os.makedirs(outdir, exist_ok=True)
    imgs = [im for im in r["images"] if not im["fatal"]]
    outs = []
    for k, im in enumerate(imgs):
        a = im["offset"]
        b = imgs[k + 1]["offset"] if k + 1 < len(imgs) else len(buf)
        fn = os.path.join(outdir, f"{im['name']}.bin")
        open(fn, "wb").write(buf[a:b])
        outs.append((im["name"], fn, a, b))
    return outs


def engine_read(path):
    """What mtklogo (LogoImage::read) sees in a file: read slots and 'cert' bytes."""
    d = open(path, "rb").read()
    h = parse_mtk_header(d)
    count, bs = struct.unpack("<II", d[HDR:HDR + 8])
    offs = struct.unpack(f"<{count}I", d[HDR + 8:HDR + 8 + 4 * count])
    ok = bs <= h["dsize"] and offs[0] == (2 + count) * 4 and max(offs) <= bs and HDR + bs <= len(d)
    return {"name": h["name"], "slots": count if ok else 0, "cert_bytes": len(d) - (HDR + bs), "ok": ok}


def join_pieces(out, pieces):
    """Concatenates the files, ensuring the start of each image is aligned to 16 B (align_size)."""
    data = b""
    for pth in pieces:
        if len(data) % 16:
            data += b"\0" * (16 - len(data) % 16)
        data += open(pth, "rb").read()
    open(out, "wb").write(data)
    return len(data)


def public(r):
    """Serializable version (excluding the slot bytes)."""
    d = dict(r)
    d["slots"] = [{k: v for k, v in s.items() if not k.startswith("_")} for s in r.get("slots", [])]
    d["regions"] = [list(x) for x in r.get("regions", [])]
    d["images"] = [{k: v for k, v in im.items() if k != "slots"} | {"slot_count": len(im["slots"])}
                   for im in r.get("images", [])]
    return d


def main():
    ap = argparse.ArgumentParser(description="Structural report of a MediaTek logo.bin file (read-only).")
    ap.add_argument("logo", nargs="?", help="logo.bin file")
    ap.add_argument("--split", metavar="DIR", help="record logo1.bin, logo2.bin... (one file per container image)")
    ap.add_argument("--join", nargs="+", metavar=("OUT", "PART"),
                    help="repacking: --join new.bin logo1.bin logo2.bin (align each part to 16 B))")
    ap.add_argument("--yaml", help="mtklogo.yaml (default: ./, alongside the script, ~/.config, /etc, ~/mtklogo-gui)")
    ap.add_argument("--compare", metavar="OTHER", help="compare the structure with another logo.bin")
    ap.add_argument("--export", metavar="DIR", help="saves PNGs of the slots (and .bin files of unknown slots)")
    ap.add_argument("--mode", default=None, choices=sorted(MODES),
                    help="color mode of --export (default: that of the best profile, or bgrabe)")
    ap.add_argument("--assume", action="append", default=[], metavar="BYTES=WxH",
                    help="imension of a raw size forced, e.g.: 25704=189x34 (repeatable)")
    ap.add_argument("--opaque", action="store_true", help="--export: alpha force 255 in PNGs")
    ap.add_argument("--no-recompress", action="store_true", help="skips the zlib reproduction test (faster)")
    ap.add_argument("--top", type=int, default=7, help="number of profiles to list (default 7)")
    ap.add_argument("--json", action="store_true", help="JSON output instead of text")
    a = ap.parse_args()

    if a.join:
        if len(a.join) < 2:
            print("erro: use --join OUT PART1 [PART2 ...]", file=sys.stderr)
            return 2
        try:
            total = join_pieces(a.join[0], a.join[1:])
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        print(f"{a.join[0]}: {n(total)} B from {len(a.join) - 1} part(s)")
        return 0
    if not a.logo:
        ap.error("provide the logo.bin file (or use --join)")

    try:
        r = analyze(a.logo, check_levels=not a.no_recompress)
    except (LogoError, OSError) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 2

    rows, note, ypath = None, None, find_yaml(a.yaml)
    if a.yaml and not ypath:
        print(f"error: yaml '{a.yaml}' not found", file=sys.stderr)
        return 2
    if ypath and not r.get("fatal"):
        profs, note = load_profiles(ypath)
        if profs:
            rows = rank_profiles(r, profs)
            if not rows:
                rows = None
    elif not ypath:
        note = "without mtklogo.yaml: dimensions determined via a list of common resolutions and heuristics. Use --yaml for profile ranking."

    if a.json:
        out = public(r)
        if rows:
            out["profiles"] = [{"name": x["name"], "mode": x["mode"], "matched": x["matched"]} for x in rows[:a.top]]
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    else:
        report(r, rows, note, a.top)
        if a.compare and not r.get("fatal"):
            try:
                compare(r, analyze(a.compare, check_levels=False))
            except (LogoError, OSError) as e:
                print(f"error in comparison: {e}", file=sys.stderr)
                return 2

    if r.get("fatal"):
        return 3

    if a.split:
        buf = open(a.logo, "rb").read()
        outs = split_container(r, buf, a.split)
        if not a.json:
            print(f"\n== --split -> {a.split}/ ==")
            for nm, fn, x, y in outs:
                e = engine_read(fn)
                print(f"  {os.path.basename(fn):<10} 0x{x:X}-0x{y:X} ({n(y - x)} B)  the mtklogo reads {e['slots']} slot(s)"
                      f" + {n(e['cert_bytes'])} B de cert" + ("" if e["ok"] else "  [INVALID]"))
            rebuilt = b"".join(open(fn, "rb").read() for _, fn, _, _ in outs)
            print("  concatenation of the parts == original file:", "yes (byte by byte)" if rebuilt == buf else "NO")
            print(f"  remount: python3 logo_structure.py --join logo_new.bin {' '.join(os.path.basename(f) for _, f, _, _ in outs)}")

    if a.export:
        assume = {}
        for item in a.assume:
            try:
                k, v = item.split("=")
                w, h = v.lower().split("x")
                assume[int(k)] = (int(w), int(h))
            except ValueError:
                print(f"error: --assume '{item}' invalid (use BYTES=WxH)", file=sys.stderr)
                return 2
        mode = a.mode or (rows[0]["mode"] if rows else "bgrabe")
        best = rows[0]["profile"] if rows else None

        def dims_for(size):
            if size in assume:
                return assume[size]
            if best:
                f = guess(best, size)
                if f:
                    return (f["w"], f["h"])
            known = [(w, h) for w, h in COMMON if w * h * MODES[mode][0] == size]
            return known[0] if len(known) == 1 else None

        done = export(r, a.export, mode, dims_for, a.opaque)
        if not a.json:
            ok = sum(1 for d in done if d[2])
            print(f"\nexported {ok} PNG(s) and {len(done) - ok} raw block(s) in {a.export}/ (mode {mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
