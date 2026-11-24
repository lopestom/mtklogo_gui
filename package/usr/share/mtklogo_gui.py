#!/usr/bin/env python3
"""
mtklogo GUI - graphical interface (Qt) for the `mtklogos.sh` script.

The script runs EXACTLY as is (`bash ./mtklogos.sh`), without any modification
to its processes. The GUI only:

  * captures stdout+stderr in real time (the text is kept for "Save log", it is not
    shown on screen; errors, warnings and result boxes pop up as alerts);
  * detects when the script is stopped waiting for input (via /proc, reading if
    any process in the tree is blocked in read(0, ...));
  * answers through the interface:

      - bash `select` menu -> options panel on the left (OK / Cancel)
      - `read` with text -> text field
      - [y/N], (y/n), yes/no -> Yes/No box
      - "Press Enter" -> Continue box

  * shows the unpacked PNG images on the right (logo, logo1, logo2);
  * sends the response to the script's stdin.

Only environment change: COLUMNS=1, so that the bash `select` prints one option
per line. It doesn't change the script's logic.

Works with PySide6 (preferred) or PyQt5.
"""
from __future__ import annotations

import codecs
import filecmp
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import mtklogo_i18n
from mtklogo_i18n import _

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    Signal = QtCore.Signal
    QT_API = "PySide6"
except ImportError:  # pragma: no cover
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets
        Signal = QtCore.pyqtSignal
        QT_API = "PyQt5"
    except ImportError:
        sys.exit("Qt not found. Install it with:  pip install PySide6   (or PyQt5)")

APP_VERSION = "1.5"
SCRIPT_NAME = "mtklogos.sh"
SEED_FILES = ("mtklogo", "mtklogos.sh", "mtklogo.yaml")
IMAGE_SETS = ("logo", "logo1", "logo2")     # folders of unpacked images shown on the right
PS3 = "#? "              # standard `select` prompt in bash
IDLE_SECONDS = 0.15      # Minimum silence on the way out before considering a prompt.
SPLASH_MS = 2400         # how long the opening splash stays on screen
SPLASH_FPS = 12          # frames per second of the pre-rendered splash animation
TILE_W, TILE_H = 94, 162  # thumbnail tile on the right panel
# Last entry of a bash `select` that means "leave / cancel" (hidden: the Cancel button sends it).
CANCEL_LABELS = {"exit", "cancel", "sair", "cancelar", "beenden", "abbrechen", "salir", "quitter",
                 "annuler", "выход", "отмена"}


def N_(text: str) -> str:
    """Marks a text for translation without translating it yet."""
    return text


# name, link, description (translated when shown)
AUTHORS = (
    ("arlept", "https://github.com/arlept/mtklogo",
     N_("Original mtklogo source code binary")),
    ("cyberknight777", "https://github.com/cyberknight777/mtklogo",
     N_("Upstream source code binary v1.0.1; improvements and ideas in yaml file")),
    ("lopestom", "https://github.com/lopestom/mtklogo_gui",
     N_("Upstream source code binary v1.1; update, improvements and ideas in yaml file; "
        "update source code to the new logo.bin files - Multi-image; "
        "Creator and designer of the GUI for mtklogo")),
)


# --------------------------------------------------------------------------- #
#  Process inspection (Linux): who is blocked from reading stdin?
# --------------------------------------------------------------------------- #
_READ_SYSCALL = {"x86_64": 0, "aarch64": 63, "arm64": 63, "riscv64": 63,
                 "i386": 3, "i686": 3, "armv7l": 3, "armv8l": 3}


