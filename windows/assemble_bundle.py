"""Assemble mtklogo-gui/bundle (flat layout, like usr/share/mtklogo-gui in the AppImage) for the Windows .exe.

  python windows/assemble_bundle.py --engine windows/bin/mtklogo.exe [--sample-logo logo.bin]

The sample logo.bin is not part of the source tree: pass one or it is downloaded from the lopestom repository.
Qt's own translations (OK/Cancel/Yes/No...) are copied from the installed PySide6.
"""
import argparse, re, shutil, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUI = ROOT / "mtklogo-gui"
SAMPLE_URL = "https://raw.githubusercontent.com/lopestom/mtklogo_gui/mtklogo_v1.2/logo.bin"


# --- version helpers --------------------------------------------------------

def find_engine_version(root: Path) -> str:
    """Return X.Y.Z taken from any mtklogo_vX.Y.Z/ folder in `root`."""
    for p in sorted(root.glob("mtklogo_v*")):
        if p.is_dir():
            m = re.fullmatch(r"mtklogo_v(\d+\.\d+\.\d+)", p.name)
            if m:
                return m.group(1)
    raise SystemExit(f"No mtklogo_vX.Y.Z/ folder found in {root}")


def patch_eng_version(script: Path, version: str) -> None:
    """Replace $ENG_VERSION (or any old version) on the `echo "mtklogo ..."` line."""
    text = script.read_text(encoding="utf-8")
    patched, n = re.subn(
        r'(echo\s+"mtklogo )[^"]*(")',
        rf'\g<1>{version}\g<2>',
        text,
    )
    if n == 0:
        raise SystemExit(f'Could not find: echo "mtklogo ..." in {script}')
    script.write_text(patched, encoding="utf-8")
    print(f"patched {script.name}: mtklogo {version}")


# --- main -------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", required=True, type=Path,
                    help="mtklogo.exe (engine 1.1.0, built from mtklogo_v1.1.0/)")
    ap.add_argument("--sample-logo", type=Path)
    a = ap.parse_args()

    out = GUI / "bundle"
    shutil.rmtree(out, ignore_errors=True)
    for d in ("lang", "assets", "qt-translations"):
        (out / d).mkdir(parents=True)

    shutil.copy2(a.engine, out / "mtklogo.exe")

    # --- mtklogos.sh: copy then patch with the version from mtklogo_vX.Y.Z/ ---
    shutil.copy2(ROOT / "mtklogos.sh", out / "mtklogos.sh")
    patch_eng_version(out / "mtklogos.sh", find_engine_version(ROOT))

    shutil.copy2(ROOT / "mtklogo.yaml", out / "mtklogo.yaml")
    for f in (GUI / "lang").glob("*.sh"):
        shutil.copy2(f, out / "lang" / f.name)
    shutil.copytree(GUI / "assets", out / "assets", dirs_exist_ok=True)

    if a.sample_logo:
        shutil.copy2(a.sample_logo, out / "logo.bin")
    else:
        urllib.request.urlretrieve(SAMPLE_URL, out / "logo.bin")

    import PySide6
    tr = Path(PySide6.__file__).parent / "translations"
    for loc in ("de", "es", "fr", "pt_BR", "ru"):
        shutil.copy2(tr / f"qtbase_{loc}.qm", out / "qt-translations" / f"qtbase_{loc}.qm")

    print("bundle ready:", out)


main()
