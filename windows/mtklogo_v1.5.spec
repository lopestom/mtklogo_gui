# -*- mode: python ; coding: utf-8 -*-
# Build from the repository root:  pyinstaller windows/mtklogo_v1.5.spec
import os
ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))
GUI = os.path.join(ROOT, 'mtklogo-gui')

a = Analysis(
    [os.path.join(GUI, 'mtklogo_gui.py')], pathex=[GUI],
    datas=[(os.path.join(GUI, 'bundle'), 'bundle'), (os.path.join(GUI, 'git'), 'git')],
    excludes=['PySide6.QtNetwork', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtPdf', 'PySide6.QtSql',
              'PySide6.QtTest', 'PySide6.QtSvg', 'PySide6.QtOpenGL', 'PySide6.QtDBus',
              'PySide6.QtPrintSupport', 'PySide6.QtConcurrent', 'PySide6.QtXml', 'tkinter'],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='mtklogo_v1.5', debug=False, strip=False, upx=False,
          console=False, icon=os.path.join(SPECPATH, 'icon.ico'))
