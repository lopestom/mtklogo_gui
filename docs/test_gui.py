import os, sys, time, shutil, filecmp, glob, tempfile
from pathlib import Path

APPDIR = os.environ["APPDIR"]
LANG = os.environ.get("MTKLOGO_GUI_LANG", "en")
SHOTS = Path(os.environ.get("SHOTS", "./shots")); SHOTS.mkdir(parents=True, exist_ok=True)
# End-to-end test with a logo.bin containing 2 images (e.g., Unihertz Tank 5, Android 16):
#   APPDIR=<Extracted AppImage> SRC_LOGO=logo_TANK5_A16.bin MTKLOGO_GUI_LANG=en python3.12 test_gui.py
SRC_LOGO = os.environ["SRC_LOGO"]
HOME = Path(tempfile.mkdtemp(prefix="gui_home_"))
os.environ.update(HOME=str(HOME), MTKLOGO_GUI_NOSPLASH="1", QT_QPA_PLATFORM="offscreen",
                  QT_LOGGING_RULES="qt.qpa.*=false", COLUMNS="1")
sys.path.insert(0, f"{APPDIR}/usr/share/")

import mtklogo_i18n, mtklogo_gui as g
from mtklogo_gui import QtCore, QtGui, QtWidgets, Path as _P

app = QtWidgets.QApplication([])
bundle = g.find_bundle()
assert bundle is not None, "bundle not found"
g._ASSET_DIRS[:] = [bundle / "assets"]
extra = [HOME / "mtklogo-gui" / "lang", bundle / "lang"]
base, loc = mtklogo_i18n.detect_language(extra, "ru_RU")
mtklogo_i18n.set_language(base, loc, extra)
work = g.seed_workspace(bundle, HOME / "mtklogo-gui")
shutil.copy2(SRC_LOGO, work / "logo.bin")
win = g.MainWindow(work)
win.show()

results = []
def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if extra else ""), flush=True)

# --- handles modal boxes (alerts / confirmations) on its own
answers = {"alpha": False}
def auto_modal():
    w = app.activeModalWidget()
    if isinstance(w, QtWidgets.QMessageBox):
        txt = w.text()
        auto_modal.seen.append((w.windowTitle(), txt[:90]))
        yes = w.button(QtWidgets.QMessageBox.Yes)
        no = w.button(QtWidgets.QMessageBox.No)
        if yes and no:                                  # script yes/no question: answer "no" (default)
            (no if not answers["alpha"] else yes).click()
        else:
            ok = w.button(QtWidgets.QMessageBox.Ok)
            (ok or w.buttons()[0]).click()
    elif w is not None:
        w.reject()
auto_modal.seen = []
t = QtCore.QTimer(); t.timeout.connect(auto_modal); t.start(80)

def wait(cond, timeout=90, what=""):
    t0 = time.time()
    while time.time() - t0 < timeout:
        app.processEvents()
        if cond():
            return True
        time.sleep(0.03)
    print("TIMEOUT:", what, flush=True)
    return False

def menu_ready():
    return win.menu_panel.list.isEnabled() and win.menu_panel.list.count() > 0
def items():
    return [win.menu_panel.list.item(i).text() for i in range(win.menu_panel.list.count())]
def shot(name):
    app.processEvents(); win.grab().save(str(SHOTS / f"{LANG}_{name}.png"))
def pick(row):
    win.menu_panel.list.setCurrentRow(row); win.menu_panel.btn_ok.click()

print(f"== language={mtklogo_i18n.LANG}  workdir={g.tilde(work)}")
# 0) initial state
check("no set selector / no manual field / no Clear",
      not any(hasattr(win, a) for a in ("combo", "set_combo", "input", "btn_send", "btn_clear", "console")))
check("field shows ~/mtklogo-gui", win.dir_edit.text() == "~/mtklogo-gui", win.dir_edit.text())
check("logo/logo1/logo2 buttons disabled before unpack", not any(b.isEnabled() for b in win.set_buttons.values()))
shot("00_start")

# 1) main menu
win.start()
check("main menu appears in the left panel", wait(menu_ready, 30, "menu"))
it = items()
check("The main menu has 6 items and NO 'Exit' option", len(it) == 6 and not any(("Exit" in x or "Sair" in x or "Beenden" in x or "Salir" in x or "Quitter" in x or "Выход" in x) for x in it), str(it))
shot("01_menu")

