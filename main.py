#!/usr/bin/env python

import os
import argparse
import sys
import io
from contextlib import redirect_stdout
from openai import OpenAI
from config import API_KEY

AUTODEV_PROMPT_PRE = """
You are a software development team.  I'm going to provide you with your codebase, then we'll build some features.

Here's my codebase:
"""

AUTODEV_PROMPT_POST_TEMPLATE = """
That's my codebase.

I will ask you to build features on top of the codebase - respond first with the files that need to be changed followed by a brief summary of the changes. Only output files that require changes to implement the current feature. When you output the files, begin with the filename of the file being updated and then output the entire un-truncated file after modifications. Do not remove any comments. Ensure that the first line of each file is "// FILENAME" or "# FILENAME" (depending on the language) where "FILENAME" is the file's name, and that the last line of each file is "// eof" or "# eof" (depending on the language) - and most importantly, make sure to surround each file with triple backticks "```" so that they will be entirely formatted as code.

Here are the features I need you to build:
[REQUIREMENTS]
"""

LIGHT_PINK = '\033[95m'
LIGHT_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

def parse_arguments():
    parser = argparse.ArgumentParser(description="A CLI program to display a directory tree and file contents.")
    parser.add_argument('--dir', type=str, default='.', help='The working directory of the codebase, default to current directory.')
    parser.add_argument('requirements', nargs='*', type=str, help='Requirements for features to build on the codebase.')
    return parser.parse_args()

def parse_gitignore(gitignore_path):
    if not os.path.exists(gitignore_path):
        return set()

    with open(gitignore_path, 'r') as file:
        lines = file.readlines()

    ignore_patterns = set()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            ignore_patterns.add(line)
    return ignore_patterns

def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if path.startswith(pattern):
            return True
    return False

def is_binary_file(filename):
    binary_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.ico',  # Image files
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',  # Audio files
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg',  # Video files
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',  # Document files
        '.zip', '.rar', '.tar', '.gz', '.7z', '.bz2',  # Compressed files
        '.exe', '.dll', '.so', '.bin', '.dmg', '.iso', '.img',  # Executable and disk image files
        '.psd', '.ai', '.indd', '.sketch',  # Adobe files
        '.swf', '.fla',  # Flash files
        '.ttf', '.otf', '.woff', '.woff2',  # Font files
        '.class', '.jar',  # Java files
        '.dat', '.bak',  # Backup and data files
        '.cr2', '.nef', '.arw', '.dng',  # Raw image files
        '.cab', '.cpl', '.cur', '.deskthemepack', '.dll', '.dmp', '.drv', '.efi', '.exe',  # Windows system files
        '.resx', '.resource',  # Resource files
        '.db', '.sqlite',  # Database files
        '.pkg', '.deb', '.rpm',  # Package management files
        '.apk',  # Android package file
        '.ipa',  # iOS app file
        '.crx',  # Chrome extension file
        '.vsix',  # Visual Studio extension file
        '.xpi',  # Firefox add-on file
        '.msi',  # Windows installer package
        '.part',  # Partially downloaded file
    }

    return os.path.splitext(filename)[1].lower() in binary_extensions

def print_tree(startpath, ignore_patterns, prefix=''):
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if not is_ignored(os.path.relpath(os.path.join(root, d), startpath), ignore_patterns)]
        files = [f for f in files if not is_ignored(os.path.relpath(os.path.join(root, f), startpath), ignore_patterns) and not is_binary_file(f)]

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{prefix}{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{prefix}{subindent}{f}')

def print_file_contents(startpath, ignore_patterns):
    for root, _, files in os.walk(startpath):
        files = [f for f in files if not is_ignored(os.path.relpath(os.path.join(root, f), startpath), ignore_patterns) and not is_binary_file(f)]
        for f in files:
            file_path = os.path.relpath(os.path.join(root, f), startpath)
            print(f"**************** FILE: {file_path} ****************")
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as file:
                    print(file.read())
            except UnicodeDecodeError as e:
                print(f"Error reading file {file_path}: {e}")
            print(f"**************** EOF ****************")

def main():
    args = parse_arguments()

    if sys.stdin.isatty():
        requirements = ' '.join(args.requirements)
    else:
        requirements = sys.stdin.read().strip()

    ignore_patterns = parse_gitignore(os.path.join(args.dir, '.gitignore'))

    f = io.StringIO()
    with redirect_stdout(f):
        print(AUTODEV_PROMPT_PRE)

        startpath = args.dir

        print("Directory Tree:")
        print_tree(startpath, ignore_patterns)

        print("\nFile Contents:")
        print_file_contents(startpath, ignore_patterns)

        autodev_prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.replace("[REQUIREMENTS]", requirements)
        print(autodev_prompt_post)

    USER_CONTENT = f.getvalue()

    # Ensure the API key is set
    if not API_KEY:
        raise ValueError("API_KEY is not set")

    client = OpenAI(api_key=API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": USER_CONTENT}
        ],
        stream=True
    )

    print(f"{LIGHT_GREEN}Streaming response:{RESET_COLOR}")
    inside_triple_stars = False  # Track whether inside **********
    for chunk in completion:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content"):
            print(f"{LIGHT_PINK}{delta.content}{RESET_COLOR}", end="", flush=True)
        else:
            print(f"{LIGHT_PINK}Chunk received: {chunk}{RESET_COLOR}", flush=True)

if __name__ == "__main__":
    main()
