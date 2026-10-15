# -*- mode: python ; coding: utf-8 -*-
# How PyInstaller packs the webcam companion into BlinkCompanion.exe and the files beside it.
# Build it with build_companion.bat. GitHub's release workflow builds it from this file too.
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = []
binaries += collect_dynamic_libs('mediapipe')


a = Analysis(
    ['blink_companion.py'],
    pathex=[],
    binaries=binaries,
    datas=[('face_landmarker.task', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'sounddevice'],
    noarchive=False,
    optimize=0,
)
# Files we don't need: OpenCV's video-file decoder (webcams don't use it, ~30 MB)
# and Pillow's AVIF image support (~7 MB, never used here).
unneeded = ('opencv_videoio_ffmpeg', '_avif')
a.binaries = [b for b in a.binaries if not any(name in b[0] for name in unneeded)]
a.datas = [d for d in a.datas if not any(name in d[0] for name in unneeded)]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BlinkCompanion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BlinkCompanion',
)
