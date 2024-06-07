# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect tiktoken data files
tiktoken_datas = collect_data_files('tiktoken')
litellm_datas = collect_data_files('litellm')

a = Analysis(
    ['arcode.py'],
    pathex=['.'],
    binaries=[],
    datas=tiktoken_datas + litellm_datas,
    hiddenimports=['tiktoken_ext.openai_public', 'tiktoken_ext'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='arcode',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='arcode',
)