# 2) Unpack -> profile selection (sub-options)
pick(0)
check("list of profiles appears (sub-option)", wait(lambda: menu_ready() and win.menu_panel.list.count() > 20, 30, "profiles"))
n_prof = win.menu_panel.list.count()
rows = [win.menu_panel.list.item(i).text() for i in range(n_prof)]
check("list of profiles excluding the 'Cancel' entry from the script", not rows[-1].lower().endswith(("cancel", "cancelar", "abbrechen", "annuler", "отмена")), rows[-1])
check("title comes from the question in the script", win.menu_panel.heading.text().endswith("?"), win.menu_panel.heading.text())
shot("02_profiles")
row = next(i for i, t in enumerate(rows) if " 1440x3200 " in t or t.split(")", 1)[1].strip().startswith("1440x3200"))
pick(row)
check("returns to the main menu after unpacking", wait(lambda: menu_ready() and win.menu_panel.list.count() == 6, 180, "post-unpack"))

# 3) gallery
b = win.set_buttons
check("logo disabled; logo1 and logo2 enabled", (not b["logo"].isEnabled()) and b["logo1"].isEnabled() and b["logo2"].isEnabled())
check("logo1 automatically selected", b["logo1"].isChecked() and win._current_set == "logo1")
wait(lambda: not win.gallery._queue, 60, "thumbs logo1")
check("gallery show 1 image in the logo area", len(win.gallery._tiles) == 1, str(len(win.gallery._tiles)))
b["logo2"].click()
wait(lambda: len(win.gallery._tiles) == 59 and not win.gallery._queue, 90, "thumbs logo2")
check("gallery displays 59 images in logo2", len(win.gallery._tiles) == 59, str(len(win.gallery._tiles)))
pm_ok = sum(1 for t_ in win.gallery._tiles if t_.img.pixmap() is not None and not t_.img.pixmap().isNull())
check("all the miniatures carried", pm_ok == 59, f"{pm_ok}/59")
check("header shows count and folder with ~", "59" in win.gallery.header.text() and "~/mtklogo-gui/logo/logo2" in win.gallery.header.text(), win.gallery.header.text()[:120])
shot("03_logo2")
b["logo1"].click(); app.processEvents(); wait(lambda: len(win.gallery._tiles) == 1, 20)
shot("04_logo1")
b["logo2"].click(); wait(lambda: len(win.gallery._tiles) == 59, 20)

# 4) Repack (alpha: no) -> result box -> menu
pick(2)
check("repack return to menu", wait(lambda: menu_ready() and win.menu_panel.list.count() == 6 and not win._notices and not win._notice_open, 300, "repack"))
outs = sorted(glob.glob(str(work / "out" / "*.bin")))
check("repack generated 1 file in out/", len(outs) == 1, str(outs))
check("repack file == original logo.bin", outs and filecmp.cmp(outs[0], SRC_LOGO, shallow=False))
check("result box (banner) was displayed", any("Repack" in s or "repack" in s for _t, s in auto_modal.seen), str(auto_modal.seen[-2:]))
shot("05_post_repack")

# 5) Cancel = what item 7 did (exits the script)
win.menu_panel.btn_cancel.click()
check("Cancel terminates the script just like the old 'Exit' item.", wait(lambda: not win._running, 30, "end"))
check("status shows as completed", "0" in win.statusBar().currentMessage(), win.statusBar().currentMessage())
check("panel returns to an idle state", not win.menu_panel.list.isEnabled())

# 6) Save Log
before = set(glob.glob(str(work / "mtklogo-gui_*.log")))
win.btn_savelog.click(); app.processEvents()
logs = sorted(set(glob.glob(str(work / "mtklogo-gui_*.log"))) - before)
txt = Path(logs[0]).read_text(encoding="utf-8") if logs else ""
check("Save Log written to the working directory", len(logs) == 1, str(logs))
check("log contains the script output and the responses sent", "Repack" in txt and "7" in txt and "mtklogo GUI 1.5" in txt, f"{len(txt)} bytes")
check("log does not contain ANSI codes", "\x1b" not in txt)

# 7) Authors
dlg = g.AuthorsDialog(win); dlg.show(); app.processEvents()
labs = [w.text() for w in dlg.findChildren(QtWidgets.QLabel)]
check("Authors lists the 3 authors with links", all(any(u in l for l in labs) for u in ("github.com/arlept/mtklogo", "github.com/cyberknight777/mtklogo", "github.com/lopestom/mtklogo_gui")))
check("Authors: lopestom without /tree/", not any("/tree/" in l for l in labs))
dlg.grab().save(str(SHOTS / f"{LANG}_06_authors.png")); dlg.close()

print(f"\nSUMMARY [{LANG}]: {sum(ok for _n, ok in results)}/{len(results)} verifications")
sys.exit(0 if all(ok for _n, ok in results) else 1)
