# Structural analysis of logo.bin (MTK)

By Claude · October 26, 2026 · Based on the methodology from lopestom/mtklogo_gui (branch mtklogo_v1.2 and `mtklogo_v1.3` a PC dedicated `mtklogo_v1.3` folder)

## Method and validation
I applied the repository methodology to `logo.bin`. I did not run their `mtklogo` binary: the "suggested" YAML and the executable are not accessible by direct URL, and the analysis environment did not have Rust. Instead, I reproduced the upstream source logic in Python (`header.rs`, `logo.rs`, and `Profile::guess_format`).

As a control, I ran the same code on the repo's example `logo.bin`: the ranking matches what `ANALYSIS_AND_SUGGESTIONS.md` documents for `1440x3200` (49/60) and `1218x2160` (33/60).

## File structure (3,137,536 B = 0x2FE000)
| Region | Offset | Size | Content |
| --- | --- | --- | --- |
| MTK header | 0x000 | 512 B | magic `88168858`, name `logo` (lowercase), extended header (`ext_magic 0x89168958`), `hdr_ver=1`, `align_size=16`, `dsize=3,131,086`, rest `0xFF` |
| Table | 0x200 | 248 B | `logo_count=60`, `block_size=3,131,086`, 60 offsets (the first is 248, the minimum valid) |
| Blobs | 0x2F8 | 3,130,838 B | 60 zlib blobs |
| Alignment | 0x2FC8CE | 2 B | zeros |
| cert1 | 0x2FC8D0 | 512 + 1,709 B | own MTK header + X.509 DER chain |
| cert2 | 0x2FD180 | 512 + 995 B | same, `img_list_end=1` (marks the end of the list) |
| Padding | 0x2FD764 | 2,205 B | zeros up to the 4 KiB limit (766 pages) |

The `LogoTable::read` validations pass: non-decreasing offsets, all between the minimum and `block_size`, `block_size ≤ dsize`, and `dsize == block_size` (so `cert_inner_len = 0`).

## Slots (map identical to the repo example)
- File structure
- Valid MTK header (88 16 88 58), type logo, 60 blocks, all zlib.
- Color model: 32 bpp with alpha byte 0xFF in the 4th position, order B,G,R,A (`bgrabe` in your YAML). When rendered this way, the battery comes out orange and the background dark teal, correct. It is not RGB565.
- Slots 0, 2, and 38 are identical (the same boot logo reused).

| Slots | Raw size (bytes) | Resolution | Function | YAML? |
| :---: | :---: | :---: | :---: | :---: |
| 0–3, 25–35, 37–48 (27) | 4,642,560 | 720×1612 | full screens (Ulefone logo, charger warning, battery levels) | ✅ profile 720x1612 |
| 4–13 | 11,520 | 45×64 | digits 0–9 | ✅ |
| 14 | 14,592 | 57×64 | `%` symbol | ✅ |
| 15–24 | 25,704 | 189×34 | charging animation (10 frames) | ❌ |
| 36 | 756 | 189×1 | charging line | ❌ |
| 49–59 | 36,864 | 72×128 | large digits 0–9 and `%` symbol (11) | ✅ |

The blobs 0, 2, and 38 are identical. All 60 start with `78 DA` and are byte-for-byte equal to zlib level 9, the same that `mtklogo` uses (`Compression::best()`). They occupy 2.5% of the raw size (3.13 MB versus 126 MB).

## Profile detection (emulating "Detect profile")
| YAML used | Best profile | Matched slots |
| --- | --- | --- |
| Original (user upload) | `720x1612` | 49/60 (11 become `.z`: 15–24 and 36) |
| Corrected (generated in this conversation) | `720x1612` | 60/60 |
| Upstream cyberknight777 | `s666ln` | 28/60 |
| Repo "suggested" (emulated from the docs) | `720x1600` | 22/60 |

The repo's `720x1600` profile fails on the full screens of this file because 1612 ≠ 1600, and the repo's `exp_*` profiles do not have `720x1612`.

The 28/60 for `s666ln` has a false positive: slot 14 "matches" 152×24 only because 57×64 = 152×24 = 3,648 px. "Matched slots" does not prove that the dimension is right, so visual confirmation is still necessary.

## Comparison with the repo's example logo.bin
|  | This file | Repo example |
| --- | --- | --- |
| Full screen | 720×1612 | 720×1600 |
| Animation / line | 189×34 / 189×1 | 180×32 / 360×1 |
| `dsize` | 3,131,086 | 2,970,035 |
| cert1 | identical | identical |
| cert2 | different |2 different |
| Final padding | 2,205 B (4 KiB aligned) | 13 B (16 aligned) |

The same 60-slot layout indicates the same OEM template, only with a different resolution.
### How I arrived at the two new resolutions
189×34: 6,426 px admits few plausible factorizations. This was the one that gave the best continuity between lines, and the rendering confirmed it: a continuous and coherent blue wave across the 10 frames.

189×1: it has the same width as the animation. This is the pattern that the other profiles follow (163×29 with 163×1, 304×52 with 304×1).

Discarded: the `s666ln` profile (itel RS4) also has a 720×1612 screen, but its digits are 28×40, and here they are 45×64. This file belongs to the `720x1612` profile family.

72×128 (blocks 49–59) comes from the best continuity among the candidates and from matching existing profiles. I did not render this group.

Without the two new entries, the tool would leave 11 blocks as raw `.z`. Add the following to the `720x1612` profile:

