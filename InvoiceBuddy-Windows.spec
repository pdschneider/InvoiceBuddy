# -*- mode: python ; coding: utf-8 -*-

import subprocess
subprocess.run(['python', 'Utils.version_gen.py'], check=True, capture_output=True)

# Hooks
from PyInstaller.utils.hooks import collect_all

ret_pyside = collect_all('PySide6')
ret_shiboken = collect_all('shiboken6')

a = Analysis(
    ['InvoiceBuddy.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('defaults', 'defaults'),
        ('CHANGELOG.md', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=['PIL._tkinter_finder', 'openpyxl', 'watchdog', 'msoffcrypto', 'tkinter', '_tkinter', 'pytesseract', 'pdf2image', 'PIL', 'packaging', 'pkg_resources', 'pdfplumber', 'PySide6', 'shiboken6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='InvoiceBuddy-Windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
    icon='defaults/assets/icon.ico',
    version='version.txt'
)
