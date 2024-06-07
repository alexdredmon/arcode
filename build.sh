#!/bin/bash

virtualenv venv-build

source venv-build/bin/activate

pip install -r requirements.txt

pyinstaller pyinstaller.spec --clean --noconfirm

deactivate

# rm -rf venv-build
