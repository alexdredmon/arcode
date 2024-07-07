import os
import pathspec
from lib.file_io import is_binary_file

DEFAULT_IGNORE_PATTERNS = [
    "/.git/",
    "/.github/",
    "/.next/",
    "__pycache__/",
    "/node_modules/",
    "/venv/",
    ".arcode.cache.pkl",
    ".arcode.checksum.txt",
    ".arcode.embeddings",
    ".DS_Store",
    ".env",
]

class UploadedFileFilter:
    def __init__(self, startpath, additional_patterns=None, max_file_size=1000000):
        self.startpath = startpath
        self.gitignore_path = os.path.join(startpath, ".gitignore")
        self.patterns = []
        self.max_file_size = max_file_size

        if os.path.exists(self.gitignore_path):
            with open(self.gitignore_path, 'r', encoding='utf-8') as ignore_file:
                for line in ignore_file:
                    line = line.rstrip('\n')
                    if line and not line.startswith("#"):
                        self.patterns.append(line)

        self.patterns.extend(DEFAULT_IGNORE_PATTERNS)
        if additional_patterns:
            self.patterns.extend(additional_patterns)

        self.spec = pathspec.GitIgnoreSpec.from_lines(self.patterns)

    def select_files(self, files):
        return [f for f in files if self.should_upload(f)]

    def should_upload(self, file):
        path = self._get_file_path(file)
        if path is None:
            return False

        path = os.path.normpath(path)
        full_path = os.path.join(self.startpath, path)
        
        if self.spec and self.spec.match_file(path):
            return False
        
        try:
            if not os.path.exists(full_path):
                return False
            
            try:
                if is_binary_file(full_path):
                    return False
            except IOError:
                return False
            
            if os.path.getsize(full_path) > self.max_file_size:
                return False
        except (IOError, OSError):
            return False
        
        return True

    def _get_file_path(self, file):
        if isinstance(file, dict) and 'path' in file:
            return file['path']
        elif isinstance(file, str):
            return file
        else:
            return None