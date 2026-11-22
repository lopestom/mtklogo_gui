# Analysis and suggestions — mtklogos.sh, mtklogo.yaml and mtklogo

Database analyzed: fork `lopestom/mtklogo` (branch `mtklogo_2025_26`) and `cyberknight777/mtklogo` (HEAD `55deb48`, v1.0.1).
Legend: **[T]** confirmed in real test · **[L]** by reading the code (not reproduced) · ✅ already corrected in the "suggested" files.

---

## 1. Summary

| # | Where | Found | Severity | Status |
|---|---|---|---|---|
| 1 | mtklogo (Rust) | `repack` with PNG without alpha channel (RGB, gray, palette) fails with the misleading message "failed to fill whole buffer" **[T]** | High | ✅ |
| 2 | mtklogo (Rust) | `rgbale`: `explore`/`unpack` fail ("failed to fill whole buffer"): `device_to_rgba` passes number of **bytes** where the name asks for number of **pixels** **[T]** | High | ✅ |
| 3 | mtklogo (Rust) | `repack` silently accepts PNG with incorrect dimensions **[T]** (generates image that may not boot/logo) | High | ✅ `--reference` |
| 4 | mtklogos.sh | `explore` saves `explore_*.png` to `logo/`; After `Repack logo.bin` (`logo/*`) fails: `cannot parse '_id' token` **[T]** | High | ✅ |
| 5 | mtklogos.sh | "Repack other" copies the `mtklogo` binary to `logo/`; the following `Repack logo.bin` fails: `cannot find '_id_' token` **[T]** | High | ✅ |
| 6 | mtklogo.yaml | Profile `720x1600` left 11 of the 60 slots of the example logo as `.z` **[T]**; corrected and visually verified | Medium | ✅ |
| 7 | mtklogo (Rust) | `~/.config/mtklogo.yaml` silently overrides the local yaml **[L]+[T]** | Medium | ✅ warning |
| 8 | mtklogos.sh | Recursion: each action calls `./mtklogos.sh` from within the `select` **[L]** | Medium | ✅ |
| 9 | mtklogos.sh | Repack output: saves `logo_$resolution.bin` but informs `logo_repacked.bin`; `$resolution` is not exported to the recursive process (remains empty → `logo_.bin`) **[L]** | Medium | ✅ |
| 10 | mtklogos.sh | Fixed resolution list in the script; new profile in yaml does not appear in the menu **[L]** | Medium | ✅ |
| 11 | mtklogos.sh | No backup; unpack overwrites `logo/` mixing files from previous executions **[L]** | Medium | ✅ |
| 12 | mtklogo (Rust) | `println!` in closed pipe → `panic`/`Aborted` (ex.: `mtklogo ... \| head`) **[T]** | Download | suggestion |
| 13 | mtklogo (Rust) | Repack does not reuse the original blob when the slot has not changed (+13 bytes vs original in the example) **[T]** | Download | suggestion |

---

## 2. `mtklogos.sh`

