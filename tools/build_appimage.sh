#!/usr/bin/env bash
# Rebuilds the mtklogo GUI AppImage using a base AppImage (e.g., the 1.5 release version) and this package.
#   Usage: tools/build_appimage.sh <base.AppImage> <version> [output.AppImage]
#   Example: tools/build_appimage.sh mtklogo-gui-1.5-x86_64.AppImage 1.6
# The embedded Python 3.12 and PySide6 are reused from the base AppImage. Only the following are replaced/updated:
#   mtklogo_vn.n (info, GUI, catalog, splash, icon) and the collection of files (binary engine, script, languages, yaml).
# Everything is placed at the root of the package (omitting subdirectories such as original/, sugerido/,
#  suggested/ or example/, which were removed in version 1.3).
# Requires: squashfs-tools (mksquashfs).
set -euo pipefail
OLD="1.4"
VER="1.5"
BASE="mtklogo-gui-$OLD-x86_64.AppImage"
PKG="$(cd "$(dirname "$0")/.." && pwd)"; OUT=mtklogo-gui-$VER-x86_64.AppImage
command -v mksquashfs >/dev/null || { echo "install squashfs-tools"; exit 1; }
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
cp "$BASE" "$W/base.AppImage"; chmod +x "$W/base.AppImage"
OFF=$("$W/base.AppImage" --appimage-offset)
( cd "$W" && ./base.AppImage --appimage-extract >/dev/null )
R="$W/squashfs-root"
S="$R/usr/share"
M="$S/mtklogo-gui"
U="$PKG/package"
T="$U/usr/share"
BIN=$(find "$PKG/bin" -maxdepth 1 -name 'mtklogo-*-linux-x86_64')   # find 1.1.0
install -m 755 "$T/mtklogo_gui.py" "$T/mtklogo_i18n.py" "$S/"
sed -i "s/^APP_VERSION = .*/APP_VERSION = \"$VER\"/" "$S/mtklogo_gui.py"
install -m 755 "$T/mtklogo-gui/mtklogos.sh" "$M/mtklogos.sh"
install -m 644 "$T/mtklogo-gui/mtklogo.yaml" "$M/mtklogo.yaml"
install -m 644 "$T/mtklogo-gui/logo.bin" "$M/logo.bin"
install -m 755 "$U/AppRun" "$R/AppRun"
install -m 644 "$U/mtklogo-gui.desktop" "$R/mtklogo-gui.desktop"
mkdir -p "$S/assets"
cp -r "$PKG/assets/." "$S/assets/"
ENG_VERSION="${BIN##*/}"                    # mtklogo-1.1.0-linux-x86_64
ENG_VERSION="${ENG_VERSION#mtklogo-}"       # 1.1.0-linux-x86_64
ENG_VERSION="${ENG_VERSION%-linux-x86_64}"  # 1.1.0
sed -i -E "s|(echo \"mtklogo )[^\"]*(\")|\1$ENG_VERSION\2|" "$M/mtklogos.sh"
install -m 644 "$PKG/assets/icon_72c.png" "$R/icon_72c.png"
install -m 644 "$PKG/assets/icon_256.png" "$R/mtklogo-gui.png"
python3 -m py_compile "$S/mtklogo_gui.py" "$S/mtklogo_i18n.py"; rm -rf "$S/__pycache__"
for f in "$T"/mtklogo-gui/lang/*.sh; do install -m 644 "$f" "$M/lang/"; done
find "$PKG/bin" -maxdepth 1 -name 'mtklogo-*-linux-x86_64' \-exec install -m 755 {} "$M/mtklogo" \;
mkdir -p "$S/qt-translations"
for f in "$PKG"/qt-translations/*.qm; do install -m 644 "$f" "$S/qt-translations/"; done
find "$R" -type d ! -perm -755 -exec chmod 755 {} +
mksquashfs "$R" "$W/fs.squashfs" -root-owned -noappend -comp zstd -b 131072 -quiet -no-progress
head -c "$OFF" "$W/base.AppImage" > "$W/runtime"
cat "$W/runtime" "$W/fs.squashfs" > "$OUT"; chmod +x "$OUT"
( cd "$(dirname "$OUT")" && sha256sum "$(basename "$OUT")" | tee "$(basename "$OUT").sha256" )
