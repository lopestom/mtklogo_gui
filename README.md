<div align="center" >
  
# **mtklogo-GUI**

<img width="194" height="318" alt="mtklogo_dark1" src="https://github.com/user-attachments/assets/b748e502-0543-4cd2-ac65-749674dfb104" />
</div>

# Changelog
General changes were implemented using AI, while other modifications were made—altered, adjusted, or refined—by a human user to align the outcome with the desired result, rather than just what was initially expected, throughout the code and the GUI.

This document compiles the key changes that have taken place since v1.2, consolidating them into a single changelog to summarize the updates made up to version 1.5.

## **New in 1.5**:
- **New window layout.** The console is gone. The script's menus, and its sub-menus such as the profile list, appear in a panel on the left (`OK` / `Cancel`; `Cancel` does what the old "Exit" option did, and that option is no longer listed). The PNG images unpacked from `logo.bin` appear on the right, with three boxes (`logo`, `logo1`, `logo2`) to choose which set is shown. Yes/No questions, alerts and result boxes still pop up as before.
- Right panel: Large preview that rescales when the window is resized + a grid of thumbnails, each showing its corresponding number and resolution for every PNG + file path.
- **Single working folder: `~/mtklogo-gui/`.** The `original/` and `suggested/` sets and the set selector were removed; the app always always use merged files from two projects/ideas for the benefit of users. (script v2.2, `mtklogo` 1.1.0, new yaml). The packaged files are in `usr/share/mtklogo-gui/`.
- **New buttons:** `Authors` (credits of arlept, cyberknight777 and lopestom), `Save log` (saves everything the script printed to `~/mtklogo-gui/mtklogo-gui_<date>.log`) and `Quit`. **Removed:** `Set:`, `Clear`, the manual input box and `Send`.
- **New icon and splash.** `iconmtklogo.svg` and the animated `splash_mtklogo.svg` are pre-rendered to PNG in `assets/` (the bundled Qt has no SVG module).
- **Languages:** every new text is translated into `pt`, `de`, `es`, `fr` and `ru` (52 GUI texts); the script now has a complete Russian file (`lang/ru.sh`) and the multi-image messages exist in all six languages. Russian `[д/Н]` questions are now detected.
- Fixed the GUI at the commit that translated its comments to English (a mis-indented docstring and an unescaped quote in the Russian text kept it from starting).

## **New in 1.4**:
- **Multi-image `logo.bin`** (e.g. Android 16 on the Unihertz Tank 5: `logo1` + `logo2` in one file). The suggested set now unpacks **every** image into its own sub-folder (`logo/logo1`, `logo/logo2`), repacks each one (checked against its original with `--reference`) and joins them back in container order. New `mtklogo` options: `unpack --image <n|label|all>`, `split` and `join` (engine 1.1.0). Older binaries keep the previous behaviour.
- **Fixed** `repack` inserting the alignment padding twice before `cert1`/`cert2` (the file grew and the certificates left their 16-byte alignment).
- `mtklogo.yaml`: Unihertz Tank 5 A16 sizes (363x65, 363x3, 108x192), generic phone/tablet full-screen profiles and `720x1612` charge animation (189x34, 189x1). `mtklogos.sh` is now v2.2. The new file is `mtklogo-gui-1.4-x86_64.AppImage`.
-  **New window layout.** Right panel: Large preview that rescales when the window is resized + file path

## **New in 1.3**:
- New `mtklogo.yaml` file by @TheoLuc from commit **04ff653** of branch `mtklogo_v1.2`.
- `mtklogos.sh` file update to v2.1 with new options.
- Improvements in russian language `ru.sh` file.

# AppImage (simplest)
* On the first run it creates `~/mtklogo-gui/ `with a `logo.bin` file to test, `mtklogos.sh` script file, `mtklogo` binary file, `mtklogo.yaml` profile and `/lang/` with all `*.sh` languages files.
Run in any Terminal:
```bash
chmod +x mtklogo-gui-1.5-x86_64.AppImage
./mtklogo-gui-1.5-x86_64.AppImage
```
Everything the script generates `logo/`, `out/`, `backup/`, log file is in these folders.
* No FUSE (`libfuse2`)? `./mtklogo-gui-1.5-x86_64.AppImage --appimage-extract-and-run`
* Requires glibc ≥ 2.34 (Ubuntu 22.04+, Debian 12+, Fedora 35+, Arch…) because of the `mtklogo` binary. Qt/xcb are built-in.

