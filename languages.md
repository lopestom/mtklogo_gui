# Script mtklogo.sh v2.2
The language's as the GUI in the `mtklogo-gui/mtklogos.sh` folder/file. 
**English is the default language for all words and phrases.**

## Add another language (without recompiling)
There are two ways to proceed, but it is important to apply the changes and additions to all of the files listed below.

1. Language file sh
For example, for Italian (it):
* Create `~your_path/mtklogo-gui/lang/it.json` with {"English text": "translation"}. The keys are in CATALOG["en"], in the mtklogo_i18n.py file.

  - Optional: copy `~your_path/mtklogo-gui/lang/en.sh` to `~your_path/mtklogo-gui/lang/it.sh` and translate.

The missing words will appear in English.

2. Python language file
A better way to contribute — if you wish to update the GUI — is to modify the source code to support your language. You can PR these `.sh` and `.py` files in this repository/branch so that other users can also benefit from your kindly work.
> [!NOTE]
> Be careful not to confuse the mtklogo_gui.AppImage files with the mtklogo_gui source code files!

- You can open the `mtklogo_i18n.py` file and *`TRANSLATE`* corresponding to your language;
- You can use the example below. Observe the English messages on the left-hand line up to the `:` symbol and translate them into your language in the message on the right – paying attention to extra encoding symbols such as `\n`; `{ }` and `PID` which should not be translated/removed during translation.
```yml
    "your_language_code": {
          "Original mtklogo source code binary": "TRANSLATE",
        "Upstream source code binary v1.0.1; improvements and ideas in yaml file": "TRANSLATE",
        "Upstream source code binary v1.1; update, improvements and ideas in yaml file; update source code to the new logo.bin files - Multi-image; Creator and designer of the GUI for mtklogo": "TRANSLATE",
        "OK": "TRANSLATE",
        "Cancel": "TRANSLATE",
        "1 image": "TRANSLATE",
        "{n} images": "{n} TRANSLATE",
        "Authors": "TRANSLATE",
        "Close": "TRANSLATE",
        "Folder…": "TRANSLATE…",
        "Open": "TRANSLATE",
        "Choose logo.bin…": "TRANSLATE logo.bin…",
        "▶  Run mtklogos.sh": "▶  TRANSLATE mtklogos.sh",
        "■  Stop": "■  TRANSLATE",
        "Press “Run mtklogos.sh” to start.": "TRANSLATE",
        "Save log": "TRANSLATE",
        "Quit": "TRANSLATE",
        "Ready.": "TRANSLATE.",
        "Folder with mtklogos.sh, mtklogo and logo.bin": "TRANSLATE",
        "Choose your logo.bin": "TRANSLATE",
        "Logo images (*.bin);;All files (*)": "TRANSLATE logo (*.bin);;TRANSLATE (*)",
        "logo.bin copied to {path}": "logo.bin TRANSLATE {path}",
        "Log saved to {path}": "TRANSLATE {path}",
        "Running…": "TRANSLATE…",
        "Running {script} (PID {pid})…": "TRANSLATE {script} (PID {pid})…",
        "Stopping the script…": "TRANSLATE…",
        "— Script finished (exit code {code}) —": "— TRANSLATE (TRANSLATE {code}) —",
        "Finished (code {code}).": "TRANSLATE (TRANSLATE {code}).",
        "Waiting for your answer…": "TRANSLATE…",
        "Select an option:": "TRANSLATE :",
        "Cancel?": "TRANSLATE",
        "Cancelling stops the script.\nDo you really want to stop the running process?": "TRANSLATE\nTRANSLATE",
        "The script asks for a value": "TRANSLATE",
        "Script confirmation": "TRANSLATE",
        "The script is waiting": "TRANSLATE",
        "Continue": "TRANSLATE",
        "Warning: this program was made for Linux.": "TRANSLATE",
        "No images here yet.\nRun “Unpack logo.bin” to extract them.": "TRANSLATE\nTRANSLATE",
        "Replace logo.bin?": "TRANSLATE",
        "A logo.bin already exists in:\n{path}\n\nReplace it with the selected file?\n(the original, if already used by the script, is kept in backup/)": "logo.bin TRANSLATE:\n{path}\n\nTRANSLATE\n(TRANSLATE)",
        "Nothing to save yet.": "TRANSLATE",
        "Script not found": "TRANSLATE",
        "{script} does not exist in:\n{path}\n\nUse “Folder…” to choose the correct folder.": "{script} TRANSLATE:\n{path}\n\nTRANSLATE",
        "Input:": "TRANSLATE",
        "Script running": "TRANSLATE",
        "The script is still running. Stop it and quit?": "TRANSLATE",
        "Copy error": "TRANSLATE",
        "Could not save the log:\n{error}": "TRANSLATE\n{error}",
        "Start error": "TRANSLATE",
        "The script asks for the number of an option:": "TRANSLATE",
        "Failed to send: the script is no longer reading input.": "TRANSLATE",
        "The script is waiting for input:": "TRANSLATE",
    },
```
Copy all the translated lines to `mtklogo_i18n.py` file in the section after the `    },` symbol from the last language.

Done!

Test everything and see if the translation matches the actions/errors/statements/paths and if there are any changes to correct that need it you can redo the translations in the files and lines anytime.
