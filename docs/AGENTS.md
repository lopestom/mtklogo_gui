# AGENTS.md — mtklogo GUI

Guide for AI coding agents (and humans) working in this repository. Read it before changing anything.

## 1. What this project is

**mtklogo GUI** is a Qt (PySide6) front-end for `mtklogos.sh`, a bash script that wraps the **`mtklogo`** command-line
tool (Rust) to *unpack* and *repack* the boot/charging images stored in MediaTek `logo.bin` partitions.

```
mtklogo_gui.py (Qt)  ──spawns──▶  bash ./mtklogos.sh  ──calls──▶  mtklogo (Rust CLI)  ──reads/writes──▶  logo.bin
        ▲                                   │
        └──── detects prompts on stdin, ────┘          mtklogo.yaml (profiles) · lang/*.sh (script messages)
              answers through the UI
```

The GUI never reimplements the script's logic: it runs `bash ./mtklogos.sh` unchanged, watches its output, detects when it
waits for input and answers through the interface.

| Component | Where | Version |
|---|---|---|
| GUI + AppImage | `mtklogo-gui/mtklogo_gui.py` | **1.5** (`APP_VERSION`) |
| `mtklogo` binary engine (Rust) | `mtklogo_v1.1.0/` (Cargo workspace from lopestom/mtklogo) | **1.1.0** (`[workspace.package] version`) |
| `mtklogos.sh` | repo root | **2.2** |
| `mtklogo.yaml` format marker | first line of the yaml | `version: "1.6"` (format marker, **not** an app version) |

Naming trap: the branch `mtklogo_v1.1.0/` keeps the **upstream** version it was forked from. Branch/tag names such as
`mtklogo_v1.1`, `mtklogo_v1.2`, `mtklogo-gui-1.2` are **GUI releases**, not binary engine versions. The GUI version is currently identified by only two numbers, such as "v1.1/v1.2/v.n.n,". The binary engine will always have three random numbers like "v1.1.0/v1.1.1/v.n.n.n". 

