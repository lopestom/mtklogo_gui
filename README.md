<div align="center" >
  
# **mtklogo GUI v1.5 – Windows 10/11**

<img width="194" height="318" alt="mtklogo_dark1" src="https://github.com/user-attachments/assets/b748e502-0543-4cd2-ac65-749674dfb104" />
</div>

# Changelog
General changes were implemented using AI, while other modifications were made—altered, adjusted, or refined—by a human user to align the outcome with the desired result, rather than just what was initially expected, throughout the code and the GUI.

This document compiles the key changes that have taken place since v1.2, consolidating them into a single changelog to summarize the updates made up to version 1.5.

# mtklogo_vn.n.exe single-file build
mtklogo_gui is a application to extract the pictures of the logo.bin_img file from `/logo` partition of a MediaTek device.

Needs Windows 10 1703+ / 11 (Qt6 uses the system `icuuc.dll`). Work folder: `%USERPROFILE%\mtklogo-gui\`.
The language follows the Windows settings. If you would like a different language, open the command prompt - cmd - in the exe file folder, choose language Tag (pt, en, de, es, fr, ru) and run: `set MTKLOGO_GUI_LANG=fr && mtklogo_v1.5.exe`

Produces **one self-contained `mtklogo_v1.5.exe`** (nothing else to install to *run* it): GUI (PySide6) - a minimal Git-for-Windows bash runtime, binary engine `mtklogo.exe` 1.1.0, script `mtklogos.sh` 2.2, `logo.bin`, translations and icon/splash.

## **New in 1.5**:
- `mtklogo.yaml`: Unihertz Tank 5 A16 sizes (363x65, 363x3, 108x192), generic phone/tablet full-screen profiles and `720x1612` charge animation (189x34, 189x1).
- `mtklogos.sh` is now v2.2.
- **Multi-image `logo.bin`** (e.g. Android 16 on the Unihertz Tank 5: `logo1` + `logo2` in one file). The suggested set now unpacks **every** image into its own sub-folder (`logo/logo1`, `logo/logo2`), repacks each one (checked against its original with `--reference`) and joins them back in container order. New `mtklogo` options: `unpack --image <n|label|all>`, `split` and `join` (engine 1.1.0). Older binaries keep the previous behaviour.
- **Fixed** `repack` inserting the alignment padding twice before `cert1`/`cert2` (the file grew and the certificates left their 16-byte alignment).
- **New window layout.** The console is gone. The script's menus, and its sub-menus such as the profile list, appear in a panel on the left (`OK` / `Cancel`; `Cancel` does what the old "Exit" option did, and that option is no longer listed). The PNG images unpacked from `logo.bin` appear on the right, with three boxes (`logo`, `logo1`, `logo2`) to choose which set is shown. Yes/No questions, alerts and result boxes still pop up as before.
- Right panel: Large preview that rescales when the window is resized + a grid of thumbnails, each showing its corresponding number and resolution for every PNG + file path.
- **Single working folder: `~/mtklogo-gui/`** The `original/` and `suggested/` sets and the set selector were removed; the app always always use merged files from two projects/ideas for the benefit of users. (script v2.2, `mtklogo` 1.1.0, new yaml). The packaged files are in `Drive:/Users/<username>/mtklogo-gui/`.
- **New buttons:** `Authors` (credits of arlept, cyberknight777 and lopestom), `Save log` (saves everything the script printed to `~/mtklogo-gui/mtklogo-gui_<date>.log`) and `Quit`. **Removed:** `Set:`, `Clear`, the manual input box and `Send`.
- **New icon and splash.** `iconmtklogo.svg` and the animated `splash_mtklogo.svg` are pre-rendered to PNG in `assets/` (the bundled Qt has no SVG module).
- **Languages:** every new text is translated into `pt`, `de`, `es`, `fr` and `ru` (52 GUI texts); the script now has a complete Russian file (`lang/ru.sh`) and the multi-image messages exist in all six languages. Russian `[д/Н]` questions are now detected.

## Languages
- Languages ​​included: `Brazilian Portuguese`, `English`, `German`, `Spanish`, `French`, and `Russian`.

- All 52 GUI texts are translated in windows and dialogs.

If you use another language, everything will be in English.

### Another language
- If you want use or add another language (without recompiling) follow languague.md.
> [!NOTE]  
> Actually all multilingual users can add more languages ​​if they wish.
>
> Read the instructions in [languages.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/languages.md)

# Build (Windows, Python 3.9+)

1. Engine: `cd mtklogo_v1.1.0 && cargo build --release --locked -p mtklogo-cli` (use `-p mtklogo-cli`: without it Cargo builds only the library) and copy `target\release\mtklogo.exe` to `windows\bin\mtklogo.exe`.
2. From the repository root: `windows\build_windows.bat` → `dist\mtklogo_v1.5.exe` (`assemble_bundle.py` → `mtklogo-gui\bundle`, `windows\prep_git.py` → `mtklogo-gui\git` with a bash self-test, then PyInstaller).

## Details
Windows 10/11 single-file build, language Tag (Locale Code) UI, GUI fixes:
* i18n: fix syntax error in the ru catalog, remove Portuguese leftovers, consistent terminology (45/45 keys).
* GUI: fix IndentationError in seed_workspace(); fix untranslated strings whose source text did not match the catalog key ("stop the execution?", "Manual input for the script (Enter sends)"); recognise [Д/н] / "нажмите" prompts; set minimum width of the path field and show full set names (tooltips / wider dropdown).
* GUI: Windows port (bundled Git-for-Windows bash, taskkill for process trees, PyInstaller bundle path, hidden console window, keep MSYS POSIX->Windows path conversion enabled).
* script v2.2: accept Russian yes answers (д / да) in confirm().
* windows/: build recipe (assemble_bundle.py, prep_git.py, PyInstaller spec, build_windows.bat, README.md).

# Differences from the Linux AppImage
* Bundled `bash.exe`; `taskkill /T /F` instead of `killpg`/`SIGKILL`; hidden console; PyInstaller bundle path.
* **MSYS path conversion must stay ON** (scripts pass absolute POSIX paths to the native `mtklogo.exe`). Never set `MSYS2_ARG_CONV_EXCL=*`.
* No `/proc` → prompts are detected by the time heuristic (a step silent for >1 s can show an input early).

> [!IMPORTANT]
> Unsigned exe (SmartScreen or antivirus may warn); first start is 1–3 s slower (one-file extraction).

## Attachments - GUI Win usage 
<details><summary> v1.5 Win English- Click to open</summary>
<p>
</p> <img width="812" height="587" alt="1_resized" src="https://github.com/user-attachments/assets/b2efad4c-4ad2-4c79-af13-9035b27409e3" />
</p> <img width="812" height="587" alt="2_resized" src="https://github.com/user-attachments/assets/a8f484fd-3b26-4d70-9c8c-7318aa31d186" />
</p> <img width="812" height="587" alt="3_resized" src="https://github.com/user-attachments/assets/aa329e9d-d247-4bf5-96a8-9823d730b9d9" />
</p> <img width="812" height="587" alt="4_resized" src="https://github.com/user-attachments/assets/955b798f-3ccf-4cc8-8115-6d772c8eac26" />
</p> <img width="811" height="524" alt="5_resized" src="https://github.com/user-attachments/assets/bffd4e34-8b84-4f10-8d73-1e06574e0bb4" />
</p> <img width="811" height="524" alt="6_resized" src="https://github.com/user-attachments/assets/bdfcac14-1129-4251-a00d-e88c44cc9186" />
</p> <img width="812" height="587" alt="7_resized" src="https://github.com/user-attachments/assets/c3b0361e-b94c-49c4-b0da-310ac7873595" />
</p> <img width="810" height="456" alt="8_resized" src="https://github.com/user-attachments/assets/f0671299-5edc-463d-aa96-74aa1c736f24" />
</p> <img width="812" height="587" alt="9_resized" src="https://github.com/user-attachments/assets/aa7ceef7-fd26-46b9-8108-0f7463ee26b8" />
</p> 
</details>

# Additional documents
To avoid cluttering the README file with too much information, any details missing from this document can be found in the [README file](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/README.md) for the Linux branch.

# To do
If you wish to submit a patch/fix from elsewhere (another project, idea, etc.), it is imperative that you retain ownership of the work of the person you wish to include. This will ensure that credit is given where it is deserved and that [open source principles](http://opensource.org/docs/osd) are respected. Your contribution to the project will still be acknowledged, as you will be permanently listed as a committer.

# Contributing
The real objective of contributing will be improvements in making the mtklogo binary file simpler, better, smaller and adding more resolutions or new resolutions/sizes/dimensions/colors to correctly decompress the `logo.bin` file.

For more details read first the [CONTRIBUTING.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/CONTRIBUTING.md) file before send a PR or any modifications.

# Authors
This project would not have been possible without the [mtklogo binary](https://github.com/lopestom/mtklogo_gui/tree/mtklogo_sc_v0.1.2) file created by @arlept and the modifications/improvements ([upstream v1.0.1](https://github.com/lopestom/mtklogo/tree/mtklogo_v1.0.1)) made by @cyberknight777.

## Collaborators
- @Rusikxxx for translation into the Russian language.
- @TheoLuc added more profiles through candidate resolutions.
