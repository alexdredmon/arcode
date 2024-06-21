# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect data files
tiktoken_datas = collect_data_files("tiktoken")
litellm_datas = collect_data_files("litellm")
tiktoken_submodules = collect_submodules("tiktoken")
litellm_submodules = collect_submodules("litellm")

a = Analysis(
    ["arcode.py"],
    pathex=[],
    binaries=[],
    datas=tiktoken_datas + litellm_datas,
    hiddenimports=["pkg_resources", "pkg_resources.extern"]
    + tiktoken_submodules
    + litellm_submodules
    + ["tiktoken_ext.openai_public", "tiktoken_ext"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name="arcode",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