Credits (also shown in the GUI's *Authors* box — keep them intact): **arlept** (original mtklogo), **cyberknight777**
(upstream v1.0.1), **lopestom** (this GUI, yaml, multi-image support).

## 2. Language policy

* Code, comments, docstrings, commit messages and the **source strings of the UI** are in **English**.
* The maintainer writes in any language: answer him in that language, but keep repository files in English.
* UI languages: `en` (source text), `pt`, `de`, `es`, `fr`, `ru`. Details in §7.

## 3. Repository layout

```
README.md                       user documentation (has a "New in X" section per release)
package/usr/share/
mtklogo_gui.py                  the whole GUI (one file)
mtklogo_i18n.py                 translation catalog (CATALOG) + language detection
assets/                         icon_*.png, icon_top_2x.png, mtklogo-gui.png, splash/frame_NNN.png, *.svg sources
qt-translations/                Qt's own translations (OK/Cancel/Yes/No buttons)

package/usr/share/mtklogo-gui/
mtklogos.sh                     the script (v2.2)
mtklogo.yaml                    device profiles (formats per resolution)
lang/{en,pt,de,es,fr,ru}.sh     the SCRIPT's messages (not the GUI's)

bin/                            Rust workspace: lib `mtklogo` + `cli` (package `mtklogo-cli`, binary `mtklogo`) by sources from lopestom/mtklogo branch mtklogo_v1.1.0
tools/                          build_appimage.sh
```
### 3.1 Repository - analysis

```
docs/
AGENTS.md                                                        this file
mtklogo-meta_vs_Repack.md                                        issues Repacking logo.bin with .mtklogo-meta file
NOTES.md                                                         Observations and a bit of discussion regarding mtklogo
logo_TANK5_A16.bin                                               a logo.bin file to testing containing 2 images
multi-image_report/1-Structural_analysis_MTK_logo_claude.ai.md   Structural analysis of logo.bin file (MTK) By Claude
multi-image_report/logo_structure.py                             Structural MTK `logo.bin` analyzer (optional)
multi-image report/2-Resolution_multi_images_logo_A16.md         resolution when handling multiple images in logo_A16 files
multi-image_report/3-mtklogo_multi_image_font_claude.md          Detailed document of logo.bin file with multi-image files (images) analysis.
binary_engine/mtklogo_v1.1.0_multi_image.md                      Detailed Upstream, update of mtklogo binary engine with support for logo.bin with multiple files (logo1 + logo2 + ...)
test_gui.py                                                      functional test (28 checks) that operates the actual window - AGENTS.md file needs it
ANALYSIS_AND_SUGGESTIONS.md                                      Script, yaml and source code analysis
```

Not in the repo: the **AppImage base** (the 1.4 released AppImage supplies the bundled Python 3.12 + PySide6) and prebuilt binaries.

### Runtime layout inside the AppImage

```
usr/share/
  mtklogo_gui.py mtklogo_i18n.py assets/  qt-translations/
usr/share/mtklogo-gui/            READ-ONLY (squashfs). Flat, no "original/", "suggested/", "sugerido/" or "example/" sets any more.
  lang/  mtklogo  mtklogos.sh  mtklogo.yaml
~/mtklogo-gui/                    WRITABLE workspace, seeded from the folder above on every start:
  mtklogo mtklogos.sh mtklogo.yaml lang/ logo.bin .seed_version
  logo/ (or logo/logo1, logo/logo2)   unpacked PNGs         out/   repacked logo.bin   backup/   original copy
  mtklogo-gui_<date>.log  saved by the "Save log" button   explore/
```

* Attempting to write to `usr/share/mtklogo-gui...` within an AppImage: since this is a read-only mount at a known path.
* Seeding: if `.seed_version != APP_VERSION`, `mtklogo`, `mtklogos.sh`, `mtklogo.yaml` and `lang/` are overwritten
  (a `.bak` is kept for user-edited text files). **Bump `APP_VERSION` for every release that changes bundled files**,
  otherwise users keep stale copies.
* New workspaces to write to `usr/share/...` within an AppImage: Legacy workspaces may be deleted, modified, altered, or superseded—starting from version `APP_VERSION = 1.5`—provided that such changes result in improvements and benefits to the Python (`.py`) and shell (`.sh`) code, or to the GUI itself.

## 4. Build, test and verification commands

### Engine (Rust, edition 2024 → Rust ≥ 1.85)

```bash
cd mtklogo_v1.1.0
cargo fmt --all -- --check          # must be clean
cargo test --workspace              # 17 unit tests today
cargo build --release -p mtklogo-cli   # → target/release/mtklogo
```
On Ubuntu 24.04 try install Rust 1.99 for better results; otherwise, install `rustc-1.89 cargo-1.89 rustfmt-1.89` and put `/usr/lib/rust-1.89/bin` first in `PATH`.
The bundled binaries need glibc ≥ 2.34 and dynamic `libz.so.1`, `libgcc_s.so.1` (same as the 1.2 binaries).

### Script and language files

```bash
bash -n mtklogos.sh
for l in en pt de es fr ru; do bash -n mtklogo-gui/lang/$l.sh; done
```
All six `lang/*.sh` must define the **same 65 keys** as `en.sh`, and every message must contain the **same number of `%s`**
as the English one (the script feeds them to `printf`). Quick check: parse `^[A-Z]_[A-Z0-9_]*=` and compare counts.

### GUI

```bash
python3 -m py_compile mtklogo-gui/mtklogo_gui.py mtklogo-gui/mtklogo_i18n.py
```
Functional test (drives the real window like a user, Qt **offscreen**, 28 checks): uses the Python/PySide6 **bundled in the
AppImage**, so extract it first.

```bash
./mtklogo-gui-1.5-x86_64.AppImage --appimage-extract
export APPDIR=$PWD/squashfs-root SRC_LOGO=/path/to/logo_with_2_images.bin MTKLOGO_GUI_LANG=en
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$APPDIR/opt/python3.12/lib/python3.12/site-packages/PySide6/Qt/lib" PYTHONNOUSERSITE=1
$APPDIR/opt/python3.12/bin/python3.12 tools/test_gui.py      # repeat with pt de es fr ru
```
The bundled Python has **no Pillow and no QtSvg**; do image post-processing with the system Python.

### AppImage

```bash
tools/build_appimage.sh mtklogo-gui-1.2-x86_64.AppImage 1.5     # needs squashfs-tools; base may be 1.2/1.4/1.5
```
It extracts the base, overlays assets, lang, script, binary, yaml and the
`.desktop`, sets `APP_VERSION`, rebuilds a zstd squashfs and prepends the base's runtime. Always extract the result and diff
it against what you expect, then run the functional test on the extracted tree and launch it once
(`APPIMAGE_EXTRACT_AND_RUN=1 QT_QPA_PLATFORM=offscreen timeout 10 ./app.AppImage`).

## 5. GUI architecture (`mtklogo_gui.py`)

Top to bottom: process inspection → `LogBuffer` → helpers → `Reader` + menu/prompt detection → workspace seeding →
widgets → `MainWindow` → `main()`.

* **Process control.** `bash ./mtklogos.sh` with `COLUMNS=1` (so `select` prints one option per line) and `MTKLOGO_GUI_LANG`
  set to the GUI language. A `Reader` thread streams stdout+stderr.
* **Prompt detection.** `stdin_waiters()` inspects `/proc` to see whether any process in the tree is blocked in `read(0,…)`.
  Classification: `#? ` suffix = bash `select` menu; `[y/N]`-like = Yes/No; "press Enter" = Continue; otherwise text input.
  `_YES_NO` / `_ENTER` regexes also match Cyrillic (`[д/Н]`, `нажмите`).
* **Menus are embedded**, not pop-ups: `MenuPanel` (left). It hides the **last** entry when its label is an exit/cancel word
  (`CANCEL_LABELS` plus `M_CANCEL`/`M_MENU_7` read from the script's `lang/<code>.sh`) and the **Cancel** button sends it. If the
  last entry is not a cancel word, Cancel asks to stop the script. The heading is the question the script printed just before
  the menu if it ends with `?` or `:`, else "Select an option:".
* **No console.** Output goes to `LogBuffer` (ANSI stripped, `\r` handled, 50 000 lines max). The status bar shows the last line.
  Errors/warnings (lines starting with `P_ERR`/`P_WARN`) and banner boxes (lines of `*****`) become message boxes, grouped
  within 350 ms. Yes/No, text and Continue prompts stay modal dialogs.
* **Gallery.** `Gallery` (right) shows `logo_*` files of one folder; three exclusive buttons `logo`, `logo1`, `logo2` map to
  `workdir/logo`, `workdir/logo/logo1`, `workdir/logo/logo2`; a button is enabled only if its folder has files.
  Thumbnails load a few per tick via `QImageReader.setScaledSize` (the PNGs can w×h). `.z` files (slots with an
  unrecognised size) get a placeholder tile.
* **Splash.** `Splash` is a frameless translucent widget playing `assets/splash/frame_*.png`; skipped when
  `MTKLOGO_GUI_NOSPLASH` is set (use it in tests).
* **Environment variables:** `MTKLOGO_GUI_LANG` (language override), `MTKLOGO_GUI_HOME` (workspace, default
  `~/mtklogo-gui`), `MTKLOGO_GUI_NOSPLASH`, `APPDIR` (set by AppRun). The script itself honours `LOGO_BIN`.
* **Layout rules.** Do not give buttons fixed pixel widths (German/Russian labels are longer); the divider between the
  left panel and the gallery must stay aligned with the right edge of the *Stop* button (`left_w` is computed from the
  buttons' size hints). Keep the system Qt style; only the gallery has a fixed dark background (`#10141a`).
* Qt: PySide6 preferred, PyQt5 tolerated. Avoid anything that needs `QtSvg`.

## 6. The script (`mtklogos.sh`)

* Works in the current directory: `logo.bin`, `logo/`, `out/`, `backup/`, `.mtklogos_state`, `mtklogo.yaml`, `lang/`.
* Menu: 1 Unpack · 2 Detect profile · 3 Repack · 4 Unpack other (explore) · 5 Repack other · 6 List profiles · **7 Exit**.
  The GUI hides item 7; the script keeps it so the command line still works. Do not remove it from the script.
* **Feature detection** of the `mtklogo` binary: `HAS_PROFILES`, `HAS_REFERENCE`, `HAS_IMAGE`. Older binaries must keep working.
* Multi-image files: `unpack --image all` writes `logo/logo1`, `logo/logo2`, each with its own `.mtklogo-meta`; the original
  parts are kept in `logo/.parts/` (with an `order` file); repack rebuilds each part with `--reference` against its original
  and joins them.
* Messages live in `lang/<code>.sh` (English is loaded first, other languages override), via `say/warn/err/banner/confirm`.
  Never put apostrophes inside single-quoted values; use typographic quotes or «…».

## 7. Translations

**GUI** (`mtklogo_i18n.py`): the **English text is the key**. `_("text", name=value)` looks it up in `CATALOG[lang]` and
falls back to English; `N_("text")` only marks a string for later translation (used by `AUTHORS`).

Rules (checked by the audit below):
1. Every literal passed to `_()`/`N_()` must exist in **all five** catalogs (`pt de es fr ru`) and no unused keys may remain.
2. `{placeholders}` must be identical between key and translation.
3. When you reword an English string in the code, rename the catalog key too — otherwise the UI silently shows English
   (this already happened once in the repo history).
4. Avoid plural logic: use constructions like `изображений: {n}` or separate `"1 image"` / `"{n} images"` keys.
5. Use each language's wording already used by the script for menu names (e.g. the Run button name inside "Press “Run …”").

```python
# audit: all literals used by the GUI must be in every catalog
import ast, importlib.util
src = open("mtklogo_gui.py", encoding="utf-8").read()
used = {n.args[0].value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id in ("_", "N_") and n.args and isinstance(n.args[0], ast.Constant)}
m = importlib.util.module_from_spec(s := importlib.util.spec_from_file_location("i", "mtklogo_i18n.py")); s.loader.exec_module(m)
for lang, cat in m.CATALOG.items(): print(lang, "missing:", sorted(used - set(cat)), "unused:", sorted(set(cat) - used))
```

**Script** (`lang/*.sh`): see §4. `ru.sh` is a complete translation. The yes/no hint for Russian is `[д/Н]`
(the script's `confirm()` already accepts `д`/`да`).

> Honesty note: the pt/de/es/fr/ru strings added in 1.5 (and `lang/ru.sh`) were written by an AI assistant. Treat them as
> good drafts that deserve a native-speaker review before a public release.

*The translations into pt_BR and ru_RU updated reviewed by native-speakers humans.*

## 8. The `logo.bin` format and the engine (read before touching Rust or the yaml)

```
[MTK header 512 B][table: u32 count, u32 block_size, u32 offsets[count]][zlib blobs][cert region…]
```
* Header: magic `88 16 88 58` (big-endian) at 0; `dsize` (LE) at 4; label at 8 (`logo`, `logo1`, `cert1`…); extended header
  magic `89 16 89 58` at 0x30 with `hdr_size`, `img_type`, `img_list_end`, `align_size` (16), …
* Blobs are zlib streams (`78 DA`, level 9 reproduces them byte for byte). Raw size = `width × height × bytes_per_pixel`.
* After the blobs come **cert1/cert2** (X.509, "Mediatek", RSA-2048 signature) each with its own MTK header, aligned to 16 B.
  The cert region must be preserved verbatim by repack. What `cert2` signs is **unverified**: a modified logo may be
  rejected by devices that enforce signatures.
* **Multi-image containers** (e.g. Android 16, Unihertz Tank 5): `[logo1][cert1][cert2][logo2][cert1][cert2]`, the last
  `cert2` has `img_list_end = 1`. `LogoImage::read` (upstream) reads **one** table and keeps the rest as an opaque `cert`,
  which is why only `logo_000` appeared before 1.4. `logo_images()` (src/mtk/container.rs) walks the header chain
  (`header + dsize`, aligned) and returns each `logo*` image; `MtkHeader::read` rejects unknown labels such as `cert1`, so the
  walker uses its own tiny header parser.
* Engine additions in 1.1.0: `unpack --image <n|label|all>`, `split`, `join`, the alignment fix (`LogoImage::read` used to keep
  the alignment padding that `write` re-creates → cert1/cert2 drifted by 2–6 bytes on every repack), plus the improvements patch
  (`profiles`, `repack --reference`, `--force`). Round trip must stay **byte-exact**: `unpack --image all` → `repack` each →
  `join` == original file.
* Pixel formats (`color_model`): `bgrabe` = bytes B,G,R,A in memory (modern files); `rgb565le` for the old `default`
  profile. BGR vs RGB cannot be detected automatically — check colours visually.
* `Profile::guess_format` matches a slot by `size / bytes_per_pixel` (integer division) and returns the **first** format whose
  `w*h` equals it → **two formats with the same pixel count in one profile are a bug** (the second never matches). Ranking
  profiles by "slots matched" can give false positives (e.g. 57×64 = 152×24 = 3648 px).

### Editing `mtklogo.yaml`

* A profile's full-screen size is usually the profile name (`720x1612`). Keep real, verified sizes; mark unverified ones
  (`exp_*`, confidence **B**) as such in comments.
* The `default` profile is RGB565; do **not** add modern (32 bpp) sizes there — create/extend a `bgrabe` profile.
* Keep byte-size comments correct (`w × h × 4` for `bgrabe`).
* Before committing: parse with PyYAML, check no duplicate profile names, no pixel-count collisions inside a profile, and run
  `mtklogo profiles` (it must list every profile).
* Panel resolutions from spec sheets are **not** always the LK logo size (1600/1604/1612, 2400/2408/2412 exist). Confirm with
  a real file: `slot_bytes / (w × h × 4)` must be an integer.

## 9. Conventions for changes

* **Small, separate commits** with Conventional-Commit style prefixes (`feat(gui):`, `fix(lib):`, `docs:`, `style:`, `chore:`).
  A bug fix goes in its own commit with a regression test that fails without the fix.
* Engine patches apply with `git am --directory=mtklogo_v1.1.0 …`; GUI patches with plain `git am`. Create them with
  `git format-patch --binary` (assets are PNGs). **Always fetch the remote tip first** — the branch moves (a merged PR added
  `mtklogo-gui/mtklogo.yaml` while this work was in progress) — and verify the series on a **fresh clone** of the tip:
  apply, compare the tree with what you tested, build, test.
* Never rewrite or silently overwrite the maintainer's text (README prose, comments, screenshots). Change only what became false
  and add a "New in X.Y" section.
* No unrequested features. If the request is ambiguous, state your assumption explicitly and keep it easy to change.
* Don't commit build output (`target/`, AppImages, extracted trees).

## 10. Definition of done (run, do not assume)

Say what you actually ran. For a GUI/script/engine change this means, at minimum:

- [ ] `cargo fmt --check` and `cargo test --workspace` (engine touched)
- [ ] `python3 -m py_compile` on the GUI files; `bash -n` on the script and all `lang/*.sh`
- [ ] i18n audit (§7) shows no missing/unused keys; `lang/*.sh` keys and `%s` counts match `en.sh`
- [ ] `tools/test_gui.py` passes on the **packaged** (extracted) AppImage, in at least `pt` and `ru` (ideally all six)
- [ ] Round trip on a real multi-image `logo.bin` is byte-identical
- [ ] AppImage extracted and diffed against the intended tree; launched once offscreen; `sha256` published
- [ ] Patch series applies to a fresh clone of the current branch tip

## 11. Known limits (do not claim otherwise)

* Automated GUI tests run Qt **offscreen**: real displays are untested (splash transparency without a compositor, dark system
  themes, high DPI, Wayland specifics). The tests drive widgets programmatically, not through a window manager.
* The gallery has exactly three sets (`logo`, `logo1`, `logo2`); containers with more than two logo images are not shown beyond that.
* `explore`/`guess` (menu 4) read only the first image of a container.
* Flashing a regenerated `logo.bin` to a phone has not been verified on hardware; the signature semantics of `cert2` are unknown.
  Always keep a backup of the `logo` partition and say so to users.
* Resolutions in the generic yaml profiles come from public spec listings (confidence A = two or more devices, B = one listing)
  and were not checked against real dumps.

## 12. Pitfalls already hit (save yourself the time)

* The `de739ed` commit translating comments to English left a mis-indented docstring and an unescaped quote in the Russian
  catalog → the GUI did not start. Always `py_compile` and actually launch it.
* `git mv` into a directory that the other side modified conflicts; when a rebase stops, **do not** run `git commit --amend`.
  Abort and rebuild the branch deterministically (cherry-pick, then recreate the last commit).
* In shell snippets: backticks inside unquoted heredocs are executed; `cut -c` can split a UTF-8 character; process
  substitution `<(…)` fails under `/bin/sh`; `set -e` aborts when `timeout` returns 124. Prefer a script file.
* AppImage mounts are read-only and some sandboxes mount the output folder `noexec`: copy the AppImage elsewhere to run it,
  and tell users to `chmod +x` after downloading.
