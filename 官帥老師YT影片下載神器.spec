# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ai_studio_code_Latest.py'],
    pathex=[],
    binaries=[('yt-dlp.exe', '.'), ('ffmpeg.exe', '.')],
    datas=[('icon.ico', '.'), ('download_icon.png', '.'), ('robot_cat.png', '.')],
    hiddenimports=[],
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
    name='官帥老師YT影片下載神器',
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
)
