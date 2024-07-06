import os
from os.path import dirname
from lib.file_util import is_binary_file
import pathspec

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
    def __init__(self, startpath, additional_patterns=None):
        self.startpath = startpath
        self.gitignore_path = os.path.join(startpath, ".gitignore")
        # Create a copy of the default ignore patterns
        self.patterns = []

        # Create a List[str] of pattern rules by
        # 1) Iterating over the lines of the .gitignore file and filtering out empty and comment lines
        # 2) Adding the default ignore patterns
        # 3) Adding the additional patterns
        if os.path.exists(self.gitignore_path):
            with open(self.gitignore_path) as ignore_file:
                for line in ignore_file:
                    line = line.rstrip('\n')
                    if line and not line.startswith("#"):
                        self.patterns.append(line)

        self.patterns.extend(DEFAULT_IGNORE_PATTERNS)
        if additional_patterns:
            self.patterns.extend(additional_patterns)

        self.spec = pathspec.GitIgnoreSpec.from_lines(self.patterns)

    def select_files(self, files):
        """
        Filter files based on the .gitignore file and additional patterns.

        Args:
            files (list): A list of file paths.

        Returns:
            list: A list of file paths that should be uploaded.
        """
        return [f for f in files if self.should_upload(f)]

    def should_upload(self, file):
        """
        Check if the file should be uploaded.

        Args:
            file (str): A file path, relative to the start directory.

        Returns:
            bool: True if the file is not excluded by the .gitignore file or any
                  additional patterns, False otherwise.
        """
        path = os.path.normpath(file)
        if self.spec and self.spec.match_file(path):
            return False
        #
        if is_binary_file(os.path.join(self.startpath, path)):
            return False
        return True

