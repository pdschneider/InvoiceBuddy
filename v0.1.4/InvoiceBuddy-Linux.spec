# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['InvoiceBuddy.py'],
    pathex=[],
    binaries=[],
    datas=[('defaults', 'defaults')],
    hiddenimports=['PIL._tkinter_finder', 'pdfplumber', 'openpyxl', 'watchdog', 'msoffcrypto', 'pytesseract', 'pdf2image', 'PIL', 'packaging', 'pkg_resources'],
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
    name='InvoiceBuddy-Linux',
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
)