```yaml
    - { w: 189, h: 34, t: "battery charge animation" }
    - { w: 189, h: 1,  t: "battery charge line" }
```

### Other findings
Wrong comment in that profile: it says "3135344 bytes" for the full screen, but the correct value is 4,642,560 (720×1612×4). Also, 3,135,344 looks like the approximate size of this `logo.bin` (3,137,536), so the comment was probably taken from the file and not from the image.

The file has 5,938 bytes after the logical end. The header size field is 3,131,086, and 3,131,086 + 512 = 3,131,598, but the file is 3,137,536. The `mtk_header_check_size` from `tools.c` (`size+512 == file size`) would reject this file. If a tool based on it fails, that is the reason. It is necessary to tolerate the excess or remove it when repacking, and the repacker must recalculate the size field.

This reinforces the previous thesis about the default: the framebuffer is 1612 and not 1600. The "strange" values come from the bootloader, and validation by file size remains the reliable method.

## Corrections to previous statements
1. I had written that the final 5,938 bytes were excess or garbage and that it would be good to "tolerate or remove" them. I was wrong: it is the `cert1` + `cert2` chain. Upstream preserves it in the repack (`cert` field), so it should not be removed. The `mtkimg` (rom1nux) check `size+512 == size` still rejects this file, but for a legitimate reason.
2. `cert1` points to "Mediatek", validity 2015–2035, RSA with SHA-256. Its being identical to the example suggests a generic template certificate. The fact that `cert2` differs is compatible with it depending on the content, but this was not proven: the search for SHA-256, SHA-1, and MD5 of the payload inside the certificates found nothing.
3. If the device applies signature verification (secure boot), an edited logo may be rejected even with the certificates preserved. This cannot be asserted for the specific model. Back up the `logo` partition before flashing, as the repo itself warns.

## Limitations
- The repo's `mtklogo` binary was not executed; the rankings come from a Python emulation of the source code.
- The repo's "suggested" YAML could not be downloaded; its profiles were emulated from the documentation.
- The relationship between `cert2` and the logo content is a hypothesis, not a verified fact.

## Next possible step
Turn the scripts into a single tool (`logo_structure.py`) that generates this report for any `logo.bin`.


------____
*It was implemented as described below.*
------____
# logo_structure.py: faithful export and structural report

## Table of Contents

- [Intro](#intro)
- [Usage](#usage)
- [What the report covers](#what-the-report-covers)
- [Useful options](#useful-options)
- [Limits](#limits)

## Intro

I’ll check the upstream source to see how each color mode maps bytes to RGBA, so the script’s `--export` stays faithful to `mtklogo`.

I already have the upstream color-mode mapping. I’ll write the tool using only the Python standard library (PyYAML and Pillow remain optional).

`logo_structure.py` is ready. It runs with only the Python 3 standard library and is read-only: it never modifies `logo.bin`. I ran it on your file and on the repo example, and the report reproduces the numbers from the previous analysis.

## Usage

```bash
python3 logo_structure.py logo.bin                              # full report
python3 logo_structure.py logo.bin --yaml mtklogo.yaml          # + profile ranking
python3 logo_structure.py logo.bin --yaml mtklogo.yaml --export png/
python3 logo_structure.py logo.bin --compare outro_logo.bin
python3 logo_structure.py logo.bin --json > relatorio.json
```

Without `--yaml`, it looks for `mtklogo.yaml` in the current folder, next to the script, in `~/.config`, and in `/etc`.

## What the report covers

- 512 B MTK header with all fields, plus the offset table validated with the same rules as upstream `LogoTable::read`.
- Region map: header, table, blobs, `cert1`, `cert2`, and padding, with offsets and sizes.
- Certificates: reads X.509 without `openssl` (algorithm, RSA, issuer, validity, serial). I checked issuer, validity, serial, and signature size with `asn1parse`; the RSA key size (2048 bits) is what the script itself calculates.
- Slots: zlib level (tests whether each blob reproduces byte for byte), duplicate blobs, and grouping by size.
- Dimensions: uses the winning profile from the YAML. Without YAML, it uses a list of common resolutions and a heuristic. The heuristic got the 45×64, 57×64, 189×34, and 72×128 groups of this file right, but suggested 9×21 for the 756 B line (the correct value is 189×1), so the report also lists the “line 189×1” hypothesis.
- Profile ranking like “Detect profile,” with warnings about ambiguities (the false positive 57×64 = 152×24) and top ties.
- Alert when the `mtkimg` check `dsize+512 == file size` fails, which is the case for your files because of the certificates.

## Useful options

- `--export` saves one PNG per slot and a contact sheet (the latter requires Pillow). Slots with unknown dimensions are saved as raw `.bin`. Use `--assume 25704=189x34` to force a dimension.
- `--mode` chooses the color mode for `--export`, using the same byte convention as upstream. The default is the one from the best profile.
- `--no-recompress` skips the zlib reproduction test.

## Limits

- It does not distinguish BGR from RGB on its own. Use `--export` and look at the colors.
- The dimension heuristic only works for blobs up to 150 thousand pixels. Full screens depend on the YAML or on the common-resolution list.
- Invalid inputs return code 2 (unreadable or non-logo file) or 3 (corrupted table). I tested an empty file, a truncated file, an invalid table, KERNEL type, legacy header, and a slot that is not zlib.

------____
*In fact, following `VERSION = "1.0"` a few improvements, in the `docs/multi-image_report/logo_structure.py` file has been updated to `VERSION = "1.2"`.*
------____