## From sources
- Open the GUI with a single set.
- Minimalist graphical interface (Python + Qt) for `mtklogos.sh`.
- The script runs **exactly as is** (`bash ./mtklogos.sh`): the GUI only captures the output in real time and respond to his questions through dialogue.
- Use **Choose logo.bin…** to bring yours own logo.bin file.

## Extract AppImage
All files in this repository and branch can viewed by extracting:
```bash
chmod +x mtklogo-gui-1.5-x86_64.AppImage
./mtklogo-gui-1.5-x86_64.AppImage --appimage-extract >/dev/null 
```

## Build AppImage
It reuses Python 3.12 + PySide6 from the base AppImage, correctly re-seeding the version (`APP_VERSION`) and copying all files located in /bin, /package, /assets, and /qt-translations folders.

Note the version 1.4 used by the base AppImage and the version 1.5 that will be updated in the new AppImage file.
        `tools/build_appimage.sh mtklogo-gui-1.4-x86_64.AppImage 1.5`      # requires squashfs-tools

### Using a Linux PC
1. Place new folders and/or new files in the base folders used for updating;
2. Open the Terminal;
3. Paste into the Terminal;

   `./tools/build_appimage.sh mtklogo-gui-1.5-x86_64.AppImage 1.6`
   
   old version= 1.5 --->> new version= 1.6
   
   You can open build_appimage.sh file to change `OLD="1.4"` to `OLD="1.5"` and `VER="1.5"` to `VER="1.6"` if you want. Two clicks in the build_appimage.sh file to run.
5. Wait for compilation;
6. On the screen, choose the correct option when the message "Run once" appears.

Done, the new AppImage mtklogo-gui-1.6-x86_64.AppImage will be updated with the new folder and new files.

## Language detection
- The GUI reads `MTKLOGO_GUI_LANG`, `LANGUAGE`, `LC_ALL`, `LC_MESSAGES`, and `LANG`, in that order. To test another language without changing the system:
```bash
MTKLOGO_GUI_LANG=de ./mtklogo-gui-1.5-x86_64.AppImage
```
- All 52 GUI texts are translated in windows and dialogs. The standard Qt buttons (`OK`, `Cancel`, `Yes`, `No`, and `file dialogs`) are also included in `German`, `Spanish`, `French`, `Russian` and `Brazilian Portuguese`.

> [!NOTE]  
> Actually all multilingual users can add more languages ​​if they wish.
>
> Read the instructions in [languages.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/languages.md)
 
## Content

| File | Description |
|---|---|
| `lang/*.sh` | script messages of mtklogos.sh (`en` = default, `pt`, `de`, `es`, `fr`, `ru`) |
| `mtklogos.sh` | updated script v2.2 (multi-image aware) |
| `mtklogo` | new upstream released Linux binary x86-64 v1.1.0 (3+ commits: upstream v1.1.0 + improvements + multi-image: `--image`, `split`, `join`) |
| `logo.bin` | example `logo.bin` file from repository (replace with yours) |
| `mtklogo.yaml` | profiles (with `exp_*`, generic phone/tablet and Tank 5 A16 sizes and more fixes/profiles) |
| `assets/` | icons and splash frames, pre-rendered from `iconmtklogo.svg` / `splash_mtklogo.svg` |
| `qt-translations/` | Qt's own translations into the languages ​​of de, es, fr, pt, ru |
| `build_appimage.sh` | rebuild the AppImage from AppImage 1.4 (base) and this branch |
| `mtklogo-gui.desktop` | AppImage shortcut |
| `AppRun` | AppImage Run doc |
| `mtklogo_gui.py`, `mtklogo_i18n.py` | GUI 1.5 (3 commits - includes the HEAD fixes described below) |
| `mtklogo_v1.1.0_multi_image.md` | Upstream and update of mtklogo with support for logo.bin with multiple files (logo1 + logo2 + ...) |
| `build-mtklogo-gui-appimage.yml` | workflow file for using with Actions |
| `languages.md` | Instructions for changing and/or adding languages ​​in the GUI |
| `CONTRIBUTING.md` | read to contribute to the project |
| `README.md` | this file containing general update information |


