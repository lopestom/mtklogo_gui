# mtklogo GUI (v1.2)

## **New in 1.2**:
- The GUI now follows your computer's system language, with English as the default. The new version is 1.2, in the file mtklogo-gui-1.2-x86_64.AppImage (50 MB).
- Languages ​​included: `Brazilian Portuguese`, `English`, `German`, `Spanish`, `French` and `Russian`. If you use another language, everything will be in English.
- Ready AppImage (`mtklogo-gui-1.2-x86_64.AppImage`), **set selector** &
- Comparring (Original × Suggested), with button **Choose logo.bin…**, folder `suggested/` (script v2 + patched mtklogo + new yaml) and correction in prompt detection (ignores `read` from script internal pipes).
- Details and justifications in `ANALYSIS_AND_SUGGESTIONS.md`.

## AppImage (simplest)

```bash
chmod +x mtklogo-gui-1.2-x86_64.AppImage
./mtklogo-gui-1.2-x86_64.AppImage
```
* On the first run it creates `~home/mtklogo-gui/original/` and `~home/mtklogo-gui/suggested/` (with a `logo.bin` of **example**). Everything the script generates 
(`logo/`, `out/`, `backup/`) is in these folders. Use **Choose logo.bin…** to bring yours.
* No FUSE (`libfuse2`)? `./mtklogo-gui-1.2-x86_64.AppImage --appimage-extract-and-run`
* Requires glibc ≥ 2.34 (Ubuntu 22.04+, Debian 12+, Fedora 35+, Arch…) because of the `mtklogo` binary. Qt/xcb are built-in.

> [!NOTE]  
> A folder named `~home/mtklogo-gui` is created with two other subfolders `~home/mtklogo-gui/sugerido` and `~home/mtklogo-gui/original`.
> Set your selection to `original` or `suggested` so that each subfolder contains the png files from your logo.bin file, located in `~home/mtklogo-gui/sugerido/logo` and `~home/mtklogo-gui/original/logo`.
>
> It is in this `/logo` subfolder that you should place your modified png images or modify the png images directly in this subfolder.
>
> <details><summary> Example - Click to open</summary>
> <p>
> <img width="982" height="375" alt="6" src="https://github.com/user-attachments/assets/98037276-cba4-435f-8a82-17fb62a6a423" />
> </p>
> </details>

## From sources

`./run.sh` opens the original pool; **`./run.sh suggested`** opens the suggested set (`sugerido/` folder).

Minimalist graphical interface (Python + Qt) for `mtklogos.sh`.

The script runs **exactly as is** (`bash ./mtklogos.sh`): the GUI only captures the output in real time and respond to his questions through dialogue.

### Language detection
- The GUI reads `MTKLOGO_GUI_LANG`, `LANGUAGE`, `LC_ALL`, `LC_MESSAGES`, and `LANG`, in that order. To test another language without changing the system:
```bash
MTKLOGO_GUI_LANG=de ./mtklogo-gui-1.2-x86_64.AppImage
```

- All 45 GUI texts are translated in windows and dialogs. The standard Qt buttons (`OK`, `Cancel`, `Yes`, `No`, and `file dialogs`) are also included in `German`, `Spanish`, `French`, `Russian` and `Brazilian Portuguese`.

> [!NOTE]  
> I had chosen only one language for the AppImage v1.1 to reduce its size and facilitate quick testing and now I've decided include only a few (approximately 840 KB) for further improvements and language choices.
>
> So now all multilingual users can add more languages ​​if they wish.

 * You can read [mtklogo_gui_Claude-AI_prompt2](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.2/mtklogo_gui_Claude-AI_prompt2.md) to understand how to add more languages ​​and, if possible, contribute to the project.
 
## Content

| File | Description |
|---|---|
| `eng.sh` | script Messages of mtklogos.sh (`English = default`) |
| `mtklogos.sh` | Original script (**unchanged**) |
| `mtklogo` | Linux binary x86-64 v1.0.1 (identical to the latest upstream release) |
| `logo.bin` | example `logo.bin` from repository (replace with yours) |
| `suggested/` | `mtklogos.sh` v2, `mtklogo.yaml` with `exp_*` fixes/profiles, `mtklogo` patched |
| `mtklogo-gui-1.2-fonts.zip` | All files from mtklogo_v1.1 (`./run.sh` included) |
| `ANALYSIS_AND_SUGGESTIONS.md` | Script, yaml and source code analysis |

