import os
import re
from .gitignore_parser import is_ignored

binary_extensions = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.ico',
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
    '.zip', '.rar', '.tar', '.gz', '.7z', '.bz2', 
    '.exe', '.dll', '.so', '.bin', '.dmg', '.iso', '.img', 
    '.psd', '.ai', '.indd', '.sketch',
    '.swf', '.fla',
    '.ttf', '.otf', '.woff', '.woff2', 
    '.class', '.jar', 
    '.dat', '.bak', 
    '.cr2', '.nef', '.arw', '.dng', 
    '.cab', '.cpl', '.cur', '.deskthemepack', '.dll', '.dmp', '.drv', '.efi', '.exe', 
    '.resx', '.resource', 
    '.db', '.sqlite', 
    '.pkg', '.deb', '.rpm', 
    '.apk', 
    '.ipa', 
    '.crx', 
    '.vsix', 
    '.xpi', 
    '.msi', 
    '.part', 
}

def is_binary_file(filename):
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
            print(f"**************** EOF: {file_path} ****************")

def parse_files(string):
    pattern = re.compile(
        r"===\.= ==== FILENAME: (?P<filename>.*?) = ===== =========\n```.*?\n(?P<content>.*?)\n```\n===\.= ==== EOF: (?P=filename) = ===== =========",
        re.DOTALL
    )
    matches = pattern.findall(string)
    files = [{"filename": match[0].strip(), "contents": match[1].strip()} for match in matches]
    return files

def extract_estimated_characters(string):
    pattern = re.compile(
        r"## ESTIMATED CHARACTERS:\n(\d+)"
    )
    match = pattern.search(string)
    if match:
        return int(match.group(1))
    return 0