def _children_map() -> dict[int, list[int]]:
    tree: dict[int, list[int]] = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat") as fh:
                stat = fh.read()
            ppid = int(stat.rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            continue
        tree.setdefault(ppid, []).append(int(entry))
    return tree


def process_tree(root: int) -> list[int]:
    tree, out, stack = _children_map(), [root], [root]
    while stack:
        for child in tree.get(stack.pop(), []):
            out.append(child)
            stack.append(child)
    return out


def stdin_waiters(root: int, stdin_fd: int | None = None):
    """PIDs (from the script and its descendants) are blocked in read() from OUR stdin.

    It only counts if it reads fd 0 *and* whose fd 0 is the same pipe that the GUI opened:
    This ignores `read` from internal script pipes (e.g., `while read ... < <(cmd)`).
    Returns None if it is not possible to inspect (different architecture, /proc
    restricted...). In this case, the GUI uses a time-based heuristic.
    """
    nr = _READ_SYSCALL.get(platform.machine())
    if nr is None:
        return None
    target = None
    if stdin_fd is not None:
        try:
            target = os.readlink(f"/proc/self/fd/{stdin_fd}")
        except OSError:
            target = None
    readable, waiting = False, []
    for pid in process_tree(root):
        try:
            with open(f"/proc/{pid}/syscall") as fh:
                parts = fh.read().split()
        except OSError:
            continue
        readable = True
        if len(parts) >= 2 and parts[0] == str(nr) and parts[1] == "0x0":
            if target is not None:
                try:
                    if os.readlink(f"/proc/{pid}/fd/0") != target:
                        continue
                except OSError:
                    continue
            waiting.append(pid)
    return waiting if readable else None




# --------------------------------------------------------------------------- #
#  In-memory log (ANSI codes removed, \r handled). Not shown, only saved on request.
# --------------------------------------------------------------------------- #
_CSI = re.compile(r"\x1b\[([0-?]*)[ -/]*([@-~])")
_PARTIAL_ESC = re.compile(r"\x1b(\[[0-?]*[ -/]*)?\Z")
_OTHER_ESC = re.compile(r"\x1b[()][0-9A-Za-z]|\x1b[=>78]")
_SPLIT = re.compile(r"(\r\n|\n|\r)")
_BANNER = re.compile(r"\*{10,}")
_STR_RE = re.compile(r"""^(P_ERR|P_WARN|M_CANCEL|M_MENU_7)=(['"])(.*)\2\s*$""")


class LogBuffer:
    """Plain-text copy of everything the script prints. Keeps `tail` (current line)."""

    MAX_LINES = 50000

    def __init__(self, on_line=None):
        self.on_line = on_line
        self.lines: list[str] = []
        self.reset_state()

    def reset_state(self):
        self.tail = ""
        self._cr = False
        self._carry = ""

    def feed(self, text: str):
        text, self._carry = self._carry + text, ""
        m = _PARTIAL_ESC.search(text)
        if m:                                  # ANSI sequence cut in half
            self._carry, text = text[m.start():], text[:m.start()]
        text = _CSI.sub("", _OTHER_ESC.sub("", text))
        for part in _SPLIT.split(text):
            if part in ("\n", "\r\n"):
                self._newline()
            elif part == "\r":
                self._cr = True
            elif part:
                if self._cr:                   # isolated '\r': overwrites the line
                    self.tail, self._cr = "", False
                self.tail += part

    def _newline(self):
        line = self.tail
        self.lines.append(line)
        if len(self.lines) > self.MAX_LINES:
            del self.lines[: len(self.lines) - self.MAX_LINES]
        self.tail, self._cr = "", False
        if self.on_line:
            self.on_line(line)

    def flush(self):
        if self.tail:
            self._newline()

    def note(self, text: str):
        """Writes a note (e.g. the answer sent to the script) on its own line."""
        self.flush()
        self.lines.append(text)

    def text(self) -> str:
        return "\n".join(self.lines + ([self.tail] if self.tail else [])) + "\n"


# --------------------------------------------------------------------------- #
#  Small helpers
# --------------------------------------------------------------------------- #
def tilde(path) -> str:
    """/home/me/mtklogo-gui -> ~/mtklogo-gui"""
    p, home = str(path), str(Path.home())
    return "~" + p[len(home):] if p == home or p.startswith(home + os.sep) else p


_ASSET_DIRS: list[Path] = []


def asset(name: str) -> Path | None:
    for d in _ASSET_DIRS:
        f = d / name
        if f.exists():
            return f
    return None


def script_strings(workdir: Path, lang: str) -> dict:
    """P_ERR / P_WARN / M_CANCEL / M_MENU_7 of the script's language file (English as base)."""
    out: dict = {}
    for code in ("en", lang):
        try:
            text = (workdir / "lang" / f"{code}.sh").read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            m = _STR_RE.match(line.strip())
            if m:
                out[m.group(1)] = m.group(3)
    return out


# --------------------------------------------------------------------------- #
#  Reading the process in thread
# --------------------------------------------------------------------------- #
class Reader(QtCore.QThread):
    chunk = Signal(bytes)
    done = Signal(int)

    def __init__(self, proc: subprocess.Popen, parent=None):
        super().__init__(parent)
        self.proc = proc

    def run(self):
        fd = self.proc.stdout.fileno()
        while True:
            try:
                data = os.read(fd, 65536)
            except OSError:
                break
            if not data:
                break
            self.chunk.emit(data)
        self.done.emit(self.proc.wait())


# --------------------------------------------------------------------------- #
#  Menu/Question Detection
# --------------------------------------------------------------------------- #
_MENU_START = re.compile(r"^\s*\d+\) ")
_MENU_ITEM = re.compile(r"(\d+)\) (.*?)(?=\s{2,}\d+\) |\s*$)")
_YES_NO = re.compile(
    r"[\[(]\s*(y(?:es)?|s(?:im|í|i)?|j(?:a)?|o(?:ui)?|д(?:а)?)\s*/\s*(n(?:o|ão|ao|ein|on)?|н(?:ет)?)\s*[\])]", re.IGNORECASE)
_ENTER = re.compile(
    r"(press|hit|pressione|tecle|aperte|pulse|presione|appuyez|нажмите)\W+(the\s+|sur\s+|la\s+tecla\s+)?(enter|return|entrée|entree|intro)"
    r"|eingabetaste|enter-taste|any key|qualquer tecla|cualquier tecla|toute touche|beliebige taste|любую клавишу",
    re.IGNORECASE)


def parse_menu_line(line: str):
    if not _MENU_START.match(line):
        return []
    return [(int(n), label.strip()) for n, label in _MENU_ITEM.findall(line)]


def install_qt_translations(app, base, locale, bundle, here):
    """Install qtbase_<language>.qm (standard Qt texts: OK, Cancel, Yes, No, file dialogs...)."""
    dirs = [d for d in ((bundle / "qt-translations") if bundle else None, here / "qt-translations") if d and d.is_dir()]
    try:
        dirs.append(Path(QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.TranslationsPath)))      # PySide6
    except AttributeError:
        dirs.append(Path(QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)))  # PyQt5
    if base == "en":
        return None
    qloc = QtCore.QLocale("pt_BR" if base == "pt" else locale)
    tr = QtCore.QTranslator(app)
    for d in dirs:
        if tr.load(qloc, "qtbase", "_", str(d)):
            app.installTranslator(tr)
            return tr
    return None


# --------------------------------------------------------------------------- #
#  Writable workspace  (~/mtklogo-gui)
# --------------------------------------------------------------------------- #
def find_bundle() -> Path | None:
    """Folder with the packaged files (mtklogo, mtklogos.sh, yaml, lang, assets)."""
    candidates = []
    if os.environ.get("APPDIR"):
        candidates.append(Path(os.environ["APPDIR"]) / "usr/share/mtklogo-gui")
    candidates.append(Path(__file__).resolve().parent / "bundle")
    return next((c for c in candidates if (c / SCRIPT_NAME).is_file()), None)


