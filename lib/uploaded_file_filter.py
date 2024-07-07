"""
This module provides functionality to filter uploaded files based on predefined and custom ignore
patterns.
It leverages patterns from a project's .gitignore file, a set of default ignore patterns, and any
additional patterns provided by the user to determine which files should be excluded from
processing.

Classes:
    UploadedFileFilter: Initializes with a starting path and optional additional ignore patterns.
    It can then be used to filter a list of files, excluding those that match the ignore patterns.

Constants:
    DEFAULT_IGNORE_PATTERNS: A list of file and directory patterns to be ignored by default.
"""
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
    """
    A class to filter uploaded files based on ignore patterns.

    This class uses ignore patterns from the project's .gitignore file, a set of default ignore
    patterns, and any additional patterns provided by the user to determine which files should be
    excluded from processing. It is initialized with a starting path and can optionally include
    additional ignore patterns.

    Attributes:
        startpath (str): The starting path from which to filter files.
        gitignore_path (str): The path to the .gitignore file within the startpath.
        patterns (List[str]): A list of ignore patterns compiled from the .gitignore file, default
            ignore patterns, and any additional patterns provided by the user.

    Methods:
        __init__(self, startpath, additional_patterns=None): Initializes the UploadedFileFilter
            with a starting path and optional additional ignore patterns.
    """
    def __init__(self, startpath, additional_patterns=None, max_file_size=1000000):
        self.startpath = startpath
        self.gitignore_path = os.path.join(startpath, ".gitignore")
        # Create a copy of the default ignore patterns
        self.patterns = []
        self.max_file_size = max_file_size

        # Create a List[str] of pattern rules by
        # 1) Iterating over the lines of the .gitignore file and filtering out empty and
        #    comment lines
        # 2) Adding the default ignore patterns
        # 3) Adding the additional patterns
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