### Problems with the original
* **Recursion (8):** in `select`, each action ends with `./mtklogos.sh`. The menu "returns", but the parent process remains alive within its `select`; when exiting the child, the parent reopens the previous menu prompt. In tests with the GUI we saw exactly this (after `Exit` in the child, the parent asks for resolution again).
* **Mixed folders (4, 5, 11):** everything goes to `logo/`. The `repack` requires that the files form a sequence `0..n` **without gaps or duplicates** and that **every** file has the format `logo_NNN_<mode>.png|raw.z`. Any intruder (PNG from `explore`, the copied binary, PNGs from two different profiles) crashes the repack.
* **`$resolution` (9):** variable not exported → empty in the recursive process. The final message mentions another filename.
* **Robustness details [L]:** duplicate `chmod` (lines 11–14), variables without quotes (`$PWD/logo` breaks with spaces in the path), `read -r width` without validation, `find "$PWD" -name mtklogo | `head -1` is recursive (with the binary copied to `logo/` you can choose the wrong copy).

### What v2 does (`suggested/mtklogos.sh`, tested via GUI with the example `logo.bin`)
* `while/select` loop without recursion; folders `logo/`, `explore/`, `out/`, `backup/`.
* Profiles read from `mtklogo profiles` (with fallback to read the yaml if the binary is the old one).
* **Detect profile:** runs `unpack -n` on all profiles (in a temporary folder) and ranks them. In the example: `720x1600` 60/60, `1440x3200` 49/60, `1218x2160` 33/60.
* Confirmations `[y/N]` before deleting folder or applying `--force`; validated width; single backup of the original (`backup/logo.bin.orig`, never overwritten); output with timestamp and sha256.
* Uses `--reference` when the patched binary is present.
* `shellcheck -S warning` clean; GUI compatible (prompts via `echo`/`printf`, not `read -p`).

### Ideas I haven't implemented
* Option to choose the `color_model` (`-m`) on unpack — currently only via profile.
* Guided flow "new profile": `explore` → choose the correct PNG → generate the yaml snippet.
* Saving via `fastboot`/`dd` is intentionally left out: it's the step that causes bootloop and deserves conscious user decision.

---

## 3. `mtklogo.yaml`

### How the binary uses the [L] file
1. Search `~/.config/mtklogo.yaml` → `/etc/mtklogo.yaml` → executable folder. **The first one found wins, without warning.** If you edit the yaml in the folder and nothing changes, look at the one in `~/.config`.
2. For each slot: uncompressed bytes ÷ bytes/pixel = pixels; uses the **first** format in the list with `w*h` equal. An unmatched slot becomes `.z` (lossless; returns intact in the repack).
3. Integer division: a size that is not a multiple of bytes/pixel may match incorrectly (suggestion: reject `size % bpp != 0`).

### Collisions of `w*h` found [T] (analysis script on yaml)
| Profile | pixels | dimensions | effect |
|---|---|---|---|
| `default` | 4,608,000 | 1440x3200 and 1600x2880 | the first in the list is valid |
| `1218x2160` | 2,880 | 40x72 and 45x64 | 45x64 (default symbols) comes first — ok |
| `1200x1920` | 2,304,000 | 1200x1920 and 1920x1200 | the first one prevails |
| `1440x3200` | 304 | 1x304 and 304x1 | the first one prevails |
These are not errors, but they explain "strange" PNGs. I documented them in the yaml header.

### Corrections made (`suggested/mtklogo.yaml`)
* **`720x1600`:** added `180x32` (10 frames of the loading animation) and `360x1` (loading line). I visually confirmed: 180x32 shows the entire continuous blue wave, while the tested alternatives (45x128, 90x64, 120x48, 160x36…) come out striped. Result: **0 `.z` slots** in the example logo (previously 11).
* Typo `progile`, header explaining file priority and collisions.

### More resolutions — what can be done honestly
Only the **full-screen image** has a guaranteed size (`w×h` of the screen). The battery/animation icons vary by device and I **have no way to verify them without the actual `logo.bin`**; inventing lists would be fabricating data. Therefore, I added **14 `exp_*` profiles (EXPERIMENTAL, unverified)**:

`720x1440 · 720x1520 · 720x1560 · 1080x2280 · 1080x2408 · 1080x2412 · 1080x2640 · 1200x2000 · 1200x2400 · 1600x2560 · 1440x2560 · 540x960 · 480x854 · 600x1024`

Each one has full screen + the 5 sizes that are repeated in several `bgrabe` profiles (45x64, 57x64, 72x128, 180x32, 360x1). Anything that doesn't match remains as `.z`, without loss. The assumed `color_model` is `bgrabe` (most modern profiles); if the fullscreen output has swapped colors, use another mode (`-m rgbabe|rgbale|bgrabe|bgrale|rgb565be|rgb565le`).

**How ​​to validate a real profile (and contribute to the upstream):**
1. Menu **Detect profile** (or `mtklogo unpack -n -p <profile> logo.bin`): how many slots match?
2. For remaining slots: `mtklogo unpack -z` extracts the `.z` files; `mtklogo guess -s <bytes>` lists the possible dimensions; `mtklogo explore -w <width>` generates PNGs in all color modes for you to choose what looks right.
3. Add `{ w, h }` to the profile, run the unpack, and check visually.

Idea for format evolution (not implemented): allow mapping **by slot index** (`slot: 15-24 → 180x32`) in addition to size, eliminating collisions.

---

## 4. `mtklogo` (source code)

I compiled the upstream with `rustc 1.91` (needs ≥ 1.88: *let chains* + edit 2024). The compiled binary from the upstream and the one from your fork have the same SHA-256; both require **glibc ≥ 2.34** and `libz.so.1`.

### Fixed in patch (`mtklogo-improvements.patch`, 4 files, +227/−11)
1. **Non-RGBA PNG (1) — `src/utils/image.rs`:** `png_to_rgba` used the decoder's raw buffer; a 3-byte/pixel RGB PNG was read as if it were RGBA and failed. Now applies `EXPAND | STRIP_16` and converts RGB, grayscale, grayscale+alphabet, and palette to 8-bit RGBA. Unit test included.
2. **`rgbale` (2):** `u32be_to_u32le(device, device.len())` → `device.len() / 4`. Round-trip test included. Before, `explore` showed "Could not extract slot 0 as 720x1600 rgbale: failed to fill whole buffer"; now it generates the PNG.
3. **`repack --reference <logo.bin original> [--force]` (3):** compares the number of slots and the unpacked size of each slot with the original. Test: PNG 700x1600 instead of 720x1600 → `mismatch: slot 0 ... (wrong image dimensions?)` and the repack is refused; `--force` only warns. Shows the final size and warns if it grows more than 5%.
4. **Config (7):** `unpack` prints `configuration: <path>` and warns when another `mtklogo.yaml` exists and is being ignored.
5. **`mtklogo profiles`:** lists `name⇥model⇥number of formats⇥aliases` (without banner), used by v2 of the script.

Tests: the 9 from the upstream + 2 new ones pass (the upstream doctest doesn't run here only because `rustdoc` isn't installed).

### Suggestions not applied
* **Idempotent repack (13):** store the PNG hash and the original blob of each slot in `.mtklogo-meta`; if the PNG hasn't changed, reuse the blob. Repacking without edits would give a file **identical** to the original (today: +13 bytes, only due to compression differences) and edits would only change what's necessary. It also avoids overflowing a tight partition.
* **Closed pipe (12):** use `writeln!` handling `BrokenPipe` (or restore SIGPIPE) instead of `println!`.
* **`guess_format`:** reject `size % bpp != 0`; use `checked_mul` in `w*h`.
* **Automatic `--profile`:** The equivalent of the script's "Detect profile" could be `unpack --auto` within the binary.
* **Portability:** Compiling with `x86_64-unknown-linux-musl` and the flate2 Rust backend (`miniz_oxide`) would generate a static binary without glibc/libz dependency (the compression would differ slightly from zlib; functional, but worth testing on the device).
* **Output:** The ASCII (`░`) art column is printed on each run; a `--quiet` flag would help scripts/GUIs.

> ⚠ The suggested binary `/mtklogo` is a **my own, unofficial** compilation - claude-.ai, tested only on PC (unpack/repack/explore/validation). **No generated logo has been saved to the device.** Changing the logo may cause a bootloop: back up the `logo` partition and use at your own risk.