def seed_workspace(bundle: Path, root: Path) -> Path:
    """Copies the packaged files to ~/mtklogo-gui/ (without touching logo.bin, logo/,
    out/ or the user's backup). In a new version of the app it overwrites
    mtklogo/mtklogos.sh/mtklogo.yaml, saving a .bak of what the user has edited."""
    root.mkdir(parents=True, exist_ok=True)
    stamp = root / ".seed_version"
    fresh = not stamp.exists() or stamp.read_text().strip() != APP_VERSION
    for name in SEED_FILES:
        s_, d_ = bundle / name, root / name
        if not s_.exists():
            continue
        if not d_.exists():
            shutil.copy2(s_, d_)
        elif fresh and not filecmp.cmp(s_, d_, shallow=False):
            if name != "mtklogo":
                shutil.copy2(d_, d_.with_name(name + ".bak"))
            shutil.copy2(s_, d_)
        if name in ("mtklogo", "mtklogos.sh"):
            d_.chmod(0o755)
    if (bundle / "lang").is_dir() and (fresh or not (root / "lang").is_dir()):
        shutil.copytree(bundle / "lang", root / "lang", dirs_exist_ok=True)
    sample = bundle / "logo.bin"
    if sample.exists() and not (root / "logo.bin").exists():
        shutil.copy2(sample, root / "logo.bin")
    stamp.write_text(APP_VERSION)
    return root


# --------------------------------------------------------------------------- #
#  Widgets
# --------------------------------------------------------------------------- #
class MenuPanel(QtWidgets.QWidget):
    """Left panel: shows the options of the script's `select` (replaces the old pop-up)."""

    chosen = Signal(int, str)
    cancelled = Signal()

    def __init__(self, width: int):
        super().__init__()
        self.setFixedWidth(width)
        v = QtWidgets.QVBoxLayout(self)
        v.setContentsMargins(0, 4, 4, 0)
        v.setSpacing(6)
        self._v = v
        self.heading = QtWidgets.QLabel()
        self.heading.setWordWrap(True)
        self.list = QtWidgets.QListWidget()
        self.list.setTextElideMode(QtCore.Qt.ElideNone)
        self.list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.list.itemActivated.connect(lambda _i: self._ok())
        self.btn_ok = QtWidgets.QPushButton(_("OK"))
        self.btn_cancel = QtWidgets.QPushButton(_("Cancel"))
        self.btn_ok.setMinimumWidth(92)
        self.btn_cancel.setMinimumWidth(100)
        self.btn_ok.clicked.connect(self._ok)
        self.btn_cancel.clicked.connect(self.cancelled)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.btn_ok)
        row.addWidget(self.btn_cancel)
        self.fill = QtWidgets.QWidget()
        v.addWidget(self.heading)
        v.addWidget(self.list)
        v.addLayout(row)
        v.addWidget(self.fill, 1)

    def _layout_for(self, n: int):
        if n > 12:                         # long menu (e.g. profile list): fills the height
            self.list.setMinimumHeight(0)
            self.list.setMaximumHeight(16777215)
            self._v.setStretchFactor(self.list, 1)
            self.fill.setVisible(False)
        else:                              # short menu: just the height of the items
            rows = max(n, 3)
            h = self.list.sizeHintForRow(0) if n else 0
            h = h if h > 0 else 22
            self.list.setFixedHeight(h * rows + 2 * self.list.frameWidth() + 2)
            self._v.setStretchFactor(self.list, 0)
            self.fill.setVisible(True)

    def set_idle(self, text: str):
        self.heading.setText(text)
        self.list.clear()
        for w in (self.list, self.btn_ok, self.btn_cancel):
            w.setEnabled(False)
        self._layout_for(0)

    def show_menu(self, heading: str, items: list):
        self.heading.setText(heading)
        self.list.clear()
        for num, label in items:
            it = QtWidgets.QListWidgetItem(f"{num})  {label}")
            it.setData(QtCore.Qt.UserRole, (num, label))
            self.list.addItem(it)
        self.list.setCurrentRow(0)
        for w in (self.list, self.btn_ok, self.btn_cancel):
            w.setEnabled(True)
        self._layout_for(len(items))
        self.list.setFocus()

    def _ok(self):
        it = self.list.currentItem()
        if it is not None and self.list.isEnabled():
            num, label = it.data(QtCore.Qt.UserRole)
            self.chosen.emit(int(num), str(label))