## Illustrative images
<details><summary> original - Click to open</summary>
<p>
<img width="1292" height="876" alt="111" src="https://github.com/user-attachments/assets/2be0b0b0-4da0-4b0c-8bdb-b49dcaa743fd" />
<img width="1416" height="952" alt="222" src="https://github.com/user-attachments/assets/f94dc55e-9498-4a68-91cd-f44579db1f37" />
<img width="1416" height="864" alt="333" src="https://github.com/user-attachments/assets/0cb2a37c-3ecc-42aa-afff-cce3be427c88" />
<img width="1416" height="864" alt="444" src="https://github.com/user-attachments/assets/19ea1ba6-f24d-4005-baf5-c217e711e216" />
<img width="1416" height="864" alt="555" src="https://github.com/user-attachments/assets/732f9d0e-15b1-4306-a93d-73aec6c3310a" />
<img width="1416" height="864" alt="666" src="https://github.com/user-attachments/assets/e7a50115-9b6e-4a69-8f0a-ba8d1e60e784" />
<img width="1416" height="864" alt="777" src="https://github.com/user-attachments/assets/a52f1dba-4bb0-465c-a7ca-fae9825f2dcf" />
<img width="1416" height="864" alt="888" src="https://github.com/user-attachments/assets/1837dc36-3533-4daa-9e08-6e3637292814" />
</p>
</details>

<details><summary> suggested - Click to open</summary>
<p>
<img width="1416" height="864" alt="001" src="https://github.com/user-attachments/assets/64939ebd-1062-40d4-a8f6-084823a267a2" />
<img width="1364" height="1019" alt="002" src="https://github.com/user-attachments/assets/122df669-e8e6-4869-bf3c-c721a689cb8e" />
<img width="1364" height="873" alt="003" src="https://github.com/user-attachments/assets/6dabad69-0d8e-4e88-a042-0726f4b25c8f" />
<img width="1364" height="873" alt="004" src="https://github.com/user-attachments/assets/21375713-ee92-4624-b081-06f9fa7f18c8" />
<img width="1364" height="873" alt="005" src="https://github.com/user-attachments/assets/8cbfa5e4-6a13-49b5-91e7-0e342a0d57e5" />
<img width="1364" height="873" alt="006" src="https://github.com/user-attachments/assets/4e3d86b8-09ad-40ab-baa2-f75300e64780" />
<img width="1420" height="940" alt="007" src="https://github.com/user-attachments/assets/f4c3adf8-9133-4d65-952e-8df6e7de9dd5" />
</p>
</details>

<details><summary> other languages - Click to open</summary>
<p>
<img width="1291" height="885" alt="de" src="https://github.com/user-attachments/assets/202959d8-71ae-491e-9286-8da56b3a0968" />
<img width="1291" height="885" alt="de1" src="https://github.com/user-attachments/assets/5e4f4e94-ab69-4b3c-b855-67e3da35a7a5" />
<img width="1291" height="885" alt="fr" src="https://github.com/user-attachments/assets/d1266d1d-2c2d-4d58-8c41-14f68ffc4ce7" />
<img width="1291" height="885" alt="fr1" src="https://github.com/user-attachments/assets/e7713c19-bc81-4a00-b659-ddd97cb86815" />
<img width="1291" height="885" alt="es" src="https://github.com/user-attachments/assets/2d572c8e-192e-471a-b3b6-fd6959961bde" />
<img width="1291" height="885" alt="es1" src="https://github.com/user-attachments/assets/f2beb2f5-b41a-4f68-bc03-ac30097f9c04" />
</p>
</details>

## To do
If you wish to submit a patch/fix from elsewhere (another project, idea, etc.), it is imperative that you retain ownership of the work of the person you wish to include. This will ensure that credit is given where it is deserved and that [open source principles](http://opensource.org/docs/osd) are respected. Your contribution to the project will still be acknowledged, as you will be permanently listed as a committer.

Read [suggestions-not-applied](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.2/ANALYSIS_AND_SUGGESTIONS.md#suggestions-not-applied) for more ideas and to avoid duplication, or to save time on new ways to contribute.

### Analysis and suggestions from claude.ai
You can read [ANALYSIS_AND_SUGGESTIONS.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.2/ANALYSIS_AND_SUGGESTIONS.md) if you want.

## Contributing
The real objective of contributing will be improvements in making the mtklogo binary file simpler, better, smaller and adding more resolutions or new resolutions/sizes/dimensions/colors to correctly decompress the `logo.bin` file.

For more details read first the [CONTRIBUTING.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.2/CONTRIBUTING.md) file before send a PR or any modifications.

## Authors
This project would not have been possible without the mtklogo binary file created by @arlept and the modifications/improvements (suggested option) made by @cyberknight777.

### Collaborators
- @Rusikxxx for translation into the Russian language.
