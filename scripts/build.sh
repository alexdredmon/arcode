#!/bin/bash

# Please ensure you're in the root directory of the repository before running this script.

# Use Python 3.9 (or another stable version known to work with PyInstaller)
PYTHON_VERSION="3.9"

# Check if pyenv is installed
if command -v pyenv 1>/dev/null 2>&1; then
    # Install Python 3.9 using pyenv if not already installed
    pyenv install -s $PYTHON_VERSION
    # Set local Python version
    pyenv local $PYTHON_VERSION
else
    echo "pyenv is not installed. Please install pyenv or ensure Python $PYTHON_VERSION is available."
    exit 1
fi

# Create and activate virtual environment
python3 -m venv venv-build
source venv-build/bin/activate

# Upgrade pip and install requirements
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Install PyInstaller
pip3 install pyinstaller

# Build the executable
pyinstaller arcode.spec --clean --noconfirm

# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv-build

# Check if the 'dist' directory exists and contains the built executable
if [ ! -f "dist/arcode" ]; then
    echo "💥 Build failed. The 'dist/arcode' file does not exist."
    exit 1
fi

# Calculate and display SHA256 checksum
shasum -a 256 "dist/arcode" | cut -d ' ' -f 1

echo "✅ Build succeeded. The standalone executable is located at dist/arcode."
exit 0