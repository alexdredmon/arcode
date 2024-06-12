#!/bin/bash

# Please ensure you're in the root directory of the repository before running this script.

virtualenv venv-build

source venv-build/bin/activate

pip install -r requirements.txt

pyinstaller arcode.spec --clean --noconfirm

deactivate

rm -rf venv-build

# Check if the 'dist' directory exists and contains the built executable
if [ ! -f "dist/arcode" ]; then
    echo "💥 Build failed. The 'dist/arcode' file does not exist."
    exit 1
fi

shasum -a 256 "dist/arcode" | cut -d ' ' -f 1

echo "✅ Build succeeded. The standalone executable is located at dist/arcode."
exit 0
