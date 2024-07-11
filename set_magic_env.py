
import os
import sys

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    basedir = sys._MEIPASS
else:
    # Running in a normal Python environment
    basedir = os.path.dirname(os.path.abspath(__file__))

os.environ['MAGIC'] = os.path.join(basedir, 'magic.mgc')
