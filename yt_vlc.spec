# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all ttkbootstrap and yt-dlp data and submodules
datas = [
    ('the logo or icon', 'the logo or icon'),
]
datas += collect_data_files('ttkbootstrap')

hiddenimports = [
    'ttkbootstrap',
    'ttkbootstrap.style',
    'ttkbootstrap.themes',
    'ttkbootstrap.themes.standard',
    'yt_dlp',
    'yt_dlp.extractor',
    'PIL',
    'PIL._tkinter_finder',
]
hiddenimports += collect_submodules('ttkbootstrap')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YT_VLC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='the logo or icon/app_icon.ico',
)
