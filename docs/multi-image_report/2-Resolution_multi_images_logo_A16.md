# Notes on resolution when handling multiple images in logo_A16
The file logo_TANK5_A16.bin was used for the analysis.

## Table of Contents

- [Intro](#intro)
- [What the engine does](#what-the-engine-does)
- [How to get the 59 images in the GUI](#how-to-get-the-59-images-in-the-gui)
- [Before reflashing a modified logo](#before-reflashing-a-modified-logo)

## Intro

Your GUI has no defect: this file has two images (`logo1` and `logo2`) and `mtklogo` only reads the first one. My tool walks every MTK header in the file; the GUI's engine does not.

## What the engine does

The code the GUI embeds (`mtklogo_v1.0.1/src/mtk/logo.rs`, in branch `mtklogo_v1.2` and a PC dedicated `mtklogo_v1.3` folder) reads a single table and the blobs up to `block_size`. Then it reads everything left in the file into a `cert` field, which it only preserves on repack.

Applied to `logo_TANK5_A16.bin`:

| Item | Value |
| --- | --- |
| `logo_count` of `logo1` | 1 |
| `blob_end` | 512 + 155,514 = 156,026 |
| file size | 8,060,256 |
| `"cert"` read | 7,904,230 B |

Those 7.9 MB include the whole `logo2` (59 slots, header at `0x27040`) plus the 4 certificates. That is why only `logo_000_bgrabe.png` appears, which should be the boot screen "8849 – Rugged by Unihertz" (`logo1:0`, identical to `logo2:37`).

I did not run the AppImage or the binary. The conclusion comes from reading the source and from emulating `LogoImage::read` over your file. The emulation yields 1 slot, which matches what you described.

## How to get the 59 images in the GUI

I updated `logo_structure.py` (v1.3). It now warns when the engine would leave images out. It also gained `--split` and `--join`:

```bash
python3 logo_structure.py logo_TANK5_A16.bin --split partes/
# partes/logo1.bin -> mtklogo reads 1 slot
# partes/logo2.bin -> mtklogo reads 59 slots (+ 3,787 B of cert)
```

Open `logo2.bin` in the GUI. To reassemble, use:

```bash
python3 logo_structure.py --join logo_novo.bin logo1.bin logo2.bin
```

Split/join test: concatenating the parts reproduces the original byte for byte. `--join` re-aligns each image to 16 B when an edited part changes size, and I tested this with a `logo1` enlarged by 5 bytes.

YAML: the GUI only generates PNGs for the slots the profile knows. Use the `mtklogo.yaml` I updated, with `363×65`, `363×3`, and `108×192` in the `1440x3200` profile. Without that, 22 of the 59 slots come out as `.z` instead of as an image. I do not know which folder the GUI stores the YAML in, so copy those three formats into whatever it uses.

## Before reflashing a modified logo

- I do not know which image the device uses at each boot stage. The boot screen exists in both (`logo1:0` and `logo2:37`), so editing only one may have no effect.
- The certificates come with each image. I have not proven what `cert2` signs, and an edited logo may be rejected.
- **Back up the `logo` partition first**, as the project's own README asks.

------____
*In fact, the file `docs/multi-image_report/logo_structure.py` has been updated to `VERSION = "1.2"` as a result of this analysis.*
------____
