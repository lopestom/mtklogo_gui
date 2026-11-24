# mtklogo multi-image: font, GUI, and engine changes

## Table of Contents

- [Package with the complete engine tree already updated](#ill-put-together-a-package-with-the-complete-engine-tree-already-updated)
  - [What is in the package](#what-is-in-the-package)
  - [Building](#building)
  - [Limitation](#limitation)
- [New versions](#new-versions)
- [mtklogo GUI v1.4](#mtklogo-gui-v14)
  - [File structure (8,060,256 B)](#file-structure-8060256-b)
  - [What the images are](#what-the-images-are)
  - [What changed in the project](#what-changed-in-the-project)
- [Why the GUI only shows one image](#why-the-gui-only-shows-one-image)
  - [What the engine does](#what-the-engine-does)
  - [How to get the 59 images in the GUI](#how-to-get-the-59-images-in-the-gui)
  - [Before reflashing a modified logo](#before-reflashing-a-modified-logo)
- [Engine and script patches](#engine-and-script-patches)
  - [New engine options](#new-engine-options)
  - [Integration in mtklogos.sh (v2.2)](#integration-in-mtklogosh-v22)
  - [Another bug I fixed](#another-bug-i-fixed)
  - [What still needs to be done](#what-still-needs-to-be-done)
- [What changed in the commands](#what-changed-in-the-commands)
  - [What each command produces with logo_TANK5_A16.bin](#what-each-command-produces-with-logo_tank5_a16bin)
  - [Repack](#repack)
  - [In mtklogos.sh and the GUI](#in-mtklogosh-and-the-gui)

## I'll put together a package with the complete engine tree already updated

The tree is clean, `Cargo.lock` already existed in the original, and there are 9 changed files in the engine. I'll put the package together.

The only difference is `.gitignore`: my test environment overwrote the original with a single `target/` line. That file is not part of the update, so I'm returning the original to the package.

The `mtklogo_multi_image_font.zip` package contains the complete and updated engine code, plus the script, the languages, the YAML, and the patches. I compiled from the extracted zip, with an empty build directory: all 15 tests pass, and the `unpack --image all → repack → join` cycle reproduces your `logo_TANK5_A16.bin` byte for byte (1 PNG in `logo1`, 59 in `logo2`).

### What is in the package

The paths are the same as in your repository, so you can copy over them:

| Path | Status |
| :---: | --- |
| `mtklogo_v1.0.1/` | complete engine tree, without `target/`, ready for `cargo build` |
| `mtklogos.sh` | v2.2 |
| `mtklogo-gui/sugerido/lang/` | `en.sh` ; `pt.sh` (3 new messages each) |
| `mtklogo.yaml` | `1440x3200` profile with the Android 16 formats, plus the generic profiles |
| `patches/` | the same changes as patches (`git am`) |
| `logo_structure.py` | analysis tool (optional) |
| `README.md` | file table, build, and usage |

Inside `mtklogo_v1.0.1/`, the zip differs from your original branch in exactly 9 files:

- **New**
  - `src/mtk/container.rs`
  - `cli/src/command/split.rs`
- **Modified**
  - `src/mtk/`
    - `logo.rs` (duplicate alignment fix),
    - `mod.rs`
    - `src/lib.rs`
  - `cli/src/command/`
    - `unpack.rs`
    - `mod.rs`
  - `cli/src/main.rs`
  - `README.org`

The zip is identical to a clean clone of your `mtklogo_v1.2` branch and `mtklogo_v1.3` folder with the patches applied.

### Building
Requires Rust 1.85 or newer (edition 2024).

```bash
cd mtklogo_v1.0.1
cargo test --workspace
cargo build --release -p mtklogo-cli      # binary at target/release/mtklogo
```

### Limitation
This code is based on `mtklogo_v1.0.1`, the only source that exists in the repository. The AppImage's "patched" binary has `profiles`, `repack --reference`, and `--force`, but its source is not there. The binary compiled here does not have those three options, and `mtklogos.sh` falls back to a fallback mode for them. If you have the patched source, port the changes from the patches to it.

**Back up the `logo` partition before flashing any generated file.**

**Mtklogo multi image fonte** — ZIP

## New versions

- `mtklogo_v1.1.0` (multi-image)
- `mtklogos.sh` v2.2
- mtklogo GUI v1.4

## mtklogo GUI v1.4

Unihertz Tank 5 · Android 16 · all images in `logo.bin`

All 60 images from `logo_TANK5_A16.bin` were unpacked and the PNG files are at original size 1440×3200.

### File structure (8,060,256 B)

The file is a container with two images, not one:

| Region | Offset | Content |
| --- | --- | --- |
| `logo1` | 0x0 | `logo1` header, 1 slot (the boot screen) |
| `cert1` + `cert2` | 0x26180 | MediaTek certificates |
| `logo2` | 0x27040 | `logo2` header, 59 slots |
| `cert1` + `cert2` | 0x7AEEA0 | certificates again; the last `cert2` has `img_list_end=1` and closes the list |

- The `logo1:0` slot is identical to `logo2:37`.
- All 60 slots are zlib level 9 and reproduce byte for byte.
- The color model is 32 bpp BGRA, the same as in your YAML. The `1440x3200` profile covers all 60 slots after the adjustment below.
- The certificates are the same as in the previous file (RSA 2048, "Mediatek"), but `cert2` now runs from 2026-06-15 to 2035-06-04.

### What the images are

| Slots | Dimension | Content |
| --- | --- | --- |
| `logo1:0`, `logo2:37` | 1440×3200 | boot: "8849 – Rugged by Unihertz" and the new "Powered by Android" |
| `logo2:0–2`, `24–36`, `38–47` | 1440×3200 | 27 charging and battery screens (levels, lightning bolt, plug, "plug in charger" warning) |
| `logo2:3–13` | 45×64 / 57×64 | digits 0–9 and symbol `%` |
| `logo2:14–23` | 363×65 | charging animation (10 frames) |
| `logo2:35` | 363×3 | charging line |
| `logo2:48–58` | 108×192 | large digits 0–9 and symbol `%` |

The last three dimensions were not in the YAML. I found 363×65 and 108×192 through line continuity and confirmed them by looking at the images. Slot 35 was subtler: 33×33 came out as a striped texture, but 4,356 B = 1,089 px = 363×3, the same width as the animation. Its gradient matches the lower blue part of the frames.

### What changed in the project

- `mtklogo.yaml`: the `1440x3200` profile gained the three formats, marked as verified on the Tank 5 A16.
- `logo_structure.py` (v1.1): it now walks containers with multiple images, shows each table, and uses names like `logo2_14_363x65.png` in the export. It also proposes "strip" when a small slot has the same width as another image. This would have found 363×3 on its own, and it now suggests 189×1 in the previous Ulefone `logo.bin`, which in both previous test files still gives the same result (60/60 and 49/60).

One caveat: BGR/RGB order is not automatically detectable. Judging by the gallery colors (orange battery, dark teal, green Android mascot), the YAML order is correct for this file.

**Logo tank5 a16 imagens** — ZIP  
**Mtklogo** — YAML  
**Logo structure** — PY

---

Here is the exact cause, in the code your GUI uses. I'll prove it with numbers and, while at it, teach the tool to warn about this and to split the container into files that `mtklogo` can read.

Your GUI has no defect: this file has two images (`logo1` and `logo2`) and `mtklogo` only reads the first. My tool walks all MTK headers in the file, and the GUI's engine does not.

### What the engine does

The code the GUI embeds (`mtklogo_v1.0.1/src/mtk/logo.rs`, in branch `mtklogo_v1.2`) reads a single table and the blobs up to `block_size`. Then it reads everything left in the file into a `cert` field, which it only preserves on repack.

Applied to `logo_TANK5_A16.bin`:

| Item | Value |
| --- | --- |
| `logo_count` of `logo1` | 1 |
| `blob_end` | 512 + 155,514 = 156,026 |
| file size | 8,060,256 |
| `"cert"` read | 7,904,230 B |

Those 7.9 MB include the whole `logo2` (59 slots, header at 0x27040) plus the 4 certificates. That is why only `logo_000_bgrabe.png` appears, which should be the boot screen "8849 – Rugged by Unihertz" (`logo1:0`, identical to `logo2:37`).

I did not run the AppImage or the binary. The conclusion comes from reading the source and from an emulation of `LogoImage::read` over your file. The emulation gives 1 slot, which matches what you described.

### How to get the 59 images in the GUI

I updated `logo_structure.py` (v1.2). It now warns when the engine would leave images out. It also gained `--split` and `--join`:

```bash
python3 logo_structure.py logo_TANK5_A16.bin --split parts/
# partes/logo1.bin -> mtklogo reads 1 slot
# partes/logo2.bin -> mtklogo reads 59 slots (+ 3,787 B of cert)
```

Open `logo2.bin` in the GUI. To reassemble, use:

```bash
python3 logo_structure.py --join logo_novo.bin logo1.bin logo2.bin
```

Split/join test: concatenating the parts reproduces the original byte for byte. `--join` re-aligns each image to 16 B when an edited part changes size, and I tested this with a `logo1` enlarged by 5 bytes.

YAML: the GUI only generates PNGs for the slots the profile knows. Use the `mtklogo.yaml` I updated, with 363×65, 363×3, and 108×192 in the `1440x3200` profile. Without that, 22 of the 59 slots come out as `.z` instead of as an image. I do not know which folder the GUI stores the YAML in, so copy those three formats into whatever it uses.

### Before reflashing a modified logo

- I do not know which image the device uses at each boot stage. The boot screen exists in both (`logo1:0` and `logo2:37`), so editing only one may have no effect.
- The certificates come with each image. I have not proven what `cert2` signs, and an edited logo may be rejected.
- **Back up the `logo` partition first**, as the project's own README asks.

**Logo structure** — PY

---

I'll read the engine code (Rust) and the GUI code (Python) you use carefully, to propose the change at the exact point and, if possible, compile and test the patch.

I'm root and `apt` is enabled. The code is edition 2024 (Rust ≥ 1.85); I'll see if I can get a recent toolchain to actually compile and test the patch.

Reproduced with the real engine: `logo image has 1 slots` and only `logo_000_bgrabe.png`, exactly your case. Now I'll read the code I need to change (`logo.rs`, `unpack.rs`, `repack.rs`).

Continuing: I'll test the fixed `mtklogos.sh` end to end, driving the menus through stdin, with the new binary, your `logo_TANK5_A16.bin`, and the updated YAML.

Everything formatted and tested. Now I'll generate the patches and validate that they apply to a clean clone of your repository (branch `mtklogo_v1.2`) and that the result compiles and passes the tests.

The patches apply cleanly to your branch, compile, and all 15 tests pass. One last proof with the binary built from that clone: the full cycle must reproduce your file.

I implemented it as new options in `mtklogo` (Rust) and in `mtklogos.sh`. The Python GUI does not need to change, because it only relays the script menus. The patches apply cleanly to a fresh clone of your `mtklogo_v1.2` branch, compile, and pass the 15 tests.

## Engine and script patches

### New engine options

```bash
mtklogo unpack --image all -o out logo.bin    # logo1/ and logo2/, one .mtklogo-meta each
mtklogo unpack --image 2   -o out logo.bin    # only logo2 (accepts 1, 2... or the label logo2)
mtklogo split  -o partes logo.bin             # logo1.bin, logo2.bin
mtklogo join   -o novo.bin logo1.bin logo2.bin
```

- Default behavior: without `--image`, nothing changes; a warning only appears when there are other images that were not read.
- Where the change is: the new `container.rs` module walks the header chain (`size + align_size`), skipping `cert1`/`cert2`. A dedicated reader is necessary because `MtkHeader::read` rejects those labels.
- Full cycle: `unpack --image all` → repack each folder → `join` reproduced your `logo_TANK5_A16.bin` byte for byte. With one edited slot (I painted `logo2:24`), only it changed, and the 2 images and certificates stayed aligned.

### Integration in mtklogos.sh (v2.2)

- Binary detection: the script uses the same method it already uses for `--reference`: it checks whether the binary has `--image`. With an old binary, it follows the previous flow without error.
- Menus: "Unpack" and "Detect profile" now handle all images. On your file the detector gives `1440x3200` 60/60.
- Repack: it redoes each subfolder, uses the original part as `--reference`, and joins in the container order.
- Messages: I added them in `en.sh` and `es.sh`. The other languages fall back to English.
- Menu test: I ran the script in Spanish with your file (unpack and repack): the result is identical to the original.

### Another bug I fixed

The current repack duplicates the alignment padding before `cert1`. My regression test fails without the fix and passes with it. In the files I tested, the effect is:

| File | Repack result |
| --- | --- |
| Ulefone `logo.bin` (single image) | before: +2 B and misaligned certificates. Now: identical to the original |
| `logo_TANK5_A16.bin` with old binary | +6 B, and `cert1`, `cert2`, `logo2`, and the `logo2` certificates fall outside the 16 B alignment |
| `logo_TANK5_A16.bin` with new binary | identical to the original |

If you have already flashed any repacked Tank 5 file with the old binary, I do not know whether the device accepts that alignment. Check the structure before flashing again.

### What still needs to be done

- **Port to the patched binary:** the source of the binary the AppImage uses (profiles, `repack --reference`, `--force`) is not in the repository, only the base `mtklogo_v1.0.1`. The patch was written against that source, and you need to port it to your patched tree. The binary I attached is only for testing: it has no profiles or `--reference`.
- **Apply the patches:** `git am --directory=mtklogo_v1.0.1 mtklogo-engine-multi-image.patch` applies the engine one, and the script one applies at the repository root with `git am`.
- **Packaging:** in the AppImage, replace the `mtklogo` binary and `mtklogos.sh`. The YAML I updated already has the Tank 5 formats.
- **Limit:** `explore` and `guess` still read only the first image. I only handled `unpack`, `repack`, `split`, and `join`.

**Mtklogo engine multi image** — PATCH  
**Mtklogo gui script multi image** — PATCH  
**mtklogo-multi-image-linux-x86_64**

## What changed in the commands

A "little" changed compared to the commands used previously in upstream v1.0.1. Currently in upstream v1.1.0 there are two stages with different commands:

1. The `split` command is what unpacks the `logo1.bin` and `logo2.bin` files;
2. The `unpack` command generates the PNG images.

### What each command produces with logo_TANK5_A16.bin

| Command | Result |
| --- | --- |
| `unpack --image all -o out` | `out/logo1/` with 1 PNG and `out/logo2/` with 59 PNGs, each folder with its own `.mtklogo-meta` |
| `unpack --image 2 -o out` | only the 59 PNGs of `logo2`, directly in `out/` |
| `split -o parts` | `parts/logo1.bin` and `parts/logo2.bin`, which are still packed images, not PNGs |

Each part from `split` is a valid `logoN.bin` on its own. That is why the common `unpack` reads `logo2.bin` alone and extracts all the PNG images. For anyone who has the `logo1.bin` and/or `logo2.bin` files, they can unpack each `.bin` file with the old binary without problems.

### Repack

`repack` does not receive `logo1.bin` and `logo2.bin` as input. It receives PNGs and returns a `.bin`. Each part is rebuilt separately and then joined:

```bash
mtklogo repack -o logo1.bin out/logo1/*.png     # 1 PNG  -> logo1.bin
mtklogo repack -o logo2.bin out/logo2/*.png     # 59 PNG -> logo2.bin
mtklogo join   -o logo_novo.bin logo1.bin logo2.bin
```

If you already have `logo1.bin` and `logo2.bin` ready (for example from `split`, without editing anything), just `join`. `repack` only comes in for the PNG folders you edited.

### In mtklogos.sh and the GUI

You do not type any of this. The "Unpack" option creates `logo/logo1/` and `logo/logo2/`, and "Repack" does both repacks and the join on its own. At the end a single file comes out in `out/`, with the complete container. The intermediate `logo1.bin` and `logo2.bin` stay in a temporary folder that the script deletes.

`unpack` and `repack` analyze and process the `.bin`/`.png` files, but `repack` does not produce two `.bin` files as the final result.