To avoid cluttering the README with too much information, some files have been placed in the [`docs`](https://github.com/lopestom/mtklogo_gui/tree/mtklogo_v1.5/docs) directory. This means that each document addresses a unique aspect applied to both the [mtklogo 1.1.0](https://github.com/lopestom/mtklogo/tree/mtklogo_v1.1.0) binary engine and the GUI. To understand each phase and the studies applied since version 1.3, each document covers a [topic addressing](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/AGENTS.md#3.1-repository---analysis) the main idea, implementation, application, testing, and/or a detailed analysis.
If you're curious to know how it went, read the documents and enjoy.

### Problems found
Problems found in the HEAD of the mtklogo_v1.2 branch and were fixed in v1.3 onwards.
The commit `de739ed` (English translation) rendered the GUI inoperable. None of these issues stem from the multi-image changes:

1. `mtklogo_gui.py`: the docstring for `seed_workspace()` ended up with 8 spaces in a 4-space body → `IndentationError`,
the app won't open.
2. `mtklogo_i18n.py`: in the `ru` block, the string `{script} не существует…` uses straight quotes `"Папка…"` inside a
quoted string → `SyntaxError`. Replaced with «Папка…».
3. `SET_LABELS` started using `"suggested"` and the code looks for the `"example"` folder, but the package and repository folders remain `sugerido` and `example` → the sugerido set was silently ignored. A `BUNDLE_DIRS` (name map) was created, without renaming folders. Note: user data is now located in `~/mtklogo-gui/suggested/` (previously `.../sugerido/`); the old folder is neither deleted nor migrated.

## Attachments - GUI usage 
<details><summary> v1.5 English- Click to open</summary>
<p>
</p> <img width="833" height="634" alt="PrintScreen_20261123_183206_resized" src="https://github.com/user-attachments/assets/a048baa7-86cc-4219-97df-94c75eec764f" />
</p> <img width="833" height="634" alt="PrintScreen_20261123_183217_resized" src="https://github.com/user-attachments/assets/26180052-9cf8-4551-8e73-732068c608a8" />
</p> <img width="756" height="547" alt="PrintScreen_20261123_183325_resized" src="https://github.com/user-attachments/assets/cf21445a-22ef-43c5-a376-2269b6e4282a" />
</p> <img width="756" height="547" alt="PrintScreen_20261123_183428_resized" src="https://github.com/user-attachments/assets/a0b7830d-14d5-4886-bf64-d13d6fb91c6e" />
</p> 
</details>

<details><summary> other languages - Click to open</summary>
<p>
</p> <img width="833" height="634" alt="PrintScreen_20261123_180128_resized" src="https://github.com/user-attachments/assets/7b2e33d2-d2d3-42c2-aa7f-5676efd1ebca" />
</p> <img width="833" height="634" alt="PrintScreen_20261123_180049_resized" src="https://github.com/user-attachments/assets/1e00a969-e3c6-4fda-bf27-a47d91f1d381" />
</p> <img width="759" height="548" alt="PrintScreen_20261123_180441_resized" src="https://github.com/user-attachments/assets/35afbbf2-d681-4778-96a1-092629464c3d" />
</p> <img width="756" height="545" alt="PrintScreen_20261123_180255_resized" src="https://github.com/user-attachments/assets/030307e4-e38b-4e8d-99d0-bec9a3b06095" />
</p> <img width="755" height="547" alt="PrintScreen_20261123_180227_resized" src="https://github.com/user-attachments/assets/cbdc3118-08e9-49b0-911c-7dfb6b4f43ef" />
</p> 
</p> <img width="833" height="634" alt="PrintScreen_20261123_182913_resized" src="https://github.com/user-attachments/assets/1416651f-094b-40bf-b17f-02318aa5b491" />
</p> <img width="833" height="634" alt="PrintScreen_20261123_182938_resized" src="https://github.com/user-attachments/assets/0b14664c-1a2e-4cad-a346-cbac1aba749c" />
</p> <img width="756" height="547" alt="PrintScreen_20261123_183038_resized" src="https://github.com/user-attachments/assets/c622cc94-e299-4dd1-8b70-b659d8005c9b" />
</p> <img width="756" height="547" alt="PrintScreen_20261123_183101_resized" src="https://github.com/user-attachments/assets/e7a0a3d2-b9c8-4565-835f-c67811afd549" />
</p> 
</p> <img width="833" height="634" alt="PrintScreen_20261123_182059_resized" src="https://github.com/user-attachments/assets/5bf361c2-9f9a-4164-985c-4b995107ddf7" />
</p> <img width="761" height="548" alt="PrintScreen_20261123_182308_resized" src="https://github.com/user-attachments/assets/56f44e35-b9a3-4e25-a5ad-75939251db65" />
</p> <img width="761" height="548" alt="PrintScreen_20261123_182518_resized" src="https://github.com/user-attachments/assets/a75c7bea-bea8-4231-a002-df549a58aeb3" />
</p> <img width="761" height="548" alt="PrintScreen_20261123_182357_resized" src="https://github.com/user-attachments/assets/b04d83fb-16fb-42b2-971d-d5a7500ca3a1" />
</p> 
</p> <img width="833" height="634" alt="PrintScreen_20261123_182626_resized" src="https://github.com/user-attachments/assets/0bfc7106-ed4e-40fe-8c90-63b734d4c794" />
</p> <img width="833" height="634" alt="PrintScreen_20261123_182640_resized" src="https://github.com/user-attachments/assets/5a1dabe3-0525-43f7-b25a-0be13c872b77" />
</p> <img width="758" height="544" alt="PrintScreen_20261123_182726_resized" src="https://github.com/user-attachments/assets/af7ac234-864e-4d7c-b7b7-e8cf281dd8eb" />
</p> <img width="758" height="544" alt="PrintScreen_20261123_182809_resized" src="https://github.com/user-attachments/assets/93ca9cd2-dd83-4dbc-87ac-d867b83f365f" />
</p> 
</p> <img width="833" height="634" alt="PrintScreen_20261123_183558_resized" src="https://github.com/user-attachments/assets/c95e2dbf-0093-4fda-b61a-8fc8cb7e3c20" />
</p> <img width="833" height="634" alt="PrintScreen_20261123_183609_resized" src="https://github.com/user-attachments/assets/c0a9760a-76eb-442b-a0d1-04576a1455dd" />
</p> <img width="758" height="549" alt="PrintScreen_20261123_183655_resized" src="https://github.com/user-attachments/assets/e7e94ecb-8974-44e6-a3a1-cf2457ebe7ae" />
</p> <img width="758" height="549" alt="PrintScreen_20261123_183719_resized" src="https://github.com/user-attachments/assets/eff2c5f5-13e8-406a-b7fa-92e2a0ae76bb" />
</p> 
</details>

> [!NOTE]  
> The folder `~/mtklogo-gui` holds the PNG files of your logo.bin in `~/mtklogo-gui/logo` (single image) or in `~/mtklogo-gui/logo/logo1` and `~/mtklogo-gui/logo/logo2` (multi-image files).
>
> It is in these subfolders that you should paste your modified png images or modify the png images directly in this subfolder.
>
> <details><summary> Example (screenshot of version 1.4 and later) - Click to open</summary>
> <p>
> <img width="1284" height="636" alt="logo1_2_Folders" src="https://github.com/user-attachments/assets/ac8b0c12-f514-418e-a150-6fc619c8fb69" />
> </p>
> </details>

# To do
If you wish to submit a patch/fix from elsewhere (another project, idea, etc.), it is imperative that you retain ownership of the work of the person you wish to include. This will ensure that credit is given where it is deserved and that [open source principles](http://opensource.org/docs/osd) are respected. Your contribution to the project will still be acknowledged, as you will be permanently listed as a committer.

Read [suggestions-not-applied](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/ANALYSIS_AND_SUGGESTIONS.md#suggestions-not-applied) for more ideas and to avoid duplication, or to save time on new ways to contribute.

# Contributing
The real objective of contributing will be improvements in making the mtklogo binary file simpler, better, smaller and adding more resolutions or new resolutions/sizes/dimensions/colors to correctly decompress the `logo.bin` file.

For more details read first the [CONTRIBUTING.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/CONTRIBUTING.md) file before send a PR or any modifications.

## Analysis and suggestions
Created for the first part of the project merger, but it also proves useful for keeping track of suggestions. For anyone or/and A.I. Agents read Script, yaml and source code analysis:
* [ANALYSIS_AND_SUGGESTIONS.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/ANALYSIS_AND_SUGGESTIONS.md) if you want.
* [AGENTS.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/docs/languages.md/AGENTS.md).

# Authors
This project would not have been possible without the [mtklogo binary](https://github.com/lopestom/mtklogo_gui/tree/mtklogo_sc_v0.1.2) file created by @arlept and the modifications/improvements ([upstream v1.0.1](https://github.com/lopestom/mtklogo/tree/mtklogo_v1.0.1)) made by @cyberknight777.

## Collaborators
- @Rusikxxx for translation into the Russian language.
- @TheoLuc added more profiles through candidate resolutions.
