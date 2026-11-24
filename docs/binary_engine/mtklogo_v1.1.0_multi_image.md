# mtklogo – support for logo.bin with multiple images (logo1 + logo2 + ...)

repo: lopestom/mtklogo
branch: `mtklogo_v1.1.0`

## Table of Contents
- [Contents (same paths as the repository)](#contents-same-paths-as-the-repository)
- [Important](#important)
  - [Integrating into the repository](#integrating-into-the-repository)
- [Building the mtklogo engine binary](#building-the-mtklogo-engine-binary)
- [Usage](#usage)
- [What was tested](#what-was-tested)

## Contents (same paths as the repository)
| Path | Status |
|---|---|
| `mtklogo_v1.1.0/src/mtk/container.rs` | **new**: walks the header chain (`logo_images`, `join_parts`) + 5 tests |
| `mtklogo_v1.1.0/src/mtk/logo.rs` | changed: fix for duplicate alignment before `cert` + test |
| `mtklogo_v1.1.0/src/mtk/mod.rs`, `src/lib.rs` | changed: export the new functions |
| `mtklogo_v1.1.0/cli/src/command/split.rs` | **new**: `split` and `join` commands |
| `mtklogo_v1.1.0/cli/src/command/unpack.rs` | changed: `--image` option and warning |
| `mtklogo_v1.1.0/cli/src/command/mod.rs`, `cli/src/main.rs` | changed: register `--image`, `split`, `join` |
| `mtklogo_v1.1.0/README.org` | changed: "Multi-image containers" section |
| `mtklogo.yaml` | `1440x3200` profile with 363x65, 363x3, 108x192 + generic profiles |
| `logo_structure.py` | analysis tool (optional) |

## Important
The mtklogo engine binary is based on upstream `mtklogo_v1.1.0` with (`profiles`, `repack --reference/--force`).
If you implement improvements that are not in the repository, put the appropriate changes in `patches/` (`mtklogos.sh` detects `--image` on its own).

### Integrating into the repository
By copying the files (keeping the paths) or by applying the patches to a clean clone:

```bash
    git am --directory=mtklogo_v1.1.0 patches/mtklogo-engine-new.patch
    git am patches/mtklogo_gui-script-new.patch
```

## Building the mtklogo engine binary
Requires Rust >= 1.85 (edition 2024).

```bash
    cd mtklogo_v1.1.0
    cargo test --workspace
    cargo build --release -p mtklogo-cli      # binary: target/release/mtklogo
```

## Usage
```bash
    mtklogo unpack -p 1440x3200 --image all -o out logo.bin   # out/logo1/ and out/logo2/
    mtklogo repack -o logo1.bin out/logo1/*.png
    mtklogo repack -o logo2.bin out/logo2/*.png
    mtklogo join   -o logo_new.bin logo1.bin logo2.bin
    mtklogo split  -o parts logo.bin                         # logo1.bin, logo2.bin
```

Without `--image`, `unpack` behaves as before (first image only) and warns that there are more images.

## What was tested
- **Engine:** 17 unit tests; `unpack --image all` → `repack` → `join` reproduces `logo_TANK5_A16.bin` byte for byte.
- **Script:** full flow (detect profile, unpack, repack with `--reference` per image) using the files seeded from the AppImage; a PNG with the wrong dimension is rejected before writing.
- **AppImage:** extracts, opens the GUI (offscreen mode), and seeds `mtklogo-gui/` with version 1.4.
