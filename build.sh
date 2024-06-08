#!/bin/bash

virtualenv venv-build

source venv-build/bin/activate

pip install -r requirements.txt

pyinstaller arcode.spec --clean --noconfirm

deactivate

rm -rf venv-build

shasum -a 256 "dist/arcode" | cut -d ' ' -f 1