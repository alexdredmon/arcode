# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import sys

block_cipher = None

# Collect data files
tiktoken_datas = collect_data_files("tiktoken")
litellm_datas = collect_data_files("litellm")
tiktoken_submodules = collect_submodules("tiktoken")
litellm_submodules = collect_submodules("litellm")

# Find libmagic and its dependencies
if sys.platform == 'darwin':
    libmagic_path = '/opt/homebrew/lib/libmagic.dylib'  # Default path for Homebrew on Apple Silicon
    if not os.path.exists(libmagic_path):
        libmagic_path = '/usr/local/lib/libmagic.dylib'  # Default path for Homebrew on Intel Macs
    magic_db_path = '/opt/homebrew/share/misc/magic.mgc'
    if not os.path.exists(magic_db_path):
        magic_db_path = '/usr/local/share/misc/magic.mgc'
elif sys.platform == 'linux':
    libmagic_path = '/usr/lib/libmagic.so.1'
    magic_db_path = '/usr/share/misc/magic.mgc'
else:
    raise OSError(f"Unsupported platform: {sys.platform}")

if not os.path.exists(libmagic_path):
    raise FileNotFoundError(f"libmagic not found at {libmagic_path}. Please ensure it's installed.")

if not os.path.exists(magic_db_path):
    raise FileNotFoundError(f"magic database not found at {magic_db_path}. Please ensure it's installed.")

# Create a runtime hook to set the MAGIC environment variable
with open('set_magic_env.py', 'w') as f:
    f.write("""
import os
import sys

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    basedir = sys._MEIPASS
else:
    # Running in a normal Python environment
    basedir = os.path.dirname(os.path.abspath(__file__))

os.environ['MAGIC'] = os.path.join(basedir, 'magic.mgc')
""")

a = Analysis(
    ["arcode.py"],
    pathex=[],
    binaries=[(libmagic_path, '.')],  # Include libmagic binary
    datas=tiktoken_datas + litellm_datas + [(magic_db_path, '.')],  # Include magic database file
    hiddenimports=["pkg_resources", "pkg_resources.extern"]
    + tiktoken_submodules
    + litellm_submodules
    + ["tiktoken_ext.openai_public", "tiktoken_ext"],
    hookspath=[],
    runtime_hooks=['set_magic_env.py'],  # Add the runtime hook
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