class Gallery(QtWidgets.QScrollArea):
    """Right panel: thumbnails of the PNG files unpacked into one folder."""

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        body = QtWidgets.QWidget()
        body.setStyleSheet("background:#10141a;")
        v = QtWidgets.QVBoxLayout(body)
        v.setContentsMargins(8, 4, 8, 8)
        v.setSpacing(4)
        self.header = QtWidgets.QLabel()
        self.header.setStyleSheet("padding:6px 2px 2px 2px;background:transparent;color:#d8dee9;")
        self.empty = QtWidgets.QLabel()
        self.empty.setAlignment(QtCore.Qt.AlignCenter)
        self.empty.setWordWrap(True)
        self.empty.setStyleSheet("color:#7d8796;background:transparent;padding:40px 10px;")
        self.host = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)
        self.grid.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        v.addWidget(self.header)
        v.addWidget(self.empty)
        v.addWidget(self.host)
        v.addStretch(1)
        self.setWidget(body)
        self._sig = None
        self._tiles: list = []
        self._cols = 0
        self._queue: list = []
        self._loader = QtCore.QTimer(self)
        self._loader.setInterval(0)
        self._loader.timeout.connect(self._load_some)
        self._resize_timer = QtCore.QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(60)
        self._resize_timer.timeout.connect(self._relayout)
        self.show_folder(None, "")

    # ---- content
    def show_folder(self, folder: Path | None, name: str, force: bool = False):
        files = []
        if folder is not None and folder.is_dir():
            files = sorted(p for p in folder.glob("logo_*") if p.is_file())
        sig = (str(folder), tuple((p.name, p.stat().st_mtime_ns, p.stat().st_size) for p in files))
        if sig == self._sig and not force:
            return
        self._sig = sig
        self._loader.stop()
        for t in self._tiles:
            self.grid.removeWidget(t)
            t.deleteLater()
        self._tiles, self._queue, self._cols = [], [], 0
        if not files:
            self.header.setText("")
            self.empty.setText(_("No images here yet.\nRun “Unpack logo.bin” to extract them."))
            self.empty.setVisible(True)
            self.host.setVisible(False)
            return
        count = _("1 image") if len(files) == 1 else _("{n} images", n=len(files))
        self.header.setText(f"<b>{name}</b> &nbsp;<span style='color:#7d8796'>{count} · {tilde(folder)}</span>")
        self.empty.setVisible(False)
        self.host.setVisible(True)
        self._tiles = [self._make_tile(p) for p in files]
        self._queue = list(self._tiles)
        self._relayout()
        self._loader.start()

    def _make_tile(self, path: Path):
        m = re.match(r"logo_(\d+)", path.name)
        idx = int(m.group(1)) if m else 0
        f = QtWidgets.QFrame()
        f.setObjectName("tile")
        f.setFixedSize(TILE_W, TILE_H)
        f.setStyleSheet("#tile{background:#1a1f27;border:1px solid #2a313c;border-radius:4px;}"
                        "QLabel{border:0;background:transparent;}")
        v = QtWidgets.QVBoxLayout(f)
        v.setContentsMargins(3, 3, 3, 3)
        v.setSpacing(2)
        f.img = QtWidgets.QLabel()
        f.img.setAlignment(QtCore.Qt.AlignCenter)
        f.cap = QtWidgets.QLabel("%03d" % idx)
        f.cap.setAlignment(QtCore.Qt.AlignCenter)
        f.cap.setStyleSheet("color:#8b95a5;font-size:7pt;")
        v.addWidget(f.img, 1)
        v.addWidget(f.cap)
        f.path, f.idx = path, idx
        f.setToolTip(str(path))
        return f

    def _load_some(self):
        for _i in range(4):                       # a few thumbnails per tick: the window stays responsive
            if not self._queue:
                self._loader.stop()
                return
            f = self._queue.pop(0)
            try:
                self._load_tile(f)
            except RuntimeError:                  # tile deleted in the meantime
                continue

    def _load_tile(self, f):
        if f.path.suffix.lower() != ".png":       # slot kept as raw .z (unknown size)
            f.img.setText(".z")
            f.img.setStyleSheet("color:#6b7586;font-size:20pt;background:transparent;")
            f.cap.setText("%03d · .z · %d KB" % (f.idx, max(1, f.path.stat().st_size // 1024)))
            return
        r = QtGui.QImageReader(str(f.path))
        size = r.size()
        if size.isValid() and size.width() > 0 and size.height() > 0:
            k = min((TILE_W - 8) / size.width(), (TILE_H - 36) / size.height(), 1.5)
            r.setScaledSize(QtCore.QSize(max(1, round(size.width() * k)), max(1, round(size.height() * k))))
            f.cap.setText("%03d · %d×%d" % (f.idx, size.width(), size.height()))
        img = r.read()
        if not img.isNull():
            f.img.setPixmap(QtGui.QPixmap.fromImage(img))

    # ---- layout
    def _relayout(self):
        avail = max(self.viewport().width() - 16 - 16, TILE_W)    # margins + scroll bar
        cols = max(1, (avail + 8) // (TILE_W + 8))
        if cols == self._cols:
            return
        self._cols = cols
        for t in self._tiles:
            self.grid.removeWidget(t)
        for i, t in enumerate(self._tiles):
            self.grid.addWidget(t, i // cols, i % cols)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_timer.start()


class AuthorsDialog(QtWidgets.QDialog):
    """Floating box with the credits."""

    def __init__(self, parent=None):
        super().__init__(parent)
        import html
        self.setWindowTitle(_("Authors"))
        self.setMinimumWidth(620)
        v = QtWidgets.QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 14)
        v.setSpacing(14)
        for name, url, desc in AUTHORS:
            lab = QtWidgets.QLabel(
                f"<span style='font-size:12pt'><b>{html.escape(name)}</b></span><br>"
                f"<a href='{url}' style='color:#4db2ff'>{url}</a><br>"
                f"{html.escape(_(desc))}")
            lab.setWordWrap(True)
            lab.setTextFormat(QtCore.Qt.RichText)
            lab.setOpenExternalLinks(True)
            v.addWidget(lab)
            sep = QtWidgets.QFrame()
            sep.setFrameShape(QtWidgets.QFrame.HLine)
            sep.setFrameShadow(QtWidgets.QFrame.Sunken)
            v.addWidget(sep)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        close = QtWidgets.QPushButton(_("Close"))
        close.setMinimumWidth(100)
        close.setDefault(True)
        close.clicked.connect(self.accept)
        row.addWidget(close)
        v.addLayout(row)


class Splash(QtWidgets.QWidget):
    """Opening splash: plays the pre-rendered frames of splash_mtklogo.svg."""

    @staticmethod
    def create():
        d = asset("splash")
        frames = sorted(d.glob("frame_*.png")) if d is not None and d.is_dir() else []
        return Splash(frames) if frames else None

    def __init__(self, frames):
        flags = QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        super().__init__(None, flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.frames = [QtGui.QPixmap(str(f)) for f in frames]
        screen = QtWidgets.QApplication.primaryScreen()
        geo = screen.availableGeometry() if screen else QtCore.QRect(0, 0, 1280, 800)
        scale = min(1.0, 0.82 * geo.height() / 550)           # shrinks on small screens
        self.resize(int(300 * scale), int(550 * scale))
        self.move(geo.center() - self.rect().center())
        self._i = 0
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(int(1000 / SPLASH_FPS))
        self._timer.timeout.connect(self._next)
        self._timer.start()

    def _next(self):
        self._i = min(self._i + 1, len(self.frames) - 1)       # stops at the last frame
        self.update()

    def paintEvent(self, _event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        p.drawPixmap(self.rect(), self.frames[self._i])


# --------------------------------------------------------------------------- #
#  Main window
# --------------------------------------------------------------------------- #
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, workdir: Path):
        super().__init__()
        self.setWindowTitle(f"mtklogo GUI v{APP_VERSION}")
        self.resize(900, 620)

        self.workdir = workdir
        self.proc = None
        self.reader = None
        self._running = False
        self._dialog_open = False
        self._menu_state = None          # {"items": [...], "cancel": (num, label) | None} while the panel waits
        self._current_set = None
        self._strings: dict = {}
        self._notices: list = []
        self._banner = None
        self._notice_open = False
        self.log = LogBuffer(on_line=self._on_line)
        self._reset_run_state()

        # --- top bar
        self.icon_label = QtWidgets.QLabel()
        pm = QtGui.QPixmap(str(asset("icon_top_2x.png") or ""))
        if not pm.isNull():
            pm.setDevicePixelRatio(2.0)
            self.icon_label.setPixmap(pm)
        self.icon_label.setFixedSize(62, 46)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.btn_dir = QtWidgets.QPushButton(_("Folder…"))
        self.dir_edit = QtWidgets.QLineEdit(tilde(workdir))
        self.dir_edit.setReadOnly(True)
        self.dir_edit.setToolTip(str(workdir))
        self.btn_open = QtWidgets.QPushButton(_("Open"))
        self.btn_logo = QtWidgets.QPushButton(_("Choose logo.bin…"))
        self.btn_authors = QtWidgets.QPushButton(_("Authors"))
        top = QtWidgets.QHBoxLayout()
        top.setSpacing(6)
        for w in (self.icon_label, self.btn_dir):
            top.addWidget(w)
        top.addWidget(self.dir_edit, 1)
        for w in (self.btn_open, self.btn_logo, self.btn_authors):
            top.addWidget(w)

        # --- bottom left: run / stop (their width sets the divider position)
        self.btn_run = QtWidgets.QPushButton(_("▶  Run mtklogos.sh"))
        self.btn_stop = QtWidgets.QPushButton(_("■  Stop"))
        left_w = max(330, self.btn_run.sizeHint().width() + self.btn_stop.sizeHint().width() + 16)
        bl = QtWidgets.QHBoxLayout()
        bl.setContentsMargins(0, 0, 4, 0)
        bl.setSpacing(8)
        bl.addWidget(self.btn_run, 1)
        bl.addWidget(self.btn_stop)
        bl_w = QtWidgets.QWidget()
        bl_w.setLayout(bl)
        bl_w.setFixedWidth(left_w)

        # --- panels
        self.menu_panel = MenuPanel(left_w)
        self.menu_panel.set_idle(_("Press “Run mtklogos.sh” to start."))
        self.gallery = Gallery()

        # --- bottom right: image sets, save log, quit
        self.set_buttons: dict = {}
        self.set_group = QtWidgets.QButtonGroup(self)
        self.set_group.setExclusive(True)
        br = QtWidgets.QHBoxLayout()
        br.setContentsMargins(8, 0, 0, 0)
        br.setSpacing(6)
        for name in IMAGE_SETS:
            b = QtWidgets.QPushButton(name)
            b.setCheckable(True)
            b.setMinimumWidth(78)
            b.setEnabled(False)
            b.toggled.connect(lambda checked, b=b: self._paint_toggle(b, checked))
            b.clicked.connect(lambda _c=False, n=name: self._set_clicked(n))
            self.set_group.addButton(b)
            self.set_buttons[name] = b
            br.addWidget(b)
        br.addStretch(1)
        self.btn_savelog = QtWidgets.QPushButton(_("Save log"))
        self.btn_quit = QtWidgets.QPushButton(_("Quit"))
        self.btn_quit.setMinimumWidth(96)
        br.addWidget(self.btn_savelog)
        br.addSpacing(4)
        br.addWidget(self.btn_quit)
        br_w = QtWidgets.QWidget()
        br_w.setLayout(br)

        vline = QtWidgets.QFrame()
        vline.setFrameShape(QtWidgets.QFrame.VLine)
        vline.setFrameShadow(QtWidgets.QFrame.Sunken)
        g = QtWidgets.QGridLayout()
        g.setHorizontalSpacing(0)
        g.setVerticalSpacing(8)
        g.addWidget(self.menu_panel, 0, 0)
        g.addWidget(vline, 0, 1, 2, 1)
        g.addWidget(self.gallery, 0, 2)
        g.addWidget(bl_w, 1, 0)
        g.addWidget(br_w, 1, 2)
        g.setColumnStretch(2, 1)
        g.setRowStretch(0, 1)
        root = QtWidgets.QVBoxLayout()
        root.setContentsMargins(10, 8, 10, 6)
        root.setSpacing(8)
        root.addLayout(top)
        root.addLayout(g, 1)
        central = QtWidgets.QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)
        self.statusBar().showMessage(_("Ready."))

        # --- signals
        self.btn_run.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_dir.clicked.connect(self.choose_dir)
        self.btn_open.clicked.connect(self.open_dir)
        self.btn_logo.clicked.connect(self.choose_logo)
        self.btn_authors.clicked.connect(self.show_authors)
        self.btn_savelog.clicked.connect(self.save_log)
        self.btn_quit.clicked.connect(self.close)
        self.menu_panel.chosen.connect(self._menu_chosen)
        self.menu_panel.cancelled.connect(self._menu_cancelled)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._poll)
        self._notice_timer = QtCore.QTimer(self)
        self._notice_timer.setSingleShot(True)
        self._notice_timer.timeout.connect(self._flush_notices)

        self._update_buttons()
        self._refresh_gallery()

    # ------------------------------------------------------------------ state
    def _reset_run_state(self):
        self._menu_buf: list = []
        self._menu_heading_src = ""
        self._pending_menu = None
        self._menus: dict = {}
        self._menu_stack: list = []
        self._last_line = ""
        self._last_data = time.monotonic()
        self._need_new_data = False
        self._sent_at = 0.0
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")

    def _update_buttons(self):
        run = self._running
        self.btn_run.setEnabled(not run)
        self.btn_stop.setEnabled(run)
        self.btn_dir.setEnabled(not run)
        self.btn_logo.setEnabled(not run)

    def _status(self, msg: str):
        self.statusBar().showMessage(msg)

    # ------------------------------------------------------------ image sets (right panel)
    def _set_dir(self, name: str) -> Path:
        return self.workdir / "logo" if name == "logo" else self.workdir / "logo" / name

    @staticmethod
    def _count_images(folder: Path) -> int:
        return sum(1 for p in folder.glob("logo_*") if p.is_file()) if folder.is_dir() else 0

    def _paint_toggle(self, b, checked: bool):
        pal = QtGui.QPalette(self.palette())
        if checked:
            pal.setColor(QtGui.QPalette.Button, self.palette().color(QtGui.QPalette.Highlight))
            pal.setColor(QtGui.QPalette.ButtonText, self.palette().color(QtGui.QPalette.HighlightedText))
        b.setPalette(pal)

    def _check_only(self, name):
        self.set_group.setExclusive(False)
        for n, b in self.set_buttons.items():
            b.setChecked(n == name)
        self.set_group.setExclusive(True)

    def _set_clicked(self, name: str):
        self._current_set = name
        self._refresh_gallery()

    def _refresh_gallery(self, force: bool = False):
        counts = {n: self._count_images(self._set_dir(n)) for n in IMAGE_SETS}
        for n, b in self.set_buttons.items():
            b.setEnabled(counts[n] > 0)
            b.setToolTip(tilde(self._set_dir(n)))
        cur = self._current_set
        if cur is None or counts.get(cur, 0) == 0:
            cur = next((n for n in IMAGE_SETS if counts[n] > 0), None)
        self._current_set = cur
        self._check_only(cur)
        self.gallery.show_folder(self._set_dir(cur) if cur else None, cur or "", force)

    # ------------------------------------------------------------ folder / actions
    def choose_dir(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(
            self, _("Folder with mtklogos.sh, mtklogo and logo.bin"), str(self.workdir))
        if d:
            self.workdir = Path(d)
            self.dir_edit.setText(tilde(d))
            self.dir_edit.setToolTip(d)
            self._current_set = None
            self._refresh_gallery(force=True)

    def choose_logo(self):
        f, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _("Choose your logo.bin"), str(Path.home()), _("Logo images (*.bin);;All files (*)"))
        if not f:
            return
        dest = self.workdir / "logo.bin"
        if dest.exists() and not filecmp.cmp(f, dest, shallow=False):
            r = QtWidgets.QMessageBox.question(
                self, _("Replace logo.bin?"),
                _("A logo.bin already exists in:\n{path}\n\nReplace it with the selected file?\n(the original, if already used by the script, is kept in backup/)",
                  path=tilde(self.workdir)))
            if r != QtWidgets.QMessageBox.Yes:
                return
        try:
            shutil.copy2(f, dest)
        except OSError as exc:
            QtWidgets.QMessageBox.critical(self, _("Copy error"), str(exc))
            return
        self._status(_("logo.bin copied to {path}", path=tilde(self.workdir)))

    def open_dir(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(self.workdir)))

    def show_authors(self):
        AuthorsDialog(self).exec()

    def save_log(self):
        self.log.flush()
        body = self.log.text()
        if not body.strip():
            QtWidgets.QMessageBox.information(self, "mtklogo", _("Nothing to save yet."))
            return
        dest = self.workdir / time.strftime("mtklogo-gui_%Y%m%d-%H%M%S.log")
        head = (f"mtklogo GUI {APP_VERSION} · {time.strftime('%Y-%m-%d %H:%M:%S')} · "
                f"{self.workdir} · {platform.platform()}\n\n")
        try:
            dest.write_text(head + body, encoding="utf-8")
        except OSError as exc:
            QtWidgets.QMessageBox.critical(self, "mtklogo", _("Could not save the log:\n{error}", error=exc))
            return
        self._status(_("Log saved to {path}", path=tilde(dest)))

    # -------------------------------------------------------------- run
    def start(self):
        if self._running:
            return
        script = self.workdir / SCRIPT_NAME
        if not script.is_file():
            QtWidgets.QMessageBox.critical(
                self, _("Script not found"),
                _("{script} does not exist in:\n{path}\n\nUse “Folder…” to choose the correct folder.",
                  script=SCRIPT_NAME, path=tilde(self.workdir)))
            return
        self.log.reset_state()
        self.log.note(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} · {SCRIPT_NAME} · {self.workdir} ===")
        self._reset_run_state()
        self._banner, self._notices = None, []
        self._strings = script_strings(self.workdir, mtklogo_i18n.LANG)
        env = os.environ.copy()
        env["COLUMNS"] = "1"          # `select` prints one option per line.
        env["MTKLOGO_GUI_LANG"] = mtklogo_i18n.LANG   # The v2 script speaks the same language as the GUI.
        try:
            self.proc = subprocess.Popen(
                ["bash", f"./{SCRIPT_NAME}"], cwd=str(self.workdir), env=env,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, bufsize=0, start_new_session=True)
        except OSError as exc:
            QtWidgets.QMessageBox.critical(self, _("Start error"), str(exc))
            return
        self._running = True
        self.reader = Reader(self.proc, self)
        self.reader.chunk.connect(self._on_chunk)
        self.reader.done.connect(self._on_done)
        self.reader.start()
        self.timer.start()
        self.menu_panel.set_idle(_("Running…"))
        self._update_buttons()
        self._status(_("Running {script} (PID {pid})…", script=SCRIPT_NAME, pid=self.proc.pid))

    def stop(self):
        if not self._running or self.proc is None:
            return
        self._signal_group(signal.SIGTERM)
        QtCore.QTimer.singleShot(2000, lambda: self._signal_group(signal.SIGKILL))
        self._status(_("Stopping the script…"))

    def _signal_group(self, sig):
        if self.proc is not None and self.proc.poll() is None:
            try:
                os.killpg(self.proc.pid, sig)
            except (ProcessLookupError, PermissionError):
                pass

    # ------------------------------------------------------------ real-time output
    def _on_chunk(self, data: bytes):
        self._last_data = time.monotonic()
        self._need_new_data = False
        self.log.feed(self._decoder.decode(data))

    def _on_done(self, code: int):
        tail = self._decoder.decode(b"", final=True)
        if tail:
            self.log.feed(tail)
        self.timer.stop()
        self._running = False
        self._dialog_open = False
        self._menu_state = None
        self._menu_buf = []
        if self.log.tail:
            self.log.feed("\n")
        self.log.note(_("— Script finished (exit code {code}) —", code=code))
        self.menu_panel.set_idle(_("Press “Run mtklogos.sh” to start."))
        self._status(_("Finished (code {code}).", code=code))
        self._update_buttons()
        self._refresh_gallery()
        self._notice_timer.start(150)

    def _on_line(self, line: str):
        items = parse_menu_line(line)
        if items:
            if not self._menu_buf:
                self._menu_heading_src = self._last_line      # the question printed just before the menu
            self._menu_buf.extend(items)
            return
        self._finalize_menu()
        s = line.strip()
        if not s:
            return
        self._last_line = s
        self._notice_from_line(s)
        if not self._dialog_open and not _BANNER.fullmatch(s):
            self._status(s[:200])

    def _finalize_menu(self):
        if self._menu_buf:
            self._pending_menu = (sorted(dict(self._menu_buf).items()), self._menu_heading_src)
            self._menu_buf = []

    # ------------------------------------------------- alerts (errors, warnings, result boxes)
    def _notice_from_line(self, s: str):
        if _BANNER.fullmatch(s):                       # box printed by the script's banner()
            if self._banner is None:
                self._banner = []
            else:
                self._add_notice("info", "\n".join(self._banner))
                self._banner = None
        elif self._banner is not None:
            self._banner.append(s)
        else:
            err, warn = self._strings.get("P_ERR"), self._strings.get("P_WARN")
            if err and s.startswith(err):
                self._add_notice("error", s)
            elif warn and s.startswith(warn):
                self._add_notice("warning", s)

    def _add_notice(self, kind: str, text: str):
        self._notices.append((kind, text))
        self._notice_timer.start(350)                  # groups consecutive messages in one box

    def _flush_notices(self):
        if not self._notices:
            return
        if self._notice_open or (self._dialog_open and self._menu_state is None):
            self._notice_timer.start(400)              # a modal question is open: try again shortly
            return
        kinds = {k for k, _t in self._notices}
        text = "\n\n".join(t for _k, t in self._notices)
        self._notices = []
        icon = (QtWidgets.QMessageBox.Critical if "error" in kinds else
                QtWidgets.QMessageBox.Warning if "warning" in kinds else
                QtWidgets.QMessageBox.Information)
        self._notice_open = True
        try:
            QtWidgets.QMessageBox(icon, "mtklogo", text, QtWidgets.QMessageBox.Ok, self).exec()
        finally:
            self._notice_open = False

    # --------------------------------------------------------- detect prompts
    def _poll(self):
        if not self._running or self._dialog_open or self._notice_open or self.proc is None:
            return
        now = time.monotonic()
        if now - self._last_data < IDLE_SECONDS:
            return
        waiters = stdin_waiters(self.proc.pid, self.proc.stdin.fileno())
        if self._need_new_data:
            # Response sent; just ask again if the script has gone back to waiting.
            if waiters and now - self._sent_at > 0.6:
                self._need_new_data = False
            else:
                return
        tail = self.log.tail
        if waiters is None:                       # without /proc: time heuristic
            if not tail.strip() or now - self._last_data < 1.0:
                return
        elif not waiters:                         # Something is still working.
            return
        self._handle_prompt(tail, waiters[-1] if waiters else None)

    def _handle_prompt(self, tail: str, pid):
        self._finalize_menu()
        is_select = tail.endswith(PS3)
        entry = None
        if is_select:
            key = pid if pid is not None else "?"
            if self._pending_menu:
                self._menus[key] = self._pending_menu
                self._menu_stack.append(self._pending_menu)
                self._pending_menu = None
            entry = self._menus.get(key)
            if entry is None and pid is None and self._menu_stack:
                entry = self._menu_stack[-1]
        if is_select and entry:
            self._begin_menu(*entry)                  # embedded panel: answered through OK / Cancel
            return
        self._dialog_open = True
        self._status(_("Waiting for your answer…"))
        try:
            answer = self._ask_until_answered(tail, is_select)
        finally:
            self._dialog_open = False
        if answer is None:
            self.stop()
            return
        if self._running:
            self._send(*answer)
            self._status(_("Running…"))

    # ---- embedded options panel
    def _cancel_words(self) -> set:
        words = set(CANCEL_LABELS)
        words |= {self._strings.get(k, "").strip().lower() for k in ("M_CANCEL", "M_MENU_7")}
        words.discard("")
        return words

    def _begin_menu(self, items: list, heading: str):
        cancel = None
        if len(items) > 1 and items[-1][1].strip().lower() in self._cancel_words():
            items, cancel = items[:-1], items[-1]     # "Exit"/"Cancel" is done by the Cancel button
        h = (heading or "").strip()
        h = h if h.endswith(("?", ":", "：")) else _("Select an option:")
        self._menu_state = {"items": items, "cancel": cancel}
        self._dialog_open = True                      # blocks prompt detection while the panel waits
        self.menu_panel.show_menu(h, items)
        self._status(_("Waiting for your answer…"))
        self._refresh_gallery()                       # e.g. right after an unpack finished
        self._notice_timer.start(150)

    def _menu_answer(self, num: int, label: str):
        self._menu_state = None
        self._dialog_open = False
        self.menu_panel.set_idle(_("Running…"))
        if self._running:
            self._send(str(num), f"{num}  ({label})")
            self._status(_("Running…"))

    def _menu_chosen(self, num: int, label: str):
        if self._menu_state is not None:
            self._menu_answer(num, label)

    def _menu_cancelled(self):
        st = self._menu_state
        if st is None:
            return
        if st["cancel"]:                              # does what the script's last entry (Exit/Cancel) did
            self._menu_answer(*st["cancel"])
            return
        r = QtWidgets.QMessageBox.question(
            self, _("Cancel?"),
            _("Cancelling stops the script.\nDo you really want to stop the running process?"))
        if r == QtWidgets.QMessageBox.Yes:
            self._menu_state = None
            self._dialog_open = False
            self.menu_panel.set_idle(_("Running…"))
            self.stop()

    # ---------------------------------------------------------------- dialogues
    def _ask_until_answered(self, tail, is_select):
        """Returns (sent_text, displayed_text) or None if the user cancels."""
        while True:
            plain = tail.strip()
            if is_select:
                text = self.ask_text(_("The script asks for the number of an option:"))
                answer = (text, text) if text is not None else None
            elif (m := _YES_NO.search(plain)):
                yes, no = m.group(1).lower(), m.group(2).lower()
                r = self.ask_yes_no(plain)
                answer = ((yes, yes) if r else (no, no)) if r is not None else None
            elif _ENTER.search(plain):
                answer = ("", "⏎") if self.ask_enter(plain) else None
            else:
                label = plain or self._last_line or _("The script is waiting for input:")
                text = self.ask_text(label)
                answer = (text, text) if text is not None else None
            if answer is not None:
                return answer
            r = QtWidgets.QMessageBox.question(
                self, _("Cancel?"),
                _("Cancelling stops the script.\nDo you really want to stop the running process?"))
            if r == QtWidgets.QMessageBox.Yes:
                return None

    def ask_text(self, label: str):
        text, ok = QtWidgets.QInputDialog.getText(
            self, _("The script asks for a value"), label.strip() or _("Input:"))
        return text.strip() if ok else None

    def ask_yes_no(self, question: str):
        r = QtWidgets.QMessageBox.question(
            self, _("Script confirmation"), question,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        return r == QtWidgets.QMessageBox.Yes

    def ask_enter(self, text: str):
        box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Information, _("The script is waiting"), text,
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, self)
        box.button(QtWidgets.QMessageBox.Ok).setText(_("Continue"))
        return box.exec() == QtWidgets.QMessageBox.Ok

    # ------------------------------------------------------------------- send
    def _send(self, text: str, shown: str | None = None):
        if not self._running or self.proc is None or self.proc.stdin is None:
            return
        try:
            self.proc.stdin.write((text + "\n").encode())
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            self._status(_("Failed to send: the script is no longer reading input."))
            return
        self.log.note(shown if shown is not None else text)
        self._need_new_data = True
        self._sent_at = time.monotonic()

    # ------------------------------------------------------------------ close
    def closeEvent(self, event):
        if self._running:
            r = QtWidgets.QMessageBox.question(
                self, _("Script running"),
                _("The script is still running. Stop it and quit?"))
            if r != QtWidgets.QMessageBox.Yes:
                event.ignore()
                return
            self._signal_group(signal.SIGKILL)
            if self.reader:
                self.reader.wait(3000)
        event.accept()


def main():
    if sys.platform != "linux":
        print(_("Warning: this program was made for Linux."), file=sys.stderr)
    here = Path(__file__).resolve().parent
    explicit = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("mtklogo GUI")
    try:
        app.setDesktopFileName("mtklogo-gui")
    except Exception:
        pass
    bundle = find_bundle()
    _ASSET_DIRS[:] = [d for d in ((bundle / "assets") if bundle else None, here / "assets") if d]
    icon = QtGui.QIcon()
    for n in (16, 24, 32, 48, 72, 64, 128, 256, 512):
        f = asset(f"icon_72c.png") # icon_{n}.png
        if f:
            icon.addFile(str(f))
    app.setWindowIcon(icon)
    home = Path(os.environ.get("MTKLOGO_GUI_HOME", Path.home() / "mtklogo-gui"))
    extra = [home / "lang"] + ([bundle / "lang"] if bundle else [])
    base, loc = mtklogo_i18n.detect_language(extra, QtCore.QLocale.system().name())
    mtklogo_i18n.set_language(base, loc, extra)
    translator = install_qt_translations(app, base, loc, bundle, here)   # Qt's OK/Cancel/Yes/No buttons
    splash = None if os.environ.get("MTKLOGO_GUI_NOSPLASH") else Splash.create()
    workdir = explicit or here
    if bundle and explicit is None:
        workdir = seed_workspace(bundle, home)
    win = MainWindow(workdir)
    if splash is not None:
        splash.show()
        app.processEvents()

        def open_main():
            win.show()
            win.raise_()
            win.activateWindow()
            splash.close()
        QtCore.QTimer.singleShot(SPLASH_MS, open_main)
    else:
        win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
