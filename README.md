# mtklogo GUI (v1.5)

## **New in 1.5**: W.I.P.


## AppImage (simplest)

```bash
chmod +x mtklogo-gui-1.2-x86_64.AppImage
./mtklogo-gui-1.2-x86_64.AppImage
```
* On the first run it creates
  - `~home/mtklogo-gui/` with a `logo.bin` file to test, `mtklogos.sh` script file, `mtklogo` binary file, `mtklogo.yaml` profile and 
  - `~home/mtklogo-gui/lang/` with all `*.sh` labguages files.
* Everything the script generates (`logo/`, `out/`, `backup/`) is in these folders. Use **Choose logo.bin…** to bring and use yours.

* No FUSE (`libfuse2`)? `./mtklogo-gui-1.5-x86_64.AppImage --appimage-extract-and-run`
* Requires glibc ≥ 2.34 (Ubuntu 22.04+, Debian 12+, Fedora 35+, Arch…) because of the `mtklogo` binary. Qt/xcb are built-in.

> [!NOTE]  
> A folder named `~home/mtklogo-gui` is created and `unpack` process create the subfolder `~home/mtklogo-gui/logo` that contains the png files from your logo.bin file.
>
> It is in this `/logo` subfolder that you should place your modified png images or modify the png images directly in this subfolder.
>
> <details><summary> Example - Click to open</summary>
> <p>
>  
> </p>
> </details>

## From sources



Minimalist graphical interface (Python + Qt) for `mtklogos.sh`.

The script runs **exactly as is** (`bash ./mtklogos.sh`): the GUI only captures the output in real time and respond to his questions through dialogue.

### Language detection
- The GUI reads `MTKLOGO_GUI_LANG`, `LANGUAGE`, `LC_ALL`, `LC_MESSAGES`, and `LANG`, in that order. To test another language without changing the system:
```bash
MTKLOGO_GUI_LANG=de ./mtklogo-gui-1.2-x86_64.AppImage
```

- All 45 GUI texts are translated in windows and dialogs. The standard Qt buttons (`OK`, `Cancel`, `Yes`, `No`, and `file dialogs`) are also included in `German`, `Spanish`, `French`, `Russian` and `Brazilian Portuguese`.

> [!NOTE]  
> Actually all multilingual users can add more languages ​​if they wish.
>
> Read the instructions in [languages.md](https://github.com/lopestom/mtklogo_gui/blob/mtklogo_v1.5/languages.md)
 
## Content

| File | Description |
|---|---|
| `*.sh` | language script Messages of mtklogo_gui (`English = default`) |
| `mtklogos.sh` | updated script v2.2 |
| `mtklogo` | Linux binary x86-64 v1.1.0 (new upstream release) |
| `logo.bin` | example `logo.bin` from repository (replace with yours) |
| `lang/` | `*.sh` languages updated to follow mtklogo.sh |
| `mtklogo-gui/` | `mtklogos.sh` updated script v2.2, `mtklogo.yaml` with `exp_*` and more fixes/profiles |


## Illustrative images
<details><summary> v1.5 - Click to open</summary>
<p>

</p>
</details>

<details><summary> other languages - Click to open</summary>
<p>

</p>
</details>

## To do
If you wish to submit a patch/fix from elsewhere (another project, idea, etc.), it is imperative that you retain ownership of the work of the person you wish to include. This will ensure that credit is given where it is deserved and that [open source principles](http://opensource.org/docs/osd) are respected. Your contribution to the project will still be acknowledged, as you will be permanently listed as a committer.

## Contributing
The real objective of contributing will be improvements in making the mtklogo binary file simpler, better, smaller and adding more resolutions or new resolutions/sizes/dimensions/colors to correctly decompress the `logo.bin` file.

For more details read first the [CONTRIBUTING.md](https://github.com/lopestom/mtklogo/blob/mtklogo_v1.2/CONTRIBUTING.md) file before send a PR or any modifications.

## Authors
This project would not have been possible without the mtklogo binary file created by @arlept and the modifications/improvements (suggested option) made by @cyberknight777.

### Collaborators
- @Rusikxxx for translation into the Russian language.
- @TheoLuc added more profiles through candidate resolutions.
